# -*- coding: utf-8 -*-
"""محرّك v3 — ثيمات لكل فصل، أيقونات خطية، أنماط عرض متنوّعة، خط أكبر"""
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re, math, os

# يبحث عن الفونتات في مجلد assets/fonts المجاور، أو في مسار يحدده المستخدم عبر ALTANWEEN_FONTS
_HERE = os.path.dirname(os.path.abspath(__file__))
_FONT_DIR = os.environ.get('ALTANWEEN_FONTS') or os.path.join(_HERE, '..', 'assets', 'fonts')
def _f(name): return os.path.join(_FONT_DIR, name)

pdfmetrics.registerFont(TTFont('THL',  _f('Thmanyah-Light.ttf')))
pdfmetrics.registerFont(TTFont('THR',  _f('Thmanyah-Regular.ttf')))
pdfmetrics.registerFont(TTFont('THM',  _f('Thmanyah-Medium.ttf')))
pdfmetrics.registerFont(TTFont('THB',  _f('Thmanyah-Bold.ttf')))
pdfmetrics.registerFont(TTFont('THXB', _f('Thmanyah-Medium.ttf')))  # عناوين بـ Medium (نقاط الفاء واضحة)
pdfmetrics.registerFont(TTFont('THNUM',_f('Thmanyah-Black.ttf')))   # أرقام عملاقة فقط

INK   = colors.HexColor('#1d1d1f')
SUBTLE= colors.HexColor('#6e6e73')
HAIR  = colors.HexColor('#d2d2d7')
CARD  = colors.HexColor('#f5f5f7')
CARD2 = colors.HexColor('#fafafa')
WHITE = colors.white
NAVY  = colors.HexColor('#1A3557')
GOLD  = colors.HexColor('#C8912A')
CYAN  = colors.HexColor('#0E9EBB')
GREEN = colors.HexColor('#2e7d52')
ORANGE= colors.HexColor('#c5710a')
RED   = colors.HexColor('#c5303a')
NAVY_BG=colors.HexColor('#e9eef4')
GOLD_BG=colors.HexColor('#f9f1e0')
CYAN_BG=colors.HexColor('#e3f4f8')
ORANGE_BG=colors.HexColor('#fdf0e3')

def tint(col, alpha):
    return colors.Color(col.red, col.green, col.blue, alpha=alpha)
def darken(col, f=0.7):
    return colors.Color(col.red*f, col.green*f, col.blue*f)

W, H = A4
ML, MR = 56, 56
XR = W - MR
CW = W - ML - MR

# ثيمات الفصول: لون رئيسي، خلفية فاتحة، لون غامق للنص الملوّن، اسم النمط
THEMES = {
    1: {'main': NAVY, 'bg': NAVY_BG, 'dark': darken(NAVY,0.8), 'accent': GOLD},
    2: {'main': CYAN, 'bg': CYAN_BG, 'dark': colors.HexColor('#0a6d82'), 'accent': NAVY},
    3: {'main': GOLD, 'bg': GOLD_BG, 'dark': colors.HexColor('#7a5a14'), 'accent': NAVY},
    4: {'main': NAVY, 'bg': NAVY_BG, 'dark': darken(NAVY,0.8), 'accent': CYAN},
    5: {'main': CYAN, 'bg': CYAN_BG, 'dark': colors.HexColor('#0a6d82'), 'accent': GOLD},
    6: {'main': GOLD, 'bg': GOLD_BG, 'dark': colors.HexColor('#7a5a14'), 'accent': NAVY},
    7: {'main': NAVY, 'bg': NAVY_BG, 'dark': darken(NAVY,0.8), 'accent': GOLD},
    8: {'main': GOLD, 'bg': GOLD_BG, 'dark': colors.HexColor('#7a5a14'), 'accent': CYAN},
    0: {'main': NAVY, 'bg': NAVY_BG, 'dark': darken(NAVY,0.8), 'accent': GOLD},
}

