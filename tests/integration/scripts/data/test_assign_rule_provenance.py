"""Statuses assigned to existing provenance records never invent a check."""

from __future__ import annotations

from collections import Counter

import pytest

from scripts.data.assign_rule_provenance import ccnl_status, migrate_ccnl

_CITED = {
    "source_document": {"url": "https://www.cnel.it/ccnl"},
    "section": "Art. 1",
}
_REVIEWED = {
    "verification_status": "verified",
    "verified_by": "reviewer",
    "verified_at": "2026-01-01T00:00:00",
}


@pytest.mark.parametrize(
    ("extraction", "status"),
    [
        ({"method": "manual", **_REVIEWED}, "verified"),
        ({"method": "ai", "model": "m", **_REVIEWED}, "verified"),
        ({"method": "manual", "verification_status": "verified"}, "derived"),
        ({"method": "ai", "verification_status": "unverified"}, "assumed"),
        ({"method": "manual", "verification_status": "unverified"}, "derived"),
        ({"method": "back_calculation"}, "derived"),
    ],
)
def test_status_follows_the_extraction(extraction: dict[str, str], status: str) -> None:
    """Verified needs a named reviewer and a date; AI without them is assumed."""
    record = {"location": _CITED, "extraction": extraction}
    assert ccnl_status(record) == status


@pytest.mark.parametrize(
    "location",
    [None, {"section": "Art. 1"}, {**_CITED, "section": None}],
)
def test_record_without_citation_is_assumed(location: object) -> None:
    """A value without a url and a located clause is neither derived nor verified."""
    record = {"location": location, "extraction": {"method": "manual", **_REVIEWED}}
    assert ccnl_status(record) == "assumed"


def test_migration_keeps_statuses_and_fills_extra_months() -> None:
    """Existing statuses stay; an extra-month period gets an assumed record."""
    counts: Counter[str] = Counter()
    data = {
        "meta": {},
        "levels": [{"provenance": {"status": "missing"}}],
        "parameters": {
            "additional_months": {
                "periods": [{"valid_from": "2026-01-01", "value": "13"}]
            }
        },
    }
    migrated = migrate_ccnl(data, counts)
    assert migrated["levels"][0]["provenance"] == {"status": "missing"}
    (period,) = migrated["parameters"]["additional_months"]["periods"]
    assert period["provenance"]["status"] == "assumed"
    assert period["provenance"]["location"] is None
    assert counts == Counter({"missing": 1, "assumed": 1})
