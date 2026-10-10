---
name: arabic-office-qa
description: Enforce Arabic RTL, safe fonts, and post-export visual QA on top of the xlsx/pptx/docx/pdf/doc-coauthoring skills. Use whenever an Office/PDF deliverable must contain Arabic text.
---

# Arabic Office QA

Companion layer over `xlsx`, `pptx`, `docx`, `pdf`, `doc-coauthoring`. Those skills build the file; this skill makes sure Arabic content in it is correct. Apply every rule below whenever a doc/sheet/slide/PDF contains Arabic text — do not skip because "it looked fine in generation."

## 1. RTL direction

- Word (docx): set paragraph `bidi` on any paragraph containing Arabic, and table `bidiVisual` on any table with Arabic content/headers.
- PowerPoint (pptx): set `rtl` on text frames/paragraphs with Arabic; right-align Arabic text boxes; mirror slide layout (titles/numbers) for RTL reading order if the deck is Arabic-first, not just Arabic-labeled.
- Excel (xlsx): set sheet `sheetView.rightToLeft` for Arabic-primary sheets; right-align Arabic cells explicitly (don't rely on auto-detection).
- PDF (generated, not extracted): shape Arabic through `arabic_reshaper` + a bidi pass before layout — see font section, this is a hard requirement, not optional polish.

## 2. Safe fonts — never assume a font "supports Arabic" from its name or cmap alone

Use only: **Noto Naskh Arabic**, **Noto Kufi Arabic**, **Cairo**, or **IBM Plex Sans Arabic**. Do not substitute a font because it's already installed or looks close — a font can claim Arabic support (glyphs present in `cmap`) while specific glyphs are empty outlines.

Known bad case, confirmed by direct incident: ThmanyahSans-Bold's "لا" (lam-alef, U+FEFB) glyph is present in cmap but has 0 contours — renders as a silent gap, not a visible error. See [[feedback_thmanyah_font_lamalef_bug]].

**Before shipping any font in a template:** verify every glyph you'll render actually has ink, not just a cmap entry:

```python
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

def has_ink(font_path, ch):
    ttf = TTFont(font_path)
    cmap = ttf.getBestCmap()
    glyphs = ttf.getGlyphSet()
    gname = cmap.get(ord(ch))
    if gname is None:
        return False  # not in cmap at all
    pen = BoundsPen(glyphs)
    glyphs[gname].draw(pen)
    return pen.bounds is not None  # False = empty outline, silent failure
```

Run this over the full string you intend to render (all lam-alef ligature forms especially: ﻻ ﻼ ﻹ ﻷ ﻵ), not just spot-checked letters.

## 3. Mixed Arabic/English tables and numbers

Column alignment does not auto-correct in mixed-direction tables. Pin alignment explicitly per column (numbers/dates LTR-aligned even inside an RTL table; Arabic text columns RTL-aligned) rather than trusting the framework default — this is where visual bugs concentrate.

## 4. Mandatory post-export visual verification

Never report an Arabic export "done" without opening the actual rendered output and checking it visually:

- Convert to image/PDF preview (e.g. LibreOffice headless `--convert-to pdf`, then render pages to PNG) and Read the image.
- Check: letters are properly connected (no floating isolated forms where they should be joined), text flows right-to-left, no tofu/box glyphs, no blank gaps where a ligature should render.
- For tables: confirm column order reads right-to-left as intended, numbers aren't mirrored.

This mirrors the same discipline used in [[project_ai_diploma_comedy_promo]]'s caption pipeline (`shape()`/`_has_ink()` glyph guard, described in [[feedback_thmanyah_font_lamalef_bug]]) — the same class of bug (present-in-cmap, empty-outline) shows up in Office/PDF exports too, not just video captions.

## Workflow

1. Build the file with the relevant official skill (xlsx/pptx/docx/pdf/doc-coauthoring).
2. Apply RTL properties (section 1) and pin fonts to the safe list (section 2), verifying glyph ink for any font not already known-good.
3. Fix mixed-direction table/number alignment explicitly (section 3).
4. Export a visual preview and actually look at it (section 4) before calling the task done.
