from __future__ import annotations

import json
from pathlib import Path

from .models import DeckSpec, SlideKind, deck_json_schema
from .providers import AIProvider


PLANNING_RULES = """
أنت مهندس تعلم ومخرج بصري لعروض تدريبية عربية احترافية.

المهمة:
حوّل الـbrief إلى مخطط عرض كامل صالح للتصيير الآلي. اكتب المحتوى نفسه، لا تكتب
تعليمات عامة للمصمم. اجعل كل شريحة تخدم هدفاً واحداً وادعاءً واحداً.

قواعد المحتوى:
1. ابدأ بغلاف، ثم تشخيص أو سؤال، ثم وحدات قصيرة، ثم تطبيق وتقييم وخلاصة.
2. اجعل ناتج التعلم سلوكاً قابلاً للملاحظة، واربط كل وحدة بتطبيق أو تحقق.
3. النص الظاهر موجز؛ الشرح الكامل يذهب إلى notes.
4. النشاط يجب أن يحدد الزمن والمخرج ومعيار النجاح داخل notes.
5. لا تخترع أرقاماً أو مصادر. ضع المصادر المعروفة في sources، واترك غير المتحقق فارغاً.
6. اكتب العربية الطبيعية مع المصطلح الإنجليزي بين قوسين عند الحاجة.

قواعد التنوع البصري:
- cover للغلاف فقط.
- section لفواصل الوحدات.
- statement لفكرة واحدة قوية أو سؤال محوري.
- concept لمفهوم مع 2-4 عناصر.
- process لسلسلة خطوات سببية أو تشغيلية.
- timeline لمراحل مرتبطة بزمن أو نضج.
- comparison لمقارنة خيارين أو أكثر.
- metrics لأرقام أو مؤشرات حقيقية فقط.
- case_study لحالة وقرار ومفاضلة.
- activity لتطبيق له مخرج.
- quiz لسؤال وخيارات وإجابة صحيحة.
- tool لقالب أو أداة قابلة للاستخدام.
- summary للاستخلاص والالتزام.

لا تستخدم النوع نفسه أكثر من مرتين متتاليتين. لا تجعل كل الشرائح بطاقات. غيّر البنية
بحسب العلاقة في المحتوى: تسلسل، مقارنة، هرم، مراحل، قرار، رقم، حالة، أو تطبيق.

حدود الكثافة:
- العنوان أقل من 12 كلمة متى أمكن.
- body حتى 55 كلمة.
- bullets حتى 5، وكل نقطة حتى 18 كلمة.
- items بين 2 و5 في المعتاد.
- choices بين 3 و4 في الاختبارات.

ملاحظات الميسّر لكل شريحة:
objective | timing | script | instruction | answer_or_debrief | transition

أرجع كائن JSON واحد فقط مطابقاً للمخطط المرفق.
""".strip()


def build_planning_prompt(brief: str, slide_count: int | None = None) -> str:
    target = (
        f"العدد المستهدف للشرائح: {slide_count}." if slide_count else "اختر عدداً مناسباً لمدة التدريب."
    )
    schema_text = json.dumps(deck_json_schema(), ensure_ascii=False, indent=2)
    return f"""{PLANNING_RULES}

{target}

الـbrief:
{brief.strip()}

JSON Schema:
{schema_text}
"""


def plan_deck(provider: AIProvider, brief: str, slide_count: int | None = None) -> DeckSpec:
    deck = provider.generate_deck(build_planning_prompt(brief, slide_count))
    return normalize_deck(deck)


def normalize_deck(deck: DeckSpec) -> DeckSpec:
    if deck.slides and deck.slides[0].kind == SlideKind.AUTO:
        deck.slides[0].kind = SlideKind.COVER
    if deck.slides and deck.slides[0].kind != SlideKind.COVER:
        deck.slides.insert(
            0,
            deck.slides[0].model_copy(
                update={
                    "id": "slide-00-cover",
                    "kind": SlideKind.COVER,
                    "title": deck.title,
                    "subtitle": deck.subtitle,
                    "body": "",
                    "bullets": [],
                    "items": [],
                    "choices": [],
                }
            ),
        )
    for index, slide in enumerate(deck.slides, start=1):
        slide.id = slide.id or f"slide-{index:02d}"
    return deck


def load_deck(path: str | Path) -> DeckSpec:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return DeckSpec.model_validate(data)


def save_deck(deck: DeckSpec, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(deck.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

