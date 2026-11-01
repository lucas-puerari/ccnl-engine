"""Seniority increment models for CCNL contracts."""

from collections.abc import Mapping
from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.types import FrozenDict


class PromotionRepricing(BaseModel):
    """When the increments matured before a promotion take the new amounts.

    Attributes:
        at_next_increment: ``True`` when the CCNL reprices them at the new
            level only when the next increment matures (Turismo art. 158
            c. 6, FIPE art. 182 c. 5); ``False`` when they take the new
            amounts from the promotion (Federmeccanica art. 6: "il cui valore
            sarà ragguagliato agli importi previsti per la categoria di
            arrivo").
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    at_next_increment: bool
    provenance: RuleProvenance


class SeniorityTier(BaseModel):
    """One cadence tier in a multi-tier seniority ladder (*scatti di anzianità*).

    When a contract uses a single cadence throughout (e.g. 10 biennial scatti)
    use the flat ``cadence_months``/``maximum_count``/``amount_by_level`` fields
    on :class:`SeniorityIncrements` instead.

    When the cadence changes after a certain number of increments (e.g. 6
    biennial, then 1 dodecennial, then 3 quadrennial), populate
    ``SeniorityIncrements.tiers`` and leave ``amount_by_level`` empty.
    Tiers are consumed in order: the engine exhausts tier 1's full capacity
    (``cadence_months * maximum_count`` service months) before advancing to tier 2.

    ``amount_by_level`` is a read-only mapping; it is frozen after construction.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    cadence_months: int = Field(gt=0)
    maximum_count: int = Field(gt=0)
    amount_by_level: Mapping[str, TimeSeries]
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _freeze_dicts(self) -> Self:
        object.__setattr__(  # noqa: PLC2801
            self, "amount_by_level", FrozenDict(self.amount_by_level)
        )
        return self


