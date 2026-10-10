---
name: arabic-pdf
description: >
  إنشاء ملفات PDF عربية احترافية بالكامل مع دعم RTL باستخدام ReportLab وNotoNaskhArabic.
  استخدم هذه المهارة دائماً عند طلب: إنشاء PDF عربي، تقرير PDF، مستند PDF ثنائي اللغة،
  أو أي ملف PDF يحتوي على نص عربي أو محتوى مُصدَّر كـ PDF.
  تشمل المهارة: Brand colors لـ Professional Engineers، Stat cards، Info boxes،
  Quote blocks، CTA، Footer، وTemplate جاهز للتشغيل.
  يجب تفعيل هذه المهارة حتى لو لم يُذكر "مهارة" صراحةً — فقط إذا كان المطلوب ملف PDF عربي.
---

# SKILL: Arabic RTL PDF Generation
**Owner:** Dr. Ahmed Al-Senosy — Professional Engineers & Ailigent.ai
**Version:** 2.0 | **Tested:** April 2026
**Reference script:** `ai_article_pdf.py` (working implementation)

---

## 1. WHAT THIS SKILL DOES

Generates professional, fully RTL Arabic PDF documents using:
- **ReportLab** for PDF rendering via canvas API
- **arabic_reshaper** for correct Arabic glyph shaping
- **python-bidi** for right-to-left text direction (BiDi algorithm)
- **NotoNaskhArabic** font for clean, professional Arabic rendering

Output: A4, multi-page, branded PDF with headers, stat cards, info boxes, quote blocks, footers.

---

## 2. TRIGGER CONDITIONS

Use this skill whenever the user asks to:
- إنشاء PDF عربي / Arabic PDF
- Create a branded document / report / article as PDF
- Export any Arabic content to a downloadable PDF file
- Generate a bilingual (AR + EN) professional document

**Trigger keywords:** `pdf`, `ملف`, `مستند`, `تقرير`, `اصدر`, `صدرلي`, `احفظ كـ pdf`

---

## 3. ENVIRONMENT SETUP

### 3.1 Required Python Libraries
```bash
pip install reportlab arabic-reshaper python-bidi --break-system-packages
```

### 3.2 Required Fonts — Download Once
```python
import urllib.request

fonts = [
    (
        'https://github.com/google/fonts/raw/main/ofl/notonaskharabic/NotoNaskhArabic%5Bwght%5D.ttf',
        '/home/claude/NotoNaskhArabic-Regular.ttf'
    ),
    (
        'https://github.com/google/fonts/raw/main/ofl/notonaskharabic/NotoNaskhArabic%5Bwght%5D.ttf',
        '/home/claude/NotoNaskhArabic-Bold.ttf'
    ),
]
for url, path in fonts:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req).read()
    with open(path, 'wb') as f:
        f.write(data)
    print(f'Downloaded: {path}')
```

> NOTE: Both Regular and Bold use the same variable font file.
> ReportLab treats them as separate named fonts ('AR' and 'ARB').

### 3.3 Font Registration (Always at top of script)
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('AR',  '/home/claude/NotoNaskhArabic-Regular.ttf'))
pdfmetrics.registerFont(TTFont('ARB', '/home/claude/NotoNaskhArabic-Bold.ttf'))
```

---

## 4. CORE ARABIC RENDERING RULES

### RULE 1 — Always reshape + bidi before drawing
```python
import arabic_reshaper
from bidi.algorithm import get_display

def ar(text):
    """Convert Arabic string for correct ReportLab rendering."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)
```

### RULE 2 — Always use drawRightString for Arabic body text
```python
# CORRECT — Arabic body text
c.drawRightString(x_right, y, ar('نص عربي'))

# CORRECT — Centered titles (both AR and EN)
c.drawCentredString(W/2, y, ar('عنوان مركزي'))

# WRONG — Never use drawString for Arabic body
# c.drawString(x, y, ar('نص عربي'))   ← alignment will be wrong
```

### RULE 3 — No inline English inside Arabic body strings
```python
# WRONG — mixing breaks reshaping
text = 'تعلم Python الآن'

# CORRECT — keep Arabic pure, add EN as separate label/badge
ar_text = 'تعلم البرمجة الآن'
en_label = 'Python'
# Draw ar_text with drawRightString, then draw en_label separately
```

### RULE 4 — Word-wrap by space-splitting and measuring
```python
def wrap_arabic(c, text, font, size, max_width):
    """Word-wrap Arabic text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = ' '.join(current + [word])
        w = c.stringWidth(ar(test), font, size)
        if w <= max_width or not current:
            current.append(word)
        else:
            lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines
