"""The employee rate run_contributions projects for the IRPEF.

The ordinary rate of the sector, read for the contract and category of the
run, plus the public end-of-service, credit, life insurance and ENAM rates
and the solidarity fund share: each adds to the rate.  The domestic flat
contributions are read for the contract of the run.
"""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

from ccnl_engine.contribution import services
from ccnl_engine.contribution.results import ContributionBreakdown

if TYPE_CHECKING:
    import pytest

    from ccnl_engine.amount.types import _AmountsInput

_BREAKDOWN = ContributionBreakdown(Decimal(0), Decimal(0), ())
_CONTRACT = object()
_CATEGORY = object()


def _with(rate: str) -> Any:  # noqa: ANN401
    return lambda _inp, breakdown, *_: (breakdown, Decimal(rate))


def test_every_rate_adds_up(monkeypatch: pytest.MonkeyPatch) -> None:
    """0.0919 + 0.001 + 0.002 + 0.004 + 0.008 + 0.016 = 0.1229."""
    seen: list[tuple[object, object]] = []

    def rates(_rules: object, contract: object, category: object) -> Any:  # noqa: ANN401
        seen.append((contract, category))
        return SimpleNamespace(employee_rate=Decimal("0.0919"))

    monkeypatch.setattr(services, "_raised", lambda _inp, base: base)
    monkeypatch.setattr(services, "_ordinary_breakdown", lambda *_: _BREAKDOWN)
    monkeypatch.setattr(services, "with_end_of_service", lambda _inp, b: b)
    monkeypatch.setattr(services, "ivs_employer_base", lambda _b: Decimal(0))
    monkeypatch.setattr(
        services, "end_of_service_employee_rate", lambda _i: Decimal("0.001")
    )
    monkeypatch.setattr(services, "with_public_credit", _with("0.002"))
    monkeypatch.setattr(services, "with_life_insurance", _with("0.004"))
    monkeypatch.setattr(services, "with_enam", _with("0.008"))
    monkeypatch.setattr(services, "with_solidarity_fund", _with("0.016"))
    monkeypatch.setattr(services, "with_sick_pay_supplement", lambda _i, b, _base: b)
    monkeypatch.setattr(services, "resolve_rates", rates)
    inp = SimpleNamespace(
        rules=SimpleNamespace(inps=object()),
        monthly_gross=Decimal(1000),
        event_inps_base=Decimal(0),
        contract_type=_CONTRACT,
        category=_CATEGORY,
    )
    _, employee = services.run_contributions(cast("_AmountsInput", inp))
    assert employee == Decimal("0.1229")
    assert seen == [(_CONTRACT, _CATEGORY)]


def test_domestic_reads_the_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    """The flat contributions take the contract of the run; no rate."""
    seen: list[object] = []

    def domestic(*args: object) -> ContributionBreakdown:
        seen.append(args[-1])
        return _BREAKDOWN

    monkeypatch.setattr(services, "compute_domestic_breakdown", domestic)
    inp = SimpleNamespace(
        rules=SimpleNamespace(inps=None),
        weekly_hours=None,
        additional_month=False,
        contributable_hours=None,
        domestic_hourly_rate=None,
        contract_type=_CONTRACT,
    )
    assert services.run_contributions(cast("_AmountsInput", inp)) == (
        _BREAKDOWN,
        Decimal(0),
    )
    assert seen == [_CONTRACT]