class ApprenticeCohort(BaseModel):
    """The apprentice increment kept by the apprentices of an earlier rule.

    Tessile moda artigianato, renewal of 16 July 2024: "Agli apprendisti in
    forza alla data di sottoscrizione del presente accordo di rinnovo
    continua a trovare applicazione la disciplina degli aumenti periodici di
    anzianità vigente alla data di assunzione".

    Attributes:
        in_service_on: Last hire date of the cohort: the day of signature.
        amount: Increment of the cohort, in place of
            :attr:`SeniorityIncrements.apprentice_amount`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    in_service_on: date
    amount: TimeSeries


class SeniorityIncrements(BaseModel):
    """Seniority increment (*scatti di anzianità*) rules for a CCNL.

    **Flat mode** (default): set ``cadence_months``, ``maximum_count``, and
    ``amount_by_level``. All increments share the same cadence and per-scatto
    amount. ``first_cadence_months`` and the ``*_by_level`` overrides refine
    the flat behaviour per level.

    **Tiered mode**: set ``tiers`` to a non-empty list of
    :class:`SeniorityTier` entries and leave ``amount_by_level`` empty.
    ``cadence_months`` and ``maximum_count`` remain required for schema
    compatibility but are ignored at runtime (the tier definitions take
    precedence). ``first_cadence_months`` and ``first_cadence_months_by_level``
    are also ignored in tiered mode; the first tier's ``cadence_months`` acts
    as the first cadence.

    ``apprentice_amount`` is the increment (if any) accrued during an
    apprenticeship, replacing the level amount; ``apprentice_cohort`` the
    one of the apprentices hired by its day. Workers of an
    ``excluded_categories`` category accrue no increment (e.g. operai edili,
    who receive APE through the Cassa Edile instead).
    ``excluded_from_extra_months`` lists the extra months the increments do
    not enter (Pubblici Esercizi FIPE art. 184: the quattordicesima is due
    "esclusi [...] gli scatti di anzianità maturati").
    ``on_promotion`` states when the increments matured before a promotion
    take the amounts of the new level; ``None`` reprices them at once.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    cadence_months: int = Field(gt=0)
    maximum_count: int = Field(ge=0)
    amount_by_level: Mapping[str, TimeSeries]
    tiers: tuple[SeniorityTier, ...] = Field(default=())
    first_cadence_months: int | None = Field(default=None, gt=0)
    first_cadence_months_by_level: Mapping[str, int] = Field(default_factory=dict)
    maximum_count_by_level: Mapping[str, int] = Field(default_factory=dict)
    apprentice_amount: TimeSeries | None = None
    apprentice_cohort: ApprenticeCohort | None = None
    excluded_categories: tuple[WorkerCategory, ...] = Field(default=())
    excluded_from_extra_months: tuple[ExtraMonthKind, ...] = Field(default=())
    amount_by_level_by_category: Mapping[WorkerCategory, Mapping[str, TimeSeries]] = (
        Field(default_factory=dict)
    )
    maximum_count_by_category: Mapping[WorkerCategory, int] = Field(
        default_factory=dict
    )
    first_cadence_months_by_category: Mapping[WorkerCategory, int] = Field(
        default_factory=dict
    )
    on_promotion: PromotionRepricing | None = None
    provenance: RuleProvenance | None = None

    def requires_category(self, level_code: str) -> bool:
        """Return whether increments for ``level_code`` exist only per category.

        True when some category carries an amount for the level and there is
        no category-independent amount to fall back on: without the worker
        category the increment cannot be priced.

        Returns:
            Whether a worker category is needed to resolve the increment.
        """
        return level_code not in self.amount_by_level and any(
            level_code in amounts
            for amounts in self.amount_by_level_by_category.values()
        )

    @model_validator(mode="after")
    def _check_cadence(self) -> Self:
        if self.tiers:
            self._check_tiered_constraints()
        else:
            self._check_flat_constraints()
        return self

    def _check_tiered_constraints(self) -> None:
        """Validate invariants that apply only when ``tiers`` is non-empty.

        Raises:
            ValueError: If flat-mode fields are set alongside tiers, or if
                ``maximum_count`` does not equal the sum of tier capacities.
        """
        if self.amount_by_level:
            msg = (
                "seniority_increments.tiers and amount_by_level are mutually "
                "exclusive: use tiers for multi-tier ladders, amount_by_level "
                "for uniform-cadence contracts"
            )
            raise ValueError(msg)
        flat_only: dict[str, object] = {
            "first_cadence_months": self.first_cadence_months,
            "first_cadence_months_by_level": self.first_cadence_months_by_level,
            "first_cadence_months_by_category": self.first_cadence_months_by_category,
            "maximum_count_by_level": self.maximum_count_by_level,
            "maximum_count_by_category": self.maximum_count_by_category,
            "amount_by_level_by_category": self.amount_by_level_by_category,
        }
        set_fields = [k for k, v in flat_only.items() if v]
        if set_fields:
            joined = ", ".join(set_fields)
            msg = (
                "seniority_increments.tiers is set; the following flat-mode "
                f"fields are not allowed in tiered mode: {joined}"
            )
            raise ValueError(msg)
        tier_sum = sum(t.maximum_count for t in self.tiers)
        if self.maximum_count != tier_sum:
            msg = (
                f"seniority_increments.maximum_count ({self.maximum_count}) "
                f"must equal the sum of tier maximum_count values ({tier_sum})"
            )
            raise ValueError(msg)

    def _check_flat_constraints(self) -> None:
        """Validate invariants that apply when ``tiers`` is empty (flat mode).

        Raises:
            ValueError: If ``maximum_count > 0`` but no amounts are defined,
                or if a first-cadence override is below ``cadence_months``,
                or if a per-level/per-category maximum count is negative.
        """
        if (
            self.maximum_count > 0
            and not self.amount_by_level
            and not (self.amount_by_level_by_category)
        ):
            msg = (
                "seniority_increments.maximum_count > 0 but neither "
                "amount_by_level nor amount_by_level_by_category is populated; "
                "add amounts or set maximum_count to 0 to disable scatti"
            )
            raise ValueError(msg)
        candidates = [("first_cadence_months", self.first_cadence_months)]
        candidates += [
            (f"first_cadence_months_by_level[{code!r}]", months)
            for code, months in self.first_cadence_months_by_level.items()
        ]
        candidates += [
            (f"first_cadence_months_by_category[{cat.value!r}]", months)
            for cat, months in self.first_cadence_months_by_category.items()
        ]
        for name, months in candidates:
            if months is not None and months < self.cadence_months:
                msg = (
                    f"{name} ({months}) must be >= cadence_months "
                    f"({self.cadence_months})"
                )
                raise ValueError(msg)
        for code, count in self.maximum_count_by_level.items():
            if count < 0:
                msg = f"maximum_count_by_level[{code!r}] must be >= 0, got {count}"
                raise ValueError(msg)
        for cat, count in self.maximum_count_by_category.items():
            if count < 0:
                msg = (
                    f"maximum_count_by_category[{cat.value!r}] must be >= 0, "
                    f"got {count}"
                )
                raise ValueError(msg)

    @model_validator(mode="after")
    def _freeze_dicts(self) -> Self:
        object.__setattr__(  # noqa: PLC2801
            self, "amount_by_level", FrozenDict(self.amount_by_level)
        )
        object.__setattr__(  # noqa: PLC2801
            self,
            "first_cadence_months_by_level",
            FrozenDict(self.first_cadence_months_by_level),
        )
        object.__setattr__(  # noqa: PLC2801
            self,
            "maximum_count_by_level",
            FrozenDict(self.maximum_count_by_level),
        )
        object.__setattr__(  # noqa: PLC2801
            self,
            "amount_by_level_by_category",
            FrozenDict({
                cat: FrozenDict(inner)
                for cat, inner in self.amount_by_level_by_category.items()
            }),
        )
        object.__setattr__(  # noqa: PLC2801
            self,
            "maximum_count_by_category",
            FrozenDict(self.maximum_count_by_category),
        )
        object.__setattr__(  # noqa: PLC2801
            self,
            "first_cadence_months_by_category",
            FrozenDict(self.first_cadence_months_by_category),
        )
        return self
