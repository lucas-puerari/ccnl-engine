"""Facts of a fixed-term contract and the exclusions of its NASpI surcharge."""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.domain.fixed_term import FixedTerm, NaspiExclusion
from ccnl_engine.shared.domain.errors import InvalidInputError


def test_facts_default_to_unknown() -> None:
    """Renewals and exclusion are unknown unless stated."""
    contract = FixedTerm()

    assert (contract.renewals, contract.naspi_exclusion) == (None, None)
    assert contract.type == "fixed_term"


def test_exclusion_is_parsed_from_its_value() -> None:
    """The string value of an exclusion is stored as the member."""
    contract = FixedTerm(renewals=3, naspi_exclusion="replacement")  # type: ignore[arg-type]

    assert contract.naspi_exclusion is NaspiExclusion.REPLACEMENT
    assert contract.renewals == 3


@pytest.mark.parametrize(
    "fields",
    [
        pytest.param({"renewals": -1}, id="negative-renewals"),
        pytest.param({"renewals": True}, id="bool-renewals"),
        pytest.param({"naspi_exclusion": "apprentice"}, id="unknown-exclusion"),
    ],
)
def test_rejects_invalid_facts(fields: dict[str, object]) -> None:
    """A negative or non-int renewal count and an unknown exclusion raise."""
    with pytest.raises(InvalidInputError, match="FixedTerm"):
        FixedTerm(**fields)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("exclusion", "surcharge", "increase"),
    [
        (NaspiExclusion.NONE, False, False),
        (NaspiExclusion.RESEARCH, False, True),
        (NaspiExclusion.REPLACEMENT, True, True),
        (NaspiExclusion.SEASONAL, True, True),
        (NaspiExclusion.PUBLIC_ADMINISTRATION, True, True),
        (NaspiExclusion.SHORT_SERVICE, True, True),
    ],
)
def test_what_each_exclusion_removes(
    exclusion: NaspiExclusion, *, surcharge: bool, increase: bool
) -> None:
    """L. 92/2012 art. 2 c. 29 removes the whole surcharge, and so its increase.

    D.L. 87/2018 art. 1 c. 3 keeps the 1.4% of research contracts and
    removes only the renewal increase of its art. 3 c. 2.
    """
    assert exclusion.excludes_surcharge is surcharge
    assert exclusion.excludes_renewal_increase is increase
