"""Travel allowance: exempt up to the daily cap of art. 51 c. 5 TUIR.

The caps are the lire amounts of art. 51 c. 5 converted at 1,936.27 lire per
euro: 90,000 lire (46.48) a day in Italy, 150,000 (77.47) abroad, reduced by
one third (60,000 / 100,000 lire: 30.99 / 51.65) when meals or lodging are
reimbursed or provided, by two thirds (30,000 / 50,000 lire: 15.49 / 25.82)
when both are.  Within the comune the allowance is income in full.  The INPS
base follows the same rule (art. 12 c. 2 L. 153/1969).
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.context.models import EffectiveDateContext
from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.event.allocation.services import _process_events
from ccnl_engine.event.facade import BonusEvent, TravelAllowanceEvent
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.facade import CompetencePeriod
from ccnl_engine.pay_item.loaders import load_policy_resolver
from ccnl_engine.pay_item.policies import PolicyContext
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import calculate_period
from ccnl_engine.reconciliation.validators import reconcile
from ccnl_engine.run.types import PeriodId
from ccnl_engine.variable_pay.benefit.handlers import fringe_threshold_of
from ccnl_engine.variable_pay.loaders import load_variable_pay_rules
from ccnl_engine.variable_pay.travel.handlers import (
    TravelAllowanceAssessment,
    TravelTerms,
)
from ccnl_engine.working_time.models import CcnlTravelAllowance
from scripts.provenance.rules import KNOWLEDGE_DIR

if TYPE_CHECKING:
    from ccnl_engine.decision.models import CalculationDecision
    from ccnl_engine.period.results import PeriodResult
    from ccnl_engine.variable_pay.models import TravelAllowanceRules

_DAY = date(2026, 3, 10)
_RULES = load_variable_pay_rules(2026).travel_allowance


def _trip(**changes: object) -> TravelAllowanceEvent:
    fields: dict[str, object] = {
        "event_date": _DAY,
        "days": 3,
        "daily_amount": Decimal("60.00"),
        "outside_municipality": True,
        "tfr_base": "none",
        "meals_lodging": "none",
    }
    fields.update(changes)
    return TravelAllowanceEvent(**fields)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("changes", "exempt", "reason"),
    [
        ({}, "139.44", "above_cap"),  # 3 x 46.48
        ({"meals_lodging": "one"}, "92.97", "above_cap"),  # 3 x 30.99
        ({"meals_lodging": "both"}, "46.47", "above_cap"),  # 3 x 15.49
        ({"abroad": True}, "180.00", "within_cap"),  # 60.00 < 77.47
        ({"abroad": True, "meals_lodging": "one"}, "154.95", "above_cap"),
        ({"abroad": True, "meals_lodging": "both"}, "77.46", "above_cap"),
        ({"outside_municipality": False}, "0.00", "within_municipality"),
    ],
    ids=[
        "italy",
        "italy_one",
        "italy_both",
        "abroad",
        "abroad_one",
        "abroad_both",
        "comune",
    ],
)
def test_exempt_part(changes: dict[str, object], exempt: str, reason: str) -> None:
    """3 days at 60.00: the exempt part is the days times the cap."""
    assessment = TravelAllowanceAssessment(_trip(**changes), _RULES, 2026)

    assert assessment.gross == Decimal("180.00")
    assert assessment.exempt == Decimal(exempt)
    assert assessment.taxable == Decimal("180.00") - Decimal(exempt)
    assert assessment.reason_code == reason


def test_caps_come_from_the_lire_amounts() -> None:
    """The bundled caps are the converted lire amounts, cited to art. 51 c. 5."""
    assert (_RULES.italy.none, _RULES.italy.one, _RULES.italy.both) == (
        Decimal("46.48"),
        Decimal("30.99"),
        Decimal("15.49"),
    )
    assert (_RULES.abroad.none, _RULES.abroad.one, _RULES.abroad.both) == (
        Decimal("77.47"),
        Decimal("51.65"),
        Decimal("25.82"),
    )
    assert _RULES.provenance is not None
    location = _RULES.provenance.location
    assert location is not None
    assert location.section == "art. 51 c. 5"


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"trasfertista": True}, "trasfertista"),
        ({"days": 0}, "days"),
        ({"daily_amount": Decimal(0)}, "daily_amount"),
        ({"meals_lodging": "dinner"}, "meals_lodging"),
        ({"tfr_base": "half"}, "tfr_base"),
        ({"daily_amount": None}, "hours_away"),
    ],
    ids=[
        "trasfertista",
        "no_days",
        "no_amount",
        "meals_lodging",
        "tfr_base",
        "no_amount_nor_hours",
    ],
)
def test_invalid_events_are_rejected(changes: dict[str, object], field: str) -> None:
    """A trasfertista is not supported; the other fields are validated."""
    with pytest.raises(InvalidInputError, match=field):
        _trip(**changes)


def _run(*events: object) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 28),
            ccnl_id="metalmeccanico-federmeccanica",
            level_code="C3",
            opening_state=PeriodState.zero(),
            events=tuple(events),  # type: ignore[arg-type]
        )
    )


def _account(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account), Decimal(0)
    )


def test_the_whole_allowance_is_paid_and_only_the_excess_is_income() -> None:
    """180.00 paid in cash; 40.56 above the cap is income like a bonus of 40.56.

    The INPS contributions and the taxable income grow as with a 40.56
    contract renewal increment (pay of the period, ordinary IRPEF).
    """
    base = _run()
    trip = _run(_trip())
    same = _run(BonusEvent(_DAY, Decimal("40.56"), kind="contract_renewal"))

    paid = _account(trip, AccountKind.CASH_EARNINGS) - _account(
        base, AccountKind.CASH_EARNINGS
    )
    assert paid == Decimal("180.00")
    assert _account(trip, AccountKind.EMPLOYEE_CONTRIBUTIONS) == _account(
        same, AccountKind.EMPLOYEE_CONTRIBUTIONS
    )
    assert (
        trip.closing_state.cash.earnings.taxable
        == same.closing_state.cash.earnings.taxable
    )
    (caller, decision) = sorted(
        (d for d in trip.decisions if d.capability == "travel_allowance"),
        key=lambda d: d.origin,
    )
    assert caller.reason_code == "caller_supplied_amount"
    assert decision.amount == Decimal("40.56")
    assert decision.inputs["daily_cap"] == Decimal("46.48")
    assert decision.rule == "tax/variable-pay-rules/2026"
    assert reconcile(trip, PeriodState.zero()).ok


def test_the_tfr_base_follows_the_event() -> None:
    """The CCNL decides whether the allowance enters the TFR base."""
    out = _run(_trip())
    included = _run(_trip(tfr_base="whole"))

    assert _account(included, AccountKind.TFR_ACCRUAL) > _account(
        out, AccountKind.TFR_ACCRUAL
    )


def test_events_without_the_rules_of_the_year_fail() -> None:
    """The event processor must be given the caps of the tax year."""
    year = 2026
    payment = date(year, 3, 28)
    with pytest.raises(
        ValueError, match=r"^the travel allowance rules of the tax year are not loaded$"
    ):
        _process_events(
            (_trip(),),
            CompetencePeriod(year=year, month=3),
            payment,
            "t",
            EffectiveDateContext.from_period(year, 3, payment),
            load_policy_resolver(),
            PolicyContext(year=year, as_of=date(year, 3, 1)),
            fringe_threshold_of(
                load_variable_pay_rules(year).fringe_benefit, year, with_children=False
            ),
        )


_DRIVER = "logistica-trasporto-confetra-viaggiante"


def _driver(*events: object) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 28),
            ccnl_id=_DRIVER,
            level_code="B3",
            opening_state=PeriodState.zero(),
            events=tuple(events),  # type: ignore[arg-type]
        )
    )


def _ccnl_trip(**changes: object) -> TravelAllowanceEvent:
    fields: dict[str, object] = {
        "event_date": _DAY,
        "days": 2,
        "outside_municipality": True,
        "meals_lodging": "none",
        "hours_away": Decimal(20),
    }
    fields.update(changes)
    return TravelAllowanceEvent(**fields)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("hours", "abroad", "paid"),
    [
        (Decimal(20), False, "88.18"),  # 2 x 43.16 + 2 x 0.93 (art. 16)
        (Decimal(13), False, "70.04"),  # 2 x 35.02
        (Decimal(20), True, "126.84"),  # 2 x 62.49 + 2 x 0.93
        (Decimal(5), False, "0.00"),  # under 6 hours: none (art. 62 c. 8)
    ],
    ids=["18_24", "12_18", "abroad", "under_6"],
)
def test_logistica_amount_of_the_hours_away(
    hours: Decimal, abroad: bool, paid: str
) -> None:
    """Without daily_amount the CCNL span of the hours away is paid."""
    result = _driver(_ccnl_trip(hours_away=hours, abroad=abroad))
    amount = sum(
        (i.amount for i in result.pay_items if i.kind == "travel_allowance_item"),
        Decimal(0),
    )
    assert amount == Decimal(paid)


def test_logistica_tfr_takes_the_part_above_the_exemption() -> None:
    """Art. 62 c. 7: only the excess over 46.48 a day enters the TFR base."""
    result = _driver(_ccnl_trip())
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "travel_allowance" and d.inputs.get("tfr_base")
    )
    assert decision.inputs["tfr_base"] == "above_exempt"
    # 43.16 is under the cap: only the 2 x 0.93 of art. 16 is income.
    assert decision.amount == Decimal("1.86")


def test_without_ccnl_amounts_the_daily_amount_is_required() -> None:
    """A CCNL without amounts rejects an event without daily_amount."""
    with pytest.raises(MissingRuleError, match="travel allowance amounts"):
        _run(_ccnl_trip(tfr_base="none"))


def test_without_ccnl_rule_the_tfr_base_is_required() -> None:
    """A CCNL without a TFR rule needs the event's tfr_base."""
    with pytest.raises(InvalidInputError, match="tfr_base"):
        _run(_trip(tfr_base=None))


