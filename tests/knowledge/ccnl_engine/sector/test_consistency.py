"""Check the statutory values the sector files of a year share.

IRPEF, the art. 13 TUIR deductions, the trattamento integrativo, the
ulteriore detrazione, the sterilizzazione and the complementary pension
cap are national: every sector file of a year carries the same values.
The NASpI surcharge of fixed-term contracts and the TFR deductions differ
by sector only where the statute says so, and the provisional year repeats
the values of the year before.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from scripts.provenance.rules import KNOWLEDGE_DIR

_SECTOR = KNOWLEDGE_DIR / "sector"
_YEARS = sorted(path.name for path in _SECTOR.iterdir() if path.is_dir())
_NATIONAL = (
    "irpef_brackets",
    "trattamento_integrativo",
    "ulteriore_detrazione",
    "sterilizzazione_detrazioni",
    "complementary_pension",
)
#: Surcharge and renewal increment of L. 92/2012 art. 2 c. 28: c. 29 lett. d)
#: exempts the public administrations, and the increment does not apply to
#: domestic work (D.L. 87/2018 art. 3 c. 2).
_FIXED_TERM = {
    "pubblica-amministrazione": ("0.000", "0.000"),
    "lavoro-domestico": ("0.014", "0.000"),
}
_FIXED_TERM_DEFAULT = ("0.014", "0.005")
#: Sectors whose TFR deducts the 0.50% of L. 297/1982 art. 3 c. 15 and
#: takes the compensation of D.Lgs. 252/2005 art. 10 (see TfrRules).
_TFR_DEDUCTED = {"artigianato", "credito", "edilizia", "industria", "terziario"}


def _strip(node: object) -> object:
    """Return ``node`` without its provenance records.

    Returns:
        The values alone.
    """
    if isinstance(node, dict):
        return {
            key: _strip(value)
            for key, value in node.items()
            if not key.endswith("provenance")
        }
    if isinstance(node, list):
        return [_strip(item) for item in node]
    return node


def _files(year: str) -> dict[str, dict[str, Any]]:
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((_SECTOR / year).glob("*.json"))
    }


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize("block", _NATIONAL)
def test_national_blocks_agree_across_sectors(year: str, block: str) -> None:
    """Every sector of a year carries the same national values."""
    values = {
        json.dumps(_strip(data[block]), sort_keys=True)
        for data in _files(year).values()
    }
    assert len(values) == 1


@pytest.mark.parametrize("year", _YEARS)
def test_fixed_term_surcharge_follows_the_statute(year: str) -> None:
    """Only the sectors the statute exempts depart from 1.4% and 0.5%."""
    for sector, data in _files(year).items():
        expected = _FIXED_TERM.get(sector, _FIXED_TERM_DEFAULT)
        actual = (
            data["fixed_term_additional_rate"],
            data["fixed_term_renewal_increment"],
        )
        assert actual == expected, sector
        exempt = data.get("fixed_term_exempt_categories", [])
        assert exempt == (["operaio"] if sector == "agricoltura" else []), sector


@pytest.mark.parametrize("year", _YEARS)
def test_tfr_deductions_follow_the_sector(year: str) -> None:
    """The 0.50% and the compensation apply to the sectors of TfrRules."""
    for sector, data in _files(year).items():
        tfr = data["tfr"]
        assert tfr["accrual_divisor"] == "13.5", sector
        deducted = sector in _TFR_DEDUCTED
        assert ("additional_ivs" in tfr) is deducted, sector
        assert ("compensation" in tfr) is deducted, sector


def test_provisional_year_repeats_the_year_before() -> None:
    """The 2027 files carry the 2026 values, marked as estimates."""
    before, after = _files("2026"), _files("2027")
    assert before.keys() == after.keys()
    for sector, data in after.items():
        assert data["ruleset"]["source_type"] == "estimated", sector
        for key, value in data.items():
            if key in {"year", "ruleset", "notes"} or key.endswith("provenance"):
                continue
            assert _strip(value) == _strip(before[sector][key]), (sector, key)


@pytest.mark.parametrize("year", _YEARS)
def test_notes_leave_the_inps_block_to_its_file(year: str) -> None:
    """INPS rates are documented in contribution/<year>/<sector>.json."""
    for sector, data in _files(year).items():
        assert not [n for n in data["notes"] if "kitech" in n or "INPS rates" in n], (
            sector
        )
