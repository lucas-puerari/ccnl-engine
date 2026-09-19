"""Reference tests: full pipeline output must match pre-recorded cases exactly.

Each case wires the bundle loaders (CCNL, tax/INPS, surtax) into ``compute()``
and compares every ``PayrollResult`` field against the stored expected values.

An optional ``source`` key on each case JSON records the primary document that
was used to verify the expected values (payslip, official table, circular).
The test passes regardless; the source is surfaced in the session summary.
"""

from __future__ import annotations

import importlib.util
import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import types

import pytest

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


def _build_leave_input(inputs: dict[str, Any]) -> LeaveInput | None:
    """Build LeaveInput from the ``leave_input`` key in *inputs*.

    Returns:
        A :class:`LeaveInput` instance, or ``None`` when the key is absent.
    """
    raw = inputs.get("leave_input")
    if raw is None:
        return None
    return LeaveInput(taken_days=Decimal(str(raw.get("taken_days", "0"))))


def _build_sick_input(inputs: dict[str, Any]) -> SickInput | None:
    """Build SickInput from the ``sick_input`` key in *inputs*.

    Returns:
        A :class:`SickInput` instance, or ``None`` when the key is absent.
    """
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


def _build_fringe_benefit_input(inputs: dict[str, Any]) -> FringeBenefitInput | None:
    """Build FringeBenefitInput from the ``fringe_benefit_input`` key in *inputs*.

    Returns:
        A :class:`FringeBenefitInput` instance, or ``None`` when the key is absent.
    """
    raw = inputs.get("fringe_benefit_input")
    if raw is None:
        return None
    return FringeBenefitInput(
        annual_amount=Decimal(str(raw.get("annual_amount", "0"))),
        has_dependent_children=bool(raw.get("has_dependent_children", False)),
    )


def _build_welfare_input(inputs: dict[str, Any]) -> WelfareInput | None:
    """Build WelfareInput from the ``welfare_input`` key in *inputs*.

    Returns:
        A :class:`WelfareInput` instance, or ``None`` when the key is absent.
    """
    raw = inputs.get("welfare_input")
    if raw is None:
        return None
    return WelfareInput(annual_amount=Decimal(str(raw.get("annual_amount", "0"))))


def _build_bonus_input(inputs: dict[str, Any]) -> BonusInput | None:
    """Build BonusInput from the ``bonus_input`` key in *inputs*.

    Returns:
        A :class:`BonusInput` instance, or ``None`` when the key is absent.
    """
    raw = inputs.get("bonus_input")
    if raw is None:
        return None
    prior_year_raw = raw.get("prior_year_gross_annual")
    return BonusInput(
        annual_amount=Decimal(str(raw.get("annual_amount", "0"))),
        eligible_for_pdr=bool(raw.get("eligible_for_pdr", False)),
        prior_year_gross_annual=(
            Decimal(str(prior_year_raw)) if prior_year_raw is not None else None
        ),
    )


def _build_family(inputs: dict[str, Any]) -> FamilyComposition | None:
    """Build FamilyComposition from the ``family`` key in *inputs*.

    Expects a ``dependents`` list of dicts, each with at least ``relationship``
    and any optional Dependent fields (birth_date, disabled, own_income, etc.).

    Returns:
        A :class:`FamilyComposition` instance, or ``None`` when the key is absent.
    """
    raw = inputs.get("family")
    if raw is None:
        return None
    deps = []
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


