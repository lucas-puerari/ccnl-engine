"""Separate taxation rule of arrears in force per tax year.

Normattiva, accessed 2026-10-09: the testo unico of D.Lgs. 19 giugno 2026
n. 117 carries art. 17 TUIR as its art. 19 ("Tassazione separata (articolo
17 decreto del Presidente della Repubblica 22 dicembre 1986, n. 917 ...)")
and art. 21 TUIR as its art. 23; it applies from 1 January 2027.
"""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.service.separate_tax_law import separate_tax_rule


@pytest.mark.parametrize(
    ("tax_year", "rule", "citation", "rate_citation"),
    [
        (2026, "tuir-art17-c1-b", "art. 17 c. 1 lett. b TUIR", "art. 21 c. 1 TUIR"),
        (
            2027,
            "dlgs117-2026-art19-c1-b",
            "art. 19 c. 1 lett. b D.Lgs. 117/2026",
            "art. 23 c. 1 D.Lgs. 117/2026",
        ),
    ],
)
def test_rule_follows_the_norm_in_force(
    tax_year: int, rule: str, citation: str, rate_citation: str
) -> None:
    """Art. 17 TUIR until 2026, art. 19 D.Lgs. 117/2026 from 2027."""
    law = separate_tax_rule(tax_year)

    assert law.rule == rule
    assert law.citation == citation
    assert law.rate_citation == rate_citation
