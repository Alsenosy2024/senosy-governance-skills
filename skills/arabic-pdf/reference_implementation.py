#!/usr/bin/env python3
"""
AI & Project Management Article PDF
Dr. Ahmed Al-Senosy - Professional Engineers
RTL Arabic with ReportLab + arabic_reshaper + python-bidi
"""

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import textwrap
import io

# ── Fonts ────────────────────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont('AR', '/home/claude/NotoNaskhArabic-Regular.ttf'))
pdfmetrics.registerFont(TTFont('ARB', '/home/claude/NotoNaskhArabic-Bold.ttf'))

# ── Color Palette ─────────────────────────────────────────────────────────────
NAVY     = colors.HexColor('#0a1f44')
CYAN     = colors.HexColor('#0e7490')
CYAN_LT  = colors.HexColor('#e0f2fe')
CYAN_BRD = colors.HexColor('#38bdf8')
ORANGE   = colors.HexColor('#f97316')
ORANGE_LT= colors.HexColor('#fff7ed')
GOLD     = colors.HexColor('#f59e0b')
WHITE    = colors.white
GRAY     = colors.HexColor('#64748b')
DARK     = colors.HexColor('#1e293b')
LIGHT_BG = colors.HexColor('#f8fafc')

W, H = A4   # 595.27 x 841.89

