from __future__ import annotations

import itertools
import math
from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import (
    ContentItem,
    DeckSpec,
    FacilitatorNotes,
    ProviderConfig,
    SlideKind,
    SlideSpec,
    ThemeSpec,
)
from .planning import plan_deck
from .providers import AIProvider


ProgressCallback = Callable[[int, str, str], None]
AI_BATCH_SIZE = 24


class ProgramAxis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=160)
    details: str = Field(default="", max_length=1200)
    weight: float = Field(default=1.0, ge=0.1, le=10)


class LongDeckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=220)
    subtitle: str = Field(default="", max_length=300)
    audience: str = Field(min_length=1, max_length=400)
    sector: str = Field(default="عام", max_length=180)
    duration_hours: float = Field(default=6, ge=1, le=100)
    slide_count: int = Field(default=80, ge=50, le=200)
    objectives: str = Field(default="", max_length=2400)
    sources: str = Field(default="", max_length=6000)
    axes: list[ProgramAxis] = Field(min_length=1, max_length=30)
    theme_pack: str = "sandstone"
    theme_strategy: Literal["single", "alternating", "contextual"] = "contextual"
    mode: Literal["demo", "ai"] = "demo"
    provider: ProviderConfig | None = None
    render_pdf: bool = False

    @model_validator(mode="after")
    def require_provider_for_ai(self) -> "LongDeckRequest":
        if self.mode == "ai" and self.provider is None:
            raise ValueError("provider is required when mode is ai")
        return self


class ModulePlan(BaseModel):
    title: str
    details: str = ""
    slides: int
    start_slide: int
    end_slide: int
    theme_key: str


class LongDeckPlan(BaseModel):
    title: str
    slide_count: int
    global_opening_slides: int
    global_closing_slides: int
    estimated_generation_calls: int
    modules: list[ModulePlan]


def theme_library() -> dict[str, ThemeSpec]:
    return {
        "sandstone": ThemeSpec(
            name="Sandstone Editorial",
            background="F6F1E8",
            paper="FFFFFF",
            ink="0B1F33",
            primary="007C7A",
            accent="D5A02C",
            muted="667085",
        ),
        "cobalt": ThemeSpec(
            name="Cobalt Systems",
            background="F2F5FA",
            paper="FFFFFF",
            ink="111827",
            primary="2446F5",
            accent="F4B740",
            muted="64748B",
        ),
        "forest": ThemeSpec(
            name="Forest Strategy",
            background="F2F1EA",
            paper="FFFFFF",
            ink="19261F",
            primary="3E664A",
            accent="D08B36",
            muted="657269",
        ),
        "coral": ThemeSpec(
            name="Coral Decisions",
            background="F8F1EC",
            paper="FFFFFF",
            ink="252033",
            primary="B7463B",
            accent="E0A12E",
            muted="746A72",
        ),
        "slate": ThemeSpec(
            name="Slate Governance",
            background="EEF1F3",
            paper="FFFFFF",
            ink="10212C",
            primary="305A70",
            accent="C98D32",
            muted="65737C",
        ),
    }


def theme_catalog() -> list[dict[str, str]]:
    return [
        {
            "id": key,
            "name": theme.name,
            "background": f"#{theme.background}",
            "ink": f"#{theme.ink}",
            "primary": f"#{theme.primary}",
            "accent": f"#{theme.accent}",
        }
        for key, theme in theme_library().items()
    ]


def _theme_for_axis(axis: ProgramAxis, index: int, request: LongDeckRequest) -> str:
    if request.theme_strategy == "single":
        return request.theme_pack
    options = [request.theme_pack, "cobalt", "forest", "coral", "slate"]
    unique = list(dict.fromkeys(options))
    if request.theme_strategy == "alternating":
        return unique[index % len(unique)]

    text = f"{axis.title} {axis.details}".lower()
    if any(token in text for token in ("مخاطر", "أزمة", "تكلفة", "risk", "cost")):
        return "coral"
    if any(token in text for token in ("ذكاء", "رقمي", "بيانات", "تقنية", "ai", "digital", "data")):
        return "cobalt"
    if any(token in text for token in ("حوكمة", "امتثال", "عقد", "قرار", "governance")):
        return "slate"
    if any(token in text for token in ("استدام", "قيمة", "استراتيجية", "strategy", "value")):
        return "forest"
    return unique[index % len(unique)]


