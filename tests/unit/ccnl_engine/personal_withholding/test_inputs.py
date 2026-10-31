"""Facts of a garnishment or salary assignment and what the state carries."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.balance.obligation.models import EmploymentObligations
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.personal_withholding.inputs import (
    PersonalWithholding,
    PersonalWithholdingKind,
    check_personal_withholdings,
)
from ccnl_engine.personal_withholding.models import WithheldToDate

_FIELDS: dict[str, Any] = {
    "withholding_id": "cessione_1",
    "kind": "salary_assignment",
    "notified_on": date(2026, 1, 10),
    "starts_on": date(2026, 2, 1),
    "total_due": Decimal(3000),
    "installment": Decimal(250),
}


def test_the_kind_is_read_from_its_value() -> None:
    """A string kind is normalized to the enum."""
    assert (
        PersonalWithholding(**_FIELDS).kind is PersonalWithholdingKind.SALARY_ASSIGNMENT
    )


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"installment": None}, "installment"),
        ({"kind": "ordinary"}, "installment"),
        ({"starts_on": date(2026, 1, 9)}, "starts_on"),
        ({"total_due": Decimal(0)}, "total_due"),
        ({"withholding_id": " "}, "withholding_id"),
    ],
)
def test_rejects_an_inconsistent_fact(change: dict[str, Any], field: str) -> None:
    """The installment is stated only where the law does not set the amount."""
    with pytest.raises(InvalidInputError, match=field):
        PersonalWithholding(**(_FIELDS | change))


def test_two_withholdings_share_no_id() -> None:
    """An id names one order, in the request and in the state."""
    one = PersonalWithholding(**_FIELDS)
    with pytest.raises(InvalidInputError, match="share an id"):
        check_personal_withholdings([one, one], "Employment.personal_withholdings")
    with pytest.raises(InvalidInputError, match="tuple or a list"):
        check_personal_withholdings(one, "Employment.personal_withholdings")
    carried = WithheldToDate("cessione_1", Decimal(250))
    with pytest.raises(ValueError, match="personal_withholdings"):
        EmploymentObligations(personal_withholdings=(carried, carried))
