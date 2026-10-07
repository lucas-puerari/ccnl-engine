"""Overtime multiplier: the caller's value prevails, else the CCNL band.

Expected amounts are ``hours x hourly_rate x multiplier`` rounded to cents,
with the multiplier ``1 + band`` read from the CCNL data:
metalmeccanico-federmeccanica (sez. quarta, titolo III, art. 7, lavoro non a
turni) OT_DIURNO 0.25 for the first two hours, OT_DIURNO_EXTRA 0.30 beyond,
OT_NOTTURNO 0.50; commercio-confcommercio (art. 149) OT_DIURNO 0.15 up to 48
weekly hours and OT_DIURNO_EXTRA 0.20 beyond.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.handlers._overtime_rate import (
    CALLER_MULTIPLIER_DIFFERS,
    CCNL_BAND_APPLIED,
    TIER_NOT_APPLIED,
    CCNLOvertimeBands,
    resolve_overtime_rate,
)
from ccnl_engine.payroll.application.handlers._standard_event import (
    _standard_event_gross,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus, DecisionOrigin
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.events import OvertimeEvent, OvertimeKind
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.provenance.domain.chain import ProvenanceStatus
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.fixtures.current_year import employment_only
from tests.fixtures.residence import COMUNE_BELFIORE, REGIONE
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult

_DAY = date(2026, 3, 10)
_METAL = "metalmeccanico-federmeccanica.json"
_RATE = Decimal("15.00")
#: Hired on 1 March: the March run is the first, opened by the zero state.
_HIRED = EmploymentPeriod(date(2026, 3, 1))


def _overtime(
    multiplier: Decimal | None = None, kind: OvertimeKind = OvertimeKind.WEEKDAY
) -> OvertimeEvent:
    return OvertimeEvent(_DAY, Decimal(10), _RATE, multiplier, kind)


def _run(event: OvertimeEvent, slug: str = _METAL, level: str = "C3") -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug=slug,
            level_code=level,
            seniority=new_hire(),
            tfr_treasury_fund=False,
            events=(event,),
            employment_period=_HIRED,
            current_year=employment_only(),
            regione=REGIONE,
            comune_belfiore=COMUNE_BELFIORE,
        )
    )


def _overtime_paid(result: PeriodResult) -> Decimal:
    (item,) = (i for i in result.pay_items if i.kind == "overtime_earning")
    return item.amount


def _codes(result: PeriodResult) -> list[str]:
    return [issue.code for issue in result.issues]


def test_no_multiplier_takes_the_ccnl_band() -> None:
    """Night: 10 h x 15.00 x (1 + 0.50) = 225.00, an engine decision."""
    result = _run(_overtime(kind=OvertimeKind.NIGHT))
    assert _overtime_paid(result) == Decimal("225.00")
    (band,) = (d for d in result.decisions if d.reason_code == CCNL_BAND_APPLIED)
    assert band.origin is DecisionOrigin.ENGINE
    assert band.status is CalculationStatus.FINAL
    assert band.inputs["band_code"] == "OT_NOTTURNO"
    assert band.inputs["multiplier"] == Decimal("1.50")
    assert band.rule.endswith("overtime_bands[OT_NOTTURNO]")
    assert band.source is not None
    (caller,) = (
        d
        for d in result.decisions
        if d.capability == "overtime" and d.origin is DecisionOrigin.CALLER_SUPPLIED
    )
    assert caller.inputs["fields"] == "hourly_rate"
    assert "caller_supplement" not in caller.inputs
    assert result.capability_report.rule_sources["overtime"] is ProvenanceStatus.ASSUMED
    assert result.issues == ()


def test_weekday_first_tier_is_applied_with_the_higher_tier_reported() -> None:
    """Weekday: 10 h x 15.00 x (1 + 0.25) = 187.50; the 30% tier is flagged."""
    result = _run(_overtime())
    assert _overtime_paid(result) == Decimal("187.50")
    (issue,) = (i for i in result.issues if i.code == TIER_NOT_APPLIED)
    assert "OT_DIURNO_EXTRA (1.30)" in issue.message
    assert result.assurance.calculation is CalculationStatus.PROVISIONAL


def test_explicit_multiplier_equal_to_the_band_raises_no_issue() -> None:
    """A caller 1.25 matches OT_DIURNO: caller-supplied, no difference."""
    result = _run(_overtime(Decimal("1.25")))
    assert _overtime_paid(result) == Decimal("187.50")
    assert result.issues == ()
    assert not [d for d in result.decisions if d.reason_code == CCNL_BAND_APPLIED]


def test_explicit_multiplier_different_from_the_band_prevails() -> None:
    """A caller 1.40 is applied (210.00) and reported against the bands."""
    result = _run(_overtime(Decimal("1.40")))
    assert _overtime_paid(result) == Decimal("210.00")
    (issue,) = (i for i in result.issues if i.code == CALLER_MULTIPLIER_DIFFERS)
    assert issue.status is CalculationStatus.PROVISIONAL
    assert "1.40" in issue.message
    assert "OT_DIURNO 1.25" in issue.message
    assert "OT_DIURNO_EXTRA 1.30" in issue.message
    assert result.assurance.calculation is CalculationStatus.PROVISIONAL


def test_no_band_and_no_multiplier_is_rejected() -> None:
    """A CCNL with no overtime band gives no multiplier: fail closed."""
    with pytest.raises(InvalidInputError, match="pass an explicit multiplier"):
        _run(_overtime(), "agenti-immobiliari-fiaip.json", "III")


def test_no_band_with_explicit_multiplier_has_nothing_to_compare() -> None:
    """Without a CCNL band the caller multiplier is applied with no issue."""
    result = _run(_overtime(Decimal("1.30")), "agenti-immobiliari-fiaip.json", "III")
    assert _overtime_paid(result) == Decimal("195.00")
    assert CALLER_MULTIPLIER_DIFFERS not in _codes(result)


def test_tiered_bands_apply_the_first_tier_provisionally() -> None:
    """Commercio: 15% applied to every hour, the 20% tier reported."""
    result = _run(_overtime(), "commercio-confcommercio.json", "4")
    assert _overtime_paid(result) == Decimal("172.50")
    (issue,) = (i for i in result.issues if i.code == TIER_NOT_APPLIED)
    assert "OT_DIURNO_EXTRA (1.20)" in issue.message
    (band,) = (d for d in result.decisions if d.reason_code == CCNL_BAND_APPLIED)
    assert band.status is CalculationStatus.PROVISIONAL


def test_explicit_multiplier_matching_a_higher_tier_raises_no_issue() -> None:
    """A caller 1.20 is the commercio OT_DIURNO_EXTRA tier: no difference."""
    result = _run(_overtime(Decimal("1.20")), "commercio-confcommercio.json", "4")
    assert CALLER_MULTIPLIER_DIFFERS not in _codes(result)


@pytest.mark.parametrize(
    ("slug", "kind"),
    [
        # Only bands beyond 40 weekly hours; LAVORO_NOTTURNO is ordinary work.
        ("impianti-sportivi-sport.json", OvertimeKind.WEEKDAY),
        ("impianti-sportivi-sport.json", OvertimeKind.NIGHT),
        # A band paid in EUR per hour is not a multiplier.
        ("dirigenza-sanitaria-area-sanita-aran.json", OvertimeKind.WEEKDAY),
    ],
)
def test_bands_that_give_no_multiplier_fail_closed(
    slug: str, kind: OvertimeKind
) -> None:
    """Thresholded, ordinary-work or per-hour bands give no multiplier."""
    bands = CCNLOvertimeBands.of(load_ccnl(slug), 2026)
    with pytest.raises(InvalidInputError, match="no first-tier percentage"):
        resolve_overtime_rate(_overtime(kind=kind), bands)


def test_band_not_in_force_on_the_event_date_fails_closed() -> None:
    """Metalmeccanico bands start in 2021: a 2020 event has no band."""
    bands = CCNLOvertimeBands.of(load_ccnl(_METAL), 2020)
    event = OvertimeEvent(date(2020, 3, 10), Decimal(1), _RATE)
    with pytest.raises(InvalidInputError, match="in force on that"):
        resolve_overtime_rate(event, bands)


def test_bands_of_a_ccnl_without_ruleset_cite_its_slug() -> None:
    """Without a ruleset the rule is cited by slug and competence year."""
    ccnl = load_ccnl(_METAL).model_copy(update={"ruleset": None})
    bands = CCNLOvertimeBands.of(ccnl, 2026)
    assert (bands.ruleset, bands.version) == (
        "ccnl/metalmeccanico-federmeccanica",
        "2026",
    )


def test_ccnl_without_work_rules_has_no_bands() -> None:
    """A CCNL with no work rules block has no overtime band."""
    ccnl = load_ccnl(_METAL).model_copy(update={"work_rules": None})
    assert CCNLOvertimeBands.of(ccnl, 2026).bands == ()


def test_gross_needs_a_resolved_multiplier() -> None:
    """The gross of an overtime event is computed only once it has a multiplier."""
    with pytest.raises(ValueError, match="must be resolved"):
        _standard_event_gross(_overtime())
