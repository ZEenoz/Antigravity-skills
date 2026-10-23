# Tables, figures, captions and the lists

The caption labels, the alignment and the spacing all come from the style profile
(`captions` block), so the rules below are the common case — the profile decides
the exact wording, for example `ตารางที่` versus `Table`.

## The flow is fixed

### Table

```
explanatory paragraph
        ↓
caption            ← centred, above the table
        ↓
[ the table ]
        ↓
source line        ← below the table
        ↓
next paragraph
```

### Figure

```
explanatory paragraph
        ↓
caption            ← centred, above the image
        ↓
[ the image ]
        ↓
next paragraph
```

While drafting a figure that does not exist yet, the caption line says so —
`รูปที่ 2.x (แปะรูป) <what the figure shows>` in the Thai style, `Figure 2.x
(placeholder) …` in the English one — and stays centred.

Things that are easy to get wrong:

- The caption is **above** the object, never below.
- The source or reference line goes **below** a table; for a figure it goes below
  the image.
- Rules and borders span the full content width.
- A short caption is centred; a long caption is left-aligned.

## Numbering

Numbers are **chapter-relative**: `ตารางที่ 3.4` / `Table 3.4` is the fourth
table in chapter 3, and `รูปที่ 3.4` / `Figure 3.4` the fourth figure.

- A number is never reused inside a chapter.
- Every table and figure in the body also appears in the list of tables / list of
  figures, in the same order as it appears in the text.
- The number depends on the position inside the chapter, so it is written as plain
  text rather than as a `SEQ` field: the chapter label in most house styles is
  literal text, so a `STYLEREF`-based automatic number cannot resolve it. Write
  the number by hand and let the compliance checker confirm that it is unique.

## Table style

- Full grid: every cell has a border, not only the outer frame. The builder writes
  `w:tblBorders` on every edge (`top`, `left`, `bottom`, `right`, `insideH`,
  `insideV`) so the look does not depend on a named style being present.
- Cell text uses the profile's `table` size; the caption keeps the profile's
  `caption` size.
- The header row is bold.
- Some departments require the table format of the accepting institution instead —
  check before assuming the grid.

## Figures

- An image never exceeds the content column: the page width minus the left and
  right margins (`page.width_mm - margin_left_mm - margin_right_mm`).
- Images are centred in their paragraph.
- Give every figure a caption and a source line. A screenshot taken from the
  project's own tool is still a source (`(Source: …)`).

## Lists of tables and figures

Both are real Word fields in the builder:

- list of tables → `TOC \h \z \t "TableCaption,1"`
- list of figures → `TOC \h \z \t "FigureCaption,1"`

The page numbers appear once Word has repaginated and rebuilt the fields — press
`Ctrl+A` then `F9` in Word, or drive the same calls from the Word MCP tools
(`references/word-backend.md`). Until then the field shows a placeholder line.

The checker verifies that a list-of-tables field exists whenever the document has
table captions, and the same for figures, and that every caption sits directly
above the object it labels.
