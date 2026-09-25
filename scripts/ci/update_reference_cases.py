"""Verify that engine output matches every reference case in tests/reference/cases/.

Runs each fixture through the public API (``calculate_year`` with auto-derived
calendar) and compares ``annual_gross``, ``annual_net`` and
``annual_employer_cost`` against the fixture's ``expected`` block.

Exit codes:
    0 — all fixtures match within tolerance.
    1 — one or more fixtures diverge; divergences are printed to stdout.

The ``--dry-run`` flag is accepted for backwards compatibility but has no effect:
verification always runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.employment import Apprentice, Permanent

_CASES_DIR = Path(__file__).parents[2] / "tests" / "reference" / "cases"
_TOLERANCE = Decimal("0.02")


def _contract_type(inputs: dict[str, object]) -> Permanent | Apprentice:
    employment_type = inputs.get("employment_type", "permanent")
    if employment_type == "apprentice":
        months_elapsed = int(str(inputs.get("months_elapsed", 0)))
        return Apprentice(months_elapsed=months_elapsed)
    return Permanent()


def _check(path: Path) -> list[str]:
    """Run one fixture and return a list of failure messages (empty = pass).

    Returns:
        A list of human-readable failure messages, empty when the fixture matches.
    """
    data: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
    inputs: dict[str, object] = data["inputs"]  # type: ignore[assignment]
    expected: dict[str, str] = data["expected"]  # type: ignore[assignment]

    ccnl_slug: str = str(inputs["ccnl_file"])
    year: int = int(str(inputs["year"]))
    level_code: str = str(inputs["level_code"])
    num_employees: int = int(str(inputs.get("num_employees", 50)))
    contract_type = _contract_type(inputs)

    try:
        result = calculate_year(
            year,
            ccnl_slug,
            level_code,
            num_employees=num_employees,
            contract_type=contract_type,
        )
    except (ValueError, KeyError, TypeError, RuntimeError) as exc:
        return [f"{path.name}: engine raised {type(exc).__name__}: {exc}"]

    failures: list[str] = []

    def _check_field(field: str, actual: Decimal, raw_expected: str | None) -> None:
        if raw_expected is None:
            return
        exp = Decimal(raw_expected)
        diff = abs(actual - exp)
        if diff > _TOLERANCE:
            failures.append(f"  {field}: expected {exp}, got {actual}, diff {diff:+}")

    _check_field("gross_annual", result.annual_gross, expected.get("gross_annual"))
    _check_field("net_annual", result.annual_net, expected.get("net_annual"))
    _check_field(
        "employer_cost_annual",
        result.annual_employer_cost,
        expected.get("employer_cost_annual"),
    )

    if failures:
        return [f"{path.name}:", *failures]
    return []


def main() -> int:
    """Run all reference cases and report divergences.

    Returns:
        0 on success, 1 if any fixture diverges.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Accepted for compatibility; verification always runs.",
    )
    parser.parse_args()

    cases = sorted(_CASES_DIR.glob("*.json"))
    if not cases:
        print(f"No reference cases found in {_CASES_DIR}")
        return 1

    print(f"Verifying {len(cases)} reference cases...")
    all_failures: list[str] = []
    for path in cases:
        failures = _check(path)
        if failures:
            all_failures.extend(failures)

    if all_failures:
        print(f"\n{len(all_failures)} divergence(s) found:\n")
        for line in all_failures:
            print(line)
        return 1

    print(f"All {len(cases)} reference cases verified successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
