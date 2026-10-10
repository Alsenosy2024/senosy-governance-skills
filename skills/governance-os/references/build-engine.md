# المحرك: البناء والطباعة — ومصائدها الحقيقية

اقرأ هذا **قبل** تشغيل المحرك. كل بند هنا مصيدة وقعنا فيها فعلاً وأصلحناها.

## 1. بنية ملفات البيانات

المحرك يقرأ من مجلد العمل:

| الملف | يحتوي |
|---|---|
| `data_core.py` | `META · ENACTMENT · SOURCES · DEPTS · PLATFORMS · ROLES · PRINCIPLES · CHAIN · DOA · DOA_NOTE · DEC · SOD · RACI · MATURITY · MATURITY_TARGET · ROADMAP` |
| `data_policies.py` | `POLICIES · CONDITIONAL` |
| `data_sops_*.py` | أي عدد من الملفات؛ المحرك يجمع تلقائياً كل قائمة إجراءات فيها |
| `data_registers.py` | `CONTROLS · RISKS · METRICS · SLAS · FORMS · REGISTERS · SYS_PERMS` |
| `data_strategy.py` | `HORIZON · MARKET · ASSUMPTIONS · VISION · MISSION · VALUES · BHAG · BHAG_TEST · CENTRAL_TENSION · PERSPECTIVES · INITIATIVES · STRAT_RISKS · CADENCE · CLOSING` |
| `data_jobs.py` | `NOTE · BANDS · JOBS · EXTERNAL · GAPS` |
| `data_guides.py` | `GUIDES · DISCLAIMER` |

الإدارات تُعرَّف مرة في `DEPTS`، والمحرك يجمّع الإجراءات والسياسات والمؤشرات لكل إدارة **تلقائياً** من حقل `dept`.

## 2. الترتيب الإلزامي للأجزاء

`٠ الاستراتيجية → ١ الطبقة الحاكمة → ٢ السياسات → ٣ العمليات التقاطعية → ٤ الإدارات → ٥ الأوصاف الوظيفية → ٦ السجلات المركزية → ٧ التطبيق والنضج → ٨ الأدلة الإرشادية`

الاستراتيجية أولاً لأنها تعطي **السبب**؛ والطبقة الحاكمة قبل الإجراءات لأنها تعطي **السلطة**.

## 3. مصيدة الطباعة #1 — لا تستخدم صناديق A4 ثابتة

**الخطأ:** جعل كل قسم `div` بارتفاع `297mm` ورأس/تذييل `position:absolute`.
**النتيجة:** القسم الأطول من صفحة **يفيض ويتداخل**، والأقصر يترك ثلث صفحة أبيض، وترقيم الصفحات يصير ترقيم أقسام.

**الصحيح:** المحتوى **يتدفّق**، والرأس/التذييل **عناصر جارية**:

```css
.page-header{position:running(rh)}  .page-footer{position:running(rf)}
@page{
  size:A4; margin:17mm 13mm 15mm;
  @top-right{content:element(rh)}
  @bottom-right{content:element(rf)}
  @bottom-left{content:"صفحة " counter(page)}
}
.sheet{break-before:page}
figure,tr,.callout,.cell{break-inside:avoid}
h1,h2,h3,h4,figcaption,.object-head{break-after:avoid}
thead{display:table-header-group}
@media print{ body{font-size:8pt} }
```

## 4. مصيدة الطباعة #2 — العربية داخل SVG لا تتشكّل في WeasyPrint

**العَرَض:** الحروف تظهر مفكوكة ومقلوبة داخل `<svg><text>` في الـPDF فقط (المتصفح سليم).
**السبب:** WeasyPrint لا يطبّق تشكيل الحروف ولا خوارزمية bidi داخل SVG.
**الحل:** وضع PDF منفصل يُشكّل النص **مسبقاً** — ولا يُفعَّل في نسخة HTML (وإلا انقلب النص في المتصفح):

