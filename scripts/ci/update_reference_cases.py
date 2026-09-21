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
from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PeriodPayrollInput,
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
from ccnl_engine.engine.payroll.service.pipeline import _annual_to_scenario, compute

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
    deps: list[Dependent] = []
    for d in raw.get("dependents", []):
        rel = DependentRelationship(d["relationship"])
        birth_date_raw = d.get("birth_date")
        birth_date = date.fromisoformat(birth_date_raw) if birth_date_raw else None
        deps.append(
            Dependent(
                relationship=rel,
                birth_date=birth_date,
                disabled=bool(d.get("disabled", False)),
                own_income=Decimal(str(d.get("own_income", "0"))),
                months_dependent=int(d.get("months_dependent", 12)),
                allocation_pct=Decimal(str(d.get("allocation_pct", "100"))),
                cohabiting=bool(d.get("cohabiting", True)),
                residency_eligibility=bool(d.get("residency_eligibility", True)),
            )
        )
    return FamilyComposition(dependents=tuple(deps))


def _build_art15(inputs: dict[str, Any]) -> Art15Deductions | None:
    raw = inputs.get("art15_deductions")
    if raw is None:
        return None
    return Art15Deductions(
        mortgage_interest=Decimal(str(raw.get("mortgage_interest", "0"))),
        mortgage_pre_2022=bool(raw.get("mortgage_pre_2022", False)),
    )


def _build_scenario(
    inputs: dict[str, Any],
) -> tuple[AnnualEstimateInput, PeriodPayrollInput | None]:
    """Reconstruct the scenario from a case's inputs dict.

    Returns:
        A tuple of ``(AnnualEstimateInput, PeriodPayrollInput | None)``
        ready for ``_annual_to_scenario`` + ``compute()``.
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

    annual = AnnualEstimateInput(
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
        family=_build_family(inputs),
        art15_deductions=_build_art15(inputs),
    )

    time_supplements = _build_supplements(inputs)
    absence_days = _build_absence(inputs)
    leave_input = _build_leave(inputs)
    sick_input = _build_sick(inputs)
    fringe_benefit_input = _build_fringe(inputs)
    welfare_input = _build_welfare(inputs)
    bonus_input = _build_bonus(inputs)

    has_period = any(
        x is not None
        for x in (
            time_supplements,
            absence_days,
            leave_input,
            sick_input,
            fringe_benefit_input,
            welfare_input,
            bonus_input,
        )
    )
    period = (
        PeriodPayrollInput(
            time_supplements=time_supplements,
            absence_days=absence_days,
            leave_input=leave_input,
            sick_input=sick_input,
            fringe_benefit_input=fringe_benefit_input,
            welfare_input=welfare_input,
            bonus_input=bonus_input,
        )
        if has_period
        else None
    )
    return annual, period


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

_DECIMAL_FIELDS = {
    "part_time_ratio",
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
    "part_time_ratio",
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


_SUB_OBJECT_FIELDS: dict[str, str] = {
    "seniority_count": "earnings",
    "base_monthly": "earnings",
    "seniority_monthly": "earnings",
    "allowances_monthly": "earnings",
    "ad_personam_monthly": "earnings",
    "gross_monthly": "earnings",
    "gross_annual": "earnings",
    "hourly_rate": "earnings",
    "apprenticeship_pct": "earnings",
    "apprenticeship_under_level_code": "earnings",
    "inps_employee_annual": "contributions",
    "inps_employer_annual": "contributions",
    "employer_funds_annual": "contributions",
    "tfr_annual": "contributions",
    "bilateral_employee_annual": "contributions",
    "bilateral_employer_annual": "contributions",
    "taxable_income": "taxes",
    "irpef_gross": "taxes",
    "work_income_deduction": "taxes",
    "ulteriore_detrazione_lavoro": "taxes",
    "irpef_net": "taxes",
    "addizionale_regionale_annual": "taxes",
    "addizionale_comunale_annual": "taxes",
    "trattamento_integrativo": "taxes",
    "fiscal_simplifications": "taxes",
    "employer_cost_annual": "employer_cost",
}


def _serialise_result(result: object) -> dict[str, Any]:
    """Extract the fields recorded in expected blocks from a PayrollResult.

    Returns:
        A dict mapping field names to JSON-serialisable values.
    """
    out: dict[str, Any] = {}
    for field in _INCLUDED_FIELDS:
        sub = _SUB_OBJECT_FIELDS.get(field)
        obj = getattr(result, sub) if sub else result
        value = getattr(obj, field)
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


def _check_source_guard(
    path: Path,
    data: dict[str, Any],
    *,
    allow_source_overwrite: bool,
) -> None:
    """Raise RuntimeError if writing this case is not allowed.

    Raises:
        RuntimeError: when the case has a source block and writing is not
            explicitly allowed, or when ``verification_status='verified'``.
    """
    source = data.get("source")
    if not source:
        return
    verification_status: str | None = (
        source.get("verification_status") if isinstance(source, dict) else None
    )
    if verification_status == "verified":
        msg = (
            f"{path.name}: case has verification_status='verified' — "
            "the updater never overwrites externally verified oracles"
        )
        raise RuntimeError(msg)
    if not allow_source_overwrite:
        msg = (
            f"{path.name}: case has a source block — "
            "pass --overwrite-source to allow rewriting it"
        )
        raise RuntimeError(msg)


def _update_case(
    path: Path,
    *,
    dry_run: bool,
    allow_source_overwrite: bool = False,
) -> tuple[bool, bool]:
    """Re-run compute() for one case and update its expected block.

    Preserves the existing key order in ``expected``; new fields are appended
    after all pre-existing ones.  Only value differences trigger a change.

    Returns:
        A tuple ``(changed, has_source)``.  ``changed`` is ``True`` when the
        file was (or would be) changed; ``has_source`` is ``True`` when the
        case carries a non-empty ``source`` field (independent oracle).

    Raises:
        RuntimeError: when writing is blocked by source-guard rules, or when
            ``compute()`` or scenario construction fails.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    has_source: bool = bool(data.get("source"))

    if has_source and not dry_run:
        _check_source_guard(path, data, allow_source_overwrite=allow_source_overwrite)

    inputs = data["inputs"]

    try:
        annual, period = _build_scenario(inputs)
        result = compute(_annual_to_scenario(annual, period)).result
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
        return False, has_source

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
        return True, has_source

    data["expected"] = merged
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Updated: {path.name}")
    return True, has_source


