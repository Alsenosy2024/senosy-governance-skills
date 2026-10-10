# Contextual Deck Studio

استوديو محلي عربي لبناء عروض تدريبية من 50 إلى 200 شريحة من محاور البرنامج،
مع ثيمات سياقية، ملاحظات ميسّر، وملفات PowerPoint وDeckSpec وتقرير جودة.

## أسرع تشغيل على macOS

انقر مرتين على `launch-studio.command`. في أول تشغيل ينشئ بيئة Python محلية داخل
المجلد ويثبت المكتبات المطلوبة، ثم يفتح الواجهة على:

`http://127.0.0.1:8765`

أو شغّل يدويًا:

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/studio.py --open --data-dir ./studio-runs
```

## وضع AI

- **Codex CLI:** يعتمد على جلسة تسجيل الدخول المحلية ولا يحتاج مفتاحًا داخل الواجهة.
- **OpenAI-compatible / GLM / Kimi:** أدخل Base URL واسم النموذج واسم متغير البيئة.
- **Gemini / Claude:** أدخل اسم النموذج واسم متغير البيئة.
- **Custom command:** Adapter داخلي يقرأ JSON من stdin ويعيد DeckSpec JSON.

مثال لتعريف مفتاح قبل تشغيل الاستوديو:

```bash
export PROVIDER_API_KEY="ضع-القيمة-هنا"
./launch-studio.command
```

القيمة لا تمر إلى الواجهة ولا تحفظ في إعداد العرض؛ المحرك يقرأها مباشرة من البيئة.

## الملفات الناتجة

كل مهمة تحفظ في `studio-runs/<job-id>/`:

- `.pptx` العرض النهائي
- `.json` مخطط DeckSpec القابل للتعديل وإعادة التصيير
- `-qa.json` تقرير الجودة
- `.pdf` اختياري عند توفر LibreOffice

للتفاصيل التقنية راجع `SKILL.md` و`references/long-deck-studio.md`.
