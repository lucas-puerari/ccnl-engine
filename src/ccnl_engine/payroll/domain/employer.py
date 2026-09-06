"""Employer-side input model for the payroll computation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.ccnl import SupplementaryAllowance


@dataclass(frozen=True)
class Employer:
    """Employer-side inputs for the payroll computation (see ``compute``).

    Attributes:
        second_level_allowances: Allowances from a territorial or company
            second-level agreement (*contrattazione di secondo livello*).
            Each item is a
            :class:`~ccnl_engine.contract.domain.ccnl.SupplementaryAllowance`
            carrying a plain monthly amount, relevance flags, and an optional
            ``months_per_year`` override.  Every item is scaled by
            ``part_time_pct``; whether the apprenticeship percentage also
            applies is controlled per-item by
            ``apprenticeship_pct_relevant``.

            Mutually exclusive with
            :attr:`~ccnl_engine.payroll.domain.employee.SalaryOverrides\
.ral_override`: a negotiated RAL already expresses the full agreed salary,
            and adding second-level items on top would double-count.  The
            guard is enforced at compute time (the two objects live at
            different call sites).
    """

    second_level_allowances: tuple[SupplementaryAllowance, ...] = ()
