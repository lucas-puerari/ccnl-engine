"""The EDAR of the Pulizia artigianato renewal of 27 October 2022 (art. 36).

PDF p. 27 (sha256
037e5a830b9027e280d0a84285afe7c69190550e5704b236270ba6ebd62f6424): 15 EUR a
month "per 26 mesi consecutivi a partire dall'1.11.2022", to the workers in
service on the date of signature, outside the TFR.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl


def test_the_edar_runs_from_november_2022_to_december_2024() -> None:
    """26 months of 15 EUR to the workers in service on 27 October 2022."""
    for level in load_ccnl("pulizia-artigianato-confartigianato").levels:
        (edar,) = (a for a in level.fixed_allowances if a.code == "EDAR")
        assert edar.monthly.value_at(date(2022, 11, 1)) == Decimal(15)
        assert edar.monthly.value_at(date(2024, 12, 1)) == Decimal(15)
        assert not edar.monthly.applies_on(date(2025, 1, 1))
        assert (edar.in_service_on, edar.tfr_relevant, edar.months_per_year) == (
            date(2022, 10, 27),
            False,
            12,
        )
