"""AnnualEstimate — the main payroll computation result type."""

from __future__ import annotations

import dataclasses
import json
import typing
from dataclasses import dataclass, field
from datetime import date as _date
from decimal import Decimal
from typing import cast

from ccnl_engine.engine.payroll.domain.components import (
    Contributions,
    Earnings,
    EmployerCost,
    Taxes,
    _coerce,
    _has_default,
    _serialise_value,
)
from ccnl_engine.engine.payroll.domain.coverage import Coverage
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance

_SUB_OBJECT_DECODERS: dict[
    str, type[Earnings | Contributions | Taxes | EmployerCost | Coverage]
] = {
    "earnings": Earnings,
    "contributions": Contributions,
    "taxes": Taxes,
    "employer_cost": EmployerCost,
    "coverage": Coverage,
}


def _decode_field(
    name: str,
    raw: object,
    hint: type,
    extra_decoders: dict[str, object] | None = None,
) -> object:
    """Coerce *raw* to the type expected for field *name*.

    Returns:
        The decoded value from a sub-object decoder or :func:`_coerce`.
    """
    if isinstance(raw, dict):
        decoder = _SUB_OBJECT_DECODERS.get(name)
        if decoder is not None:
            return decoder.from_dict(cast(dict[str, object], raw))
        if extra_decoders:
            extra = extra_decoders.get(name)
            if callable(extra):
                return extra(raw)
    return _coerce(raw, hint)


@dataclass(frozen=True, kw_only=True)
class AnnualEstimate:
    """Annual gross-to-net and employer-cost estimate for one payroll scenario.

    All monetary amounts are in EUR. Annual figures assume the contract-wide
    ``additional_months`` pay structure (typically 13 or 14 months).

    Attributes:
        ccnl_id: Identifier of the CCNL used (from ``CCNLMeta.id``).
        level_code: Classification level code used for the computation.
        employment_type: String tag of the employment type
            (``"permanent"``, ``"fixed_term"``, or ``"apprentice"``).
        part_time_ratio: Part-time coefficient applied to gross and
            contribution bases.  ``1`` for a full-time worker.
        as_of: Reference date used to resolve all time-series values.
        year: Calendar year of the pay period.
        contract_effective_date: Date from which the applicable CCNL
            salary rates are effective.  Equal to ``as_of`` when the
            contract rate period started on or before the reference date.
        tax_rule_year: Calendar year used to load IRPEF brackets and
            contribution rules.  May differ from ``year`` when an explicit
            ``tax_year`` override was passed to the scenario.
        earnings: Gross pay breakdown: base, seniority, allowances, total.
        contributions: Employee and employer social contributions.
        taxes: IRPEF chain, addizionali, and fiscal deductions.
        employer_cost: Total annual employer cost.
        coverage: Computation quality, scope, and consumed-policy identity.
        provenance: Ordered provenance of salary rules consumed.
        net_annual: Annual net pay.
        net_monthly: Monthly net pay (``net_annual / additional_months``).
        schema_version: Serialisation schema version.
    """

    ccnl_id: str
    level_code: str
    employment_type: str
    part_time_ratio: Decimal
    as_of: _date
    year: int
    contract_effective_date: _date
    tax_rule_year: int

    earnings: Earnings
    contributions: Contributions
    taxes: Taxes
    employer_cost: EmployerCost
    coverage: Coverage
    provenance: tuple[RuleProvenance, ...]

    net_annual: Decimal
    net_monthly: Decimal

    schema_version: str = field(default="2")

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain Python dictionary.

        All ``Decimal`` amounts are converted to ``str``.  ``date`` fields are
        ISO-8601 strings.  Sub-objects are serialised as nested dicts.
        ``RuleProvenance`` entries use ``model_dump(mode="json")``.

        Returns:
            A dictionary with only JSON-native types.
        """
        out: dict[str, object] = {}
        for f in dataclasses.fields(self):
            value = getattr(self, f.name)
            out[f.name] = _serialise_value(value)
        return out

    def to_json(self) -> str:
        """Serialise to a JSON string.

        Returns:
            A compact JSON string. See :meth:`to_dict` for encoding rules.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> AnnualEstimate:
        """Reconstruct from a ``to_dict()`` dict.

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`AnnualEstimate` with all fields restored.

        Raises:
            TypeError: If *data* contains unexpected keys.
            ValueError: If a required field is absent from *data*.
        """
        allowed = frozenset(f.name for f in dataclasses.fields(cls))
        extra = set(data) - allowed
        if extra:
            msg = f"AnnualEstimate.from_dict: unexpected keys: {sorted(extra)}"
            raise TypeError(msg)
        hints = typing.get_type_hints(cls)
        kwargs: dict[str, object] = {}
        for f in dataclasses.fields(cls):
            if f.name not in data:
                if _has_default(f):
                    continue
                msg = f"Missing field: {f.name!r}"
                raise ValueError(msg) from None
            kwargs[f.name] = _decode_field(f.name, data[f.name], hints[f.name])
        return cls(**kwargs)  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, raw: str) -> AnnualEstimate:
        """Reconstruct from a JSON string.

        Args:
            raw: A JSON string as returned by :meth:`to_json`.

        Returns:
            A new :class:`AnnualEstimate` equal to the original.
        """
        return cls.from_dict(json.loads(raw))
