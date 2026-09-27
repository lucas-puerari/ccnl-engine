"""Withholding rule in force per tax year.

Normattiva, accessed 2026-09-27: art. 23 D.P.R. 600/1973 "in vigore dal
21-5-2022 al 31-12-2026"; art. 243 c. 1 of the testo unico of D.Lgs. 33/2025
"si applicano a decorrere dal 1° gennaio 2027" (D.L. 200/2025 art. 4 c. 4).
Art. 33 of the testo unico renumbers the commi: art. 23 c. 3 is art. 33 c. 4.
"""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.service.withholding_law import (
    WithholdingTopic,
    withholding_rule,
)


@pytest.mark.parametrize(
    ("topic", "tax_year", "rule", "section", "citation"),
    [
        (
            WithholdingTopic.AGENTS,
            2026,
            "dpr600-1973-art23-c1",
            "art. 23 c. 1",
            "art. 23 c. 1 DPR 600/1973",
        ),
        (
            WithholdingTopic.CONGUAGLIO,
            2026,
            "dpr600-1973-art23-c3",
            "art. 23 c. 3",
            "art. 23 c. 3 DPR 600/1973",
        ),
        (
            WithholdingTopic.AGENTS,
            2027,
            "dlgs33-2025-art33-c1",
            "art. 33 c. 1",
            "art. 33 c. 1 D.Lgs. 33/2025",
        ),
        (
            WithholdingTopic.CONGUAGLIO,
            2027,
            "dlgs33-2025-art33-c4",
            "art. 33 c. 4",
            "art. 33 c. 4 D.Lgs. 33/2025",
        ),
    ],
)
def test_rule_follows_the_norm_in_force(
    topic: WithholdingTopic, tax_year: int, rule: str, section: str, citation: str
) -> None:
    """Art. 23 D.P.R. 600/1973 until 2026, art. 33 D.Lgs. 33/2025 from 2027."""
    law = withholding_rule(topic, tax_year)

    assert law.rule == rule
    assert law.source.section == section
    assert law.citation == citation


def test_sources_pin_the_documents() -> None:
    """The 2026 source is the version of art. 23 in force until 2026-12-31."""
    before = withholding_rule(WithholdingTopic.CONGUAGLIO, 2026).source
    after = withholding_rule(WithholdingTopic.CONGUAGLIO, 2027).source

    assert before.source_document.document_id == "dpr-600-1973"
    assert before.source_document.url.endswith("~art23!vig=2026-12-31")
    assert after.source_document.document_id == "dlgs-33-2025"
    assert after.source_document.url.endswith(";33:1~art33")