def test_logistica_night_allowance_from_18_hours() -> None:
    """Art. 16: 0.93 for each day of 18 hours or more, income and TFR."""
    long_days = _driver(_ccnl_trip(hours_away=Decimal(20)))
    short_days = _driver(_ccnl_trip(hours_away=Decimal(13)))

    def night(result: PeriodResult) -> Decimal:
        (decision,) = (
            d
            for d in result.decisions
            if d.capability == "travel_allowance" and "night_allowance" in d.inputs
        )
        value = decision.inputs["night_allowance"]
        assert isinstance(value, Decimal)
        return value

    assert night(long_days) == Decimal("1.86")  # 2 x 0.93
    assert night(short_days) == Decimal("0.00")


def test_the_decision_records_every_fact_of_the_block() -> None:
    """The decision states the days, amounts, place, cap and hours away."""
    for hours, shown in ((Decimal(9), Decimal(9)), (None, "none")):
        assessment = TravelAllowanceAssessment(_trip(hours_away=hours), _RULES, 2026)
        decision = assessment.decision()

        assert _RULES.ruleset is not None
        assert _RULES.provenance is not None
        assert decision.rule == _RULES.ruleset.id
        assert decision.rule_version == _RULES.ruleset.version
        assert decision.source == _RULES.provenance.location
        assert decision.amount == Decimal("40.56")
        assert decision.inputs == {
            "days": "3",
            "daily_amount": Decimal("60.00"),
            "outside_municipality": "true",
            "abroad": "false",
            "meals_lodging": "none",
            "daily_cap": Decimal("46.48"),
            "exempt_amount": Decimal("139.44"),
            "hours_away": shown,
        }