```

### RULE 5 — Measure card height BEFORE drawing
```python
# Always calculate total height needed before you draw
line_h = 20
padding = 14
lines = wrap_arabic(c, text, 'AR', 12, max_width)
total_h = padding * 2 + len(lines) * line_h

# Only then draw the background rect
c.roundRect(x, y - total_h, w, total_h, 8, fill=1, stroke=0)
```

---

## 5. PAGE SETUP

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

W, H = A4   # 595.27 x 841.89 points

c = canvas.Canvas('/path/to/output.pdf', pagesize=A4)
c.setTitle('عنوان المستند')
c.setAuthor('Dr. Ahmed Al-Senosy')
c.setSubject('موضوع المستند')

# Draw page 1 content...
c.showPage()   # ← Always call before starting a new page

# Draw page 2 content...
c.save()       # ← Finalize the PDF
```

---

## 6. BRAND COLOR PALETTE (Professional Engineers)

```python
from reportlab.lib import colors

NAVY      = colors.HexColor('#0a1f44')   # Primary dark
CYAN      = colors.HexColor('#0e7490')   # Primary accent
CYAN_LT   = colors.HexColor('#e0f2fe')   # Light cyan background
CYAN_BRD  = colors.HexColor('#38bdf8')   # Bright cyan (headers/highlights)
ORANGE    = colors.HexColor('#f97316')   # Warning / secondary accent
ORANGE_LT = colors.HexColor('#fff7ed')   # Light orange background
GOLD      = colors.HexColor('#f59e0b')   # Gold accent
WHITE     = colors.white
GRAY      = colors.HexColor('#64748b')   # Muted text
DARK      = colors.HexColor('#1e293b')   # Body text
LIGHT_BG  = colors.HexColor('#f8fafc')   # Page background tint
```

---

## 7. REUSABLE DRAWING FUNCTIONS

### 7.1 Draw Arabic Lines (right-aligned)
```python
def draw_ar_lines(c, lines, font, size, x_right, y_start, line_h, color=DARK):
    """Draw a list of right-aligned Arabic lines. Returns final y position."""
    c.setFont(font, size)
    c.setFillColor(color)
    y = y_start
    for line in lines:
        c.drawRightString(x_right, y, ar(line))
        y -= line_h
    return y
```

### 7.2 Gradient Header (Page 1)
```python
def draw_gradient_header(c):
    # Main navy block
    c.setFillColor(NAVY)
    c.rect(0, H - 200, W, 200, fill=1, stroke=0)
    # Cyan accent bar at bottom of header
    c.setFillColor(CYAN)
    c.rect(0, H - 205, W, 8, fill=1, stroke=0)
    # Decorative circle (background)
    c.setFillColor(colors.HexColor('#112244'))
    c.circle(60, H - 30, 120, fill=1, stroke=0)
    # Gold accent line
    c.setFillColor(GOLD)
    c.rect(40, H - 190, 80, 4, fill=1, stroke=0)
```

### 7.3 Mini Header (Page 2+)
```python
def draw_mini_header(c, subtitle_ar):
    c.setFillColor(NAVY)
    c.rect(0, H - 55, W, 55, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.rect(0, H - 58, W, 4, fill=1, stroke=0)
    c.setFont('ARB', 13)
    c.setFillColor(WHITE)
    c.drawCentredString(W/2, H - 36, ar(subtitle_ar))
```

### 7.4 Section Header Bar
```python
def draw_section_header(c, text_ar, y, bg=NAVY, text_color=WHITE):
    """Draws a full-width rounded section header. Returns y for next element."""
    c.setFillColor(bg)
    c.roundRect(35, y, W - 70, 34, 6, fill=1, stroke=0)
    c.setFont('ARB', 13)
    c.setFillColor(text_color)
    c.drawCentredString(W/2, y + 10, ar(text_ar))
    return y - 20
```

