# نمط البناء بتمريرتين والفهرس التلقائي

المشكلة: الفهرس يحتاج أرقام صفحات الفواصل (بداية كل جزء)، لكن هذه الأرقام لا تُعرف إلا بعد بناء الوثيقة.
الحل: ابنِ مرتين. التمريرة الأولى تتعلّم الأرقام، الثانية تستخدمها.

## الهيكلة الموصى بها (ثلاثة ملفات)

افصل المشروع إلى:
- `front.py` — الغلاف، المنهجية، الفهرس، كيف تقرأ، المسرد. كلها **دوال** (لا تُنفَّذ عند الاستيراد).
- `parts.py` — `part1()` .. `partN()` + `conclusion()`. كل دالة جزء تسجّل رقم صفحة فاصلها في `DIVPAGES`.
- `build.py` — المنظّم: يستورد بنظافة، يرتّب الاستدعاءات، يبني مرتين.

السبب في جعل كل شيء دوالاً: حتى يتحكّم المنظّم في ترتيب التنفيذ والقماش، ويعيد البناء مرتين بنظافة.

## عدّاد الصفحات والقماش المشترك

في `front.py`:
```python
from altanween_engine import *
from reportlab.pdfgen import canvas as _cv

OUT = '/mnt/user-data/outputs/<name>.pdf'
c = _cv.Canvas(OUT, pagesize=A4)
PG = [0]   # عدّاد قابل للتعديل بالإشارة (list) ليُرى عبر الموديولات

def newpage(label='', theme=0):
    PG[0]+= 1; footer(c, PG[0], label, theme); c.showPage()

def fpage():   # للفواصل: يزيد العدّاد ويعيد الرقم (الفاصل يستدعي showPage بنفسه)
    PG[0] += 1; return PG[0]
```

## تسجيل أرقام الفواصل

في `parts.py`، كل دالة جزء تبدأ بتسجيل رقم فاصلها:
```python
DIVPAGES = {}   # رقم الجزء -> رقم صفحة الفاصل

def part1():
    TH = 1
    DIVPAGES[1] = fpage()
    part_divider(c, '1', 'عنوان الجزء', 'Part One — ...',
                 ['نقطة 1','نقطة 2','نقطة 3'], DIVPAGES[1], TH, icon_name='target')
    LBL = 'الجزء الأول — ...'
    y = header(c, '...', '...', TH, icon_name='compass', kicker='الجزء الأول')
    y = body(c, '...', y, TH) - 8
    # ... بقية الصفحات، كل صفحة محتوى تنتهي بـ newpage(LBL, TH)
    newpage(LBL, TH)
```

## الفهرس الذي يقبل خريطة الصفحات

في `front.py`، اجعل `toc` يأخذ `page_map` ويحقن الأرقام:
```python
TOC = [  # (عنوان عربي, عنوان إنجليزي, رقم ثابت أو '' , أيقونة, رقم الجزء)
    ('جدول المصطلحات', 'Glossary', '5', 'doc', 0),   # رقم ثابت معروف مسبقاً
    ('الجزء الأول — ...', 'Part 1', '', 'target', 1), # '' => يُحقن من page_map[1]
    # ...
    ('الخاتمة', 'Conclusion', '', 'check', 0),
]

def toc(page_map):
    y = header(c, 'المحتويات', 'Table of Contents', 0, icon_name='map')
    for t_ar, t_en, fixed, ic, partno in TOC:
        pg = fixed if fixed else str(page_map.get(partno, ''))
        # ... ارسم الصف بكبسولة رقم بلون THEMES[partno]
    newpage('المحتويات', 0)
```
ملاحظة: عناصر معروفة الموضع مسبقاً (المسرد، الخاتمة إن كانت ثابتة) أعطها رقماً ثابتاً.

## المنظّم بتمريرتين

في `build.py`:
```python
import sys, importlib
sys.path.insert(0, '<dir>')

def build(path, known_map):
    # تحميل نظيف في كل تمريرة (قماش جديد، عدّاد صفر)
    for m in ['altanween_engine','front','parts']:
        if m in sys.modules: del sys.modules[m]
    import front as F
    F.c._filename = path            # وجّه القماش لهذا المسار
    import parts as P
    # الترتيب:
    F.cover(); F.methodology(); F.toc(known_map); F.how_to_read(); F.glossary()
    P.part1(); P.part2(); ... ; P.conclusion()
    F.c.save()
    return dict(P.DIVPAGES), F.PG[0]

if __name__ == '__main__':
    m1, _ = build('/tmp/pass1.pdf', {})           # تمريرة 1: خريطة فارغة، نتعلّم الأرقام
    m2, total = build('/mnt/user-data/outputs/<name>.pdf', m1)  # تمريرة 2: نهائية بالأرقام
    print('FINAL', total, m2)
```

نقاط حرجة:
- **رتّب الاستدعاءات يدوياً في `build()`** — لا تعتمد على تنفيذ تلقائي عند الاستيراد. أزل أي
  `cover()` أو `part1()` معلّقة في نهاية الملفات.
- **تأكد أن كل `partN()` مُستدعاة فعلاً** في المنظّم. خطأ شائع: تعريف الدالة ونسيان ندائها — فتختفي
  صفحات الجزء كلها ويُطبع الفاصل التالي مباشرة. تحقّق من تطابق عدد الأجزاء المطبوعة.
- **أرقام الفهرس = أرقام الفواصل** (بداية كل جزء)، وهي ما يُرجعه `DIVPAGES`.
