"""Art. 117, cached signed renewal PDF p. 72: A 195/208, B 173.

One A1 weekday overtime hour in March 2026: monthly EUR 1,240.42 / 195
x 1.15 = EUR 7.32, rather than EUR 8.25 using the old 173 divisor.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.events import OvertimeEvent, OvertimeKind
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.pay_item.facade import OvertimeEarning
from ccnl_engine.working_time.hourly.policies import HourlyTerms

_DAY = date(2026, 3, 10)
_AGREEMENT = "portieri-fabbricati-confedilizia"


def test_no_agreement_has_no_base_source() -> None:
    """Without a contract no source or hourly base is available."""
    assert HourlyTerms().base_source is None


@pytest.mark.parametrize(
    ("code", "divisor"),
    [
        ("A1", "195"),
        ("A2", "208"),
        ("A3", "195"),
        ("A4", "208"),
        ("A5", "195"),
        ("A6", "195"),
        ("A7", "208"),
        ("A8", "195"),
        ("A9", "208"),
    ],
)
def test_a_profile_hourly_base_uses_printed_coefficient(
    code: str, divisor: str
) -> None:
    """A1: 1240.42/195; A2: 1240.42/208, not 1240.42/173."""
    ccnl = load_ccnl(_AGREEMENT)
    amount = ccnl.level_by_code(code).base_salary.value_at(_DAY)
    assert amount is not None
    terms = HourlyTerms(
        ccnl=ccnl,
        level_code=code,
        chain=MonthlyPayChain(base=amount, seniority=Decimal(0), allowances=()),
    )
    base = terms.base(_DAY, "OvertimeEvent.hourly_rate", "overtime")
    assert base.divisor == Decimal(divisor)
    assert base.rate == amount / Decimal(divisor)


def test_a1_includes_printed_seniority_in_hourly_base() -> None:
    """Art. 120: (1240.42 + one EUR 10.00 step) / 195 = EUR 6.412410.../h."""
    ccnl = load_ccnl(_AGREEMENT)
    terms = HourlyTerms(
        ccnl=ccnl,
        level_code="A1",
        chain=MonthlyPayChain(
            base=Decimal("1240.42"), seniority=Decimal("10.00"), allowances=()
        ),
    )
    base = terms.base(_DAY, "OvertimeEvent.hourly_rate", "overtime")
    assert base.monthly == Decimal("1250.42")
    assert base.rate == Decimal("1250.42") / Decimal(195)


def test_b_profile_keeps_contract_divisor_and_unsourced_base() -> None:
    """B1's monthly EUR 1,519.10 still uses 173; its base needs a source."""
    ccnl = load_ccnl(_AGREEMENT)
    level = ccnl.level_by_code("B1")
    assert level.hourly_divisor is None
    assert ccnl.parameters.hourly_divisor.value_at(_DAY) == Decimal(173)
    terms = HourlyTerms(
        ccnl=ccnl,
        level_code="B1",
        chain=MonthlyPayChain(
            base=Decimal("1519.10"), seniority=Decimal(0), allowances=()
        ),
    )
    with pytest.raises(MissingRuleError, match="no verified hourly base"):
        terms.base(_DAY, "OvertimeEvent.hourly_rate", "overtime")


def test_b_profile_uses_contract_divisor_when_base_is_sourced() -> None:
    """With a verified base, B1 remains 1519.10/173, not 1519.10/195."""
    ccnl = load_ccnl(_AGREEMENT)
    assert ccnl.work_rules is not None
    supplements = ccnl.work_rules.time_supplements
    assert supplements is not None
    source = ccnl.level_by_code("A1").hourly_base_provenance
    assert source is not None
    rules = ccnl.work_rules.model_copy(
        update={
            "time_supplements": supplements.model_copy(
                update={"hourly_base_provenance": source}
            )
        }
    )
    sourced = ccnl.model_copy(update={"work_rules": rules})
    terms = HourlyTerms(
        ccnl=sourced,
        level_code="B1",
        chain=MonthlyPayChain(
            base=Decimal("1519.10"), seniority=Decimal(0), allowances=()
        ),
    )
    base = terms.base(_DAY, "OvertimeEvent.hourly_rate", "overtime")
    assert base.divisor == Decimal(173)
    assert base.rate == Decimal("1519.10") / Decimal(173)


def test_a1_overtime_hour_uses_level_divisor() -> None:
    """A1: one weekday hour x 115% x 1240.42/195 = EUR 7.32."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id=_AGREEMENT,
                level_code="A1",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
                seniority=SeniorityFact(0, date(2026, 1, 1), SenioritySource.PAYSLIP),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(
                events=(OvertimeEvent(_DAY, Decimal(1), kind=OvertimeKind.WEEKDAY),)
            ),
        )
    )
    assert sum(
        (item.amount for item in result.pay_items if isinstance(item, OvertimeEarning)),
        Decimal(0),
    ) == Decimal("7.32")
