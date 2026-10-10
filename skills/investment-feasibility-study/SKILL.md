---
name: "investment-feasibility-study"
description: Build comprehensive, final investor-grade feasibility studies for new ventures, expansions, locations, franchises, and capital investments. Use when the user needs a complete, deep-researched, source-backed investment decision document with market, technical, operational, legal, financial, risk, and implementation diligence; CAPEX/OPEX, break-even, NPV and IRR; and a defensible GO/CONDITIONAL GO/NO-GO recommendation. Do not substitute a preliminary screen for a final study.
---

# Investment Feasibility Study

Build a final investment decision document, not a generic business plan or a preliminary screen. Start with the investment decision and work backward to the evidence required to support or reject it.

## Non-negotiable rules

- Research current, primary sources before writing material market, regulation, tax, grant, price, or competitor claims. Browse whenever the information may have changed.
- Separate every input into `Verified`, `Derived`, `Consultant assumption`, or `Missing`. Never present an assumption as market fact.
- Cite each material claim with organisation, publication date when available, direct link, and what it supports.
- Do not use top-down market share as the main revenue forecast. Use operating drivers: capacity, conversion, utilisation, price, orders, contracts, production, or units.
- Use ranges where quotations or reliable local pricing are unavailable. Do not invent precise costs, live ratings, wages, rents, competitors, regulations, or licenses.
- Reconcile every financial table. If the model does not reconcile, stop and fix it before recommending investment.
- Never call a desk-research-only output “final” or “bankable”. A final study requires site evidence, quotations, legal/tax verification, and validated demand. When a required proof is missing, issue a clearly marked `Finalisation Blocker`, not a fabricated conclusion.

## 1. Set the decision frame

Collect or infer only what is needed to start. Ask for the smallest missing items that materially change the result:

- project, product/service, geography, target customer, ownership and launch date;
- site/scale/capacity, operating model, price or revenue logic;
- investment limit, funding structure, and decision threshold;
- available quotations, sales history, customer evidence, lease terms, or prior studies.

For a material unknown such as country, sector, project scale, site, or funding structure, ask one concise question before research. Build an evidence-request list and keep working on the parts that can be proven, but do not issue the final investment verdict until all finalisation blockers are closed.

Create an `Assumptions Register` from the first page. Give every item a basis, confidence (high/medium/low), owner, validation action, and financial impact.

## 2. Plan and execute deep research

Use the following order. Read [research-and-evidence.md](references/research-and-evidence.md) before research.

1. Define 10-15 research questions that could change the investment decision and map each to a required proof.
2. Start with official statistics, regulators, tax authorities, municipalities, investment agencies, company filings, and primary company sources.
3. Add reputable industry research for market structure or trend context. Treat estimates from paid research providers as directional unless methodology is available.
4. Verify competitor/location observations using official brand pages, maps, platforms, menus, field checks, or user-provided evidence. Timestamp dynamic data.
5. Record source, claim, date, geography, limitations, and confidence in a `Source Log`.
6. For every critical claim, use one authoritative primary source or two independent strong sources. Cross-check conflicting values and explain the chosen input.
7. Require first-party validation for demand, site, cost, and operating feasibility: customer interviews/pilot data or equivalent demand evidence; site inspection/traffic observation where relevant; three comparable quotations for major CAPEX and recurring costs; and local legal/tax verification.
8. Read [final-study-acceptance.md](references/final-study-acceptance.md) before issuing the recommendation. Do not close a gap with an assumption.

For a country-specific project, prioritise local government and statutory sources. For Saudi Arabia, normally include the relevant GASTAT, ministry/municipality, business centre, tax authority, labour, investment, and sector regulator sources.

## 3. Build the comprehensive commercial and operating case

Cover only sections relevant to the sector, but do not omit a decision-critical one:

