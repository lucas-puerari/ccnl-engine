"""The hourly pay of a worker category and its percentages on the hours."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.hourly.models import HourlyPay, HourlyPercentage

_LOCATED: dict[str, Any] = {
    "status": "derived",
    "location": {
        "source_document": {
            "document_id": "ccnl-x",
            "title": "CCNL X",
            "kind": "associazione",
        },
        "section": "Art. 1",
    },
}


def _series(value: str) -> dict[str, Any]:
    return {
        "periods": [{"valid_from": "2025-01-01", "valid_until": None, "value": value}]
    }


def _percentage(**fields: Any) -> dict[str, Any]:  # noqa: ANN401
    return {
        "code": "CASSA",
        "description": "Cassa Edile",
        "rate": _series("0.185"),
        "settlement": "cassa_edile",
        "net_rate": _series("0.142"),
        "provenance": _LOCATED,
        **fields,
    }


def test_cassa_edile_percentage_reads_both_rates() -> None:
    """A Cassa Edile percentage keeps its gross and its net rate."""
    percentage = HourlyPercentage.model_validate(_percentage())

    assert percentage.net_rate is not None
    assert percentage.base_allowances == ()


@pytest.mark.parametrize(
    "fields",
    [
        {"net_rate": None},
        {"settlement": "cash"},
        {"rate": _series("1.5")},
        {"net_rate": _series("-0.1")},
        {"net_rate": _series("0.2")},
        {
            "rate": {
                "periods": [
                    {"valid_from": "2026-01-01", "valid_until": None, "value": "0.185"}
                ]
            }
        },
        {
            "rate": {
                "periods": [
                    {
                        "valid_from": "2025-01-01",
                        "valid_until": None,
                        "gap_kind": "not_applicable",
                    }
                ]
            }
        },
    ],
    ids=[
        "accrual_without_net",
        "cash_with_net",
        "rate_above_one",
        "negative_net",
        "net_above_gross",
        "net_before_gross",
        "net_on_a_gap",
    ],
)
def test_inconsistent_rates_fail(fields: dict[str, Any]) -> None:
    """The net rate belongs to an accrual and never exceeds the gross rate."""
    with pytest.raises(ValidationError):
        HourlyPercentage.model_validate(_percentage(**fields))


def test_percentage_codes_are_unique() -> None:
    """Two percentages with one code are rejected."""
    with pytest.raises(ValidationError, match="repeat a code"):
        HourlyPay.model_validate({
            "categories": ["operaio"],
            "percentages": [_percentage(), _percentage()],
            "provenance": _LOCATED,
        })


def test_categories_are_required() -> None:
    """A clause that pays no category by the hour is rejected."""
    with pytest.raises(ValidationError):
        HourlyPay.model_validate({"categories": [], "provenance": _LOCATED})


def test_base_allowance_must_be_an_allowance_of_the_ccnl() -> None:
    """A base allowance no level of the CCNL pays is a data error."""
    ccnl = load_ccnl("edilizia-ance.json")
    data = ccnl.model_dump(mode="json")
    data["parameters"]["hourly_pay"]["percentages"][0]["base_allowances"] = ["ITS"]

    with pytest.raises(ValidationError, match="unknown allowances"):
        type(ccnl).model_validate(data)
