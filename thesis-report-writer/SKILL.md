---
name: thesis-report-writer
description: Write, extend, reformat and audit thesis, co-op, dissertation and internship report documents (.docx) in whatever house style the target project or department requires - paper size, margins, fonts, heading sizes, paragraph geometry, chapter structure, numbered tables and figures, contents/list fields, page numbering - and verify the result with a machine-checked compliance report. Use this skill whenever the user asks to write or draft a chapter, abstract, table of contents, list of tables or appendices for a report or thesis; to reformat or restyle an existing .docx report; to add tables and figures with the correct caption flow; to check whether a report matches a template or a written formatting rules file; or mentions a thesis/co-op template, a formatting rules document, a report template, เล่มสหกิจ, รายงานสหกิจศึกษา, วิทยานิพนธ์ or a dissertation - even if they never say "docx" and even if they only ask for one chapter.
---

# Thesis & Co-op Report Writer

Reports are written to a **house style**: a template, a written rules file, or a
document somebody already wrote. The style decides paper size, margins, fonts and
sizes, paragraph geometry, the order of the parts, how tables and figures are
captioned and numbered, and how pages are numbered. The content is a separate
problem, and so is the machinery.

This skill separates the three:

| Piece | What it is | Where |
|---|---|---|
| **Style profile** | The house style as data — one JSON file, portable between projects | `assets/default_profile.json`, `scripts/inspect_docx.py` |
| **Builder** | Applies a profile mechanically to a content spec | `scripts/build_report.py` |
| **Compliance gate** | Verifies the produced `.docx` against the same profile | `scripts/check_report.py` |
| **Content contract** | What each part of a report must contain | `references/` |

The division of labour is the point. The *style* is deterministic and belongs in a
script: a model re-deriving OOXML by hand gets the font hints wrong and Thai or
Arabic text scatters across the line, and a style applied by hand drifts while a
style applied by a script can be checked by a script. The *prose* is judgement work
and stays with you.

The bundled profile is the Thai KMITL Faculty of Science thesis style — one
instance, useful as a starting point and as a worked example. Any other
institution's style is expressed by editing the profile or by extracting one from a
reference document; nothing in the machinery is tied to that institution.

Paths in this file are relative to the skill directory (`scripts/…`, `assets/…`,
`references/…`).

## Step 0 — Establish the house style before writing anything

Find the style in this order, and stop at the first hit:

1. **A written rules file.** Look for something like `*RULES*.md`, `*style*.md`,
   `docs/**/format*.md`, `Docs_Rules.md`, a template description in the README. It
   usually states the values in prose and sometimes in rule IDs — quote those IDs
   back to the user, because they let a reader verify a claim without re-reading
   the whole guide.
2. **A template document.** A `.docx` or `.potx` from the department. Extract the
   measurable values from it:

   ```bash
   python scripts/inspect_docx.py template.docx -o house_style.json --inherit-structure
   ```

   The detector reads the page setup, the fonts and their sizes, the paragraph
   metrics, the caption rules and the page-numbering formats. It cannot see the
   *structure* (which parts the book has, what they are called) — that comes from
   the template's own table of contents or from the rules file.
3. **The bundled default profile**, and say so plainly. Use it when the project has
   no style of its own, and note in your report that the Thai co-op style was
   assumed.

Then adjust the profile to match what the rules file says. The profile is the
contract: the builder applies it and the checker verifies against it, so a
disagreement between the two is impossible by construction.

**Resolving conflicts between sources.** Rules documents disagree with each
other, and the disagreement is often stated inside the documents themselves
("where the two disagree, file B wins"). Read the *values*, not the summaries:
when two rules appear to conflict, check which value each one actually states
before deciding. Copy the value verbatim into the profile and note the conflict
in your report. A working example from a real Thai house style: the working copy
and the authoritative rules file both require Thai Distributed alignment, and the
authoritative file additionally explains why plain justify is banned — reading
only the headings of either document is enough to get this backwards, and the
compliance gate will catch the mistake.

## Step 1 — Plan the structure

The book's parts and their order come from the profile (or from the rules file):
front matter (covers, copyright, abstract, certification, acknowledgements,
contents, lists of tables and figures, abbreviations), the numbered chapters, then
references, appendices and the author biography. Every part starts on a new page —
a page break, never a run of empty paragraphs.

Chapters carry mandated sections in most houses. When the rules file specifies
them, follow it exactly; `references/book-structure.md` lists the common ones and
explains how to read them from a rules file.

While drafting, one file per chapter is usually the practical unit
(`Chapter_01.docx`, `Chapter_02.docx`). Page numbers restart per file; joining
them later needs section breaks, which is what the builder's `mode: "full"`
produces.

## Step 2 — Gather the facts; never invent them

The academic content must come from real material: the repository, existing
reports, the source tree, the user's own notes. Write down where each claim came
from. If a number, a result or a citation is not in the material you have, either
leave a clearly marked placeholder (`[TODO: measured latency]`) or state the gap in
your report — do not fabricate a measurement, a schedule or a reference. A report
with an honest gap is fixable; a report with invented numbers is not.

## Step 3 — Write the content spec

Describe the document as JSON: book metadata plus an ordered list of parts, each
with ordered blocks (`h2`, `h3`, `p`, `list`, `table`, `figure`, `pagebreak`). The
schema is in `references/spec-dsl.md`. Keep the spec in a file — it is reviewable,
diffable and re-runnable, which a pile of ad-hoc python-docx calls is not.

