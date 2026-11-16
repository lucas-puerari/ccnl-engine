"""FASA from 1 June 2029: the worker's choice to pay EUR 2 a month.

Alimentari art. 74 quater (FLAI text sha256 11792ad3…, PDF p. 157): "A far
data dal 1° giugno 2029 il finanziamento al Fondo potrà essere implementato
di ulteriori 2 euro mensili (per 12 mensilità) a carico del lavoratore
dipendente, dietro espressa volontà dello stesso.  Laddove il lavoratore non
manifesti la volontà di partecipare con la propria quota al Fondo, lo stesso
decade dall'iscrizione e cessa automaticamente la contribuzione da parte
dell'impresa."  The bundle has no tax tables for 2029, so the gate is shown
on a fake run context.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.inputs import Employment, Permanent
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.fund.health.rules import with_opt_ins
from ccnl_engine.fund.health.services import FundOutcome

if TYPE_CHECKING:
    from ccnl_engine.fund.health.models import ContractualFund
    from ccnl_engine.period.context.services import RunContext

_FUNDS = load_ccnl("alimentari-federalimentare").parameters.health_funds
_FASA = next(f for f in _FUNDS if f.code == "fasa")
_MATERNITY = next(f for f in _FUNDS if f.code == "cassa_maternita")
_PAID = frozenset({"fasa", "cassa_maternita"})


def _posted(
    day: date, opt_ins: frozenset[str] | None, paid: frozenset[str] = _PAID
) -> tuple[list[str], FundOutcome]:
    ctx = SimpleNamespace(
        contract=SimpleNamespace(tctx=SimpleNamespace(competence=day)),
        request=SimpleNamespace(fund_opt_ins=opt_ins),
    )
    seen: list[str] = []

    def post(
        _ctx: RunContext, funds: tuple[ContractualFund, ...], _paid: frozenset[str]
    ) -> FundOutcome:
        seen.extend(f.code for f in funds)
        return FundOutcome()

    outcome = with_opt_ins(cast("RunContext", ctx), (_FASA, _MATERNITY), paid, post)
    return seen, outcome


def test_before_june_2029_the_choice_is_not_read() -> None:
    """May 2029: FASA is paid whatever the worker states."""
    seen, outcome = _posted(date(2029, 5, 1), None)
    assert seen == ["fasa", "cassa_maternita"]
    assert outcome.issues == ()


@pytest.mark.parametrize(
    ("opt_ins", "funds"),
    [
        (frozenset({"fasa"}), ["fasa", "cassa_maternita"]),
        (frozenset(), ["cassa_maternita"]),
    ],
)
def test_from_june_2029_only_the_worker_who_pays_stays(
    opt_ins: frozenset[str], funds: list[str]
) -> None:
    """A worker who does not pay leaves FASA; the Cassa maternità stays."""
    seen, outcome = _posted(date(2029, 6, 1), opt_ins)
    assert seen == funds
    assert outcome.issues == ()


def test_an_unstated_choice_posts_nothing_for_fasa() -> None:
    """Neither the shares nor the element: a missing fact."""
    seen, outcome = _posted(date(2029, 6, 1), None)
    assert seen == ["cassa_maternita"]
    (issue,) = outcome.issues
    assert issue.code == "fund_opt_ins_unknown"
    assert issue.fact == "fund_opt_ins"
    assert "fasa" in issue.message


def test_an_employer_outside_fasa_asks_no_choice() -> None:
    """The EDR path: no worker is enrolled, so no choice is read."""
    seen, outcome = _posted(date(2029, 6, 1), None, frozenset({"cassa_maternita"}))
    assert seen == ["fasa", "cassa_maternita"]
    assert outcome.issues == ()


def test_the_worker_share_is_two_euro_from_june_2029() -> None:
    """EUR 0 before, EUR 2 a month from 1 June 2029, deductible."""
    assert _FASA.employee is not None
    assert _FASA.employee.monthly is not None
    assert _FASA.employee.monthly.value_at(date(2029, 5, 1)) == 0
    assert _FASA.employee.monthly.value_at(date(2029, 6, 1)) == Decimal(2)
    assert _FASA.employee_deductible
    assert _FASA.opt_in_from == date(2029, 6, 1)


def test_the_fund_codes_are_strings() -> None:
    """A frozenset of non-blank codes; a plain set or a blank code is rejected."""
    employment = Employment("alimentari-federalimentare", "5", Permanent())
    assert employment.fund_opt_ins is None
    chosen = Employment(
        "alimentari-federalimentare", "5", Permanent(), fund_opt_ins=frozenset({"fasa"})
    )
    assert chosen.fund_opt_ins == frozenset({"fasa"})
    for codes in ({"fasa"}, frozenset({" "})):
        with pytest.raises(InvalidInputError, match="fund_opt_ins"):
            Employment(
                "alimentari-federalimentare",
                "5",
                Permanent(),
                fund_opt_ins=codes,  # type: ignore[arg-type]
            )
