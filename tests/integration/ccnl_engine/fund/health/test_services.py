"""Contractual funds of a run: the shares when paid, the element when not.

A synthetic fund is added to the bundled Turismo Federalberghi, level 4
(minimo 1,695.69 EUR from 1 May 2026): employer 10 EUR and worker 2 EUR a
month, a health fund (worker share out of the IRPEF base, 10% INPS
solidarity on the employer share), and an elemento distinto of 16 EUR for 14
months when the employer does not pay it.  A second fund, a bilateral body
on 0.10% of the minimo from the employer, covers the quadri only.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.fund.health.models import ContractualFund, FundAmount
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    EmploymentPeriod,
    EmploymentSector,
    FamilyComposition,
    FixedTerm,
    IncomeEstimateQuality,
    NoPensionFund,
    PeriodState,
    Permanent,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.provenance.source.rule.models import (
    ProvenanceStatus,
    RuleProvenance,
)
from ccnl_engine.results import AccountKind, BlockerCode

if TYPE_CHECKING:
    from ccnl_engine.agreement.models import CCNL

_HIRED = date(2026, 1, 1)
_SOURCE = RuleProvenance(
    status=ProvenanceStatus.DERIVED,
    location=SourceLocation(
        source_document=SourceDocument(
            document_id="ccnl", title="CCNL", kind=SourceKind.ASSOCIAZIONE
        ),
        quote="10 euro a carico dell'azienda e 2 euro a carico del lavoratore",
    ),
)


def _flat(value: str) -> TimeSeries:
    return TimeSeries(
        periods=(
            ValidityPeriod(
                valid_from=date(2020, 1, 1), valid_until=None, value=Decimal(value)
            ),
        )
    )


_HEALTH = ContractualFund(
    code="fondo_test",
    description="Fondo sanitario di prova",
    employer=FundAmount(monthly=_flat("10")),
    employee=FundAmount(monthly=_flat("2")),
    employee_deductible=True,
    solidarity_rate=Decimal("0.10"),
    alternative=FundAmount(monthly=_flat("16")),
    alternative_extra_months=True,
    permanent_only=True,
    provenance=_SOURCE,
)
_QUADRI = ContractualFund(
    code="ente_quadri",
    description="Ente bilaterale dei quadri",
    categories=frozenset({WorkerCategory.QUADRO}),
    employer=FundAmount(rate=_flat("0.001")),
    provenance=_SOURCE,
)


class _FundRepository(BundledKnowledgeRepository):
    """The bundle, with the two funds on Turismo."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        ccnl = super().load_ccnl(ccnl_id)
        parameters = ccnl.parameters.model_copy(
            update={"health_funds": (_HEALTH, _QUADRI)}
        )
        return ccnl.model_copy(update={"parameters": parameters})


_ENGINE = PayrollEngine(repository=_FundRepository())


def _run(
    funds: frozenset[str] | None,
    *,
    run: PayrollRun | None = None,
    contract: Permanent | FixedTerm | None = None,
    weekly_hours: WeeklyHours | None = None,
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=run or PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27) if run is None else date(2026, 12, 15),
            employment=Employment(
                ccnl_id="turismo-federalberghi",
                level_code="4",
                contract_type=contract or Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                weekly_hours=weekly_hours,
                full_time_weekly_hours=None
                if weekly_hours is None
                else WeeklyHours(Decimal(40)),
            ),
            employer=EmployerProfile(headcount=Headcount(60), contractual_funds=funds),
            facts=PeriodFacts(family_composition=FamilyComposition()),
        )
    )


def _posted(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account is account), Decimal(0)
    )


def test_unstated_funds_are_a_missing_fact() -> None:
    """Without the fact nothing is posted and the run names it."""
    result = _run(None)

    assert (BlockerCode.MISSING_FACT, "contractual_funds", "contractual_funds") in {
        (b.code, b.feature, b.detail) for b in result.blockers
    }
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == 0
    assert not result.is_payable


