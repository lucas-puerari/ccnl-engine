"""Maternity leave and work injury of the pilots turismo and chimica.

Statutory measures (bundle ``absence/insured``):

- maternity, D.Lgs. 151/2001 artt. 22-23: 80% of the pay of the month
  before over thirty, plus the daily rateo of the extra months, for every
  calendar day of the leave;
- work injury, D.P.R. 1124/1965 artt. 68, 73, 116-117: the injury day paid
  in full by the employer and never deducted, the three days after it at
  the waiting-period rate (60% by law), from the fourth day the INAIL
  indemnity, 60% of the daily base to the ninetieth day and 75% after it;
  the daily base is the monthly pay over the CCNL monthly hours times the
  weekly hours over six.

CCNL treatment:

- turismo Federalberghi art. 179 (p. 153): "un'integrazione dell'indennità
  a carico dell'INPS [...] in modo da raggiungere complessivamente la
  misura del cento per cento della retribuzione giornaliera netta" for five
  months; art. 172 (p. 149): the INAIL indemnity is advanced to the worker
  "assunto a tempo indeterminato"; the waiting period at 60% (art. 170
  c. 3), no top-up of the INAIL share;
- chimica Federchimica art. 41: "fino a raggiungere il 100% della normale
  retribuzione globale di fatto per i primi cinque mesi di assenza" (gross);
  art. 40 C: "intera retribuzione netta per tre mesi", the waiting period
  paid in full and the INAIL indemnity advanced.

Turismo level 4: 1660.69 EUR a month to May 2026 (1695.69 from June),
daily quota by 26, 172 monthly hours, fourteen monthly payments, worker
INPS rate 9.75667%.  Chimica D1: 2360.26 EUR a month to June 2026 (2420.26
from July), hourly quota of 8 hours on 175 monthly hours, thirteen monthly
payments, worker INPS rate 9.49%.  Amounts are rounded half up to the cent.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import MaternityLeaveEvent, WorkInjuryEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    FixedTerm,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.pay_item.facade import (
    AbsenceDeduction,
    AbsenceIntegrationItem,
    MaternityItem,
    WorkInjuryItem,
)

if TYPE_CHECKING:
    from ccnl_engine.employment.inputs import Contract
    from ccnl_engine.events import WorkEvent
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2025, 1, 1)
_ENGINE = PayrollEngine.bundled()
_TURISMO = ("turismo-federalberghi", "4")
_CHIMICA = ("chimica-farmaceutica-federchimica", "D1")
_LEAVE = MaternityLeaveEvent(date(2026, 3, 1), date(2026, 7, 31))
_ITEMS = (AbsenceDeduction, AbsenceIntegrationItem, MaternityItem, WorkInjuryItem)


def _run(
    ccnl: tuple[str, str],
    event: WorkEvent,
    month: int,
    contract: Contract | None = None,
) -> PeriodResult:
    ccnl_id, level = ccnl
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                contract_type=contract or Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=(event,)),
        )
    )


def _lines(result: PeriodResult) -> dict[str, tuple[Decimal, Decimal]]:
    return {
        item.item_id.rsplit("_", 1)[1]: (item.amount, item.absence_days)
        for item in result.pay_items
        if isinstance(item, _ITEMS)
    }


def _minimum_reason(result: PeriodResult) -> object:
    decision = next(d for d in result.decisions if d.capability == "inps_employee")
    return decision.inputs.get("minimum_base_reason")


class TestMaternity:
    """The INPS indemnity and the CCNL top-up of a leave from 1 March."""

    def test_turismo_pays_the_inps_share_alone_when_it_tops_the_net(self) -> None:
        """March: 1660.69 deducted on 26 days; 1601.64 paid for INPS.

        Daily pay 1660.69 / 30 + 1660.69 * 2 / 360 = 55.3563 + 9.2261 =
        64.5824; 0.80 * 64.5824 * 31 = 1601.64.  Free of contributions, the
        INPS share stands for 1601.64 / (1 - 0.0975667) = 1774.80 of gross
        pay, above the 1660.69 the top-up reaches: no top-up.
        """
        result = _run(_TURISMO, _LEAVE, 3)

        assert _lines(result) == {
            "abs": (Decimal("1660.69"), Decimal(26)),
            "inps": (Decimal("1601.64"), Decimal(31)),
        }
        assert _minimum_reason(result) == "indemnified_month"

    def test_chimica_tops_the_inps_share_up_to_the_gross_pay(self) -> None:
        """March: 2360.26 deducted on 175 hours; 2113.74 INPS, 246.52 top-up.

        Daily pay 2360.26 / 30 + 2360.26 / 360 = 78.6753 + 6.5563 =
        85.2316; 0.80 * 85.2316 * 31 = 2113.74; the gross top-up is
        2360.26 - 2113.74 = 246.52.
        """
        result = _run(_CHIMICA, _LEAVE, 3)

        assert _lines(result) == {
            "abs": (Decimal("2360.26"), Decimal(175)),
            "inps": (Decimal("2113.74"), Decimal(31)),
            "intg": (Decimal("246.52"), Decimal(31)),
        }

    def test_chimica_tops_up_only_the_first_five_months(self) -> None:
        """July: 150 days from 1 March end on 28 July, so 28 of 31 days.

        2420.26 deducted; INPS (2420.26 / 30 + 2420.26 / 360) * 0.80 * 31
        = 2167.48; top-up (2420.26 - 2167.48) * 28 / 31 = 228.32.
        """
        result = _run(_CHIMICA, _LEAVE, 7)

        assert _lines(result) == {
            "abs": (Decimal("2420.26"), Decimal(175)),
            "inps": (Decimal("2167.48"), Decimal(31)),
            "intg": (Decimal("228.32"), Decimal(31)),
        }

    def test_chimica_pays_no_top_up_after_five_months(self) -> None:
        """August, past 28 July: INPS alone, 2167.48 as in July.

        The whole month is away: 2420.26 is deducted in full, though its 21
        working days hold 168 of the 175 monthly hours.
        """
        leave = MaternityLeaveEvent(date(2026, 3, 1), date(2026, 8, 31))
        result = _run(_CHIMICA, leave, 8)

        assert _lines(result) == {
            "abs": (Decimal("2420.26"), Decimal(175)),
            "inps": (Decimal("2167.48"), Decimal(31)),
        }


class TestWorkInjury:
    """The waiting period, the INAIL share and the CCNL top-up."""

    def test_turismo_advances_inail_to_a_permanent_worker(self) -> None:
        """Injury on Tuesday 10 March, inability to 31 March.

        The injury day is paid in full.  11-31 March are 18 days of a
        26-day month (Sundays out): 1660.69 * 18 / 26 = 1149.71 deducted.
        Waiting period 11-13 March: 1660.69 * 3 / 26 * 0.60 = 114.97.
        INAIL from 14 March, 18 calendar days: daily base 1660.69 / 172 *
        40 / 6 = 64.3678; 18 * 0.60 * 64.3678 = 695.17, advanced.  The base
        of the month is not fully indemnified: its minimum is undetermined.
        """
        result = _run(
            _TURISMO, WorkInjuryEvent(date(2026, 3, 10), date(2026, 3, 31)), 3
        )

        assert _lines(result) == {
            "abs": (Decimal("1149.71"), Decimal(18)),
            "crnz": (Decimal("114.97"), Decimal(3)),
            "inail": (Decimal("695.17"), Decimal(18)),
        }
        assert _minimum_reason(result) == "absence_in_month"

    def test_turismo_leaves_inail_to_a_fixed_term_worker(self) -> None:
        """June, days 83-112 after the injury: INAIL pays the worker itself.

        The month is deducted in full, 1695.69, and nothing is posted for
        INAIL; the INAIL measure is still recorded in the decision.
        """
        injury = WorkInjuryEvent(date(2026, 3, 10), date(2026, 6, 30))
        result = _run(_TURISMO, injury, 6, FixedTerm())

        assert _lines(result) == {"abs": (Decimal("1695.69"), Decimal(26))}
        decision = next(
            d for d in result.decisions if d.capability == "workplace_injury"
        )
        assert decision.inputs["indemnity_advanced"] == "no"
        assert decision.amount == Decimal(0)
        assert _minimum_reason(result) == "indemnified_month"

    def test_chimica_tops_inail_up_to_the_net_pay(self) -> None:
        """April, days 22-51 after the injury of 10 March.

        Daily base 2360.26 / 175 * 40 / 6 = 89.9147; 30 * 0.60 * 89.9147 =
        1618.46.  The net top-up reaches 2360.26: 2360.26 - 1618.46 / (1 -
        0.0949) = 2360.26 - 1788.16 = 572.10.
        """
        injury = WorkInjuryEvent(date(2026, 3, 10), date(2026, 6, 30))
        result = _run(_CHIMICA, injury, 4)

        assert _lines(result) == {
            "abs": (Decimal("2360.26"), Decimal(175)),
            "inail": (Decimal("1618.46"), Decimal(30)),
            "intg": (Decimal("572.10"), Decimal(30)),
        }

    def test_the_inail_rate_rises_after_the_ninetieth_day(self) -> None:
        """June, days 83-112: 8 days at 60% and 22 at 75%.

        Daily base 2360.26 / 175 * 40 / 6 = 89.9147; (8 * 0.60 + 22 *
        0.75) * 89.9147 = 21.3 * 89.9147 = 1915.18.
        """
        injury = WorkInjuryEvent(date(2026, 3, 10), date(2026, 6, 30))
        result = _run(_CHIMICA, injury, 6)

        assert _lines(result)["inail"] == (Decimal("1915.18"), Decimal(30))

    def test_the_injury_day_alone_deducts_nothing(self) -> None:
        """The employer pays the injury day: no line is posted."""
        result = _run(
            _TURISMO, WorkInjuryEvent(date(2026, 3, 10), date(2026, 3, 10)), 3
        )

        assert _lines(result) == {}
