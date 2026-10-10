---
name: gptimage2-pptx
description: >
  توليد عروض PowerPoint احترافية من gpt-image-2: كل شريحة = صورة كاملة مولودة بالذكاء الاصطناعي.
  استخدم هذه المهارة دائماً عند طلب: إنشاء بريزنتيشن بصور مولودة بالذكاء الاصطناعي،
  تحويل محتوى أو برومبتات إلى شرائح PowerPoint، توليد slides من gpt-image-2،
  إنشاء عرض تدريبي أو تسويقي بصور AI، أو أي طلب يجمع بين image generation وPowerPoint.
  المهارة تشمل: إرسال اللوجوهات مع المحتوى لـ gpt-image-2، حفظ الصور، بناء PPTX كـ ZIP خام.
---

# GPT-Image-2 → PowerPoint Skill

توليد عرض PowerPoint احترافي حيث **كل شريحة = صورة واحدة كاملة** مولودة بـ gpt-image-2.

---

## المبدأ الأساسي

- **لا overlay** — كل المحتوى (نص + لوجو + تصميم) داخل الصورة نفسها
- **لا text boxes** فوق الصورة في الـ PPTX
- **كل شريحة** = صورة JPG مستقلة محفوظة بـ index واضح
- **الـ PPTX** يُبنى كـ raw ZIP — أكثر موثوقية من python-pptx

---

## الخطوة 1: تحضير البرومبتات

لكل شريحة، ابنِ برومبت شامل يحتوي على:

```
Professional 16:9 PowerPoint slide. [background color].
[Logo placement]: Tornix logo top-left. [Badge]: TCP badge top-right.
TITLE (large bold Arabic right-aligned): [العنوان]
SUBTITLE (English): [السابتايتل]
CENTER VISUAL: [وصف الفيجوال]
BULLETS (Arabic right-aligned, [color] text):
◆ [نقطة 1]
◆ [نقطة 2]
FOOTER: [نص الفوتر] | Slide XX/YY
```

**قواعد البرومبت:**
- اذكر اللوجوهات صراحةً في كل برومبت (top-left / top-right)
- حدد الألوان بالـ hex أو الوصف الواضح
- اذكر رقم الشريحة في الفوتر
- اكتب النص العربي مباشرة في البرومبت — gpt-image-2 يتعامل معه

---

## الخطوة 2: استدعاء gpt-image-2 مع اللوجوهات

```python
import os, io, base64, time
from openai import OpenAI
from PIL import Image

client = OpenAI(api_key=API_KEY)
OUT = "/home/claude/final_slides"
os.makedirs(OUT, exist_ok=True)

def generate_slide(num, prompt, logo_path, badge_path, retry=3):
    path = f"{OUT}/slide_{num:02d}.jpg"
    if os.path.exists(path):
        print(f"  slide {num:02d} — skip (exists)")
        return path
    for attempt in range(retry):
        try:
            resp = client.images.edit(
                model="gpt-image-2",
                image=[open(logo_path, 'rb'), open(badge_path, 'rb')],
                prompt=prompt,
                size="1536x1024",   # 16:9 landscape
                quality="medium",
                n=1,
            )
            b64 = resp.data[0].b64_json
            img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
            img.save(path, "JPEG", quality=88, optimize=True)
            print(f"  slide {num:02d} — OK {img.size}")
            return path
        except Exception as e:
            print(f"  slide {num:02d} — attempt {attempt+1} error: {e}")
            if attempt < retry - 1:
                time.sleep(10)
    return None
```

**ملاحظة مهمة:** بعد كل شريحة انتظر `time.sleep(5)` لتجنب rate limiting.

**قواعد التوليد:**
- ولّد الشرائح على **دفعات صغيرة** (3-5 شرائح) لتجنب timeout
- السكريبت يتحقق من وجود الملف قبل التوليد — يمكن الاستئناف من حيث توقف
- حجم الصورة المثالي: `1536x1024` (16:9)
- quality: `medium` كافية للشرائح

---

## الخطوة 3: بناء PPTX كـ raw ZIP

**هذا هو الحل الأكثر موثوقية — لا تستخدم python-pptx لهذه الحالة.**

