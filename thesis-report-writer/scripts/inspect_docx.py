#!/usr/bin/env python3
"""
inspect_docx.py -- derive a reusable style profile from an existing Word document.

Every project expresses its house style somewhere: a rules document, a template
.docx, or a report somebody already wrote. When the machine-readable version is
missing, it can be extracted from the document itself: page setup, fonts, sizes,
paragraph metrics, caption metrics and page numbering.

The output uses the same schema as assets/default_profile.json, so it can be fed
straight into build_report.py (--profile) and check_report.py (--profile).

Usage:
    python inspect_docx.py reference.docx -o profile.json [--inherit-structure]
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

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HERE = Path(__file__).resolve().parent
DEFAULT_PROFILE = HERE.parent / "assets" / "default_profile.json"

TWIPS_PER_MM = 1440.0 / 25.4


def val(el, name, default=None):
    if el is None:
        return default
    return el.get(W + name, default)


def twips_to_mm(tw):
    return round(int(tw) / TWIPS_PER_MM, 2) if tw is not None else None


def inspect(path: Path) -> dict:
    z = zipfile.ZipFile(str(path))
    doc = etree.fromstring(z.read("word/document.xml"))
    styles = etree.fromstring(z.read("word/styles.xml"))
    settings = etree.fromstring(z.read("word/settings.xml"))
    body = doc.find(W + "body")
    paras = list(body.iter(W + "p"))
    # Paragraphs that are direct children of the body: table-cell paragraphs would
    # otherwise skew the body metrics (they use the smaller table size).
    top_paras = list(body.findall(W + "p"))

    def pPr(p):
        return p.find(W + "pPr")

    def pstyle(p):
        return val(pPr(p).find(W + "pStyle"), "val") if pPr(p) is not None else None

    def jc(p):
        return val(pPr(p).find(W + "jc"), "val") if pPr(p) is not None else None

    def ind(p):
        return pPr(p).find(W + "ind") if pPr(p) is not None else None

    def spacing(p):
        return pPr(p).find(W + "spacing") if pPr(p) is not None else None

    def text(p):
        return "".join(t.text or "" for t in p.iter(W + "t"))

    def run_size(p):
        sizes = []
        for run in p.findall(W + "r"):
            if run.find(W + "t") is None:
                continue
            rPr = run.find(W + "rPr")
            sz = rPr.find(W + "sz") if rPr is not None else None
            if sz is not None and val(sz, "val"):
                sizes.append(int(val(sz, "val")) / 2.0)
        return sizes

    # ---- page setup -------------------------------------------------------------
    sect = body.find(W + "sectPr")
    pgSz = sect.find(W + "pgSz") if sect is not None else None
    pgMar = sect.find(W + "pgMar") if sect is not None else None
    page = {
        "width_mm": twips_to_mm(val(pgSz, "w")),
        "height_mm": twips_to_mm(val(pgSz, "h")),
        "orientation": "landscape" if val(pgSz, "orient") == "landscape" else "portrait",
        "margin_top_mm": twips_to_mm(val(pgMar, "top")),
        "margin_bottom_mm": twips_to_mm(val(pgMar, "bottom")),
        "margin_left_mm": twips_to_mm(val(pgMar, "left")),
        "margin_right_mm": twips_to_mm(val(pgMar, "right")),
        "header_mm": twips_to_mm(val(pgMar, "header")),
        "footer_mm": twips_to_mm(val(pgMar, "footer")),
        "gutter_mm": twips_to_mm(val(pgMar, "gutter", "0")),
    }

    # ---- fonts ------------------------------------------------------------------
    def style_font(style_id):
        for st in styles.iter(W + "style"):
            if st.get(W + "styleId") == style_id:
                rPr = st.find(W + "rPr")
                rFonts = rPr.find(W + "rFonts") if rPr is not None else None
                return val(rFonts, "ascii") or val(rFonts, "hAnsi")
        return None

    docDefaults = styles.find(W + "docDefaults")
    default_font = None
    if docDefaults is not None:
        rPrDefault = docDefaults.find(W + "rPrDefault")
        rPr = rPrDefault.find(W + "rPr") if rPrDefault is not None else None
        rFonts = rPr.find(W + "rFonts") if rPr is not None else None
        default_font = val(rFonts, "ascii") or val(rFonts, "hAnsi") or val(rFonts, "cs")

    font_counter = Counter()
    hint_cs_runs = 0
    text_runs = 0
    for p in paras:
        for run in p.findall(W + "r"):
            if run.find(W + "t") is None:
                continue
            text_runs += 1
            rPr = run.find(W + "rPr")
            rFonts = rPr.find(W + "rFonts") if rPr is not None else None
            if rFonts is not None:
                name = val(rFonts, "ascii") or val(rFonts, "hAnsi") or val(rFonts, "cs")
                if name:
                    font_counter[name] += 1
                if val(rFonts, "hint") == "cs":
                    hint_cs_runs += 1

    body_font = default_font or (font_counter.most_common(1)[0][0] if font_counter else None)
    allowed = sorted({f for f in font_counter} | ({default_font} if default_font else set()))

    # ---- sizes ------------------------------------------------------------------
    def style_size(style_id):
        for st in styles.iter(W + "style"):
            if st.get(W + "styleId") == style_id:
                rPr = st.find(W + "rPr")
                sz = rPr.find(W + "sz") if rPr is not None else None
                if sz is not None and val(sz, "val"):
                    return int(val(sz, "val")) / 2.0
        return None

    body_sizes = Counter()
    for p in top_paras:
        if pstyle(p):
            continue
        for s in run_size(p):
            body_sizes[s] += 1
    # Body text inherits its size from the document defaults unless a paragraph
    # overrides it, so the defaults win and the explicit sizes are the fallback.
    inherited_pt = None
    if docDefaults is not None:
        rPrDefault = docDefaults.find(W + "rPrDefault")
        rPr = rPrDefault.find(W + "rPr") if rPrDefault is not None else None
        sz = rPr.find(W + "sz") if rPr is not None else None
        if sz is not None and val(sz, "val"):
            inherited_pt = int(val(sz, "val")) / 2.0
    body_pt = inherited_pt or (body_sizes.most_common(1)[0][0] if body_sizes else 12.0)

    h1_sizes = [s for p in paras if pstyle(p) == "Heading1" for s in run_size(p)]
    h1_sizes += [s for s in [style_size("Heading1")] if s]
    h1_sizes = sorted(set(h1_sizes))
    chapter_label = min(h1_sizes) if h1_sizes else body_pt + 4
    chapter_title = max(h1_sizes) if h1_sizes else body_pt + 8
    h2 = style_size("Heading2") or (chapter_title - 6)
    h3 = style_size("Heading3") or body_pt

    # ---- paragraph metrics ------------------------------------------------------
    align_counter, first_counter, after_counter = Counter(), Counter(), Counter()
    list_counter = Counter()
    for p in top_paras:
        if not text(p).strip() or pstyle(p):
            continue
        j = jc(p)
        if j:
            align_counter[j] += 1
        i = ind(p)
        if i is not None:
            fl = val(i, "firstLine")
            left = val(i, "left")
            hanging = val(i, "hanging")
            if left:
                # an indented paragraph is a list item; its hanging indent is the
                # list geometry, not the body's first-line indent
                if hanging:
                    list_counter[(int(left), int(hanging))] += 1
                continue
            if fl:
                first_counter[int(fl)] += 1
        s = spacing(p)
        if s is not None and val(s, "after"):
            after_counter[int(val(s, "after"))] += 1

    alignment = align_counter.most_common(1)[0][0] if align_counter else "left"
    first_line = first_counter.most_common(1)[0][0] if first_counter else 0
    space_after = after_counter.most_common(1)[0][0] if after_counter else 0
    if list_counter:
        (list_left, list_hanging), _count = list_counter.most_common(1)[0]
    else:
        list_left, list_hanging = 0, 0

    # ---- captions ---------------------------------------------------------------
    caption_sizes, table_before, table_after = Counter(), Counter(), Counter()
    for idx, p in enumerate(paras):
        j = jc(p)
        if j != "center" or not text(p).strip():
            continue
        sizes = run_size(p)
        if not sizes:
            continue
        nxt = paras[idx + 1] if idx + 1 < len(paras) else None
        is_caption = nxt is not None and (
            nxt.find(".//" + W + "drawing") is not None
            or nxt.find(".//" + W + "pict") is not None
            or (nxt.find(W + "pPr") is not None and nxt.find(W + "pPr").find(W + "pStyle") is None
                and jc(nxt) is None)
        )
        if not is_caption:
            continue
        caption_sizes[max(sizes)] += 1
        s = spacing(p)
        if s is not None:
            table_before[int(val(s, "before", 0))] += 1
            table_after[int(val(s, "after", 0))] += 1

    caption_pt = caption_sizes.most_common(1)[0][0] if caption_sizes else body_pt

    # ---- page numbering ---------------------------------------------------------
    fmts = [val(n, "fmt") for n in body.iter(W + "pgNumType")]
    roman = next((f for f in fmts if f and "Roman" in f), None)
    decimal = next((f for f in fmts if f and "Roman" not in f), None)

    compat = settings.find(W + "compat")
    profile = {
        "name": path.stem,
        "summary": f"Style profile extracted from {path.name}",
        "source": f"extracted by inspect_docx.py from {path}",
        "language": "th" if re.search(r"[\u0E00-\u0E7F]", "\n".join(text(p) for p in paras)) else "en",
        "page": page,
        "fonts": {
            "body": body_font,
            "allowed": allowed,
            "sizes_pt": {
                "body": body_pt,
                "chapter_label": chapter_label,
                "chapter_title": chapter_title,
                "h2": h2,
                "h3": h3,
                "front_heading": chapter_title,
                "abstract_heading": chapter_title,
                "cover_title": chapter_label,
                "cover_name": chapter_label,
                "cover_meta": body_pt,
                "table": max(1, body_pt - 2),
                "caption": caption_pt,
            },
        },
        "paragraphs": {
            "alignment": alignment,
            "forbidden_alignment": ["both"] if alignment != "both" else [],
            "first_line_tw": first_line,
            "space_after_tw": space_after,
            "space_before_tw": 0,
            "line_tw": 240,
            "list_left_tw": list_left,
            "list_hanging_tw": list_hanging,
            "hint_cs": bool(text_runs) and hint_cs_runs / max(1, text_runs) > 0.25,
        },
        "captions": {
            "alignment": "center",
            "table_before_tw": table_before.most_common(1)[0][0] if table_before else 240,
            "table_after_tw": table_after.most_common(1)[0][0] if table_after else 120,
            "figure_before_tw": table_before.most_common(1)[0][0] if table_before else 120,
            "figure_after_tw": table_after.most_common(1)[0][0] if table_after else 240,
            "table_label": "ตารางที่",
            "figure_label": "รูปที่",
            "table_label_en": "Table",
            "figure_label_en": "Figure",
            "source_prefix": "(ที่มา: ",
            "source_prefix_en": "(Reference(s): ",
        },
        "tables": {"borders": True, "header_bold": True},
        "page_numbering": {
            "front_format": roman or "lowerRoman",
            "body_format": decimal or "decimal",
            "body_start": 1,
            "position": "header",
            "alignment": "center",
            "number_cover_pages": False,
        },
        "notes": [
            "Structure and labels were not detected; they are document-specific.",
            "Use --inherit-structure to copy them from the bundled default profile.",
        ],
    }
    return profile


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", help="reference document to inspect")
    ap.add_argument("-o", "--out", default=None, help="write the profile here (default: stdout)")
    ap.add_argument("--inherit-structure", action="store_true",
                    help="copy structure and labels from the bundled default profile")
    args = ap.parse_args(argv)

    path = Path(args.docx)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1
    profile = inspect(path)
    if args.inherit_structure and DEFAULT_PROFILE.exists():
        base = json.loads(DEFAULT_PROFILE.read_text(encoding="utf-8"))
        profile["structure"] = base.get("structure")
        profile["labels"] = base.get("labels")
        profile["captions"]["table_label"] = base["captions"]["table_label"]
        profile["captions"]["figure_label"] = base["captions"]["figure_label"]
        profile["captions"]["table_label_en"] = base["captions"]["table_label_en"]
        profile["captions"]["figure_label_en"] = base["captions"]["figure_label_en"]
        profile["notes"] = ["Structure and labels inherited from the bundled default "
                            "profile; edit them to match this project."]

    text = json.dumps(profile, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"profile written: {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
