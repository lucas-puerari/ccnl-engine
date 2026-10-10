"""Foreign tax credit applied by the conguaglio of the 2026 C3 year.

Art. 23 c. 3 DPR 600/1973 lets the withholding agent deduct at the
conguaglio the foreign tax paid on employment income produced abroad, up
to the Italian tax on that income (art. 165 c. 1 TUIR).  The surtax is due
only when the IRPEF net of the credit is due (D.Lgs. 446/1997 art. 50 c. 2,
D.Lgs. 360/1998 art. 1 c. 4).

Expected values use the independent 2026 IRPEF oracle on the final taxable
income T of the year: quota = imposta lorda x income / T, to the cent.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from functools import cache
from typing import TYPE_CHECKING

from ccnl_engine.payroll.period.inputs import PeriodFacts
from ccnl_engine.payroll.taxation.inputs_prior_year import (
    ForeignTaxPaid,
    PriorYearTaxFacts,
)
from ccnl_engine.payroll.year.services_competence import (
    calculate_competence_year,
)
from tests.fixtures.normative_oracles.irpef_2026 import gross_irpef, net_irpef
from tests.helpers import year_plan

if TYPE_CHECKING:
    from ccnl_engine.payroll.year.results import CompetenceYearResult

_CCNL = "metalmeccanico-federmeccanica.json"
_FACTS = PeriodFacts(regione="IT-25")
_ZERO = Decimal(0)


def _year(*taxes: ForeignTaxPaid) -> CompetenceYearResult:
    return calculate_competence_year(
        year_plan(
            2026,
            _CCNL,
            "C3",
            facts=_FACTS,
            prior_year=PriorYearTaxFacts(foreign_taxes=taxes),
        )
    )


@cache
def _plain() -> CompetenceYearResult:
    return _year()


@cache
def _partly_abroad() -> CompetenceYearResult:
    """Return the year with 10,000 EUR earned in France, taxed 500 EUR there.

    Returns:
        The year result.
    """
    return _year(ForeignTaxPaid("FR", Decimal(10000), Decimal(500)))


def _capability(
    year: CompetenceYearResult, capability: str
) -> list[tuple[str, Decimal]]:
    last = year.period_results[-1]
    return [
        (d.reason_code, d.amount or _ZERO)
        for d in last.decisions
        if d.capability == capability
    ]


def test_credit_below_the_quota_is_deducted() -> None:
    """500 EUR is below the quota of the 10,000 EUR: all of it is credited."""
    year = _partly_abroad()
    ytd = year.period_results[-1].closing_state.cash
    taxable = ytd.earnings.taxable
    quota = (gross_irpef(taxable) * Decimal(10000) / taxable).quantize(
        Decimal("0.01"), ROUND_HALF_UP
    )
    assert quota > Decimal(500)
    assert _capability(year, "foreign_tax_credit") == [("credit_applied", Decimal(500))]
    assert ytd.tax.irpef == net_irpef(taxable) - Decimal(500)


def test_credit_leaves_the_surtax_unchanged_while_irpef_is_due() -> None:
    """The regional surtax is computed on the income, not on the IRPEF."""
    plain = _capability(_plain(), "addizionale_regionale")
    assert _capability(_partly_abroad(), "addizionale_regionale") == plain


def test_credit_only_on_the_conguaglio() -> None:
    """The runs before the conguaglio withhold as without the credit."""
    plain = _plain().period_results
    runs = _partly_abroad().period_results
    for before, run in zip(plain[:-1], runs[:-1], strict=True):
        assert run.closing_state.cash.tax == before.closing_state.cash.tax
        assert not [d for d in run.decisions if d.capability == "foreign_tax_credit"]


def test_credit_above_the_netta_cancels_irpef_and_surtax() -> None:
    """All the income earned abroad and taxed at 20,000 EUR there.

    The ratio is 1: the quota is the whole imposta lorda, above the
    imposta netta, so the credit is the imposta netta (LIMITE 2).  No IRPEF
    is due, so no surtax either: what was withheld is refunded.
    """
    year = _year(ForeignTaxPaid("FR", Decimal(40000), Decimal(20000)))
    last = year.period_results[-1]
    taxable = last.closing_state.cash.earnings.taxable
    assert _capability(year, "foreign_tax_credit") == [
        ("limited_to_net_tax", net_irpef(taxable))
    ]
    assert last.closing_state.cash.tax.irpef == _ZERO
    assert _capability(year, "addizionale_regionale")[0] == ("no_irpef_due", _ZERO)
    assert last.closing_state.cash.obligations.surtax == ()
