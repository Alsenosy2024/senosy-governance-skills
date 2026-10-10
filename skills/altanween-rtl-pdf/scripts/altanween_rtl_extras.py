# -*- coding: utf-8 -*-
"""
altanween_rtl_extras — إضافات RTL لمحرّك التنوين (altanween_engine)
=====================================================================
وحدة مكمّلة تُستورد بجانب altanween_engine، تضيف الأنماط اللي بنيناها في
عرض "زينت / أيليجنت":

  1) page_background()  — رسم ورقة رسمية (letterhead) كخلفية كاملة لكل صفحة،
                          مع منطقة محتوى آمنة بين الترويسة والفوتر.
  2) Doc                — غلاف بسيط حول canvas يدير ترقيم الصفحات تلقائياً
                          (خلفية + قطع الصفحات داخل المنطقة الآمنة).
  3) sec/subh/body/bul/quote — مكوّنات تدفق نصي عربية.
  4) rtl_table()        — *** الأهم *** جدول RTL يجعل العمود الأول المُدرَج
                          يظهر على اليمين (المسلسل 1،2،3 ييجي يمين، القيم شمال).
  5) logo_card_grid()   — شريط كروت لوجوهات المنتجات (صورة أو أيقونة + اسم).

الاستخدام:
    import sys; sys.path.insert(0, '<skill>/scripts')
    from altanween_engine import *
    from altanween_rtl_extras import *

ملاحظة الدمج في المهارة: انسخ هذا الملف إلى مجلد scripts الخاص بالمهارة
(بجانب altanween_engine.py)، أو ادمج دالة rtl_table في المحرّك مباشرةً.
"""
import os
from altanween_engine import (
    W, H, ML, MR, XR, CW, NAVY, GOLD, CYAN, WHITE, INK, SUBTLE, HAIR,
    NAVY_BG, GOLD_BG, colors, ar, bidi, has_ar, line, line_l, wrap, para,
    para_h, icon_badge,
)
from reportlab.lib.utils import ImageReader

# منطقة المحتوى الآمنة (عدّلها حسب تصميم الورقة الرسمية)
SAFE_TOP = H - 175    # تحت لوجو الترويسة
SAFE_BOT = 120        # فوق شريط الفوتر


# ── 1) خلفية الصفحة (الورقة الرسمية) ───────────────────────────────
def page_background(c, image_path):
    """يرسم صورة الورقة الرسمية بحجم A4 كامل خلف المحتوى."""
    c.drawImage(ImageReader(image_path), 0, 0, width=W, height=H, mask='auto')


# ── 2) غلاف المستند (خلفية + ترقيم تلقائي) ─────────────────────────
class Doc:
    def __init__(self, path, letterhead, top=SAFE_TOP, bot=SAFE_BOT):
        from reportlab.pdfgen import canvas as _cv
        from reportlab.lib.pagesizes import A4
        self.c = _cv.Canvas(path, pagesize=A4)
        self.letterhead = letterhead
        self.top, self.bot = top, bot
        page_background(self.c, letterhead); self.y = top
    def page(self):
        self.c.showPage(); page_background(self.c, self.letterhead); self.y = self.top
    def ensure(self, h):
        if self.y - h < self.bot: self.page()
    def sp(self, h): self.y -= h
    def save(self): self.c.showPage(); self.c.save()


# ── 3) مكوّنات التدفق ──────────────────────────────────────────────
def sec(d, text):
    d.ensure(48); c=d.c; y=d.y
    c.setFillColor(NAVY); c.roundRect(ML, y-31, CW, 31, 6, fill=1, stroke=0)
    c.setFillColor(GOLD); c.roundRect(XR-6, y-31, 6, 31, 3, fill=1, stroke=0)
    c.setFont('THXB',15); c.setFillColor(WHITE); c.drawRightString(XR-18, y-21, ar(text))
    d.y = y-31-16

def subh(d, text, color=NAVY):
    d.ensure(28); c=d.c; y=d.y
    c.setFillColor(color); c.circle(XR-5, y+1, 3.5, fill=1, stroke=0)
    c.setFont('THB',12.5); c.setFillColor(color); c.drawRightString(XR-14, y-3, ar(text))
    d.y = y-23

def body(d, text, size=11, lh=17.5, col=INK):
    h = para_h(d.c, text, 'THR', size, CW, lh); d.ensure(h+6)
    d.y = para(d.c, text, 'THR', size, XR, d.y, lh, CW, col); d.y -= 7

def bul(d, text, size=10.5, lh=15.8):
    lines = wrap(d.c, text, 'THR', size, CW-24); d.ensure(len(lines)*lh+5)
    c=d.c; y=d.y; c.setFillColor(GOLD); c.circle(XR-6, y-5, 2.7, fill=1, stroke=0)
    yy=y
    for ln in lines: line(c, ln, 'THR', size, XR-17, yy, INK); yy-=lh
    d.y = yy-4


