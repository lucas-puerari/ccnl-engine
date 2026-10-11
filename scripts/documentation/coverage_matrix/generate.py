"""Regenerate docs/contracts/index.md from the knowledge-base JSON files.

Run with::

    uv run python scripts/documentation/coverage_matrix/generate.py

Check for drift without writing (for CI)::

    uv run python scripts/documentation/coverage_matrix/generate.py --check

Or via Make::

    make generate
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.documentation.coverage.loaders import (
    build_coverage_report,
    latest_catalog_year,
    render_contracts_index,
)

_DATE_LINE_RE = re.compile(r"<!-- generated: \d{4}-\d{2}-\d{2} -->\n?")


def _strip_date(text: str) -> str:
    return _DATE_LINE_RE.sub("", text)


check_mode = "--check" in sys.argv
year = latest_catalog_year()
report = build_coverage_report(year)
root = Path(__file__).resolve().parents[3]
contracts_index = root / "docs" / "contracts" / "index.md"
generated = render_contracts_index(report, year)

if check_mode:
    committed = contracts_index.read_text(encoding="utf-8")
    if _strip_date(generated) != _strip_date(committed):
        print("docs/contracts/index.md is out of date.", file=sys.stderr)
        print(
            "Run: uv run python scripts/documentation/coverage_matrix/generate.py",
            file=sys.stderr,
        )
        print("and commit the result.", file=sys.stderr)
        sys.exit(1)
    print(f"OK — docs/contracts/index.md is up to date ({len(report.ccnl_rows)} CCNL).")
else:
    contracts_index.write_text(generated, encoding="utf-8")
    print(f"Written {contracts_index} ({len(report.ccnl_rows)} CCNL)")
