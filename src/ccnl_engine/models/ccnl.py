"""CCNL domain models."""

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.models.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipTrack,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.models.validity import TimeSeries

#: Implementation status of a coverage layer.
CoverageStatus = Literal["implemented", "partial", "out_of_scope"]

#: Worker category of a classification level (drives contribution rates
#: and employer-fund applicability).
LevelCategory = Literal["operaio", "impiegato", "quadro", "dirigente"]

#: Allowed prefixes for coverage notes.
NOTE_PREFIXES: tuple[str, ...] = ("SIMPLIFICATION:", "MISSING:", "SOURCE:", "INFO:")
_MISSING_PREFIX = "MISSING:"


class TaxSector(StrEnum):
    """INPS sector classification used to select the contribution-rate file."""

    TERZIARIO = "terziario"
    INDUSTRIA = "industria"
    EDILIZIA = "edilizia"
    CREDITO = "credito"
    ARTIGIANATO = "artigianato"
    PUBBLICA_AMMINISTRAZIONE = "pubblica_amministrazione"


class Allowance(BaseModel):
    """A named fixed monthly allowance attached to a CCNL level.

    ``role`` restricts the allowance to workers holding that role (``None``
    means every worker at the level). ``months_per_year`` overrides the
    contract-wide ``additional_months`` for this allowance only. The two
    relevance flags exclude the allowance from the contribution and TFR bases.
    """

    model_config = ConfigDict(extra="forbid")

    code: str
    description: str
    monthly: TimeSeries
    role: str | None = None
    months_per_year: int | None = Field(default=None, ge=1)
    tfr_relevant: bool = True
    contribution_relevant: bool = True


