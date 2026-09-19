"""Payroll computation trace: ordered record of gross and fiscal steps."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Literal, cast


class TraceCategory(StrEnum):
    """Semantic category of a single payroll computation step."""

    # --- Gross chain (monthly amounts) ---
    BASE_SALARY = "base_salary"
    SENIORITY = "seniority"
    ALLOWANCE = "allowance"
    AD_PERSONAM = "ad_personam"
    SECOND_LEVEL = "second_level"
    RAL_OVERRIDE = "ral_override"
    GROSS = "gross"
    # Layer 3 supplement steps (sit after GROSS; do not alter its invariant)
    TIME_SUPPLEMENT = "time_supplement"
    SUPPLEMENT_TOTAL = "supplement_total"

    # --- Fiscal chain (annual amounts) ---
    CONTRIBUTION_BASE = "contribution_base"
    INPS_EMPLOYEE = "inps_employee"
    INPS_EMPLOYER = "inps_employer"
    TFR = "tfr"
    EMPLOYER_FUNDS = "employer_funds"
    TAXABLE_INCOME = "taxable_income"
    IRPEF_GROSS = "irpef_gross"
    WORK_DEDUCTION = "work_deduction"
    ULTERIORE_DETRAZIONE = "ulteriore_detrazione"
    FAMILY_DEDUCTION = "family_deduction"
    ART15_DEDUCTION = "art15_deduction"
    STERILIZZAZIONE_CLAWBACK = "sterilizzazione_clawback"
    BILATERAL_EMPLOYEE = "bilateral_employee"
    IRPEF_NET = "irpef_net"
    ADDIZIONALE_REGIONALE = "addizionale_regionale"
    ADDIZIONALE_COMUNALE = "addizionale_comunale"
    TRATTAMENTO_INTEGRATIVO = "trattamento_integrativo"
    SOMMA_ESENTE = "somma_esente"
    NET = "net"


@dataclass(frozen=True)
class TraceStep:
    """One step in a payroll computation chain.

    Attributes:
        category: Semantic category of the step.
        label: Human-readable label (e.g. ``"Base retributiva"``,
            ``"IRPEF netta"``).
        amount: Amount contributed by this step, post-scaling.
            Gross-chain steps are monthly; fiscal-chain steps are annual.
            Check ``period`` to know which applies.
        detail: Optional machine-readable reference (e.g. allowance code,
            ``"scatti=3"``, ``"IV@H011"``).
        period: Whether ``amount`` is a monthly or annual figure.
            Defaults to ``"monthly"`` for backward compatibility with
            serialised gross-chain traces.
    """

    category: TraceCategory
    label: str
    amount: Decimal
    detail: str | None = None
    period: Literal["monthly", "annual"] = "monthly"
    formula: str | None = None
    source: str | None = None
    rounding: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Serialise to a JSON-native dict.

        Returns:
            A dict with ``str``/``None`` values; ``amount`` as its string
            form to avoid floating-point loss.  Optional fields (``formula``,
            ``source``, ``rounding``) are omitted when ``None`` so old readers
            that only check required keys remain compatible.
        """
        out: dict[str, object] = {
            "category": self.category.value,
            "label": self.label,
            "amount": str(self.amount),
            "detail": self.detail,
            "period": self.period,
        }
        if self.formula is not None:
            out["formula"] = self.formula
        if self.source is not None:
            out["source"] = self.source
        if self.rounding is not None:
            out["rounding"] = self.rounding
        return out

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> TraceStep:
        """Reconstruct from a :meth:`to_dict` dict.

        Args:
            data: A dict as produced by :meth:`to_dict`.  Keys ``formula``,
                ``source``, and ``rounding`` are optional for backward
                compatibility with snapshots serialised by older engine
                versions.

        Returns:
            A new :class:`TraceStep` equal to the original.

        Raises:
            TypeError: If ``label`` is not a ``str``.
            ValueError: If ``period`` is not ``'monthly'`` or ``'annual'``.
        """
        raw_detail = data.get("detail")
        raw_formula = data.get("formula")
        raw_source = data.get("source")
        raw_rounding = data.get("rounding")
        label_raw = data["label"]
        if not isinstance(label_raw, str):
            msg = f"TraceStep.label must be str, got {type(label_raw).__name__!r}"
            raise TypeError(msg)
        period_raw = data["period"]
        valid_periods: frozenset[object] = frozenset({"monthly", "annual"})
        if period_raw not in valid_periods:
            msg = f"TraceStep.period must be 'monthly' or 'annual', got {period_raw!r}"
            raise ValueError(msg)
        return cls(
            category=TraceCategory(str(data["category"])),
            label=label_raw,
            amount=Decimal(str(data["amount"])),
            detail=str(raw_detail) if raw_detail is not None else None,
            period=cast(Literal["monthly", "annual"], period_raw),
            formula=str(raw_formula) if raw_formula is not None else None,
            source=str(raw_source) if raw_source is not None else None,
            rounding=str(raw_rounding) if raw_rounding is not None else None,
        )


