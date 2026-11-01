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
    def __init__(self, rule_id: str, title: str, rules=None):
        self.rule_id = rule_id
        self.title = title
        self.rules = list(rules or [])
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
        return {"rule_id": self.rule_id, "rules": self.rules, "title": self.title,
                "status": self.status, "checked": self.checked,
                "messages": self.messages}


def _val(el, name, default=None):
    if el is None:
        return default
    return el.get(W + name, default)

def _res(style: Style, check: str, rule_id: str, title: str) -> Result:
    """A Result that carries the house-style rule IDs the check enforces."""
    return Result(rule_id, title, style.rule_ids(check))

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

    def in_table(self, p) -> bool:
        node = p.getparent()
        while node is not None:
            if node.tag == W + "tbl":
                return True
            if node.tag == W + "body":
                return False
            node = node.getparent()
        return False

    def leading_tab(self, p) -> bool:
        """True when the paragraph opens with a tab, the second way of spelling a
        first-line indent (Word writes <w:tab/> as its own run)."""
        for run in p.findall(W + "r"):
            for child in run:
                if child.tag == W + "t":
                    return False
                if child.tag == W + "tab":
                    return True
            if run.find(W + "rPr") is None and len(run) == 0:
                continue
        return False

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


def caption_regex(style: Style, kind: str, appendix: bool = False):
    labels = [style.captions.get(f"{kind}_label"), style.captions.get(f"{kind}_label_en")]
    labels = [re.escape(l) for l in labels if l]
    if not labels:
        return None
    number = r"(ผ|ผ\.|\d+)\.(\d+)" if appendix else r"(\d+)\.(\d+)"
    return re.compile(r"^\s*(?:" + "|".join(labels) + r")\s+" + number + r"\b")


def chapter_label_regex(style: Style):
    """The chapter label line ("บทที่ 1", "Chapter 1"), as the profile spells it."""
    prefixes = {re.escape(v) for v in (style.labels.get("chapter_label_prefix") or {}).values()
                if v}
    if not prefixes:
        prefixes = {re.escape("บทที่"), re.escape("Chapter")}
    return re.compile(r"^(?:" + "|".join(sorted(prefixes)) + r")\s*\d")


# --------------------------------------------------------------------------------------
def check_page(r: Report, style: Style) -> Result:
    res = _res(style, "page-setup", "page-setup", "Paper size and margins")
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
    res = _res(style, "fonts", "fonts", f"Only the profile fonts are used ({', '.join(style.allowed_fonts)})")
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
        res = _res(style, "script-hint", "script-hint",
                "Script hint on every run (not required by this style)")
        res.na("this style does not use a complex script")
        return res
    res = _res(style, "script-hint", "script-hint", "Every text run carries w:hint=\"cs\"")
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
    res = _res(style, "alignment", "alignment", f"Body alignment is {style.alignment}")
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
    res = _res(style, "paragraph-metrics", "paragraph-metrics",
                "First line indent (or leading tab) and space after match the profile")
    want_first = style.first_line_tw
    want_after = style.space_after_tw
    mode = style.first_line_mode
    offenders_indent, offenders_spacing = [], []
    total = 0
    for p in r.paragraphs:
        if r.pjc(p) != style.alignment or not _text_of(p).strip():
            continue
        if (r.pstyle(p) or "").lower().startswith("heading") or r.in_table(p):
            continue
        total += 1
        ind = r.pind(p)
        first = _val(ind, "firstLine")
        hanging = _val(ind, "hanging")
        left = _val(ind, "left")
        if want_first and mode != "tab":
            is_list = (hanging is not None and _close(int(left or 0), style.list_left_tw)) \
                or (r.pstyle(p) or "").startswith("List")
            indented = _close(int(first or 0), want_first) or is_list
            # a leading tab is the other way the same indent is spelled
            if mode == "either" and not indented:
                indented = r.leading_tab(p)
            if not indented:
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
    res = _res(style, "list-indent", "list-indent",
                "Numbered items use the profile hanging indent")
    if not style.list_left_tw:
        res.na("this style does not indent list items")
        return res
    offenders = []
    total = 0
    for p in r.paragraphs:
        if r.in_table(p):
            continue
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
    res = _res(style, "heading-styles", "heading-styles",
                "Real Heading styles carry outline levels")
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
    res = _res(style, "heading-sizes", "heading-sizes", "Heading sizes match the profile")
    want_h1 = str(style.size("chapter_label") * 2)
    want_h2 = str(style.size("h2") * 2)
    want_h3 = str(style.size("h3") * 2)
    h1 = r.style_size("Heading1")
    h2 = r.style_size("Heading2")
    h3 = r.style_size("Heading3")
    chapter_re = chapter_label_regex(style)
    heads = [p for p in r.paragraphs if r.pstyle(p) == "Heading1"]
    labels = [p for p in heads if chapter_re.match(_text_of(p).strip())]

    want_front = str(style.size("front_heading") * 2)
    if not labels:
        # A front-matter sheet (abstract, acknowledgements, contents): the heading
        # is the front-matter heading, not a chapter label.
        res.checked = len(heads)
        for p in heads:
            sizes = {r.run_size(run) for run in r.runs(p)
                     if run.find(W + "t") is not None and r.run_size(run)}
            if sizes and sizes != {want_front}:
                res.fail(f"front-matter heading {_text_of(p).strip()[:30]!r} uses "
                         f"{sorted(sizes)} half-points, expected {want_front} (R-09)")
        if not heads:
            res.na("no Heading 1 paragraph in this document")
        return res

    res.checked = 3
    if h1 != want_h1:
        res.fail(f"Heading1 style size is {h1} half-points, expected {want_h1} "
                 f"(the style is what a re-typed heading inherits)")
    if h2 != want_h2:
        res.fail(f"Heading2 style size is {h2} half-points, expected {want_h2}")
    if h3 is not None and h3 != want_h3:
        res.fail(f"Heading3 style size is {h3} half-points, expected {want_h3}")
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


