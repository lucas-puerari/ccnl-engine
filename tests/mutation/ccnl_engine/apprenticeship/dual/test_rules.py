"""Hand oracle: first- and third-level apprentices of the Industria alimentare.

FLAI text of the CCNL 2023-2027 (sha256 11792ad3…), art. 21 B and C (PDF
pp. 56 and 58).  June 2026: level 3A T.E.M. 1,746.84, I.A.R. 95.26.

- First level, qualifica, second school year: 55% of T.E.M. and I.A.R. at
  the conventional level 3A on the work hours, 20% on the training at the
  employer, nothing on the school hours.  60 school, 20 training and 80
  work hours: (80 x 0.55 + 20 x 0.20) / 160 = 0.30 of T.E.M. and I.A.R.;
  1,746.84 x 0.30 = 524.052 -> 524.05, 95.26 x 0.30 = 28.578 -> 28.58.
- Third level, programme of 24 months: two levels below the destination in
  the first half, one below in the second; one below in a programme of at
  most 12 months.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from importlib.resources import files
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.apprenticeship.dual.models import DualPeriod, DualTrack
from ccnl_engine.apprenticeship.dual.rules import dual_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.apprentice.inputs import (
    Apprentice,
    ApprenticeshipProgramme,
    DualHours,
)
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import (
    InvalidInputError,
    MissingRequiredFactError,
    OutOfScopeError,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.interchange.request.serializers import (
    request_from_json,
    request_to_json,
)

if TYPE_CHECKING:
    from ccnl_engine.compensation.element.types import MonthlyPayChain

_CCNL = load_ccnl("alimentari-federalimentare")
_JUNE = date(2026, 6, 1)
_FIRST = ApprenticeshipProgramme.FIRST_LEVEL
_THIRD = ApprenticeshipProgramme.THIRD_LEVEL
_HOURS = DualHours(Decimal(60), Decimal(20), Decimal(80))


def _chain(apprentice: Apprentice, level: str = "3") -> MonthlyPayChain:
    return dual_chain(
        _CCNL,
        _CCNL.level_by_code(level),
        apprentice,
        0,
        frozenset(),
        _JUNE,
        worker_category=None,
        seniority_months=None,
    )


def _pay(chain: MonthlyPayChain) -> dict[str, Decimal]:
    return {"base": chain.base, **{a.code: v for a, v in chain.allowances if v}}


def _first(**facts: object) -> Apprentice:
    return Apprentice(9, programme=_FIRST, **facts)  # type: ignore[arg-type]


def test_a_second_year_qualifica_apprentice() -> None:
    """T.E.M. and I.A.R. of 3A at 0.30; no contingenza, EDR or scatti."""
    chain = _chain(_first(track="qualifica", school_year=2, hours=_HOURS))
    assert _pay(chain) == {"base": Decimal("524.05"), "IAR": Decimal("28.58")}
    assert chain.seniority == 0


def test_the_destination_level_does_not_change_the_first_level_pay() -> None:
    """Level 3A by convention, whatever the destination."""
    apprentice = _first(track="qualifica", school_year=2, hours=_HOURS)
    assert _pay(_chain(apprentice, "1S")) == _pay(_chain(apprentice, "6"))


def test_only_school_hours_pay_nothing() -> None:
    """A month spent at school pays nothing."""
    hours = DualHours(Decimal(160), Decimal(0), Decimal(0))
    chain = _chain(_first(track="qualifica", school_year=3, hours=hours))
    assert _pay(chain) == {"base": Decimal(0)}


def test_the_first_school_year_of_a_qualifica_is_not_paid() -> None:
    """The table starts from the second year."""
    with pytest.raises(OutOfScopeError, match="sets no pay for school year 1"):
        _chain(_first(track="qualifica", school_year=1, hours=_HOURS))


def test_a_one_year_course_needs_no_school_year() -> None:
    """Certificato IFTS, anno unico: 70%."""
    hours = DualHours(Decimal(0), Decimal(0), Decimal(100))
    chain = _chain(_first(track="certificato_ifts", hours=hours))
    assert chain.base == Decimal("1222.79")  # 1,746.84 x 0.70 = 1,222.788


def test_the_course_is_needed_among_five() -> None:
    """Five first-level tracks cover every level: the course must be named."""
    with pytest.raises(OutOfScopeError, match="5 first_level apprenticeship tracks"):
        _chain(_first(school_year=2, hours=_HOURS))


@pytest.mark.parametrize(
    ("facts", "missing"),
    [
        ({"track": "qualifica", "hours": _HOURS}, "Apprentice.school_year"),
        ({"track": "qualifica", "school_year": 2}, "the hours"),
    ],
)
def test_a_missing_fact_blocks(facts: dict[str, object], missing: str) -> None:
    """No school year, no hours: the pay cannot be computed."""
    with pytest.raises(MissingRequiredFactError, match=missing):
        _chain(_first(**facts))


@pytest.mark.parametrize(
    ("months", "elapsed", "level"),
    [(24, 11, "3A"), (24, 12, "2"), (24, 13, "2"), (12, 3, "2")],
)
def test_the_third_level_by_half_and_length(
    months: int, elapsed: int, level: str
) -> None:
    """Destination 1: level 3A (two below) before month 12 of 24, then 2.

    Month 12 of 24 is the second half; a programme of 12 months pays
    level 2 (one below) throughout.
    """
    hours = DualHours(Decimal(0), Decimal(0), Decimal(160))
    apprentice = Apprentice(
        elapsed, programme=_THIRD, programme_months=months, hours=hours
    )
    paid = _CCNL.level_by_code(level)
    assert _chain(apprentice, "1").base == paid.base_salary.value_at(_JUNE)


def test_the_third_level_needs_the_programme_length() -> None:
    """The half and the length are read off Apprentice.programme_months."""
    with pytest.raises(MissingRequiredFactError, match="programme_months"):
        _chain(Apprentice(3, programme=_THIRD, hours=_HOURS), "1")


def test_a_ccnl_without_dual_tracks_refuses_the_programme() -> None:
    """Commercio sets no dual track in the data: out of scope."""
    ccnl = load_ccnl("commercio-confcommercio")
    level = ccnl.levels[0]
    with pytest.raises(OutOfScopeError, match="0 first_level"):
        dual_chain(
            ccnl,
            level,
            _first(hours=_HOURS),
            0,
            frozenset(),
            _JUNE,
            worker_category=None,
            seniority_months=None,
        )


def test_training_on_the_work_pay_scales_by_the_work_rate() -> None:
    """A CCNL paying 10% of the work pay (Agricoli All. F): 0.10 x 0.55."""
    (track,) = (t for t in _CCNL.dual_apprenticeship if t.name == "qualifica")
    on_work = track.model_copy(
        update={
            "company_training_on": "work",
            "company_training_rate": Decimal("0.10"),
            "work_elements": None,
            "company_training_elements": None,
        }
    )
    ccnl = _CCNL.model_copy(update={"dual_apprenticeship": (on_work,)})
    hours = DualHours(Decimal(0), Decimal(100), Decimal(0))
    chain = dual_chain(
        ccnl,
        ccnl.level_by_code("3"),
        _first(school_year=2, hours=hours),
        0,
        frozenset(),
        _JUNE,
        worker_category=None,
        seniority_months=None,
    )
    assert chain.base == Decimal("96.08")  # 1,746.84 x 0.055 = 96.0762


def test_a_track_repeating_a_period_is_rejected() -> None:
    """Two periods with the same selectors would be ambiguous."""
    (track,) = (t for t in _CCNL.dual_apprenticeship if t.name == "qualifica")
    period = DualPeriod(school_year=2, work_rate=Decimal("0.5"))
    with pytest.raises(ValueError, match="repeats a period"):
        DualTrack.model_validate({**track.model_dump(), "periods": [period, period]})


def test_a_track_naming_an_unknown_level_is_rejected() -> None:
    """The CCNL checks the levels of its dual tracks."""
    raw = json.loads(
        (
            files("ccnl_engine") / "knowledge/agreement/alimentari-federalimentare.json"
        ).read_text(encoding="utf-8")
    )
    raw["dual_apprenticeship"][0]["reference_level"] = "9Z"
    with pytest.raises(ValueError, match="unknown levels"):
        type(_CCNL).model_validate(raw)


@pytest.mark.parametrize(
    "hours",
    [(Decimal(-1), Decimal(0), Decimal(1)), (Decimal(0), Decimal(0), Decimal(0))],
)
def test_hours_must_be_non_negative_and_some(hours: tuple[Decimal, ...]) -> None:
    """Negative hours, or none at all, are rejected."""
    with pytest.raises(InvalidInputError):
        DualHours(*hours)


def _period_input(apprentice: Apprentice) -> PeriodInput:
    hired = date(2025, 9, 1)
    return PeriodInput(
        run=PayrollRun.regular(2026, 6),
        payment_date=date(2026, 6, 27),
        employment=Employment(
            ccnl_id="alimentari-federalimentare",
            level_code="3",
            contract_type=apprentice,
            employment_period=EmploymentPeriod(hired, None),
            seniority=SeniorityFact.since(hired, SenioritySource.EMPLOYER_RECORDS),
            pension_fund=NoPensionFund(),
            category=WorkerCategory.OPERAIO,
        ),
        employer=EmployerProfile(headcount=Headcount(60), subsector="carni"),
    )


def test_a_period_of_a_first_level_apprentice() -> None:
    """The run posts the weighed T.E.M. and I.A.R., and no contingenza."""
    apprentice = _first(track="qualifica", school_year=2, hours=_HOURS)
    result = PayrollEngine.bundled().calculate_period(_period_input(apprentice))
    pay = {i.item_id: i.amount for i in result.pay_items}
    assert pay["base_salary_2026-06-regular"] == Decimal("524.05")
    assert pay["allowance_IAR_2026-06-regular"] == Decimal("28.58")
    assert "allowance_CONTINGENZA_2026-06-regular" not in pay


def test_the_request_keeps_the_programme_and_the_hours() -> None:
    """A stored request reads back the same apprentice."""
    apprentice = _first(track="qualifica", school_year=2, hours=_HOURS)
    request = _period_input(apprentice)
    assert request_from_json(request_to_json(request), PeriodInput) == request


@pytest.mark.parametrize(
    ("elapsed", "rate"),
    [(0, "0.65"), (5, "0.65"), (6, "0.70"), (11, "0.70"), (12, "0.90"), (40, "0.90")],
)
def test_the_months_of_the_contract_select_the_period(elapsed: int, rate: str) -> None:
    """Edilizia art. 92 pays by semester: months 0-5, 6-11, then from 12."""
    (track,) = (t for t in _CCNL.dual_apprenticeship if t.name == "certificato_ifts")
    by_semester = track.model_copy(
        update={
            "periods": (
                DualPeriod(months_until=6, work_rate=Decimal("0.65")),
                DualPeriod(months_from=6, months_until=12, work_rate=Decimal("0.70")),
                DualPeriod(months_from=12, work_rate=Decimal("0.90")),
            )
        }
    )
    ccnl = _CCNL.model_copy(update={"dual_apprenticeship": (by_semester,)})
    hours = DualHours(Decimal(0), Decimal(0), Decimal(100))
    chain = dual_chain(
        ccnl,
        ccnl.level_by_code("3"),
        Apprentice(elapsed, programme=_FIRST, hours=hours),
        0,
        frozenset(),
        _JUNE,
        worker_category=None,
        seniority_months=None,
    )
    assert chain.base == (Decimal("1746.84") * Decimal(rate)).quantize(Decimal("0.01"))
