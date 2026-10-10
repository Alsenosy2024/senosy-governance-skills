# Components — المكونات الجاهزة

## 1. غلاف العنوان (Cover Title Block)

```javascript
// الجزء الأزرق العلوي
new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.CENTER,
  shading: { fill: NAVY, type: ShadingType.CLEAR },
  children: [
    new TextRun({
      text: "عنوان المستند الرئيسي",
      font: { name: AR_FONT }, color: WHITE,
      size: 52, bold: true, rightToLeft: true,
    }),
  ],
}),

// الشريط الذهبي
new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.CENTER,
  shading: { fill: GOLD, type: ShadingType.CLEAR },
  children: [
    new TextRun({
      text: "العنوان الفرعي",
      font: { name: AR_FONT }, color: WHITE,
      size: 30, bold: true, rightToLeft: true,
    }),
  ],
}),
```

---

## 2. صندوق الإحصائيات (Stat Box)

```javascript
// stats = [{ num: "95%", label: "توصيف الرقم" }, ...]
function statTable(stats) {
  const cellW = Math.floor(9026 / stats.length);
  return new Table({
    width: { size: 9026, type: WidthType.DXA },
    columnWidths: stats.map(() => cellW),
    rows: [
      new TableRow({
        children: stats.map(s =>
          new TableCell({
            width: { size: cellW, type: WidthType.DXA },
            shading: { fill: NAVY, type: ShadingType.CLEAR },
            margins: { top: 160, bottom: 160, left: 200, right: 200 },
            verticalAlign: VerticalAlign.CENTER,
            borders: {
              top:    { style: BorderStyle.NONE },
              bottom: { style: BorderStyle.NONE },
              left:   { style: BorderStyle.NONE },
              right:  { style: BorderStyle.NONE },
            },
            children: [
              new Paragraph({
                bidirectional: true,
                alignment: AlignmentType.CENTER,
                spacing: { before: 0, after: 60 },
                children: [
                  new TextRun({
                    text: s.num,
                    font: { name: EN_FONT }, color: GOLD,
                    size: 48, bold: true,
                  })
                ],
              }),
              new Paragraph({
                bidirectional: true,
                alignment: AlignmentType.CENTER,
                spacing: { before: 0, after: 0 },
                children: [
                  new TextRun({
                    text: s.label,
                    font: { name: AR_FONT }, color: WHITE,
                    size: 18, rightToLeft: true,
                  })
                ],
              }),
            ],
          })
        ),
      }),
    ],
  });
}

// الاستخدام:
statTable([
  { num: "95%",   label: "نسبة الرضا" },
  { num: "2030",  label: "رؤية المملكة" },
  { num: "500+",  label: "مشروع مُنجز" },
  { num: "16.9%", label: "معدل النمو" },
])
```

---

## 3. Pull Quote — اقتباس بارز

```javascript
function pullQuote(text) {
  return new Paragraph({
    bidirectional: true,
    alignment: AlignmentType.RIGHT,
    spacing: { before: 200, after: 200 },
    shading: { fill: LIGHT, type: ShadingType.CLEAR },
    border: {
      right: { style: BorderStyle.SINGLE, size: 24, color: GOLD, space: 10 },
    },
    indent: { right: 360 },
    children: [
      new TextRun({
        text,
        font: { name: AR_FONT }, color: NAVY,
        size: 26, bold: true, rightToLeft: true, italics: true,
      }),
    ],
  });
}
```

---

## 4. عنوان القسم (Section Heading)

```javascript
function sectionHeading(text, color = NAVY) {
  return new Paragraph({
    bidirectional: true,
    alignment: AlignmentType.RIGHT,
    spacing: { before: 280, after: 120 },
    children: [
      new TextRun({
        text,
        font: { name: AR_FONT }, color,
        size: 32, bold: true, rightToLeft: true,
      }),
    ],
  });
}
```

---

## 5. CTA Box — صندوق الدعوة للعمل