# ══ TEXT ENGINE ══
AR_PAT = re.compile(r'[\u0600-\u06FF\u0610-\u061A\u064B-\u065F\u0670\uFB50-\uFDFF\uFE70-\uFEFF]')
_resh = arabic_reshaper.ArabicReshaper(configuration={'delete_harakat': False, 'support_ligatures': False})
def bidi(t): return get_display(_resh.reshape(str(t)))
def has_ar(t): return bool(AR_PAT.search(str(t)))
def ar(t): return bidi(t)
def lw(c,t,f,s):
    t=str(t); return c.stringWidth(bidi(t) if has_ar(t) else t,f,s)
def line(c,t,f,s,xr,y,col=INK):
    c.setFillColor(col); c.setFont(f,s); t=str(t)
    c.drawRightString(xr,y,bidi(t) if has_ar(t) else t)
def line_l(c,t,f,s,xl,y,col=INK):
    c.setFillColor(col); c.setFont(f,s); t=str(t)
    c.drawString(xl,y,bidi(t) if has_ar(t) else t)
def wrap(c,t,f,s,mw):
    words=str(t).split(' '); lines=[];cur=[]
    for w in words:
        if not w: continue
        if lw(c,' '.join(cur+[w]),f,s)<=mw or not cur: cur.append(w)
        else: lines.append(' '.join(cur)); cur=[w]
    if cur: lines.append(' '.join(cur))
    return lines or ['']
def para(c,t,f,s,xr,y,lh,mw,col=INK):
    for ln in wrap(c,t,f,s,mw): line(c,ln,f,s,xr,y,col); y-=lh
    return y
def para_h(c,t,f,s,mw,lh): return len(wrap(c,t,f,s,mw))*lh

# ══════════ LINE ICONS (vector, brand colors) ══════════
def ic_setup(c,col,lw_=1.6):
    c.setStrokeColor(col); c.setLineWidth(lw_); c.setLineCap(1); c.setLineJoin(1); c.setFillColor(WHITE)

