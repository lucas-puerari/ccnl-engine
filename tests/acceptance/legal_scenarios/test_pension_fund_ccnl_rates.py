"""Negotiated fund rates of single CCNLs, each on the base of its fund.

Each run is January 2026, the rate times the base rounded half up to the
cent, the solidarity 10% of the employer contribution (D.Lgs. 252/2005 art.
16 c. 1).  Alifond, Fondapi on the food PMI, Fonchim and Prevedi compute on
the pay that enters the TFR, as their Scheda 'I destinatari e i contributi'
(or the Fonchim opuscolo informativo 2026) states:

- Alimentari (Federalimentare), level 3 in January 2026: 1566.16 minimum
  + 522.32 contingenza + 10.33 EDR + 85.41 IAR = 2184.22.  ALIFOND
  employer 1.50% = 32.7633 -> 32.76, employee minimum 1% = 21.8422 ->
  21.84, solidarity 3.276 -> 3.28.
- Alimentari PMI (Unionalimentari), level 4 in January 2026: 1746.87
  minimum + 525.02 contingenza + 10.33 EDR = 2282.22.  Fondapi computes
  on the 'Retribuzione TFR' (Scheda 'I destinatari e i contributi',
  section CCNL PMI ALIMENTARE): employer 1.20% = 27.38664 -> 27.39,
  employee minimum 1.00% = 22.8222 -> 22.82, solidarity 2.739 -> 2.74.
- Chimica farmaceutica (Federchimica), level D1 in January 2026: 2360.26
  a month.  FONCHIM employer 2.10% + 0.25% = 2.35% = 55.46611 -> 55.47,
  employee minimum 1.20% = 28.32312 -> 28.32, solidarity 5.547 -> 5.55.
- Edilizia industria (ANCE), level 5 in January 2026: 2134.70 a month.
  Prevedi, option A of its Scheda (note 2): employer 1% and employee at
  least 1% of the pay the TFR is computed on = 21.347 -> 21.35 each; an
  impiegato of level 5 also owes the contractual 15.00 (note 1): employer
  36.35, solidarity 3.635 -> 3.64.
- Metalmeccanico (Federmeccanica), level C3 in January 2026: 2158.26 a
  month, the consolidated minimum.  Cometa computes the employer 2% (2.2%
  for a member enrolled after 5 February 2021 before turning 35) and the
  employee minimum 1.2% on the minimi contrattuali, a higher employee rate
  on the TFR base (Scheda, notes 1 and 2): employer 43.1652 -> 43.17 or
  47.48172 -> 47.48, employee 25.89912 -> 25.90.  With two seniority
  increments of 29.64 the pay is 2217.54: a 2% employee rate takes
  44.3508 -> 44.35, the employer still 43.17 on the minimum.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import (
    PensionFundEnrolment,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from tests.acceptance.legal_scenarios._support import regular_period
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.results import CalculationDecision

pytestmark = pytest.mark.legal_scenario


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def _pension_decision(result: PeriodResult) -> CalculationDecision:
    return next(
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    )


def test_alifond_on_the_food_industry() -> None:
    """Alimentari level 3 enrolled in ALIFOND at the 1% minimum."""
    employment = Employment(
        ccnl_slug="alimentari-federalimentare.json",
        level_code="3",
        seniority=new_hire(),
        pension_fund=PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=True),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment)
    decision = _pension_decision(result)
    assert decision.inputs["base"] == Decimal("2184.22")
    assert _entry(result, "pension_fund_employer") == Decimal("32.76")
    assert _entry(result, "pension_fund_employee") == Decimal("21.84")
    assert decision.inputs["solidarity"] == Decimal("3.28")


def test_fondapi_on_the_food_pmi() -> None:
    """Alimentari PMI level 4 enrolled in FONDAPI at the 1% minimum."""
    employment = Employment(
        ccnl_slug="alimentari-pmi-unionalimentari.json",
        level_code="4",
        seniority=new_hire(),
        pension_fund=PensionFundEnrolment("FONDAPI", Decimal("0.01"), tfr_to_fund=True),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment)
    decision = _pension_decision(result)
    assert decision.inputs["base"] == Decimal("2282.22")
    assert _entry(result, "pension_fund_employer") == Decimal("27.39")
    assert _entry(result, "pension_fund_employee") == Decimal("22.82")
    assert decision.inputs["solidarity"] == Decimal("2.74")


def test_fonchim_on_the_chemical_industry() -> None:
    """Chimica farmaceutica D1 enrolled in FONCHIM at the 1.20% minimum."""
    employment = Employment(
        ccnl_slug="chimica-farmaceutica-federchimica.json",
        level_code="D1",
        seniority=new_hire(),
        pension_fund=PensionFundEnrolment(
            "FONCHIM", Decimal("0.012"), tfr_to_fund=True
        ),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment)
    decision = _pension_decision(result)
    assert decision.inputs["base"] == Decimal("2360.26")
    assert _entry(result, "pension_fund_employer") == Decimal("55.47")
    assert _entry(result, "pension_fund_employee") == Decimal("28.32")
    assert decision.inputs["solidarity"] == Decimal("5.55")


def test_prevedi_voluntary_contributions() -> None:
    """Edilizia industria level 5 enrolled in PREVEDI at 1%."""
    employment = Employment(
        ccnl_slug="edilizia-ance.json",
        level_code="5",
        category=WorkerCategory.IMPIEGATO,
        seniority=new_hire(),
        pension_fund=PensionFundEnrolment("PREVEDI", Decimal("0.01"), tfr_to_fund=True),
        contract_type=Permanent(),
    )
    result = regular_period(employment=employment)
    decision = _pension_decision(result)
    assert decision.inputs["base"] == Decimal("2134.70")
    assert _entry(result, "pension_fund_employer") == Decimal("36.35")
    assert _entry(result, "pension_fund_employee") == Decimal("21.35")
    assert decision.inputs["solidarity"] == Decimal("3.64")


def _cometa(
    rate: str, young_member: bool | None, seniority_months: int = 0
) -> PeriodResult:
    seniority = (
        new_hire()
        if seniority_months == 0
        else SeniorityFact(seniority_months, date(2026, 1, 1), SenioritySource.PAYSLIP)
    )
    employment = Employment(
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        seniority=seniority,
        pension_fund=PensionFundEnrolment(
            "COMETA", Decimal(rate), tfr_to_fund=True, young_member=young_member
        ),
        contract_type=Permanent(),
    )
    return regular_period(employment=employment)


@pytest.mark.parametrize(
    ("young_member", "employer"),
    [(False, Decimal("43.17")), (True, Decimal("47.48"))],
    ids=["two_percent", "young_member"],
)
def test_cometa_on_the_contractual_minimum(
    young_member: bool,
    employer: Decimal,
) -> None:
    """2% or 2.2% and 1.2% of the 2158.26 minimum."""
    result = _cometa("0.012", young_member)
    assert _pension_decision(result).inputs["base"] == Decimal("2158.26")
    assert _entry(result, "pension_fund_employer") == employer
    assert _entry(result, "pension_fund_employee") == Decimal("25.90")


def test_cometa_higher_employee_rate_on_the_tfr_base() -> None:
    """2% chosen with two increments: 44.35 on 2217.54, employer 43.17."""
    result = _cometa("0.02", young_member=False, seniority_months=60)
    assert result.period_gross == Decimal("2217.54")
    assert _entry(result, "pension_fund_employer") == Decimal("43.17")
    assert _entry(result, "pension_fund_employee") == Decimal("44.35")


def test_cometa_unknown_young_membership_is_a_missing_fact() -> None:
    """The base rate is shown and the run names the fact."""
    result = _cometa("0.012", None)
    assert _entry(result, "pension_fund_employer") == Decimal("43.17")
    codes = {i.code for i in result.issues}
    assert "pension_fund_young_member_unknown" in codes
