"""Hand oracle: the health and bilateral funds of Turismo and Pubblici Esercizi.

Turismo Federalberghi, level 4, minimo 1,695.69 EUR from 1 May 2026
(ipotesi 5 July 2024):

- EBNT/EBT (art. 23, p. 13): 0.20% of the paga base from the employer and
  0.20% from the worker, for 14 months; not paid, an elemento distinto of
  0.60% for 14 months.
- FAST (art. 163, p. 47): 10 EUR from the employer and 2 EUR from the
  worker a month; a health fund (10% INPS solidarity, worker share out of
  the IRPEF base); not paid, 14 EUR for 14 months (p. 48, c. 10).

Pubblici Esercizi FIPE, level 3, minimo 1,800.73 EUR from 1 June 2026:

- EBT (art. 24 CCNL 2018, p. 40): 0.20% + 0.20% of paga base and
  contingenza for 14 months; not paid, 0.60% for 14 months.
- Fondo Est (accordo 5 June 2024, p. 17): 12 EUR a month from the employer
  only; not paid, 16 EUR for 14 months (p. 18, c. 12).
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2026, 1, 1)
_CENT = Decimal("0.01")
_TURISMO = Decimal("1695.69")
_FIPE = Decimal("1800.73")


def _pct(rate: str, base: Decimal) -> Decimal:
    return (Decimal(rate) * base).quantize(_CENT, rounding=ROUND_HALF_UP)


def _run(
    ccnl_id: str, level: str, funds: frozenset[str], *, thirteenth: bool = False
) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.thirteenth(2026, 12)
            if thirteenth
            else PayrollRun.regular(2026, 6),
            payment_date=date(2026, 12, 15) if thirteenth else date(2026, 6, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(60), contractual_funds=funds),
        )
    )


def _entries(result: PeriodResult, prefix: str) -> dict[str, Decimal]:
    return {
        e.entry_id.removeprefix(prefix).split("_")[-1]: e.amount
        for e in result.ledger_entries
        if e.entry_id.startswith(prefix)
    }


def _posted(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account is account), Decimal(0)
    )


def test_turismo_paid_funds() -> None:
    """EBNT 3.39 + 3.39, FAST 10 + 2 and 1.00 solidarity."""
    result = _run("turismo-federalberghi", "4", frozenset({"ebnt", "fast"}))

    ebnt = _pct("0.002", _TURISMO)
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == ebnt + Decimal(10)
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == ebnt + Decimal(2)
    assert _entries(result, "fast_")["solidarity"] == Decimal("1.00")


def test_turismo_unpaid_funds_owe_their_elements() -> None:
    """0.60% of the minimo (10.17) and 14 EUR, on the month and on the 13th."""
    for thirteenth in (False, True):
        result = _run("turismo-federalberghi", "4", frozenset(), thirteenth=thirteenth)
        elements = sorted(
            i.amount for i in result.pay_items if "_element_" in i.item_id
        )
        assert elements == sorted([_pct("0.006", _TURISMO), Decimal("14.00")])


def test_turismo_13th_pays_the_ebnt_only() -> None:
    """EBNT is due on 14 months, FAST on 12."""
    result = _run(
        "turismo-federalberghi", "4", frozenset({"ebnt", "fast"}), thirteenth=True
    )

    ebnt = _pct("0.002", _TURISMO)
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == ebnt
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == ebnt


@pytest.mark.parametrize(
    ("funds", "employer", "employee", "elements"),
    [
        (
            frozenset({"ebt", "fondo_est"}),
            _pct("0.002", _FIPE) + Decimal(12),
            _pct("0.002", _FIPE),
            [],
        ),
        (
            frozenset(),
            Decimal(0),
            Decimal(0),
            sorted([_pct("0.006", _FIPE), Decimal("16.00")]),
        ),
    ],
)
def test_fipe_funds(
    funds: frozenset[str],
    employer: Decimal,
    employee: Decimal,
    elements: list[Decimal],
) -> None:
    """Paid: EBT 3.60 + 3.60 and Fondo Est 12; not paid: 10.80 and 16."""
    result = _run("pubblici-esercizi-fipe-angem", "3", funds)

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == employer
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == employee
    assert (
        sorted(i.amount for i in result.pay_items if "_element_" in i.item_id)
        == elements
    )


def test_turismo_quadro_pays_quas_a_twelfth_a_month() -> None:
    """Qu.A.S. 380 + 50 EUR a year: 31.67 and 4.17 a month, 3.17 solidarity.

    Art. 144, p. 48, from 2026; FAST does not cover the quadri.
    """
    result = _run("turismo-federalberghi", "A", frozenset({"quas", "fast"}))

    assert _entries(result, "quas_") == {
        "er": Decimal("31.67"),
        "solidarity": Decimal("3.17"),
        "emp": Decimal("4.17"),
    }
    assert not _entries(result, "fast_")


_TERZIARIO = Decimal("1781.68")


@pytest.mark.parametrize(
    ("funds", "employer", "employee", "elements"),
    [
        (
            frozenset({"ebt", "aster"}),
            _pct("0.001", _TERZIARIO) + Decimal(13),
            _pct("0.0005", _TERZIARIO) + Decimal(2),
            [],
        ),
        (
            frozenset(),
            Decimal(0),
            Decimal(0),
            sorted([_pct("0.003", _TERZIARIO), Decimal("16.00")]),
        ),
    ],
)
def test_terziario_funds(
    funds: frozenset[str],
    employer: Decimal,
    employee: Decimal,
    elements: list[Decimal],
) -> None:
    """Terziario Confesercenti IV, minimo 1,781.68 EUR from November 2025.

    Paid: EBT 0.10% + 0.05% (art. 23) and ASTER 13 + 2 EUR from April 2025
    (art. 104 as renewed on 22 March 2024, p. 17); not paid: 0.30% and 16 EUR.
    """
    result = _run("terziario-confesercenti", "IV", funds)

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == employer
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == employee
    assert (
        sorted(i.amount for i in result.pay_items if "_element_" in i.item_id)
        == elements
    )


#: Commercio Confcommercio 4th level from 1 November 2025, accordo
#: integrativo 28 March 2024, p. 65: "IV 1257,46 524,22 1781,68".  The
#: table lists the contingenza apart from the paga base: the EBT reads both
#: (art. 23, "paga base e contingenza"), as the observed payslip p17 does
#: ("retribuzione ente bilaterale commercio" 1981.84 for level 3).
_COMMERCIO = Decimal("1257.46") + Decimal("524.22")


@pytest.mark.parametrize(
    ("funds", "employer", "employee", "elements"),
    [
        (
            frozenset({"ebt", "fondo_est"}),
            _pct("0.001", _COMMERCIO) + Decimal(13),
            _pct("0.0005", _COMMERCIO) + Decimal(2),
            [],
        ),
        (
            frozenset({"ebt"}),
            _pct("0.001", _COMMERCIO),
            _pct("0.0005", _COMMERCIO),
            [Decimal("16.00")],
        ),
        (
            frozenset(),
            Decimal(0),
            Decimal(0),
            sorted([_pct("0.003", _COMMERCIO), Decimal("16.00")]),
        ),
    ],
)
def test_commercio_funds(
    funds: frozenset[str],
    employer: Decimal,
    employee: Decimal,
    elements: list[Decimal],
) -> None:
    """Commercio Confcommercio 4, June 2026: 1.78 + 13 and 0.89 + 2 paid.

    Paid: EBT 0.10% + 0.05% (art. 23, 2024 renewal p. 12) and Fondo Est 13 +
    2 EUR from April 2025 (art. 104 as renewed, p. 17); not paid: the EBT
    element of 0.30% (5.35, Testo Unico 2019 p. 49) and 16 EUR (p. 17).
    """
    result = _run("commercio-confcommercio", "4", funds)

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == employer
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == employee
    assert (
        sorted(i.amount for i in result.pay_items if "_element_" in i.item_id)
        == elements
    )


def test_commercio_fondo_est_carries_the_solidarity_contribution() -> None:
    """10% INPS solidarity on the 13 EUR of the employer, none on the EBT."""
    result = _run("commercio-confcommercio", "4", frozenset({"ebt", "fondo_est"}))

    assert _entries(result, "fondo_est_") == {
        "er": Decimal("13.00"),
        "solidarity": Decimal("1.30"),
        "emp": Decimal("2.00"),
    }
    assert "solidarity" not in _entries(result, "ebt_")


def test_commercio_13th_pays_the_ebt_and_both_elements() -> None:
    """The EBT and the two elements are due on 14 months, Fondo Est on 12.

    December 2026 reads the tranche of 1 November 2026 (p. 65, "IV 1292,46
    524,22 1816,68").
    """
    december = Decimal("1292.46") + Decimal("524.22")
    paid = _run(
        "commercio-confcommercio", "4", frozenset({"ebt", "fondo_est"}), thirteenth=True
    )
    unpaid = _run("commercio-confcommercio", "4", frozenset(), thirteenth=True)

    assert _posted(paid, AccountKind.BILATERAL_FUND_EMPLOYER) == _pct("0.001", december)
    assert _posted(paid, AccountKind.BILATERAL_FUND_EMPLOYEE) == _pct(
        "0.0005", december
    )
    assert sorted(
        i.amount for i in unpaid.pay_items if "_element_" in i.item_id
    ) == sorted([_pct("0.003", december), Decimal("16.00")])


def test_commercio_quadro_pays_quas_and_quadrifor_a_twelfth_a_month() -> None:
    """Qu.A.S. 390 + 56 EUR a year from 2026 (p. 18), Quadrifor 50 + 25 (p. 19).

    32.50 and 4.67 a month with 3.25 solidarity; 4.17 and 2.08 a month with
    none (a training fund); Fondo Est does not cover the quadri.  The
    employer states Quadrifor as paid, so the oracle holds whether or not a
    fund without an element needs the fact.
    """
    result = _run(
        "commercio-confcommercio", "Q", frozenset({"quas", "quadrifor", "fondo_est"})
    )

    assert _entries(result, "quas_") == {
        "er": Decimal("32.50"),
        "solidarity": Decimal("3.25"),
        "emp": Decimal("4.67"),
    }
    assert _entries(result, "quadrifor_") == {
        "er": Decimal("4.17"),
        "emp": Decimal("2.08"),
    }
    assert not _entries(result, "fondo_est_")


def test_commercio_quadro_without_quas_owes_37_eur() -> None:
    """Qu.A.S. not paid: an element of 37 EUR (p. 18); Quadrifor owes none."""
    result = _run("commercio-confcommercio", "Q", frozenset({"ebt", "quadrifor"}))

    assert [i.amount for i in result.pay_items if "_element_" in i.item_id] == [
        Decimal("37.00")
    ]