1. Executive summary, investment thesis, and decision requirements
2. Project definition, value proposition, business model, ownership, and funding plan
3. TAM/SAM/SOM where meaningful; demand, pricing, customers, and jobs-to-be-done
4. Location/channel/catchment analysis, including field observations where applicable
5. Competitor benchmark, price architecture, and defensible white space
6. Technical feasibility: site, capacity, design, process, equipment, utilities, suppliers, quality, and technology
7. Operating model: organisation, labour, procurement, controls, service levels, and launch ramp
8. Legal, tax, licensing, insurance, contracts, labour, data, and ESG constraints
9. Risk register, mitigations, implementation critical path, governance, and KPI dashboard

Use sector-specific operating drivers. Examples: seats and turns for restaurants; occupied keys/ADR for hotels; units and yield for manufacturing; leads/conversion/retention for digital services; lease-up and occupancy for real estate.

## 4. Build and audit the financial model

Read [financial-model-integrity.md](references/financial-model-integrity.md) before creating the model.

Build in this order:

1. CAPEX, pre-opening costs, deposits, contingencies, and working capital.
2. Bottom-up revenue by channel and period.
3. Variable, fixed, and semi-variable OPEX.
4. Five-year income statement, cash flow, and funding need.
5. Break-even and unit economics.
6. NPV, IRR, payback, discounted payback, ROI, and profitability index when applicable.
7. Conservative/base/optimistic cases plus sensitivity of the 3-5 main drivers.

State price basis (with/without tax), currency, forecast start date, calendar/operating days, inflation, tax/zakat, depreciation, discount rate, debt assumptions, and terminal/residual value. Use formulas, not opaque outputs.

## 5. Final-study quality gates

Before delivery, run all gates:

- Evidence: material claims are sourced or labeled assumptions.
- Completeness: every decision-critical data requirement in the acceptance checklist is verified or remains an explicit blocker; no `final` label while a blocker is open.
- Arithmetic: revenue → COGS → gross profit → EBITDA → EBIT → profit; opening cash + inflows - outflows = closing cash; cumulative cash flow and payback agree.
- Logic: capacity and utilisation can produce the revenue forecast; market evidence supports price/volume; recommended scale fits funding and ramp-up.
- Risk: a -20% revenue case, severe cost case, launch delay, and funding stress case are shown; critical risks have owners, triggers, and mitigations.
- Independent review: recheck all formulas, links, source dates, units, tax basis, and scenario logic before delivery.
- Recommendation: `GO`, `CONDITIONAL GO`, or `NO-GO` follows the evidence. `CONDITIONAL GO` names the exact condition, owner, evidence due, and stop rule.

If creating a spreadsheet, use the `spreadsheets` skill and verify formulas. If creating a polished report, use the `doc` or `documents` skill and render-check the deliverable.

## Default deliverable

Use professional Arabic unless the user asks otherwise. Deliver a complete 30-50 page report plus a linked spreadsheet model where requested. Begin with a short decision page, then provide analysis, tables, assumptions, and sources. Include:

```md
# دراسة جدوى: [المشروع]

## قرار الاستثمار
[GO / CONDITIONAL GO / NO-GO + why, constraints, and critical conditions]

## الملخص التنفيذي

## نطاق الدراسة وسجل الافتراضات

## السوق والعملاء والمنافسة

## الجدوى الفنية والتشغيلية والنظامية

## النموذج المالي
[CAPEX, OPEX, revenue, P&L, cash flow, break-even, investment appraisal]

## المخاطر والحساسية والسيناريوهات

## خطة التنفيذ وKPIs

## المصادر وسجل الأدلة

## ملاحق الإثبات
[عروض الأسعار، الموقع، قوائم المنافسين، مقابلات العملاء، الحسابات، وتدقيق الجودة]
```

For each financial conclusion, provide a compact trace: formula, input labels, and scenario. Finish with the minimum validations required before money is committed.

## Completion status

- `Final Investment Study`: default. Requires every applicable acceptance gate to pass and contains a final verdict.
- `Finalisation Blocked`: use only when required evidence is unavailable. Deliver the completed research and model, list the exact blockers, and do not give a false final verdict.

## Handoff

After a blocked study, offer one next step: close the smallest decision-critical blocker using the named evidence owner and acceptance test.
