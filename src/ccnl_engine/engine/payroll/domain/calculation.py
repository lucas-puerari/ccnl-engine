"""Calculation provenance: what a payroll computation used and how to replay it.

A :class:`Calculation` wraps the
:class:`~ccnl_engine.engine.payroll.domain.payroll_result.AnnualEstimate` with
everything needed to reproduce it later: the engine version that ran it, the
identity/version of every ruleset it consumed, and a serialisable snapshot of
the raw inputs. The snapshot can be serialised to JSON and, given the same
(possibly re-loaded) knowledge-base rulesets, replayed through ``compute`` to
yield an identical result years later.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ccnl_engine.engine.capability_catalog import CapabilityCatalog, CapabilityGap

from ccnl_engine.engine.payroll.domain.ledger import LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import PayItem
from ccnl_engine.engine.payroll.domain.payroll_result import (
    AnnualEstimate,
    PeriodPayroll,
)
from ccnl_engine.engine.payroll.domain.snapshot import InputSnapshot
from ccnl_engine.engine.payroll.domain.trace import (
    CalculationTrace,
    TraceCategory,
    TraceStep,
)
from ccnl_engine.engine.primitives import FrozenDict
from ccnl_engine.engine.serialization.dataclass_codec import (
    _FIELD_RENAMES,
    _NO_MATCH,
    _apply_renames,
    _coerce_scalar,
    _deep_freeze,
    _deep_thaw,
    _dump,
    _dump_dataclass,
    _dump_dict,
    _dump_frozenset,
    _load_by_hint,
    _load_collection_hint,
    _load_dataclass,
    _load_plain_dataclass,
    _load_pydantic_model,
    _load_union,
    _load_union_hint,
    _try_union_member,
    _unwrap_annotated,
)

__all__ = [
    "_FIELD_RENAMES",
    "_NO_MATCH",
    "Calculation",
    "CalculationTrace",
    "InputSnapshot",
    "LedgerEntry",
    "TraceCategory",
    "TraceStep",
    "_apply_renames",
    "_coerce_scalar",
    "_deep_freeze",
    "_deep_thaw",
    "_dump",
    "_dump_dataclass",
    "_dump_dict",
    "_dump_frozenset",
    "_load_by_hint",
    "_load_collection_hint",
    "_load_dataclass",
    "_load_plain_dataclass",
    "_load_pydantic_model",
    "_load_union",
    "_load_union_hint",
    "_try_union_member",
    "_unwrap_annotated",
]


def _result_from_dict(data: dict[str, object]) -> AnnualEstimate:
    """Deserialize a result dict into AnnualEstimate or PeriodPayroll.

    Returns:
        A :class:`PeriodPayroll` when *data* has a ``pay_period`` key,
        otherwise a plain :class:`AnnualEstimate`.
    """
    if "pay_period" in data:
        return PeriodPayroll.from_dict(data)
    return AnnualEstimate.from_dict(data)


@dataclass(frozen=True)
class Calculation:
    """A payroll computation together with everything needed to replay it.

    Attributes:
        engine_version: Version of the engine library that produced this
            calculation (see :mod:`ccnl_engine.version`).
        ruleset_version: Mapping of ruleset kind (``ccnl``, ``tax``, ``surtax``)
            to the ``id@version`` identity of the ruleset that was used.
        ruleset_verification: Mapping of ruleset kind to its
            :class:`~ccnl_engine.engine.metadata.domain.rules.VerificationStatus`
            value string.  Keys mirror :attr:`ruleset_version`.  Empty for
            calculations produced by older engine versions.
        input_snapshot: Lossless copy of the raw inputs.
        result: The resulting :class:`AnnualEstimate` (or :class:`PeriodPayroll`).
        trace: Step-by-step record of the monthly gross computation chain.
            An empty trace signals that the calculation was produced by an
            older engine version that did not emit one.
    """

    engine_version: str
    ruleset_version: Mapping[str, str]
    input_snapshot: InputSnapshot
    result: AnnualEstimate
    trace: CalculationTrace = dataclasses.field(
        default_factory=lambda: CalculationTrace(steps=())
    )
    ruleset_verification: Mapping[str, str] = dataclasses.field(
        default_factory=FrozenDict
    )
    ledger_entries: tuple[LedgerEntry, ...] = dataclasses.field(
        default_factory=tuple, compare=False
    )
    pay_items: tuple[PayItem, ...] = dataclasses.field(
        default_factory=tuple, compare=False
    )

    def __post_init__(self) -> None:
        """Freeze ruleset_version and ruleset_verification after construction."""
        object.__setattr__(
            self,
            "ruleset_version",
            FrozenDict(dict(self.ruleset_version)),
        )
        object.__setattr__(
            self,
            "ruleset_verification",
            FrozenDict(dict(self.ruleset_verification)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialise the full calculation to a JSON-native dict.

        Returns:
            A dictionary with the provenance fields, the input snapshot,
            the payroll result, and the computation trace.
        """
        out: dict[str, object] = {
            "engine_version": self.engine_version,
            "ruleset_version": dict(sorted(self.ruleset_version.items())),
            "input_snapshot": self.input_snapshot.to_dict(),
            "result": self.result.to_dict(),
            "trace": self.trace.to_dict(),
        }
        if self.ruleset_verification:
            out["ruleset_verification"] = dict(
                sorted(self.ruleset_verification.items())
            )
        return out

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Calculation:
        """Reconstruct a calculation from a dictionary (see :meth:`to_dict`).

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Calculation` equal to the original.

        Raises:
            TypeError: If ``engine_version`` or ``ruleset_version`` values are
                not ``str``.
        """
        engine_version = data["engine_version"]
        if not isinstance(engine_version, str):
            msg = (
                f"Calculation.from_dict: 'engine_version' must be str, "
                f"got {type(engine_version).__name__}"
            )
            raise TypeError(msg)
        rv_raw = cast(dict[str, object], data["ruleset_version"])
        for k, v in rv_raw.items():
            if not isinstance(k, str) or not isinstance(v, str):
                msg = (
                    "Calculation.from_dict: 'ruleset_version' keys and "
                    "values must be str"
                )
                raise TypeError(msg)
        ruleset_version = cast(dict[str, str], rv_raw)
        rv_raw_ver = cast(dict[str, object], data.get("ruleset_verification", {}))
        for k, v in rv_raw_ver.items():
            if not isinstance(k, str) or not isinstance(v, str):
                msg = (
                    "Calculation.from_dict: 'ruleset_verification' keys and "
                    "values must be str"
                )
                raise TypeError(msg)
        ruleset_verification = cast(dict[str, str], rv_raw_ver)
        return cls(
            engine_version=engine_version,
            ruleset_version=ruleset_version,
            ruleset_verification=ruleset_verification,
            input_snapshot=InputSnapshot.from_dict(
                cast(dict[str, object], data["input_snapshot"])
            ),
            result=_result_from_dict(cast(dict[str, object], data["result"])),
            trace=(
                CalculationTrace.from_dict(cast(dict[str, object], data["trace"]))
                if "trace" in data
                else CalculationTrace(steps=())
            ),
        )

    def to_json(self) -> str:
        """Serialise the calculation to a JSON string.

        Returns:
            A compact JSON string (see :meth:`to_dict` for the encoding).
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, raw: str) -> Calculation:
        """Reconstruct a calculation from a JSON string.

        Args:
            raw: JSON returned by :meth:`to_json`.

        Returns:
            A new :class:`Calculation` equal to the original.
        """
        return cls.from_dict(json.loads(raw))

    def check_capability_gaps(
        self, catalog: CapabilityCatalog
    ) -> tuple[CapabilityGap, ...]:
        """Return features declared in *catalog* that this calculation did not compute.

        Builds the observed status map from the calculation scope and delegates
        to :meth:`~ccnl_engine.engine.capability_catalog.CapabilityCatalog.gaps`.

        Args:
            catalog: The capability catalog for the same fiscal year as this
                calculation.

        Returns:
            Gaps in declaration order, one per feature declared at least
            ``computed`` or ``partially_computed`` in the catalog but observed
            as ``not_computed`` in this calculation.
        """
        observed = {
            item.feature: item.calculation_status
            for item in self.result.coverage.calculation_scope
        }
        return catalog.gaps(observed)
