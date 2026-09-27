"""Municipal surtax table built from the MEF CSV lists."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.provenance.domain.ruleset_identity import source_hash
from ccnl_engine.tax.domain.surtax_rules import ComunaleRaw
from scripts.data.build_comunale_surtax import RowError, build, main, parse_row

if TYPE_CHECKING:
    from pathlib import Path

_HEADER = (
    "CODICE_CATASTALE;COMUNE;PR;NUMERO_DELIBERA;DATA_DELIBERA;DATA_PUBBLICAZIONE;"
    "NOTE;MULTIALIQ;"
    + ";".join(f"ALIQUOTA{s};FASCIA{s}" for s in ["", *(f"_{i}" for i in range(2, 13))])
    + ";FLAG_NUOVA;IMPORTO_ESENTE"
)


def _row(
    code: str,
    name: str,
    slots: list[tuple[str, str]],
    flag: str = "0",
    exempt: str = "0",
) -> dict[str, str]:
    row = dict.fromkeys(_HEADER.split(";"), "")
    row.update(CODICE_CATASTALE=code, COMUNE=name, FLAG_NUOVA=flag)
    row["IMPORTO_ESENTE"] = exempt
    for index, (rate, text) in enumerate(slots):
        suffix = "" if index == 0 else f"_{index + 1}"
        row[f"ALIQUOTA{suffix}"] = rate
        row[f"FASCIA{suffix}"] = text
    return row


def _undeliberated(code: str, name: str) -> dict[str, str]:
    return _row(code, name, [("0*", "")], flag="")


class TestParseRow:
    """One delibera of the list becomes brackets and an exemption."""

    def test_single_rate_with_exemption(self) -> None:
        """Flag 2: the exemption amount comes from ``IMPORTO_ESENTE``."""
        row = _row(
            "A006",
            "ABBADIA SAN SALVATORE",
            [
                ("0", "Esenzione per redditi imponibili fino a euro 12.000,00"),
                (",6", "Aliquota unica"),
            ],
            flag="2",
            exempt="12000",
        )
        assert parse_row(row) == {
            "nome": "Abbadia San Salvatore",
            "brackets": [{"up_to": None, "rate": "0.006"}],
            "exemption_threshold": "12000.00",
        }

    def test_free_text_bands_and_exemption(self) -> None:
        """Flag 0: bands and exemption are read from the texts."""
        row = _row(
            "E965",
            "MARNATE",
            [
                ("0,76", "Applicabile a scaglione di reddito fino a € 15000,00"),
                (",77", "Applicabile a da euro 15000,01 FINO A euro 28000,00"),
                (",78", "Applicabile a tra 28.000,01 e 50.000,00"),
                (",8", "Applicabile a scaglione di reddito OLTRE euro 50000,00"),
                ("0", "Esenzione per reddito imponibile fino A euro 13000,00"),
            ],
        )
        assert parse_row(row)["brackets"] == [
            {"up_to": "15000.00", "rate": "0.0076"},
            {"up_to": "28000.00", "rate": "0.0077"},
            {"up_to": "50000.00", "rate": "0.0078"},
            {"up_to": None, "rate": "0.008"},
        ]
        assert parse_row(row)["exemption_threshold"] == "13000.00"

    def test_bands_without_lower_bound_and_mistyped_lower_bound(self) -> None:
        """``fino a N`` bands chain on the upper bounds; ``15.00,00`` is ignored."""
        row = _row(
            "F723",
            "MORETTA",
            [
                ("0,4", "Applicabile a fino a 15000"),
                (",5", "Applicabile a oltre euro 15.00,00 e fino a euro 28.000,00"),
                (",55", "Applicabile a fino a 50000"),
                (",8", "Applicabile a oltre 50000"),
            ],
        )
        assert [b["up_to"] for b in parse_row(row)["brackets"]] == [
            "15000.00",
            "28000.00",
            "50000.00",
            None,
        ]

    def test_category_exemptions_are_kept_as_text(self) -> None:
        """Flag 6: exemptions for a category of income are not a threshold."""
        text = "Esenzione per redditi da lavoro dipendente fino a euro 10.000,00"
        row = _row(
            "D749",
            "FOSSOMBRONE",
            [
                ("0,68", "Applicabile a scaglione di reddito fino a euro 28.000,00"),
                (",8", "Applicabile a scaglione di reddito oltre euro 28.000,00"),
                ("0", text),
            ],
            flag="6",
        )
        entry = parse_row(row)
        assert entry["specific_exemptions"] == [text]
        assert "exemption_threshold" not in entry

    @pytest.mark.parametrize(
        ("slots", "message"),
        [
            ([(",5", "Applicabile a scaglione di reddito")], "cannot read the band"),
            (
                [(",5", "Applicabile a fino a 15000"), (",6", "Applicabile a oltre 9")],
                "starts at 9",
            ),
            (
                [
                    (",5", "Applicabile a fino a 15000"),
                    (",6", "Applicabile a fino a 15000"),
                    (",8", "Applicabile a oltre 15000"),
                ],
                "ends at 15000",
            ),
            ([(",5", "Applicabile a fino a 15000")], "one open-ended band"),
            ([("x", "Aliquota unica")], "not a rate"),
            ([("120", "Aliquota unica")], "out of range"),
            (
                [(",5", "Aliquota unica"), (",6", "Applicabile a oltre 15000")],
                "both a single rate and brackets",
            ),
            ([("0", "Esenzione per redditi imponibili fino a euro")], "no rate"),
        ],
    )
    def test_unreadable_rows_fail(
        self, slots: list[tuple[str, str]], message: str
    ) -> None:
        """A row that cannot be read is an error, never a silent drop."""
        with pytest.raises(RowError, match=message):
            parse_row(_row("Z999", "BROKEN", slots))


def _lists() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    flat = [(",8", "Aliquota unica")]
    current = {
        "A001": _row("A001", "NEW", flat, flag="1"),
        "A002": _undeliberated("A002", "CARRIED"),
        "A003": _undeliberated("A003", "NEVER"),
        "A112": _row(
            "A112",
            "AIRUNO",
            [
                ("0,33", "Applicabile a fino a euro 15.000,00"),
                (",35", "Applicabile a da euro 15.000,01 fino a euro 28.000,00"),
                (",5", "Applicabile a da euro 15.000,01 fino a euro 28.000,00"),
                (",8", "Applicabile a oltre euro 50.000,00"),
            ],
        ),
    }
    previous = {
        "A002": _row("A002", "CARRIED", [(",6", "Aliquota unica")], flag="1"),
        "A003": _undeliberated("A003", "NEVER"),
    }
    return current, previous


def test_build_carries_rows_without_a_delibera() -> None:
    """``0*`` takes the year before, or rate 0 when never instituted."""
    current, previous = _lists()
    payload, errors = build(
        2026, current, previous, retrieved="2026-09-27", digests=("a", "b")
    )

    assert errors == []
    rates = payload["rates"]
    assert "rates_year" not in rates["A001"]
    assert rates["A002"]["rates_year"] == 2025
    assert rates["A002"]["brackets"] == [{"up_to": None, "rate": "0.006"}]
    assert rates["A002"]["provenance"]["status"] == "assumed"
    assert rates["A003"]["brackets"] == [{"up_to": None, "rate": "0"}]
    assert rates["A112"]["brackets"][2] == {"up_to": "50000.00", "rate": "0.005"}
    assert rates["A112"]["provenance"]["status"] == "assumed"
    assert payload["ruleset"]["source_hash"] == source_hash(payload)
    raw = ComunaleRaw.model_validate(payload)
    assert raw.rates_are_advance is False
    assert raw.rates["A002"].rates_year == 2025


def test_build_reports_unreadable_rows() -> None:
    """An unreadable row is reported with its code and name."""
    current = {"Z999": _row("Z999", "BROKEN", [(",5", "Applicabile a fino a 9")])}
    _, errors = build(2026, current, {}, retrieved="2026-09-27", digests=("a", "b"))

    assert errors == ["Z999 BROKEN: expected one open-ended band, got 0"]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [_HEADER, *(";".join(r[k] for k in _HEADER.split(";")) for r in rows)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_main_writes_the_table(tmp_path: Path) -> None:
    """The command line writes a table the loader model accepts."""
    current, previous = _lists()
    _write_csv(tmp_path / "2026.csv", list(current.values()))
    _write_csv(tmp_path / "2025.csv", list(previous.values()))
    out = tmp_path / "comunale-2026.json"

    code = main([
        "--year=2026",
        f"--current={tmp_path / '2026.csv'}",
        f"--previous={tmp_path / '2025.csv'}",
        "--retrieved=2026-09-27",
        f"--out={out}",
    ])

    assert code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert len(payload["rates"]) == 4
    assert "sha256" in payload["notes"][1]


def test_main_fails_without_writing(tmp_path: Path) -> None:
    """A row that cannot be read stops the build before anything is written."""
    _write_csv(
        tmp_path / "2026.csv",
        [_row("Z999", "BROKEN", [(",5", "Applicabile a fino a 9")])],
    )
    _write_csv(tmp_path / "2025.csv", [])
    out = tmp_path / "comunale-2026.json"

    code = main([
        "--year=2026",
        f"--current={tmp_path / '2026.csv'}",
        f"--previous={tmp_path / '2025.csv'}",
        "--retrieved=2026-09-27",
        f"--out={out}",
    ])

    assert code == 1
    assert not out.exists()
