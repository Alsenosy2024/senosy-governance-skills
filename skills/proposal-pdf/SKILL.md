---
name: proposal-pdf
description: >-
  إنشاء عرض فني أو مالي عربي احترافي بصيغة PDF من نص أو Markdown، مع دعم RTL
  والهوية البصرية والهيدر والفوتر. استخدمها للعروض والمقترحات وعروض الأسعار،
  وليس لمعالجة ملفات PDF القائمة معالجة عامة.
---

# SKILL: Arabic RTL Proposal PDF Generator
**Owner:** Dr. Ahmed Al-Senosy — Ailigent AI
**Version:** 1.0 | **Tested:** June 2026
**Reference script:** `build_proposal_pdf.py`
**Reference output:** `proposal.pdf` (render and verify before delivery)

---

## 1. TRIGGER CONDITIONS

Use this skill when the user asks to:
- إنشاء عرض فني / مالي / خدمي كـ PDF
- تحويل ملف `.md` أو نص عرض إلى PDF احترافي
- بناء proposal / quotation / service offer بفونت عربي وهيدر/فوتر

**Trigger keywords:** `عرض`, `proposal`, `pdf عرض`, `اعمل عرض`, `نسخة pdf`, `اعمل ملف`, `/proposal-pdf`

---

## 2. STACK

| Layer | Tool |
|-------|------|
| Font | **Thmanyah Sans** — `~/Library/Fonts/thmanyah-sans-*.ttf` |
| Rendering | **Chrome headless** `--print-to-pdf` |
| Layout | HTML + CSS (RTL, `direction:rtl`) |
| Running header/footer | **Table trick** — `<table><thead>` repeats on every page |
| Page numbers | **`@page @bottom-left`** — `counter(page)` + hardcoded total |
| Page count | **Two-pass**: generate → `pypdf` count → inject total → regenerate |
| Arabic markdown | Python `markdown` lib → HTML |

> ⚠️ **NOT ReportLab** — arabic-pdf skill (ReportLab+NotoNaskhArabic) is different.
> This skill = Chrome pipeline + Thmanyah font.

---

## 3. PARAMETRIC INPUTS (per call)

```python
# Required
md_path        = "/path/to/content.md"          # proposal content in Arabic markdown
out_path       = "/path/to/output.pdf"           # output PDF path
client_name    = "اسم العميل"                     # client name on cover
client_sub     = "وصف العميل"                     # client subtitle
logo_path      = "/path/to/logo.png"             # Ailigent logo (or custom)

# Cover meta cards (3 cards)
price_label    = "رسوم التنفيذ"
price_value    = "249,000 ر.س"
duration_label = "مدة التنفيذ"
duration_value = "45–60 يوم"
year1_label    = "السنة الأولى"
year1_value    = "مجاناً"

# Footer contact (cover page only)
address   = "Baljurshi, Al Olaya, Riyadh 12221, Saudi Arabia"
email     = "info@example.com"
phone     = "+966 5X XXX XXXX"
vat_id    = "الرقم الوطني الموحد: 7053888058"
```

---

## 4. LAYOUT STRUCTURE

```
PAGE 1 — Cover (letterhead style)
┌─────────────────────────────────────┐
│ [logo]  للذكاء الاصطناعي | تقنية   │ ← top-right (RTL)
│ [teal corner clip — top-right]      │
│                                     │
│         [watermark logo — faded]    │
│    عرض خدمي متكامل — التحول الرقمي │ ← H1 centered
│         ────────────────            │
│           مقدَّم خصيصاً لـ          │
│      شركة عبدالله عبدالرحمن السعيد │
│       [3 meta cards: price/dur/yr1] │
│      مقدَّم من Ailigent · التاريخ   │
│                                     │
│ [teal corner — bottom-left]         │
│ address | email | phone | vatid     │ ← address bar
└─────────────────────────────────────┘

PAGES 2–N — Body pages
┌─────────────────────────────────────┐
│ العرض الخدمي | شركة السعيد  AILIGENT│ ← running header (table thead)
│─────────────────────────────────────│
│                                     │
│  [Arabic body content — RTL]        │
│  H1 / H2 gradient boxes / H3       │
│  tables / callout boxes / lists     │
│                                     │
│─────────────────────────────────────│
│  [logo]   12 يونيو 2026 · ailigent  │ ← running footer (table tfoot)
└─────────────────────────────────────┘
  صفحة 2 من 9                          ← @page @bottom-left (outside table)

PAGE N+1 — Back cover
┌─────────────────────────────────────┐
│              [logo]                 │
│           Ailigent AI               │
│  Building Intelligent Solutions     │
│      ────────────────               │
│    عرض شركة X · التاريخ            │
│  © Ailigent AI — جميع الحقوق       │
└─────────────────────────────────────┘
```

---

## 5. KEY CSS RULES