```javascript
// صف أعلى (خط علوي سماوي)
new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.CENTER,
  shading: { fill: LIGHT, type: ShadingType.CLEAR },
  border: {
    top:    { style: BorderStyle.SINGLE, size: 6, color: CYAN },
    bottom: { style: BorderStyle.NONE },
  },
  children: [
    new TextRun({ text: "عنوان الـ CTA", font: { name: AR_FONT }, color: NAVY, size: 26, bold: true, rightToLeft: true }),
  ],
}),
new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.CENTER,
  spacing: { before: 60, after: 60 },
  shading: { fill: LIGHT, type: ShadingType.CLEAR },
  children: [
    new TextRun({ text: "website.com  |  platform.com", font: { name: EN_FONT }, color: CYAN, size: 22, bold: true }),
  ],
}),
new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.CENTER,
  shading: { fill: LIGHT, type: ShadingType.CLEAR },
  border: {
    bottom: { style: BorderStyle.SINGLE, size: 6, color: CYAN },
  },
  children: [
    new TextRun({ text: "0500000000  |  0500000001", font: { name: EN_FONT }, color: GOLD, size: 24, bold: true }),
  ],
}),
```

---

## 6. هيدر Header

```javascript
const headerPara = new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.RIGHT,
  spacing: { before: 0, after: 0 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: GOLD, space: 4 } },
  children: [
    new TextRun({ text: "Company Name  |  website.com", font: { name: EN_FONT }, color: NAVY, size: 18 }),
    new TextRun({ text: "    |    ", font: { name: EN_FONT }, color: GOLD, size: 18 }),
    new TextRun({ text: "اسم الشخص أو الشركة بالعربي", font: { name: AR_FONT }, color: NAVY, size: 18, rightToLeft: true }),
  ],
});
// الاستخدام في القسم:
headers: { default: new Header({ children: [headerPara] }) },
```

---

## 7. فوتر Footer

```javascript
const footerPara = new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 0 },
  border: { top: { style: BorderStyle.SINGLE, size: 4, color: CYAN, space: 4 } },
  children: [
    new TextRun({ text: "website.com   |   0500000000   |   0500000001", font: { name: EN_FONT }, color: GREY, size: 16 }),
  ],
});
// الاستخدام في القسم:
footers: { default: new Footer({ children: [footerPara] }) },
```

---

## 8. صف المصادر (Source Row)

```javascript
function sourceRow(num, src) {
  return new Paragraph({
    bidirectional: true,
    alignment: AlignmentType.RIGHT,
    spacing: { before: 40, after: 40 },
    children: [
      new TextRun({ text: `${num}. `, font: { name: EN_FONT }, color: CYAN, size: 18, bold: true }),
      new TextRun({ text: src, font: { name: EN_FONT }, color: GREY, size: 18, italics: true }),
    ],
  });
}

// الاستخدام:
sourceRow(1, "PMI — PMBOK Guide 7th Edition, 2021"),
sourceRow(2, "Project.co — AI in Project Management Statistics, 2024"),
```

---

## 9. نقطة قائمة عربية (Bullet Point)

```javascript
// في تعريف الـ Document:
numbering: {
  config: [
    {
      reference: "arabic-bullets",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "●",
        alignment: AlignmentType.RIGHT,
        style: {
          paragraph: {
            indent: { right: 720, hanging: 360 },
            bidirectional: true,
          }
        }
      }]
    }
  ]
},

// الاستخدام:
new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.RIGHT,
  numbering: { reference: "arabic-bullets", level: 0 },
  children: [
    new TextRun({ text: "نقطة في القائمة", font: { name: AR_FONT }, size: 24, rightToLeft: true })
  ]
})
```

---

## 10. خلية جدول عربية (Table Cell — RTL)

```javascript
new TableCell({
  width: { size: CELL_WIDTH, type: WidthType.DXA },
  shading: { fill: LIGHT, type: ShadingType.CLEAR },
  margins: { top: 120, bottom: 120, left: 180, right: 180 },
  verticalAlign: VerticalAlign.CENTER,
  borders: {
    top:    { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
    bottom: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
    left:   { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
    right:  { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
  },
  children: [
    new Paragraph({
      bidirectional: true,
      alignment: AlignmentType.RIGHT,
      children: [
        new TextRun({ text: "محتوى الخلية", font: { name: AR_FONT }, size: 22, rightToLeft: true })
      ]
    })
  ]
})
```