### 7.5 Stat Card
```python
def draw_stat_box(c, x, y, w, h, value_ar, label_ar, bg=CYAN_LT, border=CYAN):
    """Draw a KPI stat card with shadow, border top, value and label."""
    # Shadow
    c.setFillColor(colors.HexColor('#00000015'))
    c.roundRect(x + 3, y - 3, w, h, 8, fill=1, stroke=0)
    # Box
    c.setFillColor(bg)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
    # Top accent border
    c.setFillColor(border)
    c.roundRect(x, y + h - 6, w, 6, 4, fill=1, stroke=0)
    # Value (large)
    c.setFont('ARB', 16)
    c.setFillColor(NAVY)
    c.drawCentredString(x + w/2, y + h/2 + 4, ar(value_ar))
    # Label (small)
    c.setFont('AR', 10)
    c.setFillColor(GRAY)
    c.drawCentredString(x + w/2, y + h/2 - 16, ar(label_ar))
```

**Usage — 3 equal cards:**
```python
bw = (W - 90) / 3
gap = 10
y_card = current_y - 80

draw_stat_box(c, 35,              y_card, bw, 80, '68%',  'النسبة الأولى',  CYAN_LT,   CYAN)
draw_stat_box(c, 35 + bw + gap,   y_card, bw, 80, '95%',  'النسبة الثانية', ORANGE_LT, ORANGE)
draw_stat_box(c, 35+(bw+gap)*2,   y_card, bw, 80, '16%',  'النسبة الثالثة', colors.HexColor('#fef9c3'), GOLD)
```

### 7.6 Info / Content Box (with right border)
```python
def draw_info_box(c, lines_ar, x, y, w, bg=CYAN_LT, border_color=CYAN):
    """Draw a rounded content box. Returns total height used."""
    padding = 14
    line_h = 20
    total_h = padding * 2 + len(lines_ar) * line_h + 4

    # Shadow
    c.setFillColor(colors.HexColor('#00000010'))
    c.roundRect(x + 3, y - total_h - 3, w, total_h, 8, fill=1, stroke=0)
    # Box
    c.setFillColor(bg)
    c.roundRect(x, y - total_h, w, total_h, 8, fill=1, stroke=0)
    # Right border strip
    c.setFillColor(border_color)
    c.roundRect(x + w - 6, y - total_h, 6, total_h, 4, fill=1, stroke=0)

    # Text lines
    ty = y - padding - 16
    for line in lines_ar:
        c.setFont('AR', 11)
        c.setFillColor(DARK)
        c.drawRightString(x + w - 14, ty, ar(line))
        ty -= line_h

    return total_h + 12
```

### 7.7 Quote Block (dark navy)
```python
def draw_quote_box(c, lines_ar, attribution_ar, y):
    """Full-width dark quote block. Returns height used."""
    padding = 18
    line_h = 24
    total_h = padding * 2 + len(lines_ar) * line_h + 28
    x, w = 35, W - 70

    c.setFillColor(NAVY)
    c.roundRect(x, y - total_h, w, total_h, 8, fill=1, stroke=0)
    # Cyan right accent
    c.setFillColor(CYAN_BRD)
    c.rect(x + w - 5, y - total_h, 5, total_h, fill=1, stroke=0)
    # Decorative opening quote mark
    c.setFont('ARB', 36)
    c.setFillColor(colors.HexColor('#1e4a6e'))
    c.drawString(x + 10, y - 40, '\u201c')

    ty = y - padding - 20
    for line in lines_ar:
        c.setFont('ARB', 13)
        c.setFillColor(CYAN_BRD)
        c.drawCentredString(W/2, ty, ar(line))
        ty -= line_h

    # Attribution
    c.setFont('AR', 10)
    c.setFillColor(colors.HexColor('#93c5fd'))
    c.drawCentredString(W/2, ty - 4, ar(attribution_ar))

    return total_h + 16
```

### 7.8 Footer (every page)
```python
def draw_footer(c, page_num):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, 50, fill=1, stroke=0)
    c.setFillColor(CYAN_BRD)
    c.rect(0, 48, W, 3, fill=1, stroke=0)
    # Website (left side — English OK in footer)
    c.setFont('AR', 9)
    c.setFillColor(WHITE)
    c.drawString(40, 18, 'PMPmaster.com | ProfessionalEngineers.us')
    # Page number (right side)
    c.setFillColor(GOLD)
    c.drawRightString(W - 40, 18, str(page_num))
```

