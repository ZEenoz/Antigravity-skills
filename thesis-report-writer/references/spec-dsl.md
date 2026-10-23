# The content spec (JSON) the builder consumes

The builder never invents content: it turns a JSON description of the document
into a styled `.docx`. Keeping the content in a spec file means the prose can be
reviewed and diffed independently of the formatting.

```bash
python scripts/build_report.py --spec spec_ch03.json --out Chapter_03.docx \
  [--profile house_style.json]
```

## Top level

```json
{
  "language": "th",
  "mode": "full",
  "base_dir": "C:/path/to/repo",
  "book": { ... },
  "parts": [ ... ]
}
```

| Key | Values | Meaning |
|---|---|---|
| `language` | `"th"`, `"en"`, … | language of the generated book; selects the labels, the cover wording and the keywords separator |
| `mode` | `"full"`, `"chapter"` | `full` builds the whole book (front matter, body, back matter); `chapter` builds only the numbered parts, for drafting one file per chapter |
| `base_dir` | path | root for relative image paths; defaults to the spec's own directory |
| `book` | object | metadata for the front and back matter |
| `parts` | array | chapters and appendices, in order |

## `book`

Every field is optional; a missing one produces an empty or skipped part.

| Key | Meaning |
|---|---|
| `title_th`, `title_en` | the title in each language |
| `student_th`, `student_en` | the author's name; the cover prints "by \<name\>" in the English style |
| `student_id` | student id, shown on the copyright page and the certification sheet |
| `degree_th`, `degree_en` | the degree |
| `department_th`, `department_en` | the department |
| `faculty_th`, `faculty_en` | the faculty |
| `institute_th`, `institute_en` | the institution |
| `year_th`, `year_en` | the year in each convention (Buddhist and Gregorian, for instance) |
| `doc_no` | the document number, printed after the institution's prefix |
| `advisor`, `co_advisor` | the supervisors |
| `exam_date`, `exam_place` | the certification sheet: the date **with the time**, and the venue |
| `abstract_th`, `abstract_en` | arrays of paragraphs for the two abstracts |
| `keywords_th`, `keywords_en` | arrays of terms; the Thai list is space-separated, the English one comma-separated, in the same order in both |
| `acknowledgements_th`, `acknowledgements_en` | arrays of paragraphs |
| `abbreviations` | array of `{"abbr": "SMT7", "full": "SmarTest 7"}` |
| `references` | array of reference strings |
| `biography` | array of paragraphs for the author biography |

Cover statements are templates in the profile (`labels.cover_statement`) with
`{placeholder}` tokens. The builder resolves `{degree}` from `book.degree` or
`book.degree_en`, and writes `[TODO: degree]` when the value is missing, so an
unfilled field is visible instead of silently blank.

## `parts`

Each part is a chapter or an appendix:

```json
{
  "kind": "chapter",
  "number": 3,
  "label": "บทที่ 3",
  "title": "วิธีการดำเนินงานวิจัย",
  "blocks": [ ... ]
}
```

- `kind`: `"chapter"` or `"appendix"`.
- `number`: the chapter number; the label defaults to the profile's
  `chapter_label_prefix` plus the number, and the title defaults to the profile's
  `structure.chapters` entry for that number.
- `label`: the chapter label line.
- `title`: the chapter title line.
- `blocks`: the body of the part, in order.

An appendix is `{"kind": "appendix", "title": "ภาคผนวก ก", "blocks": [...]}`.

## Blocks

| `kind` | Fields | Renders as |
|---|---|---|
| `h2` | `number` (`"3.1"`), `text` | section heading — the profile's `h2` size, bold, left |
| `h3` | `number` (`"3.1.1"`), `text` | sub-section heading — the profile's `h3` size, bold, left |
| `p` | `text` | body paragraph — the profile's first-line indent, space after and alignment |
| `plain` | `text` | paragraph without the first-line indent |
| `list` | `items` | items with the profile's hanging indent; the number is part of the text (`"1. …"`) |
| `bullets` | `items` | dash-prefixed items |
| `table` | `caption` or `number`+`text`, `header`, `rows`, `source` | caption above, grid table, source line below |
| `figure` | `caption` or `number`+`text`, `image`, `width_cm`, `source` | caption above, centred image, source line below |
| `pagebreak` | — | explicit page break |
| `quote` | `text` | italic, indented block |

When a table or figure block gives `number` and `text` but no `caption`, the
builder composes the caption from the profile's label: `ตารางที่ 3.1 <text>` or
`Table 3.1 <text>`. When it gives `source` without parentheses, the builder wraps
it in the profile's source prefix.

Examples:

```json
{ "kind": "h2", "number": "3.1", "text": "ภาพรวมของระบบ" },
{ "kind": "p", "text": "ระบบประกอบด้วยส่วนแสดงผล ส่วนแปลงไฟล์ และส่วนตรวจสอบความถูกต้อง" },
{ "kind": "list", "items": ["1. อ่านไฟล์ Digital Pattern", "2. แสดงผลรูปคลื่นสัญญาณ"] },
{ "kind": "table",
  "number": "3.1",
  "text": "รูปแบบไฟล์ที่รองรับ",
  "header": ["รูปแบบ", "คำอธิบาย"],
  "rows": [["SmarTest 7", "ไฟล์ .mfh .pin .lev .tim"], ["SmarTest 8", "ไฟล์ .pat ที่บีบอัดด้วย ZIP"]],
  "source": "ผู้จัดทำ" },
{ "kind": "figure",
  "number": "3.1",
  "text": "ภาพรวมการทำงานของระบบ",
  "image": "docs/figures/system-overview.png",
  "width_cm": 13.0,
  "source": "ภาพจากโปรแกรม Visualizer Digital Pattern" }
```

`image` paths are resolved against `base_dir` when they are not absolute. A
missing image is a hard error naming the resolved path — fix the path rather than
dropping the figure silently.

## Writing the spec

- Keep the section numbering consistent with the house style; the builder does not
  renumber anything for you.
- Number tables and figures chapter-relative and never twice in the same chapter.
- Put the explanatory paragraph *before* the table/figure block: the builder emits
  the caption directly above the object, and the text that introduces it belongs
  in the preceding `p` block.
- Write the file as UTF-8; Thai and other non-ASCII text is expected.
