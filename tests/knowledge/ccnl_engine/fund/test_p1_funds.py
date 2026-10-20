"""Pension, health and bilateral contributions of the first-round CCNLs.

Logistica (testo unico, sha256
99d743d0924958c9cea8e80ec97377763090ad2b3b84d1a4bb8aa5900f0d6e24): Priamo is
paid 1% by the employer and 1% by the worker (Art. 50, pp. 63-64); Sanilog
and Ebilog (Art. 51-52) are declared, with the health and bilateral
contributions of metalmeccanico federmeccanica and artigianato.  Commercio
models its funds (EBT, Fondo Est, Qu.A.S., Quadrifor) as health funds.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl


def test_logistica_priamo() -> None:
    """1% of the employer, at least 1% of the worker."""
    funds = load_ccnl("logistica-trasporto-confetra").parameters.employer_funds
    (priamo,) = [f for f in funds if f.code == "PRIAMO"]

    assert priamo.rate.value_at(date(2026, 1, 1)) == Decimal("0.0100")
    assert priamo.employee_min_rate is not None
    assert priamo.employee_min_rate.value_at(date(2026, 1, 1)) == Decimal("0.0100")


@pytest.mark.parametrize(
    "slug",
    [
        "logistica-trasporto-confetra",
        "metalmeccanico-artigianato",
    ],
)
def test_health_and_bilateral_funds_are_declared(slug: str) -> None:
    """The contributions the engine does not compute are open limitations."""
    ccnl = load_ccnl(slug)
    variants = {n.limitation.variant for n in ccnl.coverage.notes if n.limitation}

    assert "health_and_bilateral_funds" in variants


def test_federmeccanica_models_its_health_fund_and_benefits() -> None:
    """mètaSalute and the flexible benefits are rules, no longer limitations."""
    ccnl = load_ccnl("metalmeccanico-federmeccanica")
    variants = {n.limitation.variant for n in ccnl.coverage.notes if n.limitation}

    assert {f.code for f in ccnl.parameters.health_funds} == {
        "metasalute",
        "flexible_benefits",
    }
    assert not {"health_and_bilateral_funds", "flexible_benefits"} & variants


def test_commercio_models_its_funds() -> None:
    """The four funds of commercio are rules, not an open limitation."""
    ccnl = load_ccnl("commercio-confcommercio")
    variants = {n.limitation.variant for n in ccnl.coverage.notes if n.limitation}

    assert {f.code for f in ccnl.parameters.health_funds} == {
        "ebt",
        "fondo_est",
        "quas",
        "quadrifor",
    }
    assert "health_and_bilateral_funds" not in variants
