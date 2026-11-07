"""A coverage rule can name the CCNLs it concerns.

INPS, Indennità di malattia per lavoratori dipendenti: "Non spetta a
(elenco non esaustivo): [...] portieri"; the portieri CCNL is filed under the
terziario, whose operai and impiegati INPS covers.
"""

from __future__ import annotations

from ccnl_engine.sickness.indemnity.models import SickPayCoverage

_PORTIERI = SickPayCoverage(
    ccnls=frozenset({"portieri-fabbricati-confedilizia"}), covered=False, source="INPS"
)


def test_rule_matches_only_its_ccnl() -> None:
    """The portieri rule concerns that CCNL, whatever the sector."""
    assert _PORTIERI.matches(
        "terziario", "operaio", "permanent", "portieri-fabbricati-confedilizia"
    )
    assert not _PORTIERI.matches(
        "terziario", "operaio", "permanent", "commercio-confcommercio"
    )
    assert not _PORTIERI.matches("terziario", "operaio", "permanent")
