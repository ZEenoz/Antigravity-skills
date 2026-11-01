"""Style profile: the shared, portable description of a house style.

A profile is a JSON document (see assets/default_profile.json) that carries every
style decision a report needs: page setup, fonts and sizes, paragraph metrics,
caption rules, page numbering, the order of the book's parts and the labels used
for them. build_report.py applies a profile; check_report.py verifies against it.

Units: page setup is in millimetres, paragraph metrics in twips (1/20 pt,
1440 twips = 1 inch). Sizes are in points.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PROFILE = HERE.parent / "assets" / "default_profile.json"
TWIPS_PER_MM = 1440.0 / 25.4


def mm_to_tw(mm: float) -> int:
    return int(round(float(mm) * TWIPS_PER_MM))


def twips_to_mm(tw) -> float:
    return round(int(tw) / TWIPS_PER_MM, 2) if tw is not None else None


class Style:
    """Typed view over a style profile."""

    def __init__(self, profile: dict):
        self.raw = profile
        self.page = profile.get("page", {})
        self.fonts = profile.get("fonts", {})
        self.sizes = self.fonts.get("sizes_pt", {})
        self.paras = profile.get("paragraphs", {})
        self.captions = profile.get("captions", {})
        self.tables = profile.get("tables", {})
        self.numbering = profile.get("page_numbering", {})
        self.structure = profile.get("structure", {})
        self.labels = profile.get("labels", {})
        self.headings = profile.get("headings", {})
        self.footer = profile.get("footer", {})
        self.keywords = profile.get("keywords", {})
        self.rules = profile.get("rules", {})
        self.rule_deltas = profile.get("rule_deltas", [])
        self.body_rules = profile.get("body_rules", {})

    # -- fonts / sizes -----------------------------------------------------------
    @property
    def font(self) -> str:
        return self.fonts.get("body") or "TH SarabunPSK"

    @property
    def allowed_fonts(self) -> list:
        allowed = self.fonts.get("allowed")
        if allowed:
            return list(allowed)
        return [self.font]

    def size(self, key: str, default: int = 12) -> int:
        return int(self.sizes.get(key, default))

    # -- paragraphs --------------------------------------------------------------
    @property
    def alignment(self) -> str:
        return self.paras.get("alignment", "left")

    @property
    def forbidden_alignment(self) -> list:
        return list(self.paras.get("forbidden_alignment", []))

    @property
    def first_line_tw(self) -> int:
        return int(self.paras.get("first_line_tw", 0))

    @property
    def space_after_tw(self) -> int:
        return int(self.paras.get("space_after_tw", 0))

    @property
    def space_before_tw(self) -> int:
        return int(self.paras.get("space_before_tw", 0))

    @property
    def line_tw(self) -> int:
        return int(self.paras.get("line_tw", 240))

    @property
    def list_left_tw(self) -> int:
        return int(self.paras.get("list_left_tw", 0))

    @property
    def list_hanging_tw(self) -> int:
        return int(self.paras.get("list_hanging_tw", 0))

    @property
    def hint_cs(self) -> bool:
        return bool(self.paras.get("hint_cs", False))

    # -- captions ----------------------------------------------------------------
    def caption_text(self, kind: str, number: str, text: str, lang: str) -> str:
        label = self.captions.get(
            f"{kind}_label" if lang == "th" else f"{kind}_label_en",
            self.captions.get(f"{kind}_label", ""))
        number = f" {number}" if number else ""
        return f"{label}{number}{(' ' + text) if text else ''}".strip()

    def source_text(self, text: str, lang: str) -> str:
        prefix = self.captions.get(
            "source_prefix" if lang == "th" else "source_prefix_en",
            self.captions.get("source_prefix", ""))
        return f"{prefix}{text})" if prefix else text

    def caption_labels(self) -> list:
        """Every spelling of the table/figure caption labels the style allows."""
        out = []
        for key in ("table_label", "table_label_en", "figure_label", "figure_label_en"):
            value = self.captions.get(key)
            if value:
                out.append(value)
        return out

    # -- structure ---------------------------------------------------------------
    def front_parts(self) -> list:
        return self.structure.get("front", [])

    def back_parts(self) -> list:
        return self.structure.get("back", [])

    def chapter_defaults(self, number) -> dict:
        for chapter in self.structure.get("chapters", []):
            if str(chapter.get("number")) == str(number):
                return chapter
        return {}

    def part_label(self, kind: str, lang: str) -> str:
        entry = self.labels.get(kind) or {}
        return entry.get(lang) or entry.get("th") or entry.get("en") or ""

    def label(self, key: str, lang: str) -> str:
        entry = self.labels.get(key) or {}
        return entry.get(lang) or entry.get("th") or entry.get("en") or key

    def content_width_mm(self) -> float:
        return (self.page.get("width_mm", 210.0)
                - self.page.get("margin_left_mm", 25.4)
                - self.page.get("margin_right_mm", 25.4))

    # -- rules ---------------------------------------------------------------------
    def rule_ids(self, check: str) -> list:
        """The rule IDs a check enforces, so a report can quote them back."""
        return list((self.rules.get("ids") or {}).get(check, []))

    @property
    def rules_authoritative(self) -> str:
        return self.rules.get("authoritative", "")

    def deltas_for(self, key: str) -> list:
        return [d for d in self.rule_deltas if d.get("item") == key]

    # -- body geometry -------------------------------------------------------------
    @property
    def first_line_mode(self) -> str:
        """'indent' (w:ind firstLine), 'tab' (leading <w:tab/>) or 'either'."""
        return self.paras.get("first_line_mode", "indent" if self.first_line_tw else "tab")

    @property
    def first_line_tab_tw(self) -> int:
        return int(self.paras.get("first_line_tab_tw", self.first_line_tw or 567))

    @property
    def space_after_heading_tw(self) -> int:
        return int(self.paras.get("space_after_heading_tw", self.space_after_tw))

    # -- footer / keywords ---------------------------------------------------------
    @property
    def footer_text(self) -> str:
        return str(self.footer.get("text", ""))

    def footer_text_for(self, part_kind: str) -> str:
        """The footer for one part of the book (the cover carries its own marking)."""
        return str((self.footer.get("by_part") or {}).get(part_kind) or self.footer_text)

    def footer_geometry(self):
        return (int(self.footer.get("size_pt", self.size("footer", 10))),
                self.footer.get("alignment", "left"))

    def keyword_rule(self, lang: str) -> dict:
        """The keyword line's separator and allowed count for one language."""
        sep = self.keywords.get(f"separator_{lang}", self.keywords.get("separator_th", " "))
        return {"label": self.keywords.get(f"label_{lang}", ""), "separator": sep,
                "min": int(self.keywords.get("min", 4)),
                "max": int(self.keywords.get("max", 6))}

    # -- captions -------------------------------------------------------------------
    def caption_placement(self, kind: str) -> str:
        return (self.captions.get("placement") or {}).get(kind, "above")

    def caption_alignment(self, kind: str) -> str:
        return self.captions.get(f"{kind}_alignment", self.captions.get("alignment", "center"))

    def chapter_sections(self, number) -> list:
        return list(self.chapter_defaults(number).get("sections") or [])

    def last_section_keywords(self, number) -> list:
        return list(self.chapter_defaults(number).get("last_section_keywords") or [])

    def required_section_keywords(self, number) -> list:
        return list(self.chapter_defaults(number).get("required_keywords") or [])


def load_profile(path: Path | None = None) -> Style:
    profile_path = Path(path) if path else DEFAULT_PROFILE
    if not profile_path.exists():
        raise SystemExit(f"profile not found: {profile_path}")
    return Style(json.loads(profile_path.read_text(encoding="utf-8")))
