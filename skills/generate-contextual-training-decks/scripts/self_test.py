#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from contextual_decks.models import DeckSpec, ProviderConfig
from contextual_decks.longform import LongDeckRequest, ProgramAxis, build_demo_long_deck, preview_long_deck
from contextual_decks.planning import load_deck
from contextual_decks.providers import provider_from_config
from contextual_decks.qa import inspect_pptx, inspect_spec
from contextual_decks.renderer import LayoutSelector, render_deck


def main() -> int:
    skill_dir = SCRIPT_DIR.parent
    fixture = skill_dir / "assets" / "example_deck.json"
    deck = load_deck(fixture)
    assert isinstance(deck, DeckSpec)
    assert len(deck.slides) >= 10

    provider = provider_from_config(
        ProviderConfig(provider="fixture", fixture_path=str(fixture))
    )
    planned = provider.generate_deck("ignored in fixture mode")
    assert planned.title == deck.title

    with tempfile.TemporaryDirectory(prefix="contextual-deck-test-") as temporary:
        output = Path(temporary) / "test.pptx"
        result = render_deck(planned, output)
        report = inspect_spec(planned, result.layouts)
        inspect_pptx(output, report)
        assert output.exists() and output.stat().st_size > 10_000
        assert report.passed, json.dumps(report.to_dict(), ensure_ascii=False)

        # Exercise every registered visual variant with realistic content for its kind.
        by_kind = {slide.kind: slide for slide in deck.slides}
        variant_slides = []
        for kind, variants in LayoutSelector.variants.items():
            source = by_kind[kind]
            for variant in variants:
                variant_slides.append(
                    source.model_copy(
                        deep=True,
                        update={
                            "id": f"test-{variant}",
                            "title": f"{source.title} — {variant}",
                            "layout_hint": variant,
                        },
                    )
                )
        variant_deck = deck.model_copy(deep=True, update={"slides": variant_slides})
        variants_output = Path(temporary) / "all-layouts.pptx"
        variants_result = render_deck(variant_deck, variants_output)
        variants_report = inspect_spec(variant_deck, variants_result.layouts)
        inspect_pptx(variants_output, variants_report)
        assert len(variants_result.layouts) == sum(
            len(variants) for variants in LayoutSelector.variants.values()
        )
        assert variants_report.passed, json.dumps(
            variants_report.to_dict(), ensure_ascii=False
        )

        request = LongDeckRequest(
            title="مختبر القرارات للمشروعات",
            subtitle="برنامج تطبيقي طويل",
            audience="مديرو المشروعات وقادة فرق التنفيذ",
            sector="الخدمات المهنية",
            duration_hours=10,
            slide_count=50,
            objectives="تشخيص القرار\nبناء البدائل\nنقل الأثر إلى العمل",
            axes=[
                ProgramAxis(title="تشخيص السياق", details="قراءة الموقف وأصحاب المصلحة", weight=1),
                ProgramAxis(title="البيانات والذكاء الاصطناعي", details="تحويل البيانات إلى دليل", weight=1.2),
                ProgramAxis(title="الحوكمة والقرار", details="الصلاحيات ونقاط الاعتماد", weight=1),
                ProgramAxis(title="إدارة المخاطر والتكلفة", details="المفاضلات تحت القيود", weight=1.1),
                ProgramAxis(title="نقل الأثر", details="التطبيق والمتابعة", weight=.8),
            ],
            theme_pack="sandstone",
            theme_strategy="contextual",
        )
        preview = preview_long_deck(request)
        assert sum(module.slides for module in preview.modules) + 8 == 50
        long_deck = build_demo_long_deck(request)
        assert len(long_deck.slides) == 50
        assert len({slide.theme_key for slide in long_deck.slides if slide.theme_key}) >= 3
        long_output = Path(temporary) / "long-50.pptx"
        long_result = render_deck(long_deck, long_output)
        long_report = inspect_spec(long_deck, long_result.layouts)
        inspect_pptx(long_output, long_report)
        assert long_report.passed, json.dumps(long_report.to_dict(), ensure_ascii=False)

    print(
        json.dumps(
            {
                "status": "ok",
                "sample_slides": len(deck.slides),
                "layout_variants": sum(
                    len(variants) for variants in LayoutSelector.variants.values()
                ),
                "long_deck_slides": 50,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
