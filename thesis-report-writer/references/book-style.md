# Deriving a house style from the documents you already have

Most report projects answer "what is the format?" with a rules file and a folder of
`.docx` files that somebody already wrote. Both are evidence, and they disagree.
This page is the procedure for turning that pair into one profile the builder and
the gate can both use — for any institution, not one particular book.

## 1. Decide what each source is

| Source | Role |
|---|---|
| Rules / style guide (prose, rule IDs) | What the style is *supposed* to be |
| A blank template from the department | The intended geometry, sometimes stale |
| Documents already written and accepted | What the house *actually* accepts |
| The rendered PDF of the finished book | The only source for rendered size and position |

Read the rules file that carries the IDs, not only a summary of it. Projects often
keep a long authoritative file (`RULES_*.md`, `thesis_style.md`) and a short working
copy that defers to it; the small print differs, and the gate will find it.

## 2. Measure, do not infer

Run the deriver over every part you have — chapters, abstract, appendix — not one
file. The style lives in the majority, so a single odd page cannot set it.

```bash
python scripts/derive_profile.py -o house_style.json --name "My faculty style" \
    docs/thesis/*.docx --rules docs/RULES.md
```

It reports the majority value for:

- page size, all four margins, header and footer distance, gutter
- the default font and every font the document actually references
- body / chapter-label / chapter-title / section / sub-section / table / caption sizes
- body alignment, space after (body vs heading), list indent
- **how the first-line indent is spelled** — `w:ind w:firstLine` or a leading
  `<w:tab/>`; documents written by different people use both
- heading spacing and whether the number and title are joined by a tab or a space
- caption label words, caption side (**above** or **below** the object), size,
  boldness, alignment and spacing, per table and per figure
- the appendix object prefix (`ผ.`, `A-`, none)
- the running footer text, its alignment and size, and every variant found
- page-number format and the header alignment of the `PAGE` field
- the keywords label, separator and count
- whether `<w:applyBreakingRules/>` is present

Start from the bundled profile when you only want to change a few values:

```bash
python scripts/derive_profile.py -o house_style.json --base assets/default_profile.json \
    docs/thesis/*.docx
```

`inspect_docx.py` still exists for a single quick read of one document.

## 3. Fill what a document cannot tell you

The deriver cannot see intent. Add these by hand from the rules file:

| Field | Where it comes from |
|---|---|
| `structure.front` / `structure.back` | The order of the parts in the guide or the blank template |
| `structure.chapters[].title` | The chapter titles the guide mandates |
| `structure.chapters[].sections` | Sections each chapter must carry; optional per house |
| `labels.*` | The visible heading of each part, the cover statement, the declaration sheet |
| `rules.authoritative` | Path of the ID-bearing rules file |
| `rules.ids` | Which rule IDs each check enforces (see below) |
| `rule_deltas` | Every place the documents and the rules disagree, with evidence |

## 4. Record the disagreements

Rules documents and delivered documents disagree constantly. Do not silently pick
one: write the decision into the profile so the next run reports it instead of
re-deciding it.

```jsonc
"policy": "An explicit value in the delivered documents wins; an omitted value
           falls back to the written rules.",
"rule_deltas": [
  {
    "rule": "R-02 / P-02",
    "item": "page.margin_top_mm",
    "stated": "1.0 in (25.4 mm)",
    "in_book": "1.5 in on every delivered file",
    "evidence": "w:pgMar w:top=\"2160\" in all thirteen parts",
    "decision": "the book's value is used"
  }
]
```

Decide in one of two directions, and name it:

- **The documents win** when their value is a deliberate choice — a binding
  allowance, a university footer, a caption below the figure because the style
  sheet for figures in that faculty says so.
- **The rules win** when the document's value is an *omission* rather than a
  choice: heading styles that carry no `w:sz` and therefore render at body size,
  a page number that drifted right, a missing script hint. Those are defects the
  gate should keep reporting.

## 5. Wire the rule IDs

If the rules file numbers its rules, map each check to the IDs it enforces so the
gate can quote them:

```jsonc
"rules": {
  "authoritative": "docs/RULES.md",
  "ids": {
    "page-setup":    ["R-01", "R-02", "P-01"],
    "fonts":         ["R-05", "R-14"],
    "script-hint":   ["R-14"],
    "alignment":     ["R-05", "P-06"],
    "heading-sizes": ["R-06", "R-07", "P-07"],
    "footer":        ["P-03"]
  }
}
```

A check with no mapping prints without brackets. Unknown IDs are harmless, but
verify them against the rules file — a wrong ID is worse than none.

## 6. Verify the profile before trusting it

```bash
python scripts/check_report.py <one representative part> --mode chapter \
    --profile house_style.json
```

Read the `rule-deltas` warnings and confirm each decision is the one you meant.
Then check that a document the house considers *correct* comes out green, and one
with a known defect comes out red. A profile that reports every file as compliant
is not measuring anything.

## 7. Keep it with the project

Store the profile next to the documents (`docs/thesis/house_style.json`) and pass it
with `--profile` on every build and every audit. The bundled
`assets/default_profile.json` is a starting point, not a standard: re-deriving it
for each project is what keeps the gate honest.