def icon(c, name, cx, cy, r, col):
    """أيقونة خطية مركزها (cx,cy) نصف قطرها r"""
    ic_setup(c, col, max(1.3, r*0.13))
    if name=='target':
        c.circle(cx,cy,r,stroke=1,fill=0); c.circle(cx,cy,r*0.55,stroke=1,fill=0)
        c.setFillColor(col); c.circle(cx,cy,r*0.16,stroke=0,fill=1)
    elif name=='compass':
        c.circle(cx,cy,r,stroke=1,fill=0)
        p=c.beginPath(); p.moveTo(cx,cy+r*0.55); p.lineTo(cx+r*0.3,cy-r*0.1); p.lineTo(cx,cy-r*0.5); p.lineTo(cx-r*0.3,cy-r*0.1); p.close()
        c.setFillColor(col); c.drawPath(p,fill=1,stroke=0)
    elif name=='layers':
        for i,dy in enumerate([r*0.5,0,-r*0.5]):
            p=c.beginPath(); p.moveTo(cx,cy+dy+r*0.32); p.lineTo(cx+r*0.8,cy+dy); p.lineTo(cx,cy+dy-r*0.32); p.lineTo(cx-r*0.8,cy+dy); p.close()
            c.drawPath(p,fill=0,stroke=1)
    elif name=='bulb':
        c.circle(cx,cy+r*0.2,r*0.62,stroke=1,fill=0)
        c.setStrokeColor(col); c.line(cx-r*0.3,cy-r*0.55,cx+r*0.3,cy-r*0.55); c.line(cx-r*0.22,cy-r*0.8,cx+r*0.22,cy-r*0.8)
    elif name=='gear':
        c.circle(cx,cy,r*0.5,stroke=1,fill=0)
        for a in range(0,360,45):
            ra=math.radians(a); c.line(cx+r*0.5*math.cos(ra),cy+r*0.5*math.sin(ra),cx+r*0.92*math.cos(ra),cy+r*0.92*math.sin(ra))
    elif name=='shield':
        p=c.beginPath(); p.moveTo(cx,cy+r*0.9); p.lineTo(cx+r*0.7,cy+r*0.45); p.lineTo(cx+r*0.7,cy-r*0.3)
        p.curveTo(cx+r*0.7,cy-r*0.7,cx+r*0.4,cy-r*0.9,cx,cy-r); p.curveTo(cx-r*0.4,cy-r*0.9,cx-r*0.7,cy-r*0.7,cx-r*0.7,cy-r*0.3)
        p.lineTo(cx-r*0.7,cy+r*0.45); p.close(); c.drawPath(p,fill=0,stroke=1)
    elif name=='chart':
        c.line(cx-r*0.8,cy-r*0.7,cx-r*0.8,cy+r*0.8); c.line(cx-r*0.8,cy-r*0.7,cx+r*0.85,cy-r*0.7)
        for i,hh in enumerate([0.2,0.55,0.35,0.8]):
            bx=cx-r*0.55+i*r*0.4; c.setFillColor(tint(col,0.25)); c.rect(bx,cy-r*0.7,r*0.22,r*hh,fill=1,stroke=1)
    elif name=='people':
        c.circle(cx-r*0.4,cy+r*0.3,r*0.3,stroke=1,fill=0); c.circle(cx+r*0.4,cy+r*0.3,r*0.3,stroke=1,fill=0)
        p=c.beginPath(); p.moveTo(cx-r*0.85,cy-r*0.7); p.curveTo(cx-r*0.85,cy-r*0.2,cx+r*0.05,cy-r*0.2,cx+r*0.05,cy-r*0.7); c.drawPath(p,fill=0,stroke=1)
        p=c.beginPath(); p.moveTo(cx-r*0.05,cy-r*0.7); p.curveTo(cx-r*0.05,cy-r*0.2,cx+r*0.85,cy-r*0.2,cx+r*0.85,cy-r*0.7); c.drawPath(p,fill=0,stroke=1)
    elif name=='doc':
        c.rect(cx-r*0.55,cy-r*0.8,r*1.1,r*1.6,stroke=1,fill=0)
        for dy in [0.4,0.1,-0.2,-0.5]: c.line(cx-r*0.32,cy+r*dy,cx+r*0.32,cy+r*dy)
    elif name=='bot':
        c.roundRect(cx-r*0.7,cy-r*0.5,r*1.4,r*1.1,r*0.25,stroke=1,fill=0)
        c.setFillColor(col); c.circle(cx-r*0.28,cy+r*0.05,r*0.12,fill=1,stroke=0); c.circle(cx+r*0.28,cy+r*0.05,r*0.12,fill=1,stroke=0)
        c.setStrokeColor(col); c.line(cx,cy+r*0.6,cx,cy+r*0.85); c.circle(cx,cy+r*0.92,r*0.08,fill=1,stroke=0)
    elif name=='brain':
        c.circle(cx,cy,r*0.7,stroke=1,fill=0); c.line(cx,cy-r*0.7,cx,cy+r*0.7)
        c.line(cx-r*0.35,cy-r*0.3,cx-r*0.35,cy+r*0.3); c.line(cx+r*0.35,cy-r*0.3,cx+r*0.35,cy+r*0.3)
    elif name=='link':
        c.line(cx-r*0.1,cy+r*0.5,cx+r*0.5,cy-r*0.1)
        for off in [(-0.4,0.4),(0.4,-0.4)]:
            c.saveState(); c.translate(cx+r*off[0],cy+r*off[1]); c.rotate(45)
            c.roundRect(-r*0.45,-r*0.22,r*0.9,r*0.44,r*0.2,stroke=1,fill=0); c.restoreState()
    elif name=='search':
        c.circle(cx-r*0.15,cy+r*0.15,r*0.55,stroke=1,fill=0); c.line(cx+r*0.28,cy-r*0.28,cx+r*0.75,cy-r*0.75)
    elif name=='flag':
        c.line(cx-r*0.5,cy-r*0.9,cx-r*0.5,cy+r*0.9)
        p=c.beginPath(); p.moveTo(cx-r*0.5,cy+r*0.85); p.lineTo(cx+r*0.7,cy+r*0.55); p.lineTo(cx+r*0.3,cy+r*0.15); p.lineTo(cx+r*0.7,cy-r*0.2); p.lineTo(cx-r*0.5,cy+r*0.1); c.drawPath(p,fill=0,stroke=1)
    elif name=='check':
        c.circle(cx,cy,r*0.85,stroke=1,fill=0); c.line(cx-r*0.4,cy,cx-r*0.1,cy-r*0.35); c.line(cx-r*0.1,cy-r*0.35,cx+r*0.45,cy+r*0.4)
    elif name=='route':
        c.circle(cx-r*0.6,cy+r*0.6,r*0.22,stroke=1,fill=0); c.circle(cx+r*0.6,cy-r*0.6,r*0.22,stroke=1,fill=0)
        p=c.beginPath(); p.moveTo(cx-r*0.4,cy+r*0.6); p.curveTo(cx+r*0.4,cy+r*0.6,cx-r*0.4,cy-r*0.6,cx+r*0.4,cy-r*0.6); c.drawPath(p,fill=0,stroke=1)
    elif name=='scale':
        c.line(cx,cy+r*0.85,cx,cy-r*0.7); c.line(cx-r*0.75,cy+r*0.55,cx+r*0.75,cy+r*0.55); c.line(cx-r*0.5,cy-r*0.7,cx+r*0.5,cy-r*0.7)
        c.circle(cx-r*0.75,cy+r*0.2,r*0.28,stroke=1,fill=0); c.circle(cx+r*0.75,cy+r*0.2,r*0.28,stroke=1,fill=0)
    elif name=='building':
        c.rect(cx-r*0.6,cy-r*0.8,r*1.2,r*1.6,stroke=1,fill=0)
        for ry in [0.4,0.0,-0.4]:
            for rx in [-0.28,0.28]: c.setFillColor(tint(col,0.3)); c.rect(cx+r*rx-r*0.1,cy+r*ry-r*0.08,r*0.2,r*0.16,fill=1,stroke=1)
    elif name=='rocket':
        p=c.beginPath(); p.moveTo(cx,cy+r*0.9); p.curveTo(cx+r*0.5,cy+r*0.3,cx+r*0.4,cy-r*0.5,cx,cy-r*0.6); p.curveTo(cx-r*0.4,cy-r*0.5,cx-r*0.5,cy+r*0.3,cx,cy+r*0.9); c.drawPath(p,fill=0,stroke=1)
        c.circle(cx,cy+r*0.2,r*0.2,stroke=1,fill=0); c.line(cx-r*0.3,cy-r*0.5,cx-r*0.5,cy-r*0.8); c.line(cx+r*0.3,cy-r*0.5,cx+r*0.5,cy-r*0.8)
    elif name=='map':
        p=c.beginPath(); p.moveTo(cx-r*0.8,cy-r*0.6); p.lineTo(cx-r*0.27,cy-r*0.85); p.lineTo(cx+r*0.27,cy-r*0.6); p.lineTo(cx+r*0.8,cy-r*0.85)
        p.lineTo(cx+r*0.8,cy+r*0.7); p.lineTo(cx+r*0.27,cy+r*0.45); p.lineTo(cx-r*0.27,cy+r*0.7); p.lineTo(cx-r*0.8,cy+r*0.45); p.close(); c.drawPath(p,fill=0,stroke=1)
        c.line(cx-r*0.27,cy-r*0.85,cx-r*0.27,cy+r*0.7); c.line(cx+r*0.27,cy-r*0.6,cx+r*0.27,cy+r*0.45)
    elif name=='quote':
        c.setFont('THNUM',int(r*2.2)); c.setFillColor(col); c.drawCentredString(cx,cy-r*0.5,'"')
    elif name=='star':
        pts=[]; 
        for i in range(5):
            a=math.radians(90+i*72); pts.append((cx+r*0.9*math.cos(a),cy+r*0.9*math.sin(a)))
            a2=math.radians(90+i*72+36); pts.append((cx+r*0.38*math.cos(a2),cy+r*0.38*math.sin(a2)))
        p=c.beginPath(); p.moveTo(*pts[0])
        for pt in pts[1:]: p.lineTo(*pt)
        p.close(); c.drawPath(p,fill=0,stroke=1)
    else:
        c.circle(cx,cy,r*0.5,stroke=1,fill=0)

