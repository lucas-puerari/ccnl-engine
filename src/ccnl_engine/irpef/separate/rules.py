"""Rule of the separate taxation of arrears, per tax year.

Art. 17 c. 1 lett. b D.P.R. 917/1986 (TUIR) taxes separately the arrears of
employment income of earlier years, at the rate of art. 21 c. 1, until 31
December 2026.  From 1 January 2027 the testo unico of D.Lgs. 19 giugno
2026 n. 117 applies; it carries the same rules renumbered: its art. 19
("Tassazione separata", from art. 17 TUIR) c. 1 lett. b taxes separately
the "emolumenti arretrati per prestazioni di lavoro dipendente riferibili
ad anni precedenti", and its art. 23 c. 1 (from art. 21 TUIR) sets the
rate, for the arrears of art. 19 c. 1 lett. b, on half the income of the
two years before the year "in cui sono percepiti".
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SeparateTaxRule", "separate_tax_rule"]

#: First tax year of the testo unico of D.Lgs. 117/2026.
_TESTO_UNICO_FROM = 2027


@dataclass(frozen=True)
class SeparateTaxRule:
    """The separate taxation rule of arrears in force for one tax year.

    Attributes:
        rule: Rule id, e.g. ``"tuir-art17-c1-b"``.
        citation: Short citation of the rule, e.g.
            ``"art. 17 c. 1 lett. b TUIR"``.
        rate_citation: Short citation of the rule of the rate.
    """

    rule: str
    citation: str
    rate_citation: str


def separate_tax_rule(tax_year: int) -> SeparateTaxRule:
    """Return the separate taxation rule of arrears in force for ``tax_year``.

    Returns:
        Art. 19 c. 1 lett. b of the testo unico of D.Lgs. 117/2026 from
        2027, art. 17 c. 1 lett. b TUIR before.
    """
    if tax_year >= _TESTO_UNICO_FROM:
        return SeparateTaxRule(
            rule="dlgs117-2026-art19-c1-b",
            citation="art. 19 c. 1 lett. b D.Lgs. 117/2026",
            rate_citation="art. 23 c. 1 D.Lgs. 117/2026",
        )
    return SeparateTaxRule(
        rule="tuir-art17-c1-b",
        citation="art. 17 c. 1 lett. b TUIR",
        rate_citation="art. 21 c. 1 TUIR",
    )