```python
import zipfile, os

def build_pptx_raw(slide_jpg_paths, output_path):
    W = 12192000  # 13.33 inches in EMU
    H = 6858000   # 7.5 inches in EMU
    N = len(slide_jpg_paths)

    def slide_xml(rid="rId2"):
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
      <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    <p:pic>
      <p:nvPicPr>
        <p:cNvPr id="2" name="img"/>
        <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>
        <p:nvPr/>
      </p:nvPicPr>
      <p:blipFill>
        <a:blip r:embed="{rid}"/>
        <a:stretch><a:fillRect/></a:stretch>
      </p:blipFill>
      <p:spPr>
        <a:xfrm><a:off x="0" y="0"/><a:ext cx="{W}" cy="{H}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      </p:spPr>
    </p:pic>
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClr/></p:clrMapOvr>
</p:sld>'''

    def slide_rels(img_num):
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image{img_num}.jpg"/>
</Relationships>'''

    slide_id_list = "\n    ".join(
        f'<p:sldId id="{256+i}" r:id="rId{i+1}"/>' for i in range(N)
    )
    prs_rels_entries = "\n  ".join(
        f'<Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i+1}.xml"/>'
        for i in range(N)
    )
    slide_ct = "\n  ".join(
        f'<Override PartName="/ppt/slides/slide{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(N)
    )

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="jpg" ContentType="image/jpeg"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  {slide_ct}
</Types>''')

        zf.writestr("_rels/.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>''')

        zf.writestr("ppt/presentation.xml", f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId0"/></p:sldMasterIdLst>
  <p:sldIdLst>
    {slide_id_list}
  </p:sldIdLst>
  <p:sldSz cx="{W}" cy="{H}" type="custom"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>''')

        zf.writestr("ppt/_rels/presentation.xml.rels", f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId0" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  {prs_rels_entries}
</Relationships>''')

        zf.writestr("ppt/slideMasters/slideMaster1.xml", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr clr="bg1"/></p:bgRef></p:bg>
  <p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
  <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>''')

        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>''')

        zf.writestr("ppt/slideLayouts/slideLayout1.xml", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClr/></p:clrMapOvr>
</p:sldLayout>''')

        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>''')

        # Embed each slide image
        for i, jpg_path in enumerate(slide_jpg_paths, 1):
            zf.writestr(f"ppt/slides/slide{i}.xml", slide_xml())
            zf.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels(i))
            with open(jpg_path, 'rb') as f:
                zf.writestr(f"ppt/media/image{i}.jpg", f.read())
            print(f"  Slide {i:02d} embedded ✓")

    print(f"\n✅ PPTX saved: {output_path}")
    print(f"   Size: {os.path.getsize(output_path)//1024} KB")
    return output_path
```

---

## الخطوة 4: التحقق البصري قبل التسليم

```bash
# Convert to PDF for visual QA
python3 /mnt/skills/public/pptx/scripts/office/soffice.py \
  --headless --convert-to pdf OUTPUT.pptx --outdir /home/claude/

# Convert PDF to images
pdftoppm -jpeg -r 100 OUTPUT.pdf /home/claude/qa_slide

# View each slide
# view /home/claude/qa_slide-01.jpg  ... etc
```

**تحقق من:**
- كل شريحة مختلفة عن السابقة
- اللوجو والـ badge ظاهرين في كل شريحة
- ترتيب الشرائح صحيح (01 → N)
- لا تكرار

---

## أخطاء شائعة وحلولها

| الخطأ | السبب | الحل |
|-------|-------|------|
| شرائح مكررة في PPTX | استخدام python-pptx يسبب مشاكل في الـ image references | استخدم دائماً `build_pptx_raw()` |
| timeout عند التوليد | كل صورة تأخذ ~30 ثانية | ولّد على دفعات 3-5 صور |
| صور فارغة أو رمادية | rate limiting | أضف `time.sleep(10)` بعد كل صورة |
| الـ PPTX لا يفتح | XML malformed | تحقق من أن كل `slide{i}.xml` له `image{i}.jpg` مقابله |
| اللوجو مش ظاهر | gpt-image-2 تجاهله | اذكره صراحة في أول سطر في البرومبت |

---

## ملاحظات مهمة

- **API Key**: مطلوب OPENAI_API_KEY — لا تضعه hardcoded في الملف
- **الاستئناف**: السكريبت يتحقق من وجود الملف — يمكن الاستئناف بدون إعادة التوليد
- **الحجم**: 15 صورة ≈ 3-4 MB للـ PPTX (بعد compression)
- **البرومبت**: كلما كان أوضح وأكثر تفصيلاً، كانت الصورة أدق
- **اللغة العربية**: gpt-image-2 يتعامل مع العربية — اكتبها مباشرة في البرومبت بدون أي preprocessing
