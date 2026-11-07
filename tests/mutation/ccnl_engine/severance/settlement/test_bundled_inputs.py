"""The bundled TFR settlement rules of 2026 against the statutes.

Art. 19 c. 1 TUIR (Normattiva, text in force from 12-8-2006 to 31-12-2026,
read on 19 October 2026): the reference income is the TFR net of the
revaluations already taxed, over the years and fraction of year of
service, "moltiplicando il risultato per dodici".  Art. 2120 c. 1 c.c.:
"computandosi come mese intero le frazioni di mese uguali o superiori a 15
giorni".  From 2027 the testo unico of D.Lgs. 117/2026 replaces art. 19
TUIR, so the bundle carries no 2027 rules.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.severance.loaders import load_tfr_settlement_rules
from ccnl_engine.severance.services import settlement_rules

_RULES = load_tfr_settlement_rules(2026)


def test_the_inputs_are_the_statutory_figures() -> None:
    """Twelve times the yearly TFR, and 15 days to a month."""
    assert _RULES is not None
    assert _RULES.reference_income.multiplier == Decimal(12)
    assert _RULES.service_period.month_minimum_days == 15


def test_each_rule_cites_its_article() -> None:
    """Art. 17 c. 1 lett. a, art. 19 c. 1 TUIR and art. 2120 c. 1 c.c."""
    assert _RULES is not None
    sections = [
        provenance.location.section
        for _, provenance in settlement_rules(_RULES)
        if isinstance(provenance, RuleProvenance) and provenance.location
    ]
    assert sections == ["art. 17 c. 1 lett. a)", "art. 19 c. 1", "art. 2120 c. 1"]


def test_no_rules_from_2027() -> None:
    """The TUIR article the rules cite is repealed from 1 January 2027."""
    assert load_tfr_settlement_rules(2027) is None
    assert settlement_rules(None) == ()


def test_rules_without_a_ruleset_are_named_after_the_year() -> None:
    """A table with no identity reads ``tax/<year>/tfr-settlement``."""
    assert _RULES is not None
    rules = settlement_rules(_RULES.model_copy(update={"ruleset": None}))
    assert rules[0][0] == "tax/2026/tfr-settlement:separate_taxation"