def _build_art15_deductions(inputs: dict[str, Any]) -> Art15Deductions | None:
    """Build Art15Deductions from the ``art15_deductions`` key in *inputs*.

    Returns:
        An :class:`Art15Deductions` instance, or ``None`` when the key is absent.
    """
    raw = inputs.get("art15_deductions")
    if raw is None:
        return None
    return Art15Deductions(
        mortgage_interest=Decimal(str(raw.get("mortgage_interest", "0"))),
        mortgage_pre_2022=bool(raw.get("mortgage_pre_2022", False)),
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
        night_holiday_hours=Decimal(str(raw.get("night_holiday_hours", "0"))),
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
        seniority_months_raw = inputs.get("seniority_months")
        negotiated_ral_raw = inputs["negotiated_ral"]
        ivs_ceiling_applies = bool(inputs.get("ivs_ceiling_applies", False))

        if seniority_months_raw is not None:
            seniority: SeniorityByCount | SeniorityByMonths | None = SeniorityByMonths(
                value=int(seniority_months_raw)
            )
        elif seniority_count_raw:
            seniority = SeniorityByCount(value=seniority_count_raw)
        else:
            seniority = None

        has_jurisdiction = (
            regione is not None or comune_belfiore is not None or ivs_ceiling_applies
        )
        jurisdiction = (
            Jurisdiction(regione=regione, comune_belfiore=comune_belfiore)
            if has_jurisdiction
            else None
        )

        agreement = (
            Agreement(ral_override=RalOverride(value=Decimal(negotiated_ral_raw)))
            if negotiated_ral_raw is not None
            else None
        )

        time_supplements = _build_time_supplements(inputs)
        absence_days = _build_absence_days(inputs)
        leave_input = _build_leave_input(inputs)
        sick_input = _build_sick_input(inputs)
        fringe_benefit_input = _build_fringe_benefit_input(inputs)
        welfare_input = _build_welfare_input(inputs)
        bonus_input = _build_bonus_input(inputs)

        scenario = PayrollScenario(
            employee=Employee(
                level_code=inputs["level_code"],
                seniority=seniority,
                part_time_ratio=Decimal(inputs["part_time_ratio"]),
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
                as_of=as_of,
                tax_year=tax_year,
            ),
            time_supplements=time_supplements,
            absence_days=absence_days,
            leave_input=leave_input,
            sick_input=sick_input,
            fringe_benefit_input=fringe_benefit_input,
            welfare_input=welfare_input,
            bonus_input=bonus_input,
            family=_build_family(inputs),
            art15_deductions=_build_art15_deductions(inputs),
        )

        result = compute(scenario).result

        # Compare each field in expected against the live PayrollResult
        for field, raw_value in expected.items():
            _assert_field(field, getattr(result, field), raw_value)


class TestReferenceBuilders:
    """Builder functions must forward all fields declared in fixture dicts."""

    def test_build_art15_deductions_passes_mortgage_pre_2022(self) -> None:
        """_build_art15_deductions must honour the mortgage_pre_2022 flag."""
        result = _build_art15_deductions({
            "art15_deductions": {
                "mortgage_interest": "1000",
                "mortgage_pre_2022": True,
            }
        })
        assert result is not None
        assert result.mortgage_pre_2022 is True

    def test_build_art15_deductions_defaults_mortgage_pre_2022_false(self) -> None:
        """When mortgage_pre_2022 is absent, _build_art15_deductions defaults False."""
        result = _build_art15_deductions({
            "art15_deductions": {"mortgage_interest": "500"}
        })
        assert result is not None
        assert result.mortgage_pre_2022 is False

    def test_build_bonus_input_passes_prior_year_gross_annual(self) -> None:
        """_build_bonus_input must honour prior_year_gross_annual when present."""
        result = _build_bonus_input({
            "bonus_input": {
                "annual_amount": "1000",
                "eligible_for_pdr": True,
                "prior_year_gross_annual": "28000",
            }
        })
        assert result is not None
        assert result.prior_year_gross_annual == Decimal(28000)

    def test_build_bonus_input_defaults_prior_year_gross_annual_none(self) -> None:
        """When prior_year_gross_annual is absent, _build_bonus_input yields None."""
        result = _build_bonus_input({
            "bonus_input": {"annual_amount": "500", "eligible_for_pdr": False}
        })
        assert result is not None
        assert result.prior_year_gross_annual is None


_SCRIPT_PATH = (
    Path(__file__).parent.parent.parent / "scripts" / "ci" / "update_reference_cases.py"
)


def _load_update_script() -> types.ModuleType:
    """Load update_reference_cases.py as a module at runtime.

    Returns:
        The loaded module object.
    """
    spec = importlib.util.spec_from_file_location(
        "update_reference_cases", _SCRIPT_PATH
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class TestUpdateScript:
    """Tests for the update_reference_cases maintenance script.

    Verifies that the script uses current field names and propagates errors
    instead of silently returning False.
    """

    def test_script_build_art15_uses_mortgage_pre_2022(self) -> None:
        """_build_art15 in the script must read mortgage_pre_2022, not the old name."""
        mod = _load_update_script()
        result = mod._build_art15({
            "art15_deductions": {"mortgage_interest": "2000", "mortgage_pre_2022": True}
        })
        assert result is not None
        assert result.mortgage_pre_2022 is True

    def test_script_update_case_raises_on_bad_input(self, tmp_path: Path) -> None:
        """_update_case must raise RuntimeError when the scenario cannot be built."""
        mod = _load_update_script()
        bad_case = tmp_path / "bad_case.json"
        bad_case.write_text(
            '{"inputs": {"ccnl_file": "metalmeccanico-federmeccanica.json", '
            '"year": 2026, "tax_sector": "industria", "num_employees": 50, '
            '"level_code": "C2", "as_of": "2026-09-01", '
            '"employment_type": "permanent", "part_time_ratio": "NOT_A_DECIMAL"}, '
            '"expected": {}}',
            encoding="utf-8",
        )
        with pytest.raises(RuntimeError, match=r"bad_case\.json"):
            mod._update_case(bad_case, dry_run=False)
