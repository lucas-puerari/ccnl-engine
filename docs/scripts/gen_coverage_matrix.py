"""Regenerate docs/contracts/index.md from the knowledge-base JSON files.

Run with::

    uv run python docs/scripts/gen_coverage_matrix.py

Or via Make::

    make coverage-matrix
"""

import sys
from pathlib import Path

# docs/ is the parent of this script's directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from coverage_report import (
    build_coverage_report,
    render_contracts_index,
)

report = build_coverage_report()
root = Path(__file__).parent.parent

contracts_index = root / "contracts" / "index.md"
contracts_index.write_text(render_contracts_index(report), encoding="utf-8")
print(f"Written {contracts_index} ({len(report.ccnl_rows)} CCNL)")
