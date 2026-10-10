"""Accrual, absence, sickness and first-tier overtime rules are payable."""

from __future__ import annotations

from scripts.ci.payable_rules import ccnl_rules, fiscal_rules

_RECORD: dict[str, object] = {"status": "derived", "location": {"section": "Art. 1"}}


def _band(code: str, **extra: object) -> dict[str, object]:
    return {"code": code, "kind": "percentage", "provenance": _RECORD, **extra}


def test_ccnl_without_accrual_rule_lists_it_as_missing() -> None:
    """The engine default threshold has no CCNL source: status missing."""
    (rule,) = ccnl_rules("contract/agreement/x.json", {"parameters": {}})
    assert (rule.path, rule.status, rule.capabilities) == (
        "accrual_rule",
        "missing",
        ("base_salary",),
    )


def test_stored_accrual_rule_carries_its_record() -> None:
    """A stored clause takes the status of its own record."""
    data = {"parameters": {"accrual_rule": {"provenance": _RECORD}}}
    (rule,) = ccnl_rules("contract/agreement/x.json", data)
    assert rule.status == "derived"


def test_assistance_contribution_is_payable() -> None:
    """The contribution per paid hour is one rule with its own record."""
    data = {
        "parameters": {
            "accrual_rule": {"provenance": _RECORD},
            "assistance_contribution": {"provenance": _RECORD},
        }
    }
    rules = ccnl_rules("contract/agreement/x.json", data)
    assert [(r.path, r.status, r.capabilities) for r in rules][-1] == (
        "assistance_contribution",
        "derived",
        ("assistance_contribution",),
    )


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
        r
        for r in ccnl_rules("contract/agreement/x.json", data)
        if r.path != "accrual_rule"
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
        (rule,) = ccnl_rules("contract/agreement/x.json", data)
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
        for r in ccnl_rules("contract/agreement/x.json", data)
        if r.path.startswith("work_rules")
    ]
    assert work == [
        ("work_rules.absence_rules", ("base_salary", "sickness"), "derived"),
        ("work_rules.sickness_rules", ("sickness",), "assumed"),
    ]


def test_sick_pay_bands_read_their_sibling_record() -> None:
    """The INPS bands record sits in ``bands_provenance``."""
    data = {"bands": [], "bands_provenance": _RECORD}
    (rule,) = fiscal_rules("social_security/sickness/rates.json", data)
    assert (rule.path, rule.capabilities, rule.status) == (
        "bands",
        ("sickness",),
        "derived",
    )


def test_nested_tfr_deduction_is_a_payable_rule() -> None:
    """The additional IVS block inside ``tfr`` is a rule of its own."""
    data = {
        "tfr": {
            "accrual_divisor": "13.5",
            "provenance": _RECORD,
            "additional_ivs": {"rate": "0.0050", "provenance": _RECORD},
        }
    }
    rules = fiscal_rules("taxation/annual/2026/industria.json", data)
    assert [(r.path, r.capabilities, r.status) for r in rules] == [
        ("tfr", ("tfr",), "derived"),
        ("tfr.additional_ivs", ("tfr",), "derived"),
    ]


def test_tax_file_without_tfr_has_no_nested_rule() -> None:
    """A missing parent block yields neither the block nor its child."""
    assert list(fiscal_rules("taxation/annual/2026/industria.json", {})) == []


def test_every_nested_record_of_a_block_is_a_rule() -> None:
    """Sub-blocks with a record are found at any depth, without a key list."""
    tax = {
        "work_deduction": {
            "provenance": _RECORD,
            "brackets": [{"provenance": _RECORD}],
            "minimum": {
                "open_ended": "690",
                "provenance": {"status": "assumed"},
                "detail": {"provenance": _RECORD},
            },
            "plain": {"value": "1"},
        }
    }
    employee_additional = {"provenance": _RECORD}
    inps = {"inps": {"provenance": _RECORD, "employee_additional": employee_additional}}
    found = [
        *fiscal_rules("taxation/annual/2026/industria.json", tax),
        *fiscal_rules("social_security/contribution/2026/industria.json", inps),
    ]
    both = ("inps_employee", "inps_employer")
    assert [(r.path, r.capabilities, r.status) for r in found] == [
        ("work_deduction", ("irpef",), "derived"),
        ("work_deduction.minimum", ("irpef",), "assumed"),
        ("work_deduction.minimum.detail", ("irpef",), "derived"),
        ("inps", both, "derived"),
        ("inps.employee_additional", both, "derived"),
    ]
