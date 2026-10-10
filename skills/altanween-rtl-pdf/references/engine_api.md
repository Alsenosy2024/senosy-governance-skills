# مرجع الـ API الكامل — محرّك التنوين

اقرأ هذا الملف قبل كتابة أي كود. كل التواقيع أدناه مأخوذة من المحرّك مباشرةً. استورد كل شيء عبر
`from altanween_engine import *`.

## جدول المحتويات
- ثوابت التخطيط والألوان
- نظام الثيمات
- محرّك النص (bidi، wrap، line)
- الكروم: header / footer / section_head / body
- المكوّنات: part_divider / timeline / hcards / two_col / stat_band / callout / rtl_flow / expert_note / gold_note
- الأيقونات: icon / icon_badge + القائمة الكاملة + إضافة أيقونة جديدة

---

## ثوابت التخطيط والألوان

```python
W, H            # أبعاد A4 (نقاط)
ML, MR = 56, 56 # الهوامش يسار/يمين
XR              # = W - MR  (الحافة اليمنى للنص — نقطة البداية في RTL)
CW              # = W - ML - MR  (عرض المحتوى)

# الألوان (reportlab Color)
INK    # نص أساسي #1d1d1f
SUBTLE # نص ثانوي #6e6e73
HAIR   # خطوط رفيعة #d2d2d7
CARD, CARD2   # خلفيات كروت فاتحة
WHITE
NAVY  #1A3557   GOLD #C8912A   CYAN #0E9EBB   (ألوان البراند)
GREEN, ORANGE, RED  # ألوان دلالية
NAVY_BG, GOLD_BG, CYAN_BG, ORANGE_BG  # خلفيات فاتحة جداً للألوان

tint(col, alpha)   # لون بشفافية
darken(col, f=0.7) # لون أغمق
```

## نظام الثيمات

```python
THEMES   # dict: رقم الجزء (0..8) -> {'main':لون, 'bg':خلفية فاتحة, 'dark':لون نص غامق, 'accent':لون مكمّل}
```
لتغيير توزيع الألوان على الفصول، عدّل `THEMES` في ملفك بعد الاستيراد، مثلاً:
```python
import altanween_engine as E
E.THEMES[3] = {'main': E.CYAN, 'bg': E.CYAN_BG, 'dark': E.colors.HexColor('#0a6d82'), 'accent': E.NAVY}
```

## محرّك النص

```python
ar(t)                       # يعيد النص العربي مُعالَجاً (reshape + bidi) جاهزاً للرسم
has_ar(t)                   # هل النص يحوي عربية؟
lw(c, t, font, size)        # عرض النص (يحسب الشكل العربي تلقائياً)
line(c, t, font, size, xr, y, col=INK)    # يرسم سطراً محاذى لليمين عند xr (RTL)
line_l(c, t, font, size, xl, y, col=INK)  # يرسم سطراً محاذى لليسار (للإنجليزية)
wrap(c, t, font, size, max_width)         # يعيد قائمة أسطر ملفوفة
para(c, t, font, size, xr, y, lh, mw, col=INK)  # يرسم فقرة ملفوفة، يعيد y الجديد
para_h(c, t, font, size, mw, lh)          # يحسب ارتفاع فقرة دون رسمها (للتخطيط المسبق)
```
الفونتات المسجّلة: `THL` (Light), `THR` (Regular), `THM` (Medium), `THB` (Bold),
`THXB` (عناوين = Medium)، `THNUM` (أرقام عملاقة = Black).

## الكروم

```python
header(c, title_ar, sub_en, theme=0, icon_name=None, kicker=None) -> y
#   شريط لوني علوي + كيكر (تسمية الجزء أعلى) + أيقونة يسار العنوان + عنوان + سطر إنجليزي + خط فاصل.
#   يعيد y لبدء المحتوى تحته.

footer(c, pn, part_label='', theme=0)
#   خط رفيع + PMPmaster.com يسار + تسمية الجزء وسط + رقم الصفحة في نقطة ملوّنة يمين.
#   نادِه قبل c.showPage() لكل صفحة محتوى.

section_head(c, text, y, theme, icon_name=None, sub=None) -> y
#   عنوان قسم بأيقونة خطية داخل دائرة. يعيد y تحته.

body(c, text, y, theme=0, mw=None, col=INK, f='THR', s=11.5, lh=19) -> y
#   فقرة عربية. لا تُنزل s تحت 10.5 في المتن. mw الافتراضي = CW. يعيد y تحت الفقرة.
```

## المكوّنات (كلها تعيد ارتفاعها أو y الجديد — انتبه لكل حالة)