### 7.9 CTA Box (Call to Action)
```python
def draw_cta_box(c, y):
    """Contact / CTA block at end of document."""
    cta_h = 90
    c.setFillColor(NAVY)
    c.roundRect(35, y - cta_h, W - 70, cta_h, 10, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.roundRect(35, y - 6, W - 70, 6, 4, fill=1, stroke=0)

    c.setFont('ARB', 13)
    c.setFillColor(WHITE)
    c.drawCentredString(W/2, y - 28, ar('تواصل معنا الآن'))

    c.setFont('AR', 11)
    c.setFillColor(CYAN_BRD)
    c.drawCentredString(W/2, y - 50, ar('PMPmaster.com | 0541323774 | 0542341634'))

    c.setFont('AR', 10)
    c.setFillColor(colors.HexColor('#93c5fd'))
    c.drawCentredString(W/2, y - 70, ar('برامج الماجستير والدكتوراه: ProfessionalEngineers.us'))
```

---

## 8. Y-COORDINATE SYSTEM (CRITICAL)

ReportLab's Y axis starts from the **BOTTOM** of the page.

```
H = 841.89  ← TOP of page
│
│  Content flows DOWNWARD by subtracting from y
│  y = H - 200  (200pt from top)
│  y -= 30      (move 30pt further down)
│
0           ← BOTTOM of page (footer lives here)
```

**Standard margins:**
- Left/Right content: x=35 to x=W-35 (560pt usable width)
- Right text anchor: x_right = W - 50
- Top content start: y = H - 220 (after 200pt header)
- Bottom content limit: y = 70 (above 50pt footer)

---

## 9. FULL SCRIPT TEMPLATE

```python
#!/usr/bin/env python3
"""
Arabic RTL PDF Template
Dr. Ahmed Al-Senosy — Professional Engineers
"""

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Fonts ─────────────────────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont('AR',  '/home/claude/NotoNaskhArabic-Regular.ttf'))
pdfmetrics.registerFont(TTFont('ARB', '/home/claude/NotoNaskhArabic-Bold.ttf'))

# ── Colors ────────────────────────────────────────────────────────────────────
NAVY     = colors.HexColor('#0a1f44')
CYAN     = colors.HexColor('#0e7490')
CYAN_LT  = colors.HexColor('#e0f2fe')
CYAN_BRD = colors.HexColor('#38bdf8')
GOLD     = colors.HexColor('#f59e0b')
ORANGE   = colors.HexColor('#f97316')
ORANGE_LT= colors.HexColor('#fff7ed')
WHITE    = colors.white
GRAY     = colors.HexColor('#64748b')
DARK     = colors.HexColor('#1e293b')
LIGHT_BG = colors.HexColor('#f8fafc')

W, H = A4

# ── Arabic helpers ─────────────────────────────────────────────────────────────
def ar(text):
    return get_display(arabic_reshaper.reshape(text))

def wrap_arabic(c, text, font, size, max_width):
    words = text.split()
    lines, current = [], []
    for word in words:
        test = ' '.join(current + [word])
        if c.stringWidth(ar(test), font, size) <= max_width or not current:
            current.append(word)
        else:
            lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines

def draw_ar_lines(c, lines, font, size, x_right, y_start, line_h, color=None):
    c.setFont(font, size)
    c.setFillColor(color or DARK)
    y = y_start
    for line in lines:
        c.drawRightString(x_right, y, ar(line))
        y -= line_h
    return y

# ── [Paste drawing functions from Section 7 here] ─────────────────────────────
# draw_gradient_header, draw_mini_header, draw_section_header,
# draw_stat_box, draw_info_box, draw_quote_box, draw_footer, draw_cta_box

# ── Pages ─────────────────────────────────────────────────────────────────────
def page1(c):
    draw_gradient_header(c)
    # ... page 1 content ...
    draw_footer(c, 1)

def page2(c):
    draw_mini_header(c, 'العنوان الفرعي للصفحة الثانية')
    # ... page 2 content ...
    draw_footer(c, 2)

# ── Main ──────────────────────────────────────────────────────────────────────
OUTPUT = '/mnt/user-data/outputs/output.pdf'

c = canvas.Canvas(OUTPUT, pagesize=A4)
c.setTitle('عنوان المستند')
c.setAuthor('Dr. Ahmed Al-Senosy - Professional Engineers')

page1(c)
c.showPage()
page2(c)
c.save()
print(f'PDF saved: {OUTPUT}')
```

