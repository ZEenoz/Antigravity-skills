#!/usr/bin/env python3
"""
make_master.py -- derive an empty house-master .docx from an existing compliant report.

Why this exists (rules file, section 16.2): a .docx built from scratch with python-docx
does not break Thai lines the way Word does, because the run property w:hint="cs" and the
setting <w:applyBreakingRules/> are missing. Copying a report that already renders
correctly and stripping its body keeps styles.xml, settings.xml and header1.xml intact.

Usage:
    python make_master.py --from Ch01.docx --out house_master.docx
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


def strip_body(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    doc = Document(str(dst))
    body = doc.element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)
    doc.save(str(dst))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="src", required=True, help="source .docx to copy from")
    ap.add_argument("--out", dest="dst", required=True, help="house-master .docx to write")
    args = ap.parse_args(argv)

    src, dst = Path(args.src), Path(args.dst)
    if not src.exists():
        print(f"error: source not found: {src}")
        return 1
    strip_body(src, dst)
    print(f"house master written: {dst}")
    print("  body content stripped; styles.xml, settings.xml and headers preserved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
