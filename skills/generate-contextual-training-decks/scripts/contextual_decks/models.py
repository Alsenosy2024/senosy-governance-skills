from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SlideKind(str, Enum):
    AUTO = "auto"
    COVER = "cover"
    SECTION = "section"
    STATEMENT = "statement"
    CONCEPT = "concept"
    PROCESS = "process"
    TIMELINE = "timeline"
    COMPARISON = "comparison"
    METRICS = "metrics"
    CASE_STUDY = "case_study"
    ACTIVITY = "activity"
    QUIZ = "quiz"
    TOOL = "tool"
    SUMMARY = "summary"


class SourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=240)
    url: str = Field(default="", max_length=1000)
    accessed: str = Field(default="", max_length=40)


class ContentItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(default="", max_length=80)
    title: str = Field(default="", max_length=140)
    text: str = Field(default="", max_length=500)
    value: str = Field(default="", max_length=80)
    note: str = Field(default="", max_length=240)

    @model_validator(mode="after")
    def at_least_one_value(self) -> "ContentItem":
        if not any((self.label, self.title, self.text, self.value, self.note)):
            raise ValueError("content item must contain at least one non-empty field")
        return self


class FacilitatorNotes(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(default="", max_length=500)
    timing: str = Field(default="", max_length=80)
    script: str = Field(default="", max_length=3000)
    instruction: str = Field(default="", max_length=1500)
    answer_or_debrief: str = Field(default="", max_length=1500)
    transition: str = Field(default="", max_length=500)


class SlideSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default="", max_length=80)
    kind: SlideKind = SlideKind.AUTO
    title: str = Field(min_length=1, max_length=220)
    subtitle: str = Field(default="", max_length=300)
    eyebrow: str = Field(default="", max_length=80)
    body: str = Field(default="", max_length=1800)
    bullets: list[str] = Field(default_factory=list, max_length=8)
    items: list[ContentItem] = Field(default_factory=list, max_length=8)
    choices: list[str] = Field(default_factory=list, max_length=6)
    answer_index: int | None = Field(default=None, ge=0)
    takeaway: str = Field(default="", max_length=400)
    duration_minutes: int | None = Field(default=None, ge=1, le=240)
    layout_hint: str = Field(default="", max_length=80)
    theme_key: str = Field(default="", max_length=80)
    image_path: str = Field(default="", max_length=1000)
    image_prompt: str = Field(default="", max_length=1000)
    notes: FacilitatorNotes = Field(default_factory=FacilitatorNotes)
    sources: list[SourceRef] = Field(default_factory=list, max_length=20)

    @field_validator("bullets", "choices")
    @classmethod
    def trim_string_lists(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value and value.strip()]

    @model_validator(mode="after")
    def validate_quiz(self) -> "SlideSpec":
        if self.answer_index is not None and self.answer_index >= len(self.choices):
            raise ValueError("answer_index must reference an existing choice")
        return self


class ThemeSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "Warm professional Arabic"
    font_regular: str = "Thmanyah Sans"
    font_bold: str = "Thmanyah Sans"
    background: str = "F6F1E8"
    paper: str = "FFFFFF"
    ink: str = "0B1F33"
    primary: str = "007C7A"
    accent: str = "D5A02C"
    muted: str = "6B7280"
    success: str = "157A4A"
    danger: str = "B42318"
    footer_text: str = ""
    logo_path: str = ""

    @field_validator(
        "background", "paper", "ink", "primary", "accent", "muted", "success", "danger"
    )
    @classmethod
    def validate_hex(cls, value: str) -> str:
        cleaned = value.strip().lstrip("#").upper()
        if len(cleaned) != 6 or any(ch not in "0123456789ABCDEF" for ch in cleaned):
            raise ValueError(f"invalid six-digit hex color: {value}")
        return cleaned


class DeckSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=220)
    subtitle: str = Field(default="", max_length=300)
    language: str = "ar"
    direction: str = "rtl"
    program_name: str = Field(default="", max_length=180)
    audience: str = Field(default="", max_length=300)
    duration: str = Field(default="", max_length=100)
    learning_objective: str = Field(default="", max_length=600)
    version: str = Field(default="1.0", max_length=40)
    theme: ThemeSpec = Field(default_factory=ThemeSpec)
    theme_variants: dict[str, ThemeSpec] = Field(default_factory=dict, max_length=20)
    slides: list[SlideSpec] = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def normalize_slide_ids(self) -> "DeckSpec":
        for index, slide in enumerate(self.slides, start=1):
            if not slide.id:
                slide.id = f"slide-{index:02d}"
        return self


class ProviderConfig(BaseModel):
    """Provider configuration containing references to secrets, never secret values."""

    model_config = ConfigDict(extra="allow")

    provider: str = Field(
        description=(
            "codex_cli, openai_compatible, gemini, anthropic, command, or fixture"
        )
    )
    model: str = ""
    base_url: str = ""
    api_key_env: str = ""
    timeout_seconds: int = Field(default=180, ge=5, le=1800)
    max_retries: int = Field(default=2, ge=0, le=5)
    command: list[str] = Field(default_factory=list)
    fixture_path: str = ""
    extra_headers: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_json_file(cls, path: str | Path) -> "ProviderConfig":
        import json

        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(data)


def deck_json_schema() -> dict[str, Any]:
    return DeckSpec.model_json_schema()
