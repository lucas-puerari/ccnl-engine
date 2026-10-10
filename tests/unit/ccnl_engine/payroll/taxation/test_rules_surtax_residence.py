"""Surtax decisions of a withholding run that omits the residence.

The regional surtax is due to the region of the domicilio fiscale on 1
January of the tax year (D.Lgs. 446/1997 art. 50 c. 5), the municipal one
to the municipality of the domicilio fiscale on the same date (D.Lgs.
360/1998 art. 1 c. 4): each missing code leaves its surtax undetermined.
"""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.taxation.rules_surtax_residence import (
    RESIDENCE_UNKNOWN,
    residence_unknown_decisions,
)

_REGIONAL = ("addizionale_regionale", "facts.regione", "art. 50 c. 5")
_MUNICIPAL = ("addizionale_comunale", "facts.comune_belfiore", "art. 1 c. 4")


@pytest.mark.parametrize(
    ("regione", "comune_belfiore", "expected"),
    [
        (None, None, (_REGIONAL, _MUNICIPAL)),
        ("IT-88", None, (_MUNICIPAL,)),
        (None, "A192", (_REGIONAL,)),
    ],
)
def test_each_missing_code_leaves_its_surtax_undetermined(
    regione: str | None,
    comune_belfiore: str | None,
    expected: tuple[tuple[str, str, str], ...],
) -> None:
    """One incomplete decision without amount per missing code, fact named."""
    decisions = residence_unknown_decisions(regione, comune_belfiore, 2026)

    assert [
        (d.capability, d.inputs["fact"], d.source.section if d.source else None)
        for d in decisions
    ] == list(expected)
    for decision in decisions:
        assert decision.reason_code == RESIDENCE_UNKNOWN
        assert decision.status is CalculationStatus.INCOMPLETE
        assert decision.amount is None
        assert decision.rule_version == "2026"
        assert decision.inputs["tax_year"] == "2026"
        assert decision.source is not None
        assert "domicilio fiscale" in (decision.source.quote or "")


def test_known_residence_records_nothing() -> None:
    """Both codes supplied: the surtax tables decide, not this rule."""
    assert residence_unknown_decisions("IT-88", "A192", 2026) == ()
