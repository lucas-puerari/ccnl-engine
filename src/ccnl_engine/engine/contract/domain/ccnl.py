"""CCNL domain models."""

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipTrack,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.engine.contract.domain.validity import TimeSeries
from ccnl_engine.engine.metadata import RulesetIdentity
from ccnl_engine.engine.metadata.domain.rules import VerificationStatus
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.provenance.domain.extraction import ExtractionTrace
from ccnl_engine.engine.provenance.domain.source import SourceDocument, SourceKind


class CoverageStatus(StrEnum):
    """Implementation status for a CCNL coverage layer."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    OUT_OF_SCOPE = "out_of_scope"
    NOT_IMPLEMENTED = "not_implemented"


class L3Feature(StrEnum):
    """Enumeration of Layer 3 payroll features."""

    OVERTIME = "overtime"
    NIGHT_WORK = "night_work"
    HOLIDAY_WORK = "holiday_work"
    ABSENCE = "absence"
    SICKNESS = "sickness"
    LEAVE = "leave"
    BONUS = "bonus"
    BENEFITS = "benefits"
    WELFARE = "welfare"
    FRINGE_BENEFITS = "fringe_benefits"
    FAMILY_DEDUCTIONS = "family_deductions"
    COMPANY_AGREEMENT = "company_agreement"
    TERRITORIAL_AGREEMENT = "territorial_agreement"


class TimeSupplementKind(StrEnum):
    """How the overtime band rate is applied."""

    PERCENTAGE = "percentage"
    INDENNITA_PER_SHIFT = "indennita_per_shift"
    INDENNITA_PER_HOUR = "indennita_per_hour"


class WorkKind(StrEnum):
    """Kind of working time for overtime band matching."""

    WEEKDAY = "weekday"
    NIGHT = "night"
    HOLIDAY = "holiday"
    SUPPLEMENTARE = "supplementare"


LevelCategory = Literal["operaio", "impiegato", "quadro", "dirigente"]


class NoteKind(StrEnum):
    """Semantic category of a coverage note."""

    SOURCE = "source"
    INFO = "info"
    SIMPLIFICATION = "simplification"
    MISSING = "missing"


class CoverageNote(BaseModel):
    """A structured note attached to a CCNL coverage block.

    Replaces the legacy string-prefix convention (``SIMPLIFICATION: …``,
    ``MISSING: …``, etc.) with a typed ``kind`` field.
    """

    model_config = ConfigDict(extra="forbid")

    kind: NoteKind
    text: str


class TaxSector(StrEnum):
    """INPS sector classification used to select the contribution-rate file."""

    TERZIARIO = "terziario"
    INDUSTRIA = "industria"
    EDILIZIA = "edilizia"
    CREDITO = "credito"
    ARTIGIANATO = "artigianato"
    PUBBLICA_AMMINISTRAZIONE = "pubblica-amministrazione"
    LAVORO_DOMESTICO = "lavoro-domestico"
    AGRICOLTURA = "agricoltura"


class OvertimeBand(BaseModel):
    """One overtime/supplement band: a rate applied to a specific work kind.

    ``kind`` controls how ``rate`` is interpreted:

    * ``percentage``: supplement = rate * full-time hourly base * hours.
    * ``indennita_per_hour``: supplement = rate * hours (fixed EUR/hour).
    * ``indennita_per_shift``: supplement = rate * shift count (fixed EUR/shift).

    ``applies_to_kinds`` lists the :class:`WorkKind` values this band covers.
    ``hour_threshold_per_day`` / ``hour_threshold_per_week`` optionally restrict
    the band to hours *beyond* that threshold (straordinario, not supplementare).
    """

    model_config = ConfigDict(extra="forbid")

    code: str
    description: str
    kind: TimeSupplementKind
    rate: "TimeSeries"
    hour_threshold_per_day: int | None = None
    hour_threshold_per_week: int | None = None
    applies_to_kinds: list[WorkKind]
    provenance: "RuleProvenance | None" = None


class TimeSupplements(BaseModel):
    """Layer 3 time-supplement rules (overtime, night work, holiday work).

    ``hourly_base_method`` controls which base is used:

    * ``minimo_tabellare``: the CCNL table minimum only (no allowances).
    * ``gross_incl_allowances``: the full gross including fixed allowances.

    ``overtime_bands`` is an ordered list of :class:`OvertimeBand` entries.
    All applicable bands accumulate (no "first match wins" truncation) unless
    a CCNL-specific note says otherwise.
    """

    model_config = ConfigDict(extra="forbid")

    hourly_base_method: Literal["minimo_tabellare", "gross_incl_allowances"] = (
        "minimo_tabellare"
    )
    overtime_bands: list[OvertimeBand] = []


class DailyDivisorMethod(StrEnum):
    """How the daily rate is derived for absence deductions.

    * ``by_26``: ``gross_monthly / 26`` — the standard industria divisor.
    * ``by_hourly``: ``hourly_rate * daily_hours`` — for contracts that
      specify a daily working-hours figure.
    """

    BY_26 = "by_26"
    BY_HOURLY = "by_hourly"


class AbsenceRules(BaseModel):
    """Layer 3 rules for unpaid-absence (assenza non retribuita) deductions.

    ``daily_divisor_method`` controls how the daily rate is computed:

    * ``by_26``: ``gross_monthly / 26`` (standard industria divisore).
    * ``by_hourly``: ``hourly_rate * daily_hours`` — ``daily_hours`` must
      be provided.

    ``provenance`` links this rule to its source CCNL article.
    """

    model_config = ConfigDict(extra="forbid")

    daily_divisor_method: DailyDivisorMethod = DailyDivisorMethod.BY_26
    daily_hours: Decimal | None = None
    provenance: "RuleProvenance | None" = None


class CCNLLayer3(BaseModel):
    """Container for Layer 3 rules attached to a CCNL data file."""

    model_config = ConfigDict(extra="forbid")

    time_supplements: TimeSupplements | None = None
    absence_rules: AbsenceRules | None = None


class Allowance(BaseModel):
    """A named fixed monthly allowance attached to a CCNL level.

    ``role`` restricts the allowance to workers holding that role (``None``
    means every worker at the level). ``months_per_year`` overrides the
    contract-wide ``additional_months`` for this allowance only. The three
    relevance flags exclude the allowance from the TFR base, the contribution
    base, or the apprenticeship-percentage base respectively.
    ``apprenticeship_pct_relevant=False`` means the allowance is paid at full
    value even for percentage-based apprentices (e.g. EDR per Art. 3 L.
    297/1982, which Italian CCNL commonly exempt from apprenticeship
    percentage reductions).

    ``service_months_threshold`` makes the allowance conditional: it is
    included only when ``Scenario.seniority_months`` is provided and is at
    least this many months. When ``Scenario.seniority_count`` is used instead
    of ``seniority_months``, threshold-gated allowances are excluded (the
    engine cannot gate on service time without knowing service time).
    """

    model_config = ConfigDict(extra="forbid")

    code: str
    description: str
    monthly: TimeSeries
    role: str | None = None
    months_per_year: int | None = Field(default=None, ge=1)
    tfr_relevant: bool = True
    contribution_relevant: bool = True
    apprenticeship_pct_relevant: bool = True
    service_months_threshold: int | None = Field(default=None, ge=0)
    provenance: RuleProvenance | None = None


class SupplementaryAllowance(BaseModel):
    """Caller-supplied allowance from a second-level (territorial or company) agreement.

    Unlike :class:`Allowance` — which is embedded in a CCNL data file and
    carries a time-series — this model holds a plain already-resolved monthly
    amount and is passed at runtime via ``Scenario.second_level_allowances``.

    ``months_per_year`` overrides the contract-wide ``additional_months`` for
    the annualisation of this item only (e.g. a prize paid once a year uses
    ``months_per_year=1``).  The three relevance flags mirror those on
    :class:`Allowance`:

    * ``contribution_relevant=False``: exclude from the INPS contribution base.
    * ``tfr_relevant=False``: exclude from the TFR accrual base.
    * ``apprenticeship_pct_relevant=False``: pay at full part-time value even
      for percentage-based apprentices (the apprenticeship percentage does not
      apply).

    The amount is always scaled by ``Scenario.part_time_pct``; the
    ``apprenticeship_pct_relevant`` flag further controls whether the
    apprenticeship percentage is applied on top of that.
    """

    model_config = ConfigDict(extra="forbid")

    code: str
    description: str
    monthly: Decimal = Field(ge=Decimal(0))
    months_per_year: int | None = Field(default=None, ge=1)
    tfr_relevant: bool = True
    contribution_relevant: bool = True
    apprenticeship_pct_relevant: bool = True


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
    """

    model_config = ConfigDict(extra="forbid")

    cadence_months: int = Field(gt=0)
    maximum_count: int = Field(gt=0)
    amount_by_level: dict[str, TimeSeries]
    provenance: RuleProvenance | None = None


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
    apprenticeship, replacing the level amount. Workers of an
    ``excluded_categories`` category accrue no increment (e.g. operai edili,
    who receive APE through the Cassa Edile instead).
    """

    model_config = ConfigDict(extra="forbid")

    cadence_months: int = Field(gt=0)
    maximum_count: int = Field(ge=0)
    amount_by_level: dict[str, TimeSeries]
    tiers: list[SeniorityTier] = []
    first_cadence_months: int | None = Field(default=None, gt=0)
    first_cadence_months_by_level: dict[str, int] = {}
    maximum_count_by_level: dict[str, int] = {}
    apprentice_amount: TimeSeries | None = None
    excluded_categories: list[LevelCategory] = []
    amount_by_level_by_category: dict[LevelCategory, dict[str, TimeSeries]] = {}
    maximum_count_by_category: dict[LevelCategory, int] = {}
    first_cadence_months_by_category: dict[LevelCategory, int] = {}
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_cadence(self) -> Self:
        if self.tiers:
            if self.amount_by_level:
                msg = (
                    "seniority_increments.tiers and amount_by_level are mutually "
                    "exclusive: use tiers for multi-tier ladders, amount_by_level "
                    "for uniform-cadence contracts"
                )
                raise ValueError(msg)
            return self
        candidates = [("first_cadence_months", self.first_cadence_months)]
        candidates += [
            (f"first_cadence_months_by_level[{code!r}]", months)
            for code, months in self.first_cadence_months_by_level.items()
        ]
        candidates += [
            (f"first_cadence_months_by_category[{cat!r}]", months)
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
                msg = f"maximum_count_by_category[{cat!r}] must be >= 0, got {count}"
                raise ValueError(msg)
        return self


class EmployerFund(BaseModel):
    """An employer-side contribution to a contractual fund (e.g. Cassa Edile).

    ``rate`` is a fraction of the **INPS contribution base** (gross minus
    contribution-excluded allowances) as computed by the engine.  This is the
    same base used for INPS social-security contributions.  Note that some
    sector funds (notably Cassa Edile) are conventionally assessed on a
    different base (*imponibile Cassa Edile*); if the fund's official rate is
    expressed on that base, it must be adjusted to the INPS base before being
    stored here.  ``applies_to_categories`` restricts the fund to levels of the
    given categories (``None`` = all).
    """

    model_config = ConfigDict(extra="forbid")

    code: str
    description: str
    rate: TimeSeries
    applies_to_categories: list[LevelCategory] | None = None
    provenance: RuleProvenance | None = None


class CCNLParameters(BaseModel):
    """Contract-wide parameters."""

    model_config = ConfigDict(extra="forbid")

    hourly_divisor: TimeSeries
    additional_months: TimeSeries
    seniority_increments: SeniorityIncrements
    employer_funds: list[EmployerFund] = []


class Level(BaseModel):
    """A single classification level (*livello di inquadramento*).

    Attributes:
        code: Short alphanumeric code identifying the level within the CCNL
            (e.g. ``"D3"``, ``"A1"``). Used in ``Scenario.level_code``.
        order: Numeric ranking from lowest to highest seniority/pay (1 = lowest).
            Used by ``CCNL.level_by_order``.
        description: Human-readable name of the classification level.
        base_salary: Time-series of monthly base salaries for this level.
        fixed_allowances: List of fixed monthly allowances attached to the
            level (e.g. EDR, contingenza). May be empty.
        category: Worker category for this level. ``None`` when the level
            hosts multiple categories and the category must be passed via
            ``Scenario.category``.
    """

    model_config = ConfigDict(extra="forbid")

    code: str
    order: int
    description: str
    base_salary: TimeSeries
    fixed_allowances: list[Allowance] = []
    category: LevelCategory | None = None
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_salary_non_decreasing(self) -> Self:
        periods = self.base_salary.periods
        for i in range(len(periods) - 1):
            if periods[i + 1].value < periods[i].value:
                msg = (
                    f"base_salary must be non-decreasing over time: "
                    f"period {i} value {periods[i].value} > "
                    f"period {i + 1} value {periods[i + 1].value}"
                )
                raise ValueError(msg)
        return self


class CCNLCoverage(BaseModel):
    """Declares implementation and confidence status for a CCNL data file.

    Two orthogonal axes:

    * **Coverage** (``layer_1`` / ``layer_2`` / ``layer_3``): what the engine
      implements for this contract — ``implemented``, ``partial``, or
      ``out_of_scope``.

      - L1 — Gross: base salary, seniority, fixed allowances, additional
        months, hourly rate.
      - L2 — Net: INPS contributions, TFR, IRPEF, regional/municipal surtax.
      - L3 — Extended: overtime, sick/injury leave, performance bonuses,
        welfare/benefits. Defaults to ``not_implemented``.

    * **Verification** (``verification_status``): how confident we are in the
      data behind that implementation — verified, unverified, or needs review.

    ``layer_3`` is the scalar summary status (for backward compat with the
    coverage matrix). ``layer_3_features`` is the authoritative per-feature
    dict; it drives the computed L3 rollup and the per-feature coverage table.

    A ``missing`` note documents data the engine supports but the file lacks,
    and is only allowed while at least one of layer_1 / layer_2 is ``partial``
    or any layer_3 feature is ``partial``.
    """

    model_config = ConfigDict(extra="forbid")

    layer_1: CoverageStatus
    layer_2: CoverageStatus
    layer_3: CoverageStatus = CoverageStatus.NOT_IMPLEMENTED
    layer_3_features: dict[L3Feature, CoverageStatus] = {}
    notes: list[CoverageNote]
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED

    @model_validator(mode="after")
    def _check_notes(self) -> Self:
        has_missing = any(n.kind == NoteKind.MISSING for n in self.notes)
        any_l3_partial = any(
            v == CoverageStatus.PARTIAL for v in self.layer_3_features.values()
        )
        if (
            has_missing
            and "partial" not in {self.layer_1, self.layer_2}
            and not any_l3_partial
        ):
            msg = (
                "coverage has 'missing' notes but neither layer_1 nor layer_2 "
                "is 'partial' and no layer_3 feature is 'partial'"
            )
            raise ValueError(msg)
        return self


class CCNLValidity(BaseModel):
    """Contractual validity window of the modelled agreement."""

    model_config = ConfigDict(extra="forbid")

    valid_from: date
    valid_until: date | None = None


class CCNLMeta(BaseModel):
    """Identifying metadata for a CCNL.

    Attributes:
        ccnl_id: Unique slug for the contract
            (e.g. ``"metalmeccanico-federmeccanica"``). Used as
            ``PayrollResult.ccnl_id``.
        name: Full name of the collective agreement.
        cnel_code: CNEL registry code for the agreement.
        sector: Human-readable industry sector (e.g. ``"Industria metalmeccanica"``).
        tax_sector: INPS sector classification used to select the contribution-rate
            file. Pass this to ``load_year_rules``.
        signatories: List of employer associations and unions that signed the agreement.
        sources: Primary source references (official gazette, CNEL,
            association websites) as :class:`SourceDocument` objects.
        extraction: Metadata about how the data file was produced.
        agreement_date: Date of the most recent renewal agreement, ISO 8601 string.
            ``None`` if not yet modelled.
        validity: Contractual validity window. ``None`` if not specified.
        withholding_exempt: ``True`` for sectors where the employer is not a
            *sostituto d'imposta* for IRPEF (e.g. lavoro domestico, exempt under
            Art. 4 D.P.R. 600/1973). When ``True``, the engine still computes IRPEF
            figures but sets ``irpef_net`` to zero and marks
            ``PayrollResult.employer_withholds_irpef`` as ``False``.
        workers_estimate: Approximate number of workers covered by this agreement,
            as a human-readable string (e.g. ``"~800k"``). Based on CNEL and INPS
            estimates. Empty string when unknown.
    """

    model_config = ConfigDict(extra="forbid")

    ccnl_id: str
    name: str
    cnel_code: str
    sector: str
    tax_sector: TaxSector
    signatories: list[str]
    sources: list[SourceDocument]
    extraction: ExtractionTrace
    agreement_date: str | None = None
    validity: CCNLValidity | None = None
    withholding_exempt: bool = False
    workers_estimate: str = ""

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_meta(cls, data: Any) -> Any:  # noqa: ANN401
        if not isinstance(data, dict):
            return data
        sources = data.get("sources")
        if isinstance(sources, list) and any(
            isinstance(s, dict) and "document_id" not in s for s in sources
        ):
            data = {**data, "sources": [_coerce_legacy_source(s) for s in sources]}
        extraction = data.get("extraction")
        if isinstance(extraction, dict) and "extraction_timestamp" not in extraction:
            data = {**data, "extraction": _coerce_legacy_extraction(extraction, data)}
        return data


class CCNL(BaseModel):
    """Root model for a CCNL data file.

    Attributes:
        schema_version: Data file format version (semver string).
        ruleset: Identity and provenance of this contract ruleset
            (id, version, validity, source hash, verification status).
        meta: Identifying metadata — name, sector, INPS classification, sources.
        parameters: Contract-wide parameters (hourly divisor, additional months,
            seniority-increment rules, employer funds).
        levels: Ordered list of classification levels from lowest to highest pay.
        apprenticeship: Apprenticeship tracks modelled for this CCNL. Empty
            when apprenticeship is out of scope or not yet modelled.
        coverage: Implementation status flags and notes for the data file.
        layer_3: Layer 3 rule data (overtime, night work, etc.). ``None``
            when no L3 rules are modelled for this CCNL.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["0.4", "0.5"]
    ruleset: RulesetIdentity | None = None
    meta: CCNLMeta
    parameters: CCNLParameters
    levels: list[Level]
    apprenticeship: list[ApprenticeshipTrack] = Field(
        default=[],
        description=(
            "Apprenticeship tracks for this CCNL. Empty when not modelled "
            "(out of scope or data unavailable)."
        ),
    )
    coverage: CCNLCoverage
    layer_3: CCNLLayer3 | None = None

    @model_validator(mode="after")
    def _validate_cross_fields(self) -> Self:
        self._assert_unique_orders()
        self._assert_unique_codes()
        self._assert_seniority_level_codes()
        self._assert_salary_order_non_decreasing()
        self._assert_apprenticeship_tracks()
        self._assert_coverage_consistency()
        self._assert_provenance_complete()
        return self

    def level_by_code(self, level_code: str) -> Level:
        """Return the level with the given code, or raise ``ValueError``.

        Returns:
            The Level matching the given code.

        Raises:
            ValueError: If no level with the given code exists.
        """
        for lv in self.levels:
            if lv.code == level_code:
                return lv
        msg = f"level_code {level_code!r} not found in CCNL {self.meta.ccnl_id!r}"
        raise ValueError(msg)

    def level_by_order(self, order: int) -> Level:
        """Return the level with the given order, or raise ``ValueError``.

        Returns:
            The Level matching the given order.

        Raises:
            ValueError: If no level with the given order exists.
        """
        for lv in self.levels:
            if lv.order == order:
                return lv
        msg = f"no level with order {order} in CCNL {self.meta.ccnl_id!r}"
        raise ValueError(msg)

    def apprenticeship_tracks_for(self, level_code: str) -> list[ApprenticeshipTrack]:
        """Return every apprenticeship track whose destinations include a level.

        Returns:
            List of ApprenticeshipTrack objects that cover the given level code.
        """
        return [t for t in self.apprenticeship if level_code in t.destination_levels]

    def apprenticeship_track_named(self, name: str) -> ApprenticeshipTrack:
        """Return the apprenticeship track with the given name or raise ``ValueError``.

        Returns:
            The ApprenticeshipTrack with the given name.

        Raises:
            ValueError: If no track with the given name exists.
        """
        for track in self.apprenticeship:
            if track.name == name:
                return track
        msg = f"no apprenticeship track named {name!r} in CCNL {self.meta.ccnl_id!r}"
        raise ValueError(msg)

    def _assert_unique_orders(self) -> None:
        _assert_unique("order", [lv.order for lv in self.levels])

    def _assert_unique_codes(self) -> None:
        _assert_unique("code", [lv.code for lv in self.levels])

    def _assert_seniority_level_codes(self) -> None:
        existing = {lv.code for lv in self.levels}
        si = self.parameters.seniority_increments
        _check_flat_level_codes(existing, si)
        _check_category_level_codes(existing, si)
        _check_tier_level_codes(existing, si)

    def _assert_salary_order_non_decreasing(self) -> None:
        if len(self.levels) < 2:
            return
        sorted_levels = sorted(self.levels, key=lambda lv: lv.order)
        all_dates = _collect_transition_dates(sorted_levels)
        for check_date in sorted(all_dates):
            _check_salary_ordering_at_date(sorted_levels, check_date)

    def _assert_apprenticeship_tracks(self) -> None:
        names = [track.name for track in self.apprenticeship]
        if len(names) != len(set(names)):
            msg = f"apprenticeship track names must be unique, got: {names}"
            raise ValueError(msg)
        for track in self.apprenticeship:
            self._assert_single_track(track)

    def _assert_single_track(self, track: ApprenticeshipTrack) -> None:
        for code in track.destination_levels:
            try:
                dest = self.level_by_code(code)
            except ValueError:
                msg = (
                    f"apprenticeship track {track.name!r} references "
                    f"destination level {code!r} which does not exist"
                )
                raise ValueError(msg) from None
            if isinstance(track, ApprenticeshipUnderClassification):
                self._assert_offsets_resolve(track, dest)
        if (
            isinstance(track, ApprenticeshipPercentage)
            and track.reference_level is not None
        ):
            try:
                self.level_by_code(track.reference_level)
            except ValueError:
                msg = (
                    f"apprenticeship track {track.name!r} references "
                    f"reference_level {track.reference_level!r} which does not "
                    f"exist"
                )
                raise ValueError(msg) from None

    def _assert_offsets_resolve(
        self, track: ApprenticeshipUnderClassification, dest: Level
    ) -> None:
        for period in track.periods:
            target_order = dest.order - period.levels_below
            try:
                self.level_by_order(target_order)
            except ValueError:
                msg = (
                    f"apprenticeship track {track.name!r}: no level with "
                    f"order {target_order} ({period.levels_below} below "
                    f"destination {dest.code!r}, order {dest.order})"
                )
                raise ValueError(msg) from None

    def _assert_provenance_complete(self) -> None:
        """Verify that every rule in a schema-0.5 file carries provenance.

        Raises:
            ValueError: If any level, salary period, allowance monthly period,
                or seniority_increments is missing a ``provenance`` entry.
        """
        si = self.parameters.seniority_increments
        if si.provenance is None:
            msg = "seniority_increments.provenance is required"
            raise ValueError(msg)
        for level in self.levels:
            prefix = f"level {level.code!r}"
            if level.provenance is None:
                msg = f"{prefix}: provenance is required"
                raise ValueError(msg)
            for i, period in enumerate(level.base_salary.periods):
                if period.provenance is None:
                    msg = f"{prefix}: base_salary.periods[{i}].provenance is required"
                    raise ValueError(msg)
            for allowance in level.fixed_allowances:
                if allowance.provenance is None:
                    msg = (
                        f"{prefix}: allowance {allowance.code!r}.provenance is required"
                    )
                    raise ValueError(msg)

    def _assert_coverage_consistency(self) -> None:
        has_tracks = bool(self.apprenticeship)
        status = self.coverage.layer_2
        if status == "out_of_scope" and has_tracks:
            msg = "coverage.layer_2 is 'out_of_scope' but apprenticeship tracks exist"
            raise ValueError(msg)