def icon_badge(c, name, cx, cy, r, col, bg=None):
    """أيقونة داخل دائرة خلفية فاتحة"""
    if bg is None: bg = tint(col,0.12)
    c.setFillColor(bg); c.circle(cx,cy,r*1.5,fill=1,stroke=0)
    icon(c,name,cx,cy,r,col)

print("engine_v3 base + icons OK")

# ══════════ CHROME (themed) ══════════
def footer(c, pn, part_label='', theme=0):
    th = THEMES.get(theme, THEMES[0])
    c.setStrokeColor(HAIR); c.setLineWidth(0.5); c.line(ML,42,XR,42)
    c.setFont('THL',7.5); c.setFillColor(SUBTLE); c.drawString(ML,29,'PMPmaster.com')
    if part_label:
        c.setFont('THL',7.5); c.setFillColor(SUBTLE); c.drawCentredString(W/2+30,29,ar(part_label))
    # رقم الصفحة في نقطة ملوّنة بالثيم
    c.setFillColor(th['main']); c.circle(XR-6,31,8.5,fill=1,stroke=0)
    c.setFont('THM',8); c.setFillColor(WHITE); c.drawCentredString(XR-6,28.5,ar(str(pn)))

def header(c, title_ar, sub_en, theme=0, icon_name=None, kicker=None):
    """ترويسة ملوّنة بثيم الفصل + أيقونة + شارة الجزء"""
    th = THEMES.get(theme, THEMES[0])
    # شريط لوني علوي رفيع
    c.setFillColor(th['main']); c.rect(0,H-8,W,8,fill=1,stroke=0)
    yt = H-52
    # كيكر (تسمية الجزء الصغيرة)
    if kicker:
        c.setFillColor(th['main']); c.circle(XR-4,yt+4,3,fill=1,stroke=0)
        c.setFont('THM',8.5); c.setFillColor(th['main']); c.drawRightString(XR-12,yt+1,ar(kicker))
        yt -= 20
    # أيقونة يسار العنوان
    if icon_name:
        icon_badge(c, icon_name, ML+16, yt-6, 13, th['main'])
    c.setFont('THXB',19); c.setFillColor(INK)
    c.drawRightString(XR, yt-6, ar(title_ar))
    if sub_en:
        c.setFont('THL',9); c.setFillColor(SUBTLE); c.drawRightString(XR, yt-22, sub_en)
    c.setStrokeColor(th['main']); c.setLineWidth(2)
    c.line(XR-90, yt-34, XR, yt-34)
    c.setStrokeColor(HAIR); c.setLineWidth(0.5); c.line(ML, yt-34, XR-96, yt-34)
    return yt - 56

