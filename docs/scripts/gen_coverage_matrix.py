"""Regenerate docs/coverage-matrix.md from live CCNL data.

Run with::

    uv run python docs/scripts/gen_coverage_matrix.py
"""

import sys
from pathlib import Path

# docs/ is the parent of this script's directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from coverage_report import build_coverage_report, render_markdown  # noqa: E402

report = build_coverage_report()
out = Path(__file__).parent.parent / "coverage-matrix.md"
out.write_text(render_markdown(report), encoding="utf-8")
print(f"Written {out} ({len(report.ccnl_rows)} CCNL, {report.generated_at})")
