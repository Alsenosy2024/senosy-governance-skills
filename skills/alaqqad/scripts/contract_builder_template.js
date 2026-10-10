/**
 * قالب العقّاد لبناء عقود Word عربية (RTL) — انسخ هذا الملف وعدّل:
 *   1) قسم DATA بالكامل ببيانات العقد الجديد.
 *   2) دوال art1..artN حسب هيكل المواد الفعلي (راجع reference/standard_articles.md).
 *   3) قسم BUILD DOCUMENT لترتيب المواد وفواصل الصفحات.
 *
 * تشغيل:
 *   npm list -g docx || npm install -g docx
 *   node contract_builder_template.js
 *   python3 /root/.claude/skills/docx/scripts/office/validate.py output.docx
 *
 * ⚠️ قاعدة حرجة: حدود الفقرات (pBdr) — لا تُعرّف أكثر من ضلع واحد بقيمة
 * NONE. مكتبة docx.js تفرض ترتيباً ثابتاً (top,bottom,left,right) يخالف
 * ترتيب مخطط OOXML (top,left,bottom,right) المستخدم في validate.py، فإذا
 * عرّفت كل الأضلاع الأربعة (حتى بقيمة NONE) سيفشل التحقق. عرّف فقط الضلع
 * الذي تريد إظهاره فعلياً وبس. حدود خلايا الجدول (tcBorders) لا تعاني من
 * هذه المشكلة ويمكن تعريف الأضلاع الأربعة بأمان.
 */
const {
  Document, Packer, Paragraph, TextRun,
  AlignmentType, BorderStyle, ShadingType, WidthType,
  Table, TableRow, TableCell, VerticalAlign,
  Header, Footer, PageBreak,
} = require('docx');
const fs = require('fs');

// ── COLORS — عدّل حسب براند العميل إن اقتضى الأمر ───────────
const NAVY  = "1A3557";
const GOLD  = "C8912A";
const CYAN  = "0E9EBB";
const WHITE = "FFFFFF";
const LIGHT = "F0F5FA";
const GREY  = "6B7280";
const BLACK = "111827";

const AR_FONT = "Cairo";   // أو Tajawal
const EN_FONT = "Calibri";

const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1134; // A4, هامش ~2سم
const CONTENT_W = PAGE_W - MARGIN * 2; // عرض المحتوى الصافي بوحدة DXA

// ── HELPERS ────────────────────────────────────────────────
function ar(text, opts = {}) {
  return new TextRun({
    text, font: { name: AR_FONT }, color: opts.color || BLACK,
    size: opts.size || 22, bold: opts.bold || false, italics: opts.italics || false,
    rightToLeft: true,
  });
}
function en(text, opts = {}) {
  return new TextRun({
    text, font: { name: EN_FONT }, color: opts.color || BLACK,
    size: opts.size || 20, bold: opts.bold || false, italics: opts.italics || false,
  });
}
function rtlPara({ children, spacing, alignment, shading, border, indent }) {
  return new Paragraph({
    bidirectional: true,
    alignment: alignment || AlignmentType.RIGHT,
    spacing: spacing || { before: 0, after: 160 },
    shading: shading || undefined,
    border: border || undefined,
    indent: indent || undefined,
    children,
  });
}
function spacer(after = 120) {
  return new Paragraph({ spacing: { before: 0, after }, children: [] });
}
function divider(color = GOLD) {
  return new Paragraph({
    bidirectional: true,
    spacing: { before: 60, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color, space: 1 } }, // ضلع واحد فقط — آمن
    children: [],
  });
}
// عنوان مادة رئيسية — "المادة (n) — العنوان"
function articleHeading(num, title) {
  return new Paragraph({
    bidirectional: true,
    alignment: AlignmentType.RIGHT,
    spacing: { before: 320, after: 40 },
    shading: { fill: LIGHT, type: ShadingType.CLEAR },
    border: { right: { style: BorderStyle.SINGLE, size: 24, color: GOLD, space: 8 } }, // ضلع واحد فقط — آمن
    indent: { right: 20 },
    children: [
      ar(`المادة (${num})  —  `, { color: GOLD, bold: true, size: 24 }),
      ar(title, { color: NAVY, bold: true, size: 24 }),
    ],
  });
}
function p(text, opts = {}) {
  return rtlPara({
    spacing: { before: 0, after: opts.after ?? 140 },
    children: [ar(text, { size: opts.size || 22, bold: opts.bold || false, color: opts.color })],
  });
}
// بند مرقم فرعي: 1. نص
function numItem(n, text, opts = {}) {
  return rtlPara({
    spacing: { before: 0, after: opts.after ?? 110 },
    indent: { right: 320, hanging: 320 },
    children: [ar(`${n}.  `, { color: GOLD, bold: true, size: 22 }), ar(text, { size: 22 })],
  });
}
// نقطة قائمة (شرطة)
function bullet(text, opts = {}) {
  return rtlPara({
    spacing: { before: 0, after: opts.after ?? 100 },
    indent: { right: 300, hanging: 260 },
    children: [ar("–  ", { color: CYAN, bold: true, size: 22 }), ar(text, { size: 22 })],
  });
}
function subheading(text) {
  return rtlPara({ spacing: { before: 160, after: 90 }, children: [ar(text, { color: CYAN, bold: true, size: 23 })] });
}

