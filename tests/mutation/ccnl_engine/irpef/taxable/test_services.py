"""Taxable income of one run: the PdR split, the run, the projection, lett. b)."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine.irpef.taxable import services
from ccnl_engine.irpef.taxable.services import _PdrSplit, pdr_split, taxable_income

if TYPE_CHECKING:
    from ccnl_engine.pension_fund.rules import PensionContribution

_D = Decimal
_RATE = _D("0.0919")


def _inp(**changes: object) -> Any:  # noqa: ANN401
    """Return the facts of a run that the taxable reads, ``changes`` applied.

    Returns:
        A stand-in for the amounts input of the run.
    """
    facts: dict[str, object] = {
        "pdr_rules": SimpleNamespace(max_amount=_D(3000), flat_tax_rate=_D("0.05")),
        "opening": SimpleNamespace(
            fringe=SimpleNamespace(pdr=_D(0)),
            earnings=SimpleNamespace(taxable=_D(10000)),
        ),
        "event_substitute_base": _D(0),
        "event_irpef_base": _D(0),
        "event_separate_base": _D(0),
        "event_apart_inps_base": _D(0),
        "monthly_gross": _D(2000),
        "upcoming_gross": _D(12000),
        "additional_month": False,
    }
    facts.update(changes)
    return SimpleNamespace(**facts)


_NO_PDR = _PdrSplit(eligible=_D(0), excess=_D(0), substitute_tax=_D(0))


def test_the_pdr_beyond_the_cap_left_is_its_excess() -> None:
    """1,000 of a 3,000 cap already used: 2,500 of PdR leaves 500 beyond it."""
    opening = SimpleNamespace(
        fringe=SimpleNamespace(pdr=_D(1000)), earnings=SimpleNamespace(taxable=_D(0))
    )

    split = pdr_split(_inp(event_substitute_base=_D(2500), opening=opening))

    assert split == _PdrSplit(eligible=_D(2000), excess=_D(500), substitute_tax=_D(100))


def test_the_excess_pdr_joins_the_irpef_base_and_the_run() -> None:
    """The run: gross less INPS plus the IRPEF base, the PdR excess included."""
    pdr = _PdrSplit(eligible=_D(0), excess=_D(300), substitute_tax=_D(0))

    taxable = taxable_income(_inp(event_irpef_base=_D(100)), _D(183.80), _RATE, pdr)

    assert taxable.irpef_base == _D(400)
    assert taxable.period == _D("2216.20")
    assert taxable.projected == _D(10000) + _D("2216.20") + _D(12000) - _D("1102.80")


def test_a_pension_fund_changes_the_run_and_the_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The adjustment of the run, and that of the slots still to come, add up."""
    seen: list[object] = []

    def projected(inp: object, pension: object) -> Decimal:
        seen.append(pension)
        return _D(-50) if pension is not None else _D(0)

    monkeypatch.setattr(services, "projected_adjustment", projected)
    pension: PensionContribution = SimpleNamespace(taxable_adjustment=_D(-20))  # type: ignore[assignment]

    taxable = taxable_income(_inp(), _D(183.80), _RATE, _NO_PDR, pension)

    assert seen == [pension]
    assert taxable.period == _D("1796.20")
    assert taxable.projected == _D(10000) + _D("1796.20") + _D(12000) - _D(
        "1102.80"
    ) - _D(50)


@pytest.mark.parametrize(
    ("separate_base", "excess", "expected"),
    [
        (_D(1000), _D(0), _D("908.10")),
        (_D(600), _D(400), _D("908.10")),
        (_D(5000), _D(0), _D("1816.20")),
    ],
)
def test_lett_b_withholds_the_premiums_net_of_the_inps_of_the_run(
    separate_base: Decimal, excess: Decimal, expected: Decimal
) -> None:
    """Premiums and the PdR excess, less INPS at the run rate, capped by the run."""
    pdr = _PdrSplit(eligible=_D(0), excess=excess, substitute_tax=_D(0))

    taxable = taxable_income(
        _inp(event_separate_base=separate_base), _D(183.80), _RATE, pdr
    )

    assert taxable.separate == min(expected, taxable.period)


def test_the_inps_of_the_pay_taxed_apart_is_no_ordinary_deduction() -> None:
    """Art. 19 c. 2 TUIR: 1000 taxed apart at 9.49% gives 94.90 back."""
    plain = taxable_income(_inp(), _D("189.80"), _D("0.0949"), pdr_split(_inp()))
    inp = _inp(event_apart_inps_base=_D(1000))
    apart = taxable_income(inp, _D("284.70"), _D("0.0949"), pdr_split(inp))

    assert (apart.period, apart.apart_inps) == (plain.period, _D("94.90"))