def test_caps_without_a_ruleset_are_versioned_by_the_tax_year() -> None:
    """Caps given without a ruleset cite the feature and the tax year."""
    rules = _RULES.model_copy(update={"ruleset": None, "provenance": None})
    decision = TravelAllowanceAssessment(_trip(abroad=True), rules, 2026).decision()

    assert (decision.rule, decision.rule_version) == ("travel_allowance", "2026")
    assert decision.source is None
    assert decision.inputs["abroad"] == "true"


def test_the_item_splits_the_exempt_and_the_taxable_part() -> None:
    """The item pays the whole allowance and states both parts."""
    result = _run(_trip())
    (item,) = (i for i in result.pay_items if i.kind == "travel_allowance_item")
    (entry,) = (e for e in result.ledger_entries if e.pay_item_id == item.item_id)

    assert (item.amount, item.quantity) == (Decimal("180.00"), Decimal(3))
    assert item.exempt_amount == Decimal("139.44")
    assert item.taxable_amount == Decimal("40.56")
    assert entry.account is AccountKind.CASH_EARNINGS
    assert entry.policy_decision_id == "it/earning/travel_allowance"


def _night_of(result: PeriodResult) -> Decimal:
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "travel_allowance" and "night_allowance" in d.inputs
    )
    value = decision.inputs["night_allowance"]
    assert isinstance(value, Decimal)
    return value


def test_the_night_allowance_starts_at_18_hours_included() -> None:
    """Art. 16: a day of exactly 18 hours away earns the night allowance."""
    assert _night_of(_driver(_ccnl_trip(hours_away=Decimal(18)))) == Decimal("1.86")
    assert _night_of(_driver(_ccnl_trip(hours_away=Decimal("17.5")))) == Decimal(0)


def test_the_night_allowance_enters_the_tfr_base() -> None:
    """With the allowance out of the TFR base, the night part still enters it."""
    base = _account(_driver(), AccountKind.TFR_ACCRUAL)
    night = _driver(_ccnl_trip(tfr_base="none"))
    day = _driver(_ccnl_trip(tfr_base="none", hours_away=Decimal(13)))

    assert _account(night, AccountKind.TFR_ACCRUAL) > base
    assert _account(day, AccountKind.TFR_ACCRUAL) == base


def test_a_stated_amount_without_hours_earns_no_night_allowance() -> None:
    """The night allowance needs the hours away; a stated amount does not."""
    result = _driver(_ccnl_trip(hours_away=None, daily_amount=Decimal("40.00")))

    assert _night_of(result) == Decimal(0)


