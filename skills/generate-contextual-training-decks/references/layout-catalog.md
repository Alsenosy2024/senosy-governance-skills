# كتالوج التخطيطات ومنطق الاختيار

## مبدأ التشغيل

نظام التصميم ثابت، لكن تركيب الشريحة يتغير بحسب العلاقة داخل المحتوى. محدد التخطيط يتتبع الاستخدام السابق ويقلل تكرار الـvariant نفسه. استخدم `layout_hint` فقط عندما يكون لديك سبب دلالي أو قالب عميل.

## التخطيطات

| النوع | variants |
| --- | --- |
| الغلاف | `cover-hero`, `cover-split` |
| فاصل وحدة | `section-number`, `section-band` |
| عبارة محورية | `statement-center`, `statement-sidebar` |
| مفهوم | `concept-cards`, `concept-split`, `concept-focus` |
| عملية | `process-horizontal`, `process-stair` |
| خط زمني | `timeline-ribbon`, `timeline-lanes` |
| مقارنة | `comparison-columns`, `comparison-balance` |
| مؤشرات | `metrics-grid`, `metrics-hero` |
| حالة | `case-decision`, `case-scenario` |
| نشاط | `activity-workshop`, `activity-canvas` |
| اختبار | `quiz-options` |
| أداة | `tool-canvas`, `tool-steps` |
| خلاصة | `summary-checklist`, `summary-commitment` |

## قواعد الكثافة

- البطاقات: 2-4 في المعتاد؛ لا تجعل العرض كله بطاقات.
- العمليات: 3-5 خطوات.
- الخط الزمني: 3-6 مراحل.
- المقارنة: 2-3 خيارات.
- المؤشرات: 1-6 عناصر، ويجب أن تكون ذات معنى.
- النشاط: 3-4 تعليمات ومخرج ظاهر.
- الاختبار: 3-4 اختيارات.

## التخصيص

عدّل الألوان والخطوط عبر `theme`. أضف variant جديداً عبر:

1. إضافة اسمه إلى `LayoutSelector.variants`.
2. إنشاء method باسم `_layout_<variant>` في `DeckRenderer`.
3. الحفاظ على الهيدر والفوتر والهوامش وNotes.
4. إضافة مثال في `assets/example_deck.json`.
5. تشغيل التصيير وQA والرندر البصري.

لإضافة صورة خارجية، ضع مسارها المحلي في `image_path` ثم أضف دعمها في variant المناسب. لا تجعل النص العربي صورة. `image_prompt` حقل تخطيط لطبقة وسائط اختيارية؛ المصيّر الحالي لا يستدعي مولد صور تلقائياً.

