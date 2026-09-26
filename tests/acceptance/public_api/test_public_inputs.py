"""Public inputs: validation at construction and use by the public entry points.

Covers :class:`Employment`, :class:`EmployerProfile`,
:class:`PriorYearTaxFacts`, :class:`PeriodFacts`, :class:`PeriodInput` and
:class:`YearInput`, and the public entry points of :class:`PayrollEngine`.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine import (
    CalendarOverride,
    CalendarOverrideReason,
    ContributableHours,
    ContributionCeilingStatus,
    EmployerActivity,
    EmployerProfile,
    Employment,
    EmploymentPeriod,
    EmploymentSector,
    Headcount,
    InvalidInputError,
    OvertimeEvent,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PriorYearTaxFacts,
    SubstituteTaxRegime,
    WeeklyHours,
    WorkCalendar,
    WorkerCategory,
    YearInput,
)

_ENGINE = PayrollEngine.bundled()
_YEAR = 2026
_ZERO = Decimal(0)
_METAL = "metalmeccanico-federmeccanica.json"
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_EMPLOYMENT = Employment(ccnl_slug=_METAL, level_code="C3")
_OVERTIME = OvertimeEvent(
    event_date=date(_YEAR, 6, 10), hours=Decimal(2), hourly_rate=Decimal(15)
)


def _period(
    *,
    employment: Employment = _EMPLOYMENT,
    month: int = 6,
    facts: PeriodFacts | None = None,
) -> PeriodInput:
    return PeriodInput(
        run=PayrollRun.regular(_YEAR, month),
        payment_date=date(_YEAR, month, 28),
        employment=employment,
        employer=_EMPLOYER,
        facts=facts or PeriodFacts(),
    )


def _year(**kwargs: Any) -> YearInput:  # noqa: ANN401
    return YearInput(year=_YEAR, employment=_EMPLOYMENT, employer=_EMPLOYER, **kwargs)


class TestEmployment:
    """The employment is validated and normalized at construction."""

    def test_defaults(self) -> None:
        """Untracked facts default to ``None``, empty roles and permanent."""
        employment = Employment(ccnl_slug=_METAL, level_code="C3")
        assert employment.weekly_hours is None
        assert employment.full_time_weekly_hours is None
        assert employment.employment_period is None
        assert employment.seniority_months is None
        assert employment.roles == frozenset()
        assert employment.category is None
        assert employment.sector is None
        assert employment.ceiling_status is ContributionCeilingStatus.UNKNOWN

    def test_category_string_value_is_normalized(self) -> None:
        """A category given as its string value is stored as the enum member."""
        employment = Employment(
            ccnl_slug=_METAL,
            level_code="C3",
            category="impiegato",  # type: ignore[arg-type]
        )
        assert employment.category is WorkerCategory.IMPIEGATO

    def test_unknown_category_is_rejected(self) -> None:
        """An unknown category string raises instead of being ignored."""
        with pytest.raises(InvalidInputError, match="unknown worker category"):
            Employment(
                ccnl_slug=_METAL,
                level_code="C3",
                category="manager",  # type: ignore[arg-type]
            )

    def test_sector_string_value_is_normalized(self) -> None:
        """A sector given as its string value is stored as the enum member."""
        employment = Employment(
            ccnl_slug=_METAL,
            level_code="C3",
            sector="private",  # type: ignore[arg-type]
        )
        assert employment.sector is EmploymentSector.PRIVATE

    def test_unknown_sector_is_rejected(self) -> None:
        """A sector that names no known value is invalid input."""
        with pytest.raises(InvalidInputError, match="sector must be one of"):
            Employment(
                ccnl_slug=_METAL,
                level_code="C3",
                sector="mixed",  # type: ignore[arg-type]
            )

    def test_hours_above_full_time_are_rejected(self) -> None:
        """Contracted hours cannot exceed the full-time hours."""
        with pytest.raises(InvalidInputError, match="must not exceed"):
            Employment(
                ccnl_slug=_METAL,
                level_code="C3",
                weekly_hours=WeeklyHours(41),
                full_time_weekly_hours=WeeklyHours(40),
            )


class TestEmployerProfile:
    """The employer requires a headcount and normalizes its activity."""

    def test_activity_string_value_is_normalized(self) -> None:
        """The string value of an activity is stored as the enum member."""
        employer = EmployerProfile(
            headcount=Headcount(5),
            activity="thermal_establishment",  # type: ignore[arg-type]
        )
        assert employer.activity is EmployerActivity.THERMAL_ESTABLISHMENT

    def test_unknown_activity_is_rejected(self) -> None:
        """An activity that names no known value is invalid input."""
        with pytest.raises(InvalidInputError, match="activity must be one of"):
            EmployerProfile(
                headcount=Headcount(5),
                activity="casino",  # type: ignore[arg-type]
            )


class TestPriorYearTaxFacts:
    """Prior-year income and waivers are validated at construction."""

    def test_defaults_to_unknown_income_and_no_waiver(self) -> None:
        """Nothing declared: income unknown, no regime waived."""
        facts = PriorYearTaxFacts()
        assert facts.employment_income is None
        assert facts.waived_regimes == frozenset()

    def test_waiver_strings_are_normalized(self) -> None:
        """A regime id given as a string is stored as the enum member."""
        facts = PriorYearTaxFacts(
            waived_regimes=frozenset({"rinnovo"})  # type: ignore[arg-type]
        )
        assert facts.waived_regimes == frozenset({SubstituteTaxRegime.RINNOVO})

    @pytest.mark.parametrize(
        "income",
        [Decimal(-1), Decimal("NaN"), Decimal("Infinity"), 30000],
        ids=["negative", "nan", "infinite", "int"],
    )
    def test_bad_income_is_rejected(self, income: object) -> None:
        """Income must be a finite, non-negative Decimal."""
        with pytest.raises(InvalidInputError, match="employment_income"):
            PriorYearTaxFacts(employment_income=income)  # type: ignore[arg-type]

    def test_non_frozenset_waivers_are_rejected(self) -> None:
        """A mutable set of waivers is rejected."""
        with pytest.raises(InvalidInputError, match="must be a frozenset"):
            PriorYearTaxFacts(
                waived_regimes={SubstituteTaxRegime.RINNOVO}  # type: ignore[arg-type]
            )

    def test_unknown_regime_is_rejected(self) -> None:
        """A waiver of a regime that does not exist is invalid input."""
        with pytest.raises(InvalidInputError, match="waived_regimes entries"):
            PriorYearTaxFacts(
                waived_regimes=frozenset({"pdr"})  # type: ignore[arg-type]
            )


class TestPeriodFacts:
    """The facts of a run are validated at construction."""

    def test_events_list_is_stored_as_tuple(self) -> None:
        """A list of events is accepted and frozen into a tuple."""
        facts = PeriodFacts(events=[_OVERTIME])  # type: ignore[arg-type]
        assert facts.events == (_OVERTIME,)

    @pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param({"contributable_hours": Decimal(10)}, id="raw-hours"),
            pytest.param({"regione": 45}, id="non-str-region"),
            pytest.param({"has_dependent_children": 1}, id="non-bool-children"),
            pytest.param({"events": _OVERTIME}, id="single-event"),
        ],
    )
    def test_wrong_types_are_rejected(self, kwargs: dict[str, object]) -> None:
        """A field of the wrong type fails at construction."""
        with pytest.raises(InvalidInputError, match="must be"):
            PeriodFacts(**kwargs)  # type: ignore[arg-type]

    def test_malformed_region_is_rejected(self) -> None:
        """A region name is not a region code."""
        with pytest.raises(InvalidInputError, match="ISO 3166-2:IT"):
            PeriodFacts(regione="Lombardia")


class TestPeriodInput:
    """A run input is validated at construction."""

    @pytest.mark.parametrize(
        "field",
        ["run", "payment_date", "employment", "employer", "facts", "prior_year"],
    )
    def test_wrong_types_are_rejected(self, field: str) -> None:
        """A field of the wrong type fails at construction."""
        with pytest.raises(InvalidInputError, match=f"{field} must be"):
            replace(_period(), **{field: "x"})  # type: ignore[arg-type]

    def test_run_outside_the_employment_is_rejected(self) -> None:
        """A regular run in a month without employment fails at construction."""
        employment = replace(
            _EMPLOYMENT, employment_period=EmploymentPeriod(date(_YEAR, 9, 1))
        )
        with pytest.raises(InvalidInputError, match="outside the employment"):
            _period(employment=employment)

    def test_domestic_ccnl_uses_period_hours(self) -> None:
        """Domestic INPS reads the contracted and the contributable hours."""
        result = _ENGINE.calculate_period(
            _period(
                employment=Employment(
                    ccnl_slug="lavoro-domestico-convivente.json",
                    level_code="BS",
                    weekly_hours=WeeklyHours(30),
                ),
                facts=PeriodFacts(contributable_hours=ContributableHours(Decimal(130))),
            )
        )
        assert result.period_gross > _ZERO
        assert result.contribution_breakdown.employee > _ZERO

    def test_category_conflicting_with_level_is_rejected(self) -> None:
        """Commercio level Q is reserved to quadri, so impiegato is not admitted."""
        employment = Employment(
            ccnl_slug="commercio-confcommercio.json",
            level_code="Q",
            category=WorkerCategory.IMPIEGATO,
        )
        with pytest.raises(InvalidInputError, match="not admitted"):
            _ENGINE.calculate_period(_period(employment=employment))

    def test_declared_category_selects_artigianato_employer_rate(self) -> None:
        """Artigianato level 3 hosts operai and impiegati with different rates.

        Bundled 2026 artigianato rules: employer rate 26.93% by default and
        24.71% for impiegati, applied to the same contribution base.
        """
        employment = Employment(
            ccnl_slug="metalmeccanico-artigianato.json", level_code="3"
        )
        default = _ENGINE.calculate_period(_period(employment=employment))
        impiegato = _ENGINE.calculate_period(
            _period(employment=replace(employment, category=WorkerCategory.IMPIEGATO))
        )
        base = default.period_gross
        assert impiegato.period_gross == base
        assert default.contribution_breakdown.employer == (
            base * Decimal("0.2693")
        ).quantize(Decimal("0.01"))
        assert impiegato.contribution_breakdown.employer == (
            base * Decimal("0.2471")
        ).quantize(Decimal("0.01"))


class TestYearInput:
    """A year input normalizes its periods and rejects impossible ones."""

    def test_month_and_run_id_keys_are_normalized(self) -> None:
        """A month key names the regular run; run id keys are kept."""
        june, thirteenth = PeriodFacts(events=(_OVERTIME,)), PeriodFacts()
        year = _year(periods={6: june, "2026-12-thirteenth": thirteenth})
        assert year.facts_by_run == {
            "2026-06-regular": june,
            "2026-12-thirteenth": thirteenth,
        }

    def test_runs_without_entry_take_the_default_facts(self) -> None:
        """A run without an entry uses the default facts."""
        default = PeriodFacts(regione="IT-45")
        june = replace(default, events=(_OVERTIME,))
        year = _year(periods={6: june}, default_facts=default)
        assert year.facts_for(PayrollRun.regular(_YEAR, 6)) is june
        assert year.facts_for(PayrollRun.thirteenth(_YEAR, 12)) is default

    @pytest.mark.parametrize(
        "key",
        [0, 13, True, "june", "2025-06-regular", "2026-06-bonus", 6.0],
    )
    def test_bad_keys_are_rejected(self, key: object) -> None:
        """A key that is neither a month nor a run id of the year is rejected."""
        with pytest.raises(InvalidInputError, match="periods keys must be"):
            _year(periods={key: PeriodFacts()})

    def test_same_run_named_twice_is_rejected(self) -> None:
        """The regular run of June by month and by run id is ambiguous."""
        with pytest.raises(InvalidInputError, match="twice"):
            _year(periods={6: PeriodFacts(), "2026-06-regular": PeriodFacts()})

    def test_non_facts_value_is_rejected(self) -> None:
        """A value that is not a PeriodFacts fails at construction."""
        with pytest.raises(InvalidInputError, match="must be PeriodFacts"):
            _year(periods={6: (_OVERTIME,)})

    def test_default_facts_with_events_are_rejected(self) -> None:
        """Events would repeat on every run: they belong in periods."""
        with pytest.raises(InvalidInputError, match="default_facts must carry no"):
            _year(default_facts=PeriodFacts(events=(_OVERTIME,)))

    @pytest.mark.parametrize("payment_day", [0, 29])
    def test_payment_day_out_of_range_is_rejected(self, payment_day: int) -> None:
        """A day some month does not have is rejected."""
        with pytest.raises(InvalidInputError, match="payment day"):
            _year(payment_day=payment_day)

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("employment", "x"),
            ("employer", "x"),
            ("prior_year", "x"),
            ("periods", [(6, "x")]),
            ("default_facts", "x"),
            ("calendar_override", WorkCalendar(year=_YEAR)),
            ("opening_state", "x"),
            ("year", "2026"),
        ],
    )
    def test_wrong_types_are_rejected(self, field: str, value: object) -> None:
        """A field of the wrong type fails at construction."""
        with pytest.raises(InvalidInputError, match=f"{field} must be"):
            replace(_year(), **{field: value})  # type: ignore[arg-type]

    def test_calendar_override_is_accepted(self) -> None:
        """A calendar override with its reason is kept on the input."""
        override = CalendarOverride(
            calendar=WorkCalendar.from_additional_months(_YEAR, 13),
            reason=CalendarOverrideReason.PAYMENT_MONTH,
            note="standard calendar",
        )
        assert _year(calendar_override=override).calendar_override is override


def test_year_result_closing_state_is_the_last_run_state() -> None:
    """The closing state of the year is the one of its last run."""
    year = _ENGINE.calculate_year(_year())
    assert year.closing_state is year.period_results[-1].closing_state
