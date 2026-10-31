"""Validate provenance of the payable rules and of the expected-value fixtures.

Every payable rule of the bundled knowledge data carries a provenance record
with a known status; the inventory lives in :mod:`scripts.provenance.rules`,
shared with ``scripts/provenance/check.py``.

The JSON files in ``tests/knowledge/ccnl_engine/period/reference_case/`` each
declare a known
``verification`` status consistent with their ``source`` block, and carry the
inputs and expected values that
``tests/integration/ccnl_engine/test_reference_cases.py`` executes. The rules
live in :mod:`scripts.provenance.reference_case.check`, shared with the
provenance gate.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts.provenance.reference_case.check import (
    AXIS_OF,
    CASES_DIR,
    load_case,
    verification_errors,
)
from scripts.provenance.reference_case.check import (
    count_by_status as count_cases,
)
from scripts.provenance.rules import (
    STATUSES,
    ccnl_rules,
    count_by_status,
    fiscal_rules,
    inventory,
    rule_errors,
)

if TYPE_CHECKING:
    from pathlib import Path

_ALL_CASES = sorted(CASES_DIR.glob("*.json"))
_INPUT_KEYS = frozenset({"ccnl_id", "level_code", "year", "month", "headcount"})
#: Inputs a case may add: the hours a domestic CCNL needs, the hours a CCNL
#: paying by the hour pays.
_OPTIONAL_INPUT_KEYS = frozenset({
    "weekly_hours",
    "contributable_hours",
    "ordinary_hours_worked",
    "provincial_pay_element",
})
_EXPECTED_KEYS = frozenset(AXIS_OF)
_SOURCE: dict[str, object] = {"document": "CCNL", "section": "Art. 1"}


def test_cases_exist() -> None:
    """The fixture directory is not accidentally empty."""
    assert _ALL_CASES


def test_case_verification_is_valid() -> None:
    """Every case declares a known status consistent with its source."""
    wrong = {
        p.stem: errors
        for p in _ALL_CASES
        if (errors := verification_errors(load_case(p)))
    }
    assert wrong == {}


def test_status_counts_cover_every_case() -> None:
    """Every case falls into exactly one known status bucket."""
    cases = [load_case(path) for path in _ALL_CASES]
    assert sum(count_cases(cases).values()) == len(cases)


_LINKED: dict[str, object] = {
    "verification": "source_linked",
    "axes": ["base_salary"],
    "source": _SOURCE,
    "expected": {"base_salary": "1000.00"},
}
_PAYSLIP: dict[str, object] = {
    "kind": "observed_payslip",
    "document": "Observed payslip p23",
    "path": "tests/knowledge/ccnl_engine/period/observed_payslip/p23.json",
    "verified_by": "claude-opus-5-5",
    "verified_at": "2026-10-10",
    "independence": "issued by the payroll of the employer",
}
_VERIFIED: dict[str, object] = _LINKED | {
    "verification": "verified",
    "source": _PAYSLIP,
    "tolerance": "0.00",
}


@pytest.mark.parametrize("case", [_LINKED, _VERIFIED])
def test_valid_cases_are_accepted(case: dict[str, object]) -> None:
    """Consistent status, source and axes pass validation."""
    assert verification_errors(case) == []


def test_a_document_hash_is_an_immutable_reference() -> None:
    """A verified source may cite the sha256 of its document instead of a path."""
    source = {k: v for k, v in _PAYSLIP.items() if k != "path"} | {"sha256": "a" * 64}
    assert verification_errors(_VERIFIED | {"source": source}) == []


@pytest.mark.parametrize(
    ("case", "fragment"),
    [
        ({}, "missing 'verification'"),
        ({"source": _SOURCE}, "missing 'verification'"),
        ({"verification": "unverified"}, "unknown verification"),
        ({"verification": "engine_generated"}, "unknown verification"),
        ({"verification": "source_linked"}, "requires a non-empty 'source'"),
        (
            {"verification": "source_linked", "source": {}},
            "requires a non-empty 'source'",
        ),
        ({"verification": "verified"}, "requires a non-empty 'source'"),
        (
            {"verification": "source_linked", "source": "CCNL Art. 1"},
            "'source' must be an object",
        ),
        (_LINKED | {"axes": []}, "not both empty"),
        (_LINKED | {"elements": "fixed_allowances"}, "must be lists"),
        (
            _LINKED | {"axes": ["base_salary", "payslip"]},
            "unknown axis 'payslip'",
        ),
        (
            _LINKED | {"elements": ["bonus_rate"]},
            "unknown element 'bonus_rate'",
        ),
        (
            _LINKED | {"expected": {"base_salary": "1", "bonus": "1"}},
            "'bonus' belongs to no axis",
        ),
        (
            _LINKED | {"expected": {"base_salary": "1", "period_gross": "1"}},
            "needs the axis 'gross'",
        ),
        (
            _LINKED | {"expected": {"base_salary": "1", "fixed_allowances": "1"}},
            "needs the element 'fixed_allowances'",
        ),
        (
            _LINKED | {"axes": ["base_salary", "employee_contributions"]},
            "'employee_contributions' is declared but no expected value backs it",
        ),
    ],
)
def test_invalid_cases_are_rejected(case: dict[str, object], fragment: str) -> None:
    """Missing, unknown, or unsupported statuses and axes are rejected."""
    errors = verification_errors(case)
    assert len(errors) == 1
    assert fragment in errors[0]


def test_fixed_allowances_do_not_cover_the_gross() -> None:
    """A case pinning only the allowances cannot claim the gross of the period."""
    case = _LINKED | {
        "axes": ["base_salary", "gross"],
        "elements": ["fixed_allowances"],
        "expected": {"base_salary": "1000.00", "fixed_allowances": "200.00"},
    }

    assert verification_errors(case) == [
        "'gross' is declared but no expected value backs it"
    ]
    assert verification_errors(case | {"axes": ["base_salary"]}) == []


@pytest.mark.parametrize(
    ("key", "axis"),
    [("base_salary", "base_salary"), ("period_gross", "gross")],
)
def test_each_complete_total_backs_its_axis(key: str, axis: str) -> None:
    """The expected value of a whole total covers its output axis."""
    case = _LINKED | {"axes": [axis], "expected": {key: "1000.00"}}

    assert verification_errors(case) == []


def test_a_components_only_case_is_valid_with_no_axis() -> None:
    """A case may pin components alone; it then validates no output."""
    case = _LINKED | {
        "axes": [],
        "elements": ["fixed_allowances"],
        "expected": {"fixed_allowances": "200.00"},
    }

    assert verification_errors(case) == []


@pytest.mark.parametrize(
    ("change", "fragment"),
    [
        ({"source": _SOURCE}, "source.kind"),
        ({"source": _PAYSLIP | {"kind": "signed_table"}}, "source.kind"),
        ({"source": _PAYSLIP | {"path": "missing.json"}}, "source.sha256 or"),
        (
            {"source": _PAYSLIP | {"sha256": "not-a-digest", "path": None}},
            "source.sha256",
        ),
        (
            {"source": _PAYSLIP | {"sha256": "a" * 64}},
            "source.sha256 or",
        ),
        ({"source": _PAYSLIP | {"verified_by": ""}}, "source.verified_by"),
        ({"source": _PAYSLIP | {"independence": None}}, "source.independence"),
        ({"source": _PAYSLIP | {"verified_at": "10/10/2026"}}, "verified_at"),
        ({"source": _PAYSLIP | {"verified_at": None}}, "verified_at"),
        ({"tolerance": None}, "'tolerance'"),
        ({"tolerance": "-1"}, "'tolerance'"),
    ],
)
def test_a_verified_case_names_its_independent_output(
    change: dict[str, object], fragment: str
) -> None:
    """A verified case cites an output the engine did not produce, checked."""
    errors = verification_errors(_VERIFIED | change)
    assert any(fragment in error for error in errors), errors


def test_load_case_rejects_non_object(tmp_path: Path) -> None:
    """A case file must hold a JSON object."""
    path = tmp_path / "case.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(TypeError, match="must be a JSON object"):
        load_case(path)


def test_count_by_status_reports_zero_for_missing_buckets() -> None:
    """Statuses with no cases still appear with a zero count."""
    counts = count_cases([{"verification": "source_linked"}])
    assert counts == {"verified": 0, "source_linked": 1}


def _runnable(path: Path) -> bool:
    case = load_case(path)
    inputs = case.get("inputs")
    expected = case.get("expected")
    return (
        isinstance(inputs, dict)
        and isinstance(expected, dict)
        and _INPUT_KEYS <= set(inputs) <= _INPUT_KEYS | _OPTIONAL_INPUT_KEYS
        and bool(expected)
        and set(expected) <= _EXPECTED_KEYS
    )


def test_case_declares_runnable_inputs() -> None:
    """Every case carries the inputs the runner uses and pins some of its values."""
    assert [p.stem for p in _ALL_CASES if not _runnable(p)] == []


_RULES = inventory()
_RECORD = {"status": "derived", "location": {"section": "Art. 1"}}


def test_every_payable_rule_has_a_provenance_record() -> None:
    """No bundled payable rule lacks a record or has an unknown status."""
    assert _RULES
    assert rule_errors(_RULES) == []


def test_payable_statuses_cover_every_rule() -> None:
    """Every rule falls into exactly one known status bucket."""
    counts = count_by_status(_RULES)
    assert counts["none"] == 0
    assert sum(counts[status] for status in STATUSES) == len(_RULES)


#: Paths of the shared 2026 tax tables reviewed on 2026-10-12, per file.
_SECTOR_REVIEWED = {
    "irpef_brackets",
    "trattamento_integrativo",
    "ulteriore_detrazione",
    "sterilizzazione_detrazioni",
    "fixed_term_additional_rate",
    "complementary_pension",
    "tfr",
    "tfr.additional_ivs",
    "tfr.compensation",
}


#: Blocks read from INPS circ. 6/2026 and its allegato 1, re-read in sectors
#: whose rates are still derived.
_CIRCULAR_6_REVIEWED = frozenset({"inps.employee_additional", "inps.minimum_base"})
#: Files of which only some blocks are reviewed tables.
_REVIEWED_PATHS = {
    "contribution/2026/artigianato.json": {"inps.cigs_indotto", *_CIRCULAR_6_REVIEWED},
    "contribution/2026/credito.json": _CIRCULAR_6_REVIEWED,
    "contribution/2026/agricoltura.json": {"inps.employee_additional"},
    "contribution/2026/pubblica-amministrazione.json": {
        "inps",
        "inps.public_funds.cpdel",
        *_CIRCULAR_6_REVIEWED,
    },
    "absence/insured/rates.json": {"maternity", "injury"},
}


def _reviewed(file: str, path: str) -> bool:
    """Return whether a non-CCNL rule belongs to a reviewed table.

    Returns:
        True for the reviewed L2 rules of the production CCNL, the edilizia
        and terziario INPS tables, the domestic INPS table, the blocks of
        INPS circ. 6/2026 of the other sectors, the CTPS and CPDEL rates of
        the INPS table of the Gestione Dipendenti Pubblici and the shared
        2026 tax tables.
    """
    if file == "sector/2026/industria.json" and path.startswith("tfr"):
        return True
    if file in _REVIEWED_PATHS:
        return path in _REVIEWED_PATHS[file]
    if file.startswith("sector/2026/"):
        return path in _SECTOR_REVIEWED
    return file in {
        "contribution/2026/industria.json",
        "contribution/2026/edilizia.json",
        "contribution/2026/terziario.json",
        "contribution/2026/lavoro-domestico.json",
        "family/2026.json",
        "tax_credit/somma_esente/2026.json",
        "irpef/work_deduction/2026.json",
        "surtax/regional/2026.json",
        "severance/revaluation/2026.json",
        "severance/settlement/2026.json",
        "termination/naspi/2026.json",
    }


def test_verified_fiscal_rules_are_the_reviewed_tables() -> None:
    """Outside the CCNL files, only reviewed tables are verified.

    They are the L2 rules of the production CCNL, the domestic INPS table of
    INPS circ. 9/2026 and the shared 2026 tax tables (IRPEF, work deduction,
    trattamento integrativo, ulteriore detrazione, family deductions, somma
    esente, regional surtax), the TFR divisor and revaluation of art. 2120
    c.c. (L. 297/1982 art. 1), the INPS maternity indemnity (D.Lgs. 151/2001
    artt. 22-23), the INAIL injury indemnity (D.P.R. 1124/1965) and the
    NASpI contribution of the end of an employment (L. 92/2012 art. 2 c. 31).  Each
    names its reviewer and date (``RuleProvenance`` rejects a verified
    record without them, so the bundle would not load otherwise).  Verified
    CCNL rules point to their review log instead, which the evidence gate
    checks.
    """
    verified = [
        (r.file, r.path)
        for r in _RULES
        if r.status == "verified" and not r.file.startswith("agreement/")
    ]
    assert verified
    assert [rule for rule in verified if not _reviewed(*rule)] == []
    sectors = {file for file, path in verified if path == "irpef_brackets"}
    assert len(sectors) == 8


def test_salary_period_without_provenance_fails() -> None:
    """A salary period without its own record or a level record fails."""
    ccnl = {
        "levels": [
            {
                "code": "Q",
                "base_salary": {
                    "periods": [{"valid_from": "2026-01-01", "value": "1"}]
                },
            }
        ]
    }
    (error,) = rule_errors(tuple(ccnl_rules("agreement/x.json", ccnl)))
    assert error.endswith("levels[Q].base_salary[2026-01-01]: no provenance record")


def test_level_record_covers_its_periods_and_allowances() -> None:
    """A period or an allowance without a record inherits the level's."""
    ccnl = {
        "levels": [
            {
                "code": "1",
                "provenance": _RECORD,
                "base_salary": {
                    "periods": [{"valid_from": "2026-01-01", "value": "1"}]
                },
                "fixed_allowances": [{"code": "edr"}],
            }
        ],
        "parameters": {
            "seniority_increments": {"provenance": _RECORD},
            "additional_months": {
                "periods": [
                    {"valid_from": "2025-01-01", "gap_kind": "missing"},
                    {"valid_from": "2026-01-01", "value": "13", "provenance": _RECORD},
                ]
            },
            "accrual_rule": {"provenance": _RECORD},
        },
    }
    rules = tuple(ccnl_rules("agreement/x.json", ccnl))
    assert [rule.status for rule in rules] == ["derived"] * 5
    assert rule_errors(rules) == []


