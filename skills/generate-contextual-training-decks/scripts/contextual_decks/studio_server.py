from __future__ import annotations

import argparse
import json
import mimetypes
import re
import threading
import traceback
import uuid
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from pydantic import ValidationError

from .longform import LongDeckRequest, build_ai_long_deck, build_demo_long_deck, preview_long_deck, theme_catalog
from .planning import save_deck
from .providers import ProviderError, provider_from_config
from .qa import inspect_pptx, inspect_spec, render_pdf, write_report
from .renderer import render_deck


MAX_BODY = 2 * 1024 * 1024


@dataclass
class Job:
    id: str
    title: str
    status: str = "queued"
    progress: int = 0
    stage: str = "queued"
    message: str = "تم استلام الطلب"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    logs: list[str] = field(default_factory=list)
    files: list[dict[str, str | int]] = field(default_factory=list)
    error: str = ""

    def public(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "progress": self.progress,
            "stage": self.stage,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "logs": self.logs[-30:],
            "files": self.files,
            "error": self.error,
        }


class StudioState:
    def __init__(self, data_dir: Path, static_dir: Path) -> None:
        self.data_dir = data_dir.resolve()
        self.static_dir = static_dir.resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.jobs: dict[str, Job] = {}
        self.lock = threading.Lock()

    def update(self, job_id: str, progress: int, stage: str, message: str) -> None:
        with self.lock:
            job = self.jobs[job_id]
            job.progress = max(job.progress, min(100, progress))
            job.stage = stage
            job.message = message
            job.updated_at = datetime.now(timezone.utc).isoformat()
            stamp = datetime.now().strftime("%H:%M:%S")
            line = f"{stamp} — {message}"
            if not job.logs or job.logs[-1] != line:
                job.logs.append(line)


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^\w\-]+", "-", value.strip(), flags=re.UNICODE).strip("-")
    return cleaned[:70] or "training-deck"


def _run_job(state: StudioState, job_id: str, request: LongDeckRequest) -> None:
    job_dir = (state.data_dir / job_id).resolve()
    try:
        job_dir.mkdir(parents=True, exist_ok=False)
        state.update(job_id, 3, "planning", "بدأت هندسة العرض وتوزيع الشرائح")
        if request.mode == "ai":
            provider = provider_from_config(request.provider)
            deck = build_ai_long_deck(
                request,
                provider,
                lambda percent, stage, message: state.update(job_id, percent, stage, message),
            )
        else:
            deck = build_demo_long_deck(
                request,
                lambda percent, stage, message: state.update(job_id, percent, stage, message),
            )

        slug = _safe_name(request.title)
        spec_path = job_dir / f"{slug}.json"
        pptx_path = job_dir / f"{slug}.pptx"
        qa_path = job_dir / f"{slug}-qa.json"
        save_deck(deck, spec_path)
        state.update(job_id, 86, "rendering", "يتم الآن تصيير الشرائح إلى PowerPoint")
        result = render_deck(deck, pptx_path)
        state.update(job_id, 94, "qa", "يتم فحص عدد الشرائح والمحتوى والتباين")
        report = inspect_spec(deck, result.layouts)
        inspect_pptx(pptx_path, report)
        files = [
            {"name": pptx_path.name, "label": "PowerPoint", "size": pptx_path.stat().st_size},
            {"name": spec_path.name, "label": "DeckSpec JSON", "size": spec_path.stat().st_size},
        ]
        if request.render_pdf:
            pdf = render_pdf(pptx_path, job_dir)
            if pdf:
                report.rendered_pdf = str(pdf)
                files.append({"name": pdf.name, "label": "PDF", "size": pdf.stat().st_size})
            else:
                report.add("warning", "render.pdf_failed", "LibreOffice PDF rendering was unavailable or failed.")
        write_report(report, qa_path)
        files.append({"name": qa_path.name, "label": "QA report", "size": qa_path.stat().st_size})
        with state.lock:
            job = state.jobs[job_id]
            job.status = "complete" if report.passed else "complete_with_issues"
            job.progress = 100
            job.stage = "complete"
            job.message = "اكتمل العرض واجتاز الفحص" if report.passed else "اكتمل العرض مع ملاحظات جودة"
            job.files = files
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append(f"{datetime.now().strftime('%H:%M:%S')} — {job.message}")
    except (ValidationError, ProviderError, OSError, ValueError, RuntimeError) as exc:
        with state.lock:
            job = state.jobs[job_id]
            job.status = "failed"
            job.stage = "failed"
            job.message = "تعذر إكمال العرض"
            job.error = f"{type(exc).__name__}: {exc}"
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append(f"{datetime.now().strftime('%H:%M:%S')} — {job.error}")
    except Exception as exc:  # pragma: no cover - last-resort job isolation
        with state.lock:
            job = state.jobs[job_id]
            job.status = "failed"
            job.stage = "failed"
            job.message = "حدث خطأ غير متوقع"
            job.error = f"{type(exc).__name__}: {exc}"
            job.logs.append(traceback.format_exc(limit=4))


