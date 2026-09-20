"""Serialisable snapshot of payroll computation inputs."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
from ccnl_engine.engine.serialization.dataclass_codec import (
    _deep_freeze,
    _deep_thaw,
    _dump,
    _load_by_hint,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import TaxSector


def _materialise(scenario_data: Mapping[str, object]) -> _InternalScenario:
    """Rebuild the :class:`_InternalScenario` from the snapshot.

    Returns:
        The reconstructed :class:`_InternalScenario`.
    """
    return cast(_InternalScenario, _load_by_hint(_InternalScenario, scenario_data))


@dataclass(frozen=True)
class InputSnapshot:
    """Serialisable, lossless copy of the inputs to one payroll computation.

    Attributes:
        ccnl_id: Identifier of the CCNL used (mirrors ``AnnualEstimate.ccnl_id``).
        tax_sector: INPS tax-sector classification used to load tax rules.
        year: Fiscal/tax year of the computation (from ``YearRules.year``).
        uses_surtax: ``True`` when addizionale rules were applied.
        scenario: JSON-native serialisation of the :class:`PayrollScenario`.
    """

    ccnl_id: str
    tax_sector: str
    year: int
    uses_surtax: bool
    scenario: Mapping[str, object]

    def __post_init__(self) -> None:
        """Deep-freeze the scenario so it cannot be mutated after construction."""
        object.__setattr__(self, "scenario", _deep_freeze(self.scenario))

    @classmethod
    def capture(
        cls,
        scenario: _InternalScenario,
        ccnl_id: str,
        tax_sector: TaxSector,
        year: int,
        uses_surtax: bool,
    ) -> InputSnapshot:
        """Build a snapshot from a live :class:`_InternalScenario`.

        Returns:
            A new snapshot carrying the JSON-native copy of the scenario.
        """
        return cls(
            ccnl_id=ccnl_id,
            tax_sector=str(tax_sector),
            year=year,
            uses_surtax=uses_surtax,
            scenario=cast(dict[str, object], _dump(scenario)),
        )

    def materialise(self) -> _InternalScenario:
        """Rebuild the :class:`_InternalScenario` from the snapshot.

        Returns:
            The reconstructed :class:`_InternalScenario`.
        """
        return _materialise(self.scenario)

    def to_dict(self) -> dict[str, object]:
        """Serialise the snapshot to a JSON-native dict.

        Returns:
            A dictionary with ``str``/``int``/``bool``/``dict`` values.
            The ``scenario`` value is a plain dict copy produced by
            :func:`_deep_thaw` so mutations of the returned dict cannot
            alter the frozen stored snapshot.
        """
        return {
            "ccnl_id": self.ccnl_id,
            "tax_sector": self.tax_sector,
            "year": self.year,
            "uses_surtax": self.uses_surtax,
            "scenario": cast(dict[str, object], _deep_thaw(self.scenario)),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> InputSnapshot:
        """Reconstruct a snapshot from a dictionary (see :meth:`to_dict`).

        Validation is strict: every field must carry exactly the Python type
        that :meth:`to_dict` / :func:`json.loads` produces.  Coercions such
        as ``bool("false")`` or ``int("2026")`` are rejected with
        :exc:`TypeError` so a malformed payload cannot silently flip the
        semantics of ``uses_surtax`` or mask a wrong-typed field.

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`InputSnapshot` equal to the original.

        Raises:
            TypeError: If any field value has the wrong type or if *data*
                contains unexpected keys.
        """
        allowed = frozenset({
            "ccnl_id",
            "tax_sector",
            "year",
            "uses_surtax",
            "scenario",
        })
        extra = set(data) - allowed
        if extra:
            msg = f"InputSnapshot.from_dict: unexpected keys: {sorted(extra)}"
            raise TypeError(msg)

        def _check(key: str, val: object, expected: type) -> None:
            """Raise TypeError when *val* is not exactly *expected*.

            ``bool`` is a subclass of ``int`` in Python; passing a ``bool``
            for an ``int`` field is therefore also rejected.

            Raises:
                TypeError: If *val* is not an instance of *expected*.
            """
            if not isinstance(val, expected) or (
                expected is int and isinstance(val, bool)
            ):
                msg = (
                    f"InputSnapshot.from_dict: '{key}' must be "
                    f"{expected.__name__}, got {type(val).__name__}"
                )
                raise TypeError(msg)

        _check("ccnl_id", data["ccnl_id"], str)
        _check("tax_sector", data["tax_sector"], str)
        _check("year", data["year"], int)
        _check("uses_surtax", data["uses_surtax"], bool)
        _check("scenario", data["scenario"], dict)
        return cls(
            ccnl_id=cast(str, data["ccnl_id"]),
            tax_sector=cast(str, data["tax_sector"]),
            year=cast(int, data["year"]),
            uses_surtax=cast(bool, data["uses_surtax"]),
            scenario=cast(dict[str, object], data["scenario"]),
        )

    def to_json(self) -> str:
        """Serialise the snapshot to a JSON string.

        Returns:
            A compact JSON string (see :meth:`to_dict` for the encoding).
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, raw: str) -> InputSnapshot:
        """Reconstruct a snapshot from a JSON string.

        Args:
            raw: JSON returned by :meth:`to_json`.

        Returns:
            A new :class:`InputSnapshot` equal to the original.
        """
        return cls.from_dict(json.loads(raw))
