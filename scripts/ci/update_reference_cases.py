"""Regenerate reference case expected blocks from the live engine.

For each JSON file in ``tests/reference/cases/``, re-runs ``compute()`` with
the stored inputs and overwrites the ``expected`` block with the live result.
Use this script after engine changes that intentionally alter output values.

Usage::

    uv run python scripts/ci/update_reference_cases.py [--dry-run] [case_file ...]

Options:
    --dry-run   Print a diff for each case without writing any files.
    case_file   Optional: path(s) to specific case JSON files.  If omitted,
                all files in ``tests/reference/cases/`` are updated.

Exit codes:
    0   All cases updated (or no diff found in dry-run mode).
    1   One or more cases would change (dry-run only).
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

# Ensure the package root is importable when run as a script.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.employee import (
    RalOverride,
    SeniorityByCount,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.family import FamilyComposition
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PayrollScenario,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WelfareInput,
)
from ccnl_engine.engine.payroll.service.orchestrator import compute

_CASES_DIR = Path(__file__).parent.parent.parent / "tests" / "reference" / "cases"


# ---------------------------------------------------------------------------
# Input builders (mirrors test_reference.py)
# ---------------------------------------------------------------------------


def _build_contract(inputs: dict[str, Any]) -> Permanent | FixedTerm | Apprentice:
    emp_type = inputs["employment_type"]
    if emp_type == "permanent":
        return Permanent()
    if emp_type == "fixed_term":
        return FixedTerm()
    return Apprentice(months_elapsed=inputs["months_elapsed"])


def _build_seniority(
    inputs: dict[str, Any],
) -> SeniorityByCount | SeniorityByMonths | None:
    """Mirrors test_reference.py: seniority_months beats count; count=0 means None.

    Returns:
        The appropriate seniority object, or ``None`` when both are absent/zero.
    """
    seniority_count_raw = int(inputs["seniority_count"])
    seniority_months_raw = inputs.get("seniority_months")
    if seniority_months_raw is not None:
        return SeniorityByMonths(value=int(seniority_months_raw))
    if seniority_count_raw:
        return SeniorityByCount(value=seniority_count_raw)
    return None


def _build_supplements(inputs: dict[str, Any]) -> OvertimeHours | None:
    raw = inputs.get("time_supplements")
    if raw is None:
        return None
    return OvertimeHours(
        weekday_hours=Decimal(str(raw.get("weekday_hours", "0"))),
        night_hours=Decimal(str(raw.get("night_hours", "0"))),
        holiday_hours=Decimal(str(raw.get("holiday_hours", "0"))),
        night_holiday_hours=Decimal(str(raw.get("night_holiday_hours", "0"))),
        supplementare_hours=Decimal(str(raw.get("supplementare_hours", "0"))),
    )


def _build_absence(inputs: dict[str, Any]) -> AbsenceDays | None:
    raw = inputs.get("absence_days")
    if raw is None:
        return None
    return AbsenceDays(unpaid_days=Decimal(str(raw.get("unpaid_days", "0"))))


def _build_leave(inputs: dict[str, Any]) -> LeaveInput | None:
    raw = inputs.get("leave_input")
    if raw is None:
        return None
    return LeaveInput(taken_days=Decimal(str(raw.get("taken_days", "0"))))


def _build_sick(inputs: dict[str, Any]) -> SickInput | None:
    raw = inputs.get("sick_input")
    if raw is None:
        return None
    cumulative_raw = raw.get("cumulative_sick_days")
    return SickInput(
        sick_days=Decimal(str(raw.get("sick_days", "0"))),
        cumulative_sick_days=(
            Decimal(str(cumulative_raw)) if cumulative_raw is not None else None
        ),
    )


def _build_fringe(inputs: dict[str, Any]) -> FringeBenefitInput | None:
    raw = inputs.get("fringe_benefit_input")
    if raw is None:
        return None
    return FringeBenefitInput(
        annual_amount=Decimal(str(raw.get("annual_amount", "0"))),
        has_dependent_children=bool(raw.get("has_dependent_children", False)),
    )


def _build_welfare(inputs: dict[str, Any]) -> WelfareInput | None:
    raw = inputs.get("welfare_input")
    if raw is None:
        return None
    return WelfareInput(annual_amount=Decimal(str(raw.get("annual_amount", "0"))))


def _build_bonus(inputs: dict[str, Any]) -> BonusInput | None:
    raw = inputs.get("bonus_input")
    if raw is None:
        return None
    prior = raw.get("prior_year_gross_annual")
    return BonusInput(
        annual_amount=Decimal(str(raw.get("annual_amount", "0"))),
        eligible_for_pdr=bool(raw.get("eligible_for_pdr", False)),
        prior_year_gross_annual=(Decimal(str(prior)) if prior is not None else None),
    )


def _build_family(inputs: dict[str, Any]) -> FamilyComposition | None:
    raw = inputs.get("family")
    if raw is None:
        return None
    return FamilyComposition(
        spouse_dependent=bool(raw.get("spouse_dependent", False)),
        children_21_or_older=int(raw.get("children_21_or_older", 0)),
        children_21_or_older_disabled=int(raw.get("children_21_or_older_disabled", 0)),
        ascendenti_conviventi=int(raw.get("ascendenti_conviventi", 0)),
    )


def _build_art15(inputs: dict[str, Any]) -> Art15Deductions | None:
    raw = inputs.get("art15_deductions")
    if raw is None:
        return None
    return Art15Deductions(
        mortgage_interest=Decimal(str(raw.get("mortgage_interest", "0"))),
        mortgage_pre_2022=bool(raw.get("mortgage_pre_2022", False)),
    )


def _build_scenario(inputs: dict[str, Any]) -> PayrollScenario:
    """Reconstruct the PayrollScenario from a case's inputs dict.

    Returns:
        A fully initialised :class:`PayrollScenario` ready for ``compute()``.
    """
    as_of = date.fromisoformat(inputs["as_of"])
    tax_year_raw = int(inputs["year"])
    tax_year = tax_year_raw if tax_year_raw != as_of.year else None
    regione = inputs.get("regione")
    comune = inputs.get("comune_belfiore")
    jurisdiction = (
        Jurisdiction(regione=regione, comune_belfiore=comune)
        if (regione is not None or comune is not None)
        else None
    )
    ral_raw = inputs.get("negotiated_ral")
    agreement = (
        Agreement(ral_override=RalOverride(value=Decimal(ral_raw)))
        if ral_raw is not None
        else None
    )
    ivs = bool(inputs.get("ivs_ceiling_applies"))

    return PayrollScenario(
        employee=Employee(
            level_code=inputs["level_code"],
            seniority=_build_seniority(inputs),
            part_time_ratio=Decimal(inputs["part_time_ratio"]),
            weekly_hours=(
                Decimal(str(inputs["weekly_hours"]))
                if inputs.get("weekly_hours") is not None
                else None
            ),
            category=inputs.get("category"),
            ivs_ceiling_applies=ivs,
            jurisdiction=jurisdiction,
            agreement=agreement,
        ),
        employment=Employment(
            ccnl=inputs["ccnl_file"],
            contract=_build_contract(inputs),
            employer=Employer(num_employees=int(inputs["num_employees"])),
            as_of=as_of,
            tax_year=tax_year,
        ),
        time_supplements=_build_supplements(inputs),
        absence_days=_build_absence(inputs),
        leave_input=_build_leave(inputs),
        sick_input=_build_sick(inputs),
        fringe_benefit_input=_build_fringe(inputs),
        welfare_input=_build_welfare(inputs),
        bonus_input=_build_bonus(inputs),
        family=_build_family(inputs),
        art15_deductions=_build_art15(inputs),
    )


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

_DECIMAL_FIELDS = {
    "part_time_pct",
    "base_monthly",
    "seniority_monthly",
    "allowances_monthly",
    "ad_personam_monthly",
    "second_level_monthly",
    "gross_monthly",
    "gross_annual",
    "hourly_rate",
    "apprenticeship_pct",
    "inps_employee_annual",
    "inps_employer_annual",
    "employer_funds_annual",
    "tfr_annual",
    "bilateral_employee_annual",
    "bilateral_employer_annual",
    "taxable_income",
    "irpef_gross",
    "work_income_deduction",
    "ulteriore_detrazione_lavoro",
    "irpef_net",
    "addizionale_regionale_annual",
    "addizionale_comunale_annual",
    "trattamento_integrativo",
    "net_annual",
    "net_monthly",
    "employer_cost_annual",
}

_INCLUDED_FIELDS = {
    "ccnl_id",
    "level_code",
    "employment_type",
    "part_time_pct",
    "year",
    "seniority_count",
    "base_monthly",
    "seniority_monthly",
    "allowances_monthly",
    "ad_personam_monthly",
    "gross_monthly",
    "gross_annual",
    "hourly_rate",
    "apprenticeship_pct",
    "apprenticeship_under_level_code",
    "inps_employee_annual",
    "inps_employer_annual",
    "employer_funds_annual",
    "tfr_annual",
    "bilateral_employee_annual",
    "bilateral_employer_annual",
    "taxable_income",
    "irpef_gross",
    "work_income_deduction",
    "ulteriore_detrazione_lavoro",
    "irpef_net",
    "net_annual",
    "net_monthly",
    "employer_cost_annual",
    "addizionale_regionale_annual",
    "addizionale_comunale_annual",
    "trattamento_integrativo",
    "fiscal_simplifications",
}


def _serialise_result(result: object) -> dict[str, Any]:
    """Extract the fields recorded in expected blocks from a PayrollResult.

    Returns:
        A dict mapping field names to JSON-serialisable values.
    """
    out: dict[str, Any] = {}
    for field in _INCLUDED_FIELDS:
        value = getattr(result, field)
        if field in _DECIMAL_FIELDS:
            out[field] = str(value) if value is not None else None
        elif isinstance(value, frozenset):
            out[field] = sorted(str(v) for v in value)
        else:
            out[field] = value
    return out


# ---------------------------------------------------------------------------
# Case update logic
# ---------------------------------------------------------------------------


def _update_case(path: Path, *, dry_run: bool) -> bool:
    """Re-run compute() for one case and update its expected block.

    Preserves the existing key order in ``expected``; new fields are appended
    after all pre-existing ones.  Only value differences trigger a change.

    Returns:
        ``True`` when the file was (or would be) changed, ``False`` otherwise.

    Raises:
        RuntimeError: when ``compute()`` or scenario construction fails.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    inputs = data["inputs"]

    try:
        scenario = _build_scenario(inputs)
        result = compute(scenario).result
    except Exception as exc:
        msg = f"{path.name}: {exc}"
        raise RuntimeError(msg) from exc

    new_values = _serialise_result(result)
    old_expected: dict[str, Any] = data.get("expected", {})

    # Build merged dict: preserve old key order, append new keys, update values.
    merged: dict[str, Any] = {}
    for k, v in old_expected.items():
        merged[k] = new_values.get(k, v)  # update with live value if tracked
    for k, v in new_values.items():
        if k not in merged:
            merged[k] = v  # new field not previously recorded

    # Values-only change detection (ignore key ordering).
    changed = any(merged.get(k) != old_expected.get(k) for k in merged) or any(
        k not in old_expected for k in merged
    )
    if not changed:
        return False

    if dry_run:
        old_str = json.dumps(old_expected, indent=2, ensure_ascii=False)
        new_str = json.dumps(merged, indent=2, ensure_ascii=False)
        diff = list(
            difflib.unified_diff(
                old_str.splitlines(),
                new_str.splitlines(),
                fromfile=f"a/{path.name}",
                tofile=f"b/{path.name}",
                lineterm="",
            )
        )
        if diff:
            print("\n".join(diff))
        return True

    data["expected"] = merged
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Updated: {path.name}")
    return True


def main() -> None:
    """Entry point for the reference-case update script.

    Exits with code 1 when running in dry-run mode and at least one case
    would change.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print diffs without writing files; exit 1 if any case would change.",
    )
    parser.add_argument(
        "cases",
        nargs="*",
        type=Path,
        metavar="case_file",
        help="Specific case JSON files to update (default: all).",
    )
    args = parser.parse_args()

    paths = (
        [Path(p) for p in args.cases]
        if args.cases
        else sorted(_CASES_DIR.glob("*.json"))
    )

    changed_count = sum(_update_case(p, dry_run=args.dry_run) for p in paths)

    if args.dry_run and changed_count:
        print(
            f"\n{changed_count} case(s) out of date. "
            "Run `uv run python scripts/ci/update_reference_cases.py` to fix.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.dry_run:
        print(f"Done. {changed_count} case(s) updated.")


if __name__ == "__main__":
    main()