def test_a_paid_fund_posts_both_shares_and_the_solidarity() -> None:
    """Employer 10, worker 2, INPS solidarity 1.00; the worker share is deducted."""
    paid = _run(frozenset({"fondo_test"}))
    solidarity = [
        e.amount for e in paid.ledger_entries if e.entry_id.endswith("_solidarity")
    ]

    assert _posted(paid, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("10.00")
    assert _posted(paid, AccountKind.BILATERAL_FUND_EMPLOYEE) == Decimal("2.00")
    assert solidarity == [Decimal("1.00")]
    (decision,) = [d for d in paid.decisions if d.capability == "contractual_funds"]
    assert (decision.reason_code, decision.inputs["fund"]) == (
        "fund_paid",
        "fondo_test",
    )


def test_an_unpaid_fund_owes_the_element() -> None:
    """Not paid: the elemento distinto of 16 EUR is an earning, also on the 13th."""
    regular = _run(frozenset())
    thirteenth = _run(frozenset(), run=PayrollRun.thirteenth(2026, 12))

    for result in (regular, thirteenth):
        items = [
            i for i in result.pay_items if i.item_id.startswith("fondo_test_element")
        ]
        assert [i.amount for i in items] == [Decimal("16.00")]
    assert _posted(regular, AccountKind.BILATERAL_FUND_EMPLOYER) == 0


def test_the_shares_are_due_on_the_monthly_pay_only() -> None:
    """A fund without extra months posts nothing on the tredicesima."""
    result = _run(frozenset({"fondo_test"}), run=PayrollRun.thirteenth(2026, 12))

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == 0


def test_a_fund_covers_only_its_workers() -> None:
    """A fixed term is outside a permanent-only fund, an impiegato the quadri."""
    result = _run(None, contract=FixedTerm(renewals=0))

    assert not any(d.capability == "contractual_funds" for d in result.decisions)


def test_part_time_scales_the_fixed_amounts() -> None:
    """At 20 of 40 hours the element is half: 8 EUR."""
    result = _run(frozenset(), weekly_hours=WeeklyHours(Decimal(20)))

    items = [i for i in result.pay_items if i.item_id.startswith("fondo_test_element")]
    assert [i.amount for i in items] == [Decimal("8.00")]


def test_the_funds_are_a_set_of_codes() -> None:
    """Anything but a set of codes is rejected."""
    with pytest.raises(InvalidInputError, match="contractual_funds"):
        EmployerProfile(headcount=Headcount(5), contractual_funds=["fondo"])  # type: ignore[arg-type]


def test_a_fund_amount_needs_a_value() -> None:
    """An amount with neither a monthly value nor a rate is rejected."""
    with pytest.raises(ValueError, match="monthly or annual amount or a rate"):
        FundAmount()


class _ChimicaFundRepository(BundledKnowledgeRepository):
    """The bundle, with the health fund on Chimica (no open limitation)."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        ccnl = super().load_ccnl(ccnl_id)
        parameters = ccnl.parameters.model_copy(update={"health_funds": (_HEALTH,)})
        return ccnl.model_copy(update={"parameters": parameters})


@pytest.mark.parametrize(
    ("funds", "payable"),
    [(None, False), (frozenset({"fondo_test"}), True), (frozenset(), True)],
)
def test_the_stated_funds_make_a_run_payable(
    funds: frozenset[str] | None, *, payable: bool
) -> None:
    """A fully stated chimica run is payable once the funds are stated."""
    engine = PayrollEngine(repository=_ChimicaFundRepository(), mode="operational")
    result = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 27),
            employment=Employment(
                ccnl_id="chimica-farmaceutica-federchimica",
                level_code="D1",
                contract_type=Permanent(),
                category=WorkerCategory.IMPIEGATO,
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                roles=frozenset(),
                sector=EmploymentSector.PRIVATE,
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=True,
            ),
            employer=EmployerProfile(
                headcount=Headcount(60),
                provincial_pay_element=False,
                contractual_funds=funds,
            ),
            facts=PeriodFacts(
                regione="IT-25",
                comune_belfiore="A005",
                family_composition=FamilyComposition(),
            ),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(40000)),
            current_year=CurrentYearTaxFacts(
                tax_year=2026,
                other_employment_income=Decimal(0),
                other_employment_inps_base=Decimal(0),
                other_income=Decimal(0),
                main_dwelling_income=Decimal(0),
                exempt_regime_income=Decimal(0),
                estimated_on=_HIRED,
                quality=IncomeEstimateQuality.DECLARED,
            ),
            opening_state=PeriodState.zero(),
        )
    )
    assert result.is_payable is payable, [b.detail for b in result.blockers]


_LEVELS = ContractualFund(
    code="ente_livelli",
    description="Ente dei livelli alti",
    levels=frozenset({"1"}),
    employer=FundAmount(monthly=_flat("5")),
    provenance=_SOURCE,
)
_EMPLOYER_ONLY = ContractualFund(
    code="ente_minimo",
    description="Ente bilaterale sul minimo",
    employer=FundAmount(rate=_flat("0.001")),
    provenance=_SOURCE,
)


class _MoreFundsRepository(BundledKnowledgeRepository):
    """Turismo with a fund of other levels and one without worker share."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        ccnl = super().load_ccnl(ccnl_id)
        parameters = ccnl.parameters.model_copy(
            update={"health_funds": (_LEVELS, _EMPLOYER_ONLY)}
        )
        return ccnl.model_copy(update={"parameters": parameters})


def _more(funds: frozenset[str]) -> PeriodResult:
    return PayrollEngine(repository=_MoreFundsRepository()).calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="turismo-federalberghi",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(60), contractual_funds=funds),
        )
    )