class SeniorityIncrements(BaseModel):
    """Seniority increment (*scatti di anzianità*) rules for a CCNL.

    ``first_cadence_months`` is the service required for the first increment
    when it differs from ``cadence_months``; ``first_cadence_months_by_level``
    and ``maximum_count_by_level`` override the contract-wide values for
    specific levels. ``apprentice_amount`` is the increment (if any) accrued
    during an apprenticeship, replacing the level amount. Workers of an
    ``excluded_categories`` category accrue no increment (e.g. operai edili,
    who receive APE through the Cassa Edile instead).
    """

    model_config = ConfigDict(extra="forbid")

    cadence_months: int = Field(gt=0)
    maximum_count: int = Field(ge=0)
    amount_by_level: dict[str, TimeSeries]
    first_cadence_months: int | None = Field(default=None, gt=0)
    first_cadence_months_by_level: dict[str, int] = {}
    maximum_count_by_level: dict[str, int] = {}
    apprentice_amount: TimeSeries | None = None
    excluded_categories: list[LevelCategory] = []

    @model_validator(mode="after")
    def _check_cadence(self) -> Self:
        candidates = [("first_cadence_months", self.first_cadence_months)]
        candidates += [
            (f"first_cadence_months_by_level[{code!r}]", months)
            for code, months in self.first_cadence_months_by_level.items()
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
        return self

    def maximum_for(self, level_code: str) -> int:
        """Return the maximum increment count applicable to a level.

        Returns:
            The maximum seniority increment count for the given level.
        """
        return self.maximum_count_by_level.get(level_code, self.maximum_count)

    def first_cadence_for(self, level_code: str) -> int:
        """Return the months of service required for the first increment.

        Returns:
            The months of service required for the first seniority increment.
        """
        return self.first_cadence_months_by_level.get(
            level_code, self.first_cadence_months or self.cadence_months
        )


class EmployerFund(BaseModel):
    """An employer-side contribution to a contractual fund (e.g. Cassa Edile).

    ``rate`` is a fraction of the contribution base. ``applies_to_categories``
    restricts the fund to levels of the given categories (``None`` = all).
    """

    model_config = ConfigDict(extra="forbid")

    code: str
    description: str
    rate: TimeSeries
    applies_to_categories: list[LevelCategory] | None = None

    def applies_to(self, category: LevelCategory | None) -> bool:
        """Return whether the fund applies to a level of the given category.

        Returns:
            True if the fund applies to the given category, False otherwise.
        """
        if self.applies_to_categories is None:
            return True
        return category is not None and category in self.applies_to_categories


class Parameters(BaseModel):
    """Contract-wide parameters."""

    model_config = ConfigDict(extra="forbid")

    hourly_divisor: TimeSeries
    additional_months: TimeSeries
    seniority_increments: SeniorityIncrements
    employer_funds: list[EmployerFund] = []


class Level(BaseModel):
    """A single classification level (*livello di inquadramento*)."""

    model_config = ConfigDict(extra="forbid")

    code: str
    order: int
    description: str
    base_salary: TimeSeries
    fixed_allowances: list[Allowance] = []
    category: LevelCategory | None = None

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


class Coverage(BaseModel):
    """Declares implementation status for a CCNL data file.

    Every note must start with one of :data:`NOTE_PREFIXES`. A ``MISSING:``
    note documents data the engine supports but the file lacks, and is only
    allowed while at least one of layer 1 / layer 2 is ``partial``.
    """

    model_config = ConfigDict(extra="forbid")

    layer_1: CoverageStatus
    layer_2: CoverageStatus
    layer_3: CoverageStatus
    notes: list[str]

    @model_validator(mode="after")
    def _check_notes(self) -> Self:
        for i, note in enumerate(self.notes):
            if not note.startswith(NOTE_PREFIXES):
                msg = (
                    f"coverage.notes[{i}] must start with one of "
                    f"{list(NOTE_PREFIXES)}, got: {note[:60]!r}"
                )
                raise ValueError(msg)
        has_missing = any(n.startswith(_MISSING_PREFIX) for n in self.notes)
        if has_missing and "partial" not in {self.layer_1, self.layer_2}:
            msg = (
                "coverage has MISSING: notes but neither layer_1 nor layer_2 "
                "is 'partial'"
            )
            raise ValueError(msg)
        return self


class CCNLSource(BaseModel):
    """A primary source reference for a CCNL data file."""

    model_config = ConfigDict(extra="forbid")

    url: str
    type: str
    agreement_date: str | None = None
    notes: str | None = None


class CCNLValidity(BaseModel):
    """Contractual validity window of the modelled agreement."""

    model_config = ConfigDict(extra="forbid")

    valid_from: date
    valid_until: date | None = None


class CCNLExtraction(BaseModel):
    """Metadata about how the CCNL data was extracted."""

    model_config = ConfigDict(extra="forbid")

    method: str
    model: str | None = None
    timestamp: str
    human_reviewed: bool


class CCNLMeta(BaseModel):
    """Identifying metadata for a CCNL."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    cnel_code: str
    sector: str
    tax_sector: TaxSector
    signatories: list[str]
    sources: list[CCNLSource]
    extraction: CCNLExtraction
    agreement_date: str | None = None
    validity: CCNLValidity | None = None


class CCNL(BaseModel):
    """Root model for a CCNL data file."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    meta: CCNLMeta
    parameters: Parameters
    levels: list[Level]
    apprenticeship: list[ApprenticeshipTrack] = Field(
        default=[],
        description=(
            "Apprenticeship tracks for this CCNL. Empty when not modelled "
            "(out of scope or data unavailable)."
        ),
    )
    coverage: Coverage

    @model_validator(mode="after")
    def _validate_cross_fields(self) -> Self:
        self._assert_unique_orders()
        self._assert_unique_codes()
        self._assert_seniority_level_codes()
        self._assert_salary_order_non_decreasing()
        self._assert_apprenticeship_tracks()
        self._assert_coverage_consistency()
        return self

    def level_by_code(self, level_code: str) -> Level:
        """Return the level with the given code, or raise ``KeyError``.

        Returns:
            The Level matching the given code.

        Raises:
            KeyError: If no level with the given code exists.
        """
        for lv in self.levels:
            if lv.code == level_code:
                return lv
        msg = f"level_code {level_code!r} not found in CCNL {self.meta.id!r}"
        raise KeyError(msg)

    def level_by_order(self, order: int) -> Level:
        """Return the level with the given order, or raise ``KeyError``.

        Returns:
            The Level matching the given order.

        Raises:
            KeyError: If no level with the given order exists.
        """
        for lv in self.levels:
            if lv.order == order:
                return lv
        msg = f"no level with order {order} in CCNL {self.meta.id!r}"
        raise KeyError(msg)

    def apprenticeship_tracks_for(self, level_code: str) -> list[ApprenticeshipTrack]:
        """Return every apprenticeship track whose destinations include a level.

        Returns:
            List of ApprenticeshipTrack objects that cover the given level code.
        """
        return [t for t in self.apprenticeship if level_code in t.destination_levels]

    def apprenticeship_track_named(self, name: str) -> ApprenticeshipTrack:
        """Return the apprenticeship track with the given name or raise ``KeyError``.

        Returns:
            The ApprenticeshipTrack with the given name.

        Raises:
            KeyError: If no track with the given name exists.
        """
        for track in self.apprenticeship:
            if track.name == name:
                return track
        msg = f"no apprenticeship track named {name!r} in CCNL {self.meta.id!r}"
        raise KeyError(msg)

    def _assert_unique_orders(self) -> None:
        orders = [lv.order for lv in self.levels]
        if len(orders) != len(set(orders)):
            msg = f"level order values must be unique, got: {orders}"
            raise ValueError(msg)

    def _assert_unique_codes(self) -> None:
        codes = [lv.code for lv in self.levels]
        if len(codes) != len(set(codes)):
            msg = f"level code values must be unique, got: {codes}"
            raise ValueError(msg)

    def _assert_seniority_level_codes(self) -> None:
        existing = {lv.code for lv in self.levels}
        si = self.parameters.seniority_increments
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

    def _assert_salary_order_non_decreasing(self) -> None:
        if len(self.levels) < 2:
            return
        sorted_levels = sorted(self.levels, key=lambda lv: lv.order)
        all_dates = _collect_transition_dates(sorted_levels)
        for check_date in sorted(all_dates):
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

    def _assert_apprenticeship_tracks(self) -> None:
        names = [track.name for track in self.apprenticeship]
        if len(names) != len(set(names)):
            msg = f"apprenticeship track names must be unique, got: {names}"
            raise ValueError(msg)
        for track in self.apprenticeship:
            for code in track.destination_levels:
                try:
                    dest = self.level_by_code(code)
                except KeyError:
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
                except KeyError:
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
            except KeyError:
                msg = (
                    f"apprenticeship track {track.name!r}: no level with "
                    f"order {target_order} ({period.levels_below} below "
                    f"destination {dest.code!r}, order {dest.order})"
                )
                raise ValueError(msg) from None

    def _assert_coverage_consistency(self) -> None:
        has_tracks = bool(self.apprenticeship)
        status = self.coverage.layer_2
        if status == "implemented" and not has_tracks:
            msg = "coverage.layer_2 is 'implemented' but no apprenticeship track exists"
            raise ValueError(msg)
        if status == "out_of_scope" and has_tracks:
            msg = "coverage.layer_2 is 'out_of_scope' but apprenticeship tracks exist"
            raise ValueError(msg)


def _collect_transition_dates(levels: list[Level]) -> set[date]:
    all_dates: set[date] = set()
    for lv in levels:
        all_dates.update(period.valid_from for period in lv.base_salary.periods)
    return all_dates