---

## 10. COMMON BUGS & FIXES

| Bug | Cause | Fix |
|-----|-------|-----|
| Arabic text appears reversed | Missing `ar()` call | Always call `ar(text)` before drawing |
| Text left-aligned | Using `drawString` instead of `drawRightString` | Switch to `drawRightString(x_right, y, ar(text))` |
| Text cut mid-word | Character-based wrapping | Use `wrap_arabic()` — split by space, measure whole words |
| Cards overflow the page | No height pre-calculation | Always call `measure_card()` / calculate `total_h` BEFORE drawing |
| Arabic glyphs show as boxes | Wrong font or missing font file | Verify TTF path, re-download NotoNaskhArabic |
| English in Arabic body breaks layout | Inline EN text inside Arabic string | Separate EN labels/badges, draw Arabic body 100% Arabic |
| Second page content missing | Forgot `c.showPage()` | Call `c.showPage()` BEFORE drawing page 2 content |
| PDF not saved | Forgot `c.save()` | Always call `c.save()` at the very end |
| `setFillAlpha` not resetting | Alpha persists across draws | Always call `c.setFillAlpha(1)` after using transparency |

---

## 11. TYPOGRAPHY SCALE

| Use case | Font | Size |
|----------|------|------|
| Page main title | ARB | 22–26 |
| Section header | ARB | 13–15 |
| Card value (KPI) | ARB | 16–18 |
| Body paragraph | AR | 11–12 |
| Card label | AR | 9–10 |
| Footer text | AR | 9 |
| Source citations | AR | 10 |
| Quote text | ARB | 13 |

---

## 12. STANDARD PAGE LAYOUT (Y positions for A4)

```
H = 841  ─────────────────── absolute top
H - 200  ─────────────────── header ends / content starts (page 1)
H - 58   ─────────────────── mini-header ends / content starts (page 2+)
H - 230  ─────────────────── first content element top (after header)

           [content flows downward, y decreases]

70       ─────────────────── bottom content limit
50       ─────────────────── footer top
0        ─────────────────── absolute bottom
```

---

## 13. CHECKLIST BEFORE FINALIZING PDF

- [ ] All Arabic text passed through `ar()` before drawing
- [ ] All Arabic body text uses `drawRightString` not `drawString`
- [ ] No inline English inside Arabic body strings
- [ ] `wrap_arabic()` used for any paragraph text
- [ ] `total_h` calculated before drawing each box/card
- [ ] Each new page preceded by `c.showPage()`
- [ ] `draw_footer(c, page_num)` called on every page
- [ ] `c.save()` called at the very end
- [ ] Output path is `/mnt/user-data/outputs/` for user access
- [ ] `present_files([output_path])` called after saving

---

## 14. INTEGRATION WITH OPENCLAW / TELEGRAM BOT

When this skill is triggered via OpenClaw/Moltbot on Telegram:

1. Bot receives user request (e.g., "اعمل PDF للمقال ده")
2. Bot calls Claude API with this SKILL.md as system context
3. Claude generates the Python script using the template above
4. Script is executed via bash in the container
5. Output PDF is saved to `/mnt/user-data/outputs/`
6. File is sent back to user via Telegram `sendDocument` API

**Telegram send snippet:**
```python
import requests

def send_pdf_to_telegram(bot_token, chat_id, pdf_path, caption=''):
    url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
    with open(pdf_path, 'rb') as f:
        requests.post(url, data={
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': 'HTML'
        }, files={'document': f})
```

---

## 15. REFERENCE IMPLEMENTATION

Full working example: See `ai_article_pdf.py`
- 2-page A4 PDF
- NotoNaskhArabic fonts (AR + ARB)
- Gradient header, stat cards, info boxes, quote block, CTA, footer
- 100% RTL Arabic body text, verified clean rendering
