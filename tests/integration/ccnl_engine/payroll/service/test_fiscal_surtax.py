"""Surtax decisions: not due, unknown table, below exemption, applied."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.jurisdiction import REGION_CODES
from ccnl_engine.payroll.service.fiscal_surtax import (
    MUNICIPAL_SURTAX,
    REGIONAL_SURTAX,
    SurtaxOutcome,
    compute_surtax,
)
from ccnl_engine.shared.domain.primitives import Bracket
from ccnl_engine.tax.domain.surtax_rules import SurtaxRules
from ccnl_engine.tax.domain.surtax_tables import ComunaleEntry, RegionaleEntry
from ccnl_engine.tax.service.surtax_loaders import load_surtax_rules

_D = Decimal
_TAXABLE = _D("30000")
_IRPEF = _D("1000")


def _rules(*, advance: bool = False, ruleset: bool = False) -> SurtaxRules:
    identity = load_surtax_rules(2026).regional_ruleset
    return SurtaxRules(
        year=2026,
        regional_ruleset=identity if ruleset else None,
        municipal_ruleset=identity if ruleset else None,
        regionale={
            "Lombardia": RegionaleEntry(
                brackets=(Bracket(up_to=None, rate=_D("0.0123")),)
            )
        },
        comunale={
            "H501": ComunaleEntry(
                nome="Roma", brackets=(Bracket(up_to=None, rate=_D("0.008")),)
            ),
            "A083": ComunaleEntry(
                nome="Agordo",
                brackets=(Bracket(up_to=None, rate=_D("0.008")),),
                exemption_threshold=_D("40000"),
            ),
        },
        comunale_rates_are_advance=advance,
        comunale_advance_fraction=_D("0.30"),
    )


def _compute(
    regione: str | None,
    comune: str | None,
    *,
    irpef_due: Decimal = _IRPEF,
    rules: SurtaxRules | None = None,
) -> SurtaxOutcome:
    return compute_surtax(
        _TAXABLE,
        rules if rules is not None else _rules(),
        regione=regione,
        comune_belfiore=comune,
        irpef_due=irpef_due,
    )


def test_no_jurisdiction_takes_no_decision() -> None:
    """Without codes there is nothing to decide and nothing to withhold."""
    outcome = _compute(None, None)

    assert outcome == SurtaxOutcome()


def test_known_tables_are_applied_and_final() -> None:
    """Known region and municipality give final decisions with annual amounts."""
    outcome = _compute("IT-25", "H501")

    regional, municipal = outcome.decisions
    assert (regional.capability, regional.reason_code) == (
        REGIONAL_SURTAX,
        "table_applied",
    )
    assert regional.status is CalculationStatus.FINAL
    assert regional.amount == _D("369.00")
    assert regional.inputs["table"] == "Lombardia"
    assert regional.rule == "surtax/2026/addizionale_regionale"
    assert regional.rule_version == "2026"
    assert (municipal.capability, municipal.reason_code) == (
        MUNICIPAL_SURTAX,
        "table_applied",
    )
    assert municipal.amount == _D("240.00")
    assert municipal.inputs["table"] == "Roma"
    assert outcome.regional + outcome.municipal == _D("609.00")
    assert outcome.issues == ()


def test_ruleset_identity_is_recorded_as_rule() -> None:
    """The bundled ruleset id and version identify the rule applied."""
    outcome = _compute("IT-25", "H501", rules=_rules(ruleset=True))

    identity = load_surtax_rules(2026).regional_ruleset
    assert identity is not None
    assert {(d.rule, d.rule_version) for d in outcome.decisions} == {
        ("surtax/2026/regionale", identity.version)
    }


def test_prior_year_rates_give_the_full_surtax_as_provisional() -> None:
    """A table of the year before: full surtax, provisional, issue named.

    30,000 x 0.8% = 240.00, the whole municipal surtax of the year (the
    acconto and saldo are split by the conguaglio, not here).  The rates
    are those of 2025, so the decision and its issue are provisional.
    """
    outcome = _compute(None, "H501", rules=_rules(advance=True))

    (municipal,) = outcome.decisions
    assert municipal.reason_code == "prior_year_rates_applied"
    assert municipal.amount == _D("240.00")
    assert municipal.inputs["rates_year"] == "2025"
    assert municipal.status is CalculationStatus.PROVISIONAL
    assert outcome.municipal == _D("240.00")
    (issue,) = outcome.issues
    assert issue.code == "municipal_surtax_prior_year_rates"
    assert issue.status is CalculationStatus.PROVISIONAL


def test_runs_before_the_conguaglio_determine_nothing() -> None:
    """Before the conguaglio a known table gives 0 and an unknown one fails.

    The surtax of the year is determined only by its conguaglio (D.Lgs.
    446/1997 art. 50 c. 4, D.Lgs. 360/1998 art. 1 c. 5); an unknown table
    is reported on every run, so the result is not paid as final.
    """
    outcome = compute_surtax(
        _TAXABLE,
        _rules(),
        regione="IT-25",
        comune_belfiore="Z999",
        irpef_due=_IRPEF,
        at_conguaglio=False,
    )

    assert [(d.reason_code, d.amount) for d in outcome.decisions] == [
        ("determined_at_conguaglio", _D(0)),
        ("table_unknown", None),
    ]
    assert [i.code for i in outcome.issues] == ["municipal_surtax_unknown"]


def test_income_below_exemption_is_not_due() -> None:
    """A municipal exemption threshold above the income makes the surtax 0."""
    (municipal,) = _compute(None, "A083").decisions

    assert municipal.reason_code == "below_exemption_threshold"
    assert municipal.status is CalculationStatus.FINAL
    assert municipal.amount == _D(0)


def test_no_irpef_due_means_no_surtax_due() -> None:
    """No IRPEF due: both surtaxes are final zero, even for unknown tables."""
    outcome = _compute("IT-99", "Z999", irpef_due=_D(0))

    assert [d.reason_code for d in outcome.decisions] == [
        "no_irpef_due",
        "no_irpef_due",
    ]
    assert all(d.status is CalculationStatus.FINAL for d in outcome.decisions)
    assert all(d.amount == _D(0) for d in outcome.decisions)
    assert outcome.issues == ()


@pytest.mark.parametrize(
    ("regione", "comune", "issue_code"),
    [
        ("IT-99", None, "regional_surtax_unknown"),
        ("IT-45", None, "regional_surtax_unknown"),
        (None, "Z999", "municipal_surtax_unknown"),
    ],
)
def test_unknown_table_is_incomplete(
    regione: str | None, comune: str | None, issue_code: str
) -> None:
    """A well-formed code without a table row is incomplete, amount unknown.

    ``IT-45`` is a known region code whose row is missing from this test table.
    """
    outcome = _compute(regione, comune)

    (decision,) = outcome.decisions
    assert decision.reason_code == "table_unknown"
    assert decision.status is CalculationStatus.INCOMPLETE
    assert decision.amount is None
    assert decision.inputs["table"] == "unknown"
    assert outcome.regional == outcome.municipal == _D(0)
    (issue,) = outcome.issues
    assert issue.code == issue_code
    assert issue.status is CalculationStatus.INCOMPLETE
    assert "must not be paid" in issue.message


def test_every_region_code_has_a_bundled_row() -> None:
    """The region codes and the 2026 regional table name the same rows."""
    assert set(REGION_CODES.values()) == set(load_surtax_rules(2026).regionale)