def check_heading_separator(r: Report, style: Style) -> Result:
    """'3.1' and its title are separated by a tab (the book) or a space."""
    want = style.headings.get("separator_between_number_and_title", " ").strip().lower()
    res = _res(style, "heading-separator", "heading-separator",
                f"Number and title in a section heading are separated by a {want}")
    offenders = []
    total = 0
    for p in r.paragraphs:
        if r.pstyle(p) not in ("Heading2", "Heading3"):
            continue
        runs = [run for run in p.findall(W + "r")
                if run.find(W + "t") is not None or run.find(W + "tab") is not None]
        if not runs:
            continue
        first = _text_of(runs[0]).strip()
        if not re.match(r"^\d+(\.\d+)+$", first):
            continue
        total += 1
        # The tab may be in a run of its own, so scan forward until the title text.
        has_tab = False
        for run in runs[1:]:
            if run.find(W + "tab") is not None:
                has_tab = True
                break
            if run.find(W + "t") is not None:
                break
        if want == "tab" and not has_tab:
            offenders.append(_text_of(p)[:40])
        elif want == "space" and has_tab:
            offenders.append(_text_of(p)[:40])
    res.checked = total
    if offenders:
        res.fail(f"{len(offenders)} section heading(s) do not separate the number and "
                 f"the title with a {want}, e.g. {offenders[:3]}")
    if total == 0:
        res.na("no numbered section headings in this document")
    return res


def check_page_numbers(r: Report, style: Style) -> Result:
    res = _res(style, "page-numbers", "page-numbers",
                f"Page number in the header, {style.numbering.get('alignment', 'center')} aligned")
    want_align = style.numbering.get("alignment", "center")
    if not r.headers:
        res.fail("no header part in the document")
        return res
    if "PAGE" not in r.header_xml:
        res.fail("no PAGE field in the header")
    if f'w:val="{want_align}"' not in r.header_xml:
        got = sorted(set(re.findall(r'w:jc w:val="(\w+)"', r.header_xml)))
        res.fail(f"the header page number is not {want_align} aligned "
                 f"(header uses {got or 'no w:jc'})")
    res.checked = len(r.headers)
    return res


