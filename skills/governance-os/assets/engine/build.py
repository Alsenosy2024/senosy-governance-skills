# -*- coding: utf-8 -*-
"""يبني مساحة عمل الحوكمة: ملف HTML واحد self-contained، RTL، بحث، تعليقات، فلاتر، طباعة A4.
   الإخراج يتدفّق تلقائياً على الصفحات (لا صناديق A4 ثابتة) لمنع أي overlap أو overflow."""
import html, os

# محرك WeasyPrint لا يشكّل العربية داخل <svg><text>، فنُشكّلها مسبقاً في نسخة PDF فقط.
PDF_MODE = os.environ.get("PDF_MODE") == "1"
PART = os.environ.get("PART", "")
PAGE_OFFSET = int(os.environ.get("PAGE_OFFSET", "0"))
if PDF_MODE:
    import arabic_reshaper
    from bidi.algorithm import get_display
    def shape(t): return get_display(arabic_reshaper.reshape(str(t)))
else:
    def shape(t): return str(t)

from data_core import (META, ENACTMENT, SOURCES, DEPTS, PLATFORMS, ROLES, PRINCIPLES,
                       CHAIN, DOA, DOA_NOTE, DEC, SOD, RACI, MATURITY, MATURITY_TARGET, ROADMAP)
from data_policies import POLICIES, CONDITIONAL
from data_registers import CONTROLS, RISKS, METRICS, SLAS, FORMS, REGISTERS, SYS_PERMS
from data_guides import GUIDES, DISCLAIMER
from data_strategy import (HORIZON, MARKET, ASSUMPTIONS, VISION, MISSION, VALUES, BHAG, BHAG_TEST,
                           CENTRAL_TENSION, PERSPECTIVES, INITIATIVES, STRAT_RISKS, CADENCE, CLOSING)
from data_jobs import NOTE as JOBS_NOTE, BANDS, JOBS, EXTERNAL, GAPS
# استيراد ديناميكي: أي ملف اسمه data_sops_*.py تُجمع منه كل قوائم الإجراءات
import glob, importlib
ALL_SOPS = []
for _f in sorted(glob.glob("data_sops_*.py")):
    _m = importlib.import_module(_f[:-3])
    for _n in dir(_m):
        _v = getattr(_m, _n)
        if isinstance(_v, list) and _v and isinstance(_v[0], dict) and "id" in _v[0] and "steps" in _v[0]:
            ALL_SOPS += _v
CROSS = [s for s in ALL_SOPS if s["dept"] == "CROSS"]
DEPT_NAME = {c: n for c, n, *_ in DEPTS}
DEPT_NAME["CROSS"] = "عمليات تقاطعية"
DEPT_NAME["ALL"] = "عام"
E = lambda s: html.escape(str(s))
ES = lambda s: html.escape(shape(s))

# ------------------------------------------------------------------ عناصر
def sheet(dept, body, sid="", cls=""):
    idattr = f' id="{sid}"' if sid else ""
    return f'<section class="a4-page sheet {cls}" data-dept="{dept}"{idattr}>{body}</section>'


def divider(num, title, subtitle, dept="ALL"):
    return (f'<section class="a4-page sheet divider" data-dept="{dept}" id="PART-{num}">'
            f'<div class="dv"><span class="dv-num">{num}</span>'
            f'<h2 class="dv-title">{E(title)}</h2><p class="dv-sub">{E(subtitle)}</p></div></section>')


def obj(oid, kind, status, dept, title, inner):
    return (f'<article class="object" id="{oid}" data-type="{kind}" data-status="{status}" data-dept="{dept}">'
            f'<header class="object-head"><span class="badge id" dir="ltr">{oid}</span>'
            f'<h3>{E(title)}</h3>'
            f'<span class="badge k">{kind}</span><span class="badge s-{status}">{status}</span>'
            f'<span class="badge d">{DEPT_NAME.get(dept, dept)}</span></header>{inner}</article>')


