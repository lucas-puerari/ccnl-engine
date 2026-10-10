"""Municipal surtax table built from the MEF CSV lists."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.provenance.ruleset.models import source_hash
from ccnl_engine.tax.surtax.models import ComunaleRaw
from scripts.knowledge.build import (
    BuildOptions,
    RowError,
    Tally,
    build,
    is_inapplicable,
    main,
    parse_row,
    read_list,
)

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
    note: str = "",
) -> dict[str, str]:
    row = dict.fromkeys(_HEADER.split(";"), "")
    row.update(CODICE_CATASTALE=code, COMUNE=name, FLAG_NUOVA=flag, NOTE=note)
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


#: ``NOTE`` of a delibera adopted after the deadline, as in the 2026 list.
_LATE_2026 = "ATTO OLTRE TERMINE - ALIQUOTE INAPPLICABILI PER IL 2026"
#: ``NOTE`` of the same case in the 2025 list.
_LATE_2025 = (
    "INAPPLICABILE PER IL 2025 (ADOTTATA OLTRE TERMINE - ART. 1, C. 750 E 751, "
    "L. 207/2024)"
)
_OPTIONS = BuildOptions(retrieved="2026-10-07", digests=("a", "b"), version="2026.4")


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
    result = build(2026, [current, previous], _OPTIONS)

    assert result.errors == []
    payload = result.payload
    rates = payload["rates"]
    assert "rates_year" not in rates["A001"]
    assert rates["A002"]["rates_year"] == 2025
    assert rates["A002"]["brackets"] == [{"up_to": None, "rate": "0.006"}]
    assert rates["A002"]["provenance"]["status"] == "assumed"
    assert "inapplicable" not in rates["A002"]["provenance"]["transformation"]
    assert rates["A003"] == {
        "nome": "Never",
        "brackets": [{"up_to": None, "rate": "0"}],
        "rates_year": 2025,
        "provenance": rates["A002"]["provenance"],
    }
    assert rates["A112"]["brackets"][2] == {"up_to": "50000.00", "rate": "0.005"}
    assert rates["A112"]["provenance"]["status"] == "assumed"
    assert payload["ruleset"]["version"] == "2026.4"
    assert payload["ruleset"]["source_hash"] == source_hash(payload)
    assert [s["url"][-4:] for s in payload["sources"]] == ["2026", "2025"]
    assert result.tally == Tally(
        deliberated=2, carried=2, inapplicable=0, unresolved=()
    )
    raw = ComunaleRaw.model_validate(payload)
    assert raw.rates_are_advance is False
    assert raw.rates["A002"].rates_year == 2025


def test_inapplicable_delibere_take_the_rates_in_force() -> None:
    """A late delibera is skipped, in the table year and the years before.

    B097 Bova: 2026 delibera marked inapplicable, the 2025 rate 0.5% applies.
    L676 Varco Sabino: ``0*`` in 2026, the 2025 delibera is marked
    inapplicable for 2025, so the 2024 rate 0.4% is still in force.
    """
    current = {
        "B097": _row("B097", "BOVA", [("0,8", "Aliquota unica")], note=_LATE_2026),
        "L676": _undeliberated("L676", "VARCO SABINO"),
    }
    before = {
        "B097": _row("B097", "BOVA", [("0,5", "Aliquota unica")], note="CONFERMA"),
        "L676": _row(
            "L676", "VARCO SABINO", [("0,8", "Aliquota unica")], note=_LATE_2025
        ),
    }
    older = {"L676": _row("L676", "VARCO SABINO", [("0,4", "Aliquota unica")])}
    options = BuildOptions(
        retrieved="2026-10-07", digests=("a", "b", "c"), version="2026.4"
    )

    result = build(2026, [current, before, older], options)

    rates = result.payload["rates"]
    assert (rates["B097"]["rates_year"], rates["B097"]["brackets"]) == (
        2025,
        [{"up_to": None, "rate": "0.005"}],
    )
    assert "listed for 2026" in rates["B097"]["provenance"]["transformation"]
    assert (rates["L676"]["rates_year"], rates["L676"]["brackets"]) == (
        2024,
        [{"up_to": None, "rate": "0.004"}],
    )
    assert "listed for 2025" in rates["L676"]["provenance"]["transformation"]
    assert result.tally.inapplicable == 1
    assert (
        "sha256 elenco 2026: a; elenco 2025: b; elenco 2024: c."
        in (result.payload["notes"])
    )


def test_is_inapplicable_reads_the_note() -> None:
    """Only a delibera marked inapplicable is skipped; a late confirmation is not."""
    late_confirmed = "ATTO OLTRE TERMINE - ALIQUOTE APPLICABILI PER IL 2026 IN QUANTO"
    assert is_inapplicable(_row("A", "A", [], note=_LATE_2026))
    assert is_inapplicable(_row("A", "A", [], note=_LATE_2025))
    assert not is_inapplicable(_row("A", "A", [], note=late_confirmed + " CONFERMATE"))


def test_inapplicable_in_every_list_is_an_error() -> None:
    """Without a list holding the rates in force the row cannot be built."""
    late = _row("B097", "BOVA", [("0,8", "Aliquota unica")], note=_LATE_2026)
    result = build(2026, [{"B097": late}, {"B097": late}], _OPTIONS)

    assert result.errors == [
        "B097 BOVA: no applicable delibera in the lists down to 2025"
    ]


def test_new_municipality_without_a_delibera_is_left_out() -> None:
    """M439 Castegnero Nanto: ``0*`` in 2026 and absent from the 2025 list.

    It was created by merging Castegnero (0.65% in 2025) and Nanto (0.75%):
    rate 0 would be wrong, so the row is left out and named in the notes.
    """
    current = {"M439": _undeliberated("M439", "CASTEGNERO NANTO")}

    result = build(2026, [current, {}], _OPTIONS)

    assert result.errors == []
    assert result.payload["rates"] == {}
    assert result.tally.unresolved == ("M439 Castegnero Nanto",)
    assert any("M439 Castegnero Nanto" in note for note in result.payload["notes"])


def test_build_reports_unreadable_rows() -> None:
    """An unreadable row is reported with its code and name."""
    current = {"Z999": _row("Z999", "BROKEN", [(",5", "Applicabile a fino a 9")])}
    result = build(2026, [current, {}], _OPTIONS)

    assert result.errors == ["Z999 BROKEN: expected one open-ended band, got 0"]


def _write_csv(path: Path, rows: list[dict[str, str]], *, bom: bool = False) -> None:
    lines = [_HEADER, *(";".join(r[k] for k in _HEADER.split(";")) for r in rows)]
    text = "\n".join(lines) + "\n"
    path.write_text(("﻿" if bom else "") + text, encoding="utf-8")


def test_read_list_ignores_a_byte_order_mark(tmp_path: Path) -> None:
    """A BOM before the header does not hide the code column."""
    _write_csv(tmp_path / "2026.csv", [_undeliberated("A001", "ABANO")], bom=True)

    assert list(read_list(tmp_path / "2026.csv")) == ["A001"]


def test_read_list_rejects_a_duplicate_code(tmp_path: Path) -> None:
    """Two rows of one code would make the table depend on their order."""
    row = _undeliberated("A001", "ABANO")
    _write_csv(tmp_path / "2026.csv", [row, row])

    with pytest.raises(ValueError, match="A001 is listed twice"):
        read_list(tmp_path / "2026.csv")


def _main(tmp_path: Path, out: Path) -> int:
    return main([
        "--year=2026",
        f"--current={tmp_path / '2026.csv'}",
        "--previous",
        str(tmp_path / "2025.csv"),
        str(tmp_path / "2024.csv"),
        "--retrieved=2026-10-07",
        "--version=2026.4",
        f"--out={out}",
    ])


def test_main_writes_the_table(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The command line writes a table the loader model accepts."""
    current, previous = _lists()
    merged = _undeliberated("M439", "CASTEGNERO NANTO")
    _write_csv(tmp_path / "2026.csv", [*current.values(), merged])
    _write_csv(tmp_path / "2025.csv", list(previous.values()))
    _write_csv(tmp_path / "2024.csv", [])
    out = tmp_path / "comunale-2026.json"

    assert _main(tmp_path, out) == 0

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert len(payload["rates"]) == 4
    assert payload["notes"][1].count("elenco 20") == 3
    assert "WARNING: no rates for M439 Castegnero Nanto" in capsys.readouterr().err


def test_main_fails_without_writing(tmp_path: Path) -> None:
    """A row that cannot be read stops the build before anything is written."""
    _write_csv(
        tmp_path / "2026.csv",
        [_row("Z999", "BROKEN", [(",5", "Applicabile a fino a 9")])],
    )
    _write_csv(tmp_path / "2025.csv", [])
    _write_csv(tmp_path / "2024.csv", [])
    out = tmp_path / "comunale-2026.json"

    assert _main(tmp_path, out) == 1
    assert not out.exists()
