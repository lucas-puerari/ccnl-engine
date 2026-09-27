r"""Build ``comunale-{year}.json`` from the MEF lists of the addizionale comunale.

The MEF Dipartimento delle Finanze publishes one CSV per tax year with the
rates and exemption deliberated by every municipality, updated daily:

    https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/
    fiscalitalocale/addirpef_newDF/download/download.php?anno=YYYY

(index page ``.../addirpef_newDF/download/tabella.htm``).  Until 20 December
of the year the list shows ``0*`` for a municipality that has not yet
published a delibera for the year.  Without a new delibera the rates of the
year before stay in force (art. 1 c. 169 L. 296/2006), so such a row takes
the row of the list of the year before, with ``rates_year`` set to that
year and an ``assumed`` provenance: the engine applies them as provisional.
A municipality that is ``0*`` in both lists has no surtax (rate 0).

Each row becomes marginal brackets, an exemption threshold and, when the
delibera exempts only a category of income (``FLAG_NUOVA`` 5 and 6, or an
exemption text of that kind), the published texts in
``specific_exemptions``, which the engine does not compute.  A row whose
brackets cannot be read stops the build: nothing is dropped silently.

The script is deterministic for given CSV files; their sha256 digests and
the retrieval date are written into the file.

Usage::

    curl -o 2026.csv '<download.php?anno=2026>'
    curl -o 2025.csv '<download.php?anno=2025>'
    uv run python scripts/data/build_comunale_surtax.py \
        --year 2026 --current 2026.csv --previous 2025.csv \
        --retrieved 2026-09-27
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ccnl_engine.provenance.domain.ruleset_identity import source_hash

DATA_DIR: Final = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "ccnl_engine"
    / "knowledge"
    / "surtax"
    / "data"
)
INDEX_URL: Final = (
    "https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/"
    "fiscalitalocale/addirpef_newDF/download/tabella.htm"
)
DOWNLOAD_URL: Final = (
    "https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/"
    "fiscalitalocale/addirpef_newDF/download/download.php?anno={year}"
)
NOT_DELIBERATED: Final = "0*"
SPECIFIC_FLAGS: Final = frozenset({"5", "6"})
_SLOTS: Final = ("", *(f"_{i}" for i in range(2, 13)))
_NUMBER: Final = re.compile(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?")
#: An exemption of every taxpayer up to an amount, typos of the list included
#: ("redditi imponbili finoa euro 7.500.00", "fino a 10.000,00", "15.000").
_GENERIC_EXEMPTION: Final = re.compile(
    r"esenzione per (?:(?:i )?reddit[oi](?: impon\w*)? )?(?:(?:fino|sino) ?ad? )?"
    r"(?:euro|€)?\s*[\d.,]+\s*(?:euro)?$"
)
#: Rows of the list whose bracket texts are inconsistent, with the corrected
#: texts.  Each correction is applied with an ``assumed`` record.
CORRECTIONS: Final[dict[tuple[int, str], dict[str, str]]] = {
    (2026, "A112"): {
        "FASCIA_3": "Applicabile a scaglione di reddito da euro 28.000,01 fino a "
        "euro 50.000,00",
    },
    (2026, "A785"): {
        "FASCIA_3": "Applicabile a scaglione di reddito da euro 28.000,01 fino a "
        "euro 50.000,00",
    },
}
_CORRECTION_NOTE: Final = (
    "The MEF list repeats the band 15,000.01-28,000 for the third rate while "
    "the fourth starts over 50,000; the third band is read as "
    "28,000.01-50,000."
)
_CENT: Final = Decimal("0.01")
_EURO: Final = Decimal(1)
_HUNDRED: Final = Decimal(100)
_RANGE: Final = 2


class RowError(ValueError):
    """A CSV row whose rates cannot be read."""


@dataclass(frozen=True)
class _Band:
    """Income band of one bracket; ``lower`` is ``None`` when not stated."""

    lower: Decimal | None
    upper: Decimal | None
    rate: Decimal


def _amount(text: str) -> Decimal:
    """Parse an Italian or plain amount: ``15.000,00``, ``15000``, ``15000.5``.

    Returns:
        The amount in euro.

    Raises:
        RowError: When ``text`` is not an amount.
    """
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", text):
        text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        msg = f"not an amount: {text!r}"
        raise RowError(msg) from exc


def _rate(text: str) -> Decimal:
    """Parse a percentage such as ``0,8`` or ``,45`` into a decimal rate.

    Returns:
        The rate as a fraction (``0.008`` for 0.8%).

    Raises:
        RowError: When ``text`` is not a percentage in [0, 100].
    """
    value = text.strip().replace(",", ".")
    if value.startswith("."):
        value = "0" + value
    try:
        percent = Decimal(value)
    except InvalidOperation as exc:
        msg = f"not a rate: {text!r}"
        raise RowError(msg) from exc
    if not Decimal(0) <= percent <= _HUNDRED:
        msg = f"rate out of range: {text!r}"
        raise RowError(msg)
    return (percent / _HUNDRED).normalize()


def _numbers(text: str) -> list[Decimal]:
    return [_amount(m) for m in _NUMBER.findall(text.replace("€", " "))]


def _band(rate: Decimal, text: str) -> _Band:
    """Read the income band of one bracket description.

    The upper bound is the last amount of a range (``da N fino a M``,
    ``tra N e M``, ``N-M``) or the only amount of ``fino a M``; a single
    amount after ``oltre`` or ``da`` opens the last band.  The lower bound
    is kept only when the range has exactly two amounts, to check that the
    bands are contiguous; a mistyped lower bound (``15.00,00``) yields more
    amounts and is not used.

    Returns:
        The band.

    Raises:
        RowError: When the text has no amount.
    """
    numbers = _numbers(text)
    if not numbers:
        msg = f"cannot read the band of {text!r}"
        raise RowError(msg)
    if len(numbers) == 1:
        if re.search(r"\b(?:oltre|da|dal|superiori)\b", text):
            return _Band(numbers[0], None, rate)
        return _Band(None, numbers[0], rate)
    lower = numbers[0] if len(numbers) == _RANGE else None
    return _Band(lower, numbers[-1], rate)


def _brackets(bands: list[_Band]) -> list[dict[str, str | None]]:
    """Turn the bands of a delibera into marginal brackets.

    Returns:
        Brackets with ``up_to`` (``None`` for the last) and ``rate``.

    Raises:
        RowError: When more than one band is open-ended, the upper bounds
            are not strictly ascending, or a stated lower bound is more than
            one euro away from the upper bound of the band before.
    """
    bounded = sorted((b for b in bands if b.upper is not None), key=_upper)
    open_ended = [b for b in bands if b.upper is None]
    if len(open_ended) != 1:
        msg = f"expected one open-ended band, got {len(open_ended)}"
        raise RowError(msg)
    ordered = [*bounded, *open_ended]
    previous = Decimal(0)
    out: list[dict[str, str | None]] = []
    for index, band in enumerate(ordered):
        if band.lower is not None and abs(band.lower - previous) > _EURO:
            msg = f"band {index} starts at {band.lower}, expected {previous}"
            raise RowError(msg)
        if band.upper is None:
            out.append({"up_to": None, "rate": str(band.rate)})
            break
        if band.upper <= previous:
            msg = f"band {index} ends at {band.upper}, not above {previous}"
            raise RowError(msg)
        out.append({"up_to": str(band.upper.quantize(_CENT)), "rate": str(band.rate)})
        previous = band.upper
    return out


def _upper(band: _Band) -> Decimal:
    return band.upper if band.upper is not None else Decimal(0)


def _slots(row: dict[str, str]) -> list[tuple[str, str]]:
    pairs = [(row[f"ALIQUOTA{s}"].strip(), row[f"FASCIA{s}"].strip()) for s in _SLOTS]
    return [(rate, text) for rate, text in pairs if rate or text]


def _exemption(text: str, row: dict[str, str]) -> Decimal:
    declared = _amount(row["IMPORTO_ESENTE"] or "0")
    if declared > 0:
        return declared
    numbers = _numbers(text.lower())
    if not numbers:
        msg = f"exemption without an amount: {text!r}"
        raise RowError(msg)
    return numbers[0]


@dataclass
class _Slots:
    """Rates and exemptions read from the slots of one row."""

    flat: Decimal | None = None
    bands: list[_Band] = field(default_factory=list)
    threshold: Decimal = Decimal(0)
    specific: list[str] = field(default_factory=list)


def _read_slots(row: dict[str, str]) -> _Slots:
    """Sort the slots of one row into rates, bands and exemptions.

    Returns:
        What the row states, not yet checked for consistency.
    """
    flag = row["FLAG_NUOVA"].strip()
    read = _Slots()
    for rate_text, text in _slots(row):
        lowered = re.sub(r"\s+", " ", text.lower())
        if not lowered.startswith("esenzione"):
            rate = _rate(rate_text)
            if lowered in {"", "aliquota unica"}:
                read.flat = rate
            else:
                read.bands.append(_band(rate, lowered))
        elif flag in SPECIFIC_FLAGS or not _GENERIC_EXEMPTION.match(lowered):
            read.specific.append(re.sub(r"\s+", " ", text))
        else:
            read.threshold = _exemption(lowered, row)
    return read


def _row_brackets(read: _Slots) -> list[dict[str, str | None]]:
    if read.bands and read.flat is not None:
        msg = "row has both a single rate and brackets"
        raise RowError(msg)
    if read.bands:
        return _brackets(read.bands)
    if read.flat is None:
        msg = "row has no rate"
        raise RowError(msg)
    return [{"up_to": None, "rate": str(read.flat)}]


def parse_row(row: dict[str, str]) -> dict[str, Any]:
    """Convert one CSV row that carries a delibera into a table entry.

    Returns:
        The entry fields: ``nome``, ``brackets``, and when present
        ``exemption_threshold`` and ``specific_exemptions``; a row whose
        rates cannot be read raises :class:`RowError`.
    """
    read = _read_slots(row)
    entry: dict[str, Any] = {
        "nome": _name(row["COMUNE"]),
        "brackets": _row_brackets(read),
    }
    if read.threshold > 0:
        entry["exemption_threshold"] = str(read.threshold.quantize(_CENT))
    if read.specific:
        entry["specific_exemptions"] = read.specific
    return entry


def _name(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip()).title()


def _zero(row: dict[str, str]) -> dict[str, Any]:
    return {"nome": _name(row["COMUNE"]), "brackets": [{"up_to": None, "rate": "0"}]}


def read_list(path: Path) -> dict[str, dict[str, str]]:
    """Read a MEF CSV list keyed by Belfiore code.

    Returns:
        The rows keyed by ``CODICE_CATASTALE``.
    """
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    return {r["CODICE_CATASTALE"].strip(): r for r in rows}


def _document(year: int, retrieved: str) -> dict[str, str]:
    return {
        "document_id": f"mef-addizionale-comunale-elenco-{year}",
        "title": (
            "MEF, Dipartimento delle Finanze: addizionale comunale all'IRPEF, "
            f"elenco generale {year} (CSV, retrieved {retrieved})"
        ),
        "kind": "amministrazione",
        "url": DOWNLOAD_URL.format(year=year),
    }


def _entry(
    year: int,
    code: str,
    row: dict[str, str],
    previous: dict[str, dict[str, str]],
    carried_note: str,
) -> dict[str, Any]:
    """Return the entry of one municipality, carried from the year before if needed.

    Returns:
        The entry; a carried one has ``rates_year`` and an ``assumed`` record.
    """
    if row["ALIQUOTA"].strip() != NOT_DELIBERATED:
        correction = CORRECTIONS.get((year, code))
        entry = parse_row({**row, **(correction or {})})
        if correction is not None:
            entry["provenance"] = {
                "status": "assumed",
                "transformation": _CORRECTION_NOTE,
            }
        return entry
    old = previous.get(code)
    if old is None or old["ALIQUOTA"].strip() == NOT_DELIBERATED:
        entry = _zero(row)
    else:
        entry = parse_row({**old, **CORRECTIONS.get((year - 1, code), {})})
    entry["rates_year"] = year - 1
    entry["provenance"] = {"status": "assumed", "transformation": carried_note}
    return entry


def _notes(
    year: int, retrieved: str, digests: tuple[str, str], carried: int, total: int
) -> list[str]:
    return [
        (
            "Fonte: MEF, Dipartimento delle Finanze, addizionale comunale "
            f"all'IRPEF, elenchi generali {year} e {year - 1} (CSV) scaricati "
            f"il {retrieved}; generato da scripts/data/build_comunale_surtax.py."
        ),
        f"sha256 elenco {year}: {digests[0]}; elenco {year - 1}: {digests[1]}.",
        (
            f"{total - carried} comuni con delibera {year}; {carried} senza "
            f"delibera {year} alla data di download, con le aliquote "
            f"{year - 1} (rates_year) come provvisorie."
        ),
        (
            "Chiave: codice catastale. Rate decimali (es. 0.008 = 0.8%); "
            "brackets marginali; exemption_threshold: esenzione totale se "
            "reddito imponibile <= soglia."
        ),
        (
            "specific_exemptions: esenzioni per una sola categoria di reddito, "
            "riportate come pubblicate e non calcolate dal motore."
        ),
    ]


def build(
    year: int,
    current: dict[str, dict[str, str]],
    previous: dict[str, dict[str, str]],
    *,
    retrieved: str,
    digests: tuple[str, str],
) -> tuple[dict[str, Any], list[str]]:
    """Build the table of ``year`` from its list and the list of the year before.

    Returns:
        The JSON payload and one error per row that could not be read.
    """
    carried_note = (
        f"No {year} delibera in the MEF list retrieved on {retrieved}; the "
        f"{year - 1} rates stay in force (art. 1 c. 169 L. 296/2006) unless a "
        f"{year} delibera is published by 20 December {year}."
    )
    rates: dict[str, Any] = {}
    errors: list[str] = []
    for code in sorted(current):
        try:
            entry = _entry(year, code, current[code], previous, carried_note)
        except RowError as exc:
            errors.append(f"{code} {current[code]['COMUNE']}: {exc}")
        else:
            rates[code] = entry
    carried = sum(1 for e in rates.values() if "rates_year" in e)
    payload: dict[str, Any] = {
        "year": year,
        "rates_are_advance": False,
        "notes": _notes(year, retrieved, digests, carried, len(rates)),
        "rates": rates,
        "sources": [_document(year, retrieved), _document(year - 1, retrieved)],
        "ruleset": {
            "id": f"surtax/{year}/comunale",
            "version": f"{year}.3",
            "effective_from": f"{year}-01-01",
            "effective_until": f"{year}-12-31",
            "published_at": retrieved,
            "source": INDEX_URL,
            "source_hash": "",
            "verification_status": "unverified",
            "source_type": "official_primary",
        },
        "provenance": {
            "status": "derived",
            "location": {
                "source_document": _document(year, retrieved),
                "section": f"elenco generale {year}",
            },
            "note": (
                f"Rows without a {year} delibera carry their own assumed "
                f"record and the {year - 1} rates."
            ),
        },
    }
    payload["ruleset"]["source_hash"] = source_hash(payload)
    return payload, errors


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    """Build the municipal table and write it to the knowledge bundle.

    Returns:
        0 on success, 1 when a row cannot be read (nothing is written).
    """
    parser = argparse.ArgumentParser(description="Build comunale-{year}.json")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--retrieved", required=True, help="YYYY-MM-DD")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    payload, errors = build(
        args.year,
        read_list(args.current),
        read_list(args.previous),
        retrieved=args.retrieved,
        digests=(_sha256(args.current), _sha256(args.previous)),
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    out = args.out or DATA_DIR / f"comunale-{args.year}.json"
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out}: {len(payload['rates'])} municipalities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