def _allocate(total: int, weights: list[float], minimum: int = 3) -> list[int]:
    count = len(weights)
    if total < count * minimum:
        minimum = max(1, total // count)
    base = [minimum] * count
    remaining = total - sum(base)
    if remaining <= 0:
        for index in range(-remaining):
            base[-1 - (index % count)] -= 1
        return base
    weight_sum = sum(weights)
    raw = [remaining * weight / weight_sum for weight in weights]
    floors = [int(value) for value in raw]
    allocation = [base[i] + floors[i] for i in range(count)]
    leftovers = total - sum(allocation)
    order = sorted(range(count), key=lambda i: raw[i] - floors[i], reverse=True)
    for index in range(leftovers):
        allocation[order[index % count]] += 1
    return allocation


def preview_long_deck(request: LongDeckRequest) -> LongDeckPlan:
    opening = 4
    closing = 4
    module_total = request.slide_count - opening - closing
    allocations = _allocate(module_total, [axis.weight for axis in request.axes], minimum=3)
    modules: list[ModulePlan] = []
    cursor = opening + 1
    for index, (axis, slides) in enumerate(zip(request.axes, allocations)):
        modules.append(
            ModulePlan(
                title=axis.title,
                details=axis.details,
                slides=slides,
                start_slide=cursor,
                end_slide=cursor + slides - 1,
                theme_key=_theme_for_axis(axis, index, request),
            )
        )
        cursor += slides
    return LongDeckPlan(
        title=request.title,
        slide_count=request.slide_count,
        global_opening_slides=opening,
        global_closing_slides=closing,
        estimated_generation_calls=(
            sum(math.ceil(module.slides / AI_BATCH_SIZE) for module in modules)
            if request.mode == "ai"
            else 0
        ),
        modules=modules,
    )


def _notes(
    objective: str,
    script: str,
    instruction: str = "",
    answer: str = "",
    transition: str = "",
    timing: str = "4 دقائق",
) -> FacilitatorNotes:
    return FacilitatorNotes(
        objective=objective,
        timing=timing,
        script=script,
        instruction=instruction,
        answer_or_debrief=answer,
        transition=transition,
    )


def _generic_items(axis: ProgramAxis, labels: list[str]) -> list[ContentItem]:
    descriptions = [
        f"تعريف عملي مرتبط بمحور {axis.title}.",
        "إشارة يمكن ملاحظتها داخل العمل.",
        "قرار أو أداة قابلة للتطبيق.",
        "معيار بسيط للتحقق من الجودة.",
        "خطوة لنقل الأثر إلى المشروع.",
    ]
    return [
        ContentItem(label=str(index + 1), title=label, text=descriptions[index % len(descriptions)])
        for index, label in enumerate(labels)
    ]


def _module_slide(axis: ProgramAxis, index: int, theme_key: str) -> SlideSpec:
    cycle = [
        SlideKind.CONCEPT,
        SlideKind.PROCESS,
        SlideKind.COMPARISON,
        SlideKind.CASE_STUDY,
        SlideKind.ACTIVITY,
        SlideKind.QUIZ,
        SlideKind.TOOL,
        SlideKind.METRICS,
        SlideKind.TIMELINE,
        SlideKind.STATEMENT,
    ]
    kind = cycle[(index - 1) % len(cycle)]
    common = {
        "id": f"{axis.title[:24]}-{index:02d}",
        "kind": kind,
        "eyebrow": axis.title,
        "theme_key": theme_key,
        "notes": _notes(
            objective=f"تمكين المتدرب من تطبيق جزء محدد من محور {axis.title}.",
            script=f"اشرح الفكرة في سياق {axis.details or axis.title} ثم اربطها بخبرة المشاركين.",
            transition="اربط المخرج بالشريحة التالية داخل الوحدة.",
        ),
    }
    if kind == SlideKind.CONCEPT:
        return SlideSpec(
            **common,
            title=f"الخريطة العملية لمحور {axis.title}",
            subtitle=axis.details,
            items=_generic_items(axis, ["المفهوم", "الإشارة", "القرار"]),
            takeaway="المعرفة لا تكتمل قبل تحويلها إلى قرار أو سلوك.",
        )
    if kind == SlideKind.PROCESS:
        return SlideSpec(
            **common,
            title=f"كيف نطبّق {axis.title} خطوة بخطوة؟",
            items=_generic_items(axis, ["التشخيص", "التحليل", "الاختيار", "التنفيذ", "المراجعة"]),
        )
    if kind == SlideKind.COMPARISON:
        return SlideSpec(
            **common,
            title=f"مقارنة قرارين في {axis.title}",
            items=[
                ContentItem(title="استجابة سطحية", text="حل سريع بلا تشخيص أو معيار نجاح."),
                ContentItem(title="استجابة منضبطة", text="قرار مبني على دليل ومفاضلة وحدود واضحة."),
            ],
        )
    if kind == SlideKind.CASE_STUDY:
        common["notes"] = _notes(
            objective=f"تطبيق منطق القرار في محور {axis.title}.",
            script="اعرض الحالة بمعلومات ناقصة ولا تعطِ الإجابة مقدماً.",
            instruction="اختاروا قراراً وحددوا الدليل الناقص والمفاضلة.",
            answer="قيّم منطق القرار، لا تشابه الإجابات.",
            timing="10 دقائق",
        )
        return SlideSpec(
            **common,
            title=f"حالة تطبيقية: قرار تحت ضغط في {axis.title}",
            body=f"تغيّر مؤثر في {axis.details or axis.title} ظهر قبل نقطة التزام رئيسية، والفريق مطالب بقرار خلال وقت قصير.",
            items=_generic_items(axis, ["الاستمرار", "تجربة محدودة", "إعادة التخطيط"]),
            takeaway="حدد القرار والدليل الناقص وصاحب الصلاحية.",
            duration_minutes=10,
        )
    if kind == SlideKind.ACTIVITY:
        common["notes"] = _notes(
            objective=f"إنتاج مخرج عملي في محور {axis.title}.",
            script="قسّم المشاركين إلى مجموعات صغيرة وراقب جودة المخرج.",
            instruction="طبّقوا الخطوات على موقف واقعي واكتبوا المخرج في صفحة واحدة.",
            answer="المعيار: وضوح القرار والدليل والمسؤولية.",
            timing="12 دقيقة",
        )
        return SlideSpec(
            **common,
            title=f"تطبيق: حوّل {axis.title} إلى قرار",
            body="اعمل على موقف حقيقي من مشروعك، ثم راجع النتيجة مع زميل.",
            items=_generic_items(axis, ["صف الموقف", "حلّل الأثر", "ابنِ البدائل", "ثبّت القرار"]),
            takeaway="المخرج: قرار قابل للمراجعة والتنفيذ.",
            duration_minutes=12,
        )
    if kind == SlideKind.QUIZ:
        common["notes"] = _notes(
            objective=f"التحقق من فهم محور {axis.title}.",
            script="اطلب إجابة فردية قبل النقاش.",
            instruction="اختر الإجابة واذكر سبباً واحداً.",
            answer="الإجابة ب لأنها تربط القرار بالدليل والمعيار.",
        )
        return SlideSpec(
            **common,
            title=f"تحقق سريع: {axis.title}",
            body="أي ممارسة تعكس فهماً قابلاً للتطبيق؟",
            choices=[
                "جمع معلومات أكثر بلا قرار",
                "ربط الدليل بقرار ومعيار نجاح",
                "تكرار الإجراء المعتاد",
                "تأجيل النقاش إلى نهاية المشروع",
            ],
            answer_index=1,
            duration_minutes=4,
        )
    if kind == SlideKind.TOOL:
        return SlideSpec(
            **common,
            title=f"أداة تشغيل محور {axis.title}",
            items=_generic_items(axis, ["المدخل", "التحليل", "القرار", "المالك", "المؤشر"]),
            takeaway="إذا تعذر ملء حقل، فهناك معلومة أو صلاحية ناقصة.",
        )
    if kind == SlideKind.METRICS:
        return SlideSpec(
            **common,
            title=f"ثلاث إشارات لمتابعة {axis.title}",
            items=[
                ContentItem(value="01", title="وضوح المسؤولية"),
                ContentItem(value="02", title="زمن اتخاذ القرار"),
                ContentItem(value="03", title="جودة المخرج"),
            ],
        )
    if kind == SlideKind.TIMELINE:
        return SlideSpec(
            **common,
            title=f"تدرّج التطبيق في {axis.title}",
            items=_generic_items(axis, ["ابدأ", "جرّب", "راجع", "ثبّت"]),
        )
    return SlideSpec(
        **common,
        title=f"السؤال الحاسم في {axis.title}",
        body="ما القرار الذي يجب أن يصبح أوضح بعد هذه الوحدة، وما الدليل الذي سيغيّر هذا القرار؟",
    )


def _opening_slides(request: LongDeckRequest) -> list[SlideSpec]:
    objective_lines = [line.strip(" -•\t") for line in request.objectives.splitlines() if line.strip()]
    if not objective_lines:
        objective_lines = [
            "تشخيص الموقف قبل اختيار الأداة.",
            "اتخاذ قرار مبني على دليل ومفاضلة.",
            "نقل المخرج إلى تطبيق قابل للمتابعة.",
        ]
    return [
        SlideSpec(
            id="cover",
            kind=SlideKind.COVER,
            title=request.title,
            subtitle=request.subtitle,
            eyebrow="برنامج تدريبي طويل",
            notes=_notes("افتتاح البرنامج وتثبيت ناتج الأداء.", "عرّف البرنامج ومساره ومخرجاته."),
        ),
        SlideSpec(
            id="opening-question",
            kind=SlideKind.STATEMENT,
            title="السؤال الذي يقود البرنامج",
            body=f"كيف نحول محاور {request.title} إلى قرارات وسلوكيات قابلة للملاحظة داخل {request.sector}؟",
            eyebrow="افتتاح",
            notes=_notes("كشف الفجوة العملية.", "ناقش السؤال واربطه بتوقعات المشاركين."),
        ),
        SlideSpec(
            id="learning-outcomes",
            kind=SlideKind.CONCEPT,
            title="ما الذي سيتغير في أداء المتدرب؟",
            items=[ContentItem(label=str(i + 1), title=line) for i, line in enumerate(objective_lines[:5])],
            eyebrow="نواتج التعلم",
            notes=_notes("توضيح نواتج الأداء.", "اقرأ النواتج كالتزام تدريبي قابل للقياس."),
        ),
        SlideSpec(
            id="program-map",
            kind=SlideKind.TOOL,
            title="خريطة البرنامج",
            items=[ContentItem(label=str(i + 1), title=axis.title, text=axis.details) for i, axis in enumerate(request.axes[:8])],
            eyebrow="الخريطة",
            notes=_notes("عرض مسار البرنامج.", "وضح ترتيب الوحدات والعلاقة بينها."),
        ),
    ]


def _closing_slides(request: LongDeckRequest) -> list[SlideSpec]:
    return [
        SlideSpec(
            id="integrated-case",
            kind=SlideKind.CASE_STUDY,
            title="الحالة التكاملية",
            body=f"موقف مركب في قطاع {request.sector} يتطلب استخدام أكثر من محور للوصول إلى قرار متوازن.",
            items=[
                ContentItem(title="القرار", text="ما الذي يجب حسمه الآن؟"),
                ContentItem(title="المفاضلة", text="ما الذي سنكسبه وما الذي سنحميه؟"),
                ContentItem(title="الدليل", text="ما المعلومة التي قد تغيّر القرار؟"),
            ],
            takeaway="المخرج: قرار موثق وخطة تنفيذ قصيرة.",
            duration_minutes=20,
            notes=_notes(
                "دمج محاور البرنامج في قرار واحد.",
                "اعرض الحالة على مرحلتين وأضف معلومة جديدة بعد القرار الأول.",
                "اعملوا في فرق ثم قدموا القرار والمفاضلة.",
                "قيّم منطق القرار وتكامل المحاور.",
                timing="20 دقيقة",
            ),
        ),
        SlideSpec(
            id="post-assessment",
            kind=SlideKind.QUIZ,
            title="التقييم البعدي",
            body="أي نتيجة تثبت أن التدريب انتقل إلى الأداء؟",
            choices=[
                "حفظ المصطلحات",
                "إنتاج قرار أو أداة وفق معيار واضح",
                "زيادة عدد الاجتماعات",
                "إضافة شرائح أكثر للتقرير",
            ],
            answer_index=1,
            notes=_notes("قياس ناتج الأداء.", "اطلب الإجابة والتبرير.", answer="الإجابة ب."),
        ),
        SlideSpec(
            id="transfer-plan",
            kind=SlideKind.TIMELINE,
            title="نقل الأثر خلال 30 يوماً",
            items=[
                ContentItem(label="أسبوع 1", title="اختيار موقف حقيقي", text="حدد مشروعاً أو عملية للتجربة."),
                ContentItem(label="أسبوع 2", title="تطبيق الأداة", text="نفّذ الممارسة مع فريق صغير."),
                ContentItem(label="أسبوع 3", title="مراجعة المخرج", text="افحص الجودة والوقت والمقاومة."),
                ContentItem(label="أسبوع 4", title="تثبيت الإيقاع", text="حدد المالك والمؤشر والمتابعة."),
            ],
            notes=_notes("تصميم خطة نقل أثر.", "اطلب مشروعاً وموعداً ومؤشراً لكل متدرب."),
        ),
        SlideSpec(
            id="closing-commitment",
            kind=SlideKind.SUMMARY,
            title="ما الذي ستبدأ به؟",
            bullets=[
                "اختر موقفاً حقيقياً واحداً.",
                "استخدم أداة واحدة من البرنامج.",
                "اطلب مراجعة زميل أو مدير.",
                "تابع مؤشراً واحداً خلال 30 يوماً.",
            ],
            takeaway="التدريب ينجح عندما يتغير قرار أو سلوك في العمل.",
            notes=_notes("تثبيت الالتزام الختامي.", "اطلب من كل مشارك كتابة أول خطوة وموعدها."),
        ),
    ]


def build_demo_long_deck(
    request: LongDeckRequest, progress: ProgressCallback | None = None
) -> DeckSpec:
    progress = progress or (lambda *_: None)
    plan = preview_long_deck(request)
    progress(8, "architecture", "تم توزيع الشرائح على الوحدات")
    slides = _opening_slides(request)
    progress(15, "opening", "تم بناء افتتاح البرنامج ونواتج التعلم")
    for module_index, (axis, module) in enumerate(zip(request.axes, plan.modules)):
        module_slides = [
            SlideSpec(
                id=f"section-{module_index + 1:02d}",
                kind=SlideKind.SECTION,
                title=axis.title,
                subtitle=axis.details or f"الوحدة {module_index + 1}",
                eyebrow=f"الوحدة {module_index + 1:02d}",
                theme_key=module.theme_key,
                notes=_notes("فتح الوحدة وربطها بناتج الأداء.", "قدّم سؤال الوحدة ومخرجها العملي."),
            )
        ]
        module_slides.extend(
            _module_slide(axis, index, module.theme_key)
            for index in range(1, module.slides)
        )
        slides.extend(module_slides[: module.slides])
        percent = 15 + int(60 * (module_index + 1) / len(plan.modules))
        progress(percent, "modules", f"تم بناء وحدة: {axis.title}")
    slides.extend(_closing_slides(request))
    slides = slides[: request.slide_count]
    while len(slides) < request.slide_count:
        axis = request.axes[(len(slides) - 4) % len(request.axes)]
        slides.insert(-4, _module_slide(axis, len(slides), request.theme_pack))
    library = theme_library()
    base = library.get(request.theme_pack, library["sandstone"]).model_copy(deep=True)
    base.footer_text = request.title
    variants = {key: value.model_copy(deep=True) for key, value in library.items()}
    for theme in variants.values():
        theme.footer_text = request.title
    progress(82, "assembly", "تم تجميع العرض وإسناد الثيمات")
    return DeckSpec(
        title=request.title,
        subtitle=request.subtitle,
        language="ar",
        direction="rtl",
        program_name=request.title,
        audience=request.audience,
        duration=f"{request.duration_hours:g} ساعة",
        learning_objective=request.objectives,
        theme=base,
        theme_variants=variants,
        slides=slides,
    )


def _module_ai_brief(request: LongDeckRequest, axis: ProgramAxis, slides: int) -> str:
    return f"""
أنشئ وحدة تدريبية عربية RTL داخل برنامج طويل.
اسم البرنامج: {request.title}
الجمهور: {request.audience}
القطاع: {request.sector}
مدة البرنامج: {request.duration_hours:g} ساعة
المحور الحالي: {axis.title}
تفاصيل المحور: {axis.details}
نواتج البرنامج: {request.objectives}
عدد شرائح هذه الوحدة بالضبط: {slides}

ابدأ بفاصل وحدة واحد، ثم نوّع بين مفهوم، عملية، مقارنة، حالة، نشاط، اختبار، أداة،
وملخص بحسب المعنى. لا تضف غلافاً للبرنامج. اكتب ملاحظات ميسّر كاملة. لا تخترع
مصادر أو إحصاءات. هذه الوحدة ستندمج مع وحدات أخرى، فتجنب مقدمة وخاتمة البرنامج.
""".strip()


def build_ai_long_deck(
    request: LongDeckRequest,
    provider: AIProvider,
    progress: ProgressCallback | None = None,
) -> DeckSpec:
    progress = progress or (lambda *_: None)
    plan = preview_long_deck(request)
    skeleton = build_demo_long_deck(request)
    opening = _opening_slides(request)
    closing = _closing_slides(request)
    generated_slides: list[SlideSpec] = list(opening)
    for index, (axis, module) in enumerate(zip(request.axes, plan.modules)):
        candidates: list[SlideSpec] = []
        remaining = module.slides
        batch_index = 0
        while remaining > 0:
            batch_index += 1
            batch_size = min(AI_BATCH_SIZE, remaining)
            progress(
                10 + int(65 * index / len(plan.modules)),
                "ai_generation",
                f"يتم توليد وحدة: {axis.title} — دفعة {batch_index}",
            )
            brief = _module_ai_brief(request, axis, batch_size)
            if request.sources:
                brief += f"\n\nالمصادر والقيود التي قدمها المستخدم:\n{request.sources}"
            generated = plan_deck(provider, brief, batch_size)
            batch = [slide for slide in generated.slides if slide.kind != SlideKind.COVER]
            if batch_index > 1:
                batch = [slide for slide in batch if slide.kind != SlideKind.SECTION]
            candidates.extend(batch[:batch_size])
            remaining -= batch_size
        if not candidates or candidates[0].kind != SlideKind.SECTION:
            candidates.insert(
                0,
                SlideSpec(
                    kind=SlideKind.SECTION,
                    title=axis.title,
                    subtitle=axis.details,
                    notes=_notes("فتح الوحدة.", "قدّم ناتج الوحدة وسؤالها المحوري."),
                ),
            )
        fallback = [
            slide.model_copy(deep=True)
            for slide in skeleton.slides[4 + sum(m.slides for m in plan.modules[:index]) :]
        ]
        candidates.extend(fallback)
        for slide in candidates[: module.slides]:
            slide.theme_key = module.theme_key
            generated_slides.append(slide)
    generated_slides.extend(closing)
    generated_slides = generated_slides[: request.slide_count]
    skeleton.slides = generated_slides
    progress(82, "assembly", "تم دمج الوحدات في عرض واحد")
    return skeleton
