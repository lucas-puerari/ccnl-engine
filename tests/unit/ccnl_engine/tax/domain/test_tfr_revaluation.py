"""Rate of the TFR revaluation at 31 December (art. 2120 c. 4 c.c.).

Art. 2120 c. 4 c.c. (Normattiva, text in force from 11-4-1991,
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262~art2120):
"un tasso costituito dall'1,5 per cento in misura fissa e dal 75 per cento
dell'aumento dell'indice dei prezzi al consumo per le famiglie di operai ed
impiegati, accertato dall'ISTAT, rispetto al mese di dicembre dell'anno
precedente".  Indexes in different bases are compared through the link
coefficient (ISTAT, Prezzi al consumo agosto 2026, nota metodologica,
"Calcolo delle variazioni degli indici").  The December 2025 index without
tobacco is 121,5 (base 2015=100) and the link coefficient from base 2015 to
base 2025 is 1,214 (ISTAT serie08_2026.xlsx, Tabella 10).
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.tax.domain.tfr_revaluation import (
    TfrPriceIndex,
    TfrRevaluationRate,
    TfrRevaluationRules,
    TfrSubstituteTax,
)

#: A December index used to exercise the formula; ISTAT has not published
#: the December 2026 index.  103,7 is the August 2026 index (base 2025=100).
_HYPOTHETICAL_DECEMBER = Decimal("103.7")


def _rules(december: Decimal | None) -> TfrRevaluationRules:
    return TfrRevaluationRules(
        year=2026,
        rate=TfrRevaluationRate(fixed=Decimal("0.015"), index_share=Decimal("0.75")),
        price_index=TfrPriceIndex(
            previous_december=Decimal("121.5"),
            december=december,
            link_coefficient=Decimal("1.214"),
        ),
        substitute_tax=TfrSubstituteTax(rate=Decimal("0.17")),
    )


def test_no_december_index_no_increase_and_no_rate() -> None:
    """Until ISTAT publishes the December index there is no rate."""
    rules = _rules(None)
    assert rules.price_index.increase() is None
    assert rules.annual_rate() is None


def test_increase_links_the_two_bases() -> None:
    """103.7 x 1.214 / 121.5 - 1 = 125.8918 / 121.5 - 1 = 0.0361465020...

    ANCE publishes the same 3,61465021% for the August 2026 coefficient.
    """
    increase = _rules(_HYPOTHETICAL_DECEMBER).price_index.increase()
    assert increase == Decimal("125.8918") / Decimal("121.5") - 1
    assert round(increase * 100, 8) == Decimal("3.61465021")


def test_rate_is_the_fixed_part_plus_three_quarters_of_the_increase() -> None:
    """0.015 + 0.75 x 0.0361465020... = 0.0421098765..."""
    rate = _rules(_HYPOTHETICAL_DECEMBER).annual_rate()
    increase = Decimal("125.8918") / Decimal("121.5") - 1
    assert rate == Decimal("0.015") + Decimal("0.75") * increase
    assert round(rate, 10) == Decimal("0.0421098765")


def test_same_base_needs_no_link() -> None:
    """With one base the coefficient is 1: 110 / 100 - 1 = 0.10."""
    index = TfrPriceIndex(
        previous_december=Decimal(100),
        december=Decimal(110),
        link_coefficient=Decimal(1),
    )
    assert index.increase() == Decimal("0.10")
