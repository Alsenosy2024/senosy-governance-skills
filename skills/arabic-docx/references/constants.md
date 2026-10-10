# Constants & Helper Functions — ثوابت ودوال المساعدة

## ألوان البراند الافتراضية

```javascript
// ── COLORS ─────────────────────────────────────────────────
const NAVY   = "1A3557";   // أزرق داكن — اللون الرئيسي
const GOLD   = "C8912A";   // ذهبي — لون التمييز
const CYAN   = "0E9EBB";   // سماوي — لون ثانوي
const WHITE  = "FFFFFF";   // أبيض
const LIGHT  = "F0F5FA";   // أزرق فاتح جداً — خلفيات
const GREY   = "6B7280";   // رمادي — نصوص ثانوية
const BLACK  = "111827";   // أسود داكن — النص الأساسي
```

**ألوان بديلة للبراند:**

| النمط | Primary | Accent | Background |
|-------|---------|--------|------------|
| Professional Navy | 1A3557 | C8912A | F0F5FA |
| Royal Green | 1B4332 | D4A017 | F0F7F4 |
| Burgundy | 7B2D3E | C8912A | FDF6F7 |
| Corporate Dark | 1F2937 | 3B82F6 | F8FAFC |

---

## الفونتات

```javascript
const AR_FONT = "Cairo";     // عربي أنيق — الخيار الأول
// const AR_FONT = "Tajawal"; // بديل أنيق
// const AR_FONT = "Noto Naskh Arabic"; // للنصوص الرسمية
const EN_FONT = "Calibri";   // إنجليزي — يتناسق مع Cairo
// const EN_FONT = "Gill Sans MT"; // بديل أكثر أناقة
```

> **ملاحظة:** Cairo وTajawal فونتات Google وتعمل في Word بدون تثبيت مسبق — Word يعرضها تلقائياً إذا كان الجهاز متصلاً بالإنترنت. للضمان الكامل دون إنترنت، استخدم "Arabic Typesetting" أو "Traditional Arabic".

---

## Imports الكاملة

```javascript
const {
  Document, Packer, Paragraph, TextRun,
  AlignmentType, BorderStyle, ShadingType, WidthType,
  Table, TableRow, TableCell, VerticalAlign,
  Header, Footer, LevelFormat, HeadingLevel
} = require('docx');
const fs = require('fs');
```

---

## دوال المساعدة الأساسية

### ar() — نص عربي

```javascript
function ar(text, opts = {}) {
  return new TextRun({
    text,
    font: { name: AR_FONT },
    color: opts.color || BLACK,
    size: opts.size || 24,          // 12pt افتراضي
    bold: opts.bold || false,
    italics: opts.italics || false,
    rightToLeft: true,              // ← إلزامي دائماً
  });
}
```

### en() — نص إنجليزي داخل فقرة عربية

```javascript
function en(text, opts = {}) {
  return new TextRun({
    text,
    font: { name: EN_FONT },
    color: opts.color || BLACK,
    size: opts.size || 22,
    bold: opts.bold || false,
    italics: opts.italics || false,
    // لا تضع rightToLeft هنا
  });
}
```

### rtlPara() — فقرة عربية عامة

```javascript
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
```

### divider() — خط فاصل أفقي

```javascript
function divider(color = GOLD) {
  return new Paragraph({
    bidirectional: true,
    spacing: { before: 80, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color, space: 1 } },
    children: [],
  });
}
```

### spacer() — مسافة فارغة

```javascript
function spacer(after = 120) {
  return new Paragraph({ spacing: { before: 0, after }, children: [] });
}
```

---

## إعداد الـ Styles

```javascript
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: AR_FONT, size: 24, color: BLACK } },
    },
  },
  sections: [{ ... }]
});
```
