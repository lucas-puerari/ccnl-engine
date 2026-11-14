"""The termination settles the TFR a partial conferment keeps in the company.

D.Lgs. 252/2005 art. 8 c. 9-bis: a worker may pay the fund only part of the
TFR maturando; the rest accrues in the company and is settled with the
termination like the TFR of a worker with no fund.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.inputs import NoPensionFund, PensionFundEnrolment
from tests.mutation.ccnl_engine.severance.settlement.test_services_wiring import (
    _run,
    _settlement,
)


def test_the_kept_half_is_settled() -> None:
    """Half to Cometa: the settlement takes half the quota of the run."""
    half = PensionFundEnrolment(
        "COMETA", Decimal("0.012"), tfr_to_fund=True, tfr_share=Decimal("0.5")
    )
    (partial, _) = _settlement(_run(pension_fund=half))
    (kept, _) = _settlement(_run(pension_fund=NoPensionFund()))
    assert partial.reason_code != "pension_fund_tfr"
    assert partial.amount is not None
    assert kept.amount is not None
    assert partial.amount < kept.amount