def check_footer(r: Report, style: Style) -> Result:
    res = _res(style, "footer", "footer", f"Every page carries the footer '{style.footer_text}'")
    # A cover file may legitimately carry its own marking; accept
    # any footer the profile lists for a part, and require the default on the rest.
    texts_ok = [style.footer_text] + [str(v) for v in (style.footer.get("by_part") or {}).values() if v]
    want = style.footer_text
    if not want:
        res.na("this style has no running footer")
        return res
    footers = [n for n in r.names if re.match(r"word/footer\d*\.xml$", n)]
    if not footers:
        res.fail("no footer part in the document")
        return res
    res.checked = len(footers)
    texts = {}
    for name in footers:
        xml = r.zf.read(name).decode("utf-8", "replace")
        root = etree.fromstring(xml.encode("utf-8"))
        body = "\n".join(_text_of(p).strip() for p in root.iter(W + "p"))
        texts[name] = body
    missing = [n for n, body in texts.items()
               if not any(t in body for t in texts_ok)]
    if missing:
        res.fail(f"{len(missing)} footer part(s) without '{want}': {sorted(missing)[:3]}")
    size_pt, align = style.footer_geometry()
    wrong = []
    for name in footers:
        root = etree.fromstring(r.zf.read(name))
        for p in root.iter(W + "p"):
            if want not in _text_of(p):
                continue
            for run in p.findall(W + "r"):
                sz = r.run_size(run)
                if sz and sz != str(size_pt * 2):
                    wrong.append(f"{name}: {sz} half-points")
                    break
    if wrong:
        res.warn(f"footer text is not {size_pt} pt in {sorted(set(wrong))[:3]}")
    return res


def check_numbering_formats(r: Report, style: Style, mode: str) -> Result:
    res = _res(style, "page-number-formats", "page-number-formats",
                "Front matter and body use the profile formats")
    fmts = [_val(n, "fmt") for n in r.body.iter(W + "pgNumType")]
    res.checked = len(fmts)
    want_front = style.numbering.get("front_format")
    want_body = style.numbering.get("body_format")
    if not fmts:
        res.na("no explicit page numbering (single-section document)")
        return res
    if mode == "full" and want_front and want_front not in fmts:
        res.warn(f"no '{want_front}' page numbering found for the front matter")
    has_chapter = any(chapter_label_regex(style).match(_text_of(p).strip())
                      for p in r.paragraphs)
    if want_body and want_body not in fmts and has_chapter:
        res.warn(f"no '{want_body}' page numbering found for the body")
    return res


def check_toc(r: Report, style: Style, mode: str) -> Result:
    res = _res(style, "contents-field", "contents-field",
                "The contents page is a real TOC field")
    if mode != "full":
        res.na("the contents page belongs to the assembled book, not to a chapter file")
        return res
    instr = "".join(t.text or "" for t in r.doc.iter(W + "instrText"))
    res.checked = 1
    if "TOC" not in instr:
        res.fail("no TOC field found -- the contents page will not update its page numbers")
    return res


def check_caption_lists(r: Report, style: Style, mode: str) -> Result:
    res = _res(style, "caption-lists", "caption-lists",
                "Every table and figure is listed in the lists")
    instr = "".join(t.text or "" for t in r.doc.iter(W + "instrText"))
    table_re = caption_regex(style, "table", appendix=True)
    figure_re = caption_regex(style, "figure", appendix=True)
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
    res = _res(style, "caption-placement", "caption-placement",
                "Captions sit where the profile puts them relative to the object")
    children = list(r.body)
    table_re = caption_regex(style, "table", appendix=True)
    figure_re = caption_regex(style, "figure", appendix=True)
    chapter_re = chapter_label_regex(style)
    body_start = r.body_start_index(chapter_re)
    table_want = style.caption_placement("table")
    offenders = []
    total = 0
    for idx, el in enumerate(children):
        if el.tag == W + "tbl" and idx >= body_start:
            span = (range(idx - 1, -1, -1) if table_want == "above"
                    else range(idx + 1, min(idx + 4, len(children))))
            neighbour = None
            for j in span:
                if children[j].tag == W + "p" and _text_of(children[j]).strip():
                    neighbour = children[j]
                    break
            total += 1
            if neighbour is None or not (table_re and table_re.match(_text_of(neighbour))):
                offenders.append(f"body table without a caption directly {table_want} it")
        elif el.tag == W + "p" and figure_re and figure_re.match(_text_of(el)):
            total += 1
            want = style.caption_placement("figure")

            def image_within(step):
                """Walk away from the caption until an image or a real paragraph."""
                j = idx + step
                while 0 <= j < len(children) and abs(j - idx) <= 3:
                    candidate = children[j]
                    if candidate.find(".//" + W + "drawing") is not None or \
                            candidate.find(".//" + W + "pict") is not None:
                        return True
                    if candidate.tag == W + "p" and _text_of(candidate).strip():
                        return False
                    j += step
                return False

            seen_above = image_within(+1)
            seen_below = image_within(-1)
            found = seen_above if want == "above" else seen_below
            if not found and (seen_above or seen_below):
                offenders.append(f"figure caption sits "
                                 f"{'below' if seen_below else 'above'} while the profile "
                                 f"puts it {want} the image")
            elif not found:
                offenders.append("figure caption not adjacent to an image")
    res.checked = total
    if offenders:
        res.fail("; ".join(sorted(set(offenders))))
    if total == 0:
        res.na("no tables or figures in the document")
    return res


