r"""Build ``comunale-{year}.json`` from the MEF lists of the addizionale comunale.

The MEF Dipartimento delle Finanze publishes one CSV per tax year with the
rates and exemption deliberated by every municipality, updated daily:

    https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/
    fiscalitalocale/nuova_addcomirpef/download/download.php?anno=YYYY

(index page ``.../nuova_addcomirpef/download/tabella.htm``).  Until 20 December
of the year the list shows ``0*`` for a municipality that has not yet
published a delibera for the year.  Without an applicable delibera the
rates in force stay in force (art. 1 c. 169 L. 296/2006), so such a row
takes the row of the list of the year before, with ``rates_year`` set to
that year and an ``assumed`` provenance: the engine applies them as
provisional.  A delibera the list marks inapplicable (adopted after the
deadline) is skipped the same way, down the lists passed with
``--previous``.  ``0*`` in a list of an earlier year, closed after 20
December, means no surtax (rate 0).  A municipality missing from the list
of the year before (created by a merger) and without a delibera of its own
is left out and named in the notes: the engine reports its code as unknown.

Each row becomes marginal brackets, an exemption threshold and, when the
delibera exempts only a category of income (``FLAG_NUOVA`` 5 and 6, or an
exemption text of that kind), the published texts in
``specific_exemptions``, which the engine does not compute.  A row whose
brackets cannot be read stops the build: nothing is dropped silently.

The script is deterministic for given CSV files; their sha256 digests and
the retrieval date are written into the file.  The refresh procedure is in
``docs/trust/data-operations.md``.

Usage::

    curl -o 2026.csv '<download.php?anno=2026>'
    curl -o 2025.csv '<download.php?anno=2025>'
    curl -o 2024.csv '<download.php?anno=2024>'
    uv run python scripts/data/build_comunale_surtax.py \
        --year 2026 --current 2026.csv --previous 2025.csv 2024.csv \
        --retrieved 2026-10-07 --version 2026.4
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
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from collections.abc import Sequence

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
    "fiscalitalocale/nuova_addcomirpef/download/tabella.htm"
)
DOWNLOAD_URL: Final = (
    "https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/"
    "fiscalitalocale/nuova_addcomirpef/download/download.php?anno={year}"
)
NOT_DELIBERATED: Final = "0*"
SPECIFIC_FLAGS: Final = frozenset({"5", "6"})
_INAPPLICABLE: Final = re.compile(r"\bINAPPLICABIL[EI]\b", re.IGNORECASE)
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


type Row = dict[str, str]
type MefList = dict[str, Row]


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


def read_list(path: Path) -> MefList:
    """Read a MEF CSV list keyed by Belfiore code.

    A byte order mark before the header is ignored.

    Returns:
        The rows keyed by ``CODICE_CATASTALE``.

    Raises:
        ValueError: When a code appears on two rows.
    """
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    keyed: MefList = {}
    for row in rows:
        code = row["CODICE_CATASTALE"].strip()
        if code in keyed:
            msg = f"{path}: code {code} is listed twice"
            raise ValueError(msg)
        keyed[code] = row
    return keyed


def is_inapplicable(row: Row) -> bool:
    """Return whether the list marks the delibera of ``row`` inapplicable.

    A delibera adopted after the deadline does not apply to its year
    (``NOTE`` "ATTO OLTRE TERMINE - ALIQUOTE INAPPLICABILI PER IL 2026",
    "INAPPLICABILE PER IL 2025 (ADOTTATA OLTRE TERMINE ...)"); one that
    only confirms the rates in force is applicable ("... APPLICABILI ...
    IN QUANTO CONFERMATE").

    Returns:
        ``True`` for an inapplicable delibera.
    """
    return bool(_INAPPLICABLE.search(row.get("NOTE") or ""))


@dataclass(frozen=True)
class _Source:
    """The row the rates of a municipality come from.

    Attributes:
        year: Year of the list holding the row.
        row: The row, ``None`` when the municipality had no surtax that year
            (``0*`` in a list closed after 20 December).
        skipped: Years whose delibera the list marks inapplicable.
    """

    year: int
    row: Row | None
    skipped: tuple[int, ...]


def _resolve(year: int, code: str, lists: Sequence[MefList]) -> _Source | None:
    """Find the row in force for ``code``, walking the lists newest first.

    ``0*`` in the list of ``year`` and an inapplicable delibera move to the
    list of the year before (art. 1 c. 169 L. 296/2006); ``0*`` in an
    earlier list means no surtax.

    Returns:
        The source, or ``None`` when ``code`` is missing from an earlier
        list (a municipality created that year, e.g. by a merger): its
        rates cannot be read from the lists.

    Raises:
        RowError: When every list holds an inapplicable delibera.
    """
    skipped: list[int] = []
    for offset, mef in enumerate(lists):
        list_year = year - offset
        row = mef.get(code)
        if row is None:
            return None
        if row["ALIQUOTA"].strip() == NOT_DELIBERATED:
            if offset:
                return _Source(list_year, None, tuple(skipped))
        elif is_inapplicable(row):
            skipped.append(list_year)
        else:
            return _Source(list_year, row, tuple(skipped))
    msg = f"no applicable delibera in the lists down to {year - len(lists) + 1}"
    raise RowError(msg)


def _carried_note(year: int, source: _Source, retrieved: str) -> str:
    inapplicable = ""
    if source.skipped:
        years = ", ".join(str(y) for y in source.skipped)
        inapplicable = (
            f" (the delibera listed for {years} was adopted after the deadline "
            "and the MEF list marks it inapplicable)"
        )
    return (
        f"No applicable {year} delibera in the MEF list retrieved on "
        f"{retrieved}{inapplicable}; the rates in force in {source.year} stay "
        f"in force (art. 1 c. 169 L. 296/2006). The {year} list is updated "
        f"until 20 December {year}."
    )


def _entry(year: int, code: str, source: _Source, retrieved: str) -> dict[str, Any]:
    """Return the entry of one municipality from the row in force.

    Returns:
        The entry; one carried from an earlier year has ``rates_year`` and
        an ``assumed`` record, so has a corrected row.
    """
    correction = CORRECTIONS.get((source.year, code))
    if source.row is None:
        entry: dict[str, Any] = {"brackets": [{"up_to": None, "rate": "0"}]}
    else:
        entry = parse_row({**source.row, **(correction or {})})
    if source.year < year:
        entry["rates_year"] = source.year
        note = _carried_note(year, source, retrieved)
        entry["provenance"] = {"status": "assumed", "transformation": note}
    elif correction is not None:
        entry["provenance"] = {"status": "assumed", "transformation": _CORRECTION_NOTE}
    return entry


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


@dataclass(frozen=True)
class Tally:
    """Counts of the rows of a built table.

    Attributes:
        deliberated: Rows with an applicable delibera of the table year.
        carried: Rows with the rates of an earlier year.
        inapplicable: Carried rows whose delibera of the table year is
            marked inapplicable.
        unresolved: ``"<code> <name>"`` of the municipalities left out.
    """

    deliberated: int
    carried: int
    inapplicable: int
    unresolved: tuple[str, ...]


def _notes(
    year: int, retrieved: str, digests: Sequence[str], tally: Tally
) -> list[str]:
    years = [year - offset for offset in range(len(digests))]
    hashes = "; ".join(f"elenco {y}: {d}" for y, d in zip(years, digests, strict=True))
    unresolved = ", ".join(tally.unresolved) or "nessuno"
    return [
        (
            "Fonte: MEF, Dipartimento delle Finanze, addizionale comunale "
            f"all'IRPEF, elenchi generali {', '.join(map(str, years))} (CSV) "
            f"scaricati il {retrieved}; generato da "
            "scripts/data/build_comunale_surtax.py."
        ),
        f"sha256 {hashes}.",
        (
            f"{tally.deliberated} comuni con delibera {year} applicabile; "
            f"{tally.carried} senza delibera {year} applicabile alla data di "
            f"download ({tally.inapplicable} con delibera {year} adottata oltre "
            "termine e inapplicabile), con le aliquote dell'anno indicato in "
            "rates_year come provvisorie."
        ),
        (
            "Comuni senza riga, assenti dall'elenco dell'anno precedente "
            "(istituiti per fusione) e senza delibera propria: "
            f"{unresolved}. Il motore li tratta come codice sconosciuto."
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


def _ruleset(year: int, version: str, retrieved: str) -> dict[str, str]:
    return {
        "id": f"surtax/{year}/comunale",
        "version": version,
        "effective_from": f"{year}-01-01",
        "effective_until": f"{year}-12-31",
        "published_at": retrieved,
        "source": INDEX_URL,
        "source_hash": "",
        "verification_status": "unverified",
        "source_type": "official_primary",
    }


@dataclass(frozen=True)
class BuildOptions:
    """Identity of one build.

    Attributes:
        retrieved: Download date of the lists, ``YYYY-MM-DD``.
        digests: sha256 of each list, newest first.
        version: Ruleset version, ``YYYY.N``; bump it on every refresh.
    """

    retrieved: str
    digests: tuple[str, ...]
    version: str


def _payload(
    year: int, rates: dict[str, Any], notes: list[str], options: BuildOptions
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "year": year,
        "rates_are_advance": False,
        "notes": notes,
        "rates": rates,
        "sources": [
            _document(year - offset, options.retrieved)
            for offset in range(len(options.digests))
        ],
        "ruleset": _ruleset(year, options.version, options.retrieved),
        "provenance": {
            "status": "derived",
            "location": {
                "source_document": _document(year, options.retrieved),
                "section": f"elenco generale {year}",
            },
            "note": (
                f"Rows without an applicable {year} delibera carry their own "
                "assumed record and the rates of the year in rates_year."
            ),
        },
    }
    payload["ruleset"]["source_hash"] = source_hash(payload)
    return payload


@dataclass(frozen=True)
class BuildResult:
    """Outcome of :func:`build`.

    Attributes:
        payload: The JSON table.
        errors: One message per row that could not be read.
        tally: Counts of the rows, with the municipalities left out.
    """

    payload: dict[str, Any]
    errors: list[str]
    tally: Tally


def build(year: int, lists: Sequence[MefList], options: BuildOptions) -> BuildResult:
    """Build the table of ``year`` from its list and the lists before it.

    Args:
        year: Tax year of the table.
        lists: The MEF list of ``year`` followed by the lists of the years
            before, newest first.
        options: Download date, digests and version.

    Returns:
        The payload, one error per row that could not be read and the
        counts; a municipality whose rates the lists cannot give is left
        out of the table and named in the tally and in the notes.
    """
    rates: dict[str, Any] = {}
    errors: list[str] = []
    unresolved: list[str] = []
    current = lists[0]
    for code in sorted(current):
        name = current[code]["COMUNE"]
        try:
            source = _resolve(year, code, lists)
            if source is None:
                unresolved.append(f"{code} {_name(name)}")
                continue
            entry = _entry(year, code, source, options.retrieved)
        except RowError as exc:
            errors.append(f"{code} {name}: {exc}")
        else:
            entry.pop("nome", None)
            rates[code] = {"nome": _name(name), **entry}
    tally = Tally(
        deliberated=sum(1 for e in rates.values() if "rates_year" not in e),
        carried=sum(1 for e in rates.values() if "rates_year" in e),
        inapplicable=sum(1 for c in rates if is_inapplicable(current[c])),
        unresolved=tuple(unresolved),
    )
    notes = _notes(year, options.retrieved, options.digests, tally)
    return BuildResult(_payload(year, rates, notes, options), errors, tally)


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
    parser.add_argument(
        "--previous",
        type=Path,
        nargs="+",
        required=True,
        help="lists of the years before, newest first",
    )
    parser.add_argument("--retrieved", required=True, help="YYYY-MM-DD")
    parser.add_argument("--version", required=True, help="ruleset version YYYY.N")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    paths: list[Path] = [args.current, *args.previous]
    options = BuildOptions(
        retrieved=args.retrieved,
        digests=tuple(_sha256(p) for p in paths),
        version=args.version,
    )
    result = build(args.year, [read_list(p) for p in paths], options)
    if result.errors:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    for municipality in result.tally.unresolved:
        print(f"WARNING: no rates for {municipality}; left out", file=sys.stderr)
    out = args.out or DATA_DIR / f"comunale-{args.year}.json"
    text = json.dumps(result.payload, ensure_ascii=False, indent=2) + "\n"
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out}: {len(result.payload['rates'])} municipalities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