def _check_salary_ordering_at_date(
    sorted_levels: list[Level], check_date: date
) -> None:
    """Verify that base salaries are non-decreasing across levels on one date.

    Raises:
        ValueError: If any level earns less than a lower-ordered level on that date.
    """
    prev_value: Decimal | None = None
    prev_code: str = ""
    for lv in sorted_levels:
        try:
            value = lv.base_salary.value_at(check_date)
        except ValueError:
            continue
        if prev_value is not None and value < prev_value:
            msg = (
                f"salary ordering violated on {check_date}: "
                f"level {lv.code!r} (order={lv.order}) "
                f"earns {value} < level {prev_code!r} earns {prev_value}"
            )
            raise ValueError(msg)
        prev_value = value
        prev_code = lv.code


def _check_flat_level_codes(existing: set[str], si: "SeniorityIncrements") -> None:
    for field_name, mapping in (
        ("amount_by_level", si.amount_by_level),
        ("maximum_count_by_level", si.maximum_count_by_level),
        ("first_cadence_months_by_level", si.first_cadence_months_by_level),
    ):
        for code in mapping:
            if code not in existing:
                msg = (
                    f"seniority_increments.{field_name} references level "
                    f"code {code!r} which does not exist in levels"
                )
                raise ValueError(msg)


