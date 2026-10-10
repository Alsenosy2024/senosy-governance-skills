# Samt visual tokens

## Typography

| Role | Font | Size | Weight | Line height |
|---|---|---:|---:|---:|
| Cover title | Thmanyah Sans | 32-38pt | 900 | 1.25-1.32 |
| Page title | Thmanyah Sans | 23-28pt | 900 | 1.28-1.35 |
| Section title | Thmanyah Sans | 15-17pt | 700-900 | 1.35 |
| Subtitle | Thmanyah Sans | 12.5-15pt | 400-700 | 1.55-1.7 |
| Body | Thmanyah Sans | 10.5-12.5pt | 400 | 1.55-1.7 |
| Table body | Thmanyah Sans | 9.5-10.5pt | 400 | 1.45-1.6 |

## Palette

| Token | Hex | Use |
|---|---|---|
| Navy 900 | `#071D37` | Cover / strong contrast blocks |
| Navy 700 | `#0B3155` | Headers / table headings |
| Blue teal | `#146273` | Secondary emphasis / process nodes |
| Gold | `#D8A94A` | Rules / emphasis / key markers |
| Ink | `#17243A` | Body text |
| Slate | `#506277` | Supporting text |
| Canvas | `#F7FAFC` | Soft cards / background |
| Border | `#DBE4EC` | Fine structure |
| Warning | `#FFF1F0` | Risks / constraints |

## Layout

- A4 report: 17mm side margins, 15-17mm top/bottom margins, page footer at 7-8mm.
- Use a 5-7mm gap between cards; card radius 3mm; interior padding 4-5mm.
- Use a 35-40mm gold rule under major titles; never use a full-width decorative line.
- Keep at least 55% of a report page as whitespace, structured content, or visual hierarchy; avoid dense prose walls.
- Use two columns for paired concepts and three cards only for genuinely comparable alternatives.

## RTL and mixed language

- Set the document or HTML root to `lang="ar" dir="rtl"`.
- Use `unicode-bidi: isolate` or `dir="ltr"` for URLs, English product names, formulas and codes.
- Verify number alignment and parentheses visually. Do not assume Arabic shaping has worked because raw text looks correct.

## Quality gate

Check every rendered page for: Arabic shaping, correct reading order, left/right edge clipping, table cell padding, consistent footer, page number, source link readability, no overflow page, and no nearly empty continuation page.