// خلية جدول عربية — الأضلاع الأربعة آمنة هنا (tcBorders)
function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width, type: WidthType.DXA },
    shading: { fill: opts.fill || WHITE, type: ShadingType.CLEAR },
    margins: { top: 110, bottom: 110, left: 150, right: 150 },
    verticalAlign: VerticalAlign.CENTER,
    columnSpan: opts.colSpan || undefined,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
      left: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
      right: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
    },
    children: [
      new Paragraph({
        bidirectional: true,
        alignment: opts.align || AlignmentType.RIGHT,
        spacing: { before: 0, after: 0 },
        children: [new TextRun({
          text, font: { name: AR_FONT }, color: opts.color || BLACK,
          size: opts.size || 20, bold: opts.bold || false, rightToLeft: true,
        })],
      }),
    ],
  });
}
function headerRowCell(text, width) {
  return cell(text, { width, fill: NAVY, color: WHITE, bold: true, size: 20, align: AlignmentType.CENTER });
}

// جدول بيانات طرف — تسمية | قيمة (تسمية على اليمين — الأعمدة الضيقة أولاً)
function partyTable(rows) {
  const w1 = 2400, w2 = CONTENT_W - 2400;
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [w1, w2],
    visuallyRightToLeft: true, // إلزامي لكل جدول RTL — يجعل أول عنصر بالمصفوفة يظهر يميناً
    rows: rows.map(r => new TableRow({
      children: [
        cell(r.value, { width: w2, align: AlignmentType.RIGHT, size: 20 }),
        cell(r.label, { width: w1, fill: LIGHT, bold: true, color: NAVY, size: 20 }),
      ],
    })),
  });
}

// جدول بنود مالية (BOQ) لمرحلة واحدة — items: [{desc, unit, price, total}]
function boqTable(items, subtotalLabel, subtotal) {
  const wDesc = 5400, wUnit = 1200, wPrice = 1500, wTotal = CONTENT_W - 5400 - 1200 - 1500;
  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      headerRowCell("البند والوصف", wDesc),
      headerRowCell("الوحدة", wUnit),
      headerRowCell("سعر الوحدة (ر.س)", wPrice),
      headerRowCell("الإجمالي (ر.س)", wTotal),
    ],
  });
  const itemRows = items.map(it => new TableRow({
    children: [
      cell(it.desc, { width: wDesc, size: 19 }),
      cell(it.unit, { width: wUnit, align: AlignmentType.CENTER, size: 19 }),
      cell(it.price.toLocaleString('en-US'), { width: wPrice, align: AlignmentType.CENTER, size: 19 }),
      cell(it.total.toLocaleString('en-US'), { width: wTotal, align: AlignmentType.CENTER, size: 19, bold: true }),
    ],
  }));
  const subtotalRow = new TableRow({
    children: [
      cell(subtotalLabel, { width: wDesc + wUnit + wPrice, fill: LIGHT, bold: true, color: NAVY, align: AlignmentType.RIGHT, colSpan: 3 }),
      cell(subtotal.toLocaleString('en-US') + " ر.س", { width: wTotal, fill: GOLD, bold: true, color: WHITE, align: AlignmentType.CENTER }),
    ],
  });
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [wDesc, wUnit, wPrice, wTotal],
    visuallyRightToLeft: true,
    rows: [headerRow, ...itemRows, subtotalRow],
  });
}

