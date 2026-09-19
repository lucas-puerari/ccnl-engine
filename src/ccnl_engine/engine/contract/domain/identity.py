"""CCNL identity, coverage, and root model."""

from collections.abc import Mapping
from datetime import date
from enum import StrEnum
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.absence import AbsenceRules
from ccnl_engine.engine.contract.domain.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipTrack,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.engine.contract.domain.compensation import CCNLParameters, Level
from ccnl_engine.engine.contract.domain.seniority import SeniorityIncrements
from ccnl_engine.engine.contract.domain.sickness import SicknessRules
from ccnl_engine.engine.contract.domain.validation import (
    _assert_level_provenance,
    _assert_unique,
    _check_category_level_codes,
    _check_flat_level_codes,
    _check_salary_ordering_at_date,
    _check_tier_level_codes,
    _coerce_legacy_extraction,
    _coerce_legacy_source,
    _collect_transition_dates,
)
from ccnl_engine.engine.contract.domain.working_time import LeaveRules, TimeSupplements
from ccnl_engine.engine.metadata import RulesetIdentity
from ccnl_engine.engine.metadata.domain.rules import (
    RulesetReadiness,
    VerificationStatus,
)
from ccnl_engine.engine.primitives import FrozenDict
from ccnl_engine.engine.provenance.domain.extraction import ExtractionTrace
from ccnl_engine.engine.provenance.domain.source import SourceDocument


class CoverageStatus(StrEnum):
    """Implementation status for a CCNL coverage layer."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    OUT_OF_SCOPE = "out_of_scope"
    NOT_IMPLEMENTED = "not_implemented"


class WorkRuleFeature(StrEnum):
    """Enumeration of work-rules payroll features."""

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

    model_config = ConfigDict(extra="forbid", frozen=True)

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


class CCNLWorkRules(BaseModel):
    """Container for work rules attached to a CCNL data file."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    time_supplements: TimeSupplements | None = None
    absence_rules: AbsenceRules | None = None
    leave_rules: LeaveRules | None = None
    sickness_rules: SicknessRules | None = None


class CCNLCoverage(BaseModel):
    """Declares implementation completeness for a CCNL data file.

    Measures *what* the engine implements, not how trustworthy the values are.
    For human-review confidence and traceability use :class:`CCNLVerification`.

    * **Coverage** (``gross`` / ``net`` / ``work_rules``): what the engine
      implements for this contract — ``implemented``, ``partial``, or
      ``out_of_scope``.

      - L1 — Gross: base salary, seniority, fixed allowances, additional
        months, hourly rate.
      - L2 — Net: INPS contributions, TFR, IRPEF, regional/municipal surtax.
      - Work rules — Extended: overtime, sick/injury leave, performance bonuses,
        welfare/benefits. Defaults to ``not_implemented``.

    ``work_rules`` is the scalar summary status (for backward compat with the
    coverage matrix). ``work_rules_features`` is the authoritative per-feature
    dict; it drives the computed work-rules rollup and the per-feature coverage
    table.

    A ``missing`` note documents data the engine supports but the file lacks,
    and is only allowed while at least one of gross / net is ``partial``
    or any work_rules feature is ``partial``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    gross: CoverageStatus
    net: CoverageStatus
    work_rules: CoverageStatus = CoverageStatus.NOT_IMPLEMENTED
    work_rules_features: Mapping[WorkRuleFeature, CoverageStatus] = Field(
        default_factory=dict
    )
    notes: tuple[CoverageNote, ...]

    @model_validator(mode="after")
    def _check_notes(self) -> Self:
        has_missing = any(n.kind == NoteKind.MISSING for n in self.notes)
        any_wr_partial = any(
            v == CoverageStatus.PARTIAL for v in self.work_rules_features.values()
        )
        if (
            has_missing
            and "partial" not in {self.gross, self.net}
            and not any_wr_partial
        ):
            msg = (
                "coverage has 'missing' notes but neither gross nor net "
                "is 'partial' and no work_rules feature is 'partial'"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _freeze_dicts(self) -> Self:
        object.__setattr__(  # noqa: PLC2801
            self,
            "work_rules_features",
            FrozenDict(self.work_rules_features),
        )
        return self


class CCNLVerification(BaseModel):
    """Human-review confidence and traceability for a CCNL data file.

    Measures *how trustworthy* the values are, orthogonal to field completeness.
    See :class:`CCNLCoverage` for implementation-completeness flags.

    Attributes:
        confidence: Editorial confidence in the data values — ``verified``,
            ``unverified``, or ``needs_review``.
        readiness: Production readiness of the ruleset as a whole —
            ``exploratory``, ``reviewed``, or ``production``. Separate from
            ``confidence``: a ruleset can be ``confidence=verified`` for its
            key values but still ``readiness=exploratory`` if it lacks an
            owner, reference cases, or an update-policy entry. Defaults to
            ``exploratory`` for all unclassified rulesets.
        verified_cases: Number of end-to-end payroll scenarios manually
            cross-checked against a reference payslip or official source.
        last_reviewed: ISO date of the most recent human review.
        human_reviewed_by: Identifier (name or email) of the reviewer.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    confidence: VerificationStatus = VerificationStatus.UNVERIFIED
    readiness: RulesetReadiness = RulesetReadiness.EXPLORATORY
    verified_cases: int = 0
    last_reviewed: date | None = None
    human_reviewed_by: str | None = None


class CCNLValidity(BaseModel):
    """Contractual validity window of the modelled agreement."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    valid_from: date
    valid_until: date | None = None


class CCNLMeta(BaseModel):
    """Identifying metadata for a CCNL.

    Attributes:
        ccnl_id: Unique slug for the contract
            (e.g. ``"metalmeccanico-federmeccanica"``). Used as
            ``AnnualEstimate.ccnl_id``.
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
            ``AnnualEstimate.employer_withholds_irpef`` as ``False``.
        workers_estimate: Approximate number of workers covered by this agreement,
            as a human-readable string (e.g. ``"~800k"``). Based on CNEL and INPS
            estimates. Empty string when unknown.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    ccnl_id: str
    name: str
    cnel_code: str
    sector: str
    tax_sector: TaxSector
    signatories: tuple[str, ...]
    sources: tuple[SourceDocument, ...]
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
        coverage: Implementation completeness flags and notes for the data file.
        verification: Human-review confidence and traceability metadata.
        work_rules: Work-rules data (overtime, leave, sickness, absence). ``None``
            when no work rules are modelled for this CCNL.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["0.4", "0.5"]
    ruleset: RulesetIdentity | None = None
    meta: CCNLMeta
    parameters: CCNLParameters
    levels: tuple[Level, ...]
    apprenticeship: tuple[ApprenticeshipTrack, ...] = Field(
        default=(),
        description=(
            "Apprenticeship tracks for this CCNL. Empty when not modelled "
            "(out of scope or data unavailable)."
        ),
    )
    coverage: CCNLCoverage
    verification: CCNLVerification = Field(default_factory=CCNLVerification)
    work_rules: CCNLWorkRules | None = None

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
        si: SeniorityIncrements = self.parameters.seniority_increments
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
            _assert_level_provenance(level)

    def _assert_coverage_consistency(self) -> None:
        has_tracks = bool(self.apprenticeship)
        status = self.coverage.net
        if status == "out_of_scope" and has_tracks:
            msg = "coverage.net is 'out_of_scope' but apprenticeship tracks exist"
            raise ValueError(msg)