## Step 4 — Build

```bash
python scripts/build_report.py --spec spec_ch03.json --out Chapter_03.docx \
  [--profile house_style.json] [--master house_master.docx]
```

The builder uses the neutral Word-authored master bundled in `assets/` by default.
That master matters (see *Traps*): it carries the `styles.xml`, `settings.xml` and
header parts that make Word accept the document. Point `--master` at a template or
an existing report to inherit a project's own look; `scripts/make_master.py`
derives one from any reference document.

## Step 5 — The compliance gate

```bash
python scripts/check_report.py Chapter_03.docx --profile house_style.json \
  [--mode full|chapter]
```

The checker prints one line per rule with `PASS` / `FAIL` / `WARN` and exits
non-zero on any `FAIL`. **Do not report the work as done while a FAIL remains** —
fix the cause and re-run until it is green. `--json <file>` writes machine-readable
results when you need to diff two versions.

It checks what a machine can check: page setup, the font set, script hints,
alignment, heading sizes, first-line indents, spacing, list indents, the
page-number field and its formats, the contents field, caption placement and
numbering, table borders, and the presence of every part the profile prescribes.
It cannot judge whether your prose is good — that part stays yours.

Match `--mode` to what you built: `full` for a whole book, `chapter` for a single
chapter file. The front-matter rules (contents page, lists of tables and figures,
the part inventory) belong to the assembled book, so in `chapter` mode they are
reported as not applicable rather than as failures — a chapter file legitimately
has no contents page.

## Step 6 — Refresh the fields in Word, then check again

The contents, list of tables and list of figures are real Word fields. Their page
numbers only become correct after Word repaginates and rebuilds them. Open the
file in Word and press `Ctrl+A`, then `F9` (choose *Update entire table*), or drive
it from the Word MCP tools — `references/word-backend.md` has the exact calls and
the retry pattern that Word's COM interface needs.

**Word rewrites the file when it saves.** A field refresh followed by a save makes
Word normalise runs, and it can drop the direct font, size and script-hint
properties the house style depends on. Run the compliance gate *after* the Word
step, not only before it: if the gate then reports a font, hint or spacing
failure that the freshly built file did not have, re-apply the affected
properties (the builder's run-level formatting is what Word drops) and check
again.

## Choosing the backend

| Situation | Backend |
|---|---|
| Word is running on this machine | **Word MCP** — highest fidelity, native layout, live field refresh |
| No Word (headless, CI, a Linux build box) | **Python builder** — deterministic and portable; the user refreshes the fields once in Word later |
| Auditing an existing `.docx` | **Checker only** — never rebuild a document you were only asked to inspect |
| Editing an existing chapter | Word MCP if available; otherwise the builder with a spec extracted from the current file |

The Python builder is always the fallback and always produces a compliant document.

## Traps this style work has

Each of these has been hit while producing reports; they are the reason the
machinery exists.

- **Complex-script text scatters across the line.** Word only breaks Thai with
  `w:hint="cs"` on every run *and* `<w:applyBreakingRules/>` inside `<w:compat>`
  in `word/settings.xml`. The element belongs inside `<w:compat>`; appending it to
  the end of `<w:settings>` makes the package schema-invalid, and Word then
  refuses document-level commands such as repaginating and rebuilding the
  contents page.
- **Plain justify (`w:jc="both"`) is wrong for Thai.** Thai sentences contain few
  spaces, so justify stretches those few spaces into rivers. Use `thaiDistribute`,
  which distributes at the break points Word can find.
- **Heading styles inherit the wrong font.** The template's `Heading 1`–`Heading 4`
  often point at a theme font and the document defaults at something else. Keep the
  real Heading styles (the contents field needs their outline levels) but set font
  and size *directly* on every run — a theme font reference overrides `w:ascii`,
  so setting the style alone is not enough.
- **A section break copies the previous section's header.** Two sections then share
  one header part and the cover page inherits the body's page number. Give each
  section its own header part.
- **Caption placement is fixed.** Table: explanatory text → blank line → caption →
  table → source line. Figure: explanatory text → caption → image. Captions sit
  *above* the object.
- **Numbering is chapter-relative and never reused**: `Table 3.4` is the fourth
  table in chapter 3. Every table and figure must also appear in the list of
  tables / list of figures.
- **Lists are indented, not tabbed**: a hanging indent, with the number typed as
  part of the text.
- **A machine without Thai proofing tools** shows extra gaps inside Thai words
  even in Word-authored documents. It is an environment artifact, not a formatting
  bug — do not "fix" it by changing the alignment.

## Reference map

Read these when the task touches them, not upfront.

| File | Read it when |
|---|---|
| `references/style-profiles.md` | You are deriving, editing or debugging a style profile |
| `references/book-structure.md` | You are planning the book or a chapter's content |
| `references/tables-and-figures.md` | You are adding a table, a figure, a caption or a list |
| `references/spec-dsl.md` | You are writing the JSON content spec the builder consumes |
| `references/word-backend.md` | Word is available and you want the highest-fidelity path |

## What to report back

Keep it short and verifiable:

1. the file(s) produced, with paths;
2. the compliance result — the pass/fail line from the checker;
3. which house style you applied (profile file, rules file or template), and any
   rule you deliberately deviated from, with the reason;
4. anything you could not fill in because the facts were not available — name the
   gap rather than filling it with a plausible sentence.
