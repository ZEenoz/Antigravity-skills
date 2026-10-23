#!/usr/bin/env python3
"""
build_report.py -- render a thesis / co-op report (.docx) from a content spec,
applying a house-style profile.

The profile (a JSON file) carries every style decision: page setup, fonts and sizes,
paragraph metrics, caption rules, page numbering, the order of the book's parts and
the labels used for them. The bundled assets/default_profile.json is one instance
(the Thai KMITL Faculty of Science style); scripts/inspect_docx.py can derive a
profile from any reference document, so the same builder serves any project.

Why a builder instead of hand-written python-docx calls:
  * Word only breaks Thai when every run carries w:hint="cs" and the document carries
    <w:applyBreakingRules/> inside <w:compat>. Forgetting either one leaves Thai text
    scattered across the line while the XML still looks plausible.
  * A heading style can silently re-point the font at the theme font, so the font and
    size have to be written on the run itself.
  * A style that is applied by hand drifts; a style that is applied by a script can be
    checked by a script.

Usage:
    python build_report.py --spec spec.json --out Report.docx [--profile p.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_HEADER_FOOTER, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.section import _Header
from docx.shared import Mm, Pt

from profile import DEFAULT_PROFILE, Style, load_profile

HERE = Path(__file__).resolve().parent
DEFAULT_PROFILE = HERE.parent / "assets" / "default_profile.json"
DEFAULT_MASTER = HERE.parent / "assets" / "neutral_master.docx"

# --------------------------------------------------------------------------------------
# OOXML helpers
# --------------------------------------------------------------------------------------
def _el(tag: str, **attrs) -> OxmlElement:
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn("w:" + k), str(v))
    return e


def _pPr(p):
    return p._p.get_or_add_pPr()


def set_jc(p, value: str) -> None:
    """Alignment values such as thaiDistribute have no python-docx enum."""
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY  # guarantees a correctly placed w:jc
    jc = _pPr(p).find(qn("w:jc"))
    if jc is None:
        jc = _el("w:jc")
        _pPr(p).append(jc)
    jc.set(qn("w:val"), value)


def set_ind_first_line(p, twips: int) -> None:
    p.paragraph_format.first_line_indent = Pt(twips / 20.0)


def set_ind_list(p, left_tw: int, hanging_tw: int) -> None:
    p.paragraph_format.left_indent = Pt(left_tw / 20.0)
    p.paragraph_format.first_line_indent = Pt(-hanging_tw / 20.0)


def set_spacing(p, style: Style, before_tw=None, after_tw=None) -> None:
    pf = p.paragraph_format
    if before_tw is not None:
        pf.space_before = Pt(before_tw / 20.0)
    if after_tw is not None:
        pf.space_after = Pt(after_tw / 20.0)
    if style.line_tw == 240:
        pf.line_spacing = 1.0
    else:
        pf.line_spacing = Pt(style.line_tw / 20.0)


def house_run(run, style: Style, size_pt: int = None, bold: bool = False,
              italic: bool = False):
    """Explicit font, explicit size and the script hint on every run.

    The size default and the complex-script attributes matter: Thai is a complex
    script, so w:bCs and w:szCs decide whether bold and size actually apply.
    """
    if size_pt is None:
        size_pt = style.size("body")
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = _el("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
        rFonts.set(qn("w:" + attr), style.font)
    if style.hint_cs:
        rFonts.set(qn("w:hint"), "cs")
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    for tag, on in (("w:bCs", bold), ("w:iCs", italic)):
        node = rPr.find(qn(tag))
        if on and node is None:
            rPr.append(_el(tag))
        elif not on and node is not None:
            rPr.remove(node)
    szCs = rPr.find(qn("w:szCs"))
    if szCs is None:
        szCs = _el("w:szCs")
        rPr.append(szCs)
    szCs.set(qn("w:val"), str(int(size_pt * 2)))
    return run


def add_field(paragraph, instruction: str, placeholder: str = "", style: Style = None):
    """Insert a Word field (TOC, PAGE, ...) as begin/instrText/separate/end runs."""
    for kind, payload in (("begin", None), ("instr", instruction),
                          ("separate", None), ("text", placeholder), ("end", None)):
        run = paragraph.add_run()
        house_run(run, style) if style else run
        if kind == "instr":
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = payload
            run._element.append(instr)
        elif kind == "text":
            run.text = payload
        else:
            run._element.append(_el("w:fldChar", fldCharType=kind))


# --------------------------------------------------------------------------------------
# Document-level style pass
# --------------------------------------------------------------------------------------
def ensure_settings(doc, style: Style) -> None:
    """CT_Settings and CT_Compat are ordered sequences: an element appended in the
    wrong place makes the package schema-invalid, and Word then refuses document-level
    commands such as repaginating and rebuilding the contents page."""
    settings = doc.settings.element

    compat = settings.find(qn("w:compat"))
    if compat is None:
        compat = _el("w:compat")
        settings.append(compat)
    if compat.find(qn("w:applyBreakingRules")) is None:
        br = _el("w:applyBreakingRules")
        first_setting = compat.find(qn("w:compatSetting"))
        if first_setting is not None:
            first_setting.addprevious(br)
        else:
            compat.append(br)

    if settings.find(qn("w:themeFontLang")) is None:
        tfl = _el("w:themeFontLang", val="en-US", eastAsia="th-TH", bidi="th-TH")
        anchor = None
        for tag in ("w:clrSchemeMapping", "w:doNotIncludeSubdocsInStats",
                    "w:doNotAutoCompressPictures", "w:forceUpgrade", "w:captions",
                    "w:readModeInkLockDown", "w:smartTagType", "w:schemaLibrary",
                    "w:shapeDefaults", "w:doNotEmbedSmartTags", "w:decimalSymbol",
                    "w:listSeparator"):
            found = settings.find(qn(tag))
            if found is not None:
                anchor = found
                break
        if anchor is None:
            settings.append(tfl)
        else:
            anchor.addprevious(tfl)


def set_doc_defaults(doc, style: Style) -> None:
    styles = doc.styles.element
    docDefaults = styles.find(qn("w:docDefaults"))
    if docDefaults is None:
        docDefaults = _el("w:docDefaults")
        styles.insert(0, docDefaults)
    rPrDefault = docDefaults.find(qn("w:rPrDefault"))
    if rPrDefault is None:
        rPrDefault = _el("w:rPrDefault")
        docDefaults.append(rPrDefault)
    rPr = rPrDefault.find(qn("w:rPr"))
    if rPr is None:
        rPr = _el("w:rPr")
        rPrDefault.append(rPr)
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = _el("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
        rFonts.set(qn("w:" + attr), style.font)
    if style.hint_cs:
        rFonts.set(qn("w:hint"), "cs")
    for tag in ("w:sz", "w:szCs"):
        node = rPr.find(qn(tag))
        if node is None:
            node = _el(tag)
            rPr.append(node)
        node.set(qn("w:val"), str(style.size("body") * 2))


def force_style_font(style_obj, font: str, size_pt: int, bold: bool,
                      hint_cs: bool) -> None:
    rPr = style_obj.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = _el("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        if rFonts.get(qn("w:" + attr)) is not None:
            del rFonts.attrib[qn("w:" + attr)]
    for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
        rFonts.set(qn("w:" + attr), font)
    if hint_cs:
        rFonts.set(qn("w:hint"), "cs")
    for tag, on in (("w:b", bold), ("w:bCs", bold)):
        node = rPr.find(qn(tag))
        if on and node is None:
            rPr.append(_el(tag))
        elif not on and node is not None:
            rPr.remove(node)
    for tag in ("w:sz", "w:szCs"):
        node = rPr.find(qn(tag))
        if node is None:
            node = _el(tag)
            rPr.append(node)
        node.set(qn("w:val"), str(int(size_pt * 2)))


def normalize_style_fonts(doc, style: Style) -> None:
    """Any style that still points at a theme font or a foreign family would
    re-introduce that font the moment it is used."""
    for st in doc.styles.element.iter(qn("w:style")):
        rPr = st.find(qn("w:rPr"))
        if rPr is None:
            continue
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            continue
        for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
            if rFonts.get(qn("w:" + attr)) is not None:
                del rFonts.attrib[qn("w:" + attr)]
        for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
            rFonts.set(qn("w:" + attr), style.font)
        if style.hint_cs:
            rFonts.set(qn("w:hint"), "cs")


def apply_house_styles(doc, style: Style) -> None:
    """Keep the real Heading styles (the contents field needs their outline levels)
    but force the font and size instead of inheriting them."""
    ensure_settings(doc, style)
    set_doc_defaults(doc, style)
    normalize_style_fonts(doc, style)

    specs = {
        "Heading 1": (style.size("chapter_label"), True),
        "Heading 2": (style.size("h2"), True),
        "Heading 3": (style.size("h3"), True),
        "Heading 4": (style.size("h3"), True),
    }
    for name, (size, bold) in specs.items():
        try:
            st = doc.styles[name]
        except KeyError:
            continue
        force_style_font(st, style.font, size, bold, style.hint_cs)
        pf = st.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.space_before = Pt(12)
        pf.space_after = Pt(6)
        pf.keep_with_next = True

    normal = doc.styles["Normal"]
    force_style_font(normal, style.font, style.size("body"), False, style.hint_cs)
    normal.paragraph_format.space_after = Pt(style.space_after_tw / 20.0)
    normal.paragraph_format.line_spacing = 1.0


def configure_page(section, style: Style) -> None:
    page = style.page
    section.page_width = Mm(page.get("width_mm", 210.0))
    section.page_height = Mm(page.get("height_mm", 297.0))
    section.top_margin = Mm(page.get("margin_top_mm", 25.4))
    section.bottom_margin = Mm(page.get("margin_bottom_mm", 25.4))
    section.left_margin = Mm(page.get("margin_left_mm", 25.4))
    section.right_margin = Mm(page.get("margin_right_mm", 25.4))
    section.header_distance = Mm(page.get("header_mm", 12.7))
    section.footer_distance = Mm(page.get("footer_mm", 12.7))
    section.gutter = Mm(page.get("gutter_mm", 0.0))


def set_page_numbering(section, fmt: str, start=None) -> None:
    sectPr = section._sectPr
    existing = sectPr.find(qn("w:pgNumType"))
    if existing is not None:
        sectPr.remove(existing)
    node = _el("w:pgNumType", fmt=fmt)
    if start is not None:
        node.set(qn("w:start"), str(start))
    anchor = None
    for tag in ("w:cols", "w:formProt", "w:vAlign", "w:noEndnote", "w:titlePg",
                "w:textDirection", "w:bidi", "w:rtlGutter", "w:docGrid"):
        found = sectPr.find(qn(tag))
        if found is not None:
            anchor = found
            break
    if anchor is None:
        sectPr.append(node)
    else:
        anchor.addprevious(node)


def fresh_header(section):
    """Give this section its own header part.

    A section break copies the previous section's headerReference, so two sections
    share one header part and the cover page inherits the body's page number.
    """
    sectPr = section._sectPr
    for ref in sectPr.findall(qn("w:headerReference")):
        if ref.get(qn("w:type")) == "default":
            sectPr.remove(ref)
    header_part, rId = section._document_part.add_header_part()
    sectPr.add_headerReference(WD_HEADER_FOOTER.PRIMARY, rId)
    return _Header(sectPr, section._document_part, WD_HEADER_FOOTER.PRIMARY)


def build_header(section, style: Style, with_page_number: bool = True) -> None:
    header = fresh_header(section)
    p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.text = ""
    set_jc(p, style.numbering.get("alignment", "center"))
    set_spacing(p, style, before_tw=0, after_tw=0)
    if with_page_number:
        add_field(p, " PAGE ", "1", style)


def clear_header(section) -> None:
    header = fresh_header(section)
    for p in header.paragraphs:
        for r in list(p.runs):
            r._element.getparent().remove(r._element)


# --------------------------------------------------------------------------------------
# Content emitters
# --------------------------------------------------------------------------------------
def para(doc, style: Style, text: str = "", *, size=None, bold=False, italic=False,
         jc=None, first_line=None, before=None, after=None, heading_style=None):
    p = doc.add_paragraph()
    if heading_style:
        try:
            p.style = doc.styles[heading_style]
        except KeyError:
            pass
    set_jc(p, jc or style.alignment)
    set_spacing(p, style, before_tw=before, after_tw=style.space_after_tw if after is None
                else after)
    if first_line is None:
        first_line = style.first_line_tw > 0
    if first_line:
        set_ind_first_line(p, style.first_line_tw)
    if text:
        house_run(p.add_run(text), style, size, bold, italic)
    return p


def heading(doc, style: Style, level: int, text: str, *, size=None, jc="left",
            before=None, after=None):
    p = doc.add_paragraph()
    try:
        p.style = doc.styles[f"Heading {level}"]
    except KeyError:
        pass
    set_jc(p, jc)
    set_spacing(p, style, before_tw=before, after_tw=style.space_after_tw if after is None
                else after)
    key = {1: "chapter_label", 2: "h2", 3: "h3", 4: "h3"}[level]
    house_run(p.add_run(text), style, size or style.size(key), True)
    return p


def page_break(doc, style: Style) -> None:
    p = doc.add_paragraph()
    set_spacing(p, style, before_tw=0, after_tw=0)
    house_run(p.add_run(), style).add_break(WD_BREAK.PAGE)


def caption(doc, style: Style, text: str, *, before: int, after: int):
    p = doc.add_paragraph()
    set_jc(p, style.captions.get("alignment", "center"))
    set_spacing(p, style, before_tw=before, after_tw=after)
    house_run(p.add_run(text), style, style.size("caption"))
    return p


def source_note(doc, style: Style, text: str):
    p = doc.add_paragraph()
    set_jc(p, style.alignment)
    set_spacing(p, style, before_tw=0, after_tw=style.space_after_tw)
    if style.first_line_tw:
        set_ind_first_line(p, style.first_line_tw)
    house_run(p.add_run(text), style)
    return p


def set_table_borders(table, enabled: bool) -> None:
    if not enabled:
        return
    tblPr = table._tbl.tblPr
    borders = _el("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(_el("w:" + edge, val="single", sz="4", space="0", color="000000"))
    tblPr.append(borders)


def fill_cell(cell, style: Style, text: str, bold: bool = False) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    set_jc(p, "left")
    set_spacing(p, style, before_tw=40, after_tw=40)
    for i, line in enumerate(str(text).split("\n")):
        target = p if i == 0 else cell.add_paragraph()
        if i:
            set_jc(target, "left")
            set_spacing(target, style, before_tw=40, after_tw=40)
        house_run(target.add_run(line), style, style.size("table"), bold)


def add_table(doc, style: Style, spec: dict):
    header = spec.get("header") or []
    rows = spec.get("rows") or []
    ncols = max([len(header)] + [len(r) for r in rows]) if (header or rows) else 1
    table = doc.add_table(rows=0, cols=ncols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, style.tables.get("borders", True))
    if header:
        cells = table.add_row().cells
        for i, text in enumerate(header):
            fill_cell(cells[i], style, text, style.tables.get("header_bold", True))
    for row in rows:
        cells = table.add_row().cells
        for i in range(ncols):
            fill_cell(cells[i], style, row[i] if i < len(row) else "")
    return table


def add_figure(doc, style: Style, spec: dict, base_dir: Path):
    image = spec.get("image")
    if not image:
        return
    path = Path(image)
    if not path.is_absolute():
        path = base_dir / path
    if not path.exists():
        raise FileNotFoundError(f"figure image not found: {path}")
    width = min(float(spec.get("width_cm", 0)) or style.content_width_mm() / 10.0,
                style.content_width_mm() / 10.0)
    p = doc.add_paragraph()
    set_jc(p, style.captions.get("alignment", "center"))
    set_spacing(p, style, before_tw=0, after_tw=style.space_after_tw)
    p.add_run().add_picture(str(path), width=Mm(width * 10))


def add_list(doc, style: Style, items) -> None:
    for item in items:
        p = doc.add_paragraph()
        set_jc(p, style.alignment)
        set_spacing(p, style, before_tw=None, after_tw=style.space_after_tw)
        if style.list_left_tw or style.list_hanging_tw:
            set_ind_list(p, style.list_left_tw, style.list_hanging_tw)
        house_run(p.add_run(str(item)), style)


# --------------------------------------------------------------------------------------
# Book parts
# --------------------------------------------------------------------------------------
def fill_placeholders(template: str, book: dict, lang: str) -> str:
    """Resolve {placeholder} tokens from the book metadata.

    A template written for one language refers to the language-neutral keys
    ({degree}); the book may only carry the language-specific ones
    (degree_en), so both are tried.
    """
    def repl(match):
        key = match.group(1)
        for candidate in (key, f"{key}_{lang}", f"{key}_th", f"{key}_en"):
            if candidate in book and book[candidate] not in (None, ""):
                return str(book[candidate])
        return f"[TODO: {key}]"
    return re.sub(r"\{(\w+)\}", repl, template)


def cover_page(doc, style: Style, book: dict, lang: str) -> None:
    th = lang == "th"
    title = book.get("title_th") if th else book.get("title_en")
    name = book.get("student_th") if th else book.get("student_en")
    statement_tpl = style.labels.get("cover_statement", {}).get(lang, "")
    statement = fill_placeholders(statement_tpl, book, lang)
    if book.get("doc_no"):
        statement = f"{statement} / {book['doc_no']}"

    for _ in range(7):
        para(doc, style, "", jc="center", first_line=False, before=0, after=0)
    para(doc, style, str(title or ""), size=style.size("cover_title"), bold=True,
         jc="center", first_line=False, before=0, after=240)
    by_label = style.labels.get("cover_by", {}).get(lang, "by")
    para(doc, style, f"{by_label} {name}" if name else "", size=style.size("cover_name"),
         bold=True, jc="center", first_line=False, before=0, after=120)
    para(doc, style, statement, size=style.size("cover_meta"), bold=True, jc="center",
         first_line=False, before=0, after=120)
    if book.get("advisor"):
        advisor_label = "อาจารย์ที่ปรึกษา" if th else "Advisor"
        para(doc, style, f"{advisor_label}: {book['advisor']}",
             size=style.size("cover_meta"), bold=True, jc="center", first_line=False,
             before=0, after=0)


def copyright_page(doc, style: Style, book: dict, lang: str) -> None:
    for _ in range(8):
        para(doc, style, "", jc="center", first_line=False, before=0, after=0)
    title = book.get(f"title_{lang}") or book.get("title_th") or book.get("title_en") or ""
    student = book.get(f"student_{lang}") or book.get("student_th") or ""
    degree = book.get(f"degree_{lang}") or book.get("degree_th") or ""
    department = book.get(f"department_{lang}") or book.get("department_th") or ""
    faculty = book.get(f"faculty_{lang}") or book.get("faculty_th") or ""
    institute = book.get(f"institute_{lang}") or book.get("institute_th") or ""
    labels = style.labels
    lines = [
        f"{style.label('copyright', lang)} {book.get(f'year_{lang}', '')}",
        faculty,
        institute,
        "",
        str(title),
        str(student),
        f"{labels.get('student_id', {}).get(lang, 'Student ID')}: "
        f"{book.get('student_id', '')}",
        str(degree),
        str(department),
        f"{labels.get('advisor', {}).get(lang, 'Advisor')}: {book.get('advisor', '')}",
    ]
    if book.get("co_advisor"):
        lines.append(f"{labels.get('co_advisor', {}).get(lang, 'Co-advisor')}: "
                     f"{book['co_advisor']}")
    year_line = labels.get("copyright_year", {}).get(lang, "Year {year}")
    lines.append(fill_placeholders(year_line, book, lang))
    for line in lines:
        para(doc, style, line, size=style.size("cover_meta"), bold=True, jc="center",
             first_line=False, before=0, after=120)


def abstract_page(doc, style: Style, book: dict, lang: str) -> None:
    th = lang == "th"
    heading(doc, style, 1, style.label("abstract", lang), size=style.size("abstract_heading"),
            jc="center", before=0, after=240)
    body = book.get("abstract_th") if th else book.get("abstract_en")
    for block in body or []:
        para(doc, style, block, before=0, after=style.space_after_tw)
    keywords = book.get("keywords_th") if th else book.get("keywords_en")
    if keywords:
        label = style.labels.get("keywords", {}).get(lang, "Keywords :")
        joined = " ".join(str(k) for k in keywords) if th else ", ".join(str(k) for k in keywords)
        p = doc.add_paragraph()
        set_jc(p, style.alignment)
        set_spacing(p, style, before_tw=0, after_tw=style.space_after_tw)
        if style.first_line_tw:
            set_ind_first_line(p, style.first_line_tw)
        house_run(p.add_run(f"{label} {joined}"), style, style.size("body"), True)


def certification_page(doc, style: Style, book: dict, lang: str) -> None:
    for _ in range(4):
        para(doc, style, "", jc="center", first_line=False, before=0, after=0)
    heading(doc, style, 1, style.label("certification", lang),
            size=style.size("front_heading"), jc="center", before=0, after=240)

    fields = style.labels.get("certification_fields", [])
    for field in fields:
        p = doc.add_paragraph()
        # A certification sheet is a form, not prose: left aligned, no first-line indent.
        set_jc(p, "left")
        set_spacing(p, style, before_tw=0, after_tw=120)
        label = (field.get("label") or {}).get(lang) or (field.get("label") or {}).get("th", "")
        house_run(p.add_run(f"{label} : "), style, style.size("body"), True)
        house_run(p.add_run(str(book.get(field.get("key", ""), ""))), style)

    table_spec = style.labels.get("certification_table", {})
    if table_spec:
        heading_text = (table_spec.get("heading") or {}).get(lang)
        if heading_text:
            para(doc, style, heading_text, size=style.size("body"), bold=True, jc="center",
                 first_line=False, before=120, after=120)
        columns = table_spec.get("columns", [])
        rows = table_spec.get("rows", [])
        table = doc.add_table(rows=0, cols=max(1, len(columns)))
        set_table_borders(table, style.tables.get("borders", True))
        if columns:
            cells = table.add_row().cells
            for i, col in enumerate(columns):
                fill_cell(cells[i], style, (col.get(lang) or col.get("th", "")),
                          style.tables.get("header_bold", True))
        for row in rows:
            cells = table.add_row().cells
            label = row.get(lang) or row.get("th", "")
            fill_cell(cells[0], style, label)
            for i in range(1, len(cells)):
                fill_cell(cells[i], style, "..............................................")

    closing = style.labels.get("certification_closing", {}).get(lang) or []
    for line in closing:
        para(doc, style, line, size=style.size("body"), jc="center", first_line=False,
             before=0, after=120)


def acknowledgements_page(doc, style: Style, book: dict, lang: str) -> None:
    heading(doc, style, 1, style.label("acknowledgements", lang),
            size=style.size("front_heading"), jc="center", before=0, after=240)
    body = book.get("acknowledgements_th") if lang == "th" else book.get("acknowledgements_en")
    for block in body or []:
        para(doc, style, block, before=0, after=style.space_after_tw)
    name = book.get("student_th") if lang == "th" else book.get("student_en")
    para(doc, style, str(name or ""), size=style.size("body"), jc="right", first_line=False,
         before=0, after=0)


def abbreviations_page(doc, style: Style, book: dict, lang: str) -> None:
    heading(doc, style, 1, style.label("abbreviations", lang),
            size=style.size("front_heading"), jc="center", before=0, after=240)
    rows = [[str(a.get("abbr", "")), str(a.get("full", ""))]
            for a in book.get("abbreviations", [])]
    if not rows:
        return
    table = doc.add_table(rows=0, cols=2)
    set_table_borders(table, style.tables.get("borders", True))
    hdr = table.add_row().cells
    fill_cell(hdr[0], style, style.labels.get("abbreviation_column", {}).get(
        lang, "คำย่อ" if lang == "th" else "Abbreviation"), True)
    fill_cell(hdr[1], style, style.labels.get("abbreviation_meaning", {}).get(
        lang, "ความหมาย" if lang == "th" else "Meaning"), True)
    for abbr, full in rows:
        cells = table.add_row().cells
        fill_cell(cells[0], style, abbr)
        fill_cell(cells[1], style, full)


def front_heading(doc, style: Style, text: str) -> None:
    heading(doc, style, 1, text, size=style.size("front_heading"), jc="center", before=0,
            after=240)


def render_blocks(doc, style: Style, blocks, base_dir: Path, lang: str) -> None:
    for block in blocks or []:
        kind = block.get("kind")
        if kind == "h2":
            heading(doc, style, 2, f"{block.get('number', '')} {block.get('text', '')}".strip(),
                    size=style.size("h2"), jc="left", before=240, after=style.space_after_tw)
        elif kind == "h3":
            heading(doc, style, 3, f"{block.get('number', '')} {block.get('text', '')}".strip(),
                    size=style.size("h3"), jc="left", before=240, after=style.space_after_tw)
        elif kind == "p":
            para(doc, style, block.get("text", ""), before=None,
                 after=style.space_after_tw)
        elif kind == "plain":
            para(doc, style, block.get("text", ""), jc="left", first_line=False, before=None,
                 after=style.space_after_tw)
        elif kind == "list":
            add_list(doc, style, block.get("items", []))
        elif kind == "bullets":
            add_list(doc, style, [f"- {item}" for item in block.get("items", [])])
        elif kind == "table":
            text = block.get("caption") or style.caption_text(
                "table", block.get("number", ""), block.get("text", ""), lang)
            caption(doc, style, text, before=style.captions.get("table_before_tw", 240),
                    after=style.captions.get("table_after_tw", 120))
            add_table(doc, style, block)
            source = block.get("source")
            if source:
                source_note(doc, style, source if source.startswith("(")
                            else style.source_text(source, lang))
        elif kind == "figure":
            text = block.get("caption") or style.caption_text(
                "figure", block.get("number", ""), block.get("text", ""), lang)
            caption(doc, style, text, before=style.captions.get("figure_before_tw", 120),
                    after=style.captions.get("figure_after_tw", 240))
            add_figure(doc, style, block, base_dir)
            source = block.get("source")
            if source:
                source_note(doc, style, source if source.startswith("(")
                            else style.source_text(source, lang))
        elif kind == "pagebreak":
            page_break(doc, style)
        elif kind == "quote":
            para(doc, style, block.get("text", ""), jc="left", first_line=False, before=120,
                 after=120, italic=True)
        else:
            raise ValueError(f"unknown block kind: {kind!r}")


def build_chapter(doc, style: Style, chapter: dict, base_dir: Path, lang: str) -> None:
    number = chapter.get("number")
    defaults = style.chapter_defaults(number)
    label = chapter.get("label")
    if not label:
        prefix = style.labels.get("chapter_label_prefix", {}).get(lang, "")
        label = f"{prefix} {number}".strip()
    title = chapter.get("title")
    if not title:
        title = (defaults.get("title") or {}).get(lang) or (defaults.get("title") or {}).get("th", "")
    heading(doc, style, 1, label, size=style.size("chapter_label"), jc="center", before=0,
            after=0)
    heading(doc, style, 1, title, size=style.size("chapter_title"), jc="center", before=0,
            after=240)
    render_blocks(doc, style, chapter.get("blocks", []), base_dir, lang)


def build_back_matter(doc, style: Style, book: dict, parts: list, base_dir: Path,
                       lang: str) -> None:
    for part in style.back_parts():
        kind = part.get("kind")
        if kind == "references":
            front_heading(doc, style, style.label("references", lang))
            for ref in book.get("references", []):
                p = doc.add_paragraph()
                set_jc(p, style.alignment)
                set_spacing(p, style, before_tw=0, after_tw=style.space_after_tw)
                if style.list_left_tw or style.list_hanging_tw:
                    set_ind_list(p, style.list_left_tw, style.list_hanging_tw)
                house_run(p.add_run(str(ref)), style)
        elif kind == "appendices":
            for item in parts:
                if item.get("kind") != "appendix":
                    continue
                page_break(doc, style)
                title = item.get("title") or style.label("appendix", lang)
                front_heading(doc, style, title)
                render_blocks(doc, style, item.get("blocks", []), base_dir, lang)
        elif kind == "biography":
            if not book.get("biography"):
                continue
            page_break(doc, style)
            front_heading(doc, style, style.label("biography", lang))
            for block in book["biography"]:
                para(doc, style, block, before=0, after=style.space_after_tw)


# --------------------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------------------
def split_front_parts(style: Style):
    """Split the profile's front matter into the unnumbered and the numbered parts.

    The leading covers and the copyright page carry no page numbers; everything
    after them is numbered with roman numerals.
    """
    parts = style.front_parts()
    split = 0
    while split < len(parts) and parts[split].get("kind") in ("cover", "copyright"):
        split += 1
    return parts[:split], parts[split:]


def build_front_matter_unnumbered(doc, style: Style, book: dict, lang: str) -> None:
    """Covers and the copyright page: no page numbers."""
    unnumbered, _ = split_front_parts(style)
    for part in unnumbered:
        kind = part.get("kind")
        if kind == "cover":
            cover_page(doc, style, book, part.get("lang", lang))
        elif kind == "copyright":
            copyright_page(doc, style, book, part.get("lang", lang))
        page_break(doc, style)


def build_front_matter(doc, style: Style, book: dict, lang: str) -> None:
    _unnumbered, numbered = split_front_parts(style)
    for index, part in enumerate(numbered):
        kind = part.get("kind")
        part_lang = part.get("lang", lang)
        if kind == "abstract":
            abstract_page(doc, style, book, part_lang)
        elif kind == "certification":
            certification_page(doc, style, book, part_lang)
        elif kind == "acknowledgements":
            acknowledgements_page(doc, style, book, part_lang)
        elif kind == "toc":
            front_heading(doc, style, style.label("toc", part_lang))
            add_field(doc.add_paragraph(), ' TOC \\o "1-3" \\h \\z \\u ',
                      "Update this field in Word (Ctrl+A, F9) to build the contents page.",
                      style)
        elif kind == "list_of_tables":
            front_heading(doc, style, style.label("list_of_tables", part_lang))
            add_field(doc.add_paragraph(), ' TOC \\h \\z \\t "TableCaption,1" ',
                      "Update this field in Word (Ctrl+A, F9).", style)
        elif kind == "list_of_figures":
            front_heading(doc, style, style.label("list_of_figures", part_lang))
            add_field(doc.add_paragraph(), ' TOC \\h \\z \\t "FigureCaption,1" ',
                      "Update this field in Word (Ctrl+A, F9).", style)
        elif kind == "abbreviations":
            if book.get("abbreviations"):
                abbreviations_page(doc, style, book, part_lang)
        else:
            raise ValueError(f"unknown front part kind: {kind!r}")
        if index < len(numbered) - 1:
            page_break(doc, style)


def build(spec: dict, out_path: Path, style: Style, master: Path | None) -> None:
    mode = spec.get("mode", "full")
    lang = spec.get("language", style.raw.get("language", "th"))
    book = spec.get("book", {})
    parts = spec.get("parts", [])
    base_dir = Path(spec.get("base_dir") or out_path.parent).resolve()

    if master:
        doc = Document(str(master))
        body = doc.element.body
        for child in list(body):
            if child.tag != qn("w:sectPr"):
                body.remove(child)
    else:
        doc = Document()

    apply_house_styles(doc, style)

    if mode == "full":
        cover_section = doc.sections[0]
        configure_page(cover_section, style)
        clear_header(cover_section)
        build_front_matter_unnumbered(doc, style, book, lang)

        front_section = doc.add_section(WD_SECTION.NEW_PAGE)
        configure_page(front_section, style)
        build_header(front_section, style)
        set_page_numbering(front_section, style.numbering.get("front_format", "lowerRoman"), 1)
        build_front_matter(doc, style, book, lang)

        body_section = doc.add_section(WD_SECTION.NEW_PAGE)
        configure_page(body_section, style)
        build_header(body_section, style)
        set_page_numbering(body_section, style.numbering.get("body_format", "decimal"),
                           style.numbering.get("body_start", 1))
        for part in parts:
            if part.get("kind") == "chapter":
                build_chapter(doc, style, part, base_dir, lang)
        build_back_matter(doc, style, book, parts, base_dir, lang)
    else:
        section = doc.sections[0]
        configure_page(section, style)
        build_header(section, style)
        set_page_numbering(section, style.numbering.get("body_format", "decimal"),
                           style.numbering.get("body_start", 1))
        for part in parts:
            if part.get("kind") in ("chapter", "appendix"):
                build_chapter(doc, style, part, base_dir, lang)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    print(f"wrote {out_path}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True, help="path to the JSON spec")
    ap.add_argument("--out", required=True, help="output .docx path")
    ap.add_argument("--profile", default=None,
                    help="style profile JSON (default: the bundled default profile)")
    ap.add_argument("--master", default=None,
                    help="master .docx to inherit styles/settings/header from "
                         "(default: the neutral master bundled with this skill)")
    ap.add_argument("--no-master", action="store_true",
                    help="build from scratch instead of using a master document")
    args = ap.parse_args(argv)

    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec.setdefault("base_dir", str(spec_path.parent))

    style = load_profile(Path(args.profile) if args.profile else None)

    master = None
    if not args.no_master:
        master = Path(args.master) if args.master else DEFAULT_MASTER
        if not master.exists():
            print(f"error: master document not found: {master}", file=sys.stderr)
            return 1
    build(spec, Path(args.out), style, master)
    return 0


if __name__ == "__main__":
    sys.exit(main())
