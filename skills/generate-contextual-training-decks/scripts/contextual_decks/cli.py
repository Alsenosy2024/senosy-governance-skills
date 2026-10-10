from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from .models import ProviderConfig, deck_json_schema
from .planning import load_deck, plan_deck, save_deck
from .providers import ProviderError, provider_from_config
from .qa import inspect_pptx, inspect_spec, render_pdf, write_report
from .renderer import render_deck


def _read_brief(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _add_provider_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--provider", required=True, help="Provider JSON configuration file")
    parser.add_argument("--brief", required=True, help="UTF-8 brief file, or - for stdin")
    parser.add_argument("--slides", type=int, default=None, help="Target slide count")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate_deck.py",
        description="Provider-agnostic AI planner and Arabic RTL PowerPoint renderer.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    schema = sub.add_parser("schema", help="Write the DeckSpec JSON Schema")
    schema.add_argument("--out", required=True)

    plan = sub.add_parser("plan", help="Use an AI provider to create a validated deck specification")
    _add_provider_args(plan)
    plan.add_argument("--out", required=True, help="Output DeckSpec JSON")

    render = sub.add_parser("render", help="Render a validated DeckSpec JSON to PPTX")
    render.add_argument("--spec", required=True)
    render.add_argument("--out", required=True)
    render.add_argument("--qa", default="", help="Optional QA JSON report path")
    render.add_argument("--pdf-dir", default="", help="Optional directory for LibreOffice PDF render")

    build = sub.add_parser("build", help="Plan with AI, then render PPTX")
    _add_provider_args(build)
    build.add_argument("--out", required=True, help="Output PPTX")
    build.add_argument("--spec-out", required=True, help="Persist the generated DeckSpec JSON")
    build.add_argument("--qa", default="", help="Optional QA JSON report path")
    build.add_argument("--pdf-dir", default="", help="Optional directory for LibreOffice PDF render")
    return parser


def _render_flow(spec_path: str, output_path: str, qa_path: str, pdf_dir: str) -> int:
    deck = load_deck(spec_path)
    result = render_deck(deck, output_path)
    report = inspect_spec(deck, result.layouts)
    inspect_pptx(result.output_path, report)
    if pdf_dir:
        pdf = render_pdf(result.output_path, pdf_dir)
        if pdf:
            report.rendered_pdf = str(pdf)
        else:
            report.add("warning", "render.pdf_failed", "LibreOffice PDF rendering was unavailable or failed.")
    if qa_path:
        write_report(report, qa_path)
    print(
        json.dumps(
            {
                "pptx": str(result.output_path),
                "slides": len(deck.slides),
                "qa_passed": report.passed,
                "qa_report": qa_path,
                "rendered_pdf": report.rendered_pdf,
            },
            ensure_ascii=False,
        )
    )
    return 0 if report.passed else 2


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "schema":
            output = Path(args.out)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(deck_json_schema(), ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(str(output))
            return 0

        if args.command in {"plan", "build"}:
            config = ProviderConfig.from_json_file(args.provider)
            provider = provider_from_config(config)
            deck = plan_deck(provider, _read_brief(args.brief), args.slides)
            spec_output = args.out if args.command == "plan" else args.spec_out
            save_deck(deck, spec_output)
            if args.command == "plan":
                print(json.dumps({"spec": spec_output, "slides": len(deck.slides)}, ensure_ascii=False))
                return 0
            return _render_flow(spec_output, args.out, args.qa, args.pdf_dir)

        return _render_flow(args.spec, args.out, args.qa, args.pdf_dir)
    except (ProviderError, ValidationError, OSError, ValueError) as exc:
        print(json.dumps({"error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

