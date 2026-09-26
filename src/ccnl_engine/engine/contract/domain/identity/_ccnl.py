"""CCNL root model."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipTrack,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.engine.contract.domain.compensation import CCNLParameters, Level
from ccnl_engine.engine.contract.domain.identity._coverage import (
    CCNLCoverage,
    CCNLWorkRules,
)
from ccnl_engine.engine.contract.domain.identity._meta import (
    CCNLMeta,
    CCNLVerification,
)
from ccnl_engine.engine.contract.domain.seniority import SeniorityIncrements
from ccnl_engine.engine.contract.domain.validation import (
    _assert_level_provenance,
    _assert_unique,
    _check_category_level_codes,
    _check_flat_level_codes,
    _check_salary_ordering_at_date,
    _check_tier_level_codes,
    _collect_transition_dates,
)
from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity


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