def check_caption_numbering(r: Report, style: Style) -> Result:
    res = _res(style, "caption-numbering", "caption-numbering",
                "Captions are numbered chapter.sequence, in order, and never reused")
    table_re = caption_regex(style, "table", appendix=True)
    figure_re = caption_regex(style, "figure", appendix=True)
    seen = {}
    order = []
    total = 0
    chapter_re = chapter_label_regex(style)
    for p in r.body_paragraphs(chapter_re):
        text = _text_of(p).strip()
        for kind, regex in (("table", table_re), ("figure", figure_re)):
            if not regex:
                continue
            m = regex.match(text)
            if m:
                chapter, seq = m.group(1), int(m.group(2))
                key = f"{kind} {chapter}.{seq}"
                seen[key] = seen.get(key, 0) + 1
                total += 1
                # A table that spills onto the next page repeats its caption with
                # " (ต่อ)" - that is not a second object and not a reused number.
                continuation = "ต่อ)" in text or "(cont" in text.lower()
                if chapter.isdigit() and not continuation:
                    order.append((kind, int(chapter), seq))
                break
    offenders = []
    # A caption repeated verbatim is a continuation ("(ต่อ)" pages repeat it with
    # that marker, so only exact repeats count as a duplicate number).
    plain = {}
    for p in r.body_paragraphs(chapter_re):
        text = _text_of(p).strip()
        if "ต่อ)" in text:
            continue
        for kind, regex in (("table", table_re), ("figure", figure_re)):
            if regex and regex.match(text):
                key = f"{kind} {regex.match(text).group(1)}.{regex.match(text).group(2)}"
                plain[key] = plain.get(key, 0) + 1
                break
    offenders = [f"{k} used {v} times" for k, v in plain.items() if v > 1]
    # R-47/R-50: numbers run 1..n inside each chapter, in document order.
    for kind in ("table", "figure"):
        per_chapter = {}
        for k, chapter, seq in order:
            if k == kind:
                per_chapter.setdefault(chapter, []).append(seq)
        for chapter, seqs in per_chapter.items():
            if seqs != list(range(1, len(seqs) + 1)):
                offenders.append(f"chapter {chapter} {kind} numbers are {seqs}, "
                                 f"expected 1..{len(seqs)} in order")
    res.checked = total
    if offenders:
        res.fail("; ".join(offenders))
    if total == 0:
        res.na("no captions in the document")
    return res


def check_table_style(r: Report, style: Style) -> Result:
    res = _res(style, "table-style", "table-style", "Tables use the profile's border style")
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
    res = _res(style, "settings", "settings",
                "settings.xml is schema-valid (applyBreakingRules inside w:compat)")
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
    res = _res(style, "structure", "structure",
                "Every part of the book is present, in the profile's order")
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
def _section_texts(r: Report) -> list:
    """(number, title) of every Heading 2 paragraph, in document order."""
    out = []
    for p in r.paragraphs:
        if r.pstyle(p) != "Heading2":
            continue
        text = _text_of(p).strip()
        m = re.match(r"^(\d+(?:\.\d+)*)\s*(.*)$", text)
        if m:
            out.append((m.group(1), m.group(2).strip()))
        elif text:
            out.append(("", text))
    return out


def check_chapter_sections(r: Report, style: Style, mode: str) -> Result:
    res = _res(style, "chapter-sections", "chapter-sections",
                "Each chapter carries the sections the profile prescribes")
    sections = _section_texts(r)
    chapters = [c for c in style.structure.get("chapters", []) if c.get("sections")]
    if not chapters:
        res.na("the profile prescribes no chapter sections")
        return res
    res.checked = 0
    for chapter in chapters:
        number = chapter.get("number")
        want = [s.get("number") for s in chapter.get("sections") or []]
        if mode == "chapter":
            # A single chapter file: only judge the chapter whose sections this is.
            if not any(text.startswith(str(number) + ".") for text, _ in sections):
                continue
        got = [n for n, _ in sections if n.startswith(str(number) + ".")]
        res.checked += len(want)
        missing = [n for n in want if n not in got]
        if missing:
            res.warn(f"chapter {number} does not use section(s) {missing} from the "
                     f"delivered structure; R-39a/64 allow a chapter to reshuffle its "
                     f"sections, so confirm the omission is intended")
    if res.checked == 0:
        res.na("no chapter of this document has a prescribed section list")
    return res


