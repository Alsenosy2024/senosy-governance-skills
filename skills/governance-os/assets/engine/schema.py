# -*- coding: utf-8 -*-
"""قالب الإجراء الموحّد. كل إجراء في النظام يلتزم بهذه الحقول بلا استثناء."""

FIELDS = ["id", "title", "dept", "owner", "approver", "policy", "trigger", "start", "end",
          "inputs", "outputs", "steps", "gates", "approvals", "controls", "sod",
          "evidence", "sla", "exception", "reject", "escalation", "kpis", "forms", "registers"]


def S(id, title, dept, owner, approver, policy, trigger, start, end,
      inputs, outputs, steps, gates, approvals, controls, sod,
      evidence, sla, exception, reject, escalation, kpis, forms, registers):
    """steps: [(الدور, الفعل, النظام, الزمن, معرّف الضابط)]
       gates: [(سؤال البوابة, مسار نعم, مسار لا)]
       approvals: [(ما يُعتمد, صاحب الاعتماد, سطر DOA)]"""
    return dict(zip(FIELDS, [id, title, dept, owner, approver, policy, trigger, start, end,
                             inputs, outputs, steps, gates, approvals, controls, sod,
                             evidence, sla, exception, reject, escalation, kpis, forms, registers]))
