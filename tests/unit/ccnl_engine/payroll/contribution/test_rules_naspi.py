"""NASpI surcharge of a fixed-term contract (L. 92/2012 art. 2 c. 3, 28, 29).

The rules are the minimal ones of
:func:`tests.unit.ccnl_engine.builders.make_year_rules`:
1.4% and 0.5 points per renewal, the figures of c. 28.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.payroll.contribution.rules_naspi import (
    SurchargeReason,
    naspi_surcharge,
)
from ccnl_engine.payroll.employment.inputs import Apprentice, Permanent
from ccnl_engine.payroll.employment.inputs_fixed_term import FixedTerm, NaspiExclusion
from tests.unit.ccnl_engine.builders import make_year_rules

if TYPE_CHECKING:
    from ccnl_engine.tax.annual.models import YearRules

_RULES = make_year_rules()
_AGRICULTURE = _RULES.model_copy(
    update={"fixed_term_exempt_categories": frozenset({WorkerCategory.OPERAIO})}
)
_NO_SURCHARGE = _RULES.model_copy(
    update={
        "fixed_term_additional_rate": Decimal(0),
        "fixed_term_renewal_increment": Decimal(0),
    }
)
_NONE = NaspiExclusion.NONE
_ZERO = Decimal(0)


@pytest.mark.parametrize("contract", [Permanent(), Apprentice(months_elapsed=0)])
def test_other_contracts_pay_no_surcharge(contract: Permanent | Apprentice) -> None:
    """Only a fixed term pays it; c. 29 lett. c excludes apprentices."""
    surcharge = naspi_surcharge(_RULES, contract, None)

    assert (surcharge.rate, surcharge.reason) == (_ZERO, SurchargeReason.NOT_FIXED_TERM)
    assert surcharge.missing_fact is None


@pytest.mark.parametrize("renewals", [0, 1, 3])
def test_each_renewal_adds_half_a_point(renewals: int) -> None:
    """INPS circ. 121/2019 par. 2.3: 1.4%, 1.9%, ..., 1.4% + 0.5% x renewals."""
    contract = FixedTerm(renewals=renewals, naspi_exclusion=_NONE)
    surcharge = naspi_surcharge(_RULES, contract, None)

    assert surcharge.rate == Decimal("0.014") + Decimal("0.005") * renewals
    assert (surcharge.reason, surcharge.renewals) == (SurchargeReason.CHARGED, renewals)
    assert surcharge.missing_fact is None


@pytest.mark.parametrize(
    "exclusion",
    [e for e in NaspiExclusion if e.excludes_surcharge],
)
def test_an_exclusion_of_comma_29_removes_it(exclusion: NaspiExclusion) -> None:
    """Excluded, the unknown renewals do not matter."""
    surcharge = naspi_surcharge(_RULES, FixedTerm(naspi_exclusion=exclusion), None)

    assert (surcharge.rate, surcharge.reason) == (_ZERO, SurchargeReason.EXCLUDED)
    assert surcharge.missing_fact is None


def test_research_keeps_the_rate_without_the_increase() -> None:
    """D.L. 87/2018 art. 1 c. 3: the renewals of research contracts add nothing."""
    contract = FixedTerm(naspi_exclusion=NaspiExclusion.RESEARCH)
    surcharge = naspi_surcharge(_RULES, contract, None)

    assert (surcharge.rate, surcharge.renewals) == (Decimal("0.014"), 0)
    assert surcharge.missing_fact is None


def test_domestic_work_has_no_renewal_increase() -> None:
    """C. 28, third period: not for 'contratti di lavoro domestico'."""
    contract = FixedTerm(renewals=2, naspi_exclusion=_NONE)
    surcharge = naspi_surcharge(_RULES, contract, None, domestic=True)

    assert (surcharge.rate, surcharge.reason) == (
        Decimal("0.014"),
        SurchargeReason.CHARGED,
    )


def test_exempt_category_pays_nothing() -> None:
    """C. 3: the operai agricoli, whatever the other facts."""
    surcharge = naspi_surcharge(_AGRICULTURE, FixedTerm(), WorkerCategory.OPERAIO)

    assert (surcharge.rate, surcharge.reason) == (
        _ZERO,
        SurchargeReason.EXEMPT_CATEGORY,
    )
    assert surcharge.missing_fact is None


def test_other_category_of_an_exempting_sector_pays_it() -> None:
    """An impiegato agricolo is not an operaio agricolo."""
    contract = FixedTerm(renewals=0, naspi_exclusion=_NONE)
    surcharge = naspi_surcharge(_AGRICULTURE, contract, WorkerCategory.IMPIEGATO)

    assert surcharge.rate == Decimal("0.014")
    assert surcharge.missing_fact is None


@pytest.mark.parametrize(
    ("rules", "contract", "fact"),
    [
        pytest.param(
            _AGRICULTURE,
            FixedTerm(renewals=0, naspi_exclusion=_NONE),
            "category",
            id="category",
        ),
        pytest.param(_RULES, FixedTerm(renewals=0), "naspi_exclusion", id="exclusion"),
        pytest.param(
            _RULES, FixedTerm(naspi_exclusion=_NONE), "renewals", id="renewals"
        ),
    ],
)
def test_unknown_fact_is_named(
    rules: YearRules, contract: FixedTerm, fact: str
) -> None:
    """The rate meanwhile is the one of no exclusion and no renewal."""
    surcharge = naspi_surcharge(rules, contract, None)

    assert surcharge.missing_fact == fact
    assert surcharge.rate == Decimal("0.014")


def test_nothing_is_missing_when_the_sector_charges_nothing() -> None:
    """A sector whose rate and increase are zero does not read the facts."""
    surcharge = naspi_surcharge(_NO_SURCHARGE, FixedTerm(), None)

    assert (surcharge.rate, surcharge.missing_fact) == (_ZERO, None)