def _check_category_level_codes(existing: set[str], si: "SeniorityIncrements") -> None:
    for cat, cat_amounts in si.amount_by_level_by_category.items():
        for code in cat_amounts:
            if code not in existing:
                msg = (
                    f"seniority_increments.amount_by_level_by_category"
                    f"[{cat!r}] references level code {code!r} which "
                    f"does not exist in levels"
                )
                raise ValueError(msg)


def _check_tier_level_codes(existing: set[str], si: "SeniorityIncrements") -> None:
    for i, tier in enumerate(si.tiers):
        for code in tier.amount_by_level:
            if code not in existing:
                msg = (
                    f"seniority_increments.tiers[{i}].amount_by_level "
                    f"references level code {code!r} which does not exist "
                    f"in levels"
                )
                raise ValueError(msg)


def _assert_unique(field: str, values: list[object]) -> None:
    if len(values) != len(set(values)):
        msg = f"level {field} values must be unique, got: {values}"
        raise ValueError(msg)


def _collect_transition_dates(levels: list[Level]) -> set[date]:
    all_dates: set[date] = set()
    for lv in levels:
        all_dates.update(period.valid_from for period in lv.base_salary.periods)
    return all_dates


def _coerce_legacy_source(source: dict[str, Any]) -> dict[str, Any]:
    """Shape a legacy ``meta.sources`` entry (schema 0.4) into a SourceDocument.

    Returns:
        A dict shaped for :class:`SourceDocument`.
    """
    url = source.get("url", "")
    doc_id = _slugify_url(url) or "source"
    kind = _legacy_source_kind(source.get("type"))
    return {
        "document_id": doc_id,
        "title": source.get("notes") or url or doc_id,
        "kind": kind,
        "url": url,
        "pages": [],
        "published_on": (
            source["agreement_date"] if source.get("agreement_date") else None
        ),
    }