_CCNL_TRAVEL = json.loads(
    (KNOWLEDGE_DIR / "agreement" / f"{_DRIVER}.json").read_text(encoding="utf-8")
)["work_rules"]["travel_allowance"]


def _terms(**changes: object) -> TravelTerms:
    rules = CcnlTravelAllowance.model_validate(_CCNL_TRAVEL).model_copy(update=changes)
    return TravelTerms(rules, "ccnl/logistica/2026")


def _processed(
    event: TravelAllowanceEvent,
    terms: TravelTerms | None,
    rules: TravelAllowanceRules = _RULES,
) -> tuple[Decimal, tuple[CalculationDecision, ...]]:
    payment = date(2026, 3, 28)
    totals, items, _ = _process_events(
        (event,),
        CompetencePeriod(year=2026, month=3),
        payment,
        "t",
        EffectiveDateContext.from_period(2026, 3, payment),
        load_policy_resolver(),
        PolicyContext(year=2026, as_of=date(2026, 3, 1)),
        fringe_threshold_of(
            load_variable_pay_rules(2026).fringe_benefit, 2026, with_children=False
        ),
        travel_allowance=rules,
        ccnl_travel=terms,
    )
    return sum((i.amount for i in items), Decimal(0)), totals.decisions


def _process(event: TravelAllowanceEvent, terms: TravelTerms | None) -> Decimal:
    return _processed(event, terms)[0]


def test_caps_without_a_ruleset_cite_the_tax_year_of_the_run() -> None:
    """The run versions caps given without a ruleset by its own tax year."""
    rules = _RULES.model_copy(update={"ruleset": None})
    _, decisions = _processed(_trip(), None, rules)
    (decision,) = (d for d in decisions if d.reason_code == "above_cap")

    assert (decision.rule, decision.rule_version) == ("travel_allowance", "2026")


def test_a_ccnl_without_night_allowance_pays_the_day_amount_only() -> None:
    """A CCNL with day amounts but no night allowance pays the span alone."""
    assert _process(_ccnl_trip(), _terms(night_allowance=None)) == Decimal("86.32")


def test_without_ccnl_terms_the_event_states_amount_and_tfr_base() -> None:
    """With no CCNL terms the event's amount and TFR base are used as given."""
    trip = _trip(hours_away=Decimal(20), tfr_base="whole")

    assert _process(trip, None) == Decimal("180.00")
    with pytest.raises(MissingRuleError, match="state daily_amount"):
        _process(_ccnl_trip(tfr_base="whole"), None)
    with pytest.raises(InvalidInputError, match="tfr_base"):
        _process(_trip(tfr_base=None), None)


def _gap(series: dict[str, object]) -> dict[str, object]:
    return {"periods": [{**series["periods"][0], "valid_from": "2026-06-01"}]}  # type: ignore[index]


def test_a_ccnl_amount_not_yet_in_force_names_its_ruleset() -> None:
    """A day or night amount missing on the event date fails with its ruleset."""
    bands = [
        {**band, "italy": _gap(band["italy"]), "abroad": _gap(band["abroad"])}
        for band in _CCNL_TRAVEL["bands"]
    ]
    later_days = TravelTerms(
        CcnlTravelAllowance.model_validate({**_CCNL_TRAVEL, "bands": bands}),
        "ccnl/logistica/2026",
    )
    later_night = TravelTerms(
        CcnlTravelAllowance.model_validate({
            **_CCNL_TRAVEL,
            "night_allowance": _gap(_CCNL_TRAVEL["night_allowance"]),
        }),
        "ccnl/logistica/2026",
    )
    for terms in (later_days, later_night):
        with pytest.raises(MissingRuleError) as raised:
            _process(_ccnl_trip(), terms)
        assert raised.value.ruleset == "ccnl/logistica/2026"
        assert raised.value.feature == "travel_allowance"
        assert raised.value.as_of == _DAY


def test_the_errors_name_the_feature_the_field_and_the_day() -> None:
    """A missing amount or TFR rule names what to state, for which feature."""
    with pytest.raises(MissingRuleError) as missing:
        _run(_ccnl_trip(tfr_base="none"))
    with pytest.raises(InvalidInputError) as invalid:
        _run(_trip(tfr_base=None))

    assert missing.value.as_of == _DAY
    assert missing.value.feature == "travel_allowance"
    assert missing.value.ruleset is None
    assert missing.value.detail == (
        "the CCNL of the run has no travel allowance amounts: state daily_amount"
    )
    assert invalid.value.field == "TravelAllowanceEvent.tfr_base"
    assert invalid.value.feature == "travel_allowance"
    assert str(invalid.value).startswith(
        "TravelAllowanceEvent.tfr_base: the CCNL states no TFR rule for the "
        "allowance (art. 2120 c.c. leaves it to the CCNL): state it"
    )
