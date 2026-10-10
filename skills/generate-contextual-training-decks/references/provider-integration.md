# تكامل مزودي الذكاء الاصطناعي والمنصة

## المعمارية

```text
brief / source content
        ↓
AIProvider.generate_json(prompt, DeckSpec schema)
        ↓
Pydantic validation + normalized DeckSpec JSON
        ↓
deterministic layout selector + python-pptx renderer
        ↓
PPTX + Notes + QA JSON + optional rendered PDF
```

لا يمر مفتاح المزود إلى المصيّر. طبقة المزود وحدها تقرأ قيمة متغير البيئة وقت التشغيل، ولا تطبعها.

## Codex CLI authentication

استخدم هذا الخيار عندما تكون آلة التشغيل مسجلة في Codex بالفعل:

```json
{
  "provider": "codex_cli",
  "model": "",
  "timeout_seconds": 600,
  "max_retries": 0
}
```

يشغّل adapter الأمر `codex exec` في وضع مؤقت وقراءة فقط، ويمرر JSON Schema عبر `--output-schema`، ويقرأ الرسالة الأخيرة من ملف مؤقت. لا يقرأ ملفات المصادقة ولا يعيد استخدام token خارج Codex CLI.

## OpenAI-compatible APIs

استخدمه مع أي بوابة تدعم `POST /chat/completions`. يصلح عادةً لبوابات GLM وKimi والمزودات الداخلية، لكن اختبر توافق `response_format`; إذا رفضه endpoint يعيد adapter المحاولة من دون هذا الحقل ويعتمد على عقد JSON داخل prompt.

```json
{
  "provider": "openai_compatible",
  "model": "YOUR_MODEL_ID",
  "base_url": "https://YOUR_HOST/v1",
  "api_key_env": "YOUR_PROVIDER_API_KEY",
  "timeout_seconds": 240,
  "max_retries": 2,
  "extra_headers": {}
}
```

ضع المفتاح في البيئة وقت التشغيل، مثالاً:

```bash
export YOUR_PROVIDER_API_KEY="..."
```

لا تحفظ القيمة في JSON أو قاعدة بيانات إعدادات العرض.

## Gemini

```json
{
  "provider": "gemini",
  "model": "YOUR_GEMINI_MODEL",
  "base_url": "https://generativelanguage.googleapis.com",
  "api_key_env": "GEMINI_API_KEY",
  "timeout_seconds": 240,
  "max_retries": 2
}
```

يستخدم adapter `generateContent` مع `application/json`، ثم يتحقق من DeckSpec محلياً.

## Anthropic / Claude

```json
{
  "provider": "anthropic",
  "model": "YOUR_CLAUDE_MODEL",
  "base_url": "https://api.anthropic.com",
  "api_key_env": "ANTHROPIC_API_KEY",
  "timeout_seconds": 240,
  "max_retries": 2
}
```

## Command adapter

استخدمه للـSDK الداخلي، أو مصادقة cloud خاصة، أو gateway لا يشبه الواجهات السابقة:

```json
{
  "provider": "command",
  "command": ["/srv/training/bin/provider-adapter"],
  "timeout_seconds": 300
}
```

العقد مع الأمر:

- stdin: كائن JSON يحوي `prompt` و`schema`.
- stdout: كائن DeckSpec JSON فقط.
- stderr: لرسائل التشغيل الآمنة.
- exit code غير صفر: فشل واضح للمحرّك.

لا تستخدم shell string؛ مرر command كقائمة لتجنب مشاكل الاقتباس وتنفيذ نص غير مقصود.

## تكامل Backend

نفّذ التخطيط كـjob منفصل لأنه قد يستغرق وقتاً، واحفظ `deck.json` كنسخة قابلة للمراجعة. بعد اعتماد المحتوى، نفّذ التصيير محلياً. افصل حالات النظام:

1. `planning`
2. `spec_validation_failed`
3. `ready_for_review`
4. `rendering`
5. `qa_failed`
6. `completed`

احتفظ بنسخة إعداد عامة بلا أسرار، وسجّل اسم المزود والموديل وزمن الاستدعاء ومعرّف الطلب، لكن لا تسجل prompt إذا كان يحوي بيانات عميل حساسة إلا وفق سياسة المنصة.

## أخطاء متوقعة

| الخطأ | المعالجة |
| --- | --- |
| متغير المفتاح غير موجود | أوقف job برسالة اسم المتغير فقط |
| JSON غير صالح | احتفظ بالنص الخام في سجل محمي، ولا ترسله للمصيّر |
| Schema validation | اعرض الحقول المخالفة وأعد التخطيط |
| 429 أو 5xx | إعادة محدودة مع backoff |
| timeout | job قابل لإعادة المحاولة دون تكرار التصيير المكتمل |
| تخطيط كثيف | QA warning ثم مراجعة أو إعادة تخطيط |