def _slugify_url(url: str) -> str:
    slug = (
        url
        .strip()
        .lower()
        .replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
    )
    keep: list[str] = [ch if ch.isalnum() or ch in "-_" else "-" for ch in slug]
    squashed = "".join(keep).strip("-").strip("_")
    return squashed[:80]


def _legacy_source_kind(raw: str | None) -> SourceKind:  # noqa: PLR0911
    value = (raw or "").lower()
    if any(token in value for token in ("tabella", "table", "salary", "wage")):
        return SourceKind.TABELLA_RETRIBUTIVA
    if "gazzetta" in value:
        return SourceKind.GAZZETTA
    if "cnel" in value:
        return SourceKind.CNEL
    if any(token in value for token in ("circolar", "circular")):
        return SourceKind.INPS_CIRCOLARE
    if "legge" in value:
        return SourceKind.LEGGE
    if "dpr" in value:
        return SourceKind.DPR
    if any(token in value for token in ("dl ", "decreto")):
        return SourceKind.DL
    if any(token in value for token in ("associazion", "aggregator")):
        return SourceKind.ASSOCIAZIONE
    return SourceKind.ALTRO


def _coerce_legacy_extraction(
    extraction: dict[str, Any], meta: dict[str, Any]
) -> dict[str, Any]:
    """Shape a legacy ``meta.extraction`` block (schema 0.4) into an ExtractionTrace.

    ``effective_from`` is inferred from ``meta.validity`` when present, else
    set to a pre-agreement epoch so the trace always carries a date.

    Returns:
        A dict shaped for :class:`ExtractionTrace`.
    """
    human_reviewed = bool(extraction.get("human_reviewed"))
    raw_validity = meta.get("validity")
    validity: dict[str, Any] = raw_validity if isinstance(raw_validity, dict) else {}
    timestamp = extraction.get("timestamp") or datetime.now(tz=UTC).isoformat()
    return {
        "method": extraction.get("method") or "manual",
        "model": extraction.get("model"),
        "extraction_timestamp": timestamp,
        "verification_status": "verified" if human_reviewed else "unverified",
        "effective_from": validity.get("valid_from") or "1970-01-01",
    }
