"""Allowance activation by role and service months."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest

from ccnl_engine.agreement.validity.rules import (
    SalaryGapKind,
    SeriesGapError,
    TimeSeries,
    ValidityPeriod,
)
from ccnl_engine.compensation.element import rules
from ccnl_engine.compensation.element.rules import (
    _allowance_active,
    _level_chain,
    service_gated_allowances,
)
from ccnl_engine.compensation.models import Allowance
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind
from ccnl_engine.seniority.rules import APPRENTICE_SENIORITY_VARIANT
from tests.unit.ccnl_engine.builders import _series

_DAY = date(2026, 6, 1)


def _time_series(value: str) -> TimeSeries:
    """Build a single-period TimeSeries for the given value.

    Returns:
        A :class:`TimeSeries` valid from 2020-01-01 with no end date.
    """
    return TimeSeries.model_validate(_series(value))


def _allowance(
    *,
    code: str = "EDR",
    monthly: str = "10.00",
    role: str | None = None,
    apprenticeship_pct_relevant: bool = True,
    service_months_threshold: int | None = None,
) -> Allowance:
    """Build a minimal :class:`Allowance` for testing.

    Returns:
        A frozen :class:`Allowance` with the given parameters.
    """
    return Allowance(
        code=code,
        description=code,
        monthly=_time_series(monthly),
        role=role,
        apprenticeship_pct_relevant=apprenticeship_pct_relevant,
        service_months_threshold=service_months_threshold,
        provenance=None,
    )


class TestAllowanceActive:
    """_allowance_active branching logic."""

    def test_role_not_in_roles_returns_false(self) -> None:
        """Returns False when the allowance has a role not present in roles."""
        a = _allowance(role="manager")
        assert _allowance_active(a, frozenset({"driver"}), None, _DAY) is False

    def test_no_role_no_threshold_returns_true(self) -> None:
        """Returns True when role is None and threshold is None."""
        a = _allowance(role=None, service_months_threshold=None)
        assert _allowance_active(a, frozenset(), None, _DAY) is True

    def test_threshold_met(self) -> None:
        """Returns True when seniority_months >= service_months_threshold."""
        a = _allowance(service_months_threshold=12)
        assert _allowance_active(a, frozenset(), 24, _DAY) is True

    def test_threshold_not_met(self) -> None:
        """Returns False when seniority_months < service_months_threshold."""
        a = _allowance(service_months_threshold=24)
        assert _allowance_active(a, frozenset(), 12, _DAY) is False

    def test_not_in_force_returns_false(self) -> None:
        """Returns False in a ``not_applicable`` gap, before the rule exists."""
        monthly = TimeSeries(
            periods=(
                ValidityPeriod(
                    valid_from=date(2024, 1, 1),
                    valid_until=date(2025, 7, 1),
                    gap_kind=SalaryGapKind.NOT_APPLICABLE,
                ),
                ValidityPeriod(
                    valid_from=date(2025, 7, 1), valid_until=None, value=Decimal(30)
                ),
            )
        )
        a = _allowance().model_copy(update={"monthly": monthly})
        assert _allowance_active(a, frozenset(), None, date(2025, 6, 1)) is False
        assert _allowance_active(a, frozenset(), None, date(2025, 7, 1)) is True


def _gated(
    threshold: int | None, until: int | None, role: str | None = None
) -> Allowance:
    return Allowance(
        code="GATED",
        description="gated",
        monthly=_time_series("25.00"),
        role=role,
        service_months_threshold=threshold,
        service_months_until=until,
        provenance=None,
    )


@pytest.mark.parametrize(
    ("threshold", "until", "months", "active"),
    [
        (24, None, 24, True),
        (24, None, 23, False),
        (None, 36, 35, True),
        (None, 36, 36, False),
        (12, 36, 12, True),
        (12, 36, 36, False),
    ],
)
def test_service_months_open_at_the_threshold_and_close_at_the_until(
    threshold: int | None, until: int | None, months: int, *, active: bool
) -> None:
    """From the threshold included, up to the until excluded."""
    allowance = _gated(threshold, until)

    assert _allowance_active(allowance, frozenset(), months, _DAY) is active


def test_only_service_gated_allowances_of_a_held_role_are_listed() -> None:
    """A gate on either bound counts; a role the worker lacks is left out."""
    level = SimpleNamespace(
        fixed_allowances=(
            _gated(24, None),
            _gated(None, 36),
            _gated(None, None),
            _gated(12, None, role="driver"),
            _gated(12, None, role="manager"),
        )
    )

    gated = service_gated_allowances(level, frozenset({"driver"}))  # type: ignore[arg-type]

    assert [
        (a.service_months_threshold, a.service_months_until, a.role) for a in gated
    ] == [
        (24, None, None),
        (None, 36, None),
        (12, None, "driver"),
    ]


def _ccnl(apprentice_amount: object = None) -> Any:  # noqa: ANN401
    increments = SimpleNamespace(
        apprentice_amount=apprentice_amount,
        excluded_from_extra_months=(ExtraMonthKind.FOURTEENTH,),
    )
    return SimpleNamespace(
        parameters=SimpleNamespace(seniority_increments=increments),
        meta=SimpleNamespace(ccnl_id="x"),
    )


def _level(base: TimeSeries | None = None) -> Any:  # noqa: ANN401
    return SimpleNamespace(
        code="C3",
        base_salary=base or _time_series("2000.00"),
        fixed_allowances=(_gated(24, None),),
    )


class _Seniority:
    """Records each call and pays 10.00 to an apprentice, 30.00 otherwise."""

    def __init__(self) -> None:
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def __call__(self, *args: object, **kwargs: object) -> Decimal:
        self.calls.append((args, kwargs))
        return Decimal(10) if kwargs["is_apprentice"] else Decimal(30)


def test_the_chain_passes_the_worker_to_the_seniority_rule(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Rules, level, count, day, category, apprenticeship and months, as given."""
    seniority = _Seniority()
    monkeypatch.setattr(rules, "_seniority_amount", seniority)
    ccnl = _ccnl()

    chain = _level_chain(
        ccnl,
        _level(),
        2,
        frozenset(),
        _DAY,
        worker_category=WorkerCategory.IMPIEGATO,
        is_apprentice=False,
        seniority_months=30,
    )

    args, kwargs = seniority.calls[0]
    assert args == (ccnl.parameters.seniority_increments, "C3", 2, _DAY)
    assert kwargs == {
        "worker_category": WorkerCategory.IMPIEGATO,
        "is_apprentice": False,
        "seniority_months": 30,
    }
    assert chain.seniority == Decimal(30)
    assert chain.base == Decimal("2000.00")
    assert [a.code for a, _ in chain.allowances] == ["GATED"]
    assert chain.seniority_excluded_from == frozenset({14})
    assert chain.limitations == ()


