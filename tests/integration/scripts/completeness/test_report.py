"""The completeness report: per CCNL gaps, census rows and the strict gate."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.agreement.census.models import Census
from scripts.completeness import report
from scripts.provenance.evidence.check import snapshot
from scripts.provenance.rules import PayableRule

if TYPE_CHECKING:
    from pathlib import Path

_TEST = "tests/integration/scripts/completeness/test_report.py"
_COMPLETE = report.CcnlCompleteness(
    ccnl_id="x",
    family="commercio",
    readiness="exploratory",
    census_rows=3,
    open_rows=(),
    census_errors=(),
    weak_rules=0,
    shared_weak_rules=0,
    limitations=(),
    outside_input=(),
    capabilities=(),
)


def _rule(file: str, path: str, status: str) -> PayableRule:
    return PayableRule(file, path, ("base_salary",), status)


def test_weak_rules_are_split_by_the_ccnls_that_read_them() -> None:
    """A CCNL file, a yearly sector file and a common file."""
    weak = report.weakness([
        _rule("agreement/anas.json", "levels[0]", "assumed"),
        _rule("agreement/anas.json", "levels[1]", "verified"),
        _rule("contribution/2027/industria.json", "ivs", "missing"),
        _rule("sector/2027/industria.json", "tfr", "assumed"),
        _rule("irpef/work_deduction/2027.json", "minimum", "assumed"),
    ])

    assert weak.by_ccnl == {"anas": 1}
    assert weak.by_sector == {"industria": 2}
    assert weak.common == 1
    assert "agreement/anas.json#levels[0]" in weak.ids
    assert "agreement/anas.json#levels[1]" not in weak.ids


def test_a_ccnl_with_nothing_open_is_complete() -> None:
    """A census and no open item: complete."""
    assert _COMPLETE.complete
    assert _COMPLETE.gaps == ()


@pytest.mark.parametrize(
    ("change", "gap"),
    [
        ({"census_rows": None}, "census missing"),
        ({"open_rows": ("a", "b")}, "2 open requirements"),
        ({"census_errors": ("a: no rule r",)}, "1 census error"),
        ({"weak_rules": 1}, "1 weak rule"),
        ({"shared_weak_rules": 3}, "3 shared weak rules"),
        ({"limitations": ("x/a",)}, "1 monetary limitation"),
        ({"outside_input": ("x/a", "x/b")}, "2 outside_input limitations"),
        ({"capabilities": ("inail",)}, "1 non-native capability"),
        ({"capabilities": ("inail", "una_tantum")}, "2 non-native capabilities"),
    ],
)
def test_each_open_item_is_a_gap(change: dict[str, object], gap: str) -> None:
    """Every kind of open item makes the CCNL incomplete, with its reason."""
    row = replace(_COMPLETE, **change)  # type: ignore[arg-type]

    assert not row.complete
    assert row.gaps == (gap,)


def _census(*rows: dict[str, object]) -> Census:
    return Census.model_validate({
        "schema_version": 1,
        "ccnl_id": "x",
        "requirements": rows,
    })


def _row(row_id: str, **fields: object) -> dict[str, object]:
    return {
        "id": row_id,
        "institute": "sickness",
        "variant": "all",
        "source": {"document_id": "d", "section": "art. 1"},
        "state": "implemented",
        "scenarios": [f"{_TEST}::test_a_ccnl_with_nothing_open_is_complete"],
        **fields,
    }


_EVIDENCE = report.Evidence(
    weakness=report.Weakness(frozenset({"f.json#weak"}), {}, {}, 0),
    rules=frozenset({"f.json#weak", "f.json#strong"}),
    limitations=frozenset({"x/open", "x/closed"}),
    open_limitations=frozenset({"x/open"}),
)


def test_a_row_is_open_until_its_rule_and_links_are_closed() -> None:
    """Origin, state, scenarios, linked limitations and linked rules decide."""
    census = _census(
        _row("a_done", links={"limitations": ["x/closed"], "rules": ["f.json#strong"]}),
        _row("b_absent", state="absent", work=["T03.01"]),
        _row("c_untested", scenarios=[]),
        _row("d_open_limitation", links={"limitations": ["x/open"]}),
        _row("e_weak_rule", links={"rules": ["f.json#weak"]}),
        _row("f_not_applicable", state="not_applicable", scenarios=[]),
        _row("g_seeded", origin="seeded", source=None),
    )

    open_rows, errors = report.census_state(census, _EVIDENCE)

    assert open_rows == (
        "b_absent",
        "c_untested",
        "d_open_limitation",
        "e_weak_rule",
        "g_seeded",
    )
    assert errors == ()


def test_a_name_the_bundle_does_not_hold_is_an_error() -> None:
    """A scenario, limitation or rule that does not exist is reported."""
    census = _census(
        _row(
            "a",
            scenarios=[f"{_TEST}::test_gone", "reference_case:gone"],
            links={"limitations": ["x/gone"], "rules": ["f.json#gone"]},
        )
    )

    _, errors = report.census_state(census, _EVIDENCE)

    assert errors == (
        f"a: no scenario {_TEST}::test_gone",
        "a: no scenario reference_case:gone",
        "a: no limitation x/gone",
        "a: no rule f.json#gone",
    )


@pytest.mark.parametrize(
    ("scenario", "exists"),
    [
        (f"{_TEST}::test_a_ccnl_with_nothing_open_is_complete", True),
        (f"{_TEST}::test_each_open_item_is_a_gap[change0-census missing]", True),
        (f"{_TEST}::TestNone::test_gone", False),
        (f"{_TEST}::", False),
        ("tests/none.py::test_x", False),
    ],
)
def test_a_scenario_is_a_test_function(scenario: str, exists: bool) -> None:
    """A node id resolves to a test function defined in its file."""
    assert report.scenario_exists(scenario) is exists


def test_a_reference_case_scenario_names_a_case_file(tmp_path: Path) -> None:
    """``reference_case:<name>`` resolves to a case of the reference set."""
    case = next(report.REFERENCE_CASES.glob("*.json"))

    assert report.scenario_exists(f"reference_case:{case.stem}", tmp_path)


def test_the_bundle_totals_match_the_evidence_snapshot() -> None:
    """The report counts every weak rule and every open limitation once."""
    built = report.build_report()
    evidence = snapshot()

    assert built.weak_rules == sum(map(len, evidence.weak_rules.values()))
    assert built.open_limitations == sum(map(len, evidence.open_limitations.values()))
    assert len(built.rows) == 132
    assert built.census_errors == ()


def test_today_no_ccnl_is_complete() -> None:
    """Every census is seeded only: every CCNL is incomplete and says why."""
    built = report.build_report()

    assert built.complete == ()
    assert all(row.census_rows == len(row.open_rows) for row in built.rows)


def test_the_page_names_every_ccnl_and_the_totals() -> None:
    """One table row per CCNL, the totals above it."""
    built = report.build_report()
    page = report.render(built)

    assert f"**Complete: 0/{len(built.rows)} CCNLs.**" in page
    assert "| [anas](../contracts/anas.md) | `trasporti-logistica` |" in page


def test_check_and_strict_modes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--check`` fails on drift, ``--strict`` while a CCNL is incomplete."""
    page = tmp_path / "completeness.md"
    monkeypatch.setattr(report, "OUTPUT", page)
    monkeypatch.setattr(report, "ROOT", tmp_path)

    assert report.main(["--check"]) == 1
    assert report.main([]) == 0
    assert page.is_file()
    assert report.main(["--check"]) == 0
    assert report.main(["--check", "--strict"]) == 1
    assert "Complete: 0/132 CCNLs." in capsys.readouterr().out


def test_a_census_error_fails_every_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A dangling name in a census fails even the plain write."""
    built = report.build_report()
    broken = replace(built.rows[0], census_errors=("a: no rule r",))
    monkeypatch.setattr(
        report, "build_report", lambda: replace(built, rows=(broken, *built.rows[1:]))
    )
    monkeypatch.setattr(report, "OUTPUT", tmp_path / "completeness.md")

    assert report.main([]) == 1
