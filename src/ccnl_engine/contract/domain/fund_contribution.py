"""Fixed contribution a CCNL charges the employer for every worker to its fund."""

from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.contract.domain.validity import TimeSeries
from ccnl_engine.provenance.domain.chain import RuleProvenance


class ContractualFundContribution(BaseModel):
    """Monthly employer contribution owed to a fund whatever the enrolment.

    Some CCNLs charge the employer a fixed amount a month per worker, which
    enrols the worker in the fund by contract (e.g. the 5 EUR "riparametrati
    sul base 100" the CCNL Materiali da costruzione owes Fondapi from 1
    January 2022).  It is an employer contribution to a pension fund: outside
    the INPS base with the 10% solidarity contribution and within the
    deduction cap of the worker's contributions.

    Attributes:
        code: Code of the fund it is paid to.
        description: Name of the fund.
        monthly_by_level: Amount a month for each level code, in EUR.
        provenance: Source of the clause.

    Raises:
        ValueError: When an amount is negative.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    monthly_by_level: dict[str, TimeSeries]
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_non_negative(self) -> Self:
        for level, series in self.monthly_by_level.items():
            for period in series.periods:
                if period.value is not None and period.value < 0:
                    msg = (
                        f"monthly_by_level[{level}] must be >= 0; period "
                        f"starting {period.valid_from} has {period.value}"
                    )
                    raise ValueError(msg)
        return self
