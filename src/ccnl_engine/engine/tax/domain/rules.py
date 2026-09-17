"""Tax rule models for a single fiscal year."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.metadata import RulesetIdentity
from ccnl_engine.engine.primitives import Bracket, assert_ivs_le_total
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.provenance.domain.extraction import ExtractionTrace
from ccnl_engine.engine.provenance.domain.source import SourceDocument

#: A single IRPEF marginal tax bracket (Art. 11 TUIR).
IrpefBracket = Bracket

#: Contribution rate or per-hour amount: must be >= 0.
NonNegativeRate = Annotated[Decimal, Field(ge=Decimal(0))]

#: Monetary ceiling that, when present, must be strictly positive.
PositiveCeiling = Annotated[Decimal, Field(gt=Decimal(0))]


class DeductionBreakpoint(BaseModel):
    """A single breakpoint in a piecewise-linear deduction schedule.

    Reused for Art. 12 TUIR family deductions (spouse, children) whose
    schedules are tabulated as breakpoint lists in the tax data files.

    Note: Art. 13 TUIR work-income deduction uses statutory piecewise
    formulas in ``irpef.py`` and no longer stores breakpoints here.
    """

    model_config = ConfigDict(extra="forbid")

    income_up_to: Decimal | None
    deduction: Decimal
    provenance: RuleProvenance | None = None


class InpsRates(BaseModel):
    """Resolved (flat) INPS contribution rates for a sector and employer size.

    ``employer_rate_by_category`` overrides ``employer_rate`` for levels whose
    ``category`` matches (e.g. lower rates for *impiegati* in artigianato).

    ``employee_ivs_rate`` and ``employer_ivs_rate`` are the IVS portions of
    the respective total rates.  When ``ceiling`` is set and
    ``ivs_ceiling_applies`` is passed to the contribution engine, only these
    portions are capped at the massimale retributivo; the remainder is always
    applied to the full base.

    **Uniform-IVS invariant**: ``employer_ivs_rate`` is a single scalar that
    applies uniformly across all worker categories.  When a category-specific
    rate is active, the IVS component is still taken from ``employer_ivs_rate``
    and the category non-IVS residual is ``category_rate - employer_ivs_rate``.
    This invariant is enforced by ``InpsEmployerTier._check_ivs_rate``, which
    requires every category rate to be >= ``ivs_rate`` so the residual is
    non-negative.  A sector where the IVS rate genuinely varies by category
    would need a ``ivs_rate_by_category`` field.

    ``employee_additional_rate`` and ``employee_additional_threshold`` model
    the 1% IVS contribution charged to employees on the portion of annual
    earnings exceeding the first pensionable band (Art. 3-ter D.L. 384/1992).
    When set, the additional is applied on top of the ordinary rate; it is
    IVS and therefore subject to the massimale when ``ivs_ceiling_applies``
    is True.  Both fields are required together; presence of one without the
    other is rejected by the loader.
    """

    model_config = ConfigDict(extra="forbid")

    employee_rate: NonNegativeRate
    employee_ivs_rate: NonNegativeRate
    employer_rate: NonNegativeRate
    employer_ivs_rate: NonNegativeRate
    ceiling: PositiveCeiling | None
    employer_rate_by_category: dict[str, NonNegativeRate] = {}
    employee_additional_rate: NonNegativeRate | None = None
    employee_additional_threshold: Decimal | None = None
    provenance: RuleProvenance | None = None


class ApprenticeRates(BaseModel):
    """Resolved contribution rates for apprentices (L. 296/2006 art. 1 c. 773).

    Employer rates are already resolved for the employer's headcount: firms
    with at most ``small_firm_max_employees`` pay the reduced rates in the
    first two years, all others pay ``employer_rate_after`` throughout.

    ``employee_ivs_rate`` and ``employer_ivs_rate_*`` carry the IVS-only
    portions of the corresponding total rates.  For apprentice employees the
    full rate is IVS (NASpI is employer-only for apprentice contracts).  For
    employers the statutory IVS-only rate is 10 % for large firms and steps
    up from 1.5 % / 3 % for small firms; NASpI (1.31 %) and CIGS (0.30 %)
    are non-IVS and must not be capped.
    """

    model_config = ConfigDict(extra="forbid")

    employee_rate: NonNegativeRate
    employee_ivs_rate: NonNegativeRate
    employer_rate_months_0_11: NonNegativeRate
    employer_ivs_rate_months_0_11: NonNegativeRate
    employer_rate_months_12_23: NonNegativeRate
    employer_ivs_rate_months_12_23: NonNegativeRate
    employer_rate_after: NonNegativeRate
    employer_ivs_rate_after: NonNegativeRate
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_ivs_rates(self) -> Self:
        pairs: list[tuple[str, Decimal, str, Decimal]] = [
            (
                "employee_ivs_rate",
                self.employee_ivs_rate,
                "employee_rate",
                self.employee_rate,
            ),
            (
                "employer_ivs_rate_months_0_11",
                self.employer_ivs_rate_months_0_11,
                "employer_rate_months_0_11",
                self.employer_rate_months_0_11,
            ),
            (
                "employer_ivs_rate_months_12_23",
                self.employer_ivs_rate_months_12_23,
                "employer_rate_months_12_23",
                self.employer_rate_months_12_23,
            ),
            (
                "employer_ivs_rate_after",
                self.employer_ivs_rate_after,
                "employer_rate_after",
                self.employer_rate_after,
            ),
        ]
        for ivs_name, ivs_val, total_name, total_val in pairs:
            assert_ivs_le_total(ivs_name, ivs_val, total_name, total_val)
        return self


class InpsEmployerTier(BaseModel):
    """A single employer-rate tier keyed by maximum headcount.

    ``ivs_rate`` is the IVS (Invalidità, Vecchiaia, Superstiti) portion of
    ``rate``.  Only this portion is subject to the annual massimale retributivo
    (Art. 1 c. 18 L. 335/1995); the remainder (NASpI, CUAF, CIG, etc.) is
    always applied to the full contribution base.
    """

    model_config = ConfigDict(extra="forbid")

    max_employees: int | None
    rate: NonNegativeRate
    ivs_rate: NonNegativeRate
    rate_by_category: dict[str, NonNegativeRate] = {}
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_ivs_rate(self) -> Self:
        assert_ivs_le_total("ivs_rate", self.ivs_rate, "rate", self.rate)
        for cat, cat_rate in self.rate_by_category.items():
            if cat_rate < self.ivs_rate:
                msg = (
                    f"rate_by_category[{cat!r}] = {cat_rate} is below "
                    f"ivs_rate {self.ivs_rate}; non-IVS portion would be negative"
                )
                raise ValueError(msg)
        return self


class InpsEmployeeTier(BaseModel):
    """A single employee-rate tier keyed by maximum headcount.

    ``ivs_rate`` is the IVS portion of ``rate`` (subject to the massimale).
    For most private-sector employees this equals the full rate; the 0.30%
    CIGS employee share (added above certain headcount thresholds) is *not*
    IVS and must be excluded from ``ivs_rate``.
    """

    model_config = ConfigDict(extra="forbid")

    max_employees: int | None
    rate: NonNegativeRate
    ivs_rate: NonNegativeRate
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_ivs_rate(self) -> Self:
        assert_ivs_le_total("ivs_rate", self.ivs_rate, "rate", self.rate)
        return self


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


class InpsRawRates(BaseModel):
    """Raw INPS block from the tax JSON file, before tier resolution.

    ``employee_additional_rate`` and ``employee_additional_threshold`` are
    optional; both must be present together (validated by the loader).  When
    absent, the additional contribution is not modelled for this sector.
    """

    model_config = ConfigDict(extra="forbid")

    employee_tiers: list[InpsEmployeeTier]
    employer_tiers: list[InpsEmployerTier]
    ceiling: PositiveCeiling | None
    employee_additional_rate: NonNegativeRate | None = None
    employee_additional_threshold: Decimal | None = None
    provenance: RuleProvenance | None = None


class ApprenticeRawRates(BaseModel):
    """Raw apprentice block from the tax JSON file, before headcount resolution."""

    model_config = ConfigDict(extra="forbid")

    employee_rate: NonNegativeRate
    employee_ivs_rate: NonNegativeRate
    employer_rate: NonNegativeRate
    employer_ivs_rate: NonNegativeRate
    small_firm_max_employees: int = Field(ge=0)
    small_firm_employer_rate_months_0_11: NonNegativeRate
    small_firm_employer_ivs_rate_months_0_11: NonNegativeRate
    small_firm_employer_rate_months_12_23: NonNegativeRate
    small_firm_employer_ivs_rate_months_12_23: NonNegativeRate
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_ivs_rates(self) -> Self:
        pairs: list[tuple[str, Decimal, str, Decimal]] = [
            (
                "employee_ivs_rate",
                self.employee_ivs_rate,
                "employee_rate",
                self.employee_rate,
            ),
            (
                "employer_ivs_rate",
                self.employer_ivs_rate,
                "employer_rate",
                self.employer_rate,
            ),
            (
                "small_firm_employer_ivs_rate_months_0_11",
                self.small_firm_employer_ivs_rate_months_0_11,
                "small_firm_employer_rate_months_0_11",
                self.small_firm_employer_rate_months_0_11,
            ),
            (
                "small_firm_employer_ivs_rate_months_12_23",
                self.small_firm_employer_ivs_rate_months_12_23,
                "small_firm_employer_rate_months_12_23",
                self.small_firm_employer_rate_months_12_23,
            ),
        ]
        for ivs_name, ivs_val, total_name, total_val in pairs:
            assert_ivs_le_total(ivs_name, ivs_val, total_name, total_val)
        return self


class TfrRules(BaseModel):
    """TFR (severance pay) accrual rules (Art. 2120 c.c.)."""

    model_config = ConfigDict(extra="forbid")

    accrual_divisor: Decimal = Field(gt=Decimal(0))
    provenance: RuleProvenance | None = None


class TrattamentoIntegrativoRules(BaseModel):
    """Parameters for the trattamento integrativo (Art. 1 D.L. 3/2020).

    The bonus is computed on gross annual income (RAL) as follows:

    - RAL <= ``threshold_mid``: ``max_amount`` if IRPEF lorda > detrazioni lavoro,
      else 0.
    - ``threshold_mid`` < RAL <= ``threshold_upper``:
      max(0, ``max_amount`` * (``threshold_upper`` - RAL)
      / (``threshold_upper`` - ``threshold_mid``)).
    - RAL > ``threshold_upper``: 0.
    """

    model_config = ConfigDict(extra="forbid")

    threshold_mid: Decimal
    threshold_upper: Decimal
    max_amount: Decimal
    provenance: RuleProvenance | None = None


class UlterioreDetrazioneRules(BaseModel):
    """Ulteriore detrazione del lavoro dipendente (Art. 1 c. 6 L. 207/2024).

    Three zones by reddito complessivo (``rc``):

    - ``rc <= threshold_low``: zero.
    - ``threshold_low < rc <= threshold_mid``: ``max_amount`` (flat).
    - ``threshold_mid < rc <= threshold_high``:
      ``max_amount * (threshold_high - rc) / (threshold_high - threshold_mid)``
      (tapering to zero at the upper boundary).
    - ``rc > threshold_high``: zero.

    Pro-rating to the actual work period is the caller's responsibility.
    """

    model_config = ConfigDict(extra="forbid")

    threshold_low: Decimal
    threshold_mid: Decimal
    threshold_high: Decimal
    max_amount: Decimal
    provenance: RuleProvenance | None = None


class SommaEsenteBand(BaseModel):
    """One income band for the somma esente schedule.

    The ``rate`` applies to the full reddito complessivo (not a marginal
    slice) when the income falls within this band (i.e. does not exceed
    ``up_to``).  Bands are ordered ascending by ``up_to``.
    """

    model_config = ConfigDict(extra="forbid")

    up_to: Decimal
    rate: Decimal


class SommaEsenteRules(BaseModel):
    """Somma esente L. 207/2024 for low-income workers.

    A flat-rate bonus added to net pay when reddito complessivo does not
    exceed the last band's ``up_to`` threshold.  The applicable rate is
    the rate of the first band whose ``up_to`` is >= reddito complessivo;
    it is applied to the full reddito complessivo (not just the marginal
    slice).

    Band cut points in the knowledge bundle are unverified reconstructions
    from available examples and are flagged in the JSON ``notes`` array.
    """

    model_config = ConfigDict(extra="forbid")

    bands: list[SommaEsenteBand]
    provenance: RuleProvenance | None = None


class SterilizzazioneDetrazioniRules(BaseModel):
    """Sterilizzazione detrazioni for high-income earners.

    Per Art. 1 c. 3-4 L. 199/2025 (Legge di Bilancio 2026): for
    reddito complessivo exceeding ``threshold``, the Art. 15 TUIR
    oneri detraibili al 19 % (lett. a, b, d, e; not lett. c spese
    sanitarie) is reduced by ``reduction`` EUR. The reduction is the
    exact clawback of the tax benefit from the 35% to 33% IRPEF
    bracket change on the EUR 28 000-50 000 slice:
    2% x EUR 22 000 = EUR 440.
    """

    model_config = ConfigDict(extra="forbid")

    threshold: Decimal
    reduction: Decimal
    provenance: RuleProvenance | None = None


class YearRulesRaw(BaseModel):
    """Full deserialization model for a tax/data/<year>-<sector>.json file.

    Either ``inps`` + ``apprentice`` (standard percentage model) or
    ``domestic_contributions`` (flat per-hour domestic model) must be present.
    Both combinations are validated by ``_check_contribution_model``.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    sector: TaxSector
    ruleset: RulesetIdentity | None = None
    irpef_brackets: list[IrpefBracket]
    fixed_term_additional_rate: Decimal
    inps: InpsRawRates | None = None
    apprentice: ApprenticeRawRates | None = None
    domestic_contributions: DomesticInpsRates | None = None
    tfr: TfrRules
    trattamento_integrativo: TrattamentoIntegrativoRules | None = None
    ulteriore_detrazione: UlterioreDetrazioneRules | None = None
    somma_esente: SommaEsenteRules | None = None
    sterilizzazione_detrazioni: SterilizzazioneDetrazioniRules | None = None
    notes: list[str] = Field(default_factory=list)
    sources: list[SourceDocument] = Field(default_factory=list)
    extraction: ExtractionTrace | None = None
    inps_sources: list[SourceDocument] = Field(default_factory=list)
    inps_extraction: ExtractionTrace | None = None

    @model_validator(mode="after")
    def _check_contribution_model(self) -> Self:
        has_inps = self.inps is not None
        has_apprentice = self.apprentice is not None
        has_domestic = self.domestic_contributions is not None
        if has_inps != has_apprentice:
            msg = (
                "'inps' and 'apprentice' must both be present "
                "(standard model) or both absent; "
                "found one without the other"
            )
            raise ValueError(msg)
        has_standard = has_inps
        if not has_standard and not has_domestic:
            msg = (
                "tax file must contain either 'inps' + 'apprentice' "
                "(standard model) or 'domestic_contributions' (domestic model)"
            )
            raise ValueError(msg)
        if has_standard and has_domestic:
            msg = (
                "tax file must not mix 'inps'+'apprentice' (standard model) "
                "with 'domestic_contributions' (domestic model): "
                "the two contribution models are mutually exclusive"
            )
            raise ValueError(msg)
        return self


