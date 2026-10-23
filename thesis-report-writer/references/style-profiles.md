# Style profiles — the house style as data

A style profile is one JSON file that carries every measurable decision of a house
style. The builder applies it, the checker verifies against it. Because the style
lives in data rather than in code, the same tooling serves any institution: change
the profile, not the scripts.

## Where a profile comes from

| Source | How |
|---|---|
| A written rules file | Read the values out of it and write the profile by hand. The rules file stays the authority; the profile is its machine-readable shadow. |
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
worked example of how a profile expresses a house style.
