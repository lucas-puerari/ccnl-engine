"""Written deferral request and deferred IRPEF of a conguaglio.

Art. 23 c. 3 DPR 600/1973: the request is made for the conguaglio, due by
28 February of the next year; the deferred IRPEF is withheld on the pay
periods after the second of the next year, with interest at 0.50 per cent
a month.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.shortfall_deferral import (
    DeferredInstallment,
    DeferredShortfall,
    ShortfallDeferralRequest,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

_DECEMBER = date(2025, 12, 1)


def _deferred(irpef: str = "300.00", tax_year: int = 2025) -> DeferredShortfall:
    return DeferredShortfall(
        tax_year=tax_year,
        signed_on=date(tax_year, 12, 10),
        deferred_from=date(tax_year, 12, 1),
        irpef=Decimal(irpef),
    )


class TestRequest:
    """The written request and its window."""

    def test_rejects_a_value_that_is_not_a_date(self) -> None:
        """The signature date is a date."""
        with pytest.raises(InvalidInputError, match="signed_on"):
            ShortfallDeferralRequest(signed_on="2026-12-10")  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "signed_on", [date(2026, 1, 1), date(2026, 12, 31), date(2027, 2, 28)]
    )
    def test_accepts_the_tax_year_and_the_conguaglio_deadline(
        self, signed_on: date
    ) -> None:
        """From 1 January of N to 28 February of N+1 (2027 not a leap year)."""
        ShortfallDeferralRequest(signed_on).check_for(2026)

    def test_accepts_29_february_of_a_leap_year(self) -> None:
        """2028 is a leap year: the deadline is 29 February."""
        ShortfallDeferralRequest(date(2028, 2, 29)).check_for(2027)

    @pytest.mark.parametrize("signed_on", [date(2025, 12, 31), date(2027, 3, 1)])
    def test_rejects_a_date_outside_the_window(self, signed_on: date) -> None:
        """Before N or after the deadline of the conguaglio."""
        with pytest.raises(InvalidInputError, match=r"art\. 23 c\. 3 DPR 600/1973"):
            ShortfallDeferralRequest(signed_on).check_for(2026)

    def test_rejection_from_2027_cites_the_testo_unico(self) -> None:
        """From 2027 the rule is art. 33 c. 4 D.Lgs. 33/2025 (art. 243 c. 1)."""
        with pytest.raises(InvalidInputError, match=r"art\. 33 c\. 4 D\.Lgs\. 33/2025"):
            ShortfallDeferralRequest(date(2028, 3, 1)).check_for(2027)

    def test_prior_year_facts_reject_another_type(self) -> None:
        """The facts hold a request or nothing."""
        with pytest.raises(InvalidInputError, match="ShortfallDeferralRequest"):
            PriorYearTaxFacts(shortfall_deferral=date(2026, 12, 1))  # type: ignore[arg-type]


class TestDeferredShortfall:
    """Validation, months of interest and one payslip's withholding."""

    def test_rejects_a_tax_year_before_2020(self) -> None:
        """The engine models no tax year before 2020."""
        with pytest.raises(InvalidInputError, match="tax_year"):
            _deferred(tax_year=2019)

    @pytest.mark.parametrize(
        "start", [date(2024, 12, 1), date(2026, 3, 1), date(2027, 1, 1)]
    )
    def test_rejects_a_start_outside_the_conguaglio(self, start: date) -> None:
        """The conguaglio of 2025 is in 2025 or January-February 2026."""
        with pytest.raises(InvalidInputError, match="deferred_from"):
            DeferredShortfall(2025, date(2025, 12, 10), start, Decimal(1))

    def test_accepts_a_conguaglio_of_february(self) -> None:
        """A conguaglio made on the February pay of N+1 is in time."""
        deferred = DeferredShortfall(
            2025, date(2026, 2, 10), date(2026, 2, 1), Decimal(1)
        )
        assert deferred.months_to(2026, 3) == 1

    @pytest.mark.parametrize("irpef", ["0", "-1", "Infinity"])
    def test_rejects_an_amount_that_is_not_positive(self, irpef: str) -> None:
        """Only a positive finite amount is deferred."""
        with pytest.raises(InvalidInputError, match="irpef"):
            _deferred(irpef)

    def test_months_and_window(self) -> None:
        """December 2025 to March 2026 is 3 months; the window is 2026."""
        deferred = _deferred()
        assert deferred.withheld_in == 2026
        assert deferred.months_to(2026, 3) == 3
        assert deferred.months_to(2025, 11) == 0
        assert not deferred.due_in(2026, 2)
        assert deferred.due_in(2026, 3)
        assert not deferred.due_in(2027, 3)

    def test_post_withholds_the_whole_residual(self) -> None:
        """300.00 in March: interest 300.00 x 0.005 x 3 = 4.50."""
        posted, after = _deferred().post(Decimal(1000), 2026, 3)
        assert posted == DeferredInstallment(Decimal("300.00"), Decimal("4.50"), 3)
        assert posted.total == Decimal("304.50")
        assert after is None

    def test_post_fits_principal_and_interest_in_the_pay(self) -> None:
        """101.50 EUR of pay in March: 100.00 principal, 1.50 interest."""
        posted, after = _deferred().post(Decimal("101.50"), 2026, 3)
        assert posted == DeferredInstallment(Decimal("100.00"), Decimal("1.50"), 3)
        assert after == _deferred("200.00")

    @pytest.mark.parametrize(
        ("pay", "principal", "interest"),
        [
            # 3.04 / 1.015 = 2.995 truncated to 2.99; 2.99 x 0.015 = 0.04485
            ("3.04", "2.99", "0.04"),
            # 0.34 / 1.015 = 0.334 truncated to 0.33; 0.00495 rounds to 0.00
            ("0.34", "0.33", "0.00"),
            # 1.02 / 1.015 = 1.0049 truncated to 1.00; 0.015 rounds to 0.02
            ("1.02", "1.00", "0.02"),
        ],
    )
    def test_post_truncates_the_principal_to_the_pay(
        self, pay: str, principal: str, interest: str
    ) -> None:
        """The principal is truncated to the cent; the interest still fits."""
        posted, _ = _deferred().post(Decimal(pay), 2026, 3)
        assert posted == DeferredInstallment(Decimal(principal), Decimal(interest), 3)
        assert posted.total <= Decimal(pay)

    def test_post_with_no_pay_withholds_nothing(self) -> None:
        """No pay left: nothing withheld, the deferral kept."""
        deferred = _deferred()
        assert deferred.post(Decimal(0), 2026, 3) == (None, deferred)
        assert deferred.post(Decimal(-5), 2026, 3) == (None, deferred)


class TestObligations:
    """The deferred shortfalls among the employment obligations."""

    def test_two_deferrals_of_one_year_are_rejected(self) -> None:
        """One conguaglio defers once."""
        with pytest.raises(ValueError, match="deferred_shortfall"):
            EmploymentObligations(deferred_shortfall=(_deferred(), _deferred("1")))

    def test_lookup_and_latest_year(self) -> None:
        """The deferral is found by year and dates the obligations."""
        deferred = _deferred()
        obligations = EmploymentObligations(deferred_shortfall=(deferred,))
        assert obligations.deferred_of(2025) == deferred
        assert obligations.deferred_of(2024) is None
        assert obligations.latest_tax_year == 2025