def section_head(c, text, y, theme, icon_name=None, sub=None):
    """عنوان قسم مع أيقونة خطية"""
    th=THEMES.get(theme,THEMES[0])
    if icon_name:
        icon_badge(c, icon_name, XR-10, y-2, 9.5, th['main'])
        tx = XR-28
    else:
        c.setFillColor(th['main']); c.circle(XR-5,y+3,4,fill=1,stroke=0); tx=XR-16
    c.setFont('THB',14); c.setFillColor(INK); c.drawRightString(tx,y,ar(text))
    if sub:
        c.setFont('THL',8.5); c.setFillColor(SUBTLE); c.drawRightString(tx,y-13,sub); return y-30
    return y-22

# خط أكبر للمتن: s=11.5, lh=19
def body(c, text, y, theme=0, mw=None, col=INK, f='THR', s=11.5, lh=19):
    if mw is None: mw=CW
    return para(c,text,f,s,XR,y,lh,mw,col)

# ══════════ VARIED DISPLAY COMPONENTS ══════════

def expert_note(c, text, y, theme, style='box'):
    """رأي الخبير بأنماط متنوّعة: box / quote / side"""
    th=THEMES.get(theme,THEMES[0])
    if style=='quote':
        # اقتباس كبير بخط جانبي ملوّن، بدون خلفية صلبة
        pad=18; lh=18
        lines=wrap(c,text,'THM',11.5,CW-70)
        bh=len(lines)*lh+44
        c.setStrokeColor(th['main']); c.setLineWidth(3); c.line(XR-2,y-12,XR-2,y-bh+18)
        icon(c,'quote',XR-26,y-6,11,th['accent'])
        c.setFont('THM',7.5); c.setFillColor(th['main']); c.drawRightString(XR-46,y-8,ar('رؤية الدكتور أحمد السنوسي'))
        yy=y-30
        for ln in lines: line(c,ln,'THM',11.5,XR-16,yy,th['dark']); yy-=lh
        return bh
    else:
        pad=16; lh=17.5
        lines=wrap(c,text,'THR',11,CW-pad*2-14)
        bh=len(lines)*lh+pad*2+18
        c.setFillColor(th['main']); c.roundRect(ML,y-bh,CW,bh,11,fill=1,stroke=0)
        c.setFillColor(th['accent']); c.roundRect(XR-6,y-bh+11,4,bh-22,2,fill=1,stroke=0)
        icon(c,'quote',ML+pad+8,y-pad-4,9,tint(WHITE,0.9))
        c.setFont('THB',8.5); c.setFillColor(th['accent']); c.drawRightString(XR-pad-10,y-pad-3,ar('من واقع الممارسة — د. أحمد السنوسي'))
        yy=y-pad-22
        for ln in lines: line(c,ln,'THR',11,XR-pad-10,yy,WHITE); yy-=lh
        return bh

