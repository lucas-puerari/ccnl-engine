"""A limitation awaiting a publication due by a known date."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from ccnl_engine.limitation.models import (
    AwaitedPublication,
    LimitationStatus,
    ModelLimitation,
    NoteLimitation,
)

_DUE = AwaitedPublication(
    publication="The minimi of 2027", expected_by=date(2027, 1, 31)
)


def _limitation(**changes: object) -> ModelLimitation:
    fields: dict[str, object] = {
        "id": "x/minimi",
        "capability": "base_salary",
        "variant": "minimi",
        "summary": "s",
        "monetary_impact": "yes",
        "status": LimitationStatus.AWAITING_PUBLICATION,
        "rulesets": ("x",),
        "source": "x.json",
        "remediation": "r",
        "awaited": _DUE,
        **changes,
    }
    return ModelLimitation.model_validate(fields)


def test_it_waits_until_its_date_and_still_blocks() -> None:
    """Awaited on 31 January, open work again on 1 February; it blocks runs."""
    limitation = _limitation()
    assert limitation.awaited_on(date(2027, 1, 31))
    assert not limitation.awaited_on(date(2027, 2, 1))
    assert limitation.blocks


def test_an_open_limitation_awaits_nothing() -> None:
    """Only the awaiting status names a publication."""
    assert not _limitation(status=LimitationStatus.OPEN, awaited=None).awaited_on(
        date(2026, 1, 1)
    )


@pytest.mark.parametrize(
    "changes",
    [{"awaited": None}, {"status": LimitationStatus.OPEN}],
    ids=["no-publication", "publication-on-open"],
)
def test_the_publication_goes_with_the_status(changes: dict[str, object]) -> None:
    """Awaiting without a publication, or a publication on another status."""
    with pytest.raises(ValidationError, match="awaited publication"):
        _limitation(**changes)
    with pytest.raises(ValidationError, match="awaited publication"):
        NoteLimitation.model_validate({
            "variant": "minimi",
            "remediation": "r",
            "status": changes.get("status", LimitationStatus.AWAITING_PUBLICATION),
            "awaited": changes.get("awaited", _DUE),
        })
