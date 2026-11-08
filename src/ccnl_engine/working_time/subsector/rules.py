"""The time-supplement bands of the sub-sector and category of the run.

Some CCNL set their overtime, night and holiday premiums by industry and
category: Alimentari art. 31 prints a table for each sub-sector (vini,
bevande, conserve vegetali...) with the operai apart from the intermedi
and the impiegati.  A band naming sub-sectors applies only to an employer
of one of them (``EmployerProfile.subsector``), a band naming categories
only to a worker of one of them.  When the employer does not state the
sub-sector, the run is priced with the first sub-sector the bands name (the
first table of the CCNL) and names the missing fact.  The supplement bands
of ordinary night, holiday and shift hours follow the same rule.

The levels follow the sub-sector too: a level with ``Level.subsectors``
exists only for an employer of one of them, and a run keeps only the levels
of the stated sub-sector and of every sub-sector (``levels_for``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.compensation.ladder.rules import levels_for
from ccnl_engine.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.working_time.models import OvertimeBand
    from ccnl_engine.working_time.supplement.models import SupplementBand

__all__ = ["subsectors_of", "with_subsector"]


def subsectors_of(ccnl: CCNL) -> frozenset[str]:
    """Return the sub-sectors the time bands and permits of ``ccnl`` name.

    Returns:
        Every sub-sector code of the overtime and supplement bands, of the
        week absorptions and yearly hours of the permits and of the pay
        tables and sub-sector levels, empty when none names one.
    """
    rules = ccnl.work_rules
    supplements = None if rules is None else rules.time_supplements
    bands: tuple[OvertimeBand | SupplementBand, ...] = (
        ()
        if supplements is None
        else (*supplements.overtime_bands, *supplements.supplement_bands)
    )
    leave = None if rules is None else rules.leave_rules
    permits = () if leave is None else leave.permits
    absorbed = {
        code for p in permits for a in p.week_absorption for code in a.subsectors
    }
    tiers = {code for p in permits for h in p.annual_hours for code in h.subsectors}
    named = {code for band in bands for code in band.subsectors}
    named |= set(() if rules is None else rules.subsector_rules)
    tables = {
        code
        for level in ccnl.levels
        for code in (*level.base_salary_by_subsector, *level.subsectors)
    }
    return frozenset(named | absorbed | tiers | tables)


def with_subsector(
    ccnl: CCNL,
    subsector: str | None,
    category: WorkerCategory | None,
    *,
    level_code: str | None = None,
) -> tuple[CCNL, bool]:
    """Return the CCNL with the overtime bands and levels of the run only.

    Args:
        ccnl: The CCNL of the run.
        subsector: ``EmployerProfile.subsector``.
        category: Category of the worker, ``None`` when not known.
        level_code: ``Employment.level_code``, checked against the
            sub-sectors its level exists in; ``None`` skips the check.

    Returns:
        The CCNL, unchanged when no band names a sub-sector or a category,
        and whether the sub-sector is not stated, the run then priced with
        the first one the bands name.

    Raises:
        InvalidInputError: When ``subsector`` is not one the CCNL names, the
            level exists only for other sub-sectors, or the bands differ by
            category and ``category`` is not known.
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
    _check_level(ccnl, subsector, level_code)
    ccnl = _with_sector_rules(_with_levels(ccnl, subsector), subsector, category)
    rules = ccnl.work_rules
    supplements = None if rules is None else rules.time_supplements
    bands: tuple[OvertimeBand | SupplementBand, ...] = (
        ()
        if supplements is None
        else (*supplements.overtime_bands, *supplements.supplement_bands)
    )
    if (
        rules is None
        or supplements is None
        or not any(b.subsectors or b.categories for b in bands)
    ):
        return ccnl, False
    first = next((b.subsectors[0] for b in bands if b.subsectors), None)
    stated = subsector if subsector is not None else first
    if category is None and any(b.categories and stated in b.subsectors for b in bands):
        msg = (
            f"the overtime of sub-sector {stated!r} of {ccnl.meta.ccnl_id} "
            "differs by category: state Employment.category"
        )
        raise InvalidInputError(msg, field="Employment.category", feature="overtime")
    supplements = supplements.model_copy(
        update={
            "overtime_bands": tuple(
                b for b in supplements.overtime_bands if _applies(b, stated, category)
            ),
            "supplement_bands": tuple(
                b for b in supplements.supplement_bands if _applies(b, stated, category)
            ),
        }
    )
    work = rules.model_copy(update={"time_supplements": supplements})
    return ccnl.model_copy(update={"work_rules": work}), bool(known) and not subsector