def gold_note(c, text, y, theme, icon_name='bulb'):
    """ملاحظة ذهبية — تظهر في مكان متغيّر (يمررها المنادي بـ y)"""
    th=THEMES.get(theme,THEMES[0])
    pad=13; lh=15.5
    lines=wrap(c,text,'THM',9.5,CW-pad*2-34)
    bh=len(lines)*lh+pad*2
    c.setFillColor(GOLD_BG); c.roundRect(ML,y-bh,CW,bh,9,fill=1,stroke=0)
    c.setStrokeColor(GOLD); c.setLineWidth(0.8); c.roundRect(ML,y-bh,CW,bh,9,fill=0,stroke=1)
    icon_badge(c,icon_name,XR-pad-6,y-bh/2,8,GOLD)
    yy=y-pad-4
    for ln in lines: line(c,ln,'THM',9.5,XR-pad-26,yy,colors.HexColor('#7a5a14')); yy-=lh
    return bh

def hcards(c, items, y, theme, cols=3, icons=None, h=None):
    """كروت أفقية — items: [(title, desc)]"""
    th=THEMES.get(theme,THEMES[0])
    gap=12; cw=(CW-gap*(cols-1))/cols
    # احسب أقصى ارتفاع
    maxh=0
    for t,d in items[:cols]:
        dl=wrap(c,d,'THR',9,cw-22); maxh=max(maxh,38+len(dl)*12.5+12)
    if h: maxh=h
    cx=XR-cw
    for i,(t,d) in enumerate(items[:cols]):
        c.setFillColor(th['bg']); c.roundRect(cx,y-maxh,cw,maxh,9,fill=1,stroke=0)
        c.setFillColor(th['main']); c.roundRect(cx,y-maxh,cw,3.5,0,fill=1,stroke=0)
        if icons: icon_badge(c,icons[i],cx+cw-16,y-18,8.5,th['main'])
        line(c,t,'THB',10,cx+cw-(30 if icons else 12),y-15,th['dark'])
        yy=y-34
        for ln in wrap(c,d,'THR',9,cw-22): line(c,ln,'THR',9,cx+cw-12,yy,INK); yy-=12.5
        cx-=cw+gap
    return maxh

