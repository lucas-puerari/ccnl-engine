"""Every payable CCNL rule must carry a provenance record at load time."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.identity.facade import CCNL
from tests.unit.ccnl_engine.builders import make_ccnl_dict


def test_additional_months_period_requires_provenance() -> None:
    """An additional-months period without a record is rejected."""
    data = make_ccnl_dict()
    del data["parameters"]["additional_months"]["periods"][0]["provenance"]
    with pytest.raises(ValidationError, match=r"additional_months\.periods\[0\]"):
        CCNL.model_validate(data)


def test_additional_months_gap_needs_no_provenance() -> None:
    """A gap period holds no value, so it needs no record."""
    data = make_ccnl_dict()
    data["parameters"]["additional_months"]["periods"] = [
        {
            "valid_from": "2019-01-01",
            "valid_until": "2020-01-01",
            "gap_kind": "missing",
        },
        data["parameters"]["additional_months"]["periods"][0],
    ]
    ccnl = CCNL.model_validate(data)
    assert ccnl.parameters.additional_months.periods[0].is_gap
