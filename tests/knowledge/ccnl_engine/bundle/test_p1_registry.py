"""CNEL code and contractual term of the CCNLs of the first review round.

Each code is the one of the 21st CNEL report of the CCNLs in force (30 June
2025, sha256
9b8e03b292ad71b6fcbc993eea8e070364423ee4e4dd4a495df7236112ae25c3), the code
the Uniemens declarations carry; each term is the one of the term clause of
the text read in the P1 review, or of the report where the text was not
readable (commercio, edilizia).
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_REGISTRY = (
    ("metalmeccanico-federmeccanica", "C011", date(2025, 11, 22), date(2028, 6, 30)),
    ("commercio-confcommercio", "H011", date(2023, 4, 1), date(2027, 3, 31)),
    ("edilizia-ance", "F012", date(2025, 2, 1), date(2028, 6, 30)),
    ("operai-agricoli-florovivaisti", "A011", date(2026, 1, 1), date(2029, 12, 31)),
    ("funzioni-centrali-aran", "S005", date(2025, 1, 1), date(2027, 12, 31)),
    ("lavoro-domestico-non-convivente", "H501", date(2025, 11, 1), None),
    ("bancari-abi", "J241", date(2023, 7, 1), date(2026, 3, 31)),
    ("logistica-trasporto-confetra", "I100", date(2025, 1, 1), date(2027, 12, 31)),
    ("sanita-privata-aiop-aris", "T011", date(2016, 1, 1), date(2018, 12, 31)),
    ("metalmeccanico-artigianato", "C030", date(2023, 1, 1), date(2026, 12, 31)),
)


@pytest.mark.parametrize(("slug", "code", "start", "end"), _REGISTRY)
def test_code_and_term(slug: str, code: str, start: date, end: date | None) -> None:
    """The CNEL code and the term the CCNL file declares."""
    meta = load_ccnl(slug).meta

    assert meta.cnel_code == code
    assert meta.validity is not None
    assert (meta.validity.valid_from, meta.validity.valid_until) == (start, end)


def test_sanita_privata_signatories_are_those_of_the_text() -> None:
    """AIOP and ARIS with FP-CGIL, CISL-FPS and UIL-FPL (CCNL 8 October 2020)."""
    meta = load_ccnl("sanita-privata-aiop-aris").meta

    assert meta.signatories == ("AIOP", "ARIS", "FP-CGIL", "CISL-FPS", "UIL-FPL")
