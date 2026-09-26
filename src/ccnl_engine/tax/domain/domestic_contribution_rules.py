"""Flat per-hour INPS contribution table for lavoro domestico."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.primitives import NonNegativeRate


class DomesticInpsHoursBracket(BaseModel):
    """Flat-hour rates for domestic workers with > ``weekly_hours_threshold`` h/week.

    Applies regardless of the worker's actual hourly wage; overrides all
    ``DomesticInpsWageBracket`` entries when the hours condition is met.
    """

    model_config = ConfigDict(extra="forbid")

    employee_per_hour: NonNegativeRate
    employer_per_hour: NonNegativeRate
    employer_per_hour_fixed_term: NonNegativeRate


class DomesticInpsWageBracket(BaseModel):
    """One hourly-wage bracket in the domestic INPS flat-rate table.

    ``hourly_rate_up_to`` is inclusive; ``None`` on the last entry means
    unbounded (covers any wage above the preceding bracket's threshold).
    """

    model_config = ConfigDict(extra="forbid")

    hourly_rate_up_to: Decimal | None
    employee_per_hour: NonNegativeRate
    employer_per_hour: NonNegativeRate
    employer_per_hour_fixed_term: NonNegativeRate
    provenance: RuleProvenance | None = None


class DomesticInpsRates(BaseModel):
    """Flat per-hour INPS contribution table for lavoro domestico.

    The selector is two-dimensional (INPS Circ. 9/2026, table 1):
    * ``weekly_hours > weekly_hours_threshold`` → use ``hours_bracket``,
      regardless of the worker's actual wage.
    * otherwise → walk ``wage_brackets`` in ascending ``hourly_rate_up_to``
      order and use the first bracket whose threshold is not exceeded.

    ``wage_brackets`` must be non-empty and end with one entry whose
    ``hourly_rate_up_to`` is ``None`` (the open-ended top bracket).
    """

    model_config = ConfigDict(extra="forbid")

    weekly_hours_threshold: int = Field(ge=0)
    hours_bracket: DomesticInpsHoursBracket
    wage_brackets: list[DomesticInpsWageBracket] = Field(min_length=1)
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_wage_brackets(self) -> Self:
        for i, bracket in enumerate(self.wage_brackets[:-1]):
            if bracket.hourly_rate_up_to is None:
                msg = (
                    f"DomesticInpsRates: wage_brackets[{i}] has "
                    "hourly_rate_up_to=None but is not the last bracket"
                )
                raise ValueError(msg)
            nxt = self.wage_brackets[i + 1].hourly_rate_up_to
            if nxt is not None and nxt <= bracket.hourly_rate_up_to:
                msg = (
                    "DomesticInpsRates: wage_brackets must have strictly "
                    f"ascending hourly_rate_up_to: bracket {i} = "
                    f"{bracket.hourly_rate_up_to} >= bracket {i + 1} = {nxt}"
                )
                raise ValueError(msg)
        last = self.wage_brackets[-1]
        if last.hourly_rate_up_to is not None:
            msg = (
                "DomesticInpsRates: last wage_bracket must have "
                f"hourly_rate_up_to=None (open-ended), "
                f"got {last.hourly_rate_up_to!r}"
            )
            raise ValueError(msg)
        return self
