"""The lavoro supplementare of the Studi professionali (Art. 42 c. 3).

"Le ore di lavoro supplementare verranno retribuite con la quota oraria
della retribuzione di fatto e la maggiorazione forfetaria convenzionalmente
determinata nella misura del 40%".
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.working_time.models import WorkKind


def test_the_supplementary_hours_take_40_percent() -> None:
    """One band for the part-time supplementary hours, from the 2024 text."""
    work = load_ccnl("studi-professionali-confprofessioni").work_rules
    assert work is not None
    assert work.time_supplements is not None
    (band,) = [
        b
        for b in work.time_supplements.overtime_bands
        if WorkKind.SUPPLEMENTARE in b.applies_to_kinds
    ]

    assert band.rate.value_at(date(2024, 3, 1)) == Decimal("0.40")
