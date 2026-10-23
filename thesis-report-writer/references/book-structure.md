# Book structure and chapter content

## How to read a house style's structure

Most report houses define the book in three lists. They appear in the rules file
in prose, in the template as its table of contents, or in the profile's
`structure` block:

1. **Front matter** — the parts before the body, in order.
2. **The body** — the numbered chapters, and the sections each chapter must have.
3. **Back matter** — references, appendices, and the author biography.

Extract them into the profile's `structure` block, and keep the parts' visible
names in `labels`. The builder then emits exactly that order, and the checker
verifies that every part is present.

Two rules hold nearly everywhere:

- **Every part starts on a new page.** A page break, not a run of empty
  paragraphs — empty paragraphs collapse when the document is edited.
- **Front matter is numbered separately from the body.** Roman numerals for the
  front, arabic restarting at 1 for chapter 1, the page number centred in the
  header, and no number on the covers and the copyright page.

## The common front matter

| Part | What belongs in it |
|---|---|
| Cover (per language) | the title in that language, the author's name, the degree statement, the department, faculty and institution, the year, the document number, the advisor |
| Copyright | the institution, the title, the author, the student id, the degree, the department, the advisors, the year |
| Abstract | a short summary of the problem, the method, the results and the meaning, then a keywords line |
| Certification / declaration | the title, the author, the degree, the supervisor, the examination date **with the time**, the venue, and a committee table with signature space |
| Acknowledgements | who helped, and how |
| Contents | a real `TOC` field, not a typed-out list |
| List of tables / list of figures | one row per object, with its page number |
| Abbreviations / symbols | only when the book uses them |

The keywords line usually has a fixed shape: four to six terms, one space between
them in Thai, comma-separated in English, and the same order in both languages so
the two versions of the book correspond.

## The body chapters

Chapters almost always have a label line ("บทที่ 1" / "Chapter 1") and a title
line, each centred and bold at its own size, and then a set of numbered sections
("1.1", "1.2", …) with optional sub-sections ("2.1.1").

The **sections a chapter must contain** come from the house style. The common
pattern, and the one the bundled default profile encodes:

| Chapter | Must contain |
|---|---|
| 1 Introduction | background and importance of the problem; objectives (as numbered items); scope (as numbered items); expected benefits (as numbered items) |
| 2 Theory and related work | the theory and prior work the study builds on — the literature review is normally the *last* section of this chapter, not an optional extra |
| 3 Methodology | how the work was done, in enough detail that somebody else could repeat it: the system, the workflow, the tooling |
| 4 Results and discussion | the interpretation of the data, the conclusions reached, and the comparison with previous work |
| 5 Conclusions and suggestions | what was concluded, and what should be done next |

When a rules file specifies sections, follow it exactly and quote its IDs back to
the user. When it says a section may be added or removed per department, keep the
mandatory ones.

## Back matter

| Part | What belongs in it |
|---|---|
| References | the citations, in the department's own format — a template usually points at a citation guide rather than showing samples |
| Appendices | long tables, code listings, raw data; keep the heading even when the appendix is still empty |
| Author biography | name, date of birth, address, education history, scholarships, publications |

## Drafting one file per chapter

While drafting, one `.docx` per chapter is usually the practical unit
(`Chapter_01.docx`, `Chapter_02.docx`). Page numbers restart in each file, and
joining them into one book later needs section breaks so the numbering runs on —
which is exactly what the builder's `mode: "full"` produces, since it emits real
sections with explicit page-number formats.

Use `mode: "chapter"` for a single chapter file and `mode: "full"` for the
assembled book. The compliance checker's `--mode` should match: `chapter` skips
the checks that only make sense for a whole book (the presence of every front and
back matter part).

## Writing the content

- Lead with the finding, not with the background.
- Prefer a specific number to a vague claim — and if the number does not exist
  yet, mark it `[TODO: ...]` rather than approximating.
- Keep the section numbering consistent with the book; the builder does not
  renumber anything for you.
- One table or figure per block, with the explanatory paragraph *before* it.
