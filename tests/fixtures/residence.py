"""Residence of a worker for requests whose subject is not the surtax.

A withholding run without ``regione`` or ``comune_belfiore`` records a
``residence_unknown`` surtax decision and is incomplete, so a test that
checks the status of another capability states the residence.  Alghero
(Belfiore A192, Sardegna IT-88) is the residence of
:mod:`tests.fixtures.explicit_facts`: its row of ``comunale-2026.json``
holds the 2026 rates (no ``rates_year``) with no exemption for a category
of income, so on a conguaglio its municipal decision is neither
``prior_year_rates_applied`` nor ``specific_exemptions_not_applied``.
"""

from __future__ import annotations

from dataclasses import replace

from ccnl_engine import PeriodFacts

__all__ = ["COMUNE_BELFIORE", "REGIONE", "resident"]

#: Sardegna, ISO 3166-2:IT.
REGIONE = "IT-88"
#: Alghero, codice catastale.
COMUNE_BELFIORE = "A192"


def resident(facts: PeriodFacts | None = None) -> PeriodFacts:
    """Return ``facts`` with the worker resident in Alghero.

    Returns:
        A copy of ``facts`` (empty facts when ``None``) with ``regione``
        and ``comune_belfiore`` set.
    """
    return replace(
        facts or PeriodFacts(), regione=REGIONE, comune_belfiore=COMUNE_BELFIORE
    )
