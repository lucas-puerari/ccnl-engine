"""Check the bundled regional surtax tables against the limits of the statutes.

- D.Lgs. 446/1997 art. 50 c. 3 sets the base rate at 1.23%, and D.Lgs.
  68/2011 art. 6 c. 1 lett. c lets a region raise it by up to 2.1 points
  (3.33%).  L. 191/2009 art. 2 c. 86 adds 0.30 points in a region whose
  health deficit is not covered (Molise in 2026, 3.63%).
- D.Lgs. 68/2011 art. 6 c. 2 allows different rates only by the IRPEF
  brackets: the bundled limits are 15,000, 28,000 and 50,000 EUR, and each
  bracket is taxed at least as much as the one below it.
- Only a region with a special statute (Friuli-Venezia Giulia) sets a rate
  below the base, on the whole income up to a limit.

The values themselves were checked against the MEF Dipartimento delle
Finanze pages of every region on 14 October 2026; these limits keep a later
edit from leaving the range the statutes allow.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

import pytest

from scripts.provenance.rules import KNOWLEDGE_DIR

_YEARS = ("2026", "2027")
_BASE = Decimal("0.0123")
_MAXIMUM = Decimal("0.0333")
_DEFICIT_INCREASE = Decimal("0.0030")
#: Regions whose 2026 rates carry the 0.30 points of L. 191/2009 art. 2 c. 86.
_DEFICIT_REGIONS = {"Molise"}
_SPECIAL_STATUTE = {
    "Friuli-Venezia Giulia",
    "Provincia Autonoma di Bolzano",
    "Provincia Autonoma di Trento",
    "Sardegna",
    "Sicilia",
    "Valle d'Aosta",
}
_LIMITS = {Decimal(15_000), Decimal(28_000), Decimal(50_000)}


def _rates(year: str) -> dict[str, dict[str, Any]]:
    path = KNOWLEDGE_DIR / "surtax" / "regional" / f"{year}.json"
    rates: dict[str, dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))[
        "rates"
    ]
    return rates


@pytest.mark.parametrize("year", _YEARS)
def test_every_region_and_autonomous_province_is_bundled(year: str) -> None:
    """Nineteen regions and the two autonomous provinces."""
    assert len(_rates(year)) == 21


@pytest.mark.parametrize("year", _YEARS)
def test_bracket_rates_stay_within_the_statutory_range(year: str) -> None:
    """From 1.23% to 3.33%, plus 0.30 points in a region with a deficit."""
    for region, table in _rates(year).items():
        ceiling = _MAXIMUM + (
            _DEFICIT_INCREASE if region in _DEFICIT_REGIONS else Decimal(0)
        )
        for bracket in table["brackets"]:
            assert _BASE <= Decimal(bracket["rate"]) <= ceiling, region


@pytest.mark.parametrize("year", _YEARS)
def test_brackets_follow_the_irpef_limits_and_rise(year: str) -> None:
    """Limits of 15,000, 28,000 and 50,000; the last is open; rates rise."""
    for region, table in _rates(year).items():
        brackets = table["brackets"]
        limits = [Decimal(b["up_to"]) for b in brackets[:-1]]
        rates = [Decimal(b["rate"]) for b in brackets]
        assert brackets[-1]["up_to"] is None, region
        assert set(limits) <= _LIMITS, region
        assert limits == sorted(set(limits)), region
        assert rates == sorted(rates), region


@pytest.mark.parametrize("year", _YEARS)
def test_only_a_special_statute_goes_below_the_base(year: str) -> None:
    """A whole-income rate under 1.23% belongs to a special statute region."""
    below = {
        region
        for region, table in _rates(year).items()
        if Decimal((table.get("whole_income_rate") or {}).get("rate", _BASE)) < _BASE
    }

    assert below <= _SPECIAL_STATUTE
    assert below == {"Friuli-Venezia Giulia"}


def test_the_provisional_year_repeats_the_published_one() -> None:
    """2027 carries the 2026 tables until the regions publish theirs."""

    def values(table: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in table.items() if key != "provenance"}

    published, provisional = _rates("2026"), _rates("2027")
    assert {region: values(t) for region, t in provisional.items()} == {
        region: values(t) for region, t in published.items()
    }
