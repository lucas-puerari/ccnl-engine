"""Regenerate docs/contracts/index.md from the knowledge-base JSON files.

Run with::

    uv run python scripts/docs/gen_coverage_matrix.py

Check for drift without writing (for CI)::

    uv run python scripts/docs/gen_coverage_matrix.py --check

Or via Make::

    make coverage-matrix
"""

import re
import sys
from pathlib import Path

# scripts/docs/ — add this directory to sys.path for the sibling import
sys.path.insert(0, str(Path(__file__).parent))

from coverage_report import (
    build_coverage_report,
    render_contracts_index,
)

_DATE_LINE_RE = re.compile(r"<!-- generated: \d{4}-\d{2}-\d{2} -->\n?")


def _strip_date(text: str) -> str:
    return _DATE_LINE_RE.sub("", text)


check_mode = "--check" in sys.argv
report = build_coverage_report()
root = Path(__file__).parent.parent.parent
contracts_index = root / "docs" / "contracts" / "index.md"
generated = render_contracts_index(report)

if check_mode:
    committed = contracts_index.read_text(encoding="utf-8")
    if _strip_date(generated) != _strip_date(committed):
        print("docs/contracts/index.md is out of date.", file=sys.stderr)
        print(
            "Run: uv run python scripts/docs/gen_coverage_matrix.py",
            file=sys.stderr,
        )
        print("and commit the result.", file=sys.stderr)
        sys.exit(1)
    print(f"OK — docs/contracts/index.md is up to date ({len(report.ccnl_rows)} CCNL).")
else:
    contracts_index.write_text(generated, encoding="utf-8")
    print(f"Written {contracts_index} ({len(report.ccnl_rows)} CCNL)")