# ── 4) *** جدول RTL — العمود الأول على اليمين *** ─────────────────
def _cell(t, a='r', bold=False, fill=WHITE, col=INK, size=9.3):
    return dict(t=t, a=a, bold=bold, fill=fill, col=col, size=size)

def HDR(t, a='r', size=9.3):  # خلية ترويسة
    return _cell(t, a=a, bold=True, fill=NAVY, col=WHITE, size=size)

def rtl_table(d, widths, header, rows):
    """
    جدول عربي صحيح الاتجاه: أول عمود تكتبه = أقصى اليمين، وآخر عمود = أقصى اليسار.
    السر: نعكس ترتيب الأعمدة داخلياً لأن canvas يرسم من اليسار.
      widths : أوزان الأعمدة (أي وحدة؛ تُطبَّع تلقائياً على عرض المحتوى)
      header : قائمة خلايا الترويسة (استخدم HDR)
      rows   : قائمة صفوف، كل صف قائمة خلايا (استخدم _cell)
    """
    widths = list(reversed(widths))
    header = list(reversed(header))
    rows   = [list(reversed(r)) for r in rows]
    s = CW/float(sum(widths)); widths=[w*s for w in widths]
    pad=6; lh=12.6; vpad=6
    from reportlab.lib import colors as _c
    from reportlab.pdfbase import pdfmetrics  # noqa
    def rh(row):
        m=1
        for i,w in enumerate(widths):
            cell=row[i]; f='THB' if cell.get('bold') else 'THR'
            m=max(m, len(wrap(d.c, str(cell.get('t','')), f, cell.get('size',9.3), w-2*pad)))
        return m*lh+2*vpad
    def draw(row):
        c=d.c; y=d.y; ht=rh(row); xr=XR
        for i,w in enumerate(widths):
            cell=row[i]; xl=xr-w
            c.setFillColor(cell.get('fill',WHITE)); c.rect(xl, y-ht, w, ht, fill=1, stroke=0)
            c.setStrokeColor(HAIR); c.setLineWidth(0.7); c.rect(xl, y-ht, w, ht, fill=0, stroke=1)
            f='THB' if cell.get('bold') else 'THR'; sz=cell.get('size',9.3); col=cell.get('col',INK)
            ty=y-vpad-sz+1; a=cell.get('a','r')
            for ln in wrap(c, str(cell.get('t','')), f, sz, w-2*pad):
                if a=='c':
                    c.setFillColor(col); c.setFont(f,sz)
                    c.drawCentredString(xl+w/2, ty, bidi(ln) if has_ar(ln) else ln)
                elif a=='l': line_l(c, ln, f, sz, xl+pad, ty, col)
                else:        line(c, ln, f, sz, xr-pad, ty, col)
                ty-=lh
            xr=xl
        d.y -= ht
    d.ensure(rh(header)+(rh(rows[0]) if rows else 0)); draw(header)
    for row in rows:
        if d.y - rh(row) < d.bot: d.page(); draw(header)
        draw(row)
    d.y -= 6


# ── 5) شريط كروت لوجوهات المنتجات ─────────────────────────────────
def logo_card_grid(d, items, out_dir, ch=100):
    """
    items: [(image_path_or_None, ar_name, en_name, fallback_icon, logo_bg_hex_or_None), ...]
    out_dir: المجلد الذي تُقرأ منه الصور.
    لو الصورة موجودة تُرسم؛ وإلا تُرسم أيقونة احتياطية. logo_bg لخلفية لوجو فاتح/داكن.
    """
    n=len(items); gap=10; cw=(CW-gap*(n-1))/n
    d.ensure(ch+16); c=d.c; y=d.y; x=XR-cw
    for path,arn,enn,ic,bg in items:
        full = os.path.join(out_dir, path) if path else None
        c.setFillColor(WHITE); c.setStrokeColor(HAIR); c.setLineWidth(1)
        c.roundRect(x, y-ch, cw, ch, 9, fill=1, stroke=1)
        lh=46; lx=x+9; ly=y-12-lh; lw_=cw-18
        if bg:
            c.setFillColor(colors.HexColor('#'+bg)); c.roundRect(lx-2, ly-4, lw_+4, lh+8, 6, fill=1, stroke=0)
        if full and os.path.exists(full):
            try: c.drawImage(full, lx, ly, width=lw_, height=lh, mask='auto', preserveAspectRatio=True, anchor='c')
            except Exception as e: print('logo', path, e)
        else:
            icon_badge(c, ic, x+cw/2, y-34, 14, NAVY)
        c.setFont('THB',11); c.setFillColor(NAVY); c.drawCentredString(x+cw/2, y-ch+24, ar(arn))
        c.setFont('THL',8); c.setFillColor(SUBTLE); c.drawCentredString(x+cw/2, y-ch+11, enn)
        x-=cw+gap
    d.y -= ch+16
