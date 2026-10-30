"""Every threshold of the bundle, just below, exactly at and just above it.

The cases are generated from the values the bundle declares, so a new year
or a changed threshold is tested without a new test:

- the IRPEF brackets of each year (TUIR art. 11): the marginal rate below
  and above each limit;
- the art. 13 c. 1 TUIR work deduction: the 15,000 flat tier, the formulas
  of the 28,000 and 50,000 tiers, and the 65 EUR increment from 25,000
  excluded to 35,000 included;
- the trattamento integrativo (D.L. 3/2020 art. 1 c. 1): due in full up to
  15,000 included, on the comparison of deductions up to 28,000 included,
  never above;
- the additional 1% IVS (D.L. 384/1992 art. 3-ter): charged on the pay of
  the month above the monthly threshold only;
- the pay tables of every CCNL: the day before, the day and the day after
  each tranche;
- the month counted in the ratei of a termination, on the day of the month
  each production CCNL names.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal
from functools import cache
from itertools import pairwise
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
)
from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.agreement.validity.rules import SeriesGapError
from ccnl_engine.contribution.additional_ivs.rules import (
    AdditionalIvsPosition,
    additional_ivs,
)
from ccnl_engine.inputs import EmploymentPeriod, Permanent
from ccnl_engine.irpef.deduction.rules import work_income_deduction
from ccnl_engine.irpef.rules import irpef_gross
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.tax_credit.rules import trattamento_integrativo_outcome
from scripts.provenance.rules import KNOWLEDGE_DIR
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.sector.models import YearRules

_D = Decimal
_YEARS = (2026, 2027)
_REPO = BundledKnowledgeRepository()
_STEP = _D(100)


@cache
def _rules(year: int) -> YearRules:
    return _REPO.load_year_rules(year, TaxSector.TERZIARIO, 20)


def _limits() -> list[tuple[int, Decimal, Decimal, Decimal]]:
    found = []
    for year in _YEARS:
        brackets = _rules(year).irpef_brackets
        found += [
            (year, low.up_to, low.rate, high.rate)
            for low, high in pairwise(brackets)
            if low.up_to is not None
        ]
    return found


@pytest.mark.parametrize(("year", "limit", "below", "above"), _limits())
def test_each_irpef_limit_changes_the_marginal_rate_at_the_limit(
    year: int, limit: Decimal, below: Decimal, above: Decimal
) -> None:
    """The last 100 EUR up to the limit pay its rate; the next 100 the next."""
    rules = _rules(year)
    at = irpef_gross(limit, rules)

    assert at - irpef_gross(limit - _STEP, rules) == _STEP * below
    assert irpef_gross(limit + _STEP, rules) - at == _STEP * above


def _ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    """Return a ratio of art. 13 TUIR, truncated to four decimals (c. 6).

    Returns:
        The truncated ratio.
    """
    return (numerator / denominator).quantize(_D("0.0001"), rounding=ROUND_DOWN)


@pytest.mark.parametrize("year", _YEARS)
def test_the_work_deduction_switches_tier_after_each_limit(year: int) -> None:
    """15,000 and 28,000 belong to the lower tier; 50,000 deducts nothing."""
    w = _rules(year).work_deduction

    def deduction(income: Decimal) -> Decimal:
        return work_income_deduction(income, constants=w)

    lo, mid, high = w.detr_lo, w.detr_mid, w.detr_high
    tier_b = w.detr_a + w.detr_b_coeff * _ratio(mid - (lo + 1), w.detr_b_span)
    tier_c = w.detr_a * _ratio(high - (mid + 1), w.detr_c_span)
    assert deduction(lo) == w.detr_flat
    assert deduction(lo + 1) == tier_b.quantize(_D("0.01"))
    assert deduction(mid) == w.detr_a + w.detr_increment
    assert deduction(mid + 1) == (tier_c + w.detr_increment).quantize(_D("0.01"))
    assert deduction(high) == 0
    assert deduction(high + 1) == 0


@pytest.mark.parametrize("year", _YEARS)
def test_the_65_eur_increment_runs_from_25000_excluded_to_35000_included(
    year: int,
) -> None:
    """Art. 13 c. 1-bis TUIR: the increment opens above 25,000, closes after 35,000."""
    w = _rules(year).work_deduction

    def jump(income: Decimal) -> Decimal:
        return work_income_deduction(income + 1, constants=w) - work_income_deduction(
            income, constants=w
        )

    assert jump(w.increment_lo) > 0
    assert jump(w.increment_lo) - jump(w.increment_lo + 1) == pytest.approx(
        w.detr_increment, abs=1
    )
    assert jump(w.increment_hi) < 0
    assert -jump(w.increment_hi) - (-jump(w.increment_hi + 1)) == pytest.approx(
        w.detr_increment, abs=1
    )


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize(
    ("offset", "reason"),
    [
        ("-0.01", "full_amount"),
        ("0", "full_amount"),
        ("0.01", "deductions_above_irpef"),
    ],
)
def test_the_trattamento_is_due_in_full_up_to_15000_included(
    year: int, offset: str, reason: str
) -> None:
    """Above the middle threshold the deductions must exceed the gross tax."""
    rules = _rules(year)
    ti = rules.trattamento_integrativo
    assert ti is not None
    income = ti.threshold_mid + _D(offset)
    work = work_income_deduction(income, constants=rules.work_deduction)

    outcome = trattamento_integrativo_outcome(
        income,
        irpef_gross(income, rules),
        work,
        work + _D(3000),
        ti,
        constants=rules.work_deduction,
    )

    assert outcome.reason_code == reason


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize(
    ("offset", "above"), [("-0.01", False), ("0", False), ("0.01", True)]
)
def test_no_trattamento_above_28000(year: int, offset: str, *, above: bool) -> None:
    """28,000 included is the last income the credit can be due on."""
    rules = _rules(year)
    ti = rules.trattamento_integrativo
    assert ti is not None
    income = ti.threshold_upper + _D(offset)
    work = work_income_deduction(income, constants=rules.work_deduction)

    outcome = trattamento_integrativo_outcome(
        income,
        irpef_gross(income, rules),
        work,
        work,
        ti,
        constants=rules.work_deduction,
    )

    assert (outcome.reason_code == "income_above_upper_threshold") is above


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize(("offset", "base"), [(-1, 0), (0, 0), (1, 1), (100, 100)])
def test_the_additional_ivs_starts_above_the_monthly_threshold(
    year: int, offset: int, base: int
) -> None:
    """The 1% is charged on the pay of the month above the threshold only."""
    inps = _rules(year).inps
    assert inps is not None
    rule = inps.employee_additional
    assert rule is not None
    pay = rule.monthly_threshold + offset

    component = additional_ivs(
        rule, pay, ytd_base=pay, ceiling=None, position=AdditionalIvsPosition()
    )

    if base == 0:
        assert component is None
    else:
        assert component is not None
        assert component.base == _D(base)
        assert component.amount == (_D(base) * rule.rate).quantize(_D("0.01"))


def _tranches() -> list[tuple[str, str, date, Decimal, Decimal]]:
    found = []
    for path in sorted((KNOWLEDGE_DIR / "agreement").glob("*.json")):
        ccnl = _REPO.load_ccnl(path.stem)
        for level in ccnl.levels:
            periods = level.base_salary.periods
            found += [
                (path.stem, level.code, nxt.valid_from, prev.value, nxt.value)
                for prev, nxt in pairwise(periods)
                if prev.valid_until == nxt.valid_from
                and prev.value is not None
                and nxt.value is not None
            ]
    return found


_TRANCHES = _tranches()


_ONE_DAY = timedelta(days=1)


def test_each_tranche_starts_on_its_day() -> None:
    """The day before pays the old table, the day and the day after the new."""
    wrong = []
    for ccnl, level, start, old, new in _TRANCHES:
        series = _REPO.load_ccnl(ccnl).level_by_code(level).base_salary
        try:
            before = series.value_at(start - timedelta(days=1))
        except SeriesGapError:  # pragma: no cover - a gap is no tranche
            continue
        found = (before, series.value_at(start), series.value_at(start + _ONE_DAY))
        if found != (old, new, new):
            wrong.append((ccnl, level, start, found))
    assert wrong == []


_ENGINE = PayrollEngine.bundled()
#: Day of the month from which a month of employment counts in the ratei.
_COUNTED_FROM = {
    ("commercio-confcommercio", "4"): 15,
    ("pubblici-esercizi-fipe-angem-ristorazione-collettiva", "4"): 15,
    ("metalmeccanico-federmeccanica", "C3"): 16,
    ("edilizia-ance-impiegati", "4"): 16,
}


def _ratei(ccnl: str, level: str, last_day: int) -> Decimal:
    employment = Employment(
        ccnl_id=ccnl,
        level_code=level,
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2026, 1, 1), date(2026, 6, last_day)),
        contract_type=Permanent(),
    )
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=employment,
            employer=EmployerProfile(headcount=Headcount(20)),
        )
    )
    (june,) = (r for r in year.period_results if r.run == PayrollRun.regular(2026, 6))
    return sum(
        (i.quantity for i in june.pay_items if i.kind == "extra_month_earning"),
        _D(0),
    )


@pytest.mark.parametrize(("ccnl", "level"), sorted(_COUNTED_FROM))
def test_the_month_of_leaving_counts_from_the_day_the_ccnl_names(
    ccnl: str, level: str
) -> None:
    """Leaving on the day before: five twelfths; on the day: six."""
    day = _COUNTED_FROM[ccnl, level]

    twelfths = [_ratei(ccnl, level, d) * 12 for d in (day - 1, day, day + 1)]

    assert [t.quantize(_D(1)) for t in twelfths] == [5, 6, 6]
