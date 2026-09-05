"""Payslip — the output record of compute()."""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from datetime import date as _date
from decimal import Decimal

from ccnl_engine.models.fiscal import FiscalSimplification


@dataclass(frozen=True)
class Payslip:
    """Full gross-to-net and employer-cost breakdown for one payroll computation.

    Monthly components (``base_monthly``, ``seniority_monthly``,
    ``allowances_monthly``, ``ad_personam_monthly``) are already scaled by
    ``part_time_pct`` and sum to ``gross_monthly``.

    All ``Decimal`` amounts are in EUR. Annual figures assume the contract-wide
    ``additional_months`` pay structure (typically 13 or 14 months).

    Attributes:
        ccnl_id: Identifier of the CCNL used (from ``CCNLMeta.id``).
        level_code: Classification level code used for the computation.
        employment_type: String tag of the employment type
            (``"permanent"``, ``"fixed_term"``, or ``"apprentice"``).
        part_time_pct: Part-time coefficient applied to gross and
            contribution bases. ``1`` for a full-time worker.
        as_of: Reference date used to resolve all time-series values.
        year: Calendar year derived from ``as_of``; used to select IRPEF
            brackets and contribution rules.

        seniority_count: Number of seniority increments (*scatti di
            anzianità*) applied. ``0`` when no seniority applies.
        base_monthly: Base monthly pay from the CCNL table, scaled by
            ``part_time_pct``.
        seniority_monthly: Monthly seniority increment amount, scaled by
            ``part_time_pct``.
        allowances_monthly: Sum of all applicable fixed monthly allowances,
            scaled by ``part_time_pct``.
        ad_personam_monthly: Individual frozen monthly element (e.g.
            pre-abolition seniority) added directly to gross, **not** scaled
            by ``part_time_pct``.
        gross_monthly: Total monthly gross pay (sum of the four monthly
            components above).
        gross_annual: Annual gross pay, accounting for additional months
            (``gross_monthly * additional_months``).
        hourly_rate: Hourly gross rate derived from the contractual weekly
            hours and the standard number of months per year.

        apprenticeship_pct: Percentage applied to destination-level pay for
            percentage-track apprentices (e.g. ``Decimal("0.80")``). ``None``
            for non-apprentice or under-classification contracts.
        apprenticeship_under_level_code: Destination level code for
            under-classification apprentices. ``None`` otherwise.

        inps_employee_annual: Employee INPS contribution for the year.
        inps_employer_annual: Employer INPS contribution for the year,
            including any NASpI addizionale for fixed-term contracts.
        employer_funds_annual: Employer contribution to contractual funds
            (e.g. Cassa Edile, Fondapi) for the year.
        tfr_annual: TFR (*Trattamento di Fine Rapporto*) accrual for the
            year (Art. 2120 c.c.).

        taxable_income: IRPEF taxable base (``gross_annual``
            minus ``inps_employee_annual``).
        irpef_gross: IRPEF before work-income deduction (Art. 11 TUIR).
        work_income_deduction: Work-income tax deduction (Art. 13 TUIR).
        irpef_net: IRPEF actually withheld (``irpef_gross``
            minus ``work_income_deduction``, floored at zero).
        employer_withholds_irpef: ``False`` when the employer is not a
            *sostituto d'imposta* (e.g. lavoro domestico); in that case
            ``irpef_gross`` and ``work_income_deduction`` are informational
            only and ``irpef_net`` is zero.

        addizionale_regionale_annual: Annual addizionale regionale IRPEF
            (Art. 50 TUIR), computed from the regional marginal bracket table.
            Zero when ``Scenario.regione`` is ``None`` or no
            :class:`~ccnl_engine.surtax.models.SurtaxRules` was passed to
            :func:`~ccnl_engine.engine.compute.compute`.
        addizionale_comunale_annual: Annual addizionale comunale IRPEF
            (Art. 1 D.Lgs. 360/1998), computed from the municipal bracket
            table and exemption threshold.  Zero when
            ``Scenario.comune_belfiore`` is ``None`` or no
            :class:`~ccnl_engine.surtax.models.SurtaxRules` was passed.

        trattamento_integrativo: Trattamento integrativo bonus (Art. 1 D.L.
            3/2020), if computed; ``0`` when not applicable or when the tax
            data file does not carry the required parameters.
        fiscal_simplifications: Set of fiscal elements omitted from this
            computation. Callers can check membership to know which items are
            absent from the net figure.

        net_annual: Annual net pay (``gross_annual`` minus
            ``inps_employee_annual`` minus ``irpef_net`` minus
            ``addizionale_regionale_annual`` minus
            ``addizionale_comunale_annual`` plus ``trattamento_integrativo``).
        net_monthly: Monthly net pay (``net_annual / additional_months``).

        employer_cost_annual: Total annual employer cost
            (``gross_annual`` + ``inps_employer_annual``
            + ``employer_funds_annual`` + ``tfr_annual``).
    """

    ccnl_id: str
    level_code: str
    employment_type: str
    part_time_pct: Decimal
    as_of: _date
    year: int

    seniority_count: int
    base_monthly: Decimal
    seniority_monthly: Decimal
    allowances_monthly: Decimal
    ad_personam_monthly: Decimal
    gross_monthly: Decimal
    gross_annual: Decimal
    hourly_rate: Decimal

    apprenticeship_pct: Decimal | None
    apprenticeship_under_level_code: str | None

    inps_employee_annual: Decimal
    inps_employer_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal

    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    irpef_net: Decimal
    employer_withholds_irpef: bool

    addizionale_regionale_annual: Decimal
    addizionale_comunale_annual: Decimal

    trattamento_integrativo: Decimal
    fiscal_simplifications: frozenset[FiscalSimplification]

    net_annual: Decimal
    net_monthly: Decimal

    employer_cost_annual: Decimal

    def to_dict(self) -> dict[str, object]:
        """Serialise the payslip to a plain Python dictionary.

        All ``Decimal`` amounts are converted to ``str`` to avoid floating-point
        loss. ``date`` is serialised as an ISO-8601 string. ``frozenset`` fields
        are converted to sorted lists of strings for deterministic output.

        Returns:
            A dictionary with only JSON-native types (``str``, ``int``, ``bool``,
            ``list``, ``None``).
        """
        out: dict[str, object] = {}
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if isinstance(value, Decimal):
                out[field.name] = str(value)
            elif isinstance(value, _date):
                out[field.name] = value.isoformat()
            elif isinstance(value, frozenset):
                out[field.name] = sorted(str(v) for v in value)
            else:
                out[field.name] = value
        return out

    def to_json(self) -> str:
        """Serialise the payslip to a JSON string.

        Returns:
            A compact JSON string. See :meth:`to_dict` for the encoding rules.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Payslip:
        """Reconstruct a :class:`Payslip` from a dictionary produced by :meth:`to_dict`.

        Args:
            data: A dictionary as returned by :meth:`to_dict`.

        Returns:
            A new :class:`Payslip` with all fields restored to their original types.
        """
        field_types = {f.name: f.type for f in dataclasses.fields(cls)}
        kwargs: dict[str, object] = {}
        for field in dataclasses.fields(cls):
            raw = data[field.name]
            hint = field_types[field.name]
            # Resolve the field type by name; TYPE_CHECKING-guarded hints are
            # stored as strings when from __future__ import annotations is active.
            if hint in {"Decimal", "Decimal | None"}:
                kwargs[field.name] = Decimal(raw) if raw is not None else None  # type: ignore[arg-type]
            elif hint in {"date", "_date"}:
                kwargs[field.name] = _date.fromisoformat(raw)  # type: ignore[arg-type]
            elif hint == "frozenset[FiscalSimplification]":
                kwargs[field.name] = frozenset(
                    FiscalSimplification(v)
                    for v in raw  # type: ignore[attr-defined]
                )
            else:
                kwargs[field.name] = raw
        return cls(**kwargs)  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, raw: str) -> Payslip:
        """Reconstruct a :class:`Payslip` from a JSON string.

        Args:
            raw: A JSON string as returned by :meth:`to_json`.

        Returns:
            A new :class:`Payslip` with all fields restored to their original types.
        """
        return cls.from_dict(json.loads(raw))
