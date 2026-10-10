from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .models import DeckSpec, ProviderConfig, deck_json_schema


class ProviderError(RuntimeError):
    """Raised when a provider cannot produce a valid response."""


class AIProvider(ABC):
    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    @abstractmethod
    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def generate_deck(self, prompt: str) -> DeckSpec:
        payload = self.generate_json(prompt, deck_json_schema())
        return DeckSpec.model_validate(payload)


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ProviderError("provider response did not contain a JSON object") from None
        try:
            payload = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ProviderError(f"provider returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ProviderError("provider response root must be a JSON object")
    return payload


def _secret_from_env(name: str) -> str:
    if not name:
        raise ProviderError("api_key_env is required for this provider")
    value = os.environ.get(name, "")
    if not value:
        raise ProviderError(f"required credential environment variable is not set: {name}")
    return value


class HttpProvider(AIProvider):
    def _post(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=body, method="POST")
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header("Content-Type", "application/json")

        attempts = self.config.max_retries + 1
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(
                    request, timeout=self.config.timeout_seconds
                ) as response:
                    parsed = json.loads(response.read().decode("utf-8"))
                    if not isinstance(parsed, dict):
                        raise ProviderError("provider HTTP response root is not an object")
                    return parsed
            except urllib.error.HTTPError as exc:
                retryable = exc.code == 429 or 500 <= exc.code < 600
                if retryable and attempt + 1 < attempts:
                    time.sleep(min(2**attempt, 8))
                    continue
                safe_detail = exc.read(1200).decode("utf-8", errors="replace")
                safe_detail = re.sub(r"(?i)(api[_-]?key|authorization)[^,}\n]*", r"\1=[redacted]", safe_detail)
                raise ProviderError(f"provider HTTP {exc.code}: {safe_detail}") from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt + 1 < attempts:
                    time.sleep(min(2**attempt, 8))
                    continue
                raise ProviderError(f"provider connection failed: {exc}") from exc
        raise ProviderError("provider request exhausted retries")


class OpenAICompatibleProvider(HttpProvider):
    """Works with OpenAI-compatible chat-completions endpoints, including GLM/Kimi gateways."""

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        base = self.config.base_url.rstrip("/")
        if not base:
            raise ProviderError("base_url is required for openai_compatible")
        key = _secret_from_env(self.config.api_key_env)
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Return one JSON object only. It must match the supplied schema.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.35,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "training_deck",
                    "strict": True,
                    "schema": schema,
                },
            },
        }
        headers = {"Authorization": f"Bearer {key}", **self.config.extra_headers}
        try:
            response = self._post(f"{base}/chat/completions", payload, headers)
        except ProviderError as exc:
            if "HTTP 400" not in str(exc):
                raise
            payload.pop("response_format", None)
            response = self._post(f"{base}/chat/completions", payload, headers)

        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("unexpected OpenAI-compatible response structure") from exc
        return _extract_json(content)


class GeminiProvider(HttpProvider):
    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        key = _secret_from_env(self.config.api_key_env)
        base = (self.config.base_url or "https://generativelanguage.googleapis.com").rstrip("/")
        model = self.config.model
        if not model:
            raise ProviderError("model is required for Gemini")
        encoded_key = urllib.parse.quote(key, safe="")
        url = f"{base}/v1beta/models/{urllib.parse.quote(model, safe='')}:generateContent?key={encoded_key}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.35,
                "responseMimeType": "application/json",
            },
        }
        response = self._post(url, payload, self.config.extra_headers)
        try:
            content = response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("unexpected Gemini response structure") from exc
        return _extract_json(content)


class AnthropicProvider(HttpProvider):
    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        key = _secret_from_env(self.config.api_key_env)
        base = (self.config.base_url or "https://api.anthropic.com").rstrip("/")
        payload = {
            "model": self.config.model,
            "max_tokens": 16000,
            "temperature": 0.35,
            "system": "Return one JSON object only. It must match the schema in the request.",
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            **self.config.extra_headers,
        }
        response = self._post(f"{base}/v1/messages", payload, headers)
        try:
            blocks = response["content"]
            content = "".join(block["text"] for block in blocks if block.get("type") == "text")
        except (KeyError, TypeError) as exc:
            raise ProviderError("unexpected Anthropic response structure") from exc
        return _extract_json(content)


class CodexCliProvider(AIProvider):
    """Uses the locally authenticated Codex CLI without reading or copying its credentials."""

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        command = [
            "codex",
            "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
        ]
        if self.config.model:
            command.extend(["--model", self.config.model])

        with tempfile.TemporaryDirectory(prefix="deck-codex-") as temporary:
            temp = Path(temporary)
            schema_path = temp / "deck.schema.json"
            output_path = temp / "deck.json"
            schema_path.write_text(json.dumps(schema, ensure_ascii=False), encoding="utf-8")
            command.extend(
                ["--output-schema", str(schema_path), "--output-last-message", str(output_path), "-"]
            )
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                cwd=temp,
                timeout=self.config.timeout_seconds,
                check=False,
            )
            if completed.returncode != 0:
                detail = completed.stderr.strip()[-1200:]
                raise ProviderError(f"Codex CLI failed with exit {completed.returncode}: {detail}")
            if not output_path.exists():
                raise ProviderError("Codex CLI completed without writing the requested output")
            return _extract_json(output_path.read_text(encoding="utf-8"))


class CommandProvider(AIProvider):
    """Runs a user-supplied executable that accepts a prompt on stdin and emits JSON on stdout."""

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        if not self.config.command:
            raise ProviderError("command provider requires a non-empty command array")
        request = json.dumps({"prompt": prompt, "schema": schema}, ensure_ascii=False)
        completed = subprocess.run(
            self.config.command,
            input=request,
            text=True,
            capture_output=True,
            timeout=self.config.timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            raise ProviderError(
                f"command provider failed with exit {completed.returncode}: "
                f"{completed.stderr.strip()[-1200:]}"
            )
        return _extract_json(completed.stdout)


class FixtureProvider(AIProvider):
    def generate_json(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        del prompt, schema
        if not self.config.fixture_path:
            raise ProviderError("fixture provider requires fixture_path")
        return json.loads(Path(self.config.fixture_path).read_text(encoding="utf-8"))


def provider_from_config(config: ProviderConfig) -> AIProvider:
    providers: dict[str, type[AIProvider]] = {
        "openai_compatible": OpenAICompatibleProvider,
        "gemini": GeminiProvider,
        "anthropic": AnthropicProvider,
        "codex_cli": CodexCliProvider,
        "command": CommandProvider,
        "fixture": FixtureProvider,
    }
    try:
        provider_type = providers[config.provider]
    except KeyError as exc:
        supported = ", ".join(sorted(providers))
        raise ProviderError(f"unsupported provider '{config.provider}'; choose: {supported}") from exc
    return provider_type(config)