// جدول دفعات — rows: [{label, cond, pct, amount}]
function paymentTable(rows, totalAmount) {
  const wLabel = 2400, wCond = 4238, wPct = 1000, wAmt = CONTENT_W - 2400 - 4238 - 1000;
  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      headerRowCell("الدفعة", wLabel), headerRowCell("شرط الاستحقاق", wCond),
      headerRowCell("النسبة", wPct), headerRowCell("المبلغ (ر.س)", wAmt),
    ],
  });
  const dataRows = rows.map(r => new TableRow({
    children: [
      cell(r.label, { width: wLabel, bold: true, color: NAVY, size: 19 }),
      cell(r.cond, { width: wCond, size: 18 }),
      cell(r.pct, { width: wPct, align: AlignmentType.CENTER, size: 19 }),
      cell(r.amount.toLocaleString('en-US'), { width: wAmt, align: AlignmentType.CENTER, size: 19, bold: true }),
    ],
  }));
  const totalRow = new TableRow({
    children: [
      cell("الإجمالي — رسوم التنفيذ الكاملة (غير شامل ضريبة القيمة المضافة)", { width: wLabel + wCond, fill: NAVY, color: WHITE, bold: true, align: AlignmentType.RIGHT, colSpan: 2, size: 19 }),
      cell("100%", { width: wPct, fill: NAVY, color: WHITE, bold: true, align: AlignmentType.CENTER, size: 19 }),
      cell(totalAmount.toLocaleString('en-US'), { width: wAmt, fill: GOLD, color: WHITE, bold: true, align: AlignmentType.CENTER, size: 19 }),
    ],
  });
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [wLabel, wCond, wPct, wAmt],
    visuallyRightToLeft: true,
    rows: [headerRow, ...dataRows, totalRow],
  });
}

// جدول ملخص القيمة الإجمالية (رسوم + ضريبة + إجمالي)
function totalsTable(rows) {
  const w1 = CONTENT_W - 2600, w2 = 2600;
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [w1, w2],
    visuallyRightToLeft: true,
    rows: rows.map(r => new TableRow({
      children: [
        cell(r.value, { width: w2, align: AlignmentType.CENTER, bold: true, color: r.highlight ? WHITE : NAVY, fill: r.highlight ? GOLD : LIGHT, size: 21 }),
        cell(r.label, { width: w1, align: AlignmentType.RIGHT, bold: true, color: r.highlight ? WHITE : BLACK, fill: r.highlight ? GOLD : WHITE, size: 20 }),
      ],
    })),
  });
}

// جدول توقيعات ثنائي الأعمدة
function signatureTable(colA, colB) {
  // colA/colB: مصفوفة نصوص بنفس الطول — الصف الأول عادة "الطرف الثاني" ثم "الطرف الأول"
  // (بحكم visuallyRightToLeft: العنصر الأول بالمصفوفة يظهر يميناً)
  const wSig = Math.floor(CONTENT_W / 2);
  const sigCell = (text, opts = {}) => cell(text, { width: wSig, align: AlignmentType.CENTER, ...opts });
  const rows = colA.map((text, i) => new TableRow({ children: [sigCell(text, colA.meta?.[i] || {}), sigCell(colB[i], colB.meta?.[i] || {})] }));
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [wSig, wSig], visuallyRightToLeft: true, rows });
}

// ── HEADER / FOOTER ────────────────────────────────────────
function buildHeaderFooter({ enTitle, arTitle, contactLine }) {
  const headerPara = new Paragraph({
    bidirectional: true, alignment: AlignmentType.RIGHT, spacing: { before: 0, after: 0 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: GOLD, space: 4 } }, // ضلع واحد فقط
    children: [en(enTitle, { color: NAVY, size: 16 }), en("    |    ", { color: GOLD, size: 16 }), ar(arTitle, { color: NAVY, size: 16 })],
  });
  const footerPara = new Paragraph({
    bidirectional: true, alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0 },
    border: { top: { style: BorderStyle.SINGLE, size: 4, color: CYAN, space: 4 } }, // ضلع واحد فقط
    children: [en(contactLine, { color: GREY, size: 15 })],
  });
  return { headerPara, footerPara };
}

// ═══════════════════════════════════════════════════════════
// ── DATA — TODO: عدّل كل ما يلي ببيانات العقد الجديد ────────
// ═══════════════════════════════════════════════════════════
const CONTRACT_NO = "XXX-YYY-2026-001";
const ISSUE_DATE = "TODO — شهر وسنة الإصدار";

const partyOneRows = [
  { label: "اسم الشركة", value: "TODO" },
  // ... باقي الحقول (السجل التجاري/الرقم الوطني، الرقم الضريبي، العنوان، التواصل، الممثل القانوني)
];
const partyTwoRows = [
  { label: "اسم الشركة", value: "TODO" },
];

// أمثلة بيانات BOQ ودفعات — استبدلها ببيانات العقد الفعلي من العرض الفني والمالي
const phase1Items = [
  { desc: "TODO", unit: "خدمة", price: 0, total: 0 },
];
const paymentRows = [
  { label: "الدفعة الأولى", cond: "TODO", pct: "0%", amount: 0 },
];

console.log("عدّل قسم DATA ثم أضف مواد العقد (articleHeading + numItem/bullet/p/الجداول) وفق reference/standard_articles.md، ثم اجمعها في body وابنِ Document كما في مثال المهارة arabic-docx.");
