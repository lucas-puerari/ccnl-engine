"""Unit tests for the apprenticeship scaling of MonthlyPayChain."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.contract.compensation.models import Allowance
from ccnl_engine.contract.identity.rules_validity import TimeSeries
from ccnl_engine.payroll.amount.types_chain import (
    ApprenticeshipScaling,
    MonthlyPayChain,
)

_D = Decimal


def _allowance(code: str, *, relevant: bool) -> Allowance:
    return Allowance(
        code=code,
        description=code,
        monthly=TimeSeries.model_validate({
            "periods": [
                {"valid_from": "2020-01-01", "valid_until": None, "value": "1.00"}
            ]
        }),
        apprenticeship_pct_relevant=relevant,
    )


_CONTINGENZA = _allowance("CONTINGENZA", relevant=True)
_EDR = _allowance("EDR", relevant=False)


def _chain(seniority: str = "0.00") -> MonthlyPayChain:
    return MonthlyPayChain(
        base=_D("1307.47"),
        seniority=_D(seniority),
        allowances=((_CONTINGENZA, _D("522.19")), (_EDR, _D("41.85"))),
    )


class TestScaledForApprenticeship:
    """Only the base and the relevant allowances are reduced."""

    def test_exempt_allowance_keeps_full_value(self) -> None:
        """75% of 1307.47 and 522.19, rounded half up; EDR stays 41.85.

        The seniority is the apprentice amount, already set for
        apprentices: it stays 20.00 instead of being reduced a second time.
        """
        result = _chain("20.00").scaled_for_apprenticeship(_D("0.75"))

        assert result.base == _D("980.60")
        assert result.seniority == _D("20.00")
        assert result.allowances == (
            (_CONTINGENZA, _D("391.64")),
            (_EDR, _D("41.85")),
        )

    def test_extra_month_scaling_still_reduces_every_component(self) -> None:
        """``scaled`` is the extra-month rateo and ignores the flag."""
        result = _chain().scaled(_D("0.5"))

        assert result.allowances[1] == (_EDR, _D("20.93"))


class TestApprenticeshipScalingOf:
    """The scaling lists the components it reduced and those paid in full."""

    def test_lists_scaled_and_unscaled_components(self) -> None:
        """Seniority, listed when the chain carries some, is paid in full."""
        scaling = ApprenticeshipScaling.of(_chain("20.00"), _D("0.75"))

        assert scaling == ApprenticeshipScaling(
            percentage=_D("0.75"),
            scaled=("base_salary", "CONTINGENZA"),
            unscaled=("seniority", "EDR"),
        )

    def test_omits_seniority_when_none_is_due(self) -> None:
        """A chain without seniority scales the base and relevant allowances."""
        scaling = ApprenticeshipScaling.of(_chain(), _D("0.80"))

        assert scaling.scaled == ("base_salary", "CONTINGENZA")
