# Style profiles — the house style as data

A style profile is one JSON file that carries every measurable decision of a house
style. The builder applies it, the checker verifies against it. Because the style
lives in data rather than in code, the same tooling serves any institution: change
the profile, not the scripts.

## Where a profile comes from

| Source | How |
|---|---|
| A written rules file | Read the values out of it and write the profile by hand. The rules file stays the authority; the profile is its machine-readable shadow. |
| Existing documents from the project | `python scripts/derive_profile.py -o house_style.json docs/thesis/*.docx` — the majority value across every part (see `references/book-style.md`) |
| A template or an existing report | `python scripts/inspect_docx.py template.docx -o house_style.json --inherit-structure` |
| Nothing | Use `assets/default_profile.json` (the Thai KMITL Faculty of Science co-op style) and say so in your report. |

`inspect_docx.py` reads the page setup, the fonts and their sizes, the paragraph
metrics, the caption rules and the page-numbering formats from a reference
document. It cannot see the *structure* — which parts the book has and what they
are called — so `--inherit-structure` copies that from the bundled default and
leaves a note telling you to edit it.

Always compare the extracted profile against the rules file when both exist: the
detector reports what the document does, the rules file states what it should do,
and they occasionally disagree (a document may have been hand-edited into a state
nobody intended).

## The schema

```jsonc
{
  "name": "Human-readable style name",
  "summary": "one line describing the style",
  "source": "where it came from — file path, URL, rule document",
  "language": "th",                       // default language of the book

  "page": {
    "width_mm": 210.0, "height_mm": 297.0, "orientation": "portrait",
    "margin_top_mm": 25.4, "margin_bottom_mm": 25.4,
    "margin_left_mm": 38.1, "margin_right_mm": 25.4,
    "header_mm": 12.7, "footer_mm": 12.7, "gutter_mm": 0.0
  },

  "fonts": {
    "body": "TH SarabunPSK",
    "allowed": ["TH SarabunPSK"],        // any other family is a violation
    "sizes_pt": {
      "body": 16, "chapter_label": 20, "chapter_title": 24,
      "h2": 18, "h3": 16, "front_heading": 24, "abstract_heading": 17,
      "cover_title": 20, "cover_name": 18, "cover_meta": 16,
      "table": 14, "caption": 16
    }
  },

  "paragraphs": {
    "alignment": "thaiDistribute",        // any w:jc value
    "forbidden_alignment": ["both"],      // never allowed in the document
    "first_line_tw": 720,                 // 720 twips = 0.5 in
    "space_after_tw": 120,                // 120 twips = 6 pt
    "space_before_tw": 0,
    "line_tw": 240,                       // 240 = single spacing
    "list_left_tw": 283, "list_hanging_tw": 283,
    "hint_cs": true                       // w:hint="cs" on every run
  },

  "captions": {
    "alignment": "center",
    "table_before_tw": 240, "table_after_tw": 120,
    "figure_before_tw": 120, "figure_after_tw": 240,
    "table_label": "ตารางที่", "figure_label": "รูปที่",
    "table_label_en": "Table", "figure_label_en": "Figure",
    "source_prefix": "(ที่มา: ", "source_prefix_en": "(Reference(s): "
  },

  "tables": { "borders": true, "header_bold": true },

  "page_numbering": {
    "front_format": "lowerRoman",         // w:pgNumType w:fmt
    "body_format": "decimal",
    "body_start": 1,
    "position": "header",
    "alignment": "center",
    "number_cover_pages": false
  },

  "structure": {
    "front": [ { "kind": "cover", "lang": "th" }, { "kind": "copyright" }, ... ],
    "chapters": [ { "number": 1, "label": { "th": "บทที่ 1" },
                    "title": { "th": "บทนำ", "en": "Introduction" } }, ... ],
    "back": [ { "kind": "references" }, { "kind": "appendices" },
              { "kind": "biography" } ]
  },

  "labels": { "abstract": { "th": "บทคัดย่อ", "en": "Abstract" }, ... }
}
```

### Units

- **Page setup is in millimetres** — it is what a rules document or a template
  dialog shows.
