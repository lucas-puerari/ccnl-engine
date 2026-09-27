"""Household employers withhold no tax and pay no payroll tax credit.

Sources:

- art. 23 c. 1 D.P.R. 600/1973 (in force until 31 December 2026; from 2027
  art. 33 c. 1 D.Lgs. 33/2025, art. 243 as amended by D.L. 200/2025 art. 4)
  lists the withholding agents: entities, companies, partnerships,
  individuals running a business or a profession, the condominium.  A
  household employer is a private individual outside that list;
- the surtaxes are determined and withheld by the sostituti of art. 23
  (D.Lgs. 446/1997 art. 50 c. 4, D.Lgs. 360/1998 art. 1 c. 5);
- the trattamento integrativo is recognized by the sostituti of art. 23
  (D.L. 3/2020 art. 1 c. 3), and so are the somma esente and the ulteriore
  detrazione (L. 207/2024 art. 1 c. 7).

So the net of a domestic payslip is the gross less the employee INPS.  The
expected values below come from the bundled tables: the monthly minimum of
the level (DOMINA table 2026, conviventi and non conviventi) and the INPS
hourly rates of Circ. 9/2026:

- more than 24 weekly hours: employee 0.31 EUR per contributable hour;
- up to 24 weekly hours, hourly pay up to 9.61 EUR: employee 0.43 EUR.

The hourly pay is the monthly minimum over the hourly divisor of the CCNL
(234 for conviventi, 173 for non conviventi).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    BonusEvent,
    CalculationStatus,
    ContributableHours,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    NightShiftEvent,
    OpeningBalances,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
    PeriodState,
    PriorYearTaxFacts,
    RecoveryObligation,
    RecoveryPlan,
    WeeklyHours,
    WorkEvent,
    YearInput,
)

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_CONVIVENTE = "lavoro-domestico-convivente.json"
_NON_CONVIVENTE = "lavoro-domestico-non-convivente.json"
_HOUSEHOLD = EmployerProfile(headcount=Headcount(1))
_ZERO = Decimal(0)
_TAX_ACCOUNTS = frozenset({
    "ordinary_tax",
    "substitute_tax",
    "separate_tax",
    "surtax",
    "credits",
})
_SKIPPED = (
    "irpef",
    "family_deductions",
    "ulteriore_detrazione_lavoro",
    "trattamento_integrativo",
    "somma_esente",
    "addizionale_regionale",
    "addizionale_comunale",
)


@dataclass(frozen=True)
class _Case:
    """One domestic payslip and the net computed by hand."""

    ccnl_slug: str
    level_code: str
    weekly_hours: int
    contributable_hours: int
    gross: Decimal
    employee_inps: Decimal
    net: Decimal


#: Convivente level A, September 2026, 40 weekly hours, 173 contributable
#: hours: gross 908.10 (table A); 40 > 24, so 173 * 0.31 = 53.63;
#: net 908.10 - 53.63 = 854.47.  Without a residence the engine used to
#: pay 937.16, above the gross: IRPEF 57.53 withheld, trattamento
#: integrativo 92.31 and somma esente 47.91 paid.
_REPORTED = _Case(
    _CONVIVENTE, "A", 40, 173, Decimal("908.10"), Decimal("53.63"), Decimal("854.47")
)

_CASES = (
    _REPORTED,
    # Convivente level C, 54 weekly hours, 234 hours: gross 1,123.63;
    # 234 * 0.31 = 72.54; net 1,123.63 - 72.54 = 1,051.09.
    _Case(
        _CONVIVENTE,
        "C",
        54,
        234,
        Decimal("1123.63"),
        Decimal("72.54"),
        Decimal("1051.09"),
    ),
    # Non convivente level B, 25 weekly hours, 108 hours: gross 1,212.73;
    # 108 * 0.31 = 33.48; net 1,212.73 - 33.48 = 1,179.25.
    _Case(
        _NON_CONVIVENTE,
        "B",
        25,
        108,
        Decimal("1212.73"),
        Decimal("33.48"),
        Decimal("1179.25"),
    ),
    # Non convivente level A, 20 weekly hours, 86 hours: gross 1,126.23;
    # hourly pay 1,126.23 / 173 = 6.51 <= 9.61, so 86 * 0.43 = 36.98;
    # net 1,126.23 - 36.98 = 1,089.25.
    _Case(
        _NON_CONVIVENTE,
        "A",
        20,
        86,
        Decimal("1126.23"),
        Decimal("36.98"),
        Decimal("1089.25"),
    ),
)


def _employment(case: _Case) -> Employment:
    return Employment(
        ccnl_slug=case.ccnl_slug,
        level_code=case.level_code,
        weekly_hours=WeeklyHours(case.weekly_hours),
    )


def _facts(case: _Case, *events: WorkEvent) -> PeriodFacts:
    return PeriodFacts(
        contributable_hours=ContributableHours(Decimal(case.contributable_hours)),
        regione="IT-45",
        comune_belfiore="F257",
        events=events,
    )


def _september(
    case: _Case,
    *,
    facts: PeriodFacts | None = None,
    opening: PeriodState | None = None,
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=9),
            payment_date=date(2026, 9, 28),
            employment=_employment(case),
            employer=_HOUSEHOLD,
            facts=facts or _facts(case),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(10_000)),
            opening_state=opening or PeriodState.zero(),
        )
    )


def _tax_postings(result: PeriodResult) -> list[str]:
    return [
        e.account
        for e in result.ledger_entries
        if e.account in _TAX_ACCOUNTS and e.amount
    ]


@pytest.mark.parametrize(
    "case", _CASES, ids=lambda c: f"{c.ccnl_slug[:-5]}-{c.level_code}"
)
def test_net_is_gross_less_employee_contributions(case: _Case) -> None:
    """No IRPEF, surtax or credit: net = gross - employee INPS, below gross."""
    result = _september(case)

    assert result.period_gross == case.gross
    assert result.contribution_breakdown.employee == case.employee_inps
    assert result.period_net == case.net
    assert result.period_net <= result.period_gross
    assert _tax_postings(result) == []
    assert result.status is CalculationStatus.FINAL


def test_reported_case_without_residence() -> None:
    """The reported payslip, no residence declared: net 854.47, not 937.16."""
    facts = PeriodFacts(contributable_hours=ContributableHours(Decimal(173)))

    result = _september(_REPORTED, facts=facts)

    assert result.period_net == _REPORTED.net
    assert _tax_postings(result) == []


def test_skipped_capabilities_are_decided_not_applicable() -> None:
    """Each payroll tax records a final, nil not_withholding_agent decision."""
    result = _september(_REPORTED)

    skipped = [d for d in result.decisions if d.reason_code == "not_withholding_agent"]
    assert tuple(d.capability for d in skipped) == _SKIPPED
    assert {d.status for d in skipped} == {CalculationStatus.FINAL}
    assert {d.amount for d in skipped} == {_ZERO}
    assert {d.rule for d in skipped} == {"dpr600-1973-art23-c1"}
    assert {s.section for d in skipped if (s := d.source)} == {"art. 23 c. 1"}
    tax = result.tax_computation
    assert (tax.ordinary_tax, tax.trattamento_integrativo) == (_ZERO, _ZERO)
    assert tax.components == ()


def test_skipped_capabilities_read_no_tax_rule() -> None:
    """Not applicable capabilities report no rule source and no gap."""
    result = _september(_REPORTED)

    report = result.capability_report
    assert set(report.rule_sources) == {
        "base_salary",
        "inps_employee",
        "inps_employer",
        "tfr",
    }
    assert not {g.feature for g in report.gaps} & set(_SKIPPED)


def test_productivity_bonus_is_ordinary_income_without_substitute_tax() -> None:
    """A PdR of 1,000 is paid in full: net 908.10 + 1,000 - 53.63 = 1,854.47.

    The employee INPS of a domestic worker is per contributable hour, so the
    bonus does not change it (173 * 0.31 = 53.63).
    """
    bonus = BonusEvent(
        event_date=date(2026, 9, 1), amount=Decimal(1000), kind="productivity_bonus"
    )
    result = _september(_REPORTED, facts=_facts(_REPORTED, bonus))

    assert result.period_net == Decimal("1854.47")
    assert _tax_postings(result) == []
    (pdr,) = (d for d in result.decisions if d.capability == "bonus_pdr")
    assert pdr.reason_code == "not_withholding_agent"
    assert pdr.inputs["ordinary_amount"] == Decimal(1000)


def test_night_supplement_gets_no_substitute_regime() -> None:
    """The 15% regime of L. 199/2025 c. 10 is withheld by the sostituto only.

    The 50 EUR supplement is paid in full: net 908.10 + 50 - 53.63 = 904.47.
    """
    night = NightShiftEvent(event_date=date(2026, 9, 10), supplement_amount=Decimal(50))
    result = _september(_REPORTED, facts=_facts(_REPORTED, night))

    assert _tax_postings(result) == []
    (regime,) = (
        d
        for d in result.decisions
        if d.capability == "notte_festivi_turni_substitute_tax"
    )
    assert regime.reason_code == "not_withholding_agent"
    assert regime.amount == _ZERO
    assert result.period_net == Decimal("904.47")


_PLAN = RecoveryPlan(
    kind="trattamento_integrativo",
    original_amount=Decimal(160),
    installment_amount=Decimal(20),
    installments_total=8,
    installments_posted=0,
)


@pytest.mark.parametrize(
    "balances",
    [
        OpeningBalances(
            tax_year=2026,
            regular_periods_closed=8,
            tax_withholding_periods_closed=8,
            recoveries=(RecoveryObligation(tax_year=2025, plan=_PLAN),),
        ),
        OpeningBalances(
            tax_year=2026,
            regular_periods_closed=8,
            tax_withholding_periods_closed=8,
            irpef_withheld=Decimal(100),
        ),
    ],
    ids=["credit-recovery", "irpef-withheld"],
)
def test_opening_tax_state_is_rejected(balances: OpeningBalances) -> None:
    """A household employer never recognized a credit or withheld a tax."""
    with pytest.raises(InvalidInputError, match="not a withholding agent"):
        _september(_REPORTED, opening=balances.to_state())


def test_year_has_no_withholding_and_no_conguaglio() -> None:
    """Every run of 2026, tredicesima and December included, withholds nothing."""
    year = _ENGINE.calculate_year(
        YearInput(
            year=2026,
            employment=_employment(_REPORTED),
            employer=_HOUSEHOLD,
            default_facts=_facts(_REPORTED),
        )
    )

    results = year.period_results
    assert len(results) == 13
    for result in results:
        assert _tax_postings(result) == []
        assert result.period_net == (
            result.period_gross - result.contribution_breakdown.employee
        )
    closing = results[-1].closing_state.ytd
    assert closing.tax.irpef == _ZERO
    assert closing.tax.surtax == _ZERO
    assert closing.trattamento.recognized == _ZERO
    assert closing.somma_esente.recognized == _ZERO