```python
part_divider(c, num, title_ar, sub_en, items, page_no, theme, icon_name=None)
#   صفحة فاصل كاملة (تستدعي showPage داخلياً). num نص الرقم ('1'..'8').
#   items: قائمة عناوين محتويات الجزء (تظهر بأيقونة check). page_no: رقم الصفحة المعروض.

timeline(c, items, y, theme, icons=None) -> total_height
#   خط زمني رأسي RTL. items: [(title, desc), ...]. النقاط مرقّمة تلقائياً على اليمين.
#   icons: قائمة أسماء أيقونات (اختياري). نمط بديل ممتاز للكروت.

hcards(c, items, y, theme, cols=3, icons=None, h=None) -> max_height
#   كروت أفقية. items: [(title, desc), ...]. cols عدد الأعمدة. icons أسماء أيقونات.
#   تطرح القيمة المعادة من y: y -= hcards(...) + gap

two_col(c, left_title, left_items, right_title, right_items, y, theme) -> consumed_height
#   عمودان متقابلان برأسين ملوّنين. *_items قوائم نصوص. العمود الأيمن بلون الثيم، الأيسر رمادي.

stat_band(c, stats, y, theme) -> height (=58)
#   شريط إحصائيات. stats: [(value, label), ...]. القيم بخط ضخم (THNUM).

callout(c, label, text, y, theme, icon_name='check') -> height
#   صندوق نداء أفقي فاتح بأيقونة. label اختياري (مرّر None لإخفائه).

rtl_flow(c, x, y, w, steps, theme, title_ar=None, h=64, icons=None) -> y_bottom
#   مخطط تدفق أفقي. الخطوة 1 يميناً، الأسهم تتجه يساراً (اتجاه القراءة العربي).
#   steps: قائمة نصوص (يمكن أن تحوي \n لسطرين). x عادةً ML، w عادةً CW. icons اختياري.

expert_note(c, text, y, theme, style='box') -> height
#   رأي خبير. style='quote' (خط جانبي ملوّن بلا خلفية صلبة) أو 'box' (صندوق ملوّن ممتلئ نص أبيض).
#   نوّع بين النمطين عبر الصفحات لكسر الرتابة (مثلاً quote للأرقام الفردية، box للزوجية).

gold_note(c, text, y, theme, icon_name='bulb') -> height
#   ملاحظة ذهبية بحدود + أيقونة في دائرة. للتلميحات والقواعد الذهبية.
```

نمط الاستخدام النموذجي (تتبّع y يدوياً):
```python
y = header(c, ...)
y = body(c, '...', y, TH) - 8           # body يعيد y جديداً
y -= callout(c, ..., y, TH) + 12        # المكوّنات التي تعيد ارتفاعاً: اطرحها
y = rtl_flow(c, ML, y, CW, [...], TH) - 14   # rtl_flow يعيد y سفلي
y -= expert_note(c, '...', y, TH, 'quote')
```

## الأيقونات

```python
icon(c, name, cx, cy, r, col)
#   يرسم أيقونة خطية مركزها (cx,cy) نصف قطرها r باللون col. سُمك الخط يتناسب مع r تلقائياً.

icon_badge(c, name, cx, cy, r, col, bg=None)
#   نفس الأيقونة داخل دائرة خلفية فاتحة (افتراضياً tint من اللون). bg مخصّص اختياري.
```

الأسماء المتاحة (22):
`target` (هدف)، `compass` (بوصلة)، `layers` (طبقات)، `bulb` (فكرة)، `gear` (ترس)،
`shield` (درع)، `chart` (مخطط)، `people` (أشخاص)، `doc` (مستند)، `bot` (روبوت)،
`brain` (دماغ)، `link` (رابط)، `search` (بحث)، `flag` (علم)، `check` (صح)، `route` (مسار)،
`scale` (ميزان)، `building` (مبنى)، `rocket` (صاروخ)، `map` (خريطة)، `quote` (اقتباس)، `star` (نجمة).

### إضافة أيقونة جديدة
أضف فرعاً في دالة `icon()` داخل المحرّك. كل الإحداثيات نسبية لـ `r` (نصف القطر) ليتكيّف الشكل مع أي حجم.
استخدم العناصر الأولية: `c.circle`, `c.line`, `c.rect`, `c.roundRect`, ومسارات `c.beginPath()` مع
`moveTo/lineTo/curveTo`. ابدأ بـ `ic_setup(c, col, line_width)` لضبط الستايل. مثال (أيقونة الهدف):
```python
elif name=='target':
    c.circle(cx,cy,r,stroke=1,fill=0); c.circle(cx,cy,r*0.55,stroke=1,fill=0)
    c.setFillColor(col); c.circle(cx,cy,r*0.16,stroke=0,fill=1)
```
