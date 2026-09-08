"""Reference tests: full pipeline output must match pre-recorded cases exactly.

Each case wires the bundle loaders (CCNL, tax/INPS, surtax) into ``compute()``
and compares every ``PayrollResult`` field against the stored expected values.

An optional ``source`` key on each case JSON records the primary document that
was used to verify the expected values (payslip, official table, circular).
The test passes regardless; the source is surfaced in the session summary.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from ccnl_engine.engine.payroll.domain.employee import (
    RalOverride,
    SeniorityByCount,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PayrollScenario,
)
from ccnl_engine.engine.payroll.domain.supplements import AbsenceDays, OvertimeHours
from ccnl_engine.engine.payroll.service.orchestrator import compute

_CASES_DIR = Path(__file__).parent / "cases"
_CASE_FILES = sorted(_CASES_DIR.glob("*.json"))


def _build_absence_days(inputs: dict[str, Any]) -> AbsenceDays | None:
    """Build AbsenceDays from the ``absence_days`` key in *inputs*.

    Returns:
        An :class:`AbsenceDays` instance, or ``None`` when the key is absent.
    """
    raw = inputs.get("absence_days")
    if raw is None:
        return None
    return AbsenceDays(
        unpaid_days=Decimal(str(raw.get("unpaid_days", "0"))),
    )


def _build_time_supplements(inputs: dict[str, Any]) -> OvertimeHours | None:
    """Build OvertimeHours from the ``time_supplements`` key in *inputs*.

    Returns:
        An :class:`OvertimeHours` instance, or ``None`` when the key is absent.
    """
    raw = inputs.get("time_supplements")
    if raw is None:
        return None
    return OvertimeHours(
        weekday_hours=Decimal(str(raw.get("weekday_hours", "0"))),
        night_hours=Decimal(str(raw.get("night_hours", "0"))),
        holiday_hours=Decimal(str(raw.get("holiday_hours", "0"))),
        supplementare_hours=Decimal(str(raw.get("supplementare_hours", "0"))),
    )


def _assert_field(field: str, actual: object, raw_value: object) -> None:
    """Assert that *actual* matches the stored *raw_value* for *field*.

    Handles ``None``, ``Decimal``, ``frozenset``, ``tuple``, and plain values.
    """
    if raw_value is None:
        assert actual is None, f"{field}: expected None, got {actual!r}"
    elif isinstance(actual, Decimal):
        assert actual == Decimal(raw_value), (  # type: ignore[arg-type]
            f"{field}: expected {raw_value!r}, got {actual!r}"
        )
    elif isinstance(actual, frozenset):
        actual_sorted = sorted(str(v) for v in actual)
        assert actual_sorted == raw_value, (
            f"{field}: expected {raw_value!r}, got {actual_sorted!r}"
        )
    elif isinstance(actual, tuple):
        assert list(actual) == raw_value, (
            f"{field}: expected {raw_value!r}, got {list(actual)!r}"
        )
    else:
        assert actual == raw_value, f"{field}: expected {raw_value!r}, got {actual!r}"


def _build_contract(inputs: dict[str, Any]) -> Permanent | FixedTerm | Apprentice:
    """Construct a contract model from the integration case inputs dict.

    Returns:
        A Permanent, FixedTerm, or Apprentice instance based on employment_type.
    """
    emp_type = inputs["employment_type"]
    if emp_type == "permanent":
        return Permanent()
    if emp_type == "fixed_term":
        return FixedTerm()
    months = inputs["months_elapsed"]
    return Apprentice(months_elapsed=months)


class TestReferenceCases:
    """Each case JSON must match compute() output field-by-field."""

    @pytest.mark.parametrize("case_file", _CASE_FILES, ids=lambda p: p.stem)
    def test_case_matches(self, case_file: Path) -> None:
        """Run compute() and compare every field against the stored case JSON."""
        case = json.loads(case_file.read_text(encoding="utf-8"))
        inputs = case["inputs"]
        expected = case["expected"]

        contract = _build_contract(inputs)
        as_of = date.fromisoformat(inputs["as_of"])
        tax_year_raw = int(inputs["year"])
        tax_year = tax_year_raw if tax_year_raw != as_of.year else None

        weekly_hours_raw = inputs.get("weekly_hours")
        regione = inputs.get("regione")
        comune_belfiore = inputs.get("comune_belfiore")
        seniority_count_raw = int(inputs["seniority_count"])
        negotiated_ral_raw = inputs["negotiated_ral"]
        ivs_ceiling_applies = bool(inputs.get("ivs_ceiling_applies", False))

        seniority = (
            SeniorityByCount(seniority_count_raw) if seniority_count_raw else None
        )

        has_jurisdiction = (
            regione is not None or comune_belfiore is not None or ivs_ceiling_applies
        )
        jurisdiction = (
            Jurisdiction(regione=regione, comune_belfiore=comune_belfiore)
            if has_jurisdiction
            else None
        )

        agreement = (
            Agreement(ral_override=RalOverride(Decimal(negotiated_ral_raw)))
            if negotiated_ral_raw is not None
            else None
        )

        time_supplements = _build_time_supplements(inputs)
        absence_days = _build_absence_days(inputs)

        scenario = PayrollScenario(
            employee=Employee(
                level_code=inputs["level_code"],
                seniority=seniority,
                part_time_pct=Decimal(inputs["part_time_pct"]),
                weekly_hours=(
                    Decimal(str(weekly_hours_raw))
                    if weekly_hours_raw is not None
                    else None
                ),
                category=inputs.get("category"),
                ivs_ceiling_applies=ivs_ceiling_applies,
                jurisdiction=jurisdiction,
                agreement=agreement,
            ),
            employment=Employment(
                ccnl=inputs["ccnl_file"],
                contract=contract,
                employer=Employer(num_employees=int(inputs["num_employees"])),
                date=as_of,
                tax_year=tax_year,
            ),
            time_supplements=time_supplements,
            absence_days=absence_days,
        )

        result = compute(scenario)

        # Compare each field in expected against the live PayrollResult
        for field, raw_value in expected.items():
            _assert_field(field, getattr(result, field), raw_value)