def table(headers, rows, cls=""):
    h = "".join(f"<th>{E(x)}</th>" for x in headers)
    b = "".join("<tr>" + "".join(
        f"<td>{c if isinstance(c, str) and c.lstrip().startswith('<') else E(c)}</td>" for c in r) + "</tr>"
        for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def ul(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"


def ol(items):
    return "<ol class=\"rules\">" + "".join(f"<li>{E(i)}</li>" for i in items) + "</ol>"


def link(ids):
    return " ".join(f'<a class="ref" href="#{i.split()[0]}" dir="ltr">{E(i.split()[0])}</a>' for i in ids)


# --------------------------------------------------------------- رسم SVG
def wrap(text, per):
    """يلفّ النص بلا أي بتر — الصندوق ينمو بدل أن يفيض."""
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= per or not cur:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


W = 720
LANE_X, LANE_W = 566, 142          # مسار الدور
BOX_X, BOX_W = 96, 462             # صندوق الخطوة
CTL_X, CTL_W = 6, 82               # شريط الضابط
LH = 13                            # ارتفاع السطر


def steps_svg(sop):
    rows, y = [], 34
    for i, (actor, action, system, sla, ctl) in enumerate(sop["steps"], 1):
        tl = wrap(action, 58)
        al = wrap(actor, 17)
        h = max(22 + len(tl) * LH, 20 + len(al) * 12, 42)
        rows.append((y, h, i, al, tl, system, sla, ctl))
        y += h + 30
    H = y + 34
    p = [f'<svg class="flow" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="خريطة تدفق: {ES(sop["title"])}">',
         '<defs><marker id="a1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
         '<path d="M0,0 L9,4.5 L0,9 z" fill="#19395f"/></marker></defs>',
         f'<rect x="{BOX_X}" y="4" width="{BOX_W}" height="22" rx="11" fill="#19395f"/>'
         f'<text x="{BOX_X+BOX_W/2}" y="19" text-anchor="middle" fill="#fff" font-size="10">'
         f'{ES("بداية: " + wrap(sop["trigger"], 70)[0])}</text>']
    cx = BOX_X + BOX_W / 2
    for (y, h, i, al, tl, system, sla, ctl) in rows:
        p.append(f'<line x1="{cx}" y1="{y-26}" x2="{cx}" y2="{y-3}" stroke="#19395f" stroke-width="1.3" marker-end="url(#a1)"/>')
        p.append(f'<rect x="{BOX_X}" y="{y}" width="{BOX_W}" height="{h}" rx="8" fill="#f5f9fb" stroke="#a7bccd"/>')
        p.append(f'<circle cx="{BOX_X+13}" cy="{y+13}" r="8.5" fill="#087f8c"/>'
                 f'<text x="{BOX_X+13}" y="{y+16.5}" text-anchor="middle" fill="#fff" font-size="9">{i}</text>')
        for j, ln in enumerate(tl):
            p.append(f'<text x="{BOX_X+BOX_W-12}" y="{y+17+j*LH}" text-anchor="end" font-size="9.3" fill="#172033">{ES(ln)}</text>')
        p.append(f'<rect x="{LANE_X}" y="{y}" width="{LANE_W}" height="{h}" rx="8" fill="#e9f0f5" stroke="#a7bccd"/>')
        oy = y + (h - len(al) * 12) / 2 + 9
        for j, ln in enumerate(al):
            p.append(f'<text x="{LANE_X+LANE_W/2}" y="{oy+j*12}" text-anchor="middle" font-size="8.4" fill="#19395f">{ES(ln)}</text>')
        meta = " · ".join(x for x in (system, sla) if x and x != "—")
        if meta:
            p.append(f'<text x="{BOX_X+BOX_W-12}" y="{y+h+11}" text-anchor="end" font-size="7.6" fill="#7b8794">{ES(meta)}</text>')
        if ctl:
            p.append(f'<rect x="{CTL_X}" y="{y+2}" width="{CTL_W}" height="15" rx="7.5" fill="#fff3d9" stroke="#c79430"/>'
                     f'<text x="{CTL_X+CTL_W/2}" y="{y+12.5}" text-anchor="middle" font-size="8" fill="#7a5610" dir="ltr">{E(ctl)}</text>')
    p.append(f'<line x1="{cx}" y1="{H-56}" x2="{cx}" y2="{H-31}" stroke="#19395f" stroke-width="1.3" marker-end="url(#a1)"/>')
    p.append(f'<rect x="{BOX_X}" y="{H-28}" width="{BOX_W}" height="22" rx="11" fill="#087f8c"/>'
             f'<text x="{cx}" y="{H-13}" text-anchor="middle" fill="#fff" font-size="10">'
             f'{ES("نهاية: " + wrap(sop["end"], 70)[0])}</text>')
    p.append("</svg>")
    return "".join(p)


def gates_svg(sop):
    if not sop["gates"]:
        return ""
    rows, y = [], 6
    for q, yes, no in sop["gates"]:
        ql, yl, nl = wrap(q, 25), wrap(yes, 33), wrap(no, 62)
        h = max(len(ql) * 11 + 24, len(yl) * 11 + 20, len(nl) * 11 + 20, 62)
        rows.append((y, h, ql, yl, nl)); y += h + 14
    H = y + 4
    p = [f'<svg class="flow" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-label="بوابات القرار ومسارات الرفض">',
         '<defs><marker id="a2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
         '<path d="M0,0 L9,4.5 L0,9 z" fill="#19395f"/></marker></defs>']
    for (y, h, ql, yl, nl) in rows:
        cy = y + h / 2
        p.append(f'<path d="M714,{cy} L610,{y} L506,{cy} L610,{y+h} z" fill="#fff7e6" stroke="#c79430"/>')
        oy = cy - (len(ql) - 1) * 5.5
        for j, ln in enumerate(ql):
            p.append(f'<text x="610" y="{oy+j*11+3}" text-anchor="middle" font-size="8" fill="#7a5610">{ES(ln)}</text>')
        # نعم
        yh = len(yl) * 11 + 12
        yy = y + 2
        p.append(f'<line x1="506" y1="{yy+yh/2}" x2="480" y2="{yy+yh/2}" stroke="#0a6b3d" marker-end="url(#a2)"/>')
        p.append(f'<text x="493" y="{yy+yh/2-4}" text-anchor="middle" font-size="7.5" fill="#0a6b3d">{ES("نعم")}</text>')
        p.append(f'<rect x="286" y="{yy}" width="188" height="{yh}" rx="6" fill="#e7f5ed" stroke="#0a6b3d"/>')
        for j, ln in enumerate(yl):
            p.append(f'<text x="380" y="{yy+15+j*11}" text-anchor="middle" font-size="7.8" fill="#0a4b2b">{ES(ln)}</text>')
        # لا
        nh = len(nl) * 11 + 12
        ny = y + h - nh - 2
        p.append(f'<line x1="506" y1="{ny+nh/2}" x2="480" y2="{ny+nh/2}" stroke="#a83434" marker-end="url(#a2)"/>')
        p.append(f'<text x="493" y="{ny+nh/2-4}" text-anchor="middle" font-size="7.5" fill="#a83434">{ES("لا")}</text>')
        p.append(f'<rect x="6" y="{ny}" width="468" height="{nh}" rx="6" fill="#fdeeee" stroke="#a83434"/>')
        for j, ln in enumerate(nl):
            p.append(f'<text x="462" y="{ny+15+j*11}" text-anchor="end" font-size="7.8" fill="#7a1f1f">{ES(ln)}</text>')
    p.append("</svg>")
    return "".join(p)


def lifecycle_svg():
    stages = [("Pre-project", "ما قبل المشروع", "G0"), ("Initiation", "البدء", "G1"),
              ("Planning", "التخطيط", "G2"), ("Execution", "التنفيذ", "G3"),
              ("Monitoring", "الضبط والمراقبة", "G4"), ("Closing", "الإقفال", "G5"),
              ("Benefits", "تحقّق المنافع", "G6")]
    n = len(stages); bw, gap = 88, 12
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    p = [f'<svg class="flow" viewBox="0 0 {W} 150" xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-label="دورة حياة المشروع العقاري وبواباتها">',
         '<defs><marker id="a3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
         '<path d="M0,0 L9,4.5 L0,9 z" fill="#19395f"/></marker></defs>']
    for i, (en, ar, g) in enumerate(stages):
        x = x0 + (n - 1 - i) * (bw + gap)          # من اليمين لليسار
        col = "#19395f" if i < 5 else "#087f8c"
        p.append(f'<rect x="{x}" y="42" width="{bw}" height="46" rx="8" fill="{col}"/>')
        for j, ln in enumerate(wrap(ar, 12)):
            p.append(f'<text x="{x+bw/2}" y="{62+j*12}" text-anchor="middle" fill="#fff" font-size="8.6">{ES(ln)}</text>')
        p.append(f'<text x="{x+bw/2}" y="{100}" text-anchor="middle" fill="#667085" font-size="7.4" dir="ltr">{E(en)}</text>')
        p.append(f'<rect x="{x+bw/2-14}" y="16" width="28" height="18" rx="9" fill="#fff3d9" stroke="#c79430"/>'
                 f'<text x="{x+bw/2}" y="29" text-anchor="middle" font-size="9" fill="#7a5610" dir="ltr">{E(g)}</text>')
        p.append(f'<line x1="{x+bw/2}" y1="34" x2="{x+bw/2}" y2="40" stroke="#c79430"/>')
        if i < n - 1:
            xn = x0 + (n - 2 - i) * (bw + gap)
            p.append(f'<line x1="{x}" y1="65" x2="{xn+bw+3}" y2="65" stroke="#19395f" stroke-width="1.3" marker-end="url(#a3)"/>')
    p.append(f'<text x="{W/2}" y="128" text-anchor="middle" font-size="8.6" fill="#7a1f1f">'
             f'{ES("لا تبدأ مرحلة قبل إغلاق بوابة سابقتها بقرار موثَّق: مضي · مضي بشروط مكتوبة · إيقاف")}</text>')
    p.append("</svg>")
    return "".join(p)




def strategy_map_svg():
    rows = [("L", "التعلّم والنمو", "#7a5610", ["L-01 قدرة إدارة الأصول", "L-02 مصدر واحد للحقيقة", "L-03 ثقافة الدليل"]),
            ("P", "العمليات الداخلية", "#2c5580", ["P-01 حوكمة نافذة", "P-02 ضغط زمن الدورة", "P-03 كفاءة تشغيل الأصل", "P-04 بوابة رأس المال"]),
            ("C", "العملاء والسوق", "#087f8c", ["C-01 مستأجر مستقر", "C-02 تسعير بالبيانات", "C-03 رأس مال شريك"]),
            ("F", "المالي", "#19395f", ["F-01 دخل متكرر", "F-02 حماية السيولة", "F-03 ضبط الرافعة", "F-04 عائد رأس المال", "F-05 دوران رأس المال", "F-06 ضبط التكلفة"])]
    RH, H = 96, 96 * 4 + 46
    p = [f'<svg class="flow" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="خريطة الاستراتيجية">',
         '<defs><marker id="a4" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
         '<path d="M0,0 L9,4.5 L0,9 z" fill="#8aa0b3"/></marker></defs>',
         f'<text x="{W-6}" y="16" text-anchor="end" font-size="10" fill="#6b7a89">'
         f'{ES("منطق السببية: القدرة ← العملية ← السوق ← المال. لا هدف مالي بلا عملية تسنده.")}</text>']
    for k, (code, name, col, objs) in enumerate(rows):
        y = 30 + k * RH
        p.append(f'<rect x="{W-116}" y="{y}" width="110" height="76" rx="8" fill="{col}"/>')
        for j, ln in enumerate(wrap(name, 13)):
            p.append(f'<text x="{W-61}" y="{y+34+j*13}" text-anchor="middle" fill="#fff" font-size="9.5">{ES(ln)}</text>')
        n = len(objs); bw = (W - 138) / n - 8
        for i, o in enumerate(objs):
            x = 6 + (n - 1 - i) * (bw + 8)
            p.append(f'<rect x="{x}" y="{y+8}" width="{bw}" height="60" rx="7" fill="#f5f9fb" stroke="{col}"/>')
            for j, ln in enumerate(wrap(o, 16)[:4]):
                p.append(f'<text x="{x+bw/2}" y="{y+25+j*12}" text-anchor="middle" font-size="8.2" fill="#16202e">{ES(ln)}</text>')
        if k < 3:
            p.append(f'<line x1="{W/2-60}" y1="{y+76}" x2="{W/2-60}" y2="{y+RH+4}" stroke="#8aa0b3" stroke-width="1.4" marker-end="url(#a4)"/>')
    p.append("</svg>")
    return "".join(p)


def strategy_html():
    per = ""
    for code, name, col, objs in PERSPECTIVES:
        per += f'<h3 id="BSC-{code}">المنظور: {E(name)}</h3>'
        for oid, title, why, owner, kpis in objs:
            per += obj(oid, "هدف استراتيجي", "تصميم", "ALL", title,
                f'<p class="para">{E(why)}</p>'
                + table(["الحقل", "القيمة"], [["المسؤول", owner], ["المنظور", name]])
                + table(["المؤشر (KPI)", "المعادلة", "خط الأساس", "مستهدف 2026", "مستهدف 2027"],
                        [list(k) for k in kpis]))
    return per


def jobs_html():
    out = ""
    for (jid, title, dept, band, reports, subs, purpose, resp, auth, procs, ifaces, kpis, ctrls, quals, status) in JOBS:
        out += obj(jid, "وصف وظيفي", "تصميم" if status.startswith("تصميم") else "معتمد", dept, title,
            f'<div class="two"><div>'
            + table(["الحقل", "القيمة"], [["الإدارة", DEPT_NAME.get(dept, dept)], ["الرتبة", band],
                                          ["يرفع إلى", reports], ["المرؤوسون", subs], ["الحالة", status]])
            + f'</div><div><h4>الغرض</h4><p class="para">{E(purpose)}</p>'
              f'<h4>الصلاحيات (سطور DOA)</h4><p>{" · ".join(E(a) for a in auth)}</p></div></div>'
            f'<h4>المسؤوليات</h4>{ol(resp)}'
            f'<div class="grid3">'
            f'<div class="cell"><b>العمليات المملوكة</b>{ul(procs)}</div>'
            f'<div class="cell"><b>الواجهات</b>{ul(ifaces)}</div>'
            f'<div class="cell"><b>المؤشرات</b>{ul(kpis)}</div></div>'
            f'<div class="callout warn"><b>ضوابط حرجة — لا يجوز خرقها:</b>{ul(ctrls)}</div>'
            f'<div class="callout"><b>المؤهلات والكفاءات:</b> {E(" · ".join(quals))}</div>')
    return out


# --------------------------------------------------------------- بناء الكائنات
def sop_html(s):
    steps = table(["#", "الدور", "الفعل", "النظام", "الزمن", "الضابط"],
                  [[i, a, act, sysm or "—", sla or "—",
                    f'<a class="ref" href="#{c}" dir="ltr">{c}</a>' if c else "—"]
                   for i, (a, act, sysm, sla, c) in enumerate(s["steps"], 1)], "steps")
    gates = table(["بوابة القرار", "نعم", "لا"], [list(g) for g in s["gates"]]) if s["gates"] else ""
    apps = table(["ما يُعتمد", "صاحب الاعتماد", "سطر الصلاحية"],
                 [[w, who, (f'<a class="ref" href="#{d.split("/")[0]}" dir="ltr">{d}</a>'
                            if d.startswith(("DOA", "DEC")) else d)] for w, who, d in s["approvals"]])
    meta = table(["الحقل", "القيمة"], [
        ["المالك", s["owner"]], ["صاحب الاعتماد", s["approver"]],
        ["السياسة الأم", f'<a class="ref" href="#{s["policy"]}" dir="ltr">{s["policy"]}</a>'],
        ["المُشغِّل (Trigger)", s["trigger"]], ["حد البداية", s["start"]], ["حد النهاية", s["end"]],
        ["زمن الخدمة (SLA)", s["sla"]]])
    return obj(s["id"], "إجراء", "تصميم", s["dept"], s["title"],
        f'<div class="two"><div><h4>البيانات الأساسية</h4>{meta}</div>'
        f'<div><h4>المدخلات</h4>{ul(s["inputs"])}<h4>المخرجات</h4>{ul(s["outputs"])}</div></div>'
        f'<h4>الخطوات</h4>{steps}'
        f'<figure class="kt"><figcaption>خريطة التدفق — {E(s["id"])}</figcaption>{steps_svg(s)}</figure>'
        + (f'<h4>بوابات القرار</h4>{gates}'
           f'<figure class="kt"><figcaption>بوابات القرار ومسارات الرفض</figcaption>{gates_svg(s)}</figure>' if gates else "")
        + f'<h4>نقاط الاعتماد</h4>{apps}'
        f'<div class="grid3">'
        f'<div class="cell"><b>الضوابط</b><p>{link(s["controls"])}</p></div>'
        f'<div class="cell"><b>فصل الواجبات</b><p>{E(s["sod"])}</p></div>'
        f'<div class="cell"><b>المؤشرات</b><p>{link(s["kpis"])}</p></div></div>'
        f'<div class="callout"><b>الاستثناء:</b> {E(s["exception"])}</div>'
        f'<div class="callout warn"><b>مسار الرفض:</b> {E(s["reject"])}<br><b>التصعيد:</b> {E(s["escalation"])}</div>'
        f'<div class="grid3">'
        f'<div class="cell"><b>الدليل المحفوظ</b>{ul(s["evidence"])}</div>'
        f'<div class="cell"><b>النماذج</b>{ul(s["forms"])}</div>'
        f'<div class="cell"><b>السجلات</b>{ul(s["registers"])}</div></div>')


def policy_html(p):
    return obj(p["id"], "سياسة", "تصميم", p["dept"], p["title"],
        f'<div class="two"><div>'
        f'{table(["الحقل", "القيمة"], [["المالك", p["owner"]], ["صاحب الاعتماد", p["approver"]], ["العائلة", p["family"]], ["الحالة", p["priority"]], ["المرجع المعياري", p["standard"]], ["دورة المراجعة", p["review"]]])}'
        f'</div><div><h4>الغرض</h4><p>{E(p["purpose"])}</p><h4>النطاق</h4><p>{E(p["scope"])}</p></div></div>'
        f'<h4>التعريفات</h4>{table(["المصطلح", "التعريف"], [list(d) for d in p["definitions"]])}'
        f'<h4>القواعد الإلزامية</h4>{ol([r[r.find(".")+1:].strip() for r in p["rules"]])}'
        f'<div class="grid3">'
        f'<div class="cell"><b>الأدوار</b><p>{E(p["roles"])}</p></div>'
        f'<div class="cell"><b>الضوابط</b><p>{link(p["controls"])}</p></div>'
        f'<div class="cell"><b>الإجراءات المرتبطة</b><p>{link(p["sops"])}</p></div></div>'
        f'<div class="callout"><b>الاستثناءات:</b> {E(p["exceptions"])}</div>'
        f'<div class="callout warn"><b>عواقب المخالفة:</b> {E(p["consequences"])}</div>')


def guide_html(g):
    gid, title, ref, purpose, when, secs = g
    body = (f'<div class="two"><div><h4>الغرض</h4><p>{E(purpose)}</p></div>'
            f'<div><h4>متى تستخدمه</h4><p>{E(when)}</p><h4>المرجع</h4><p class="tiny"><bdi dir="ltr">{E(ref)}</bdi></p></div></div>')
    if gid == "GID-02":
        body += f'<figure class="kt"><figcaption>دورة حياة المشروع العقاري وبواباتها</figcaption>{lifecycle_svg()}</figure>'
    for title2, kind, content in secs:
        body += f"<h4>{E(title2)}</h4>"
        if kind == "table":
            body += table(content[0], content[1])
        elif kind == "steps":
            body += ol(content)
        else:
            body += f'<p class="para">{content if "<b>" in content else E(content)}</p>'
    return obj(gid, "دليل", "إرشادي", "ALL", title, body)


# =============================================================== المحتوى
P = []

# ---------- الغلاف
P.append(sheet("ALL", f'''
<div class="cover">
  <div class="cover-bar"></div>
  <span class="badge s-تصميم">تصميم مستهدف — يتطلب اعتماداً</span>
  <h1>{E(META["title"])}</h1>
  <p class="cover-sub">{E(META["company"])}</p>
  <p class="cover-lead">مساحة عمل تفاعلية للقرارات والصلاحيات والسياسات والإجراءات والأدوار والمخاطر والضوابط والمؤشرات والأدلة الإرشادية.</p>
  <div class="stats">
    <div><b>{len(ALL_SOPS)}</b><span>إجراء</span></div>
    <div><b>{len(POLICIES)}</b><span>سياسة</span></div>
    <div><b>{len(DOA)}</b><span>سطر صلاحية</span></div>
    <div><b>{len(CONTROLS)}</b><span>ضابط</span></div>
    <div><b>{len(METRICS)}</b><span>مؤشر</span></div>
    <div><b>{len(JOBS)}</b><span>وصف وظيفي</span></div>
    <div><b>{len(GUIDES)}</b><span>دليل إرشادي</span></div>
  </div>
  {table(["الحقل", "القيمة"], [["رقم الوثيقة", META["docid"]], ["الإصدار", META["version"]], ["التاريخ", META["date"]],
                              ["التصنيف", META["classification"]], ["سلطة الاعتماد", META["authority"]],
                              ["الحالة", "مصمَّم — غير معتمد وغير مطبَّق بعد"]])}
  <div class="callout warn"><b>حدود هذه الوثيقة:</b> المكتمل الآن هو <b>تصميم</b> الحوكمة ومكتبة الإجراءات والضوابط والأدلة.
  «مصمَّم» ليس «معتمداً»، و«معتمد» ليس «مطبَّقاً»، و«مطبَّق» ليس «فعّالاً» حتى تُختبر الضوابط على معاملات حقيقية.</div>
</div>''', "cover", "cover-sheet"))


# ---------- الجزء صفر: الخطة الاستراتيجية
P.append(divider("٠", "الخطة الاستراتيجية 2026–2027", "بطاقة أداء متوازن (BSC) — مسودة بتركيز على المحور المالي"))

P.append(sheet("ALL", f'''
<h2 id="STR">مسودة الخطة الاستراتيجية — {E(HORIZON)}</h2>
<div class="callout warn"><b>حالة الوثيقة: مسودة.</b> {CLOSING}</div>
<h3 id="STR-MKT">قراءة السوق — ما تقوله الأرقام المنشورة</h3>
{table(["المعرّف", "الملاحظة", "الرقم", "فئة الدليل", "الترجمة الاستراتيجية", "المصدر"],
       [[m[0], m[1], m[2], f'<span class="badge s-معتمد">{m[3]}</span>', m[4], f'<bdi dir="ltr" class="mono">{E(m[5])}</bdi>'] for m in MARKET], "dense")}
<div class="callout warn"><b>الاستنتاج المحوري:</b> الأسعار تتراجع بينما الإيجارات ترتفع، ورسوم الأراضي البيضاء حوّلت الأرض من مخزون قيمة إلى نزيف نقدي.
نموذج «اشترِ أرضاً واحتفظ وبِع» صار الأسوأ عائداً. الرابح حتى 2027: <b>سرعة الدوران + أصول مدرّة للدخل</b>. هذا ما تُبنى عليه كل أهداف المحور المالي أدناه.</div>
''', "strategy"))

P.append(sheet("ALL", f'''
<h2 id="STR-ID">الرؤية والرسالة والقيم</h2>
<h3>الرؤية</h3><p class="para chain" style="text-align:right">{VISION}</p>
<h3>الرسالة</h3><p class="para">{E(MISSION)}</p>
<h3>القيم</h3>
{table(["المعرّف", "القيمة", "ما تعنيه عند التعارض مع الربح"], [list(v) for v in VALUES])}
<h2 id="STR-GOAL">الهدف الجامع (Goal)</h2>
<div class="callout">{BHAG}</div>
<div class="callout warn">{E(BHAG_TEST)}</div>
''', "strategy-id"))

P.append(sheet("ALL", f'''
<h2 id="STR-TENSION">التوتر المركزي في هذه الخطة — والحل</h2>
<p class="para">أي خطة لا تُسمّي التناقض الذي بداخلها هي تمنٍّ. هذا هو التناقض، وهذا هو حلّه.</p>
{table(["البُعد", "التحليل"], [[t[0], t[1]] for t in CENTRAL_TENSION])}
<h2 id="STR-ASM">الافتراضات — ما هو مؤكَّد وما يحتاج تأكيدك</h2>
<p class="para">الأرقام الموسومة «افتراض» هي أرقام عمل لبناء المنطق، وليست التزامات. استبدالها بأرقامك الفعلية هو الشرط الأول لتحويل هذه المسودة إلى خطة.</p>
{table(["المعرّف", "الافتراض", "القيمة", "المصدر", "الحالة"],
       [[a[0], a[1], a[2], a[3], f'<span class="badge s-{"معتمد" if a[4]=="مؤكَّد" else "تصميم"}">{a[4]}</span>'] for a in ASSUMPTIONS])}
''', "strategy-tension"))

P.append(sheet("ALL", f'''
<h2 id="STR-MAP">خريطة الاستراتيجية (Strategy Map)</h2>
<figure class="kt"><figcaption>منطق السببية بين المناظير الأربعة</figcaption>{strategy_map_svg()}</figure>
<p class="para">تُقرأ من أسفل لأعلى: <b>القدرة</b> تُمكّن <b>العملية</b>، والعملية تخلق <b>القيمة للسوق</b>، والسوق يُنتج <b>النتيجة المالية</b>.
أي هدف مالي بلا عملية تسنده هو رقم على ورق. ولهذا يبدأ التنفيذ من الأسفل بينما يبدأ القياس من الأعلى.</p>
''', "strategy-map"))

P.append(sheet("ALL", f'''
<h2 id="STR-BSC">بطاقة الأداء المتوازن — الأهداف والمؤشرات</h2>
<p class="para">لكل هدف: <b>لماذا</b> يوجد · <b>من</b> يملكه بالاسم الوظيفي · <b>مؤشرات</b> بمعادلة ومستهدف لسنتين.
المؤشر بلا معادلة رأي، والمستهدف بلا مالك أمنية.</p>
{strategy_html()}
''', "strategy-bsc"))

P.append(sheet("ALL", f'''
<h2 id="STR-INI">محفظة المبادرات</h2>
<p class="para">المبادرة ليست هدفاً بل <b>آلة</b> لتحقيقه. المبادرات مرتّبة بالأثر مقابل الجهد — والأربع الأولى (أثر عالٍ جداً / جهد منخفض إلى متوسط) هي التي تُنفَّذ أولاً.</p>
{table(["المعرّف", "المبادرة", "المنظور", "الأهداف المخدومة", "الأثر", "الجهد", "المالك", "الموعد", "معيار النجاح"],
       [[i[0], i[1], i[2], i[3], f'<span class="badge s-{"عالية" if "عالٍ جداً" in i[4] else "تصميم"}">{i[4]}</span>', i[5], i[6], i[7], i[8]] for i in INITIATIVES], "dense")}
<h2 id="STR-RSK">المخاطر الاستراتيجية</h2>
<p class="para">بصيغة <b>سبب ← حدث ← أثر</b>. المخاطرة الأولى (SR-01) وجودية: هي التي تُسقط الخطة كلها لو تحققت.</p>
{table(["المعرّف", "المخاطرة", "الفئة", "الدرجة", "المالك", "الاستجابة", "الهدف المرتبط"],
       [[r[0], r[1], r[2], f'<span class="badge s-{"عالية" if "عالية" in r[3] else "تصميم"}">{r[3]}</span>', r[4], r[5],
         f'<a class="ref" href="#{r[6]}" dir="ltr">{r[6]}</a>'] for r in STRAT_RISKS], "dense")}
<h2 id="STR-CAD">حوكمة الاستراتيجية — الإيقاع</h2>
{table(["الحلقة", "الدورية", "المشاركون", "ما يُراجَع", "القرار المتوقع"], [list(c) for c in CADENCE])}
''', "strategy-ini"))

# ---------- الجزء الأول
P.append(divider("١", "الطبقة الحاكمة", "المبادئ · الأدوار · فصل الواجبات · كتالوج القرارات · مصفوفة الصلاحيات"))

P.append(sheet("ALL", f'''
<h2 id="HOWTO">كيف تستخدم مساحة العمل</h2>
{table(["الأداة", "الاستخدام"], [
  ["البحث", "يبحث في كل المحتوى والمعرّفات، عربي وإنجليزي، ويتجاهل التشكيل واختلاف الألف والياء. يعرض عدد النتائج ويتنقّل بينها."],
  ["فلتر الإدارة", "يعرض إدارة واحدة ويخفي ما عداها. اطبع بعدها لتحصل على «كُتيّب الإدارة» وحده."],
  ["فلتر النوع", "لعرض السياسات فقط، أو الإجراءات فقط، أو الأدلة فقط."],
  ["التعليقات", "حدّد نصاً ثم اضغط «تعليق على التحديد». التعليقات تُحفظ على هذا الجهاز فقط، وتُصدَّر وتُستورد كملف JSON."],
  ["الروابط الزرقاء", "كل معرّف (DOA-05 · CTL-22 · SOP-X01) رابط ينقلك إلى تعريفه."],
  ["تصدير PDF", "يطبع بمقاس A4 مع رأس وتذييل وترقيم صفحات تلقائي."],
])}
<h2 id="ENACT">شروط النفاذ — الفارق بين ملف ونظام شغّال</h2>
<p>هذه الوثيقة لا تُنفَّذ بذاتها. الخمسة التالية شروط لازمة، ولا يُعدّ النظام نافذاً قبل استيفائها كاملة.</p>
{table(["#", "الشرط", "لماذا", "المسؤول", "دليل الإغلاق"], [list(e) for e in ENACTMENT])}
<h3>سلسلة التشغيل الثابتة</h3>
<p class="chain">{" ← ".join(CHAIN)}</p>
<p>أي معاملة لا تمر بهذه السلسلة كاملة تُعدّ غير مكتملة، مهما كانت صحيحة موضوعياً.</p>''', "howto"))

P.append(sheet("ALL", f'''
<h2 id="SRC">سجل الأدلة والمصادر</h2>
<p>كل ما في هذه الوثيقة مسند إلى المصادر أدناه أو موسوم بأنه <b>تصميم مقترح</b>. عند تعارض إفادة شفهية مع مستند معتمد، تكون الأولوية للمستند المعتمد الأحدث.</p>
{table(["المعرّف", "المصدر", "التاريخ", "فئة الدليل", "دوره في هذا النظام"],
       [[s[0], s[1], s[2], f'<span class="badge s-{"معتمد" if s[3]=="معتمد" else "تصميم"}">{s[3]}</span>', s[4]] for s in SOURCES])}''', "sources"))

P.append(sheet("ALL", f'''
<h2 id="PRN">مبادئ التصميم</h2>
{table(["المعرّف", "المبدأ", "ما يعنيه عملياً"], [list(p) for p in PRINCIPLES])}
<h2 id="PLAT">المنصات الأربع والضابط البشري</h2>
{table(["المنصة", "الدور", "الضابط البشري"], [[k, v[0], v[1]] for k, v in PLATFORMS.items()])}
<div class="callout warn"><b>قاعدة قاطعة:</b> المنصات تحلّل وتطابق وتُجهّز وتُنبّه. الاعتماد والصرف والتعيين والترسية والتعديل التعاقدي قرارات بشرية مسجّلة باسم صاحبها. لا وكيل آلي يملك صلاحية دفع أو اعتماد أو توقيع.</div>
<h2 id="ORG">مواثيق الإدارات</h2>
{table(["الرمز", "الإدارة", "المالك", "الولاية التشغيلية", "القاعدة الحاكمة", "الوحدات"],
       [[d[0], d[1], d[2], d[3], d[4], "، ".join(d[5])] for d in DEPTS])}''', "principles"))

P.append(sheet("ALL", f'''
<h2 id="ROLES">مواثيق الأدوار الحرجة</h2>
{table(["المعرّف", "الدور", "المساءلة الأساسية", "قراراته واعتماداته", "الواجهات", "ضوابطه"], [list(r) for r in ROLES])}''', "roles"))

P.append(sheet("ALL", f'''
<h2 id="SOD">قواعد فصل الواجبات — التعارضات الممنوعة</h2>
<p>كل سطر أدناه تعارض <b>ممنوع</b> جمعه في شخص واحد. النظام يجب أن يمنعه تقنياً، لا أن يعتمد على الالتزام الطوعي.</p>
{table(["المعرّف", "التعارض الممنوع", "التوزيع الصحيح", "الضابط"],
       [[s[0], s[1], s[2], f'<a class="ref" href="#{s[3]}" dir="ltr">{s[3]}</a>'] for s in SOD])}
<h2 id="RACI">مصفوفة RACI للعمليات الجوهرية</h2>
{table(["العملية", "R — ينفّذ", "A — مسؤول عن النتيجة", "C — يُستشار", "I — يُبلَّغ"], [list(r) for r in RACI])}''', "sod"))

P.append(sheet("ALL", f'''
<h2 id="DEC">كتالوج القرارات</h2>
<p>يحدد «نوع القرار» ومالكه قبل كتابة أي إجراء. كل قرار مربوط بسطر في مصفوفة الصلاحيات.</p>
{table(["المعرّف", "الفئة", "القرار", "الموصي", "المراجعة", "الاعتماد", "سطر الصلاحية", "الزمن"],
       [[d[0], d[1], d[2], d[3], d[4], d[5], f'<a class="ref" href="#{d[6].split("/")[0]}" dir="ltr">{d[6]}</a>', d[7]] for d in DEC])}''', "dec"))

P.append(sheet("ALL", f'''
<h2 id="DOA">مصفوفة الصلاحيات الموحّدة (DOA)</h2>
<div class="callout warn"><b>حالة هذه المصفوفة: تصميم — يتطلب اعتماداً.</b> {E(DOA_NOTE)}</div>
{table(["المعرّف", "الفئة", "القرار / الحد", "الطالب", "المراجع", "المعتمد", "الاعتماد النهائي", "الدليل", "فحص فصل الواجبات"],
       [list(d) for d in DOA], "dense")}
<div class="callout"><b>قاعدة الاستثناء:</b> يُطلب قبل التنفيذ، ويعتمده صاحب صلاحية أعلى بدرجة <b>واحدة فقط</b>، ويكون محدد المدة والقيمة والشرط. لا يعتمد أحد استثناءً من طلبه. الاستثناء المتكرر ثلاث مرات يعني أن <b>الإجراء</b> معيب لا أن الموظف مخالف.</div>''', "doa"))

# ---------- الجزء الثاني: السياسات
P.append(divider("٢", "السياسات", f"{len(POLICIES)} سياسة مكتوبة بالكامل — قواعد إلزامية مرقّمة وعواقب وضوابط"))
P.append(sheet("ALL", f'''
<h2 id="POL">معمارية السياسات</h2>
<p class="chain">دليل الحوكمة ← سياسة ← إجراء تشغيلي (SOP) ← تعليمات عمل ← نموذج/قائمة تحقق ← سجل/دليل</p>
<p>السياسة تُلزم بالقواعد، والإجراء يشرح «كيف»، والنموذج يجمع البيانات، والسجل يثبت التنفيذ. كل وثيقة لها مالك وإصدار وتاريخ نفاذ ومراجعة دورية وعلاقة صريحة بمصفوفة الصلاحيات.</p>
{table(["المعرّف", "السياسة", "العائلة", "المالك", "الحالة"],
       [[f'<a class="ref" href="#{p["id"]}" dir="ltr">{p["id"]}</a>', p["title"], p["family"], p["owner"], p["priority"]] for p in POLICIES])}
<h3>سياسات مشروطة — لم تُكتب بعد، وهذا قرار مبرَّر</h3>
{table(["المعرّف", "السياسة", "الحالة", "المبرر"], [list(c) for c in CONDITIONAL])}''', "policies"))
for p in POLICIES:
    P.append(sheet(p["dept"], policy_html(p)))

# ---------- الجزء الثالث: العمليات التقاطعية
P.append(divider("٣", "العمليات التقاطعية", "11 عملية End-to-End لا تخص إدارة واحدة — بيتها هنا ولا تُكرَّر", "CROSS"))
P.append(sheet("CROSS", f'''
<h2 id="XPROC">فهرس العمليات التقاطعية</h2>
<p>تكرار هذه العمليات داخل الإدارات يعني نسخاً تتعارض بعد أول تعديل. لذلك بيتها واحد، والإدارات تشير إليه.</p>
{table(["المعرّف", "العملية", "المالك", "زمن الخدمة"],
       [[f'<a class="ref" href="#{s["id"]}" dir="ltr">{s["id"]}</a>', s["title"], s["owner"], s["sla"]] for s in CROSS])}''', "xproc"))
for s in CROSS:
    P.append(sheet("CROSS", sop_html(s)))

# ---------- الجزء الرابع: الإدارات
P.append(divider("٤", "الإدارات", "ميثاق كل إدارة وسياساتها وإجراءاتها الداخلية ومؤشراتها"))
DEPT_SOPS = {code: [s for s in ALL_SOPS if s["dept"] == code] for code, *_ in DEPTS}
for code, name, owner, mandate, rule, units in DEPTS:
    sops = DEPT_SOPS.get(code, [])
    pols = [p for p in POLICIES if p["dept"] == code]
    mets = [m for m in METRICS if m[2] == code]
    P.append(sheet(code, f'''
<h2 id="DEPT-{code}">إدارة: {E(name)}</h2>
{table(["الحقل", "القيمة"], [["المالك", owner], ["الولاية التشغيلية", mandate], ["الوحدات", "، ".join(units)]])}
<div class="callout"><b>القاعدة الحاكمة:</b> {E(rule)}</div>
<h3>سياسات هذه الإدارة</h3>
{table(["المعرّف", "السياسة"], [[f'<a class="ref" href="#{p["id"]}" dir="ltr">{p["id"]}</a>', p["title"]] for p in pols]) if pols else "<p>لا تملك هذه الإدارة سياسة أُم خاصة؛ تعمل تحت السياسات المركزية.</p>"}
<h3>إجراءات هذه الإدارة ({len(sops)})</h3>
{table(["المعرّف", "الإجراء", "المُشغِّل", "زمن الخدمة"],
       [[f'<a class="ref" href="#{s["id"]}" dir="ltr">{s["id"]}</a>', s["title"], s["trigger"], s["sla"]] for s in sops]) if sops else "<p>—</p>"}
<h3>مؤشرات هذه الإدارة ({len(mets)})</h3>
{table(["المعرّف", "المؤشر", "المستهدف", "عتبة الإنذار"],
       [[f'<a class="ref" href="#{m[0]}" dir="ltr">{m[0]}</a>', m[3], m[7], m[8]] for m in mets]) if mets else "<p>—</p>"}''', f"DEPT-{code}"))
    for s in sops:
        P.append(sheet(code, sop_html(s)))


# ---------- الأوصاف الوظيفية
P.append(divider("٥", "معمارية الوظائف والأوصاف الوظيفية", f"{len(JOBS)} مسمّى داخل الهيكل المعتمد — عقد مساءلة لا قائمة مهام"))
P.append(sheet("ALL", f'''
<h2 id="JOBS">معمارية الوظائف</h2>
<div class="callout">{JOBS_NOTE}</div>
<h3>مستويات الرتب (Job Bands)</h3>
{table(["الرتبة", "المستوى", "المسميات", "طبيعة القرار", "حدود الصلاحية"], [list(b) for b in BANDS])}
<h3>كتالوج المسميات</h3>
{table(["المعرّف", "المسمى", "الإدارة", "الرتبة", "يرفع إلى", "الحالة"],
       [[f'<a class="ref" href="#{j[0]}" dir="ltr">{j[0]}</a>', j[1], DEPT_NAME.get(j[2], j[2]), j[3], j[4],
         f'<span class="badge s-{"معتمد" if j[14]=="معتمد" else "تصميم"}">{j[14]}</span>'] for j in JOBS], "dense")}
<h3>الخدمات الخارجية — ليست وظائف داخلية في هذا الهيكل</h3>
{table(["الجهة", "الصفة", "النطاق"], [list(x) for x in EXTERNAL])}
<h3 id="JOBGAP">فجوات القدرة الحرجة — ما ينقص لتشغيل استراتيجية 2027</h3>
<p class="para">هذه ليست شواغر إدارية بل <b>شروط تشغيل</b> للخطة الاستراتيجية. بدونها، أهداف المحور المالي بلا من ينفّذها.</p>
{table(["الفجوة", "لماذا هي حرجة", "الوظائف/المبادرات", "الأولوية"], [list(g) for g in GAPS])}
''', "jobs"))
P.append(sheet("ALL", jobs_html()))

# ---------- الجزء الخامس: السجلات المركزية
P.append(divider("٦", "السجلات المركزية", "الضوابط · المخاطر · المؤشرات · اتفاقيات الخدمة · النماذج · السجلات · صلاحيات الأنظمة"))

P.append(sheet("ALL", f'''
<h2 id="CTL">سجل الضوابط ({len(CONTROLS)})</h2>
<p>كل ضابط له هدف رقابي ونوع ومالك وتكرار ودليل و<b>طريقة اختبار</b>. الضابط الذي لا يمكن اختباره ليس ضابطاً.</p>
{table(["المعرّف", "الضابط", "الهدف الرقابي", "النوع", "المالك", "التكرار", "الدليل", "طريقة الاختبار"],
       [list(c) for c in CONTROLS], "dense")}''', "controls"))

P.append(sheet("ALL", f'''
<h2 id="RSK">سجل المخاطر ({len(RISKS)})</h2>
<p>كل مخاطرة بصيغة <b>سبب ← حدث ← أثر</b>. الصيغ العامة مثل «تأخر المشروع» مرفوضة لأنها لا تقود إلى ضابط.</p>
{table(["المعرّف", "المخاطرة (سبب ← حدث ← أثر)", "الفئة", "الدرجة", "المالك", "الاستجابة", "الضوابط", "المؤشر"],
       [[r[0], r[1], r[2], f'<span class="badge s-{"عالية" if r[3]=="عالية" else "تصميم"}">{r[3]}</span>', r[4], r[5],
         link(r[6]), f'<a class="ref" href="#{r[7]}" dir="ltr">{r[7]}</a>'] for r in RISKS], "dense")}''', "risks"))

kpis = [m for m in METRICS if m[1] == "KPI"]
kris = [m for m in METRICS if m[1] == "KRI"]
P.append(sheet("ALL", f'''
<h2 id="KPI">مكتبة مؤشرات الأداء — KPI ({len(kpis)})</h2>
<p>لكل مؤشر <b>معادلة صريحة</b> ومصدر بيانات وعتبة و<b>استجابة إلزامية</b>. المؤشر بلا استجابة عند التجاوز ضوضاء لا قياس.</p>
{table(["المعرّف", "الإدارة", "المؤشر", "المعادلة", "المصدر", "الدورية", "المستهدف", "عتبة الإنذار", "الاستجابة الإلزامية", "المالك"],
       [[m[0], DEPT_NAME.get(m[2], m[2]), m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10]] for m in kpis], "dense")}''', "kpis"))

P.append(sheet("ALL", f'''
<h2 id="KRI">مكتبة مؤشرات الخطر — KRI ({len(kris)})</h2>
<p>مؤشرات إنذار مبكر. كل تجاوز له استجابة إلزامية محددة، لا «متابعة».</p>
{table(["المعرّف", "الإدارة", "المؤشر", "المعادلة", "المصدر", "الدورية", "الحد المقبول", "عتبة التصعيد", "الاستجابة الإلزامية", "المالك"],
       [[m[0], DEPT_NAME.get(m[2], m[2]), m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10]] for m in kris], "dense")}''', "kris"))

P.append(sheet("ALL", f'''
<h2 id="SLA">كتالوج اتفاقيات مستوى الخدمة والواجهات ({len(SLAS)})</h2>
<div class="callout"><b>أساس احتساب الوقت:</b> أيام العمل تُحسب من <b>تاريخ اكتمال المستند</b>، لا من تاريخ استلامه ناقصاً. المستند الناقص لا يبدأ عدّاده.</div>
{table(["المعرّف", "الواجهة", "المرسل", "المستلم", "الحزمة", "معايير القبول", "الزمن", "مسار الرفض", "التصعيد"],
       [[s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[8], s[9]] for s in SLAS], "dense")}''', "slas"))

P.append(sheet("ALL", f'''
<h2 id="SYS">مصفوفة صلاحيات الأنظمة</h2>
<div class="callout warn"><b>قاعدة حاكمة:</b> الصلاحية الورقية تتجاوزها الصلاحية الرقمية. إذا كان النظام يسمح لمستخدم بتجاوز حد في الـDOA، فالحد <b>غير موجود عملياً</b>. مطابقة صلاحيات الأنظمة للـDOA شرط نفاذ (ENA-03) وتُراجَع ربع سنوياً.</div>
{table(["المنصة", "المالك", "الصلاحيات التشغيلية", "الاعتمادات", "القيد الحاكم"], [list(s) for s in SYS_PERMS])}
<h2 id="FRM">حزمة النماذج ({len(FORMS)})</h2>
{table(["المعرّف", "النموذج", "الإدارة", "الحقول الإلزامية"],
       [[f[0], f[1], DEPT_NAME.get(f[2], f[2]), f[3]] for f in FORMS], "dense")}''', "forms"))

P.append(sheet("ALL", f'''
<h2 id="REG">السجلات ({len(REGISTERS)})</h2>
{table(["المعرّف", "السجل", "الإدارة", "المالك", "الحقول الإلزامية"],
       [[r[0], r[1], DEPT_NAME.get(r[2], r[2]), r[3], r[4]] for r in REGISTERS], "dense")}''', "regs"))

# ---------- الجزء السادس: التطبيق
P.append(divider("٧", "التطبيق والنضج", "الموجات الست · مقياس النضج · لغة الحالة"))
P.append(sheet("ALL", f'''
<h2 id="ROADMAP">خطة التطبيق — الموجات الست</h2>
{table(["الموجة", "العنوان", "المخرجات", "اختبار النجاح"], [list(r) for r in ROADMAP])}
<h2 id="MAT">مقياس النضج</h2>
{table(["المستوى", "الوصف", "دليل القياس"], [list(m) for m in MATURITY])}
<div class="callout">{E(MATURITY_TARGET)}</div>
<h2 id="STATUS">لغة الحالة — دقيقة وغير قابلة للخلط</h2>
{table(["الحالة", "ما تعنيه بالضبط"], [
  ["مصمَّم", "المحتوى موجود ومتسق داخلياً. لا يعني أنه معتمد ولا مطبَّق."],
  ["معتمد", "أجازه صاحب الصلاحية المسمّى بقرار مؤرَّخ."],
  ["مُهيَّأ", "مُنفَّذ في النظام: النماذج والصلاحيات والسجلات جاهزة."],
  ["مُجرَّب", "اختُبر على معاملات حقيقية وقيست نتائجه."],
  ["مطبَّق", "أصبح طريقة العمل الإلزامية بعد تاريخ قطع معلن."],
  ["فعّال", "اجتازت ضوابطه مراجعة مبنية على أدلة وعيّنات."],
])}
<div class="callout warn">لن تجد في هذه الوثيقة كلمة «مكتمل» أو «متوافق» أو «أفضل ممارسة» بلا تحديد النطاق المختبَر والدليل. المكتمل الآن هو <b>التصميم</b> فقط.</div>''', "roadmap"))

# ---------- الجزء السابع: الأدلة الإرشادية
P.append(divider("٨", "الأدلة الإرشادية", f"{len(GUIDES)} أدلة تُكيَّف ولا تُنسخ — إرشادية لا إلزامية"))
P.append(sheet("ALL", f'''
<h2 id="GID">فهرس الأدلة الإرشادية</h2>
<div class="callout warn">{DISCLAIMER}</div>
{table(["المعرّف", "الدليل", "المرجع"],
       [[f'<a class="ref" href="#{g[0]}" dir="ltr">{g[0]}</a>', g[1], f'<bdi dir="ltr" class="mono">{E(g[2])}</bdi>'] for g in GUIDES])}''', "guides"))
for g in GUIDES:
    P.append(sheet("ALL", guide_html(g)))

SPLIT_AT = len(P) // 2

# =============================================================== القالب
DEPT_OPTS = "".join(f'<option value="{c}">{E(n)}</option>' for c, n, *_ in DEPTS)

HTML = f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(META["title"])} — {E(META["company"])}</title>
<style>
:root{{--ink:#16202e;--navy:#19395f;--navy2:#2c5580;--teal:#087f8c;--gold:#c79430;--paper:#fff;--wash:#eef3f6;--line:#d3dde5;--muted:#6b7a89;--danger:#a83434;--shadow:0 10px 40px #15243a1a;--radius:12px}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}
body{{margin:0;background:#e3eaef;color:var(--ink);font-family:"Noto Kufi Arabic","IBM Plex Sans Arabic",Tajawal,"thmanyah sans","Geeza Pro","Segoe UI",system-ui,sans-serif;line-height:1.7;font-size:14px}}
button,input,select,textarea{{font:inherit}}
.skip{{position:fixed;top:-80px;right:16px;background:#fff;padding:8px;z-index:99}}.skip:focus{{top:8px}}
.toolbar{{position:sticky;top:0;z-index:30;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 16px;background:#12283fF2;color:#fff;backdrop-filter:blur(10px);box-shadow:0 2px 18px #0004}}
.search-wrap{{display:flex;gap:6px;flex:1;min-width:280px}}
.search-wrap input{{width:100%;min-width:0;padding:8px 12px;border:1px solid #ffffff44;border-radius:8px;background:#fff;color:#111}}
.toolbar button,.toolbar select{{border:1px solid #ffffff44;border-radius:8px;background:#ffffff16;color:#fff;padding:7px 11px;cursor:pointer}}
.toolbar select option{{color:#111}}
.toolbar button:hover,.toolbar button:focus,.toolbar select:focus{{background:#ffffff2e;outline:2px solid #ffd76b;outline-offset:2px}}
.count{{min-width:80px;font-size:12px;color:#cfe0ee}}
.layout{{display:grid;grid-template-columns:300px minmax(0,1fr) 330px;gap:18px;max-width:1760px;margin:20px auto;padding:0 18px}}
.panel{{position:sticky;top:70px;align-self:start;max-height:calc(100vh - 92px);overflow:auto;background:#f7fafc;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}}
.panel h2{{margin:0;padding:13px 16px;background:var(--navy);color:#fff;font-size:14px;border:0}}
.panel-body{{padding:10px}}
.toc a{{display:block;padding:6px 9px;border-radius:6px;color:#26394d;text-decoration:none;font-size:12.5px}}
.toc a.lvl0{{font-weight:700;background:#e7eef3;color:var(--navy);margin-top:8px}}
.toc a.lvl2{{padding-right:20px;font-size:11.5px;color:#55697d}}
.toc a:hover,.toc a:focus{{background:#dceaf1;outline:2px solid var(--teal)}}
.document{{min-width:0}}
.sheet{{position:relative;width:210mm;max-width:100%;margin:0 auto 16px;padding:16mm 14mm;background:var(--paper);box-shadow:var(--shadow);border-radius:4px}}
h1,h2,h3,h4{{color:var(--navy);line-height:1.4;scroll-margin-top:80px}}
h1{{font-size:27px;margin:0 0 12px}}
h2{{font-size:19px;margin:22px 0 10px;padding:0 10px 6px 0;border-bottom:2px solid var(--teal)}}
h2:first-child{{margin-top:0}}
h3{{font-size:15px;color:var(--teal);margin:16px 0 7px}}
h4{{font-size:12.5px;margin:13px 0 5px;color:var(--navy2);border-right:3px solid var(--gold);padding-right:7px}}
p,li,td,th{{font-size:11.6px}}
p.para{{text-align:justify}}
p.tiny{{font-size:10px;color:var(--muted)}}
.tw{{width:100%;overflow-x:auto;margin:8px 0}}
table{{border-collapse:collapse;width:100%;table-layout:fixed}}
th,td{{border:1px solid #c8d3dc;padding:5px 7px;vertical-align:top;text-align:right;word-wrap:break-word;overflow-wrap:anywhere}}
th{{background:var(--navy);color:#fff;font-weight:600;font-size:11px}}
tr:nth-child(even) td{{background:#f4f8fa}}
table.dense{{table-layout:auto}}
table.dense th,table.dense td{{padding:4px 5px;font-size:10.2px}}
table.steps{{table-layout:fixed}}
table.steps th:nth-child(1),table.steps td:nth-child(1){{width:4%;text-align:center}}
table.steps th:nth-child(2),table.steps td:nth-child(2){{width:17%}}
table.steps th:nth-child(3),table.steps td:nth-child(3){{width:47%}}
table.steps th:nth-child(4),table.steps td:nth-child(4){{width:11%}}
table.steps th:nth-child(5),table.steps td:nth-child(5){{width:11%}}
table.steps th:nth-child(6),table.steps td:nth-child(6){{width:10%;text-align:center}}
bdi.mono{{font-size:9.5px;color:#55697d;word-break:break-all}}
ul,ol{{margin:5px 0;padding-right:18px}}
ol.rules li{{margin-bottom:4px}}
.badge{{display:inline-block;border-radius:999px;padding:2px 9px;background:#dfeef1;color:#075c65;font-size:9.5px;white-space:nowrap}}
.badge.id{{background:var(--navy);color:#fff;font-weight:700;letter-spacing:.3px}}
.badge.k{{background:#e6eef3;color:var(--navy)}}
.badge.d{{background:#f3ead8;color:#7a5610}}
.badge.s-تصميم{{background:#fff3d9;color:#7a5610}}
.badge.s-معتمد{{background:#e7f5ed;color:#0a4b2b}}
.badge.s-إرشادي{{background:#e8ecfb;color:#39418f}}
.badge.s-عالية{{background:#fdeeee;color:#7a1f1f}}
.callout{{border-right:4px solid var(--gold);background:#fffaf0;padding:8px 12px;margin:10px 0;font-size:11.4px;border-radius:0 6px 6px 0}}
.callout.warn{{border-right-color:var(--danger);background:#fdf0f0}}
.object{{border:1px solid var(--line);border-radius:10px;padding:13px;margin:6px 0;background:#fff}}
.object-head{{display:flex;align-items:center;flex-wrap:wrap;gap:6px;border-bottom:1px solid var(--line);padding-bottom:8px;margin-bottom:9px}}
.object-head h3{{margin:0;flex:1;min-width:200px;font-size:16px;color:var(--navy)}}
.ref{{color:#0b5f9e;text-decoration:none;border-bottom:1px dotted #0b5f9e;font-size:10.5px;white-space:nowrap}}
.ref:hover,.ref:focus{{background:#dcecf0;outline:2px solid var(--teal)}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:9px;margin:10px 0}}
.cell{{border:1px solid var(--line);border-radius:8px;padding:8px;background:#f8fbfc;font-size:10.8px}}
.cell b{{color:var(--navy);display:block;margin-bottom:4px;font-size:11px}}
.cell ul{{margin:0;padding-right:15px}}
figure.kt{{margin:10px 0;border:1px solid var(--line);border-radius:8px;padding:8px 6px 4px;background:#fcfdfe}}
figcaption{{font-size:10px;color:var(--muted);margin-bottom:4px;text-align:center;font-weight:600}}
svg.flow{{width:100%;height:auto;display:block}}
.chain{{background:var(--wash);border-radius:8px;padding:9px;font-weight:700;color:var(--navy);text-align:center;font-size:11.5px}}
.cover-sheet{{padding-top:34mm}}
.cover{{text-align:center}}
.cover-bar{{width:70px;height:5px;background:var(--teal);border-radius:3px;margin:0 auto 20px}}
.cover h1{{font-size:33px;margin:14px 0 6px;letter-spacing:-.5px}}
.cover-sub{{color:var(--teal);font-size:17px;font-weight:700;margin:0}}
.cover-lead{{color:var(--muted);font-size:12.5px;margin:8px auto 18px;padding:0 8%}}
.cover table{{margin:14px auto}}
.cover .callout{{text-align:right;margin:16px 0 0}}
.stats{{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin:18px 0}}
.stats div{{border:1px solid var(--line);border-radius:9px;padding:9px 4px;background:var(--wash)}}
.stats b{{display:block;font-size:21px;color:var(--navy);line-height:1.2}}
.stats span{{font-size:9.5px;color:var(--muted)}}
.divider{{background:linear-gradient(135deg,#19395f,#0d2237);color:#fff;padding:26mm 14mm}}
.dv{{display:flex;align-items:center;gap:22px}}
.dv-num{{font-size:76px;font-weight:800;color:#ffffff26;line-height:1}}
.dv-title{{color:#fff;border:0;margin:0;font-size:26px}}
.dv-sub{{color:#b9cede;margin:6px 0 0;font-size:12px}}
.comment-card{{border:1px solid var(--line);border-radius:9px;background:#fff;padding:10px;margin-bottom:9px}}
.comment-card small{{color:var(--muted)}}
.comment-actions{{display:flex;gap:5px;margin-top:8px;flex-wrap:wrap}}
.comment-actions button,.secondary{{border:1px solid var(--line);background:#fff;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:11px}}
.resolved{{opacity:.6}}
.quote{{border-right:3px solid var(--teal);padding-right:8px;color:#445;max-height:70px;overflow:auto;font-size:11px}}
.empty{{color:var(--muted);font-size:12px}}
mark{{background:#ffe36e;color:#111;border-radius:2px}}
.active-hit{{outline:3px solid #ef7f1a;background:#ffc65c}}
.dialog{{border:0;border-radius:12px;box-shadow:0 24px 80px #0008;max-width:520px;width:calc(100% - 30px)}}
.dialog::backdrop{{background:#0b1729aa}}
.dialog label{{display:block;margin-top:9px;font-size:12px}}
.dialog input,.dialog textarea{{width:100%;padding:8px;border:1px solid var(--line);border-radius:7px}}
.dialog menu{{display:flex;gap:8px;padding:0;margin-top:12px}}
.dialog button{{padding:7px 12px;border:0;border-radius:7px;background:var(--navy);color:#fff;cursor:pointer}}
@media(max-width:1250px){{.layout{{grid-template-columns:240px minmax(0,1fr)}}.comments-panel{{position:fixed;left:12px;bottom:12px;top:76px;width:min(360px,calc(100vw - 24px));z-index:25;display:none}}.comments-panel.open{{display:block}}.sheet{{width:100%}}}}
@media(max-width:760px){{.layout{{display:block;padding:0 8px}}.toc-panel{{position:fixed;right:8px;top:70px;bottom:8px;width:min(330px,calc(100vw - 16px));z-index:26;display:none}}.toc-panel.open{{display:block}}.sheet{{padding:18px 14px}}.two,.grid3,.stats{{grid-template-columns:1fr}}}}

.page-header,.page-footer{{display:none}}
@page{{
  size:A4;margin:17mm 13mm 15mm;
  @top-right{{content:element(rh);font-size:7.5pt;color:#6b7a89;border-bottom:.4pt solid #d3dde5;padding-bottom:2mm;width:100%}}
  @bottom-right{{content:element(rf);font-size:7.5pt;color:#6b7a89}}
  @bottom-left{{content:"صفحة " counter(page);font-size:7.5pt;color:#6b7a89}}
}}
@media print{{.page-header{{display:block;position:running(rh)}}.page-footer{{display:block;position:running(rf)}}}}
@media print{{
 body{{background:#fff;font-size:8pt;line-height:1.55}}
 .no-print,.panel,.toolbar{{display:none!important}}
 .layout{{display:block;max-width:none;margin:0;padding:0}}
 .sheet{{width:auto;margin:0;padding:0 0 4mm;box-shadow:none;border-radius:0;break-before:page}}
 .sheet:first-child{{break-before:auto}}
 .sheet[hidden]{{display:none!important}}
 .cover-sheet{{padding-top:24mm}}
 .divider{{padding:30mm 10mm;break-after:page}}
 .dv-num{{color:#ffffff33}}
 p,li,td,th{{font-size:8pt}}
 table.dense th,table.dense td{{font-size:7pt;padding:3px 4px}}
 h1{{font-size:20pt}}h2{{font-size:13pt}}h3{{font-size:10.5pt}}h4{{font-size:9pt}}
 h1,h2,h3,h4,figcaption{{break-after:avoid}}
 .object-head{{break-after:avoid}}
 tr,figure,.cell,.callout,.chain,.stats{{break-inside:avoid}}
 figure.kt{{break-inside:avoid;page-break-inside:avoid}}
 .two,.grid3{{break-inside:avoid}}
 thead{{display:table-header-group}}
 a,.ref{{color:inherit;text-decoration:none;border:0}}
 mark{{background:transparent}}
 .badge{{border:1px solid #b9c5cf}}
 .object{{border:0;padding:0}}
 .tw{{overflow:visible}}
}}
@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important;animation:none!important}}}}
</style>
</head>
<body>
<a class="skip no-print" href="#main">انتقل للمحتوى</a>
<div class="page-header" id="rh">{E(META["company"])} — {E(META["title"])}</div>
<div class="page-footer" id="rf">{E(META["classification"])} · {META["docid"]} · {META["version"]}</div>
<header class="toolbar no-print" aria-label="أدوات المستند">
  <div class="search-wrap">
    <input id="search" type="search" placeholder="ابحث في النظام كله… (مثال: مستخلص · DOA-05 · عهدة · PMBOK)" aria-label="بحث">
    <button id="prevHit" title="النتيجة السابقة" aria-label="النتيجة السابقة">↑</button>
    <button id="nextHit" title="النتيجة التالية" aria-label="النتيجة التالية">↓</button>
    <button id="clearSearch">مسح</button>
  </div>
  <span id="hitCount" class="count">0 نتيجة</span>
  <select id="deptFilter" aria-label="فلتر الإدارة"><option value="">كل الإدارات</option><option value="CROSS">عمليات تقاطعية</option>{DEPT_OPTS}</select>
  <select id="typeFilter" aria-label="فلتر النوع"><option value="">كل الأنواع</option><option>سياسة</option><option>إجراء</option><option>دليل</option><option>هدف استراتيجي</option><option>وصف وظيفي</option></select>
  <button id="addComment">تعليق على التحديد</button>
  <button id="toggleComments">التعليقات</button>
  <button id="toggleToc">الفهرس</button>
  <button id="printBtn">تصدير PDF</button>
</header>
<div class="layout">
  <nav class="panel toc-panel no-print" aria-label="فهرس المحتويات"><h2>المحتويات</h2><div class="panel-body"><div id="toc" class="toc"></div></div></nav>
  <main id="main" class="document" style="counter-reset:page {PAGE_OFFSET}">
{"".join(P)}
  </main>
  <aside class="panel comments-panel no-print" aria-label="التعليقات"><h2>تعليقات المراجعة</h2>
    <div class="panel-body">
      <p class="empty">التعليقات تُحفظ على هذا الجهاز وهذا المتصفح فقط، ولا تُرسل إلى أي جهة. صدّرها كملف JSON لمشاركتها.</p>
      <div style="display:flex;gap:6px;margin:10px 0">
        <button class="secondary" id="exportComments">تصدير JSON</button>
        <button class="secondary" id="importComments">استيراد</button>
        <input id="importFile" type="file" accept="application/json" hidden>
      </div>
      <div id="comments"></div>
    </div>
  </aside>
</div>
<dialog id="commentDialog" class="dialog">
  <form method="dialog" id="commentForm">
    <h2>إضافة تعليق</h2>
    <p id="selectedQuote" class="quote"></p>
    <label>الاسم<input id="commentAuthor" maxlength="80" value="مراجع"></label>
    <label>التعليق<textarea id="commentBody" rows="5" required maxlength="2000"></textarea></label>
    <menu><button value="cancel">إلغاء</button><button id="saveComment" value="default">حفظ</button></menu>
  </form>
</dialog>
<script>
(()=>{{'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],KEY='kelma-governance-comments-v1';
let hits=[],hitIndex=-1,pending=null;
const norm=s=>String(s).toLowerCase().normalize('NFKD').replace(/[\\u064b-\\u065f\\u0670]/g,'').replace(/[إأآٱ]/g,'ا').replace(/ى/g,'ي').replace(/ة/g,'ه').replace(/ـ/g,'');
function buildToc(){{const t=$('#toc');t.textContent='';
 $$('#main .dv-title,#main h2[id],#main .object-head h3').forEach((h,i)=>{{
  const a=document.createElement('a');
  let target=h;
  if(h.classList.contains('dv-title')){{target=h.closest('.sheet');a.className='lvl0';}}
  else if(h.tagName==='H3'){{target=h.closest('.object');a.className='lvl2';}}
  if(!target.id)target.id='n-'+i;
  a.href='#'+target.id;a.textContent=h.textContent;t.appendChild(a);}});}}
function clearMarks(){{$$('mark[data-s]').forEach(m=>{{const t=document.createTextNode(m.textContent);const p=m.parentNode;m.replaceWith(t);p&&p.normalize();}});hits=[];hitIndex=-1;$('#hitCount').textContent='0 نتيجة';}}
function search(){{clearMarks();const raw=$('#search').value.trim();if(!raw)return;const q=norm(raw);
 const w=document.createTreeWalker($('#main'),NodeFilter.SHOW_TEXT,{{acceptNode:n=>{{const p=n.parentElement;
  if(!p||['SCRIPT','STYLE','MARK'].includes(p.tagName))return NodeFilter.FILTER_REJECT;
  if(p.closest('[hidden]'))return NodeFilter.FILTER_REJECT;
  return norm(n.nodeValue).includes(q)?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT;}}}});
 const nodes=[];while(w.nextNode())nodes.push(w.currentNode);
 nodes.forEach(n=>{{const txt=n.nodeValue,nt=norm(txt);const i=nt.indexOf(q);if(i<0)return;
  const b=document.createTextNode(txt.slice(0,i)),m=document.createElement('mark'),a=document.createTextNode(txt.slice(i+raw.length));
  m.dataset.s='1';m.textContent=txt.slice(i,i+raw.length);n.replaceWith(b,m,a);hits.push(m);}});
 $('#hitCount').textContent=hits.length+' نتيجة';if(hits.length)goto(0);}}
function goto(i){{if(!hits.length)return;hits.forEach(h=>h.classList.remove('active-hit'));hitIndex=(i+hits.length)%hits.length;
 hits[hitIndex].classList.add('active-hit');hits[hitIndex].scrollIntoView({{block:'center'}});$('#hitCount').textContent=(hitIndex+1)+' / '+hits.length;}}
const load=()=>{{try{{const v=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(v)?v:[];}}catch(e){{return[];}}}};
const save=v=>{{try{{localStorage.setItem(KEY,JSON.stringify(v));}}catch(e){{alert('تعذّر حفظ التعليق على هذا المتصفح.');}}}};
function renderComments(){{const box=$('#comments'),items=load();box.textContent='';
 if(!items.length){{const p=document.createElement('p');p.className='empty';p.textContent='لا توجد تعليقات محفوظة على هذا الجهاز.';box.appendChild(p);return;}}
 items.forEach(c=>{{const card=document.createElement('article');card.className='comment-card'+(c.status==='resolved'?' resolved':'');
  const s=document.createElement('small');s.textContent=c.author+' · '+new Date(c.created).toLocaleString('ar');
  const q=document.createElement('p');q.className='quote';q.textContent=c.quote||('القسم: '+c.section);
  const b=document.createElement('p');b.textContent=c.body;
  const acts=document.createElement('div');acts.className='comment-actions';
  const mk=(l,fn)=>{{const btn=document.createElement('button');btn.textContent=l;btn.onclick=fn;acts.appendChild(btn);}};
  mk(c.status==='resolved'?'إعادة فتح':'حل',()=>update(c.id,{{status:c.status==='resolved'?'open':'resolved'}}));
  mk('تعديل',()=>{{const v=prompt('عدّل التعليق',c.body);if(v!==null&&v.trim())update(c.id,{{body:v.trim()}});}});
  mk('حذف',()=>{{if(confirm('حذف التعليق؟')){{save(load().filter(x=>x.id!==c.id));renderComments();}}}});
  mk('اذهب',()=>{{const el=document.getElementById(c.section);if(el)el.scrollIntoView({{block:'center'}});}});
  card.append(s,q,b,acts);box.appendChild(card);}});}}
function update(id,patch){{save(load().map(x=>x.id===id?Object.assign({{}},x,patch):x));renderComments();}}
function prepare(){{const sel=window.getSelection(),quote=sel?sel.toString().trim():'';
 let node=(sel&&sel.anchorNode)?(sel.anchorNode.nodeType===1?sel.anchorNode:sel.anchorNode.parentElement):null;
 const sec=node?node.closest('.object,.sheet'):null;
 pending={{quote:quote.slice(0,1000),section:(sec&&sec.id)?sec.id:'main'}};
 $('#selectedQuote').textContent=quote||('القسم: '+pending.section);
 $('#commentBody').value='';$('#commentDialog').showModal();}}
function applyFilters(){{const d=$('#deptFilter').value,t=$('#typeFilter').value;
 $$('.object').forEach(o=>{{o.hidden=!!(t&&o.dataset.type!==t);}});
 $$('.sheet').forEach(p=>{{
  let show=true;
  if(d)show=(p.dataset.dept===d);
  if(t){{const objs=[...p.querySelectorAll('.object')];show=show&&objs.length>0&&objs.some(o=>o.dataset.type===t);}}
  p.hidden=!show;}});
 clearMarks();}}
$('#search').addEventListener('input',()=>{{clearTimeout(window.__t);window.__t=setTimeout(search,200);}});
$('#prevHit').onclick=()=>goto(hitIndex-1);
$('#nextHit').onclick=()=>goto(hitIndex+1);
$('#clearSearch').onclick=()=>{{$('#search').value='';clearMarks();}};
$('#addComment').onclick=prepare;
$('#toggleComments').onclick=()=>$('.comments-panel').classList.toggle('open');
$('#toggleToc').onclick=()=>$('.toc-panel').classList.toggle('open');
$('#printBtn').onclick=()=>window.print();
$('#deptFilter').onchange=applyFilters;
$('#typeFilter').onchange=applyFilters;
$('#commentForm').addEventListener('submit',e=>{{if(e.submitter&&e.submitter.value==='cancel')return;
 const body=$('#commentBody').value.trim();if(!body){{e.preventDefault();return;}}
 const items=load();
 items.push({{id:(crypto.randomUUID?crypto.randomUUID():String(Date.now())),section:pending.section,quote:pending.quote,
  author:($('#commentAuthor').value.trim()||'مراجع').slice(0,80),body:body.slice(0,2000),status:'open',created:new Date().toISOString()}});
 save(items);setTimeout(renderComments);}});
$('#exportComments').onclick=()=>{{const blob=new Blob([JSON.stringify(load(),null,2)],{{type:'application/json'}});
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='governance-comments.json';a.click();URL.revokeObjectURL(a.href);}};
$('#importComments').onclick=()=>$('#importFile').click();
$('#importFile').onchange=async e=>{{try{{const f=e.target.files[0];if(!f)return;const data=JSON.parse(await f.text());
 if(!Array.isArray(data))throw new Error('bad');
 save(data.slice(0,5000).map(x=>({{id:String(x.id||Date.now()),section:String(x.section||'main').slice(0,80),
  quote:String(x.quote||'').slice(0,1000),author:String(x.author||'مراجع').slice(0,80),body:String(x.body||'').slice(0,2000),
  status:x.status==='resolved'?'resolved':'open',created:x.created||new Date().toISOString()}})));
 renderComments();}}catch(err){{alert('ملف التعليقات غير صالح.');}}}};
document.addEventListener('keydown',e=>{{if((e.ctrlKey||e.metaKey)&&e.key==='f'){{e.preventDefault();$('#search').focus();}}
 if(e.key==='Escape'){{$('#search').value='';clearMarks();}}}});
buildToc();renderComments();
}})();
</script>
</body>
</html>'''

if PART == "A":
    HTML = HTML.replace("".join(P), "".join(P[:SPLIT_AT]))
elif PART == "B":
    HTML = HTML.replace("".join(P), "".join(P[SPLIT_AT:]))
BASE = os.environ.get("OUT_NAME", "governance-workspace")
OUT = ("%s.pdfsrc%s.html" % (BASE, PART.lower())) if PDF_MODE else ("%s.html" % BASE)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"{OUT} | SOPs {len(ALL_SOPS)} | Policies {len(POLICIES)} | Guides {len(GUIDES)} | "
      f"DOA {len(DOA)} | Controls {len(CONTROLS)} | Metrics {len(METRICS)} | Sheets {len(P)}")