def check_last_section(r: Report, style: Style) -> Result:
    res = _res(style, "chapter-sections", "last-section",
                "Chapter 2 ends with the related-work section (R-40)")
    sections = _section_texts(r)
    rules = [(c, [k for k in c.get("last_section_keywords") or []])
             for c in style.structure.get("chapters", [])
             if c.get("last_section_keywords")]
    if not rules:
        res.na("the profile prescribes no closing section")
        return res
    res.checked = 0
    for chapter, keywords in rules:
        own = [(n, t) for n, t in sections if n.startswith(str(chapter.get("number")) + ".")]
        if not own:
            continue
        res.checked += 1
        last = own[-1][1]
        if not any(k in last for k in keywords):
            res.fail(f"chapter {chapter.get('number')} ends with '{last}', but the last "
                     f"section must mention {keywords}")
    if res.checked == 0:
        res.na("this document does not contain the chapter that needs a closing section")
    return res


def check_keywords(r: Report, style: Style) -> Result:
    res = _res(style, "keywords", "keywords", "The keywords line has 4-6 terms")
    found = 0
    total = 0
    for p in r.paragraphs:
        text = _text_of(p).strip()
        for lang, rule in (("th", style.keyword_rule("th")), ("en", style.keyword_rule("en"))):
            label = rule["label"]
            if not label or not text.startswith(label):
                continue
            found += 1
            body = text[len(label):].strip()
            sep = rule["separator"]
            terms = [t for t in (body.split(sep) if sep.strip() else body.split()) if t.strip()]
            total += len(terms)
            if not (rule["min"] <= len(terms) <= rule["max"]):
                res.fail(f"{lang} keywords: {len(terms)} term(s), expected "
                         f"{rule['min']}-{rule['max']}: {terms}")
            if lang == "th" and sep == " " and re.search(r"\s{2,}", body):
                res.fail("Thai keywords are separated by more than one space (R-31)")
    res.checked = found
    if not found:
        res.na("no keywords line in this document")
    return res


def check_caption_alignment(r: Report, style: Style) -> Result:
    res = _res(style, "caption-alignment", "caption-alignment",
                "Captions and table text use the profile's size and alignment")
    want_size = str(style.size("caption") * 2)
    sizes, jcs = [], []
    table_re = caption_regex(style, "table", appendix=True)
    figure_re = caption_regex(style, "figure", appendix=True)
    for p in r.paragraphs:
        text = _text_of(p).strip()
        kind = None
        for k, regex in (("table", table_re), ("figure", figure_re)):
            if regex and regex.match(text):
                kind = k
                break
        if not kind:
            continue
        sizes.append((text[:30], r.pjc(p), style.caption_alignment(kind)))
    res.checked = len(sizes)
    if not sizes:
        res.na("no captions in the document")
        return res
    if style.captions.get("bold"):
        not_bold = []
        for p in r.paragraphs:
            text = _text_of(p).strip()
            if not (table_re and table_re.match(text)):
                continue
            bold = any(run.find(W + "rPr") is not None
                       and run.find(W + "rPr").find(W + "b") is not None
                       for run in r.runs(p) if run.find(W + "t") is not None)
            if not bold:
                not_bold.append(text)
        if not_bold:
            res.fail(f"{len(not_bold)} table caption(s) are not bold, "
                     f"e.g. {not_bold[0][:50]!r}")
    run_sizes = set()
    for p in r.paragraphs:
        if table_re and table_re.match(_text_of(p).strip()):
            for run in r.runs(p):
                if r.run_size(run):
                    run_sizes.add(r.run_size(run))
    if run_sizes and run_sizes != {want_size}:
        res.fail(f"table captions carry {sorted(run_sizes)} half-points, "
                 f"expected {want_size} (P-12/P-13)")
    return res


