"""Contractual assistance contribution charged per paid hour."""

from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.contract.domain.validity import TimeSeries
from ccnl_engine.provenance.domain.chain import RuleProvenance


class AssistanceContribution(BaseModel):
    """Contribution a CCNL charges per paid hour to fund its joint bodies.

    The CCNL lavoro domestico (art. 54) charges the employer and the worker
    a fixed amount per paid hour for the Cas.Sa.Colf and the other joint
    bodies of the contract; the worker's share is withheld from the pay.

    Attributes:
        employee_per_hour: Worker share per paid hour, in EUR.
        employer_per_hour: Employer share per paid hour, in EUR.
        provenance: Source of the clause.

    Raises:
        ValueError: When a rate is negative.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    employee_per_hour: TimeSeries
    employer_per_hour: TimeSeries
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_non_negative(self) -> Self:
        for name, series in (
            ("employee_per_hour", self.employee_per_hour),
            ("employer_per_hour", self.employer_per_hour),
        ):
            for period in series.periods:
                if period.value is not None and period.value < 0:
                    msg = (
                        f"{name} values must be >= 0; period starting "
                        f"{period.valid_from} has value {period.value}"
                    )
                    raise ValueError(msg)
        return self