def _classify_results(
    paths: list[Path], results: list[tuple[bool, bool]]
) -> tuple[list[Path], list[Path]]:
    """Split changed cases into oracle regressions and auto-promotions.

    Returns:
        A tuple ``(oracle_regressions, auto_promotions)``.
    """
    oracle_regressions = [
        p
        for p, (changed, has_src) in zip(paths, results, strict=True)
        if changed and has_src
    ]
    auto_promotions = [
        p
        for p, (changed, has_src) in zip(paths, results, strict=True)
        if changed and not has_src
    ]
    return oracle_regressions, auto_promotions


def _report_oracle_regressions(regressions: list[Path]) -> None:
    """Print a structured error for independently-verified cases that diverged."""
    names = "\n".join(f"  {p.name}" for p in regressions)
    print(
        f"\n{len(regressions)} independently-verified case(s) diverged "
        f"from the engine output:\n{names}\n\n"
        "These cases have a 'source' field — their expected values were "
        "verified against an external document.\n"
        "Do NOT run the update script to fix this: investigate why the engine "
        "output changed, then either correct the engine or re-verify the case "
        "against the source and update the 'source.verified_at' date.",
        file=sys.stderr,
    )


def _report_auto_promotions(promotions: list[Path]) -> None:
    """Print a structured warning for engine-generated cases that are out of date."""
    names = "\n".join(f"  {p.name}" for p in promotions)
    print(
        f"\n{len(promotions)} engine-generated case(s) are out of date:\n{names}\n\n"
        "These cases have no 'source' field.\n"
        "Run `uv run python scripts/ci/update_reference_cases.py` locally, "
        "review the diff carefully to confirm the change is intentional, "
        "and where possible add a 'source' block documenting the "
        "external reference that verifies the expected values.",
        file=sys.stderr,
    )


def main() -> None:
    """Entry point for the reference-case update script.

    In dry-run mode, exits with code 1 when any case would change and
    distinguishes two categories:

    * **Oracle regression** — a case with a ``source`` field would change.
      This indicates the engine diverged from a value verified against an
      external document.  Do NOT auto-update; investigate the cause.
    * **Auto-promotion** — a case without a ``source`` field would change.
      Running the script would silently crystallise engine output as the new
      expected value.  Acceptable only after manual review of the diff.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print diffs without writing files; exit 1 if any case would change.",
    )
    parser.add_argument(
        "--overwrite-source",
        action="store_true",
        help=(
            "Allow rewriting cases that carry a source block. "
            "Has no effect on cases with verification_status='verified', "
            "which the updater never overwrites."
        ),
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

    results = [
        _update_case(
            p,
            dry_run=args.dry_run,
            allow_source_overwrite=args.overwrite_source,
        )
        for p in paths
    ]
    oracle_regressions, auto_promotions = _classify_results(paths, results)

    if args.dry_run:
        if oracle_regressions:
            _report_oracle_regressions(oracle_regressions)
        if auto_promotions:
            _report_auto_promotions(auto_promotions)
        if oracle_regressions or auto_promotions:
            sys.exit(1)
    else:
        changed_count = len(oracle_regressions) + len(auto_promotions)
        print(f"Done. {changed_count} case(s) updated.")


if __name__ == "__main__":
    main()
