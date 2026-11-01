"""What keeps the engine from settling the TFR at a termination, as issues."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.employment.fact.inputs import PublicEndOfService

if TYPE_CHECKING:
    pass


#: Capability of the TFR settlement, as the events name it.
CAPABILITY = "termination_tfr"
_KIND = "tfr_settlement_item"
_ZERO = Decimal(0)
_MONTHS = 12
_AT_INPS = frozenset({PublicEndOfService.TFS, PublicEndOfService.TFR_INPS})
#: Months of service up to which a fixed term takes the art. 19 c. 1-ter deduction.
_SHORT_FIXED_TERM = 24
_FINAL = CalculationStatus.FINAL
_INCOMPLETE = CalculationStatus.INCOMPLETE


@dataclass(frozen=True)
class _Gap:
    """Why an amount is not computed: reason, missing fact and explanation.

    ``cause`` is what resolves a gap that names no fact.
    """

    reason: str
    message: str
    fact: str | None = None
    cause: IssueCause = IssueCause.RULE


_TFR_AT_INPS = _Gap(
    "tfr_at_inps",
    "the TFR of a public employee under the TFS or the TFR at INPS is paid by "
    "INPS, not by the employer",
    cause=IssueCause.CONDITION,
)
_PENSION_FUND = _Gap(
    "pension_fund_tfr",
    "the TFR goes to a pension fund, whose sums art. 19 c. 1 TUIR adds to the "
    "reference income: state the payout and its rate",
)
_FUND_UNKNOWN = _Gap(
    "required_fact_missing",
    "the TFR fund at 31 December of the year before the termination is not "
    "stated: set Employment.tfr_fund",
    "tfr_fund",
)
_PERIOD_UNKNOWN = _Gap(
    "required_fact_missing",
    "the start of the employment is not stated, so the TFR of the year and the "
    "years of service are not known: set Employment.employment_period",
    cause=IssueCause.CONDITION,
)
_QUOTAS_UNKNOWN = _Gap(
    "required_fact_missing",
    "the TFR the runs of the termination year accrued is not known: open the "
    "run with the closing state of the run before, or import the balances with "
    "OpeningBalances.tfr_quotas",
    "tfr_quotas",
)
_REVALUATIONS_UNKNOWN = _Gap(
    "required_fact_missing",
    "the revaluations the TFR fund holds, already taxed at the substitute rate "
    "and left out of the taxable (art. 19 c. 1 TUIR), are not stated: set "
    "TfrFundBalance.revaluations",
    "revaluations",
)
_ADVANCES_UNKNOWN = _Gap(
    "required_fact_missing",
    "whether advances were paid out of the TFR fund is not stated: set "
    "TfrFundBalance.advances",
    "advances",
)
_ADVANCES = _Gap(
    "required_fact_missing",
    "advances were paid out of the TFR fund: the conguaglio of their tax (art. "
    "19 c. 4 TUIR) needs their taxable and the tax withheld on them: set "
    "TfrFundBalance.advances_taxable and advances_tax, or state the rate",
    "advances_taxable",
)
_ADVANCES_OVERWITHHELD = _Gap(
    "advances_refund_not_modelled",
    "the tax withheld on the advances exceeds the tax of the whole TFR (art. 19 "
    "c. 4 TUIR): the refund of the conguaglio is not computed; state the rate",
)
_BEFORE_2001 = _Gap(
    "tfr_before_2001_not_modelled",
    "the employment started before 1 January 2001: the TFR accrued up to 31 "
    "December 2000 keeps the rules before D.Lgs. 47/2000 (art. 11 c. 1), which "
    "are not computed; state the rate",
)
_NO_RULES = _Gap(
    "rule_not_in_bundle",
    "the bundle has no separate taxation rules of the TFR for the year of the "
    "termination, or the run is paid in another tax year: state the rate",
)