# ── Arabic helpers ────────────────────────────────────────────────────────────
def ar(text):
    """Reshape + bidi for correct Arabic rendering."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def measure(c, text, font, size):
    c.setFont(font, size)
    return c.stringWidth(text, font, size)

def wrap_arabic(c, text, font, size, max_width):
    """Word-wrap Arabic text into lines that fit max_width."""
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = ' '.join(current + [word])
        w = measure(c, ar(test), font, size)
        if w <= max_width or not current:
            current.append(word)
        else:
            lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines

def draw_ar_lines(c, lines, font, size, x_right, y_start, line_h, color=DARK):
    """Draw right-aligned Arabic lines, returns final y."""
    c.setFont(font, size)
    c.setFillColor(color)
    y = y_start
    for line in lines:
        rendered = ar(line)
        c.drawRightString(x_right, y, rendered)
        y -= line_h
    return y

# ── Decorative elements ───────────────────────────────────────────────────────
def draw_gradient_header(c):
    """Draw layered header background."""
    # Main navy block
    c.setFillColor(NAVY)
    c.rect(0, H - 200, W, 200, fill=1, stroke=0)
    # Cyan accent bar at bottom of header
    c.setFillColor(CYAN)
    c.rect(0, H - 205, W, 8, fill=1, stroke=0)
    # Decorative circle (top-left background)
    c.setFillColor(colors.HexColor('#112244'))
    c.circle(60, H - 30, 120, fill=1, stroke=0)
    # Small gold accent line
    c.setFillColor(GOLD)
    c.rect(40, H - 190, 80, 4, fill=1, stroke=0)

def draw_footer(c, page_num):
    """Footer bar with page number."""
    c.setFillColor(NAVY)
    c.rect(0, 0, W, 50, fill=1, stroke=0)
    c.setFillColor(CYAN_BRD)
    c.rect(0, 48, W, 3, fill=1, stroke=0)
    # Left: website
    c.setFont('AR', 9)
    c.setFillColor(WHITE)
    c.drawString(40, 18, 'PMPmaster.com | ProfessionalEngineers.us')
    # Right: page number
    c.setFillColor(GOLD)
    c.drawRightString(W - 40, 18, f'{page_num}')

def draw_stat_box(c, x, y, w, h, value, label, bg=CYAN_LT, border=CYAN):
    """Draw a stat card."""
    # Shadow
    c.setFillColor(colors.HexColor('#00000015'))
    c.roundRect(x + 3, y - 3, w, h, 8, fill=1, stroke=0)
    # Box
    c.setFillColor(bg)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
    # Border top
    c.setFillColor(border)
    c.roundRect(x, y + h - 6, w, 6, 4, fill=1, stroke=0)
    # Value
    c.setFont('ARB', 16)
    c.setFillColor(NAVY)
    c.drawCentredString(x + w/2, y + h/2 + 4, ar(value))
    # Label
    c.setFont('AR', 10)
    c.setFillColor(GRAY)
    c.drawCentredString(x + w/2, y + h/2 - 16, ar(label))

def draw_section_header(c, text, y, bg=NAVY, text_color=WHITE):
    """Section header bar."""
    c.setFillColor(bg)
    c.roundRect(35, y, W - 70, 34, 6, fill=1, stroke=0)
    c.setFont('ARB', 13)
    c.setFillColor(text_color)
    c.drawCentredString(W/2, y + 10, ar(text))
    return y - 20

def draw_info_box(c, lines_ar, x, y, w, bg=CYAN_LT, border_color=CYAN, border_side='right'):
    """Draw a rounded info box, returns height used."""
    padding = 14
    line_h = 20
    total_h = padding * 2 + len(lines_ar) * line_h + 4

    # Shadow
    c.setFillColor(colors.HexColor('#00000010'))
    c.roundRect(x + 3, y - total_h - 3, w, total_h, 8, fill=1, stroke=0)
    # Box bg
    c.setFillColor(bg)
    c.roundRect(x, y - total_h, w, total_h, 8, fill=1, stroke=0)
    # Border strip
    c.setFillColor(border_color)
    c.roundRect(x + w - 6, y - total_h, 6, total_h, 4, fill=1, stroke=0)

    # Text
    ty = y - padding - 16
    for line in lines_ar:
        c.setFont('AR', 11)
        c.setFillColor(DARK)
        rendered = ar(line)
        c.drawRightString(x + w - 14, ty, rendered)
        ty -= line_h

    return total_h + 12

def draw_quote_box(c, lines_ar, attribution, y):
    """Full-width dark quote block."""
    padding = 18
    line_h = 24
    total_h = padding * 2 + len(lines_ar) * line_h + 28
    x = 35
    w = W - 70

    c.setFillColor(NAVY)
    c.roundRect(x, y - total_h, w, total_h, 8, fill=1, stroke=0)
    # Cyan line left
    c.setFillColor(CYAN_BRD)
    c.rect(x + w - 5, y - total_h, 5, total_h, fill=1, stroke=0)

    # Quote marks decorative
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
    c.drawCentredString(W/2, ty - 4, ar(attribution))

    return total_h + 16

# ── PAGE 1 ────────────────────────────────────────────────────────────────────
def page1(c):
    draw_gradient_header(c)

    # Logo / Brand name in header
    c.setFont('ARB', 11)
    c.setFillColor(CYAN_BRD)
    c.drawCentredString(W/2, H - 30, 'Professional Engineers | Ailigent.ai')

    # Main Title
    c.setFont('ARB', 22)
    c.setFillColor(WHITE)
    c.drawCentredString(W/2, H - 80, ar('الذكاء الاصطناعي وإدارة المشاريع'))

    # Subtitle
    c.setFont('AR', 14)
    c.setFillColor(GOLD)
    c.drawCentredString(W/2, H - 110, ar('هل أنت مستعد؟'))

    # Underline accent
    c.setFillColor(CYAN_BRD)
    c.rect(W/2 - 40, H - 122, 80, 3, fill=1, stroke=0)

    # Author line
    c.setFont('AR', 11)
    c.setFillColor(colors.HexColor('#93c5fd'))
    c.drawCentredString(W/2, H - 148, ar('د. أحمد السنوسي | المدير التنفيذي - Professional Engineers'))

    # Date line
    c.setFont('AR', 10)
    c.setFillColor(colors.HexColor('#7dd3fc'))
    c.drawCentredString(W/2, H - 168, ar('أبريل 2026'))

    # ── Intro paragraph ───────────────────────────────────────────────────────
    y = H - 230
    c.setFillColor(LIGHT_BG)
    c.roundRect(35, y - 65, W - 70, 72, 8, fill=1, stroke=0)

    intro = 'مهنة إدارة المشاريع تمر بتحول جذري، والذكاء الاصطناعي يعيد تعريف المنهجيات الأساسية وعمليات اتخاذ القرار من جذورها. مش بكرة — ده بيحصل دلوقتي.'
    lines = wrap_arabic(c, intro, 'AR', 12, W - 100)
    draw_ar_lines(c, lines, 'AR', 12, W - 50, y - 18, 20, DARK)

    # ── Stats section header ──────────────────────────────────────────────────
    y -= 90
    draw_section_header(c, 'أرقام تتحدث عن نفسها', y)

    # ── 3 stat boxes ─────────────────────────────────────────────────────────
    y -= 30
    bw = (W - 90) / 3
    gap = 10
    draw_stat_box(c, 35, y - 80, bw, 80, '3.03 مليار دولار', 'حجم السوق 2024', CYAN_LT, CYAN)
    draw_stat_box(c, 35 + bw + gap, y - 80, bw, 80, '14.45 مليار دولار', 'المتوقع 2034', ORANGE_LT, ORANGE)
    draw_stat_box(c, 35 + (bw + gap)*2, y - 80, bw, 80, '16.91%', 'معدل النمو السنوي', colors.HexColor('#fef9c3'), GOLD)

    # ── Impact stats row ──────────────────────────────────────────────────────
    y -= 110
    draw_stat_box(c, 35, y - 70, bw, 70, '68%', 'توقعون تأثيراً كبيراً', CYAN_LT, CYAN)
    draw_stat_box(c, 35 + bw + gap, y - 70, bw, 70, '95%', 'يتوقعون تعزيز الربحية', CYAN_LT, CYAN)
    draw_stat_box(c, 35 + (bw+gap)*2, y - 70, bw, 70, '58%', 'أكدوا تحسن جودة المشروع', CYAN_LT, CYAN)

    # ── Challenge box ─────────────────────────────────────────────────────────
    y -= 100
    draw_section_header(c, 'التحديات — موجودة وما نتجاهلهاش ⚠️', y, bg=colors.HexColor('#7c2d12'), text_color=WHITE)
    y -= 30

    challenges = [
        '56.5% من المنظمات بدأت تبني الذكاء الاصطناعي',
        '21.7% فقط نجحوا في التكامل الفعلي حتى الآن',
        'فجوة المهارات: 56.5% | مقاومة التغيير: 47.8%',
        'عدم اليقين من العائد على الاستثمار: 43.5%',
    ]
    for ch in challenges:
        c.setFont('AR', 11)
        c.setFillColor(DARK)
        rendered = ar('◆  ' + ch)
        c.drawRightString(W - 50, y, rendered)
        y -= 22

    # ── Key insight ───────────────────────────────────────────────────────────
    y -= 16
    insight_lines = [
        'الذكاء الاصطناعي التوليدي يمكّن المديرين من تكريس 28% وقت أكثر',
        'للتفكير النقدي وحل المشكلات عوضاً عن المهام الروتينية.',
        '80% من مهام إدارة المشاريع ستتأتمت أو تتغير جذرياً بحلول 2030.',
    ]
    total_h = 14*2 + len(insight_lines)*20 + 8
    c.setFillColor(CYAN_LT)
    c.roundRect(35, y - total_h, W - 70, total_h, 8, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.roundRect(35 + W - 70 - 6, y - total_h, 6, total_h, 4, fill=1, stroke=0)
    ty = y - 20
    for line in insight_lines:
        c.setFont('AR', 11)
        c.setFillColor(NAVY)
        c.drawRightString(W - 50, ty, ar(line))
        ty -= 20

    draw_footer(c, 1)

# ── PAGE 2 ────────────────────────────────────────────────────────────────────
def page2(c):
    # Mini header stripe
    c.setFillColor(NAVY)
    c.rect(0, H - 55, W, 55, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.rect(0, H - 58, W, 4, fill=1, stroke=0)
    c.setFont('ARB', 13)
    c.setFillColor(WHITE)
    c.drawCentredString(W/2, H - 36, ar('الذكاء الاصطناعي وإدارة المشاريع — الرؤية الاستراتيجية'))

    # ── Quote block ───────────────────────────────────────────────────────────
    y = H - 80
    quote_lines = [
        'مش الذكاء الاصطناعي هيحل محل مدير المشروع.',
        'لكن مدير المشروع اللي بيستخدم الذكاء الاصطناعي',
        'هيحل محل اللي مش بيستخدمه.',
    ]
    qh = draw_quote_box(c, quote_lines, 'د. أحمد السنوسي — CEO, Professional Engineers', y)
    y -= qh

    # ── Strategic perspective section ─────────────────────────────────────────
    y -= 10
    draw_section_header(c, 'المنظور الاستراتيجي', y)
    y -= 38

    para1 = 'المعادلة واضحة: الإبداع والحكم الأخلاقي والذكاء العاطفي هتظل جوهر دور الإنسان في إدارة المشاريع. الذكاء الاصطناعي أداة تضخيم، مش أداة إحلال.'
    lines1 = wrap_arabic(c, para1, 'AR', 12, W - 90)
    draw_ar_lines(c, lines1, 'AR', 12, W - 50, y, 22, DARK)
    y -= len(lines1) * 22 + 14

    para2 = 'في Professional Engineers، بنؤمن إن التطوير المهني مش رفاهية، ده ضرورة استراتيجية. لو عايز تفهم كيف تدمج الذكاء الاصطناعي في بيئة عملك وتتخذ قرارات أذكى في مشاريعك، تواصل معانا.'
    lines2 = wrap_arabic(c, para2, 'AR', 12, W - 90)
    draw_ar_lines(c, lines2, 'AR', 12, W - 50, y, 22, DARK)
    y -= len(lines2) * 22 + 20

    # ── 5 year countdown visual ───────────────────────────────────────────────
    draw_section_header(c, '5 سنين... تتأهل أو تتأخر', y, bg=CYAN, text_color=WHITE)
    y -= 40

    years = ['2026', '2027', '2028', '2029', '2030']
    labels = ['الاستعداد', 'التكامل', 'التوسع', 'التحول', 'المستقبل']
    bw2 = (W - 80) / 5
    for i, (yr, lb) in enumerate(zip(years, labels)):
        bx = 40 + i * bw2
        # Progress shading
        alpha = 0.3 + i * 0.14
        shade = colors.HexColor(f'#0e7490')
        c.setFillColor(shade)
        c.setFillAlpha(alpha)
        c.roundRect(bx, y - 55, bw2 - 8, 50, 6, fill=1, stroke=0)
        c.setFillAlpha(1)

        c.setFont('ARB', 14)
        c.setFillColor(NAVY)
        c.drawCentredString(bx + (bw2-8)/2, y - 28, yr)
        c.setFont('AR', 9)
        c.setFillColor(GRAY)
        c.drawCentredString(bx + (bw2-8)/2, y - 46, ar(lb))

    y -= 80

    # ── Sources ───────────────────────────────────────────────────────────────
    draw_section_header(c, 'المصادر والمراجع', y, bg=GRAY, text_color=WHITE)
    y -= 30

    sources = [
        'Project.co — AI in Project Management Statistics, 2024',
        'Precedence Research — AI in Project Management Market, 2025–2034',
        'ScienceDirect — Impact of AI on Project Management: PM2030 Study',
        'Scientific Research Publishing — AI in PM: Challenges & Solutions, 2025',
        'MosaicApp — Project Management Software Statistics & Trends, 2025',
    ]
    for i, src in enumerate(sources, 1):
        c.setFont('AR', 10)
        c.setFillColor(GRAY)
        c.drawRightString(W - 50, y, ar(f'{i}. {src}'))
        y -= 18

    # ── CTA box ───────────────────────────────────────────────────────────────
    y -= 16
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

    draw_footer(c, 2)

# ── MAIN ──────────────────────────────────────────────────────────────────────
output_path = '/home/claude/ai_project_management_article.pdf'
c = canvas.Canvas(output_path, pagesize=A4)
c.setTitle('الذكاء الاصطناعي وإدارة المشاريع')
c.setAuthor('Dr. Ahmed Al-Senosy - Professional Engineers')
c.setSubject('AI Impact on Project Management')

page1(c)
c.showPage()
page2(c)
c.save()
print(f'PDF saved: {output_path}')
