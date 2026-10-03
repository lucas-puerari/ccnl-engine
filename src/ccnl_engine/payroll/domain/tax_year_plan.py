"""Public input of every payment actually cashed in one tax year.

Employment income is taxed on a cash basis (TUIR art. 51 c. 1): a tax year
holds the payments made in it, whatever their competence.  With December
2026 paid on 13 January 2027, tax year 2026 holds the eleven months, the
quattordicesima and the tredicesima of 2026, and tax year 2027 opens with
the December of 2026.  A :class:`TaxYearPlan` lists the competence years
whose runs may be paid in the tax year; the payments of the tax year, their
order and the conguaglio are derived from the payment dates.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ccnl_engine.payroll.domain.competence_year_plan import CompetenceYearPlan
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.shared.domain.collection_validation import items_of_type, tuple_of
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import require_instance, require_int

__all__ = ["TaxYearPlan"]

_FEATURE = "tax_year_plan"
_OWNER = "TaxYearPlan"


@dataclass(frozen=True)
class TaxYearPlan:
    """Every payment of one tax year, drawn from its competence years.

    The payments of the tax year are the runs of :attr:`competence_years`
    whose payment date falls in :attr:`tax_year` under the cassa allargata
    rule (paid by 12 January for a period of the year before: that year),
    plus the payments already closed in :attr:`opening_state`.  They are
    computed in order of payment date, ties in run order.  The conguaglio
    (art. 23 c. 3 DPR 600/1973) falls on the last payment of the tax year:
    a late December paid on 13 January comes before the standard runs, a
    late payment in July among them, one paid after the tredicesima after
    them, and the conguaglio follows in every case.

    Attributes:
        tax_year: The tax year.
        competence_years: Plans of the competence years paid in the tax
            year, at most one per year, none after :attr:`tax_year`:
            usually the year before (for a December paid in January) and
            the tax year itself.  Their own ``opening_state`` must be
            ``None``.
        opening_state: State the first payment opens with: ``None`` for a
            new employment, ``close_tax_year()`` of the previous tax year,
            or a state of :attr:`tax_year` that already closed some of the
            payments; those are not computed again (resume after a retry).

    Raises:
        InvalidInputError: When a field is not of its type, there is no
            competence year, two plans share a year, a plan is of a year
            after :attr:`tax_year` or carries an opening state.
    """

    tax_year: int
    competence_years: tuple[CompetenceYearPlan, ...]
    opening_state: PeriodState | None = field(default=None)

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.tax_year,
            f"{_OWNER}.tax_year",
            feature=_FEATURE,
            minimum=1970,
            maximum=9999,
        )
        require_instance(
            self.opening_state,
            PeriodState,
            f"{_OWNER}.opening_state",
            feature=_FEATURE,
            optional=True,
        )
        path = f"{_OWNER}.competence_years"
        plans = tuple_of(
            self.competence_years,
            path,
            items_of_type(CompetenceYearPlan, feature=_FEATURE),
            feature=_FEATURE,
        )
        object.__setattr__(self, "competence_years", plans)
        if not plans:
            msg = "a tax year plan needs at least one competence year"
            raise InvalidInputError(msg, field=path, feature=_FEATURE)
        years = [p.year for p in plans]
        for index, plan in enumerate(plans):
            entry = f"{path}[{index}]"
            if plan.year in years[:index] or plan.year > self.tax_year:
                msg = (
                    f"competence year {plan.year} must appear once and not "
                    f"after the tax year {self.tax_year}"
                )
                raise InvalidInputError(msg, field=entry, feature=_FEATURE)
            if plan.opening_state is not None:
                msg = (
                    "a competence year of a tax year plan carries no opening "
                    "state: set TaxYearPlan.opening_state instead"
                )
                raise InvalidInputError(
                    msg, field=f"{entry}.opening_state", feature=_FEATURE
                )
