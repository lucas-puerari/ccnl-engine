"""Ordinary contribution of the bilateral solidarity fund of a CCNL.

D.Lgs. 148/2015 art. 26 has the sectors outside the CIGO and CIGS set up a
solidarity fund at INPS by collective agreement; the decree of each fund
sets its ordinary contribution on the INPS taxable pay, split between the
employer and the worker.  The fund belongs to the CCNL, not to the INPS
sector: in credito the bancari ABI and the BCC have funds of their own.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from ccnl_engine.primitives import PercentageRate
from ccnl_engine.provenance.source.models_chain import RuleProvenance

__all__ = ["SolidarityFund"]


class SolidarityFund(BaseModel):
    """Ordinary contribution of a solidarity fund on the INPS base.

    Attributes:
        code: Short name of the fund.
        employer_rate: Share of the ordinary contribution the employer pays.
        employee_rate: Share the worker pays, withheld from the pay.
        provenance: Source of the rates and of the workers they cover:
            every worker with a permanent contract, dirigenti and
            apprentices included.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    employer_rate: PercentageRate
    employee_rate: PercentageRate
    provenance: RuleProvenance
