---
name: arabic-docx
description: >
  إنشاء وتنسيق ملفات Word (.docx) باللغة العربية بشكل احترافي مع دعم كامل للاتجاه من اليمين لليسار (RTL).
  استخدم هذه المهارة دائماً عند طلب: إنشاء مستند Word عربي، تقرير عربي، مقال، خطاب، عرض تقديمي نصي،
  أي وثيقة بالعربية أو ثنائية اللغة (عربي/إنجليزي)، أو أي ملف .docx يحتوي على نص عربي.
  تشمل المهارة: فونتات Cairo وTajawal، ألوان براند احترافية، هيدر وفوتر، صناديق إحصائيات،
  Pull Quotes، جداول RTL، وعناوين وأقسام منسقة بالكامل.
  يجب تفعيل هذه المهارة حتى لو لم يُذكر "مهارة" أو "SKILL" صراحةً — فقط إذا كان المطلوب وثيقة Word عربية.
---

# Arabic DOCX Skill — مهارة إنشاء ملفات Word العربية

## نظرة عامة

هذه المهارة تُمكّن إنشاء ملفات Word (.docx) عربية أو ثنائية اللغة بجودة احترافية عالية،
مع دعم كامل لـ RTL، فونتات عربية أنيقة، وتصميم بصري متكامل.

**التبعيات المطلوبة:**
- Node.js + حزمة `docx` (npm install -g docx)
- التحقق: `npm list -g docx`

---

## الخطوات الأساسية

### 1. تحديد متطلبات المستند

قبل الكتابة، حدد:
- نوع المستند (مقال، تقرير، خطاب، عقد، أجندة تدريب...)
- اللغة (عربي فقط / ثنائية / إنجليزي مع عربي)
- ألوان البراند (افتراضي: Navy + Gold + Cyan)
- الفونت المطلوب (Cairo أو Tajawal — كلاهما يعمل بدون تثبيت)
- هل يحتاج: هيدر/فوتر، جداول، إحصائيات، CTA؟

### 2. الإعداد الأساسي — الثوابت والمساعدات

اقرأ ملف `references/constants.md` للحصول على:
- ثوابت الألوان والفونتات
- دوال المساعدة (ar، en، rtlPara، divider، spacer)
- إعدادات الصفحة A4 و RTL

### 3. بناء المستند

اقرأ ملف `references/components.md` للمكونات الجاهزة:
- غلاف العنوان (Cover Title Block)
- صناديق الإحصائيات (Stat Box Table)
- Pull Quote
- عناوين الأقسام (Section Headings)
- جدول المصادر
- CTA Box
- هيدر وفوتر

### 4. كتابة وتشغيل السكريبت

```bash
node article.js
```

### 5. التحقق من الملف

```bash
python scripts/office/validate.py output.docx
```

### 6. النقل للمخرجات

```bash
cp output.docx /mnt/user-data/outputs/
```

---

## قواعد حرجة — RTL في docx-js

```javascript
// كل فقرة عربية يجب أن تحتوي على:
new Paragraph({
  bidirectional: true,                    // ← إلزامي لكل فقرة عربية
  alignment: AlignmentType.RIGHT,         // ← محاذاة يمين
  children: [ ... ]
})

// كل TextRun عربي يجب أن يحتوي على:
new TextRun({
  text: "نص عربي",
  font: { name: "Cairo" },               // ← Cairo أو Tajawal
  rightToLeft: true,                     // ← إلزامي للنصوص العربية
  size: 24,                              // ← 24 = 12pt (مضاعفة في docx)
})
```

> **تحذير:** بدون `bidirectional: true` و `rightToLeft: true`، النص العربي يظهر معكوساً أو بترتيب خاطئ.

---

## قواعد حرجة — الجداول

```javascript
// الجداول تحتاج عرضاً مزدوجاً: على الجدول وعلى كل خلية
new Table({
  width: { size: 9026, type: WidthType.DXA },    // A4 بهامش 2cm
  columnWidths: [3008, 3009, 3009],               // مجموعها = 9026
  rows: [ new TableRow({ children: [
    new TableCell({
      width: { size: 3008, type: WidthType.DXA }, // ← نفس العرض على الخلية
      shading: { fill: "1A3557", type: ShadingType.CLEAR }, // CLEAR وليس SOLID
      margins: { top: 160, bottom: 160, left: 200, right: 200 },
      children: [ ... ]
    })
  ]}) ]
})
```

---

## قواعد حرجة — الفواصل والمسافات

```javascript
// لا تستخدم \n أبداً — استخدم Paragraph منفصلة
// ❌ خطأ
new TextRun({ text: "سطر أول\nسطر ثاني" })

// ✅ صحيح
new Paragraph({ children: [new TextRun({ text: "سطر أول" })] }),
new Paragraph({ children: [new TextRun({ text: "سطر ثاني" })] }),

// للمسافة الفارغة:
new Paragraph({ spacing: { before: 0, after: 200 }, children: [] })
```

---

## أحجام الفونت في docx-js

| المقاس المرئي | قيمة size |
|--------------|-----------|
| 10pt | 20 |
| 11pt | 22 |
| 12pt | 24 |
| 13pt | 26 |
| 14pt | 28 |
| 16pt | 32 |
| 20pt | 40 |
| 24pt | 48 |

---

## إعدادات الصفحة

```javascript
sections: [{
  properties: {
    page: {
      size: { width: 11906, height: 16838 },       // A4
      margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 }, // ~2cm
    },
  },
  headers: { default: new Header({ children: [headerPara] }) },
  footers: { default: new Footer({ children: [footerPara] }) },
  children: [ ... ]
}]
```

---

## الملفات المرجعية

| الملف | المحتوى |
|-------|---------|
| `references/constants.md` | ثوابت الألوان والفونتات ودوال المساعدة الكاملة |
| `references/components.md` | المكونات الجاهزة (Cover، Stats، Quote، CTA، Footer...) |
| `scripts/validate_arabic.sh` | سكريبت للتحقق السريع من الملف |

---

## مثال سريع — مستند بسيط

```javascript
const { Document, Packer, Paragraph, TextRun, AlignmentType } = require('docx');
const fs = require('fs');

const doc = new Document({
  sections: [{
    properties: {
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } }
    },
    children: [
      new Paragraph({
        bidirectional: true,
        alignment: AlignmentType.RIGHT,
        children: [
          new TextRun({ text: "مرحباً بالعالم", font: { name: "Cairo" }, size: 32, bold: true, rightToLeft: true, color: "1A3557" })
        ]
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buf => fs.writeFileSync('test.docx', buf));
```
