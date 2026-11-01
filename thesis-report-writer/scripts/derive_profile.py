#!/usr/bin/env python3
"""
derive_profile.py -- build one style profile from the documents a project already has.

`inspect_docx.py` reads a single reference document and stops at the measurable
basics. A project usually has more than one part — chapters, an abstract, an
appendix — and the house style shows up in the majority of them, not in any single
file. This script measures every part and merges the results by frequency, so one
oddly formatted page cannot set the style.

It also detects the details that decide whether Thai (or Arabic) text lays out
correctly and whether the compliance gate will be satisfiable:

  * how the first-line indent is spelled      (w:ind firstLine= vs a leading <w:tab/>)
  * which side a table/figure caption sits on (image first or caption first)
  * the caption label words                   ("ตารางที่", "Table", "Tabelle" …)
  * the appendix object prefix                ("ผ.", "A-", …)
  * the running footer, with any per-part variant
  * the keywords line: label, separator, count
  * the heading number/title separator        (tab or space)

Everything it cannot see (which parts the book has, what they are called) is left
out or marked in `notes`; fill those in from the rules file or a template — see
references/book-style.md.

Usage:
    python derive_profile.py -o house_style.json FILE... [--name NAME]
                             [--rules RULES.md] [--base template_profile.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TWIPS_PER_MM = 1440.0 / 25.4


def val(el, name, default=None):
    return default if el is None else el.get(W + name, default)


def text_of(el) -> str:
    return "".join(t.text or "" for t in el.iter(W + "t"))


def twips_to_mm(tw):
    return round(int(tw) / TWIPS_PER_MM, 2) if tw is not None else None


def mm_to_tw(mm: float) -> int:
    return int(round(float(mm) * TWIPS_PER_MM))


# --------------------------------------------------------------------------------------
class Part:
    """One .docx, opened once and queried by every measurement."""

    def __init__(self, path: Path):
        self.path = path
        self.zf = zipfile.ZipFile(str(path))
        self.doc = etree.fromstring(self.zf.read("word/document.xml"))
        self.styles = etree.fromstring(self.zf.read("word/styles.xml"))
        self.settings = etree.fromstring(self.zf.read("word/settings.xml"))
        self.body = self.doc.find(W + "body")
        self.top = list(self.body.findall(W + "p"))
        self.names = self.zf.namelist()

    # -- paragraph accessors -------------------------------------------------------
    def ppr(self, p):
        return p.find(W + "pPr")

    def pstyle(self, p):
        ppr = self.ppr(p)
        return val(ppr.find(W + "pStyle"), "val") if ppr is not None else None

    def jc(self, p):
        ppr = self.ppr(p)
        return val(ppr.find(W + "jc"), "val") if ppr is not None else None

    def spacing(self, p):
        ppr = self.ppr(p)
        return ppr.find(W + "spacing") if ppr is not None else None

    def indent(self, p):
        ppr = self.ppr(p)
        return ppr.find(W + "ind") if ppr is not None else None

    def is_heading(self, p) -> bool:
        sid = self.pstyle(p) or ""
        return sid.lower().startswith("heading") or sid.startswith("Heading")

    def leading_tab(self, p) -> bool:
        for run in p.findall(W + "r"):
            for child in run:
                if child.tag == W + "t":
                    return False
                if child.tag == W + "tab":
                    return True
        return False

    def run_sizes(self, p):
        out = []
        for run in p.findall(W + "r"):
            if run.find(W + "t") is None:
                continue
            rpr = run.find(W + "rPr")
            sz = rpr.find(W + "sz") if rpr is not None else None
            if sz is not None and val(sz, "val"):
                out.append(int(val(sz, "val")) / 2.0)
        return out

    def run_bold(self, p) -> bool:
        for run in p.findall(W + "r"):
            if run.find(W + "t") is None:
                continue
            rpr = run.find(W + "rPr")
            if rpr is not None and rpr.find(W + "b") is not None:
                return True
        return False

    def has_image(self, el) -> bool:
        return el.find(".//" + W + "drawing") is not None or \
            el.find(".//" + W + "pict") is not None

    def style_size(self, style_id):
        for st in self.styles.iter(W + "style"):
            if st.get(W + "styleId") == style_id:
                rpr = st.find(W + "rPr")
                sz = rpr.find(W + "sz") if rpr is not None else None
                if sz is not None and val(sz, "val"):
                    return int(val(sz, "val")) / 2.0
        return None

    def default_size(self):
        dd = self.styles.find(W + "docDefaults")
        rpr = dd.find(W + "rPrDefault/" + W + "rPr") if dd is not None else None
        sz = rpr.find(W + "sz") if rpr is not None else None
        if sz is not None and val(sz, "val"):
            return int(val(sz, "val")) / 2.0
        return None

    def default_fonts(self):
        dd = self.styles.find(W + "docDefaults")
        rpr = dd.find(W + "rPrDefault/" + W + "rPr") if dd is not None else None
        rf = rpr.find(W + "rFonts") if rpr is not None else None
        return [val(rf, k) for k in ("ascii", "hAnsi", "cs", "eastAsia") if val(rf, k)]

    def fonts_used(self):
        found = set()
        for rf in list(self.doc.iter(W + "rFonts")) + list(self.styles.iter(W + "rFonts")):
            for slot in ("ascii", "hAnsi", "cs", "eastAsia"):
                v = val(rf, slot)
                if v:
                    found.add(v)
        return found

    def headers(self):
        return [n for n in self.names if re.match(r"word/header\d*\.xml$", n)]

    def footers(self):
        out = []
        for name in self.names:
            if not re.match(r"word/footer\d*\.xml$", name):
                continue
            root = etree.fromstring(self.zf.read(name))
            for p in root.iter(W + "p"):
                body = text_of(p).strip()
                # Word repeats the same string in consecutive runs when a style
                # change happened; collapse "X,Y" that is really "X"
                half = len(body) // 2
                if half and body[:half] == body[half:]:
                    body = body[:half]
                if not body:
                    continue
                ppr = p.find(W + "pPr")
                out.append({
                    "part": name,
                    "text": body,
                    "jc": val(ppr.find(W + "jc"), "val") if ppr is not None else None,
                    "size": (self.run_sizes(p) or [None])[0],
                })
        return out


# --------------------------------------------------------------------------------------
def measure_part(part: Part) -> dict:
    """Every measurement one file contributes; the merge step counts them."""
    m = defaultdict(list)

    sect = part.body.find(W + "sectPr")
    pgSz = sect.find(W + "pgSz") if sect is not None else None
    pgMar = sect.find(W + "pgMar") if sect is not None else None
    m["page"] = [[twips_to_mm(val(pgSz, "w")), twips_to_mm(val(pgSz, "h")),
                  twips_to_mm(val(pgMar, "top")), twips_to_mm(val(pgMar, "bottom")),
                  twips_to_mm(val(pgMar, "left")), twips_to_mm(val(pgMar, "right")),
                  twips_to_mm(val(pgMar, "header")), twips_to_mm(val(pgMar, "footer")),
                  twips_to_mm(val(pgMar, "gutter", "0"))]]
    m["fonts"] = part.default_fonts()
    m["used_fonts"] = sorted(part.fonts_used())
    m["body_size"] = [part.default_size()]

    # ---- body paragraphs (never inside a table, never a heading) ----------------
    for p in part.top:
        if part.is_heading(p):
            continue
        body = text_of(p).strip()
        if not body:
            continue
        m["body_jc"].append(part.jc(p) or "None")
        sp = part.spacing(p)
        m["space_after"].append(int(val(sp, "after", 0) or 0))
        ind = part.indent(p)
        first = val(ind, "firstLine") if ind is not None else None
        hanging = val(ind, "hanging") if ind is not None else None
        left = val(ind, "left") if ind is not None else None
        if hanging and left:
            m["list_indent"].append((int(left), int(hanging)))
        elif first:
            m["indent_tw"].append(int(first))
        elif part.leading_tab(p):
            m["leading_tab"].append(1)

    # ---- headings ---------------------------------------------------------------
    head_sizes = defaultdict(list)
    for p in part.top:
        sid = part.pstyle(p)
        if not sid or not part.is_heading(p):
            continue
        body = text_of(p).strip()
        if not body:
            continue
        sp = part.spacing(p)
        before = int(val(sp, "before", 0) or 0)
        after = int(val(sp, "after", 0) or 0)
        sizes = part.run_sizes(p)
        head_sizes[sid].extend(sizes)
        m[f"{sid}_spacing"].append((before, after))
        m[f"{sid}_jc"].append(part.jc(p) or "None")
        runs = [r for r in p.findall(W + "r")
                if r.find(W + "t") is not None or r.find(W + "tab") is not None]
        first_text = text_of(runs[0]).strip() if runs else ""
        if re.match(r"^\d+(\.\d+)+$", first_text):
            joined_by_tab = any(r.find(W + "tab") is not None for r in runs[1:])
            m["heading_sep"].append("tab" if joined_by_tab else "space")
    for sid, sizes in head_sizes.items():
        m[f"style_{sid}"].append(sizes)

    # ---- captions ---------------------------------------------------------------
    # Recognise a caption by its *shape* first ("<words> <number>.<number>"), then
    # classify the label by which objects actually follow or precede it. Guessing
    # the label from a fixed vocabulary breaks on every other language.
    labels = {"table": Counter(), "figure": Counter()}
    appendix_prefixes = Counter()
    for idx, el in enumerate(part.body):
        if el.tag != W + "p":
            continue
        body = text_of(el).strip()
        mt = re.match(r"^\s*([^\d\s][^\d]{0,24}?)\s+([^\s]+)\s*[.]?\s*(\d+)\b", body)
        if not mt:
            continue
        word, chapter, seq = mt.group(1).strip(), mt.group(2), mt.group(3)
        chapter_core = chapter.rstrip(".")
        nxt = part.body[idx + 1] if idx + 1 < len(part.body) else None
        prv = part.body[idx - 1] if idx > 0 else None
        # which side is the object on? that is what tells a table from a figure
        obj_after = nxt is not None and (nxt.tag == W + "tbl" or part.has_image(nxt))
        obj_before = prv is not None and (prv.tag == W + "tbl" or part.has_image(prv))
        if not (obj_after or obj_before):
            continue
        kind = "table" if (nxt is not None and nxt.tag == W + "tbl") or \
            (prv is not None and prv.tag == W + "tbl") else "figure"
        label_text = re.sub(r"\s*", "", word) if chapter_core[0].isalpha() else word
        labels[kind][label_text] += 1
        if chapter_core.isdigit():
            sizes = part.run_sizes(el)
            if sizes:
                m[f"caption_size_{kind}"].extend(sizes)
            m[f"caption_bold_{kind}"].append(part.run_bold(el))
            m[f"caption_jc_{kind}"].append(part.jc(el) or "None")
            sp = part.spacing(el)
            m[f"caption_before_{kind}"].append(int(val(sp, "before", 0) or 0))
            m[f"caption_after_{kind}"].append(int(val(sp, "after", 0) or 0))
            if obj_after:
                m[f"placement_{kind}"].append("above")
            elif obj_before:
                m[f"placement_{kind}"].append("below")
            # a source line is the paragraph that opens with "(" after the object
            look = idx + 1
            while look < len(part.body) and look < idx + 4:
                cand = part.body[look]
                line = text_of(cand).strip() if cand.tag == W + "p" else ""
                if line.startswith("("):
                    m["source_prefix"].append(line[:line.find(")") + 1])
                    break
                look += 1
        elif re.match(r"^[A-Za-z\u0E00-\u0E7F]{1,3}\.?$", chapter):
            # a short non-numeric chapter token is an appendix letter ("ผ", "A")
            appendix_prefixes[chapter] += 1
    for kind, counter in labels.items():
        m[f"label_{kind}"] = [counter.most_common(1)[0][0]] if counter else []
    if appendix_prefixes:
        m["appendix_prefix"].append(appendix_prefixes.most_common(1)[0][0])

    # ---- footer / header ---------------------------------------------------------
    for f in part.footers():
        m["footer_text"].append(f["text"])
        if f["jc"]:
            m["footer_jc"].append(f["jc"])
        if f["size"]:
            m["footer_size"].append(f["size"])
    for name in part.headers():
        xml = part.zf.read(name).decode("utf-8", "replace")
        if "PAGE" not in xml:
            continue
        root = etree.fromstring(xml.encode("utf-8"))
        for p in root.iter(W + "p"):
            if not list(p.iter(W + "instrText")):
                continue
            ppr = p.find(W + "pPr")
            m["page_jc"].append(val(ppr.find(W + "jc"), "val") if ppr is not None else "left")

    # ---- page numbering ----------------------------------------------------------
    for n in part.body.iter(W + "pgNumType"):
        fmt = val(n, "fmt")
        if fmt:
            m["pg_fmt"].append(fmt)

    # ---- keywords ---------------------------------------------------------------
    for p in part.top:
        body = text_of(p).strip()
        mt = re.match(r"^([^\d]{2,20}?[:：])\s*(.+)$", body)
        if mt and ("คำสำคัญ" in mt.group(1) or "Keyword" in mt.group(1)
                   or "Schlagwort" in mt.group(1)):
            rest = mt.group(2)
            sep = ", " if ", " in rest else (" " if " " in rest else ",")
            terms = [t for t in rest.split(sep) if t.strip()]
            label = mt.group(1).strip()
            m["keyword_label"].append(label)
            lang = "th" if "คำสำคัญ" in label else "en"
            m[f"keyword_sep_{lang}"].append(sep)
            m["keyword_count"].append(len(terms))

    # ---- settings ---------------------------------------------------------------
    compat = part.settings.find(W + "compat")
    if compat is not None and compat.find(W + "applyBreakingRules") is not None:
        m["breaking_rules"].append(1)
    return m


# --------------------------------------------------------------------------------------
def _jc_or_default(values, default="center"):
    real = [v for v in values if v and v != "None"]
    return Counter(real).most_common(1)[0][0] if real else default


def most(rows, key, default=None):
    vals = [r[key] for r in rows if key in r]
    if not vals:
        return default
    return Counter(vals).most_common(1)[0][0]


def top(counter_or_list, default=None):
    if isinstance(counter_or_list, Counter):
        return counter_or_list.most_common(1)[0][0] if counter_or_list else default
    if isinstance(counter_or_list, list) and counter_or_list:
        return Counter(counter_or_list).most_common(1)[0][0]
    return default


def merge(measurements: list, name: str, rules_path: str | None) -> dict:
    flat = [k for m in measurements for k, v in m.items()]
    def vals(key):
        out = []
        for m in measurements:
            out.extend(m.get(key, []))
        return out

    page_triples = vals("page")
    page = page_triples[0] if page_triples else [210, 297, 25.4, 25.4, 25.4, 25.4, 12.7, 12.7, 0]

    fonts = Counter(vals("fonts"))
    used = Counter(vals("used_fonts"))
    body_size = top(vals("body_size"))

    tab_mode = len(vals("leading_tab"))
    ind_tw = top(vals("indent_tw"))
    indent_mode = "tab" if tab_mode and not ind_tw else (
        "either" if tab_mode and ind_tw else ("indent" if ind_tw else "tab"))

    space_after = top(vals("space_after"), 0)

    head = {}
    for sid, short in (("Heading1", "h1"), ("Heading2", "h2"), ("Heading3", "h3")):
        sizes = [s for group in vals(f"style_{sid}") for s in group]
        if sizes:
            head[f"{short}_size"] = min(sizes) if short == "h1" else top(sizes)
        sp = Counter(vals(f"{sid}_spacing")).most_common(1)
        if sp:
            head[f"{short}_before"] = sp[0][0][0]
            head[f"{short}_after"] = sp[0][0][1]

    h1_sizes = [s for group in vals("style_Heading1") for s in group]
    chapter_label = min(h1_sizes) if h1_sizes else None
    chapter_title = max(h1_sizes) if h1_sizes else None

    footer_text = top(vals("footer_text"))
    footer_variants = sorted(set(vals("footer_text")))

    profile = {
        "name": name,
        "summary": f"Style profile derived from {len(measurements)} document(s) by derive_profile.py.",
        "source": "derive_profile.py measurements: " +
                  ", ".join(sorted({Path(r["file"]).name for r in measurements})),
        "language": "th" if re.search(r"[\u0E00-\u0E7F]", " ".join(
            text_of(p) for p in measurements[0].get("_sample_paras", [])) or "ไ") else "en",
        "page": {
            "width_mm": page[0] or 210.0,
            "height_mm": page[1] or 297.0,
            "orientation": "portrait",
            "margin_top_mm": page[2] or 25.4,
            "margin_bottom_mm": page[3] or 25.4,
            "margin_left_mm": page[4] or 25.4,
            "margin_right_mm": page[5] or 25.4,
            "header_mm": page[6] or 12.7,
            "footer_mm": page[7] or 12.7,
            "gutter_mm": page[8] or 0.0,
        },
        "fonts": {
            "body": top(fonts) or top(used) or "Times New Roman",
            "allowed": sorted(set(vals("used_fonts"))) or [top(fonts) or "Times New Roman"],
            "sizes_pt": {
                "body": body_size or 12,
                "chapter_label": chapter_label or (body_size or 12) + 4,
                "chapter_title": chapter_title or (body_size or 12) + 8,
                "h2": head.get("h2_size") or (body_size or 12),
                "h3": head.get("h3_size") or body_size or 12,
                "front_heading": chapter_title or (body_size or 12) + 8,
                "abstract_heading": body_size or 12,
                "cover_title": chapter_label or (body_size or 12) + 4,
                "cover_name": chapter_label or (body_size or 12) + 4,
                "cover_meta": body_size or 12,
                "table": max(1, (body_size or 12) - 2),
                "caption": top(vals("caption_size_table")) or body_size or 12,
                "footer": top(vals("footer_size")) or 10,
            },
        },
        "paragraphs": {
            "alignment": top(vals("body_jc"), "left"),
            "forbidden_alignment": [] if top(vals("body_jc")) == "both" else ["both"],
            "first_line_mode": indent_mode,
            "first_line_tw": ind_tw or 720,
            "first_line_tab_tw": 567,
            "space_after_tw": space_after,
            "space_after_heading_tw": head.get("h2_after", 120),
            "space_before_tw": 0,
            "line_tw": 240,
            "list_left_tw": top([a for pair in vals("list_indent") for a in [pair[0]]]) or 0,
            "list_hanging_tw": top([p[1] for p in vals("list_indent")]) or 0,
            "hint_cs": bool(vals("breaking_rules")) or bool(re.search(
                r"[\u0E00-\u0E7F\u0600-\u06FF]", " ".join(vals("footer_text")))),
        },
        "headings": {
            "label_before_tw": head.get("h1_before", 0),
            "label_after_tw": head.get("h1_after", 120),
            "title_before_tw": head.get("h1_before", 0),
            "title_after_tw": head.get("h1_after", 240),
            "h2_before_tw": head.get("h2_before", 240),
            "h2_after_tw": head.get("h2_after", 120),
            "h3_before_tw": head.get("h3_before", 120),
            "h3_after_tw": head.get("h3_after", 120),
            "separator_between_number_and_title": top(vals("heading_sep"), "space"),
        },
        "captions": {
            "placement": {
                "table": top(vals("placement_table"), "above"),
                "figure": top(vals("placement_figure"), "above"),
            },
            "alignment": "center",
            "table_alignment": _jc_or_default(vals("caption_jc_table")),
            "figure_alignment": _jc_or_default(vals("caption_jc_figure")),
            "bold": bool(top(vals("caption_bold_table"), False)),
            "table_before_tw": top(vals("caption_before_table"), 240),
            "table_after_tw": top(vals("caption_after_table"), 120),
            "figure_before_tw": top(vals("caption_before_figure"), 120),
            "figure_after_tw": top(vals("caption_after_figure"), 240),
            "figure_image_before_tw": 120,
            "figure_image_after_tw": 120,
            "table_label": top(vals("label_table"), "Table"),
            "figure_label": top(vals("label_figure"), "Figure"),
            "table_label_en": "Table",
            "figure_label_en": "Figure",
            "appendix_prefix": top(vals("appendix_prefix"), ""),
            "source_prefix": top(vals("source_prefix"), ""),
            "source_prefix_en": "(Reference(s): ",
        },
        "tables": {"borders": True, "header_bold": True, "caption_bold": True},
        "page_numbering": {
            "front_format": top(vals("pg_fmt"), "lowerRoman"),
            "body_format": "decimal",
            "body_start": 1,
            "position": "header",
            "alignment": top(vals("page_jc"), "center"),
            "number_cover_pages": False,
        },
        "footer": {
            "text": footer_text or "",
            "size_pt": top(vals("footer_size"), 10),
            "alignment": top(vals("footer_jc"), "left"),
            "variants": footer_variants,
        },
        "keywords": {
            "label_th": top([l for l in vals("keyword_label") if "คำสำคัญ" in l], "คำสำคัญ :"),
            "label_en": top([l for l in vals("keyword_label") if "Keyword" in l], "Keywords :"),
            "separator_th": top(vals("keyword_sep_th"), " "),
            "separator_en": top(vals("keyword_sep_en"), ", "),
            "min": 4,
            "max": 6,
        },
        "notes": [
            "Structure (which parts the book has, what each is called) and the "
            "chapter section lists were NOT detected: copy them from the rules file "
            "or the template. See references/book-style.md.",
            "`footer.variants` lists every footer text found; if the book uses a "
            "different marking on one part, set `footer.by_part`.",
        ],
    }
    if rules_path:
        profile["rules"] = {"authoritative": rules_path}
        profile["policy"] = ("An explicit value in the delivered documents wins; an "
                             "omitted value falls back to the written rules. Record "
                             "each disagreement in `rule_deltas`.")
    # drop nulls so the profile stays readable
    for section in ("captions",):
        profile[section] = {k: v for k, v in profile[section].items() if v is not None}
    return profile


# --------------------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", nargs="+", help="the project's existing documents")
    ap.add_argument("-o", "--out", required=True, help="write the profile here")
    ap.add_argument("--name", default=None, help="style name (default: the output stem)")
    ap.add_argument("--rules", default=None,
                    help="path of the written rules file, recorded in the profile")
    ap.add_argument("--base", default=None,
                    help="start from this profile and override what was measured")
    args = ap.parse_args(argv)

    parts = [Part(Path(p)) for p in args.docx]
    measurements = [measure_part(part) for part in parts]
    for m, part in zip(measurements, parts):
        m["file"] = str(part.path)
        m["_sample_paras"] = [p for p in part.top[:5]]

    name = args.name or Path(args.out).stem.replace("_", " ")
    profile = merge(measurements, name, args.rules)
    profile.pop("_sample_paras", None)

    if args.base:
        base = json.loads(Path(args.base).read_text(encoding="utf-8"))
        merged = dict(base)
        for key, value in profile.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        profile = merged

    Path(args.out).write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    print(f"profile written: {args.out} ({len(parts)} document(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
