"""The exempt share of the impatriati and researcher regimes in the somma esente.

L. 207/2024 art. 1 c. 9 (Normattiva): "Ai fini della determinazione del
reddito complessivo e del reddito di lavoro dipendente di cui ai commi 4 e
6 del presente articolo rileva anche la quota esente del reddito agevolato
ai sensi dell'articolo 44, comma 1, del decreto-legge 31 maggio 2010, n. 78
[...] nonché dell'articolo 16 del decreto legislativo 14 settembre 2015, n.
147, e dell'articolo 5 del decreto legislativo 27 dicembre 2023, n. 209".

A Commercio level 4 hired on 1 July 2026 earns six months of 1783.75 and
the accrued extra months: about 10,500 EUR of employment income in 2026,
below the 20,000 EUR of c. 4.  15,000 EUR exempt under the impatriati
regime from an earlier employment of the year bring the reddito complessivo
above 20,000: the somma esente is no longer due.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    Employment,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    EmploymentPeriod,
    FamilyComposition,
    NoPensionFund,
    Permanent,
)
from tests.integration.ccnl_engine.payroll.taxation.builders_prior_year import (
    RENEWAL_WAIVED,
)
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire
from tests.knowledge.ccnl_engine.payroll.state.builders_opening_state import (
    fresh_tax_year,
)
from tests.knowledge.ccnl_engine.payroll.support import EMPLOYER, ENGINE
from tests.knowledge.ccnl_engine.payroll.termination.builders_tfr import no_tfr_fund

pytestmark = pytest.mark.legal_scenario

_HIRED = date(2026, 7, 1)


def _july(exempt_regime_income: Decimal) -> PeriodResult:
    current_year = replace(
        CurrentYearTaxFacts.employment_only(2026, _HIRED),
        exempt_regime_income=exempt_regime_income,
    )
    return ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 7),
            payment_date=date(2026, 7, 27),
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                employment_period=EmploymentPeriod(started_on=_HIRED),
                seniority=new_hire(2026),
                tfr_fund=no_tfr_fund(2026),
                tfr_treasury_fund=False,
                contract_type=Permanent(),
                pension_fund=NoPensionFund(),
            ),
            employer=EMPLOYER,
            facts=PeriodFacts(
                regione="IT-25",
                comune_belfiore="F205",
                family_composition=FamilyComposition(),
            ),
            opening_state=fresh_tax_year(2026),
            prior_year=RENEWAL_WAIVED,
            current_year=current_year,
        )
    )


def test_somma_esente_is_due_without_exempt_income() -> None:
    """About 10,500 EUR of reddito complessivo: the somma esente is due."""
    somma = _july(Decimal(0)).closing_state.cash.somma_esente
    assert somma.due is not None
    assert somma.due > 0
    assert somma.recognized > 0


def test_exempt_share_of_the_impatriati_regime_removes_it() -> None:
    """10,500 + 15,000 exempt exceeds 20,000 (c. 9): nothing is due."""
    somma = _july(Decimal(15000)).closing_state.cash.somma_esente
    assert somma.due == 0
    assert somma.recognized == 0
