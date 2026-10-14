"""The bundled TFR revaluation of 2026 against ISTAT and the statutes.

ISTAT, Prezzi al consumo, agosto 2026, serie storiche (serie08_2026.xlsx,
sha256 074b836b74328a0d3da22a0192d97583d4825c88063d7bae88665cfed9b1aa06,
re-read on 14 October 2026), Tabella 10, FOI esclusi i tabacchi: December
2025 at 121.5 (base 2015=100) and the link coefficient from base 2015 to
base 2025 at 1.214.  Art. 2120 c. 4 c.c. sets the rate at 1.5% plus 75% of
the index increase over December of the year before; D.Lgs. 47/2000 art. 11
c. 3 taxes the revaluation at 17%.  The December 2026 index comes out in
January 2027: until then the rate of the year is not known.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.severance.loaders import load_tfr_revaluation_rules

_RULES = load_tfr_revaluation_rules(2026)


def test_the_inputs_are_the_istat_and_statutory_figures() -> None:
    """121.5, 1.214, 1.5%, 75% and 17%."""
    assert _RULES is not None
    index = _RULES.price_index
    assert (index.previous_december, index.link_coefficient) == (
        Decimal("121.5"),
        Decimal("1.214"),
    )
    assert (_RULES.rate.fixed, _RULES.rate.index_share) == (
        Decimal("0.015"),
        Decimal("0.75"),
    )
    assert _RULES.substitute_tax.rate == Decimal("0.17")


def test_the_december_index_is_not_published_yet() -> None:
    """Without the December 2026 index the rate of the year is unknown."""
    assert _RULES is not None
    assert _RULES.price_index.december is None
    assert _RULES.annual_rate() is None


def test_a_december_index_in_the_new_base_is_linked_to_the_old_one() -> None:
    """The 2026 index (base 2025) times 1.214 over the 121.5 of base 2015.

    With the August 2026 index, 103.7, as if it were December's: 103.7 x
    1.214 / 121.5 = 1.03616..., so the rate is 1.5% + 75% of 3.616...%.
    """
    assert _RULES is not None
    december = Decimal("103.7")
    rules = _RULES.model_copy(
        update={
            "price_index": _RULES.price_index.model_copy(update={"december": december})
        }
    )
    increase = december * Decimal("1.214") / Decimal("121.5") - 1

    assert rules.annual_rate() == Decimal("0.015") + Decimal("0.75") * increase
