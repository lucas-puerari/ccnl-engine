"""The run reports the open reading of the 65 EUR increment as an issue."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast

from ccnl_engine.irpef.net.rules import NetIrpef
from ccnl_engine.irpef.services import TRATTAMENTO_INCREMENT_OPEN, trattamento_issues
from ccnl_engine.tax_credit.models import TrattamentoIntegrativoRules
from ccnl_engine.tax_credit.recovery.models import InstallmentRun
from ccnl_engine.tax_credit.trattamento_integrativo.rules import resolve_trattamento
from tests.unit.ccnl_engine.builders import make_year_rules

_RULES = make_year_rules().model_copy(
    update={
        "trattamento_integrativo": TrattamentoIntegrativoRules(
            threshold_mid=Decimal(15_000),
            threshold_upper=Decimal(28_000),
            max_amount=Decimal(1200),
        )
    }
)


def _issues(family: Decimal) -> tuple[object, ...]:
    annual = NetIrpef(
        gross=Decimal("4600.00"),
        work_deduction=Decimal("2642.21"),
        family_deductions=family,
        ulteriore=None,
    )
    _, _, _, decisions = resolve_trattamento(
        Decimal(26_000), annual, _RULES, Decimal(0), 12, run=InstallmentRun()
    )
    inp = cast("Any", SimpleNamespace(rules=_RULES))
    irpef = cast("Any", SimpleNamespace(tax=SimpleNamespace(decisions=decisions)))
    return trattamento_issues(inp, irpef)


def test_the_issue_names_a_credit_the_increment_decides() -> None:
    """An excess of 22.21 exists only through the 65.00: the run is incomplete."""
    assert _issues(Decimal(1980)) == (TRATTAMENTO_INCREMENT_OPEN,)


def test_no_issue_when_the_credit_is_capped_anyway() -> None:
    """An excess of 1,542.21 pays the 1,200.00 cap with or without 65.00."""
    assert _issues(Decimal(3500)) == ()
