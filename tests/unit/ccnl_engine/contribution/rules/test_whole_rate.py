"""One contribution per worker at the whole rate, to cents.

The UniEmens <Contributo> of <DatiRetributivi> is "l'importo della
contribuzione calcolata sull'imponibile previdenziale del mese corrente
[...] con arrotondamento ai centesimi": the employer pays it less the share
it withholds from the employee.  The payslip withholds that share as one
contribution at the whole employee rate, to cents once (FILCTEM CGIL 2024
guide p. 21: "1.672 x 9,49% = 158,67").  The base above the IVS massimale
is declared apart, with the minor contributions only.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.contribution.rules import whole_rate_addition
from ccnl_engine.employment.inputs import Permanent
from ccnl_engine.pay_item.rounding.policies import money
from tests.unit.ccnl_engine.builders import make_year_rules
from tests.unit.ccnl_engine.contribution.builders import first_run_contributions

if TYPE_CHECKING:
    from ccnl_engine.contribution.results import ContributionBreakdown
    from ccnl_engine.sector.models import YearRules

_D = Decimal
#: The fixed-term industria impiegato of 2026: IVS 23.81%, the rest of the
#: employer rate 5.25% and the NASpI surcharge 1.40%; employee 9.19% IVS
#: and 0.30% CIGS.
_EMPLOYEE, _EMPLOYEE_IVS = _D("0.0949"), _D("0.0919")
_EMPLOYER, _EMPLOYER_IVS = _D("0.3046"), _D("0.2381")


def _rules(sector: TaxSector | None, ceiling: str | None = None) -> YearRules:
    rules = make_year_rules(
        inps={
            "employee_rate": str(_EMPLOYEE),
            "employee_ivs_rate": str(_EMPLOYEE_IVS),
            "employer_rate": str(_EMPLOYER),
            "employer_ivs_rate": str(_EMPLOYER_IVS),
            "ceiling": ceiling,
        }
    )
    return rules.model_copy(update={"sector": sector})


def _amounts(breakdown: ContributionBreakdown) -> dict[str, Decimal]:
    return {c.name: c.amount for c in breakdown.components}


def test_the_employer_pays_the_whole_contribution_less_the_employee() -> None:
    """2382 x 39.95% = 951.61, less 2382 x 9.49% = 226.05 withheld: 725.56."""
    base = _D(2382)
    breakdown = first_run_contributions(
        base, _rules(TaxSector.INDUSTRIA), Permanent(), None
    )

    assert breakdown.employee == money(base * _EMPLOYEE) == _D("226.05")
    assert money(base * (_EMPLOYEE + _EMPLOYER)) == _D("951.61")
    assert breakdown.employer == _D("725.56")
    amounts = _amounts(breakdown)
    assert amounts["ivs_employer"] == money(base * _EMPLOYER_IVS) == _D("567.15")
    assert amounts["non_ivs_employer"] == _D("158.41")


@pytest.mark.parametrize(
    "sector", [TaxSector.PUBBLICA_AMMINISTRAZIONE, TaxSector.AGRICOLTURA, None]
)
def test_other_declarations_round_each_rate(sector: TaxSector | None) -> None:
    """ListaPosPA, DMAG and rules built apart keep the rates rounded apart."""
    base = _D(2385)
    breakdown = first_run_contributions(base, _rules(sector), Permanent(), None)
    split = money(base * _EMPLOYER_IVS) + money(base * (_EMPLOYER - _EMPLOYER_IVS))

    assert breakdown.employer == split


def test_the_sectors_differ_where_the_rounding_does() -> None:
    """A base where the whole rate and the split rates round apart."""
    base = next(
        _D(b)
        for b in range(2000, 3000)
        if money(_D(b) * (_EMPLOYEE + _EMPLOYER))
        - money(_D(b) * _EMPLOYEE_IVS)
        - money(_D(b) * (_EMPLOYEE - _EMPLOYEE_IVS))
        != money(_D(b) * _EMPLOYER_IVS) + money(_D(b) * (_EMPLOYER - _EMPLOYER_IVS))
    )
    whole = first_run_contributions(
        base, _rules(TaxSector.TERZIARIO), Permanent(), None
    )
    split = first_run_contributions(base, _rules(None), Permanent(), None)

    assert whole.employer != split.employer
    assert whole.employee == money(base * _EMPLOYEE)
    assert whole.employee + whole.employer == money(base * (_EMPLOYEE + _EMPLOYER))


def test_the_base_above_the_massimale_takes_the_minor_rates_apart() -> None:
    """The excess is declared apart, at the non-IVS rates only."""
    ceiling = _D(120000)
    ytd = ceiling - _D(1000)
    base = _D(2385)
    breakdown = first_run_contributions(
        base,
        _rules(TaxSector.INDUSTRIA, ceiling=str(ceiling)),
        Permanent(),
        None,
        ytd_inps_base=ytd,
    )
    excess = base - _D(1000)
    other = (_EMPLOYEE - _EMPLOYEE_IVS) + (_EMPLOYER - _EMPLOYER_IVS)
    whole = money(_D(1000) * (_EMPLOYEE + _EMPLOYER)) + money(excess * other)

    assert breakdown.employee + breakdown.employer == whole


@pytest.mark.parametrize(
    ("sector", "expected"),
    [(TaxSector.TERZIARIO, None), (TaxSector.PUBBLICA_AMMINISTRAZIONE, "split")],
)
def test_a_further_rate_joins_the_rounding_of_the_sector(
    sector: TaxSector, expected: str | None
) -> None:
    """The 0.77% sickness supplement of the pubblici esercizi."""
    base, rate = _D(3459), _D("0.0077")
    rules = _rules(sector)
    breakdown = first_run_contributions(base, rules, Permanent(), None)
    added = whole_rate_addition(breakdown, rules, base, rate)

    if expected == "split":
        assert added == money(base * rate)
        return
    total = breakdown.employee + breakdown.employer
    assert total + added == money(base * (_EMPLOYEE + _EMPLOYER + rate))


def test_a_further_rate_above_the_massimale() -> None:
    """The excess takes the further rate with the minor rates."""
    ceiling = _D(120000)
    base, rate = _D(3459), _D("0.0077")
    rules = _rules(TaxSector.TERZIARIO, ceiling=str(ceiling))
    breakdown = first_run_contributions(
        base, rules, Permanent(), None, ytd_inps_base=ceiling - _D(1000)
    )
    added = whole_rate_addition(breakdown, rules, base, rate)
    other = (_EMPLOYEE - _EMPLOYEE_IVS) + (_EMPLOYER - _EMPLOYER_IVS)
    with_rate = money(_D(1000) * (_EMPLOYEE + _EMPLOYER + rate)) + money(
        (base - _D(1000)) * (other + rate)
    )
    without = money(_D(1000) * (_EMPLOYEE + _EMPLOYER)) + money(
        (base - _D(1000)) * other
    )

    assert added == with_rate - without


def test_no_employer_rate_charges_the_employer_nothing() -> None:
    """A whole contribution of the employee alone leaves the employer at zero."""
    rules = make_year_rules(
        inps={
            "employee_rate": str(_EMPLOYEE),
            "employee_ivs_rate": str(_EMPLOYEE_IVS),
            "employer_rate": "0",
            "employer_ivs_rate": "0",
            "ceiling": None,
        }
    ).model_copy(update={"sector": TaxSector.INDUSTRIA})
    breakdown = first_run_contributions(_D(2385), rules, Permanent(), None)

    assert breakdown.employer == 0
    assert {c.name for c in breakdown.components} == {
        "ivs_employee",
        "non_ivs_employee",
    }


_BASES = [_D(b) for b in range(2000, 2200, 7)]


@pytest.mark.parametrize("sector", [TaxSector.INDUSTRIA, TaxSector.EDILIZIA])
def test_the_components_add_up_to_the_shares_of_every_base(sector: TaxSector) -> None:
    """Employee and employer components sum to the shares, the whole to cents."""
    rules = _rules(sector)
    for base in _BASES:
        breakdown = first_run_contributions(base, rules, Permanent(), None)
        employer = sum(
            (c.amount for c in breakdown.components if c.name.endswith("_employer")),
            _D(0),
        )
        assert employer == breakdown.employer, base
        assert breakdown.employee + breakdown.employer == money(
            base * (_EMPLOYEE + _EMPLOYER)
        ), base


def test_a_further_rate_joins_the_whole_of_every_base() -> None:
    """The addition is the whole with the rate less the whole without it."""
    rate = _D("0.0077")
    rules = _rules(TaxSector.TERZIARIO)
    differs = False
    for base in _BASES:
        breakdown = first_run_contributions(base, rules, Permanent(), None)
        added = whole_rate_addition(breakdown, rules, base, rate)
        total = breakdown.employee + breakdown.employer
        assert total + added == money(base * (_EMPLOYEE + _EMPLOYER + rate)), base
        differs |= added != money(base * rate)
    assert differs


def test_a_further_rate_without_ivs_components() -> None:
    """Rates with no IVS share: the whole base takes the minor rates."""
    rules = make_year_rules(
        inps={
            "employee_rate": "0.0030",
            "employee_ivs_rate": "0",
            "employer_rate": "0.0525",
            "employer_ivs_rate": "0",
            "ceiling": None,
        }
    ).model_copy(update={"sector": TaxSector.TERZIARIO})
    rate = _D("0.0077")
    for base in _BASES:
        breakdown = first_run_contributions(base, rules, Permanent(), None)
        added = whole_rate_addition(breakdown, rules, base, rate)
        assert added == money(base * _D("0.0632")) - money(base * _D("0.0555")), base


def test_the_employee_share_is_rounded_once() -> None:
    """1,672 x 9.49% = 158.67; the IVS and CIGS rates apart give 158.68."""
    base = _D(1672)
    whole = first_run_contributions(
        base, _rules(TaxSector.INDUSTRIA), Permanent(), None
    )
    split = first_run_contributions(base, _rules(None), Permanent(), None)
    amounts = _amounts(whole)

    assert whole.employee == _D("158.67")
    assert split.employee == _D("158.68")
    assert amounts["ivs_employee"] == _D("153.66")
    assert amounts["non_ivs_employee"] == _D("5.01")


def test_the_employee_share_above_the_massimale() -> None:
    """The excess takes the minor employee rate apart."""
    ceiling = _D(120000)
    base = _D(2385)
    breakdown = first_run_contributions(
        base,
        _rules(TaxSector.INDUSTRIA, ceiling=str(ceiling)),
        Permanent(),
        None,
        ytd_inps_base=ceiling - _D(1000),
    )
    minor = _EMPLOYEE - _EMPLOYEE_IVS

    assert breakdown.employee == money(_D(1000) * _EMPLOYEE) + money(
        (base - _D(1000)) * minor
    )


def test_no_employee_rate_withholds_nothing() -> None:
    """An employer-only rate leaves the employee share at zero."""
    rules = make_year_rules(
        inps={
            "employee_rate": "0",
            "employee_ivs_rate": "0",
            "employer_rate": str(_EMPLOYER),
            "employer_ivs_rate": str(_EMPLOYER_IVS),
            "ceiling": None,
        }
    ).model_copy(update={"sector": TaxSector.INDUSTRIA})
    breakdown = first_run_contributions(_D(2385), rules, Permanent(), None)

    assert breakdown.employee == 0
    assert not any(c.name.endswith("_employee") for c in breakdown.components)