@pytest.mark.parametrize(
    ("count", "apprentice_amount", "limited"),
    [(2, None, True), (0, None, False), (1, None, True), (2, "set", False)],
)
def test_an_apprentice_without_a_ccnl_amount_records_the_limitation(
    monkeypatch: pytest.MonkeyPatch,
    count: int,
    apprentice_amount: object,
    *,
    limited: bool,
) -> None:
    """Matured increments, no apprentice amount, a level amount that differs."""
    monkeypatch.setattr(rules, "_seniority_amount", _Seniority())

    chain = _level_chain(
        _ccnl(apprentice_amount),
        _level(),
        count,
        frozenset(),
        _DAY,
        is_apprentice=True,
        seniority_months=30,
    )

    assert chain.limitations == (
        (f"x/{APPRENTICE_SENIORITY_VARIANT}",) if limited else ()
    )


def test_a_qualified_worker_records_no_apprentice_limitation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The limitation concerns apprentices only."""
    monkeypatch.setattr(rules, "_seniority_amount", _Seniority())

    chain = _level_chain(
        _ccnl(),
        _level(),
        2,
        frozenset(),
        _DAY,
        is_apprentice=False,
        seniority_months=30,
    )

    assert chain.limitations == ()


def test_a_gap_in_the_seniority_names_the_seniority_feature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A series without a value on the day is a missing seniority rule."""

    def gap(*args: object, **kwargs: object) -> Decimal:
        raise SeriesGapError(_DAY, None, None)

    monkeypatch.setattr(rules, "_seniority_amount", gap)

    with pytest.raises(MissingRuleError) as missing:
        _level_chain(_ccnl(), _level(), 2, frozenset(), _DAY, is_apprentice=False)

    assert missing.value.feature == "seniority"


def test_a_gap_in_the_base_salary_names_the_base_salary_feature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A base salary not yet in force on the day is a missing base rule."""
    monkeypatch.setattr(rules, "_seniority_amount", _Seniority())
    later = TimeSeries(
        periods=(
            ValidityPeriod(
                value=Decimal(2000), valid_from=date(2027, 1, 1), valid_until=None
            ),
        )
    )

    with pytest.raises(MissingRuleError) as missing:
        _level_chain(_ccnl(), _level(later), 2, frozenset(), _DAY, is_apprentice=False)

    assert missing.value.feature == "base_salary"


def test_a_service_gated_allowance_without_the_months_is_inactive() -> None:
    """Unknown service months never open a gate."""
    assert _allowance_active(_gated(24, None), frozenset(), None, _DAY) is False


def test_the_level_amount_is_read_for_the_same_worker_as_qualified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The comparison reads the level rule with the facts of the apprentice."""
    seniority = _Seniority()
    monkeypatch.setattr(rules, "_seniority_amount", seniority)
    ccnl = _ccnl()

    _level_chain(
        ccnl,
        _level(),
        2,
        frozenset(),
        _DAY,
        worker_category=WorkerCategory.OPERAIO,
        is_apprentice=True,
        seniority_months=30,
    )

    assert seniority.calls[1] == (
        (ccnl.parameters.seniority_increments, "C3", 2, _DAY),
        {
            "worker_category": WorkerCategory.OPERAIO,
            "is_apprentice": False,
            "seniority_months": 30,
        },
    )


def test_a_level_amount_without_a_value_keeps_the_limitation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the level rule has no value the amounts cannot be shown equal."""

    def amount(*args: object, **kwargs: object) -> Decimal:
        if kwargs["is_apprentice"]:
            return Decimal(10)
        raise SeriesGapError(_DAY, None, None)

    monkeypatch.setattr(rules, "_seniority_amount", amount)

    chain = _level_chain(_ccnl(), _level(), 2, frozenset(), _DAY, is_apprentice=True)

    assert chain.limitations == (f"x/{APPRENTICE_SENIORITY_VARIANT}",)