def test_a_rate_fund_without_worker_share() -> None:
    """0.10% of the 1,695.69 minimo from the employer, nothing withheld."""
    result = _more(frozenset({"ente_minimo"}))

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("1.70")
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == 0
    assert [
        d.inputs["fund"]
        for d in result.decisions
        if d.capability == "contractual_funds"
    ] == ["ente_minimo"]


def test_a_fund_without_element_is_paid_whatever_the_employer_states() -> None:
    """The CCNL owes it with no alternative: posted even when not named."""
    result = _more(frozenset())

    (decision,) = [d for d in result.decisions if d.capability == "contractual_funds"]
    assert (decision.reason_code, decision.amount) == ("fund_paid", Decimal("1.70"))
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("1.70")


def test_part_time_owes_the_fixed_shares_in_full() -> None:
    """The shares are per capita: 10 and 2 EUR also at 20 of 40 hours."""
    result = _run(frozenset({"fondo_test"}), weekly_hours=WeeklyHours(Decimal(20)))

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("10.00")
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == Decimal("2.00")


class _FullElementRepository(BundledKnowledgeRepository):
    """Turismo with an element the CCNL owes in full to a part-timer."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        ccnl = super().load_ccnl(ccnl_id)
        full = _HEALTH.model_copy(update={"alternative_scaled": False})
        parameters = ccnl.parameters.model_copy(update={"health_funds": (full,)})
        return ccnl.model_copy(update={"parameters": parameters})


def test_an_element_owed_in_full_ignores_part_time() -> None:
    """Not reproportioned: 16 EUR at 20 of 40 hours."""
    result = PayrollEngine(repository=_FullElementRepository()).calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="turismo-federalberghi",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                weekly_hours=WeeklyHours(Decimal(20)),
                full_time_weekly_hours=WeeklyHours(Decimal(40)),
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), contractual_funds=frozenset()
            ),
        )
    )

    items = [i for i in result.pay_items if i.item_id.startswith("fondo_test_element")]
    assert [i.amount for i in items] == [Decimal("16.00")]


class _GroupRepository(BundledKnowledgeRepository):
    """Turismo with two alternative funds and no element."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        ccnl = super().load_ccnl(ccnl_id)
        first = _EMPLOYER_ONLY.model_copy(update={"group": "ente"})
        second = _LEVELS.model_copy(update={"group": "ente", "levels": None})
        parameters = ccnl.parameters.model_copy(
            update={"health_funds": (first, second)}
        )
        return ccnl.model_copy(update={"parameters": parameters})


def test_a_group_without_element_owes_nothing_when_none_is_named() -> None:
    """Neither way of the group is named and it has no element: nothing."""
    result = PayrollEngine(repository=_GroupRepository()).calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="turismo-federalberghi",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), contractual_funds=frozenset()
            ),
        )
    )

    (decision,) = [d for d in result.decisions if d.capability == "contractual_funds"]
    assert (decision.inputs["fund"], decision.reason_code, decision.amount) == (
        "ente_minimo",
        "alternative_element_paid",
        Decimal(0),
    )
