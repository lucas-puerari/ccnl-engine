"""Contributions of a public employee to the end-of-service fund of INPS.

INPS, 'I contributi dei dipendenti pubblici': "ENPAS (TFS) 9,6 7,1 2,5
ENPAS (TFR) 9,6 9,6 -- INADEL (TFS) 6,1 3,6 2,5 INADEL (TFR) 6,1 6,1 --".
DPCM 20 dicembre 1999 art. 1 c. 3: under the TFR "la retribuzione lorda
viene ridotta in misura pari al contributo previdenziale obbligatorio
soppresso", for "l'invarianza della retribuzione netta complessiva".

Funzioni Centrali (ENPAS), Funzionari, January 2026: 2227.99, base 80% =
1782.392 -> 1782.39.

- TFS: worker 2.50% = 44.55975 -> 44.56, administration 7.10% =
  126.54969 -> 126.55; with the CTPS (196.06 and 539.17) and the credit
  (0.35% of 2227.99 = 7.797965 -> 7.80) 248.42 and 665.72.
- TFR at INPS: the gross reduced by 44.56 to 2183.43 (a negative earning,
  the INPS base and the end-of-service base unreduced), administration
  9.60% = 171.10944 -> 171.11; 203.86 and 710.28; the same net, taxable and
  cost of the administration as the TFS (2227.99 + 665.72 = 2183.43 +
  710.28 = 2893.71).
- TFR at the employer: the CTPS and the credit, 203.86 and 539.17, the TFR
  accrued in the company.

Funzioni Locali (INADEL), Istruttori: the tredicesima of 2026, 1928.23,
is part of the base: 1542.584 -> 1542.58, worker 38.5645 -> 38.56,
administration 3.60% = 55.53288 -> 55.53.  ENPAS leaves it out.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment, InvalidInputError
from ccnl_engine.inputs import (
    FixedTerm,
    NaspiExclusion,
    NoPensionFund,
    PensionFundEnrolment,
    Permanent,
    PublicEndOfService,
)
from tests.acceptance.legal_scenarios._support import EMPLOYER, ENGINE, regular_period
from tests.fixtures.current_year import employment_only
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario


def _employment(
    regime: PublicEndOfService | None,
    slug: str = "funzioni-centrali-aran.json",
    level: str = "FUNZIONARI",
) -> Employment:
    return Employment(
        ccnl_slug=slug,
        level_code=level,
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        public_end_of_service=regime,
    )


def _january(regime: PublicEndOfService | None) -> PeriodResult:
    return regular_period(
        employment=_employment(regime), current_year=employment_only()
    )


def _components(result: PeriodResult) -> dict[str, Decimal]:
    return {c.name: c.amount for c in result.contribution_breakdown.components}


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("regime", "employee", "employer", "names"),
    [
        (
            PublicEndOfService.TFS,
            "248.42",
            "665.72",
            ("tfs_employee", "tfs_employer", "credit_employee"),
        ),
        (
            PublicEndOfService.TFR_INPS,
            "203.86",
            "710.28",
            ("tfr_employer", "credit_employee"),
        ),
        (PublicEndOfService.TFR_EMPLOYER, "203.86", "539.17", ("credit_employee",)),
    ],
    ids=["tfs", "tfr_inps", "tfr_employer"],
)
def test_contributions_of_the_regime(
    regime: PublicEndOfService, employee: str, employer: str, names: tuple[str, ...]
) -> None:
    """ENPAS on 80% of the pay, the CTPS beside it."""
    result = _january(regime)
    breakdown = result.contribution_breakdown
    assert breakdown.employee == Decimal(employee)
    assert breakdown.employer == Decimal(employer)
    components = _components(result)
    for name in names:
        assert name in components
    assert "public_end_of_service_unknown" not in {i.code for i in result.issues}


def test_tfr_keeps_the_net_of_the_tfs() -> None:
    """DPCM art. 1 c. 3: the same net, taxable and cost, a lower gross."""
    tfs = _january(PublicEndOfService.TFS)
    tfr = _january(PublicEndOfService.TFR_INPS)
    assert tfs.period_net == tfr.period_net
    taxable = [r.closing_state.cash.earnings.taxable for r in (tfs, tfr)]
    assert taxable[0] == taxable[1]
    assert tfs.period_employer_cost == tfr.period_employer_cost == Decimal("2893.71")
    assert tfs.period_gross - tfr.period_gross == Decimal("44.56")
    (reduction,) = [i for i in tfr.pay_items if i.kind == "public_tfr_reduction"]
    assert reduction.amount == Decimal("-44.56")


@pytest.mark.parametrize(
    ("regime", "posted"),
    [
        (PublicEndOfService.TFS, False),
        (PublicEndOfService.TFR_INPS, False),
        (PublicEndOfService.TFR_EMPLOYER, True),
    ],
    ids=["tfs", "tfr_inps", "tfr_employer"],
)
def test_tfr_accrued_by_the_employer_alone(
    regime: PublicEndOfService, posted: bool
) -> None:
    """INPS accrues the TFR notionally; the TFS accrues none."""
    result = _january(regime)
    assert (_entry(result, "tfr_accrual") > 0) is posted


def test_unknown_regime_is_a_missing_fact() -> None:
    """Without the regime the contributions are left out."""
    result = _january(None)
    (issue,) = [i for i in result.issues if i.code == "public_end_of_service_unknown"]
    assert issue.fact == "public_end_of_service"
    assert not result.is_payable


@pytest.mark.parametrize(
    ("slug", "level", "employee"),
    [
        ("funzioni-locali-aran.json", "ISTRUTTORI", "38.56"),
        ("funzioni-centrali-aran.json", "FUNZIONARI", None),
    ],
    ids=["inadel", "enpas"],
)
def test_tredicesima_in_the_base_of_inadel_alone(
    slug: str, level: str, employee: str | None
) -> None:
    """L. 152/1968 art. 11 counts the tredicesima, DPR 1032/1973 does not."""
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment(PublicEndOfService.TFS, slug, level),
            employer=EMPLOYER,
            current_year=employment_only(),
        )
    )
    (thirteenth,) = [
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind == "thirteenth"
    ]
    components = _components(thirteenth)
    if employee is None:
        assert "tfs_employee" not in components
        return
    assert components["tfs_employee"] == Decimal(employee)
    assert components["tfs_employer"] == Decimal("55.53")


@pytest.mark.parametrize(
    "employment",
    [
        replace(
            _employment(PublicEndOfService.TFS),
            contract_type=FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE),
        ),
        replace(
            _employment(PublicEndOfService.TFS),
            pension_fund=PensionFundEnrolment(
                "PERSEO_SIRIO", Decimal("0.01"), tfr_to_fund=True
            ),
        ),
        replace(
            _employment(PublicEndOfService.TFR_INPS),
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
        ),
    ],
    ids=["tfs_fixed_term", "tfs_enrolled", "private_ccnl"],
)
def test_regimes_the_employment_cannot_have(employment: Employment) -> None:
    """The TFS of a fixed term or of a fund member, any regime off the PA."""
    with pytest.raises(InvalidInputError, match="public_end_of_service"):
        regular_period(employment=employment, current_year=employment_only())
