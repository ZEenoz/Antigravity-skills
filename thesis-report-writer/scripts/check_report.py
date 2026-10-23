#!/usr/bin/env python3
"""
check_report.py -- compliance gate for a report document.

Turns a house style into an executable checklist: every rule that can be checked
mechanically is checked against the style profile, and the result is reported per
rule so the author can fix exactly what is wrong instead of re-reading the style
guide.

Usage:
    python check_report.py Report.docx [--profile p.json] [--mode full|chapter]
                                        [--json out.json]

Exit code 0 = compliant, 1 = at least one FAIL.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profile import Style, load_profile, mm_to_tw  # noqa: E402

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class Result:
    def __init__(self, rule_id: str, title: str):
        self.rule_id = rule_id
        self.title = title
        self.status = "PASS"
        self.messages: list[str] = []
        self.checked = 0

    def fail(self, msg: str) -> None:
        self.status = "FAIL"
        self.messages.append(msg)

    def warn(self, msg: str) -> None:
        if self.status == "PASS":
            self.status = "WARN"
        self.messages.append(msg)

    def na(self, msg: str = "not present in this document") -> None:
        self.status = "NA"
        self.messages.append(msg)

    def as_dict(self) -> dict:
        return {"rule_id": self.rule_id, "title": self.title, "status": self.status,
                "checked": self.checked, "messages": self.messages}


def _val(el, name, default=None):
    if el is None:
        return default
    return el.get(W + name, default)


def _text_of(el) -> str:
    return "".join(t.text or "" for t in el.iter(W + "t"))


def _close(got: int, want: int, tol: int = 20) -> bool:
    """Measurements are compared with a small tolerance: a rule written in
    centimetres and converted to twips rounds, and 0.63 cm is 357 twips while
    0.635 cm is 360. That difference is not a formatting error."""
    return abs(got - want) <= tol


class Report:
    def __init__(self, path: Path):
        self.path = path
        self.zf = zipfile.ZipFile(str(path))
        self.names = self.zf.namelist()
        self.doc = etree.fromstring(self.zf.read("word/document.xml"))
        self.styles = etree.fromstring(self.zf.read("word/styles.xml"))
        self.settings = etree.fromstring(self.zf.read("word/settings.xml"))
        self.body = self.doc.find(W + "body")
        self.headers = [n for n in self.names if re.match(r"word/header\d*\.xml$", n)]
        self.header_xml = "".join(self.zf.read(n).decode("utf-8", "replace")
                                  for n in self.headers)
        self.paragraphs = list(self.body.iter(W + "p"))
        self.tables = list(self.body.iter(W + "tbl"))

    def pPr(self, p):
        return p.find(W + "pPr")

    def pstyle(self, p):
        pPr = self.pPr(p)
        return _val(pPr.find(W + "pStyle"), "val") if pPr is not None else None

    def pjc(self, p):
        pPr = self.pPr(p)
        return _val(pPr.find(W + "jc"), "val") if pPr is not None else None

    def pind(self, p):
        pPr = self.pPr(p)
        return pPr.find(W + "ind") if pPr is not None else None

    def pspacing(self, p):
        pPr = self.pPr(p)
        return pPr.find(W + "spacing") if pPr is not None else None

    def runs(self, p):
        return p.findall(W + "r")

    def run_size(self, run):
        rPr = run.find(W + "rPr")
        if rPr is None:
            return None
        return _val(rPr.find(W + "sz"), "val")

    def body_start_index(self, chapter_re) -> int:
        """Index of the first body paragraph in the body's direct children.

        The heading must be a real Heading 1 paragraph: a rendered table of
        contents contains a line "บทที่ 1" too, and counting it as the start of
        the body would make every front-matter entry look like a body caption.
        """
        children = list(self.body)
        for idx, el in enumerate(children):
            if el.tag == W + "p" and self.pstyle(el) == "Heading1" \
                    and chapter_re.match(_text_of(el).strip()):
                return idx
        return len(children)

    def body_paragraphs(self, chapter_re) -> list:
        """Paragraphs from the body onwards, in document order."""
        children = list(self.body)
        start = self.body_start_index(chapter_re)
        out = []
        for el in children[start:]:
            out.extend(el.iter(W + "p"))
        return out

    def style_size(self, style_id: str):
        for st in self.styles.iter(W + "style"):
            if st.get(W + "styleId") == style_id:
                rPr = st.find(W + "rPr")
                return _val(rPr.find(W + "sz"), "val") if rPr is not None else None
        return None


def caption_regex(style: Style, kind: str):
    labels = [style.captions.get(f"{kind}_label"), style.captions.get(f"{kind}_label_en")]
    labels = [re.escape(l) for l in labels if l]
    if not labels:
        return None
    return re.compile(r"^\s*(?:" + "|".join(labels) + r")\s+(\d+)\.(\d+)\b")


def chapter_label_regex(style: Style):
    """The chapter label line ("บทที่ 1", "Chapter 1"), as the profile spells it."""
    prefixes = {re.escape(v) for v in (style.labels.get("chapter_label_prefix") or {}).values()
                if v}
    if not prefixes:
        prefixes = {re.escape("บทที่"), re.escape("Chapter")}
    return re.compile(r"^(?:" + "|".join(sorted(prefixes)) + r")\s*\d")


# --------------------------------------------------------------------------------------
def check_page(r: Report, style: Style) -> Result:
    res = Result("page-setup", "Paper size and margins")
    # Tolerate the rounding that comes from writing a rule in centimetres and
    # converting it to twips: 2.5 cm and 2.54 cm are the same instruction.
    margin_tol = mm_to_tw(1.0)
    size_tol = mm_to_tw(1.0)
    want_w, want_h = mm_to_tw(style.page.get("width_mm", 210)), mm_to_tw(
        style.page.get("height_mm", 297))
    want = {
        "top": mm_to_tw(style.page.get("margin_top_mm", 25.4)),
        "bottom": mm_to_tw(style.page.get("margin_bottom_mm", 25.4)),
        "left": mm_to_tw(style.page.get("margin_left_mm", 25.4)),
        "right": mm_to_tw(style.page.get("margin_right_mm", 25.4)),
    }
    sizes = list(r.body.iter(W + "pgSz"))
    margins = list(r.body.iter(W + "pgMar"))
    res.checked = len(sizes) + len(margins)
    if not sizes:
        res.fail("no w:pgSz element found")
    for pg in sizes:
        w, h = _val(pg, "w"), _val(pg, "h")
        if abs(int(w) - want_w) > size_tol or abs(int(h) - want_h) > size_tol:
            res.fail(f"page size {w}x{h} twips does not match the profile "
                     f"({want_w}x{want_h})")
    if not margins:
        res.fail("no w:pgMar element found")
    for m in margins:
        for side, expected in want.items():
            got = _val(m, side)
            if got is None or abs(int(got) - expected) > margin_tol:
                res.fail(f"{side} margin is {got} twips, expected about {expected}")
    return res


def check_fonts(r: Report, style: Style) -> Result:
    res = Result("fonts", f"Only the profile fonts are used ({', '.join(style.allowed_fonts)})")
    allowed = set(style.allowed_fonts)
    docDefaults = r.styles.find(W + "docDefaults")
    rPr = docDefaults.find(W + "rPrDefault") if docDefaults is not None else None
    rPr = rPr.find(W + "rPr") if rPr is not None else None
    rFonts = rPr.find(W + "rFonts") if rPr is not None else None
    if rFonts is None:
        res.fail("the document defaults do not set a font")
    else:
        for slot in ("ascii", "hAnsi", "cs", "eastAsia"):
            value = _val(rFonts, slot)
            if value not in allowed:
                res.fail(f"document default font slot '{slot}' is {value!r}, "
                         f"expected one of {sorted(allowed)}")
    found = set()
    for el in list(r.doc.iter(W + "rFonts")) + list(r.styles.iter(W + "rFonts")):
        for slot in ("ascii", "hAnsi", "cs", "eastAsia"):
            value = _val(el, slot)
            if value:
                found.add(value)
    res.checked = len(found)
    bad = found - allowed
    if bad:
        res.fail(f"the document references fonts outside the profile: {sorted(bad)}")
    return res


def check_run_hints(r: Report, style: Style) -> Result:
    if not style.hint_cs:
        res = Result("script-hint", "Script hint on every run (not required by this style)")
        res.na("this style does not use a complex script")
        return res
    res = Result("script-hint", "Every text run carries w:hint=\"cs\"")
    offenders = []
    total = 0
    for p in r.paragraphs:
        for run in r.runs(p):
            if run.find(W + "t") is None:
                continue
            total += 1
            rPr = run.find(W + "rPr")
            rFonts = rPr.find(W + "rFonts") if rPr is not None else None
            if rFonts is None or _val(rFonts, "hint") != "cs":
                offenders.append(_text_of(run)[:40])
    res.checked = total
    if offenders:
        res.fail(f"{len(offenders)} run(s) without w:hint=\"cs\", e.g. {offenders[:3]}")
    if total == 0:
        res.na("no text runs found")
    return res


def check_alignment(r: Report, style: Style) -> Result:
    res = Result("alignment", f"Body alignment is {style.alignment}")
    forbidden = style.forbidden_alignment
    bad = Counter()
    used = 0
    for p in r.paragraphs:
        jc = r.pjc(p)
        if jc is None:
            continue
        used += 1
        if jc in forbidden:
            bad[jc] += 1
    res.checked = used
    for jc, count in bad.items():
        res.fail(f"{count} paragraph(s) use the forbidden alignment '{jc}'")
    if style.alignment and not forbidden:
        body = [p for p in r.paragraphs
                if r.pjc(p) == style.alignment and _text_of(p).strip()]
        if not body:
            res.warn(f"no paragraph uses the profile alignment '{style.alignment}'")
    return res


def check_body_metrics(r: Report, style: Style) -> Result:
    res = Result("paragraph-metrics", "First-line indent and space after match the profile")
    want_first = style.first_line_tw
    want_after = style.space_after_tw
    offenders_indent, offenders_spacing = [], []
    total = 0
    for p in r.paragraphs:
        if r.pjc(p) != style.alignment or not _text_of(p).strip():
            continue
        total += 1
        ind = r.pind(p)
        first = _val(ind, "firstLine")
        hanging = _val(ind, "hanging")
        left = _val(ind, "left")
        if want_first:
            is_list = hanging is not None and _close(int(left or 0), style.list_left_tw)
            if not (_close(int(first or 0), want_first) or is_list):
                offenders_indent.append(_text_of(p)[:40])
        if want_after:
            sp = r.pspacing(p)
            if not _close(int(_val(sp, "after") or 0), want_after):
                offenders_spacing.append(_text_of(p)[:40])
    res.checked = total
    if offenders_indent:
        res.fail(f"{len(offenders_indent)} body paragraph(s) without a {want_first}-twip "
                 f"first-line indent, e.g. {offenders_indent[:3]}")
    if offenders_spacing:
        res.fail(f"{len(offenders_spacing)} body paragraph(s) without {want_after}-twip "
                 f"space after, e.g. {offenders_spacing[:3]}")
    if total == 0:
        res.na("no body paragraphs found")
    return res


def check_list_indent(r: Report, style: Style) -> Result:
    res = Result("list-indent", "Numbered items use the profile hanging indent")
    if not style.list_left_tw:
        res.na("this style does not indent list items")
        return res
    offenders = []
    total = 0
    for p in r.paragraphs:
        ind = r.pind(p)
        if ind is None or not _close(int(_val(ind, "left") or 0), style.list_left_tw):
            continue
        total += 1
        if not _close(int(_val(ind, "hanging") or 0), style.list_hanging_tw):
            offenders.append(_text_of(p)[:40])
    res.checked = total
    if offenders:
        res.fail(f"{len(offenders)} list paragraph(s) with the wrong hanging indent, "
                 f"e.g. {offenders[:3]}")
    if total == 0:
        res.na("no list paragraphs found")
    return res


def check_heading_styles(r: Report, style: Style) -> Result:
    res = Result("heading-styles", "Real Heading styles carry outline levels")
    for style_id, level in (("Heading1", "0"), ("Heading2", "1"), ("Heading3", "2")):
        found = False
        for st in r.styles.iter(W + "style"):
            if st.get(W + "styleId") == style_id:
                found = True
                pPr = st.find(W + "pPr")
                outline = _val(pPr.find(W + "outlineLvl"), "val") if pPr is not None else None
                if outline != level:
                    res.fail(f"style {style_id} has outlineLvl {outline}, expected {level}")
        if not found:
            res.fail(f"style {style_id} is missing from styles.xml")
    res.checked = 3
    return res


def check_heading_sizes(r: Report, style: Style) -> Result:
    res = Result("heading-sizes", "Heading sizes match the profile")
    want_h1 = str(style.size("chapter_label") * 2)
    want_h2 = str(style.size("h2") * 2)
    want_h3 = str(style.size("h3") * 2)
    h1 = r.style_size("Heading1")
    h2 = r.style_size("Heading2")
    h3 = r.style_size("Heading3")
    res.checked = 3
    if h1 != want_h1:
        res.fail(f"Heading1 style size is {h1} half-points, expected {want_h1}")
    if h2 != want_h2:
        res.fail(f"Heading2 style size is {h2} half-points, expected {want_h2}")
    if h3 is not None and h3 != want_h3:
        res.fail(f"Heading3 style size is {h3} half-points, expected {want_h3}")

    chapter_re = chapter_label_regex(style)
    heads = [p for p in r.paragraphs if r.pstyle(p) == "Heading1"]
    labels = [p for p in heads if chapter_re.match(_text_of(p).strip())]
    titles = []
    for idx, p in enumerate(heads):
        if idx + 1 < len(heads) and heads[idx] in labels:
            titles.append(heads[idx + 1])
    res.checked += len(heads)
    want_label = str(style.size("chapter_label") * 2)
    want_title = str(style.size("chapter_title") * 2)
    for p in labels:
        sizes = {r.run_size(run) for run in r.runs(p)
                 if run.find(W + "t") is not None and r.run_size(run)}
        if sizes and sizes != {want_label}:
            res.fail(f"chapter label {_text_of(p).strip()[:30]!r} uses {sorted(sizes)} "
                     f"half-points, expected {want_label}")
    for p in titles:
        sizes = {r.run_size(run) for run in r.runs(p)
                 if run.find(W + "t") is not None and r.run_size(run)}
        if sizes and sizes != {want_title}:
            res.fail(f"chapter title {_text_of(p).strip()[:30]!r} uses {sorted(sizes)} "
                     f"half-points, expected {want_title}")
    for p in r.paragraphs:
        if r.pstyle(p) == "Heading2":
            sizes = {r.run_size(run) for run in r.runs(p)
                 if run.find(W + "t") is not None and r.run_size(run)}
            if sizes and sizes != {want_h2}:
                res.fail(f"section heading {_text_of(p).strip()[:30]!r} uses {sorted(sizes)} "
                         f"half-points, expected {want_h2}")
        elif r.pstyle(p) == "Heading3":
            sizes = {r.run_size(run) for run in r.runs(p)
                 if run.find(W + "t") is not None and r.run_size(run)}
            if sizes and sizes != {want_h3}:
                res.fail(f"sub-section heading {_text_of(p).strip()[:30]!r} uses "
                         f"{sorted(sizes)} half-points, expected {want_h3}")
    return res


def check_page_numbers(r: Report, style: Style) -> Result:
    res = Result("page-numbers", "Page number centred in the header")
    if not r.headers:
        res.fail("no header part in the document")
        return res
    if "PAGE" not in r.header_xml:
        res.fail("no PAGE field in the header")
    if 'w:val="center"' not in r.header_xml:
        res.fail("the header page number is not centred")
    res.checked = len(r.headers)
    return res


def check_numbering_formats(r: Report, style: Style, mode: str) -> Result:
    res = Result("page-number-formats", "Front matter and body use the profile formats")
    fmts = [_val(n, "fmt") for n in r.body.iter(W + "pgNumType")]
    res.checked = len(fmts)
    want_front = style.numbering.get("front_format")
    want_body = style.numbering.get("body_format")
    if not fmts:
        res.na("no explicit page numbering (single-section document)")
        return res
    if mode == "full" and want_front and want_front not in fmts:
        res.warn(f"no '{want_front}' page numbering found for the front matter")
    if want_body and want_body not in fmts:
        res.warn(f"no '{want_body}' page numbering found for the body")
    return res


def check_toc(r: Report, style: Style, mode: str) -> Result:
    res = Result("contents-field", "The contents page is a real TOC field")
    if mode != "full":
        res.na("the contents page belongs to the assembled book, not to a chapter file")
        return res
    instr = "".join(t.text or "" for t in r.doc.iter(W + "instrText"))
    res.checked = 1
    if "TOC" not in instr:
        res.fail("no TOC field found -- the contents page will not update its page numbers")
    return res


def check_caption_lists(r: Report, style: Style, mode: str) -> Result:
    res = Result("caption-lists", "Every table and figure is listed in the lists")
    instr = "".join(t.text or "" for t in r.doc.iter(W + "instrText"))
    table_re = caption_regex(style, "table")
    figure_re = caption_regex(style, "figure")
    chapter_re = chapter_label_regex(style)
    body_paras = r.body_paragraphs(chapter_re)
    tables = [p for p in body_paras if table_re and table_re.match(_text_of(p))]
    figures = [p for p in body_paras if figure_re and figure_re.match(_text_of(p))]
    res.checked = len(tables) + len(figures)
    if mode == "full":
        if tables and "TableCaption" not in instr:
            res.fail(f"{len(tables)} table caption(s) but no list-of-tables field")
        if figures and "FigureCaption" not in instr:
            res.fail(f"{len(figures)} figure caption(s) but no list-of-figures field")
    else:
        # the lists live in the front matter of the assembled book
        if (tables and "TableCaption" not in instr) or (figures and "FigureCaption" not in instr):
            res.warn("the list-of-tables / list-of-figures field is not in this chapter "
                     "file; it belongs to the assembled book")
    if not tables and not figures:
        res.na("the document contains no table or figure captions")
    return res


def check_caption_placement(r: Report, style: Style) -> Result:
    res = Result("caption-placement", "Captions sit above the object they label")
    children = list(r.body)
    table_re = caption_regex(style, "table")
    figure_re = caption_regex(style, "figure")
    chapter_re = chapter_label_regex(style)
    body_start = r.body_start_index(chapter_re)
    offenders = []
    total = 0
    for idx, el in enumerate(children):
        if el.tag == W + "tbl" and idx >= body_start:
            prev = None
            for j in range(idx - 1, -1, -1):
                if children[j].tag == W + "p" and _text_of(children[j]).strip():
                    prev = children[j]
                    break
            total += 1
            if prev is None or not (table_re and table_re.match(_text_of(prev))):
                offenders.append("body table without a caption directly above it")
        elif el.tag == W + "p" and figure_re and figure_re.match(_text_of(el)):
            total += 1
            found = False
            # Check following paragraphs (caption above)
            for j in range(idx + 1, min(idx + 4, len(children))):
                candidate = children[j]
                if candidate.tag == W + "tbl":
                    found = candidate.find(".//" + W + "drawing") is not None or \
                        candidate.find(".//" + W + "pict") is not None
                elif candidate.tag == W + "p":
                    if candidate.find(".//" + W + "drawing") is not None or \
                            candidate.find(".//" + W + "pict") is not None:
                        found = True
                    elif _text_of(candidate).strip():
                        break
                if found:
                    break
            # Check preceding paragraphs (caption below: [รูปภาพ] then รูปที่ X.Y)
            if not found:
                for j in range(idx - 1, max(-1, idx - 4), -1):
                    candidate = children[j]
                    if candidate.tag == W + "tbl":
                        found = candidate.find(".//" + W + "drawing") is not None or \
                            candidate.find(".//" + W + "pict") is not None
                    elif candidate.tag == W + "p":
                        if candidate.find(".//" + W + "drawing") is not None or \
                                candidate.find(".//" + W + "pict") is not None:
                            found = True
                        elif _text_of(candidate).strip():
                            break
                    if found:
                        break
            if not found:
                offenders.append("figure caption not adjacent to an image")
    res.checked = total
    if offenders:
        res.fail("; ".join(sorted(set(offenders))))
    if total == 0:
        res.na("no tables or figures in the document")
    return res


def check_caption_numbering(r: Report, style: Style) -> Result:
    res = Result("caption-numbering", "Captions are numbered chapter.sequence and never reused")
    table_re = caption_regex(style, "table")
    figure_re = caption_regex(style, "figure")
    seen = {}
    total = 0
    chapter_re = chapter_label_regex(style)
    for p in r.body_paragraphs(chapter_re):
        text = _text_of(p).strip()
        for kind, regex in (("table", table_re), ("figure", figure_re)):
            if not regex:
                continue
            m = regex.match(text)
            if m:
                key = f"{kind} {m.group(1)}.{m.group(2)}"
                seen[key] = seen.get(key, 0) + 1
                total += 1
                break
    offenders = [f"{k} used {v} times" for k, v in seen.items() if v > 1]
    res.checked = total
    if offenders:
        res.fail("; ".join(offenders))
    if total == 0:
        res.na("no captions in the document")
    return res


def check_table_style(r: Report, style: Style) -> Result:
    res = Result("table-style", "Tables use the profile's border style")
    if not style.tables.get("borders", True):
        res.na("this style does not require table borders")
        return res
    if not r.tables:
        res.na("the document contains no tables")
        return res
    res.checked = len(r.tables)
    for idx, tbl in enumerate(r.tables):
        tblPr = tbl.find(W + "tblPr")
        borders = tblPr.find(W + "tblBorders") if tblPr is not None else None
        tbl_style = _val(tblPr.find(W + "tblStyle"), "val") if tblPr is not None else None
        if borders is None and tbl_style != "TableGrid":
            res.fail(f"table {idx + 1} has no explicit borders and no Table Grid style")
            break
    return res


def check_settings(r: Report, style: Style) -> Result:
    res = Result("settings", "settings.xml is schema-valid (applyBreakingRules inside w:compat)")
    res.checked = 1
    compat = r.settings.find(W + "compat")
    if compat is None:
        res.fail("settings.xml has no <w:compat> block")
    elif compat.find(W + "applyBreakingRules") is None:
        res.fail("<w:applyBreakingRules/> must live inside <w:compat>; without it Thai "
                 "text is laid out with Latin rules and the characters scatter")
    if any(child.tag == W + "applyBreakingRules" for child in r.settings):
        res.fail("<w:applyBreakingRules/> sits directly under <w:settings>; the schema "
                 "requires it inside <w:compat>, and Word then refuses document-level "
                 "commands such as repaginating and rebuilding the contents page")
    return res


def check_structure(r: Report, style: Style, mode: str) -> Result:
    res = Result("structure", "Every part of the book is present, in the profile's order")
    if mode != "full":
        res.na("chapter-scoped document")
        return res
    lang = style.raw.get("language", "th")
    text = "\n".join(_text_of(p) for p in r.paragraphs)
    expected = []
    for part in style.front_parts():
        kind = part.get("kind")
        if kind in ("cover", "copyright"):
            continue
        label = style.part_label(kind, part.get("lang", lang))
        if label:
            expected.append((kind, label))
    for part in style.back_parts():
        label = style.part_label(part.get("kind"), lang)
        if label:
            expected.append((part.get("kind"), label))
    res.checked = len(expected)
    missing = [f"{kind} ('{label}')" for kind, label in expected if label not in text]
    if missing:
        res.fail("missing parts: " + ", ".join(missing))
    prefix = style.labels.get("chapter_label_prefix", {})
    for chapter in style.structure.get("chapters", []):
        number = chapter.get("number")
        label = (chapter.get("label") or {}).get(lang) or (chapter.get("label") or {}).get("th") \
            or (chapter.get("label") or {}).get("en") \
            or f"{prefix.get(lang, prefix.get('th', 'Chapter'))} {number}"
        if label not in text:
            res.fail(f"missing chapter {number} ('{label}')")
        res.checked += 1
    breaks = sum(1 for br in r.body.iter(W + "br") if br.get(W + "type") == "page")
    res.checked += 1
    if breaks < len(expected):
        res.warn(f"only {breaks} explicit page breaks found; every part needs one")
    return res


# --------------------------------------------------------------------------------------
def run_checks(report: Report, style: Style, mode: str) -> list:
    return [
        check_page(report, style),
        check_fonts(report, style),
        check_run_hints(report, style),
        check_alignment(report, style),
        check_heading_styles(report, style),
        check_heading_sizes(report, style),
        check_body_metrics(report, style),
        check_list_indent(report, style),
        check_page_numbers(report, style),
        check_numbering_formats(report, style, mode),
        check_toc(report, style, mode),
        check_caption_lists(report, style, mode),
        check_caption_placement(report, style),
        check_caption_numbering(report, style),
        check_table_style(report, style),
        check_settings(report, style),
        check_structure(report, style, mode),
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", help="path to the .docx to check")
    ap.add_argument("--profile", default=None,
                    help="style profile JSON (default: the bundled default profile)")
    ap.add_argument("--mode", default="full", choices=["full", "chapter"])
    ap.add_argument("--json", default=None, help="write machine-readable results here")
    args = ap.parse_args(argv)

    path = Path(args.docx)
    if not path.exists():
        print(f"FAIL  file not found: {path}")
        return 1
    try:
        report = Report(path)
    except (KeyError, zipfile.BadZipFile) as exc:
        print(f"FAIL  cannot read {path}: {exc}")
        return 1

    style = load_profile(Path(args.profile) if args.profile else None)
    results = run_checks(report, style, args.mode)
    failed = [r for r in results if r.status == "FAIL"]

    print(f"Compliance report: {path}")
    print(f"Style profile: {style.raw.get('name', 'custom')}")
    print("=" * 78)
    for res in results:
        marker = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN", "NA": "  - "}[res.status]
        print(f"[{marker}] {res.rule_id:<22} {res.title}")
        for msg in res.messages:
            print(f"         - {msg}")
    print("=" * 78)
    passed = sum(1 for r in results if r.status == "PASS")
    print(f"{passed} passed, {len(failed)} failed, "
          f"{sum(1 for r in results if r.status == 'WARN')} warnings, "
          f"{sum(1 for r in results if r.status == 'NA')} not applicable")

    if args.json:
        payload = {"file": str(path), "mode": args.mode, "profile": style.raw.get("name"),
                   "passed": passed, "failed": len(failed),
                   "results": [r.as_dict() for r in results]}
        Path(args.json).write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
        print(f"machine-readable results -> {args.json}")

    if failed:
        print("RESULT: NOT COMPLIANT -- fix the FAIL items above before submitting.")
        return 1
    print("RESULT: COMPLIANT with the house style rules checked here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
