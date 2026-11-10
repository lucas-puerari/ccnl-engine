"""Annual construction loyalty premium and one-time milestone parameters."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.provenance.source.rule.models import RuleProvenance


class LoyaltyPremium(BaseModel):
    """Annual anniversary award for clerical employees and middle managers.

    Milestone awards may instead be once-only and cover manual workers.

    The monthly run-chain pay approximates the CCNL's enumerated elements;
    interruptions of actual service and group-company continuity are not
    represented by the employment start date alone. A once-only milestone
    can additionally restrict the eligible categories and employer subsectors;
    manual workers may use a specified number of normal hourly wages.
    A recognised-service milestone uses the caller's seniority fact, which
    must describe the service credited for that award, not merely increments.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    service_years: int = Field(gt=0)
    months: Decimal = Field(default=Decimal(1), gt=0)
    recurrence: Literal["annual", "once"] = "annual"
    categories: tuple[WorkerCategory, ...] = (
        WorkerCategory.IMPIEGATO,
        WorkerCategory.QUADRO,
    )
    subsectors: tuple[str, ...] = ()
    levels: tuple[str, ...] = ()
    service_basis: Literal["actual", "recognised"] = "actual"
    manual_hours: Decimal | None = Field(default=None, gt=0)
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _manual_rate_required(self) -> "LoyaltyPremium":
        """Require an hourly award when manual workers are eligible.

        Returns:
            The validated award parameters.

        Raises:
            ValueError: If a manual worker would otherwise receive monthly pay.
        """
        if WorkerCategory.OPERAIO in self.categories and self.manual_hours is None:
            msg = "manual_hours is required for manual workers"
            raise ValueError(msg)
        return self
