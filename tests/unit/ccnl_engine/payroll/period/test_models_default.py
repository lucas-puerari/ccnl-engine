"""Classification of the default of a public input field."""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.period.models_default import (
    DefaultPolicy,
    FactEnforcement,
    FieldDefault,
    absence_is_fact,
    requires_fact,
)


def test_absence_is_fact_names_no_fact() -> None:
    """A default that is the fact feeds no capability."""
    default = absence_is_fact("no work event in the period")
    assert default == FieldDefault(
        DefaultPolicy.ABSENCE_IS_FACT, "no work event in the period"
    )


def test_requires_fact_names_the_capability_and_the_fact() -> None:
    """A default that stands for a fact names what the fact feeds."""
    default = requires_fact(
        "addizionale_regionale",
        "facts.regione",
        FactEnforcement.REQUIREMENT,
        "unknown residence",
    )
    assert (default.policy, default.capability, default.fact) == (
        DefaultPolicy.REQUIRES_FACT,
        "addizionale_regionale",
        "facts.regione",
    )
    assert default.enforcement is FactEnforcement.REQUIREMENT


@pytest.mark.parametrize(
    "default",
    [
        pytest.param(
            (DefaultPolicy.ABSENCE_IS_FACT, "", None, None, None), id="no_reason"
        ),
        pytest.param(
            (DefaultPolicy.REQUIRES_FACT, "unknown", "irpef", None, None),
            id="requires_without_fact",
        ),
        pytest.param(
            (
                DefaultPolicy.ABSENCE_IS_FACT,
                "no event",
                "irpef",
                "facts.events",
                FactEnforcement.PENDING,
            ),
            id="absence_with_fact",
        ),
    ],
)
def test_inconsistent_classification_is_rejected(
    default: tuple[DefaultPolicy, str, str | None, str | None, FactEnforcement | None],
) -> None:
    """Capability, fact and enforcement go together with ``requires_fact``."""
    with pytest.raises(ValueError, match="a reason is required"):
        FieldDefault(*default)