```python
PDF_MODE = os.environ.get("PDF_MODE") == "1"
if PDF_MODE:
    import arabic_reshaper
    from bidi.algorithm import get_display
    def shape(t): return get_display(arabic_reshaper.reshape(str(t)))
else:
    def shape(t): return str(t)
ES = lambda s: html.escape(shape(s))   # للنصوص داخل SVG فقط
```

المعرّفات اللاتينية (`CTL-22`) تبقى بـ`E()` عادية مع `dir="ltr"`.

## 5. مصيدة الطباعة #3 — الروابط الإنجليزية تنقلب داخل فقرة عربية

`https://www.iso.org/standard/50003` تظهر `//:https ... standard html.50003`.
**الحل:** `<bdi dir="ltr">…</bdi>` حول أي URL أو نص لاتيني طويل داخل نص عربي.

## 6. مصيدة الرسم — البتر الصامت

**لا تقصّ النص** (`lines[:4]`). الصندوق **ينمو** ليستوعبه:

```python
def wrap(text, per):   # بلا أي بتر
    ...
h = max(22 + len(text_lines)*13, 20 + len(actor_lines)*12, 42)
```

خطوة مبتورة في خريطة تدفق = إجراء ناقص لا يلاحظه أحد. هذا أسوأ من رسم قبيح.

## 7. مصيدة الخطوط

بيئة التنفيذ غالباً **بلا خطوط عربية**. ثبّت خطاً قبل التصدير وإلا خرج الـPDF مربعات:

```bash
mkdir -p ~/.fonts && cp <arabic-font>.ttf ~/.fonts/ && fc-cache -f
fc-list | grep -i arab   # تحقق
```
وأدرج اسم الخط في `font-family` بعد الخطوط المفضّلة.

## 8. مصيدة زمن التنفيذ — التصدير على دفعتين

الوثائق الكبيرة (>300 صفحة) تتجاوز سقف زمن استدعاء الشِل. صدّر على أجزاء وادمج، مع ترقيم صفحات متصل:

```bash
PDF_MODE=1 PART=A python3 build.py && python3 -c "
from weasyprint import HTML; HTML(filename='...pdfsrca.html').write_pdf('pA.pdf')"
nA=$(عدد صفحات pA)
PDF_MODE=1 PART=B PAGE_OFFSET=$nA python3 build.py && ... write_pdf('pB.pdf')
# ثم دمج pA + pB بـ pypdf
```
`PAGE_OFFSET` يُحقن كـ`style="counter-reset:page N"` على `<main>`.
لا تستخدم `counter(pages)` (الإجمالي) لأنه يكسر عند التقسيم — اكتفِ بـ`counter(page)`.

**لا تشغّل عملية في الخلفية** — بيئة الشِل تقتلها بين الاستدعاءات.

## 9. الجداول

- `table-layout:fixed` + `overflow-wrap:anywhere` للجداول العادية.
- `table-layout:auto` للجداول الكثيفة (10 أعمدة) وإلا تنضغط الأعمدة المهمة.
- أعمدة جدول الخطوات بعرض منطقي: `# 4% · الدور 17% · الفعل 47% · النظام 11% · الزمن 11% · الضابط 10%`.

## 10. التحقق الإلزامي

```bash
python3 verify.py     # صفر إخفاقات — لا تسليم قبلها
```
يفحص: كل نقطة اعتماد لها سطر DOA موجود · كل ضابط/مؤشر/سياسة مُشار إليه معرَّف · كل خطر له ضابط ومؤشر · لا ضابط بلا طريقة اختبار · لا مؤشر بلا استجابة · لا إجراء بلا خطوات/اعتماد/ضابط/دليل/SLA/استثناء/تصعيد · لا ضابط يتيم.

**ثم افحص الـPDF بصرياً.** `pdftoppm -f N -l N -r 58 -png out.pdf p` ثم اقرأ الصورة فعلياً. الـvalidator لا يرى التداخل البصري.