def _applies(
    band: OvertimeBand | SupplementBand,
    subsector: str | None,
    category: WorkerCategory | None,
) -> bool:
    """Return whether ``band`` applies to the sub-sector and category.

    Returns:
        ``True`` when it names neither, or names the stated ones.
    """
    return (not band.subsectors or subsector in band.subsectors) and (
        not band.categories or category in band.categories
    )


def _check_level(ccnl: CCNL, subsector: str | None, level_code: str | None) -> None:
    """Raise when the level of the run exists only for other sub-sectors.

    Raises:
        InvalidInputError: On ``EmployerProfile.subsector`` when no
            sub-sector is stated, on ``Employment.level_code`` when another is.
    """
    level = next((lv for lv in ccnl.levels if lv.code == level_code), None)
    if level is None or not level.subsectors or subsector in level.subsectors:
        return
    only = f"level {level.code!r} of {ccnl.meta.ccnl_id} exists only for the "
    only += f"sub-sectors {list(level.subsectors)}"
    if subsector is None:
        msg = f"{only}: state EmployerProfile.subsector"
        field = "EmployerProfile.subsector"
    else:
        msg = f"{only}, not for {subsector!r}"
        field = "Employment.level_code"
    raise InvalidInputError(msg, field=field, feature="employer_facts")


def _with_levels(ccnl: CCNL, subsector: str | None) -> CCNL:
    """Return the CCNL with the levels and base salary of the sub-sector.

    A level of other sub-sectors is dropped; a level whose
    ``base_salary_by_subsector`` names the stated sub-sector is paid that
    table (Pubblici esercizi art. 162: the paga base of the aziende minori);
    without a stated sub-sector the levels keep their own table.

    Returns:
        The CCNL, unchanged when no level depends on the sub-sector.
    """
    if not any(
        level.subsectors or subsector in level.base_salary_by_subsector
        for level in ccnl.levels
    ):
        return ccnl
    levels = tuple(
        level.model_copy(
            update={"base_salary": level.base_salary_by_subsector[subsector]}
        )
        if subsector is not None and subsector in level.base_salary_by_subsector
        else level
        for level in levels_for(ccnl.levels, subsector)
    )
    return ccnl.model_copy(update={"levels": levels})


def _with_sector_rules(
    ccnl: CCNL, subsector: str | None, category: WorkerCategory | None
) -> CCNL:
    """Return the CCNL with the seniority and apprenticeship of the sub-sector.

    Tessile-moda artigianato art. 67-68: the chimica and ceramica sectors
    have their own increments and apprenticeship tables.  The increments of
    ``seniority_increments_by_subsector`` replace the CCNL's; the
    apprenticeship tracks naming the sub-sector replace those naming none.

    Returns:
        The CCNL, unchanged when neither depends on the sub-sector.
    """
    parameters = ccnl.parameters
    own = parameters.seniority_increments_by_subsector.get(subsector or "")
    named = [t for t in ccnl.apprenticeship if subsector in t.subsectors]
    tracks = tuple(named or [t for t in ccnl.apprenticeship if not t.subsectors])
    work = ccnl.work_rules
    rules = None if work is None else work.subsector_rules.get(subsector or "")
    if own is None and rules is None and tracks == ccnl.apprenticeship:
        return ccnl
    changed: dict[str, object] = {}
    if own is not None:
        changed["seniority_increments"] = own
    if rules is not None and category in rules.hourly_divisor_by_category:
        changed["hourly_divisor"] = rules.hourly_divisor_by_category[category]
    update: dict[str, object] = {
        "apprenticeship": tracks,
        "parameters": parameters.model_copy(update=changed),
    }
    if work is not None and rules is not None and rules.sickness_rules is not None:
        update["work_rules"] = work.model_copy(
            update={"sickness_rules": rules.sickness_rules}
        )
    return ccnl.model_copy(update=update)