@dataclass(frozen=True)
class CalculationTrace:
    """Ordered record of the gross and fiscal computation steps.

    **Gross chain** (``steps``): monthly amounts from base salary through to
    the gross total.  The ``GROSS`` step is always last and equals the sum of
    all preceding entries — the engine enforces this invariant at construction
    time.  L3 supplement steps sit in ``supplement_steps`` and do not alter
    the ``GROSS`` invariant.

    **Fiscal chain** (``fiscal_steps``): annual amounts from gross through to
    net.  This is a *derivation* chain, not a sum: each step shows the
    derivation formula rather than a contribution. The canonical identity is::

        net_annual = gross_annual
                   - inps_employee_annual
                   - irpef_net
                   - addizionale_regionale_annual
                   - addizionale_comunale_annual
                   + trattamento_integrativo

    Steps that were omitted (e.g. addizionali when no jurisdiction was
    supplied) are still emitted with ``amount=0`` so the skeleton is stable
    across runs and diffs cleanly.

    Attributes:
        steps: Ordered gross-chain steps (monthly), ending with ``GROSS``.
        supplement_steps: Optional L3 supplement steps (monthly). Empty when
            no supplement input is provided.
        fiscal_steps: Ordered fiscal-chain steps (annual). Empty when not
            yet emitted (pre-2025 serialised calculations).
    """

    steps: tuple[TraceStep, ...]
    supplement_steps: tuple[TraceStep, ...] = dataclasses.field(default=())
    fiscal_steps: tuple[TraceStep, ...] = dataclasses.field(default=())

    def to_dict(self) -> dict[str, object]:
        """Serialise to a JSON-native dict.

        Returns:
            A dict with ``steps``, ``supplement_steps``, and ``fiscal_steps``
            lists.  Empty optional sequences are omitted.
        """
        out: dict[str, object] = {"steps": [s.to_dict() for s in self.steps]}
        if self.supplement_steps:
            out["supplement_steps"] = [s.to_dict() for s in self.supplement_steps]
        if self.fiscal_steps:
            out["fiscal_steps"] = [s.to_dict() for s in self.fiscal_steps]
        return out

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> CalculationTrace:
        """Reconstruct from a :meth:`to_dict` dict.

        Args:
            data: A dict as produced by :meth:`to_dict`.

        Returns:
            A new :class:`CalculationTrace` equal to the original.
        """
        return cls(
            steps=tuple(
                TraceStep.from_dict(cast(dict[str, object], s))
                for s in cast(list[object], data["steps"])
            ),
            supplement_steps=tuple(
                TraceStep.from_dict(cast(dict[str, object], s))
                for s in cast(list[object], data.get("supplement_steps", []))
            ),
            fiscal_steps=tuple(
                TraceStep.from_dict(cast(dict[str, object], s))
                for s in cast(list[object], data.get("fiscal_steps", []))
            ),
        )
