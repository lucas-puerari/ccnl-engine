"""Allowance models for contractual and individual remuneration."""

from datetime import date
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import RuleProvenance


class Allowance(BaseModel):
    """A named fixed monthly allowance attached to a CCNL level.

    ``role`` restricts the allowance to workers holding that role (``None``
    means every worker at the level). ``months_per_year`` overrides the
    contract-wide ``additional_months`` for this allowance only. The
    relevance flags exclude the allowance from the TFR base (with the
    end-of-service base of a public employee and the fund bases on it) or the
    apprenticeship-percentage base.  ``contribution_relevant`` false is
    rejected: the engine does not take an allowance out of the INPS base.
    ``apprenticeship_pct_relevant=False`` means the allowance is paid at full
    value even for percentage-based apprentices (e.g. the EDR, which Italian
    CCNL commonly leave out of the elements the apprenticeship percentage
    applies to).  The default ``True`` reduces the allowance by the
    percentage together with the base salary; a CCNL that lists the reduced
    elements exempts every allowance it does not list.

    ``percentage_rate`` calculates a role supplement on the worker's own
    base pay plus ``percentage_base_allowances``. ``floor_level`` identifies
    the comparison level for a separate ordinary-remuneration integration,
    without changing contractual base salary or the supplement percentage.
    The integration is not the special supplement listed in Art. 24(4)
    for the Art. 17-18 percentage bases.

    ``absorbed_by_individual_excess`` reduces the allowance by the worker's paid
    individual elements, down to zero, leaving those elements whole (ANASTE
    art. 70 c. 2: the nurse allowance absorbed "fino a concorrenza").
    ``individual=True`` marks an element of the worker, not of the CCNL
    (:class:`~ccnl_engine.compensation.individual.inputs.IndividualElement`):
    the hourly base counts it as the CCNL says
    (:class:`~ccnl_engine.working_time.supplement.models.IndividualElementsRule`).

    ``in_service_on`` limits the allowance to the workers in service on
    that day (Logistica Confetra art. 60 c. 8: the EDR of the workers "in
    servizio alla data del 26 gennaio 2011"): it is paid only when the
    employment started on or before it, and not when the start is unknown.
    ``service_months_threshold`` includes the allowance only when the
    recognised seniority (``Employment.seniority``) is known and at least
    this many months on the run; unknown, the run names the missing fact.
    ``service_months_until`` closes the band (the RPD of the AFAM docenti).
    ``career_service`` gates on ``SeniorityFact.career_months`` when stated
    (Farmacie Tabella C: the years in level 1 and Area Q).

    ``part_time_proportionable=False`` marks allowances paid at their full
    contractual value whatever the part-time fraction (fixed welfare
    contributions, presence-based indennità the CCNL do not reduce).

    ``replaced_by`` names what replaces a national element paid only in its
    absence: ``provincial_element`` (Commercio Art. 215, terzo elemento),
    decided by ``EmployerProfile.provincial_pay_element``;
    ``second_level_premium`` (Unionalimentari, elemento di garanzia
    retributiva), decided by ``EmployerProfile.second_level_premium``.

    ``in_kind=True``: a benefit in kind (board and lodging, domestico art. 36),
    unpaid on a regular run but in the TFR base, paid in cash in extra months.
    ``tfr_relevant_from`` dates the TFR relevance (Federalimentare art. 73).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    monthly: TimeSeries
    role: str | None = None
    percentage_rate: Decimal | None = Field(default=None, ge=0, le=1)
    percentage_base_allowances: tuple[str, ...] = ()
    floor_level: str | None = None
    months_per_year: int | None = Field(default=None, ge=1)
    tfr_relevant: bool = True
    tfr_relevant_from: date | None = None
    contribution_relevant: bool = True
    apprenticeship_pct_relevant: bool = True
    part_time_proportionable: bool = True
    in_kind: bool = False
    replaced_by: Literal["provincial_element", "second_level_premium"] | None = None
    service_months_threshold: int | None = Field(default=None, ge=0)
    service_months_until: int | None = Field(default=None, ge=1)
    career_service: bool = False
    in_service_on: date | None = None
    individual: bool = False
    absorbed_by_individual_excess: bool = False
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_contribution_relevant(self) -> Self:
        if self.percentage_rate is None and (
            self.percentage_base_allowances or self.floor_level is not None
        ):
            msg = f"allowance {self.code}: percentage base needs a rate"
            raise ValueError(msg)
        if not self.contribution_relevant:
            msg = (
                f"allowance {self.code}: contribution_relevant false is not "
                "supported, the INPS base would keep it"
            )
            raise ValueError(msg)
        return self

    @property
    def apprenticeship_pct_declared(self) -> bool:
        """Whether the data states ``apprenticeship_pct_relevant``.

        ``False`` when the flag holds its default: whether the CCNL reduces
        the allowance for percentage apprentices was not sourced.
        """
        return "apprenticeship_pct_relevant" in self.model_fields_set