def timeline(c, items, y, theme, icons=None):
    """خط زمني رأسي RTL — النقاط على اليمين، النص يسارها. items:[(title,desc)]"""
    th=THEMES.get(theme,THEMES[0])
    railx=XR-22
    total=0
    # ارسم الخط الرأسي
    ys=[]
    cy=y
    for i,(t,d) in enumerate(items):
        dl=wrap(c,d,'THR',10,CW-80)
        bh=24+len(dl)*15
        ys.append((cy,bh,t,d,dl)); cy-=bh+10; total+=bh+10
    c.setStrokeColor(tint(th['main'],0.35)); c.setLineWidth(2)
    c.line(railx,y+2,railx,ys[-1][0]-ys[-1][1]+12)
    for i,(cyy,bh,t,d,dl) in enumerate(ys):
        # نقطة مرقّمة
        c.setFillColor(th['main']); c.circle(railx,cyy-6,11,fill=1,stroke=0)
        c.setFont('THB',9.5); c.setFillColor(WHITE); c.drawCentredString(railx,cyy-9.3,ar(str(i+1)))
        line(c,t,'THB',11.5,railx-22,cyy-9,th['dark'])
        yy=cyy-26
        for ln in dl: line(c,ln,'THR',10,railx-22,yy,INK); yy-=15
    return total

def stat_band(c, stats, y, theme):
    """شريط إحصائيات ملوّن. stats:[(value,label)]"""
    th=THEMES.get(theme,THEMES[0])
    n=len(stats); gap=10; bw=(CW-gap*(n-1))/n
    bx=XR-bw
    for v,l in stats:
        c.setFillColor(th['bg']); c.roundRect(bx,y-58,bw,58,10,fill=1,stroke=0)
        c.setFont('THNUM',19); c.setFillColor(th['main']); c.drawCentredString(bx+bw/2,y-28,ar(v))
        for j,ln in enumerate(wrap(c,l,'THL',7.5,bw-12)[:2]):
            c.setFont('THL',7.5); c.setFillColor(SUBTLE); c.drawCentredString(bx+bw/2,y-42-j*9,ar(ln))
        bx-=bw+gap
    return 58

def callout(c, label, text, y, theme, icon_name='check'):
    """صندوق نداء أفقي ملوّن فاتح بأيقونة"""
    th=THEMES.get(theme,THEMES[0])
    pad=13; lh=15.5
    lines=wrap(c,text,'THR',9.8,CW-pad*2-40)
    bh=max(len(lines)*lh+pad*2, 44)
    c.setFillColor(th['bg']); c.roundRect(ML,y-bh,CW,bh,9,fill=1,stroke=0)
    icon_badge(c,icon_name,XR-pad-8,y-bh/2,9,th['main'])
    if label:
        c.setFont('THB',8.5); c.setFillColor(th['dark']); c.drawRightString(XR-pad-28,y-pad-2,ar(label))
        yy=y-pad-18
    else: yy=y-pad-4
    for ln in lines: line(c,ln,'THR',9.8,XR-pad-28,yy,INK); yy-=lh
    return bh

def two_col(c, left_title, left_items, right_title, right_items, y, theme):
    """عمودان متقابلان (مثلاً تحسين مقابل تحوّل)"""
    th=THEMES.get(theme,THEMES[0])
    gap=14; cw=(CW-gap)/2
    rx=XR; lx=ML
    # رؤوس
    c.setFillColor(th['main']); c.roundRect(rx-cw,y-26,cw,26,7,fill=1,stroke=0)
    c.setFillColor(SUBTLE); c.roundRect(lx,y-26,cw,26,7,fill=1,stroke=0)
    c.setFont('THB',10); c.setFillColor(WHITE)
    c.drawCentredString(rx-cw/2,y-17,ar(right_title)); c.drawCentredString(lx+cw/2,y-17,ar(left_title))
    yy=y-26
    maxlen=max(len(right_items),len(left_items))
    for i in range(maxlen):
        rh=40
        for items,xx,al in [(right_items,rx,'r'),(left_items,lx,'l')]:
            if i<len(items):
                c.setFillColor(CARD2 if i%2==0 else WHITE); c.roundRect(xx-cw if al=='r' else xx, yy-rh,cw,rh,0,fill=1,stroke=0)
                tx=xx-10 if al=='r' else xx+cw-10
                yyy=yy-16
                for ln in wrap(c,items[i],'THR',9,cw-20)[:2]:
                    line(c,ln,'THR',9,tx,yyy,INK); yyy-=12
        yy-=rh
    return y-yy

