"""Accrual, absence, sickness and first-tier overtime rules are payable."""

from __future__ import annotations

from scripts.ci.payable_rules import ccnl_rules, fiscal_rules

_RECORD: dict[str, object] = {"status": "derived", "location": {"section": "Art. 1"}}


def _band(code: str, **extra: object) -> dict[str, object]:
    return {"code": code, "kind": "percentage", "provenance": _RECORD, **extra}


def test_ccnl_without_accrual_rule_lists_it_as_missing() -> None:
    """The engine default threshold has no CCNL source: status missing."""
    (rule,) = ccnl_rules("ccnl/data/x.json", {"parameters": {}})
    assert (rule.path, rule.status, rule.capabilities) == (
        "accrual_rule",
        "missing",
        ("base_salary",),
    )


def test_stored_accrual_rule_carries_its_record() -> None:
    """A stored clause takes the status of its own record."""
    data = {"parameters": {"accrual_rule": {"provenance": _RECORD}}}
    (rule,) = ccnl_rules("ccnl/data/x.json", data)
    assert rule.status == "derived"


def test_only_first_tier_overtime_bands_are_payable() -> None:
    """Thresholded, conditional, per-hour and non-overtime bands are not read."""
    bands = [
        _band("OT_DIURNO"),
        _band("OT_DIURNO_EXTRA", hour_threshold_per_week=8),
        _band("OT_DIURNO_LONG", hour_threshold_per_day=10),
        _band("OT_NOTTURNO_STRAORDINARIO", required_context_kinds=["night"]),
        _band("OT_FESTIVO", kind="indennita_per_hour"),
        _band("LAVORO_NOTTURNO"),
    ]
    data = {
        "parameters": {"accrual_rule": {"provenance": _RECORD}},
        "work_rules": {"time_supplements": {"overtime_bands": bands}},
    }
    overtime = [
        r for r in ccnl_rules("ccnl/data/x.json", data) if r.path != "accrual_rule"
    ]
    assert [(r.path, r.capabilities) for r in overtime] == [
        ("overtime_bands[OT_DIURNO]", ("overtime",))
    ]


def test_malformed_work_rules_yield_no_band() -> None:
    """A work-rules block without bands, or not an object, adds no rule."""
    malformed: tuple[object, ...] = (
        {"time_supplements": None},
        [],
        {"time_supplements": {}},
    )
    for work_rules in malformed:
        data: dict[str, object] = {
            "parameters": {"accrual_rule": {}},
            "work_rules": work_rules,
        }
        (rule,) = ccnl_rules("ccnl/data/x.json", data)
        assert rule.path == "accrual_rule"


def test_absence_and_sickness_rules_carry_their_records() -> None:
    """Each block is one rule; the absence rule feeds proration and sickness."""
    data = {
        "parameters": {"accrual_rule": {"provenance": _RECORD}},
        "work_rules": {
            "absence_rules": {"provenance": _RECORD},
            "sickness_rules": {"provenance": {"status": "assumed"}},
            "leave_rules": {"provenance": _RECORD},
        },
    }
    work = [
        (r.path, r.capabilities, r.status)
        for r in ccnl_rules("ccnl/data/x.json", data)
        if r.path.startswith("work_rules")
    ]
    assert work == [
        ("work_rules.absence_rules", ("base_salary", "sickness"), "derived"),
        ("work_rules.sickness_rules", ("sickness",), "assumed"),
    ]


def test_sick_pay_bands_read_their_sibling_record() -> None:
    """The INPS bands record sits in ``bands_provenance``."""
    data = {"bands": [], "bands_provenance": _RECORD}
    (rule,) = fiscal_rules("inps/data/sick-pay-rates.json", data)
    assert (rule.path, rule.capabilities, rule.status) == (
        "bands",
        ("sickness",),
        "derived",
    )