- **Paragraph metrics are in twips** — one twentieth of a point, 1440 twips per
  inch. Word's own unit; the values in a rules file are usually in inches or
  centimetres, so convert: 1 in = 1440 twips, 1 cm = 567 twips.
- **Sizes are in points.** OOXML stores half-points (`w:sz="32"` = 16 pt); the
  scripts convert.

### The provenance block: `policy`, `rules`, `rule_deltas`

When a project has both a written rules file and existing documents, the profile
must say **which wins** and **where they disagree**. Without that, a stale rules
file silently overrules the book the user actually has.

```jsonc
"policy": "An explicit value in the delivered files wins; an omitted value falls
           back to the written rules.",
"rules": {
  "authoritative": "RULES_thai_report.md",
  "working_copy": "Docs_rules.md",
  "ids": {
    "page-setup":    ["R-01", "R-02", "P-01"],     // check id -> rule IDs
    "heading-sizes": ["R-06", "R-07", "P-07", "P-08"],
    "footer":        ["P-03"]
  }
},
"rule_deltas": [
  { "rule": "R-15", "item": "paragraphs.first_line_tw",
    "stated": "0.5 in via w:ind w:firstLine=\"720\"",
    "in_book": "a leading <w:tab/> to the 567-twip stop",
    "evidence": "37/39 body paragraphs in chapter 1",
    "decision": "mode \"either\" accepts both" }
]
```

- **`rules.ids`** makes the gate quote rule IDs: every `[PASS]`/`[FAIL]` line ends
  with the IDs that check enforces, so the user can act on "R-12" without
  re-reading the guide. `RULES_thai_report.md` already numbers its rules; other
  houses usually number theirs too.
- **`rule_deltas`** is printed as one `rule-deltas` warning per row, and the row
  survives every future run. It is the honest record of "the document is like
  this, the rule says that, we chose this".

### Extended keys (optional — absent means the older behaviour)

```jsonc
"paragraphs": {
  "first_line_mode": "either",        // "indent" (w:ind) | "tab" (leading <w:tab/>) | "either"
  "first_line_tab_tw": 567,           // tab stop the leading tab lands on
  "space_after_heading_tw": 120       // headings/captions space after, when body uses 0
},

"headings": {
  "label_before_tw": 0, "label_after_tw": 120,
  "title_before_tw": 0, "title_after_tw": 240,
  "h2_before_tw": 240, "h2_after_tw": 120,
  "h3_before_tw": 120, "h3_after_tw": 120,
  "separator_between_number_and_title": "tab"   // "tab" | "space"
},

"captions": {
  "placement": { "table": "above", "figure": "below" },
  "table_alignment": "center", "figure_alignment": "center",
  "bold": true,
  "appendix_prefix": "ผ."            // appendix objects: ตารางที่ ผ.1
},

"footer": {
  "text": "CONFIDENTIAL",                 // running footer text, or "" for none
  "size_pt": 10,
  "alignment": "left",
  "by_part": { "cover": "DRAFT" }         // optional per-part override
},

"keywords": {
  "label_th": "คำสำคัญ :", "label_en": "Keywords :",
  "separator_th": " ",  "separator_en": ", ",
  "min": 4, "max": 6
},

"structure": {
  "chapters": [
    { "number": 1, "file": "Chapter_01_Introduction.docx",
      "title": { "th": "บทนำ" },
      "sections": [ { "number": "1.1", "title": "…" } ],
      "required_keywords": ["วัตถุประสงค์", "ขอบเขต"],
      "last_section_keywords": ["งานวิจัย"] }
  ]
}
```