```css
/* Named pages — cover gets margin:0, no @page counter */
@page { size:A4; margin: 0 0 8mm 0; }
@page { @bottom-left {
  content: "صفحة " counter(page) " من TOTAL_PAGES";
  font-family: 'Thmanyah'; font-size:7pt; color:#5B6472; direction:rtl;
}}
@page cover-pg { size:A4; margin:0; }   /* cover — no page counter */
.cover     { page: cover-pg; }
.back-cover{ page: cover-pg; }

/* Running header/footer — table trick */
table.main { width:100%; border-collapse:collapse; }
table.main > thead > tr > th { height:18mm; border-bottom:2.5px solid #0ABFBC; }
table.main > tfoot > tr > td { height:14mm; border-top:1px solid #E3E7EE; }
table.main > tbody > tr > td { padding:7mm 14mm 5mm 14mm; vertical-align:top; }

/* RTL base */
html, body { direction:rtl; text-align:right; font-family:'Thmanyah'; }
```

---

## 6. COLOR PALETTE

```python
NAVY    = "#0D1B2A"   # primary dark (text, headings)
TEAL    = "#0ABFBC"   # primary accent (borders, badges)
TEAL2   = "#00B4D8"   # secondary teal
BLUE    = "#1565C0"   # H3 color
SOFT    = "#5B6472"   # muted text
BTEAL   = "#E8F8F8"   # light teal bg (callouts, h2 gradient)
BALT    = "#F0F8FF"   # alternate row bg
LINE    = "#E3E7EE"   # border lines
WHITE   = "#FFFFFF"
```

---

## 7. TWO-PASS PAGE NUMBERING (critical)

`counter(page)` and `counter(pages)` return `0` in Chrome headless for table-based elements.
**Solution**: `@page @bottom-left` works for `counter(page)`, but `counter(pages)` still fails.
**Fix**: two-pass with hardcoded total:

```python
def build(md_path, out_path, **params):
    html = render_html(md_path, **params)  # has "TOTAL_PAGES" placeholder
    html_path = out_path.with_suffix(".html")

    # Pass 1 — get page count
    html_path.write_text(html)
    run_chrome(html_path, out_path)
    total = len(pypdf.PdfReader(str(out_path)).pages)

    # Pass 2 — inject real total
    if total > 0:
        html_path.write_text(html.replace("TOTAL_PAGES", str(total)))
        run_chrome(html_path, out_path)
        html_path.write_text(html)  # restore readable HTML

def run_chrome(html_path, out_path):
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer", "--virtual-time-budget=15000",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={out_path}", html_path.as_uri()
    ], capture_output=True, timeout=180)
```

---

## 8. FONT LOADING

```python
# Thmanyah fonts are on Mac, not on EC2
FONT_DIR = Path.home() / "Library/Fonts"
THMANYAH_REG  = FONT_DIR / "thmanyah-sans-regular.ttf"
THMANYAH_BOLD = FONT_DIR / "thmanyah-sans-bold.ttf"

# Load as base64 → embed in HTML (portable, no server dependency)
import base64
def font_face(name, weight, path):
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"@font-face{{font-family:'{name}';font-weight:{weight};src:url('data:font/ttf;base64,{b64}') format('truetype');}}"

faces = font_face("Thmanyah", "400", THMANYAH_REG) + font_face("Thmanyah", "700", THMANYAH_BOLD)
```

---

## 9. MARKDOWN BODY PROCESSING

```python
import markdown
from pathlib import Path

body_md = Path(md_path).read_text(encoding="utf-8")
body_html = markdown.markdown(
    body_md,
    extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
)
# body_html goes inside table.main > tbody > tr > td
```

**Markdown conventions for proposals:**
- `#` → H1 (section title with bottom border)
- `##` → H2 (gradient navy/teal box)
- `###` → H3 (right teal border)
- `> text` → callout / highlighted box
- `| col | col |` → styled RTL table (navy header, striped rows)
- `✅ text` → checkbox-style bullet

---

## 10. USAGE EXAMPLE

```
/proposal-pdf
Content: ./content/proposal.md
Client: اسم العميل | وصف العميل
Price: 249,000 ر.س | Duration: 45-60 يوم | Year1: مجاناً
Output: ./output/client_proposal.pdf
```

Or pass just the markdown text in the message if no file.

---

## 11. REFERENCE FILES

- **Script**: `./scripts/build_proposal_pdf.py`
- **Content**: `./content/proposal.md`
- **Output**: `./output/proposal.pdf`
- **Logo**: provide an authorized local brand asset when needed.

---

## 12. COMMON BUGS & FIXES

| Bug | Fix |
|-----|-----|
| `صفحة 0 من 0` in footer | Use `@page @bottom-left` not CSS counter in tfoot |
| `counter(pages)` = 0 | Two-pass: hardcode total after first render |
| Cover gets page counter | Use `page: cover-pg` named page with `margin:0` |
| Table overflow | `table-layout:fixed; word-break:break-word` |
| Arabic font missing | Embed font as base64 in `<style>` |
| Logo on wrong side | `flex-direction:row-reverse` + first child = right content |

---

## 13. CHECKLIST

- [ ] Thmanyah fonts exist in `~/Library/Fonts/`
- [ ] Logo PNG path valid
- [ ] Content `.md` is UTF-8 Arabic
- [ ] Chrome at `/Applications/Google Chrome.app/...`
- [ ] `pypdf` installed (`pip install pypdf`)
- [ ] `markdown` installed (`pip install markdown`)
- [ ] Two-pass ran (page numbers show "صفحة X من Y", not "0 من 0")
- [ ] Visual review: cover, body page 2, last body page, back cover
- [ ] Send via Telegram bot token `~/.openclaw/secrets/tg_token`