def handler_factory(state: StudioState):
    class StudioHandler(BaseHTTPRequestHandler):
        server_version = "ContextualDeckStudio/1.0"

        def log_message(self, format: str, *args) -> None:
            return

        def _json(self, payload: dict | list, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _error(self, status: int, message: str, details: object = None) -> None:
            payload = {"error": message}
            if details is not None:
                payload["details"] = details
            self._json(payload, status)

        def _read_json(self) -> dict:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise ValueError("invalid Content-Length") from exc
            if length <= 0 or length > MAX_BODY:
                raise ValueError("request body must be between 1 byte and 2 MB")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON root must be an object")
            return payload

        def _serve_static(self, relative: str) -> None:
            name = "index.html" if relative in {"", "/"} else relative.lstrip("/")
            target = (state.static_dir / name).resolve()
            if state.static_dir not in target.parents and target != state.static_dir:
                self._error(HTTPStatus.FORBIDDEN, "invalid path")
                return
            if not target.is_file():
                target = state.static_dir / "index.html"
            body = target.read_bytes()
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8" if content_type.startswith("text/") else content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            path = unquote(urlparse(self.path).path)
            if path == "/api/health":
                self._json({"ok": True, "service": "Contextual Deck Studio", "version": "1.0"})
                return
            if path == "/api/themes":
                self._json(theme_catalog())
                return
            match = re.fullmatch(r"/api/jobs/([a-f0-9]{32})", path)
            if match:
                with state.lock:
                    job = state.jobs.get(match.group(1))
                    payload = job.public() if job else None
                if payload is None:
                    self._error(HTTPStatus.NOT_FOUND, "job not found")
                else:
                    self._json(payload)
                return
            match = re.fullmatch(r"/api/jobs/([a-f0-9]{32})/download/([^/]+)", path)
            if match:
                job_id, filename = match.groups()
                target = (state.data_dir / job_id / filename).resolve()
                job_root = (state.data_dir / job_id).resolve()
                if job_root not in target.parents or not target.is_file():
                    self._error(HTTPStatus.NOT_FOUND, "file not found")
                    return
                body = target.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
                self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{target.name}")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self._serve_static(path)

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            try:
                payload = self._read_json()
                request = LongDeckRequest.model_validate(payload)
            except json.JSONDecodeError:
                self._error(HTTPStatus.BAD_REQUEST, "invalid JSON")
                return
            except ValidationError as exc:
                self._error(HTTPStatus.UNPROCESSABLE_ENTITY, "validation failed", exc.errors(include_url=False))
                return
            except ValueError as exc:
                self._error(HTTPStatus.BAD_REQUEST, str(exc))
                return

            if path == "/api/preview":
                self._json(preview_long_deck(request).model_dump(mode="json"))
                return
            if path == "/api/jobs":
                job_id = uuid.uuid4().hex
                with state.lock:
                    state.jobs[job_id] = Job(id=job_id, title=request.title)
                thread = threading.Thread(target=_run_job, args=(state, job_id, request), daemon=True)
                thread.start()
                self._json({"job_id": job_id, "status": "queued"}, HTTPStatus.ACCEPTED)
                return
            self._error(HTTPStatus.NOT_FOUND, "endpoint not found")

    return StudioHandler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local Arabic long-deck generation studio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data-dir", default="studio-runs")
    parser.add_argument("--open", action="store_true", dest="open_browser")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    static_dir = Path(__file__).resolve().parents[2] / "studio" / "static"
    if not static_dir.is_dir():
        raise SystemExit(f"static directory not found: {static_dir}")
    state = StudioState(Path(args.data_dir), static_dir)
    server = ThreadingHTTPServer((args.host, args.port), handler_factory(state))
    url = f"http://{args.host}:{args.port}"
    print(json.dumps({"status": "ready", "url": url, "data_dir": str(state.data_dir)}, ensure_ascii=False), flush=True)
    if args.open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