@pytest.mark.parametrize(
    ("file", "data", "fragment"),
    [
        ("sector/2026/x.json", {"tfr": {"accrual_divisor": "13.5"}}, "tfr"),
        ("sector/2026/x.json", {"irpef_brackets": []}, "irpef_brackets"),
        (
            "contribution/2026/x.json",
            {"inps": {"provenance": None}},
            "inps",
        ),
        ("surtax/regional/2026.json", {"rates": {}}, "rates"),
        ("variable_pay/2026.json", {"pdr": {}}, "pdr"),
        (
            "variable_pay/2026.json",
            {"rinnovo": {"source_status": "derived"}},
            "rinnovo",
        ),
    ],
)
def test_fiscal_block_without_provenance_fails(
    file: str, data: dict[str, object], fragment: str
) -> None:
    """A fiscal block, a table or a regime without a record fails."""
    (error,) = rule_errors(tuple(fiscal_rules(file, data)))
    assert f": {fragment}: no provenance record" in error


def test_missing_status_is_allowed_but_unknown_status_fails() -> None:
    """``missing`` is a valid status; any other string is rejected."""
    data = {
        "tfr": {"provenance": {"status": "missing"}},
        "fixed_term_additional_rate": "0.014",
        "fixed_term_renewal_increment": "0.005",
        "fixed_term_additional_rate_provenance": {"status": "unknown"},
    }
    rules = tuple(fiscal_rules("sector/2026/x.json", data))
    assert [rule.status for rule in rules] == ["unknown", "missing"]
    (error,) = rule_errors(rules)
    assert "unknown status 'unknown'" in error
