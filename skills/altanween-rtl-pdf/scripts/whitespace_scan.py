#!/usr/bin/env python3
"""
كاشف الفراغ السفلي — يرصد الصفحات نصف-الفارغة في PDF.
الاستخدام:
    python whitespace_scan.py <pdf_path> [threshold]
يصدّر الصفحات صوراً مؤقتة، ويحسب لكل صفحة نسبة الفراغ بين آخر محتوى وأعلى الفوتر.
يطبع الصفحات التي تتجاوز العتبة (افتراضياً 0.40 أي 40%).
يتطلب: pdftoppm (poppler) و Pillow.
"""
import sys, glob, os, subprocess, tempfile

def scan(pdf, threshold=0.40, dpi=85):
    from PIL import Image
    tmp = tempfile.mkdtemp()
    prefix = os.path.join(tmp, 'pg')
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', pdf, prefix],
                   check=True, capture_output=True)
    pages = sorted(glob.glob(prefix + '*.png'))
    flagged = []
    for p in pages:
        im = Image.open(p).convert('L'); w, h = im.size; px = im.load()
        footer_top = h - 58; last = 0
        for y in range(footer_top, 108, -1):
            row_ink = False
            for x in range(42, w - 42, 6):
                if px[x, y] < 205:
                    row_ink = True; break
            if row_ink:
                last = y; break
        gap_frac = (footer_top - last) / h
        pn = int(os.path.basename(p).split('-')[-1].split('.')[0])
        if gap_frac > threshold:
            flagged.append((pn, round(gap_frac * 100)))
    print(f'{len(pages)} pages scanned; {len(flagged)} pages with >{int(threshold*100)}% bottom whitespace:')
    for pn, g in flagged:
        print(f'  page {pn}: {g}% empty bottom')
    return flagged

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    th = float(sys.argv[2]) if len(sys.argv) > 2 else 0.40
    scan(sys.argv[1], th)
