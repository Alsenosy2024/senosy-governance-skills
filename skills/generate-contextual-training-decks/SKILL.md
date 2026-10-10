---
name: "generate-contextual-training-decks"
description: Generate varied, context-aware Arabic RTL training presentations from a brief or structured content using a provider-agnostic AI planning layer and a deterministic Python PowerPoint renderer. Use for building PPTX training materials, integrating automatic presentation generation into a platform, switching among Codex CLI authentication, OpenAI-compatible APIs, Gemini, Claude, GLM, Kimi, or custom model commands, and rendering or validating DeckSpec JSON without exposing provider credentials.
---

# توليد عروض تدريبية سياقية

حوّل brief إلى عقد `DeckSpec` موحّد، ثم صيّره محلياً إلى PPTX. افصل دائماً بين:

1. **التخطيط بالذكاء الاصطناعي:** كتابة المحتوى، هندسة التعلم، اختيار نوع كل شريحة، وملاحظات الميسّر.
2. **التصيير الحتمي:** تطبيق نظام التصميم، RTL، التخطيطات المتنوعة، الملاحظات، والترقيم.
3. **الجودة:** فحص المخطط والملف، ثم رندر PDF وفحص بصري عند توفر LibreOffice.

## ابدأ بعقد التدريب

حدّد الجمهور، المستوى، القطاع، المدة، ناتج الأداء، عدد الشرائح، اللغة، العلامة، ومواد المصدر. إذا غابت التفاصيل، اذكر افتراضاتك داخل brief. لا تبدأ من قائمة موضوعات فقط.

اقرأ [content-contract.md](references/content-contract.md) عند إعداد brief أو تعديل مخطط الشرائح. اقرأ [provider-integration.md](references/provider-integration.md) عند توصيل مزود أو دمج المحرّك في منصة. اقرأ [layout-catalog.md](references/layout-catalog.md) عند تخصيص منطق التنوع البصري.

للعروض الطويلة من 50 إلى 200 شريحة، استخدم الاستوديو المحلي واقرأ [long-deck-studio.md](references/long-deck-studio.md). قسّم التوليد إلى وحدات ولا تطلب عرضاً ضخماً في استدعاء AI واحد.

## اختر مسار التشغيل

### واجهة محلية للعروض الطويلة

```bash
python scripts/studio.py --open --data-dir ./studio-runs
```

أدخل المحاور وأوزانها، عاين توزيع الشرائح والثيمات، ثم اختر الوضع التجريبي أو مزود AI. يدعم الاستوديو 50–200 شريحة ومهام توليد في الخلفية وتنزيل PPTX وDeckSpec وتقرير QA.

### مخطط ومزود AI ثم PPTX

```bash
python scripts/generate_deck.py build \
  --brief brief.txt \
  --provider provider.json \
  --slides 30 \
  --spec-out deck.json \
  --out deck.pptx \
  --qa qa.json \
  --pdf-dir rendered
```

### تصيير مخطط موجود بلا استدعاء AI

```bash
python scripts/generate_deck.py render \
  --spec assets/example_deck.json \
  --out deck.pptx \
  --qa qa.json \
  --pdf-dir rendered
```

### إنشاء المخطط فقط

```bash
python scripts/generate_deck.py plan \
  --brief brief.txt \
  --provider provider.json \
  --slides 30 \
  --out deck.json
```

## بدّل المزود دون تغيير المحرّك

- استخدم `codex_cli` للاستفادة من تسجيل دخول Codex الموجود محلياً؛ لا تقرأ أو تنسخ رموز المصادقة.
- استخدم `openai_compatible` مع أي endpoint متوافق، بما فيه بوابات GLM وKimi والمزودات الخاصة.
- استخدم `gemini` أو `anthropic` للواجهات الأصلية.
- استخدم `command` لربط أي adapter داخلي يقرأ JSON من stdin ويكتب DeckSpec JSON إلى stdout.
- ضع اسم متغير البيئة في `api_key_env`، ولا تضع قيمة المفتاح في ملف الإعداد.

انسخ أحد أمثلة `assets/provider.*.example.json` وعدّل القيم العامة فقط. اختبر المخطط الناتج عبر Pydantic قبل التصيير.

## حافظ على تنوع يخدم المعنى

دع نوع المحتوى يحدد التخطيط: مفهوم، تسلسل، مقارنة، زمن، أرقام، حالة، نشاط، اختبار، أداة، أو خلاصة. لا تجبر كل شيء على بطاقات. يقاوم محدد التخطيط التكرار، لكن `layout_hint` يسمح بالتثبيت عند وجود سبب واضح.

استخدم نصاً ظاهراً موجزاً، وضع شرح الميسّر والمصادر في Notes. لا تخترع مصادر أو أرقاماً. لا تستخدم `metrics` إلا لأرقام أو مؤشرات ذات معنى.

## بوابات التسليم

1. شغّل `render` أو `build` مع `--qa`.
2. أصلح أخطاء الأنشطة بلا تعليمات، الاختبارات الناقصة، التباين، والشرائح الفارغة.
3. استخدم `--pdf-dir` ورندر الشرائح عندما يتوفر LibreOffice.
4. افحص بصرياً القص، الالتفاف، RTL، تسلسل التخطيطات، وكثافة النص.
5. سلّم PPTX وDeckSpec وQA report. سلّم إعداد المزود مثالاً بلا أسرار.
