# The Word backend

Use this path when Word is running on the machine. It gives native Thai layout, live
field refresh and a PDF for visual proof. It is the higher-fidelity option; the
Python builder stays the fallback for headless and RHEL 7 environments.

The Word MCP tools are named `mcp__word_mcp_*`; the ones listed below are the ones
that matter for report work.

## Which tool to reach for

| Need | Tool |
|---|---|
| What is open in Word right now | `mcp__word_mcp_word_live_list_open` |
| Page / word count, section count | `mcp__word_mcp_word_live_get_info` |
| Read the text of an open document | `mcp__word_mcp_word_live_get_text` |
| Insert paragraphs | `mcp__word_mcp_word_live_insert_paragraphs` |
| Format runs (font, size, bold) | `mcp__word_mcp_word_live_format_text` |
| Page layout of a section | `mcp__word_mcp_word_live_set_page_layout` |
| Header / footer text | `mcp__word_mcp_word_live_add_header_footer` |
| Page numbers in header or footer | `mcp__word_mcp_word_live_add_page_numbers` |
| Refresh the fields | `mcp__word_mcp_word_live_get_diff` after `select all` + `F9`, or via COM (below) |
| Save | `mcp__word_mcp_word_live_save` |
| Export a PDF | `mcp__word_mcp_convert_to_pdf` (file-based) or COM `ExportAsFixedFormat` |

Editing live in Word is the right tool for a *small correction* to an existing
document — a heading that lost its size, a caption in the wrong place, a page
number that vanished. For a whole chapter, the Python builder is faster and more
reproducible, and then Word only has to refresh the fields.

## Refreshing fields through COM

The contents, list of tables and list of figures are fields. Their page numbers are
only correct after Word repaginates and rebuilds them.

```python
import pythoncom, win32com.client as win32

pythoncom.CoInitialize()
word = win32.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
doc = word.Documents.Open(path, ReadOnly=False, AddToRecentFiles=False)
doc.Repaginate()
doc.Fields.Update()
doc.Repaginate()
doc.Fields.Update()      # second pass settles the page numbers
doc.SaveAs2(pdf_path, FileFormat=17)   # 17 = wdFormatPDF
doc.Close(SaveChanges=0)
word.Quit()
```

Repaginate first, update twice: the first `Fields.Update()` rebuilds the field
results on the previous pagination, so the numbers can lag one page behind.

### "Call was rejected by callee" / "a macro is currently running"

Word refuses document-level commands while it is busy. This is not a document
defect — retry:

```python
BUSY_CODES = {-2147418111, -2147352567}   # RPC_E_CALL_REJECTED, "command not available"

def retry(fn, tries=8, delay=1.5):
    last = None
    for _ in range(tries):
        try:
            return fn()
        except Exception as exc:                      # noqa: BLE001
            busy = getattr(exc, "args", [None])[0] in BUSY_CODES
            if not busy:
                for arg in getattr(exc, "args", ()):
                    if isinstance(arg, tuple) and any("37373" in str(x) for x in arg):
                        busy = True
            if not busy:
                raise
            last = exc
            time.sleep(delay)
    raise last
```

If `TablesOfContents(i).Update()` keeps refusing while `doc.Fields.Update()`
succeeds, use the latter — it produces the same rebuilt field, which is what the
`F9` key does.

## Verifying what Word produced

Do not trust the XML alone. After building:

1. run `scripts/check_report.py` on the `.docx` with the project's profile — it checks
   every rule the profile defines;
2. export a PDF and read a few pages — the page numbers, the Thai line breaking and
   the image placement are only visible in the rendered output.

```bash
python scripts/check_report.py Report.docx --profile house_style.json
```

## Editing an existing chapter instead of rebuilding it

When the task is "add section 3.4 to the chapter I already wrote", do not rebuild the
chapter from a spec — that risks losing hand-written prose. Open it in Word and
edit in place, then run the checker on the result: it reports the rule IDs that the
edit broke, which is the fastest way to keep a hand-edited document compliant.
