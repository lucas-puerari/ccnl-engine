"""Public research and university Perseo Sirio contributions on a hand-computed month.

For TFR-relevant pay of EUR 2,000.00, each 1% cash contribution is EUR
20.00; employer solidarity is 10% of EUR 20.00 = EUR 2.00. Before the
fund was recorded in these agreements the cash contributions were EUR 0.00.
The public TFR allocation and pre-2001 optants' 1.5% TFS-base incentive
are not cash contributions to the pension fund.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.fund.models import FundContributionBase
from ccnl_engine.pension_fund.inputs import PensionFundEnrolment
from ccnl_engine.pension_fund.models import ComplementaryPensionRules
from ccnl_engine.pension_fund.rules import contribute, resolve_terms


@pytest.mark.parametrize(
    ("agreement", "day"),
    [
        ("enti-ricerca-aran", date(2026, 3, 1)),
        ("universita-aran", date(2026, 3, 1)),
        ("universita-tecnologi-aran", date(2026, 3, 1)),
    ],
)
def test_enrolled_public_worker_month(agreement: str, day: date) -> None:
    """EUR 2,000 TFR base gives EUR 20 each and EUR 2 solidarity."""
    ccnl = load_ccnl(agreement)
    enrolment = PensionFundEnrolment("PERSEO_SIRIO", Decimal("0.01"), True)
    rules = ComplementaryPensionRules(
        deduction_cap=Decimal("5300.00"), solidarity_rate=Decimal("0.10")
    )
    terms = resolve_terms(ccnl, enrolment, None, day, rules, apprentice=False)
    payment = contribute(terms, Decimal("2000.00"), Decimal(0))
    assert terms.fund.contribution_base is FundContributionBase.TFR_BASE
    assert terms.employee_min_rate == Decimal("0.01")
    assert terms.tfr_notional is True
    assert payment.employer == Decimal("20.00")
    assert payment.employee == Decimal("20.00")
    assert payment.solidarity == Decimal("2.00")