# ══════════ RTL FLOW (themed, bigger) ══════════
def rtl_flow(c, x, y, w, steps, theme, title_ar=None, h=64, icons=None):
    th=THEMES.get(theme,THEMES[0])
    n=len(steps); gap=18; bw=(w-gap*(n-1))/n; bx=x+w-bw; ty=y
    if title_ar:
        c.setFont('THB',11); c.setFillColor(INK); c.drawRightString(x+w,y,ar(title_ar)); ty=y-22
    for i,st in enumerate(steps):
        c.setFillColor(th['bg']); c.roundRect(bx,ty-h,bw,h,9,fill=1,stroke=0)
        c.setStrokeColor(th['main']); c.setLineWidth(0.8); c.roundRect(bx,ty-h,bw,h,9,fill=0,stroke=1)
        c.setFillColor(th['main']); c.circle(bx+bw-12,ty-13,8,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont('THB',8.5); c.drawCentredString(bx+bw-12,ty-15.7,ar(str(i+1)))
        if icons: icon(c,icons[i],bx+14,ty-14,7,th['main'])
        lines=wrap(c,st,'THM',8.6,bw-16); cy=ty-30
        for ln in lines[:3]: line(c,ln,'THM',8.6,bx+bw-9,cy,INK); cy-=11.5
        if i<n-1:
            c.setStrokeColor(th['accent']); c.setLineWidth(2)
            c.line(bx-3,ty-h/2,bx-gap+4,ty-h/2)
            c.setFillColor(th['accent']); p=c.beginPath()
            p.moveTo(bx-gap+4,ty-h/2); p.lineTo(bx-gap+10,ty-h/2+4); p.lineTo(bx-gap+10,ty-h/2-4); p.close(); c.drawPath(p,fill=1,stroke=0)
        bx-=bw+gap
    return (ty-h)

# ══════════ DIVIDER (themed) ══════════
def part_divider(c, num, title_ar, sub_en, items, page_no, theme, icon_name=None):
    th=THEMES.get(theme,THEMES[0])
    main=th['main']
    c.setFillColor(main); c.rect(0,0,W,H,fill=1,stroke=0)
    # طبقات قطرية شفافة
    c.setFillColor(tint(WHITE,0.06))
    p=c.beginPath(); p.moveTo(0,H*0.58); p.lineTo(W,H*0.8); p.lineTo(W,H*0.64); p.lineTo(0,H*0.42); p.close(); c.drawPath(p,fill=1,stroke=0)
    c.setFillColor(tint(th['accent'],0.18))
    p2=c.beginPath(); p2.moveTo(0,H*0.36); p2.lineTo(W,H*0.58); p2.lineTo(W,H*0.53); p2.lineTo(0,H*0.31); p2.close(); c.drawPath(p2,fill=1,stroke=0)
    # أيقونة كبيرة باهتة خلفية
    if icon_name:
        ic_setup(c,tint(WHITE,0.13),3.5); icon(c,icon_name,W*0.28,H*0.42,70,tint(WHITE,0.13))
    # رقم عملاق
    c.setFont('THNUM',120); c.setFillColor(tint(th['accent'],0.9)); c.drawRightString(XR,H-225,ar(num))
    c.setStrokeColor(th['accent']); c.setLineWidth(2.5); c.line(XR-180,H-255,XR,H-255)
    c.setFont('THXB',26); c.setFillColor(WHITE); yy=H-298
    for ln in wrap(c,title_ar,'THXB',26,CW-30): line(c,ln,'THXB',26,XR,yy,WHITE); yy-=36
    c.setFont('THL',11.5); c.setFillColor(tint(WHITE,0.7)); c.drawRightString(XR,yy-4,sub_en)
    iy=yy-58
    for it in items:
        icon(c,'check',XR-7,iy+3,6,th['accent'])
        c.setFont('THR',12); c.setFillColor(tint(WHITE,0.92)); c.drawRightString(XR-22,iy,ar(it)); iy-=26
    c.setFont('THL',7.5); c.setFillColor(tint(WHITE,0.5)); c.drawString(ML,29,'PMPmaster.com')
    c.setFont('THM',8.5); c.setFillColor(th['accent']); c.drawRightString(XR,29,ar(str(page_no)))
    c.showPage()

print("engine_v3 chrome + components OK")
