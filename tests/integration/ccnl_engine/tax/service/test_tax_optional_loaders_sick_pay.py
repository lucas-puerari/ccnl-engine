"""Bundled sick-pay rates load through the optional tax loaders."""

from __future__ import annotations

import importlib.resources
import json
from typing import Any

import pytest

from ccnl_engine.provenance.domain.chain import ProvenanceStatus
from ccnl_engine.shared.domain.errors import DataIntegrityError
from ccnl_engine.tax.service.tax_optional_loaders import (
    load_sick_pay_rates,
    sick_pay_rates_from,
)

_FILE = "sick-pay-rates.json"


def _bundled() -> dict[str, Any]:
    pkg = importlib.resources.files("ccnl_engine.knowledge.inps.data")
    raw: dict[str, Any] = json.loads(pkg.joinpath(_FILE).read_text("utf-8"))
    return raw


class TestMiscCoverageGaps:
    """Bundled sick-pay rates."""

    def test_load_sick_pay_rates_returns_valid_rates(self) -> None:
        """The bundled table states every statutory field."""
        rates = load_sick_pay_rates()
        raw = _bundled()

        assert rates.carenza_days == raw["carenza_days"]
        assert rates.annual_max_days == raw["annual_max_days"]
        assert len(rates.bands) == len(raw["bands"])
        assert len(rates.coverage) == len(raw["coverage"])

    def test_indemnity_bands_carry_their_provenance_record(self) -> None:
        """The bands record is read from ``bands_provenance``, never left empty.

        The secondary summary it cites records no URL, so the record is
        ``assumed`` while keeping its location.
        """
        record = load_sick_pay_rates().bands_provenance
        assert record is not None
        assert record.status is ProvenanceStatus.ASSUMED
        assert record.location is not None


@pytest.mark.parametrize(
    "field", ["carenza_days", "bands", "annual_max_days", "coverage"]
)
def test_a_table_without_a_statutory_field_is_a_data_error(field: str) -> None:
    """A missing field names the file and the field; no default is taken."""
    raw = _bundled()
    del raw[field]

    with pytest.raises(DataIntegrityError, match=rf"{_FILE}.*{field}"):
        sick_pay_rates_from(raw, _FILE)


@pytest.mark.parametrize(
    ("field", "value"),
    [("carenza_days", -1), ("bands", []), ("annual_max_days", 0), ("coverage", [])],
)
def test_a_table_with_an_invalid_field_is_a_data_error(
    field: str, value: object
) -> None:
    """A value the model rejects is a data error of the file."""
    raw = _bundled()
    raw[field] = value

    with pytest.raises(DataIntegrityError, match=_FILE):
        sick_pay_rates_from(raw, _FILE)
