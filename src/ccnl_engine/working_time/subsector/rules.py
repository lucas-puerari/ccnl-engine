"""The time-supplement bands of the sub-sector and category of the run.

Some CCNL set their overtime, night and holiday premiums by industry and
category: Alimentari art. 31 prints a table for each sub-sector (vini,
bevande, conserve vegetali...) with the operai apart from the intermedi
and the impiegati.  A band naming sub-sectors applies only to an employer
of one of them (``EmployerProfile.subsector``), a band naming categories
only to a worker of one of them.  When the employer does not state the
sub-sector, the run is priced with the first sub-sector the bands name (the
first table of the CCNL) and names the missing fact.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.working_time.models import OvertimeBand

__all__ = ["subsectors_of", "with_subsector"]


def subsectors_of(ccnl: CCNL) -> frozenset[str]:
    """Return the sub-sectors the overtime bands of ``ccnl`` name.

    Returns:
        Every sub-sector code of the bands, empty when none names one.
    """
    rules = ccnl.work_rules
    supplements = None if rules is None else rules.time_supplements
    bands = () if supplements is None else supplements.overtime_bands
    return frozenset(code for band in bands for code in band.subsectors)


def with_subsector(
    ccnl: CCNL, subsector: str | None, category: WorkerCategory | None
) -> tuple[CCNL, bool]:
    """Return the CCNL with the overtime bands of the run only.

    Args:
        ccnl: The CCNL of the run.
        subsector: ``EmployerProfile.subsector``.
        category: Category of the worker, ``None`` when not known.

    Returns:
        The CCNL, unchanged when no band names a sub-sector or a category,
        and whether the sub-sector is not stated, the run then priced with
        the first one the bands name.

    Raises:
        InvalidInputError: When ``subsector`` is not one the CCNL names, or
            its bands differ by category and ``category`` is not known.
    """
    known = subsectors_of(ccnl)
    if subsector is not None and subsector not in known:
        msg = (
            f"EmployerProfile.subsector {subsector!r} is not a sub-sector of "
            f"{ccnl.meta.ccnl_id}; expected one of {sorted(known)}"
        )
        raise InvalidInputError(
            msg, field="EmployerProfile.subsector", feature="employer_facts"
        )
    rules = ccnl.work_rules
    supplements = None if rules is None else rules.time_supplements
    if (
        rules is None
        or supplements is None
        or not any(b.subsectors or b.categories for b in supplements.overtime_bands)
    ):
        return ccnl, False
    first = next(
        (b.subsectors[0] for b in supplements.overtime_bands if b.subsectors), None
    )
    stated = subsector if subsector is not None else first
    if category is None and any(
        b.categories and stated in b.subsectors for b in supplements.overtime_bands
    ):
        msg = (
            f"the overtime of sub-sector {stated!r} of {ccnl.meta.ccnl_id} "
            "differs by category: state Employment.category"
        )
        raise InvalidInputError(msg, field="Employment.category", feature="overtime")
    kept = tuple(b for b in supplements.overtime_bands if _applies(b, stated, category))
    supplements = supplements.model_copy(update={"overtime_bands": kept})
    work = rules.model_copy(update={"time_supplements": supplements})
    return ccnl.model_copy(update={"work_rules": work}), bool(known) and not subsector


def _applies(
    band: OvertimeBand, subsector: str | None, category: WorkerCategory | None
) -> bool:
    """Return whether ``band`` applies to the sub-sector and category.

    Returns:
        ``True`` when it names neither, or names the stated ones.
    """
    return (not band.subsectors or subsector in band.subsectors) and (
        not band.categories or category in band.categories
    )