| Key | What it changes |
|---|---|
| `paragraphs.first_line_mode` | Both `w:ind w:firstLine` and a leading `<w:tab/>` are indentations in Word; real documents use either. `"tab"` also makes the **builder** emit the tab instead of the indent. |
| `headings.separator_between_number_and_title` | The book writes `3.1` ⇥ `title`, which extracts as `3.1title`. The gate checks the run structure rather than the extracted text. |
| `captions.placement` | Which side of the object the caption sits on. Houses differ — some captions sit above the object, others below the image. Measure it (`derive_profile.py`) instead of assuming. |
| `captions.appendix_prefix` | Appendix objects are numbered separately (`ตารางที่ ผ.1`), so the caption regex must accept that prefix. |
| `captions.bold` | Whether the caption line is bold. |
| `footer.*` | A running footer outside the page number (a confidentiality marking, the faculty name), with an optional per-part override. |
| `keywords.*` | The label, separator and count (R-31/R-32 mandate 4–6, one space in Thai). |
| `structure.chapters[].sections` | The delivered skeleton. A chapter that omits one is a **warning**, not a failure — houses allow a chapter to reshuffle its sections (R-39a, §13.6), but the user should confirm. |
| `structure.chapters[].last_section_keywords` | A hard rule: the last section of chapter 2 is the related-work section (R-40). |
| `structure.chapters[].required_keywords` | Sections a chapter must carry, matched by keyword so the wording can change. |
| `structure.chapters[].file` | The file each chapter lives in, for the folder inventory. |


### Part kinds

`front` entries are rendered in order. The kinds the builder knows:

| Kind | Renders |
|---|---|
| `cover` | the title page, in the given `lang` |
| `copyright` | the copyright page |
| `abstract` | the abstract, with the keywords line |
| `certification` | the certification / declaration sheet and its committee table |
| `acknowledgements` | the acknowledgements, signed right |
| `toc` | the contents page (a real `TOC` field) |
| `list_of_tables` | the list of tables (a `TOC \t "TableCaption,1"` field) |
| `list_of_figures` | the list of figures |
| `abbreviations` | the abbreviations table |

The leading `cover` and `copyright` parts are emitted unnumbered; everything after
them is numbered with `front_format`, and the body restarts at `body_start`.

`back` entries: `references`, `appendices`, `biography`.

`chapters` supplies the defaults for the chapter label and title lines. The spec
may override them per chapter.

### Labels

`labels` holds the visible strings: the heading of each part in each language, the
cover wording template, the certification fields, the committee rows and the
closing lines. Templates use `{placeholder}` tokens that are filled from the
book metadata (`{degree}`, `{department}`, `{institute}`, `{year}`); a token with
no value becomes `[TODO: token]` rather than an empty line.

### Editing a profile safely

- Keep `fonts.allowed` in sync with `fonts.body` — the checker treats anything
  outside `allowed` as a violation.
- Set `paragraphs.hint_cs` to `true` for any style that contains Thai, Arabic or
  other complex script, and `false` otherwise; the checker then skips the
  requirement instead of reporting a rule that does not apply.
- If the style allows plain justify, drop `"both"` from `forbidden_alignment`.
- Changing the profile changes the compliance result. Re-run the checker after
  every edit — the point of the profile is that the checker and the builder can
  never disagree.

## The bundled default profile

`assets/default_profile.json` is the Thai KMITL Faculty of Science house style for
thesis and co-op reports, extracted from that faculty's template and codified as
rules `R-01`…`R-64` with the format profile `P-01`…`P-14`:

- A4, 1.5 in left binding margin, 1 in elsewhere, header/footer 0.5 in
- TH SarabunPSK only — body 16 pt, chapter label 20 pt, chapter title 24 pt,
  section heading 18 pt, sub-section 16 pt, front-matter heading 24 pt, abstract
  heading 17 pt, cover title 20 / name 18 / meta 16 pt, table text 14 pt,
  captions 16 pt
- body alignment `thaiDistribute` (never `both`), first-line indent 0.5 in,
  6 pt after each paragraph, hanging indent 0.5 cm for numbered items
- captions centred above the object, chapter-relative numbering, a source line
  below
- front matter in roman numerals, the body restarting at arabic 1, the page
  number centred in the header, no number on the covers
- the book order: Thai cover → English cover → copyright → Thai abstract →
  English abstract → certification → acknowledgements (Thai) → acknowledgements
  (English) → contents → list of tables → list of figures → abbreviations →
  chapters 1–5 → references → appendices → author biography

Use it as the starting point for a Thai report with no style of its own, and as a
worked example of how a profile expresses a house style. It is **one** style, not
the standard: when a project has its own documents, derive a profile from them.