def check_references(r: Report, style: Style) -> Result:
    res = _res(style, "references", "references",
                f"The reference list is headed '{style.label('references', 'th')}' and is numbered")
    heading = style.label("references", "th")
    texts = [_text_of(p).strip() for p in r.paragraphs]
    if heading not in texts:
        res.na(f"no '{heading}' heading in this document")
        return res
    idx = texts.index(heading)
    entries = []
    for p in r.paragraphs[idx + 1:]:
        style_id = r.pstyle(p) or ""
        text = _text_of(p).strip()
        if style_id.startswith("Heading"):
            break           # the next heading closes the reference list
        if text:
            entries.append(text)
    res.checked = len(entries)
    if not entries:
        res.fail(f"'{heading}' is followed by no entries")
        return res
    unnumbered = [e for e in entries if not re.match(r"^\[\d+\]", e)]
    if unnumbered:
        res.warn(f"{len(unnumbered)} reference(s) without a [n] label, "
                 f"e.g. {unnumbered[0][:60]!r}")
    return res


def check_appendix(r: Report, style: Style) -> Result:
    res = _res(style, "appendix", "appendix",
                f"Appendices are headed '{style.label('appendix', 'th')}' and numbered with "
                f"the profile prefix")
    prefix = style.captions.get("appendix_prefix") or "ผ."
    sep = r"\s*" if prefix.endswith(".") else r"\s*"
    heading = style.label("appendix", "th")
    # A table-of-contents entry also says "ภาคผนวก"; only a real heading opens one.
    is_heading = any((r.pstyle(p) or "").startswith("Heading")
                     and _text_of(p).strip().startswith(heading) for p in r.paragraphs)
    if not is_heading:
        res.na("no appendix in this document")
        return res
    texts = [_text_of(p).strip() for p in r.paragraphs]
    res.checked = 1
    numbered = [t for t in texts
                if re.search(rf"(?:ตารางที่|รูปที่)\s*{re.escape(prefix)}{sep}\d+", t)]
    if not numbered:
        res.fail(f"appendix objects are not numbered '{prefix}' "
                 f"(expected e.g. 'ตารางที่ {prefix}1')")
    res.checked += len(numbered)
    return res


def check_biography(r: Report, style: Style) -> Result:
    res = _res(style, "biography", "biography",
                "The author biography carries the seven required fields (R-60)")
    heading = style.label("biography", "th")
    texts = [_text_of(p).strip() for p in r.paragraphs]
    if heading not in texts:
        res.na("no author biography in this document")
        return res
    idx = texts.index(heading)
    body = "\n".join(texts[idx + 1:])
    fields = ["ชื่อ", "สาขา", "เกิด", "ที่อยู่", "ประวัติการศึกษา"]
    res.checked = len(fields)
    missing = [f for f in fields if f not in body]
    if missing:
        res.warn(f"biography may be missing: {missing} (R-60 asks for name, birth date, "
                 f"address, education, scholarship and publications)")
    return res


def check_rule_deltas(r: Report, style: Style) -> Result:
    """Surface the places where the written rules and the delivered files disagree."""
    res = Result("rule-deltas", "Known differences between the rules and this project",
                 [style.rules_authoritative] if style.rules_authoritative else [])
    if not style.rule_deltas:
        res.na("this profile records no rules-vs-files differences")
        return res
    res.checked = len(style.rule_deltas)
    for delta in style.rule_deltas:
        res.warn(f"{delta.get('rule')} {delta.get('item')}: rule says "
                 f"{delta.get('stated')}; the book has {delta.get('in_book')} "
                 f"-> {delta.get('decision')}")
    return res


def run_checks(report: Report, style: Style, mode: str) -> list:
    return [
        check_page(report, style),
        check_fonts(report, style),
        check_run_hints(report, style),
        check_alignment(report, style),
        check_heading_styles(report, style),
        check_heading_sizes(report, style),
        check_heading_separator(report, style),
        check_body_metrics(report, style),
        check_list_indent(report, style),
        check_page_numbers(report, style),
        check_footer(report, style),
        check_numbering_formats(report, style, mode),
        check_toc(report, style, mode),
        check_caption_lists(report, style, mode),
        check_caption_placement(report, style),
        check_caption_numbering(report, style),
        check_caption_alignment(report, style),
        check_chapter_sections(report, style, mode),
        check_last_section(report, style),
        check_keywords(report, style),
        check_references(report, style),
        check_appendix(report, style),
        check_biography(report, style),
        check_table_style(report, style),
        check_settings(report, style),
        check_structure(report, style, mode),
        check_rule_deltas(report, style),
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
        rules = f"  [{', '.join(res.rules)}]" if res.rules else ""
        print(f"[{marker}] {res.rule_id:<22} {res.title}{rules}")
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
