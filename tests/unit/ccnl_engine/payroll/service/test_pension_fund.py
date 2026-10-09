"""Resolution of the fund terms and the contributions of one run.

Rates from the tabacco bundle: ALIFOND employer 1.50% from 2025-07-01,
employee not less than 1% (art. 47 of the accord of 02/07/2025).  The cap
and solidarity rate are the 2026 values of D.Lgs. 252/2005 art. 8 c. 4 and
art. 16 c. 1: 5 300.00 and 10%.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.payroll.domain.pension_fund import PensionFundEnrolment
from ccnl_engine.payroll.service.pension_fund import (
    PensionFundTerms,
    contractual_only,
    contribute,
    resolve_terms,
    upcoming_adjustment,
)
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.tax.domain.pension_rules import ComplementaryPensionRules

_RULES = ComplementaryPensionRules(
    deduction_cap=Decimal("5300.00"), solidarity_rate=Decimal("0.10")
)
_DAY = date(2026, 3, 1)
_ENROLMENT = PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=True)
_TABACCO = load_ccnl("tabacco-apti.json")


def _terms() -> PensionFundTerms:
    return resolve_terms(_TABACCO, _ENROLMENT, None, _DAY, _RULES, apprentice=False)


class TestResolveTerms:
    """Fund lookup, category, rate in force and statutory rules."""

    def test_rates_in_force(self) -> None:
        """ALIFOND 1.50% employer and 1% employee minimum in 2026."""
        terms = _terms()
        assert terms.employer_rate == Decimal("0.0150")
        assert terms.employee_min_rate == Decimal("0.0100")
        assert terms.tfr_to_fund is True

    def test_no_rate_before_the_series(self) -> None:
        """ALIFOND starts on 2025-07-01: no rate in January 2025."""
        with pytest.raises(InvalidInputError, match="no employer rate"):
            resolve_terms(
                _TABACCO, _ENROLMENT, None, date(2025, 1, 1), _RULES, apprentice=False
            )

    def test_missing_statutory_rules(self) -> None:
        """A tax year without complementary pension rules is rejected."""
        with pytest.raises(InvalidInputError, match="no complementary pension"):
            resolve_terms(_TABACCO, _ENROLMENT, None, _DAY, None, apprentice=False)

    @pytest.mark.parametrize(
        ("apprentice", "expected"),
        [(True, Decimal("0.0105")), (False, Decimal("0.0150"))],
    )
    def test_apprentice_rate(self, *, apprentice: bool, expected: Decimal) -> None:
        """A fund with an apprentice rate charges it to apprentices only."""
        fund = _TABACCO.parameters.employer_funds[0]
        apart = fund.rate.model_copy(
            update={
                "periods": tuple(
                    p.model_copy(update={"value": Decimal("0.0105")})
                    for p in fund.rate.periods
                )
            }
        )
        params = _TABACCO.parameters.model_copy(
            update={
                "employer_funds": (fund.model_copy(update={"apprentice_rate": apart}),)
            }
        )
        ccnl = _TABACCO.model_copy(update={"parameters": params})
        terms = resolve_terms(
            ccnl, _ENROLMENT, None, _DAY, _RULES, apprentice=apprentice
        )
        assert terms.employer_rate == expected

    def test_ccnl_without_funds(self) -> None:
        """A CCNL with no fund rejects every enrolment."""
        bancari = load_ccnl("bancari-abi.json")
        with pytest.raises(InvalidInputError, match="its funds are \\[\\]"):
            resolve_terms(bancari, _ENROLMENT, None, _DAY, _RULES, apprentice=False)

    @pytest.mark.parametrize(
        ("category", "accepted"),
        [
            (WorkerCategory.QUADRO, True),
            (WorkerCategory.OPERAIO, False),
            (None, False),
        ],
    )
    def test_category_restriction(
        self, category: WorkerCategory | None, *, accepted: bool
    ) -> None:
        """A fund restricted to quadri takes only a declared quadro."""
        fund = _TABACCO.parameters.employer_funds[0].model_copy(
            update={"applies_to_categories": (WorkerCategory.QUADRO,)}
        )
        params = _TABACCO.parameters.model_copy(update={"employer_funds": (fund,)})
        ccnl = _TABACCO.model_copy(update={"parameters": params})
        if accepted:
            assert resolve_terms(
                ccnl, _ENROLMENT, category, _DAY, _RULES, apprentice=False
            )
        else:
            with pytest.raises(InvalidInputError, match="covers the categories"):
                resolve_terms(
                    ccnl, _ENROLMENT, category, _DAY, _RULES, apprentice=False
                )


class TestContribute:
    """Contributions and deduction of a run of base 2000.00."""

    def test_within_the_cap(self) -> None:
        """Employer 30.00, employee 20.00, solidarity 3.00, 50.00 deducted."""
        pension = contribute(_terms(), Decimal("2000.00"), Decimal(0))
        assert (pension.employer, pension.employee) == (
            Decimal("30.00"),
            Decimal("20.00"),
        )
        assert pension.solidarity == Decimal("3.00")
        assert pension.deductible == Decimal("50.00")
        assert pension.taxable_adjustment == Decimal("-20.00")

    def test_beyond_the_cap(self) -> None:
        """5 280.00 deducted: 20.00 left, the other 30.00 is taxable."""
        pension = contribute(_terms(), Decimal("2000.00"), Decimal("5280.00"))
        assert pension.deductible == Decimal("20.00")
        assert pension.taxable_adjustment == Decimal("10.00")

    def test_cap_already_exceeded(self) -> None:
        """A deducted total above the cap leaves nothing to deduct."""
        pension = contribute(_terms(), Decimal("2000.00"), Decimal("6000.00"))
        assert pension.deductible == 0

    def test_upcoming_slots(self) -> None:
        """Projected 10 000.00 of base: 150.00 employer, 100.00 employee.

        With 5 200.00 deducted, 100.00 of cap is left: the taxable rises by
        150.00 - 100.00 = 50.00.
        """
        change = upcoming_adjustment(_terms(), Decimal("10000.00"), Decimal("5200.00"))
        assert change == Decimal("50.00")


class TestContractual:
    """The contractual contribution joins the employer part."""

    def test_added_to_the_employer_part(self) -> None:
        """30.00 on 2000.00 at 1.50% plus 6.80: 36.80, solidarity 3.68."""
        pension = contribute(_terms(), Decimal("2000.00"), Decimal(0), Decimal("6.80"))
        assert (pension.employer, pension.contractual) == (
            Decimal("36.80"),
            Decimal("6.80"),
        )
        assert pension.solidarity == Decimal("3.68")

    def test_alone_without_enrolment(self) -> None:
        """6.80 alone: no rates, deducted in full within the cap."""
        pension = contractual_only(Decimal("6.80"), _RULES, Decimal(0))
        assert pension.terms is None
        assert (pension.employer, pension.employee) == (Decimal("6.80"), Decimal(0))
        assert (pension.solidarity, pension.deductible) == (
            Decimal("0.68"),
            Decimal("6.80"),
        )
        assert pension.taxable_adjustment == 0

    def test_alone_needs_the_rules_of_the_year(self) -> None:
        """A tax year without complementary pension rules is rejected."""
        with pytest.raises(InvalidInputError, match="no complementary pension"):
            contractual_only(Decimal("6.80"), None, Decimal(0))
