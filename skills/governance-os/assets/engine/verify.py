# -*- coding: utf-8 -*-
"""تحقق التتبّع: كل مرجع في كل إجراء وسياسة يجب أن يوجد له تعريف."""
import re, sys
from data_core import DOA, DEC, SOD, ROLES
from data_policies import POLICIES
from data_registers import CONTROLS, RISKS, METRICS, SLAS, FORMS, REGISTERS
import glob, importlib
SOPS = []
for _f in sorted(glob.glob("data_sops_*.py")):
    _m = importlib.import_module(_f[:-3])
    for _n in dir(_m):
        _v = getattr(_m, _n)
        if isinstance(_v, list) and _v and isinstance(_v[0], dict) and "id" in _v[0] and "steps" in _v[0]:
            SOPS += _v
DOA_IDS = {d[0] for d in DOA}
DEC_IDS = {d[0] for d in DEC}
CTL_IDS = {c[0] for c in CONTROLS}
MET_IDS = {m[0] for m in METRICS}
POL_IDS = {p["id"] for p in POLICIES}
SOP_IDS = {s["id"] for s in SOPS}
FRM_IDS = {f[0] for f in FORMS}
REG_IDS = {r[0] for r in REGISTERS}

fail, warn = [], []

# 1) كل نقطة اعتماد في كل إجراء تشير إلى سطر DOA أو DEC موجود
for s in SOPS:
    for what, who, ref in s["approvals"]:
        if ref in ("—", ""):
            continue
        for part in re.findall(r"(DOA-\d+|DEC-\d+|DOA-\d+(?:/\d+)*)", ref):
            pass
        base = ref.split("/")[0].strip()
        nums = re.findall(r"(DOA|DEC)-(\d+)", ref)
        prefix = base.split("-")[0]
        # يتعامل مع صيغة DOA-08/09/10
        m = re.match(r"(DOA|DEC)-(\d+)((?:/\d+)*)", ref)
        if not m:
            if not ref.startswith(("DOA", "DEC")):
                warn.append(f"{s['id']}: نقطة اعتماد بلا سطر صلاحية: «{what}» → {ref}")
            continue
        pre = m.group(1)
        ids = [m.group(2)] + [x for x in m.group(3).split("/") if x]
        for i in ids:
            oid = f"{pre}-{i.zfill(2)}"
            pool = DOA_IDS if pre == "DOA" else DEC_IDS
            if oid not in pool:
                fail.append(f"{s['id']}: سطر صلاحية غير موجود: {oid}")

# 2) كل ضابط مذكور في إجراء له تعريف
for s in SOPS:
    for c in s["controls"]:
        if c not in CTL_IDS:
            fail.append(f"{s['id']}: ضابط غير معرَّف: {c}")
    for a, act, sysm, sla, c in s["steps"]:
        if c and c not in CTL_IDS:
            fail.append(f"{s['id']}: ضابط في خطوة غير معرَّف: {c}")
    for k in s["kpis"]:
        if k not in MET_IDS:
            fail.append(f"{s['id']}: مؤشر غير معرَّف: {k}")
    if s["policy"] not in POL_IDS:
        fail.append(f"{s['id']}: سياسة أُم غير معرَّفة: {s['policy']}")
    for f in s["forms"]:
        fid = f.split()[0]
        if fid not in FRM_IDS:
            warn.append(f"{s['id']}: نموذج غير معرَّف: {fid}")
    for r in s["registers"]:
        rid = r.split()[0]
        if rid not in REG_IDS:
            warn.append(f"{s['id']}: سجل غير معرَّف: {rid}")

# 3) كل سياسة تشير إلى إجراءات وضوابط موجودة
for p in POLICIES:
    for c in p["controls"]:
        if c not in CTL_IDS:
            fail.append(f"{p['id']}: ضابط غير معرَّف: {c}")
    for sp in p["sops"]:
        if sp not in SOP_IDS:
            fail.append(f"{p['id']}: إجراء غير معرَّف: {sp}")

# 4) كل خطر مرتبط بضابط ومؤشر موجودين
for r in RISKS:
    for c in r[6]:
        if c not in CTL_IDS:
            fail.append(f"{r[0]}: ضابط غير معرَّف: {c}")
    if r[7] not in MET_IDS:
        fail.append(f"{r[0]}: مؤشر غير معرَّف: {r[7]}")

# 5) كل ضابط له مالك وتكرار ودليل وطريقة اختبار غير فارغة
for c in CONTROLS:
    if not all(c[3:]):
        fail.append(f"{c[0]}: ضابط ناقص حقلاً إلزامياً")

# 6) كل مؤشر له معادلة وعتبة واستجابة
for m in METRICS:
    if not m[4] or not m[9]:
        fail.append(f"{m[0]}: مؤشر بلا معادلة أو بلا استجابة إلزامية")

# 7) كل إجراء له خطوات وبوابات ونقاط اعتماد وضوابط ودليل
for s in SOPS:
    if not s["steps"]:
        fail.append(f"{s['id']}: بلا خطوات")
    if not s["gates"]:
        warn.append(f"{s['id']}: بلا بوابات قرار")
    if not s["approvals"]:
        fail.append(f"{s['id']}: بلا نقطة اعتماد")
    if not s["controls"]:
        fail.append(f"{s['id']}: بلا ضابط")
    if not s["evidence"]:
        fail.append(f"{s['id']}: بلا دليل محفوظ")
    if not s["sla"]:
        fail.append(f"{s['id']}: بلا SLA")
    for field in ("exception", "reject", "escalation", "sod"):
        if not s[field]:
            fail.append(f"{s['id']}: بلا {field}")

# 8) كل ضابط مستخدم فعلياً في إجراء أو سياسة أو خطر (لا ضابط يتيم)
used = set()
for s in SOPS:
    used |= set(s["controls"])
    used |= {c for *_, c in s["steps"] if c}
for p in POLICIES:
    used |= set(p["controls"])
for r in RISKS:
    used |= set(r[6])
orphan = CTL_IDS - used
if orphan:
    warn.append(f"ضوابط غير مستخدمة في أي إجراء: {sorted(orphan)}")

# 9) لا يوجد سطر DOA بلا اعتماد نهائي
for d in DOA:
    if not d[6]:
        fail.append(f"{d[0]}: سطر صلاحية بلا اعتماد نهائي")

print("=" * 60)
print(f"إجراءات: {len(SOPS)} | سياسات: {len(POLICIES)} | صلاحيات: {len(DOA)} | ضوابط: {len(CONTROLS)} | مؤشرات: {len(METRICS)}")
print("=" * 60)
if fail:
    print(f"\n❌ إخفاقات ({len(fail)}):")
    for f in fail:
        print("  -", f)
if warn:
    print(f"\n⚠️  تنبيهات ({len(warn)}):")
    for w in warn:
        print("  -", w)
if not fail:
    print("\n✅ اجتاز التتبّع: كل نقطة اعتماد لها سطر صلاحية، وكل ضابط ومؤشر وسياسة مُشار إليهم معرَّفون.")
sys.exit(1 if fail else 0)
