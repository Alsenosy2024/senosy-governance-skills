# -*- coding: utf-8 -*-
"""السياسات — مكتوبة بالكامل. راجع references/policy-standard.md."""
FIELDS = ["id","title","family","dept","owner","approver","purpose","scope","definitions","rules",
          "roles","controls","exceptions","consequences","sops","standard","review","priority"]
def P(*a): return dict(zip(FIELDS, a))

POLICIES = [
 P("POL-01", "عنوان السياسة", "العائلة", "GOV", "المالك", "صاحب الاعتماد",
   "الغرض في جملة واحدة تشرح لماذا توجد.",
   "النطاق: على من ينطبق وعلى ماذا.",
   [("مصطلح", "تعريفه")],
   ["1. قاعدة إلزامية بصيغة أمر أو منع.", "2. قاعدة ثانية."],
   "الأدوار: من يفعل ماذا.",
   ["CTL-01"],
   "الاستثناءات: من يعتمدها ولمدة كم — أو «لا استثناء».",
   "عواقب المخالفة.",
   ["SOP-X01"], "المرجع المعياري", "سنوياً", "إلزامية"),
]
CONDITIONAL = []   # (id, السياسة, الحالة, المبرر)
