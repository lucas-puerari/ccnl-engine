"""Default cases of the sickness facts of a CCNL counting several episodes.

Part of
``DEFAULT_CASES``: Metalmeccanico
C3 operaio of CCNL Federmeccanica, whose sick pay counts the episodes of
three years and reduces the fourth short absence of a year (CCNL 5 febbraio
2021, Sez. Quarta, Titolo VI, Art. 2, https://www.fiom-cgil.it/images/CCNL/
INDUSTRIA/2021_02_05-CCNL-federmeccanica.pdf, pp. 196-199).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import SicknessEpisode
from ccnl_engine.inputs import (
    InpsBaseYtd,
    OpeningBalances,
    PeriodState,
    Permanent,
    WorkerCategory,
)
from tests.integration.ccnl_engine.payroll.withholding.builders_withholding import (
    paid_before,
)
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

__all__ = ["sickness_cases"]

_EMPLOYMENT = Employment(
    contract_type=Permanent(),
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    category=WorkerCategory.OPERAIO,
    seniority=new_hire(2025),
)


def _march(opening: PeriodState, *episodes: SicknessEpisode) -> PeriodInput:
    return PeriodInput(
        run=PayrollRun.regular(2026, 3),
        payment_date=date(2026, 3, 27),
        employment=_EMPLOYMENT,
        employer=EmployerProfile(headcount=Headcount(50)),
        facts=PeriodFacts(events=episodes),
        opening_state=opening,
    )


def _short_absences(fourth_exempt: bool | None) -> PeriodInput:
    """Return four two-day absences of March 2026, the fourth's exemption given.

    Returns:
        The March run; the fourth absence of at most five days is reduced
        unless exempt.
    """
    episodes = tuple(
        SicknessEpisode(
            f"S{day}",
            date(2026, 3, day),
            date(2026, 3, day + 1),
            short_absence_exempt=False if day < 23 else fourth_exempt,
        )
        for day in (2, 9, 16, 23)
    )
    return _march(PeriodState.zero(), *episodes)


def _sickness_import(known_from: date | None) -> PeriodInput:
    """Return March 2026 after an import of January and February.

    The worker was hired before 2026: without ``known_from`` the sickness
    of the three previous years is unknown.

    Returns:
        The March run with a twelve-day episode.
    """
    opening = PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            payments=paid_before(PayrollRun.regular(2026, 3)),
            sickness_known_from=known_from,
            inps_bases=(InpsBaseYtd(2026, other_employers=Decimal(0)),),
            recoveries=(),
            surtax_obligations=(),
        )
    )
    episode = SicknessEpisode("M", date(2026, 3, 2), date(2026, 3, 13))
    return _march(opening, episode)


def sickness_cases[C](
    case: Callable[[PeriodInput, PeriodInput, str], C],
) -> Mapping[str, tuple[C, ...]]:
    """Return the cases of the sickness facts, built with ``case``.

    Returns:
        The cases keyed ``Type.field``.
    """
    return {
        "SicknessEpisode.short_absence_exempt": (
            case(
                _short_absences(False),
                _short_absences(None),
                "short_absence_exempt",
            ),
        ),
        "OpeningBalances.sickness_known_from": (
            case(
                _sickness_import(date(2023, 1, 1)),
                _sickness_import(None),
                "sickness_known_from",
            ),
        ),
    }