class YearRules(BaseModel):
    """All statutory tax and contribution parameters for a single fiscal year.

    ``inps`` and ``apprentice`` are set for standard sectors; ``None`` for
    domestic sectors where ``domestic_contributions`` carries the flat-rate
    table instead.  Exactly one contribution model is present (enforced by
    the loader, which mirrors ``YearRulesRaw._check_contribution_model``).
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    ruleset: RulesetIdentity | None = None
    inps_ruleset: RulesetIdentity | None = None
    irpef_brackets: list[IrpefBracket]
    fixed_term_additional_rate: Decimal
    inps: InpsRates | None = None
    apprentice: ApprenticeRates | None = None
    domestic_contributions: DomesticInpsRates | None = None
    tfr: TfrRules
    trattamento_integrativo: TrattamentoIntegrativoRules | None = None
    ulteriore_detrazione: UlterioreDetrazioneRules | None = None
    somma_esente: SommaEsenteRules | None = None
    sterilizzazione_detrazioni: SterilizzazioneDetrazioniRules | None = None
    notes: list[str] = Field(default_factory=list)
    sources: list[SourceDocument] = Field(default_factory=list)
    extraction: ExtractionTrace | None = None
    inps_sources: list[SourceDocument] = Field(default_factory=list)
    inps_extraction: ExtractionTrace | None = None

    @model_validator(mode="after")
    def _validate_sequences(self) -> Self:
        self._check_irpef_brackets()
        self._check_contribution_model()
        return self

    def _check_contribution_model(self) -> None:
        has_inps = self.inps is not None
        has_apprentice = self.apprentice is not None
        has_domestic = self.domestic_contributions is not None
        if has_inps != has_apprentice:
            msg = (
                "'inps' and 'apprentice' must both be present "
                "(standard model) or both absent; "
                "found one without the other"
            )
            raise ValueError(msg)
        has_standard = has_inps
        if not has_standard and not has_domestic:
            msg = (
                "YearRules must contain either 'inps' + 'apprentice' "
                "(standard model) or 'domestic_contributions' (domestic model)"
            )
            raise ValueError(msg)
        if has_standard and has_domestic:
            msg = (
                "YearRules must not mix standard model ('inps'+'apprentice') "
                "with 'domestic_contributions': mutually exclusive"
            )
            raise ValueError(msg)

    def _check_irpef_brackets(self) -> None:
        brackets = self.irpef_brackets
        if not brackets:
            msg = "irpef_brackets must not be empty"
            raise ValueError(msg)
        for i, b in enumerate(brackets[:-1]):
            if b.up_to is None:
                msg = (
                    f"only the last irpef_bracket may have up_to=None "
                    f"(bracket {i} is not the last)"
                )
                raise ValueError(msg)
            next_b = brackets[i + 1]
            if next_b.up_to is not None and next_b.up_to <= b.up_to:
                msg = (
                    f"irpef_brackets must have strictly ascending up_to: "
                    f"bracket {i} up_to={b.up_to} >= "
                    f"bracket {i + 1} up_to={next_b.up_to}"
                )
                raise ValueError(msg)
        if brackets[-1].up_to is not None:
            msg = (
                "last irpef_bracket must be unbounded (up_to=None), "
                f"got up_to={brackets[-1].up_to}"
            )
            raise ValueError(msg)
