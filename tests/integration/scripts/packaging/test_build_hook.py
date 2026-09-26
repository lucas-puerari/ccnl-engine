"""Tests that guard against silent packaging and demo startup failures.

Build hook: scripts/packaging/build_hook.py lists source directories whose JSON
files it compresses into .json.gz for the wheel.  A typo in any of those
paths silently produces an empty wheel -- no data files are found, no error is
raised -- which breaks all runtime data access without any test failure.

Demo glue: demo/app.py imports ccnl_engine modules that run inside Pyodide.
An obsolete import path lets the wheel build succeed but crashes the browser at
runtime with ModuleNotFoundError.  demo/index.html carries a WHEEL_VERSION
placeholder that pages.yml substitutes at publish time; if it goes missing, the
browser receives a literal filename and micropip.install fails silently.

The module also covers demo-layer correctness:
- Gross breakdown annualises correctly when allowances carry per-component
  months_per_year; additional_months is read from the CCNL, not derived from ratio
- hasL3 predicate covers all conditional L3 rows, including leave and sick integration

All checks use AST parsing or plain string search so that neither hatchling
nor a browser runtime is required in the test environment.
"""

from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_BUILD_HOOK = _PROJECT_ROOT / "scripts" / "packaging" / "build_hook.py"
_APP_PY = _PROJECT_ROOT / "demo" / "app.py"
_INDEX_HTML = _PROJECT_ROOT / "demo" / "index.html"


def _extract_data_dirs() -> list[tuple[str, str]]:
    """Parse _DATA_DIRS from build_hook.py without importing it.

    Returns:
        List of (dist_prefix, src_rel) tuples, same as _DATA_DIRS.

    Raises:
        AssertionError: If _DATA_DIRS cannot be found in the build hook.
    """
    tree = ast.parse(_BUILD_HOOK.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        # _DATA_DIRS uses a type annotation so it is an AnnAssign, not Assign.
        if not (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "_DATA_DIRS"
            and isinstance(node.value, ast.List)
        ):
            continue
        pairs: list[tuple[str, str]] = []
        for elt in node.value.elts:
            if not isinstance(elt, ast.Tuple) or len(elt.elts) != 2:
                continue
            a, b = elt.elts
            if isinstance(a, ast.Constant) and isinstance(b, ast.Constant):
                pairs.append((str(a.value), str(b.value)))
        return pairs
    msg = "_DATA_DIRS not found in build_hook.py"
    raise AssertionError(msg)


_DATA_DIRS = _extract_data_dirs()


@pytest.mark.parametrize(
    ("dist_prefix", "src_rel"),
    _DATA_DIRS,
    ids=[src for _, src in _DATA_DIRS],
)
class TestBuildHookDataDirs:
    """Each entry in _DATA_DIRS must point to a real, populated directory."""

    def test_source_dir_exists(self, dist_prefix: str, src_rel: str) -> None:
        """The source directory listed in the build hook must exist."""
        src_dir = _PROJECT_ROOT / src_rel
        assert src_dir.is_dir(), (
            f"Build hook source directory not found: {src_rel!r}. "
            "Check the _DATA_DIRS entries in scripts/packaging/build_hook.py."
        )

    def test_source_dir_has_json_files(self, dist_prefix: str, src_rel: str) -> None:
        """The source directory must contain at least one .json file."""
        src_dir = _PROJECT_ROOT / src_rel
        json_files = list(src_dir.glob("*.json"))
        assert len(json_files) > 0, (
            f"No .json files found in {src_rel!r}. "
            "The wheel would be built without any data files."
        )


def _ccnl_imports_in(source: str) -> list[str]:
    """Return ccnl_engine module names from top-level ``from X import Y`` nodes.

    Returns:
        Unique module name strings that start with ``ccnl_engine``.
    """
    tree = ast.parse(source)
    return [
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module
        and node.module.startswith("ccnl_engine")
    ]


class TestDemoGlue:
    """Demo startup must not be broken by stale imports or a missing placeholder."""

    def test_app_py_imports_resolve(self) -> None:
        """Every ccnl_engine import in demo/app.py must exist in the package."""
        modules = _ccnl_imports_in(_APP_PY.read_text(encoding="utf-8"))
        assert modules, "No ccnl_engine imports found in demo/app.py"
        for module in modules:
            importlib.import_module(module)

    def test_index_html_has_wheel_version_placeholder(self) -> None:
        """WHEEL_VERSION must appear in index.html or ui.js for sed substitution."""
        ui_js = _PROJECT_ROOT / "demo" / "ui.js"
        html = _INDEX_HTML.read_text(encoding="utf-8")
        js = ui_js.read_text(encoding="utf-8") if ui_js.exists() else ""
        assert "WHEEL_VERSION" in html or "WHEEL_VERSION" in js, (
            "Neither demo/index.html nor demo/ui.js contains WHEEL_VERSION. "
            "The pages.yml sed pass would silently produce a broken page."
        )

    def test_generate_snippet_removed(self) -> None:
        """The code-snippet tab and generateSnippet must not exist in ui.js.

        The code-snippet tab and its supporting logic were removed; this guard
        ensures they are not accidentally reintroduced.
        """
        ui_js = _PROJECT_ROOT / "demo" / "ui.js"
        js = ui_js.read_text(encoding="utf-8")
        assert "generateSnippet" not in js, (
            "generateSnippet found in ui.js — the code-snippet tab was "
            "intentionally removed; do not reintroduce it here."
        )

    def test_do_compute_catches_pyodide_errors(self) -> None:
        """``doCompute`` must wrap pyodide.runPython in try/catch.

        Without the guard, any exception from the Python bridge (e.g.
        invalid overtime_weeks JSON) propagates uncaught instead of
        reaching showError().
        """
        ui_js = _PROJECT_ROOT / "demo" / "ui.js"
        js = ui_js.read_text(encoding="utf-8")
        do_compute_idx = js.find("function doCompute(")
        assert do_compute_idx != -1, "doCompute not found in ui.js"
        # Find the matching closing brace by tracking brace depth.
        depth = 0
        func_end = do_compute_idx
        for i, ch in enumerate(js[do_compute_idx:], start=do_compute_idx):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    func_end = i
                    break
        body = js[do_compute_idx:func_end]
        assert "try {" in body or "try{" in body, (
            "doCompute does not contain a try block. "
            "Exceptions from pyodide.runPython bypass showError()."
        )
        assert "catch" in body, (
            "doCompute does not contain a catch clause. "
            "Exceptions from pyodide.runPython bypass showError()."
        )

    def test_compare_error_uses_local_element_not_show_error(self) -> None:
        """Compare error branch must call showCompareError, not showError.

        showError() hides #results, which removes the compare form (selectors,
        buttons) from view even though the base result is still valid.
        showCompareError() targets #compare-error inside the compare panel and
        leaves #results visible.
        """
        ui_js = _PROJECT_ROOT / "demo" / "ui.js"
        js = ui_js.read_text(encoding="utf-8")
        # Extract initCompare body.
        init_idx = js.find("function initCompare(")
        assert init_idx != -1, "initCompare not found in ui.js"
        depth = 0
        func_end = init_idx
        for i, ch in enumerate(js[init_idx:], start=init_idx):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    func_end = i
                    break
        body = js[init_idx:func_end]
        assert "showCompareError(" in body, (
            "initCompare does not call showCompareError(). "
            "A compare error will hide #results and the compare form."
        )
        assert "showError(" not in body, (
            "initCompare still calls showError() on a compare error. "
            "This hides #results even when the base result is valid."
        )
        # clearCompare must also clear the local error box.
        clear_idx = js.find("function clearCompare(")
        assert clear_idx != -1, "clearCompare not found in ui.js"
        depth = 0
        clear_end = clear_idx
        for i, ch in enumerate(js[clear_idx:], start=clear_idx):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    clear_end = i
                    break
        clear_body = js[clear_idx:clear_end]
        assert "clearCompareError(" in clear_body, (
            "clearCompare does not call clearCompareError(). "
            "A stale compare error message stays visible after Azzera."
        )

    def test_index_html_has_compare_error_element(self) -> None:
        """index.html must contain #compare-error inside the compare panel.

        Without this element showCompareError() cannot display the message and
        throws a TypeError at runtime.
        """
        html = _INDEX_HTML.read_text(encoding="utf-8")
        assert 'id="compare-error"' in html, (
            "#compare-error element missing from index.html. "
            "showCompareError() will throw TypeError at runtime."
        )
        # The element must appear after panel-compare opens.
        panel_compare_idx = html.find('id="panel-compare"')
        compare_error_idx = html.find('id="compare-error"')
        assert panel_compare_idx != -1, "#panel-compare not found in index.html"
        assert panel_compare_idx < compare_error_idx, (
            "#compare-error must appear inside #panel-compare."
        )

    def test_compute_salary_invalid_weeks_json_returns_error(self) -> None:
        """compute_salary must return {error: ...} for invalid overtime_weeks.

        Before the fix, _build_time_supplements() was called outside the
        try block, so JSONDecodeError / AttributeError / ValueError propagated
        uncaught to the caller instead of being converted to an error dict.
        """
        demo_dir = str(_PROJECT_ROOT / "demo")
        if demo_dir not in sys.path:
            sys.path.insert(0, demo_dir)
        demo_app = importlib.import_module("app")

        bad_inputs = [
            "[",  # JSONDecodeError
            "[1]",  # AttributeError: int has no .get
            '[{"weekday_hours":-1}]',  # ValueError from Decimal validation
        ]
        for bad in bad_inputs:
            raw = demo_app.compute_salary(
                "tessile-moda-artigianato-confartigianato.json",
                "1",
                "permanent",
                50,
                overtime_weeks=bad,
            )
            result = json.loads(raw)
            assert "error" in result, (
                f"compute_salary did not return an error dict for "
                f"overtime_weeks={bad!r}; got {raw!r}"
            )
            assert result["error"].startswith("overtime_weeks:"), (
                f"Error message should be prefixed 'overtime_weeks:'; "
                f"got {result['error']!r}"
            )


# ---------------------------------------------------------------------------
# additional_months from CCNL + breakdown reconciliation
# hasL3 predicate covers leave and sick integration rows
# ---------------------------------------------------------------------------

_DEMO_DIR = _PROJECT_ROOT / "demo"
_UI_JS = _PROJECT_ROOT / "demo" / "ui.js"


def _import_demo_app() -> types.ModuleType:
    """Import demo/app.py, inserting demo/ into sys.path if needed.

    Returns:
        The imported ``app`` module.
    """
    demo_dir = str(_DEMO_DIR)
    if demo_dir not in sys.path:
        sys.path.insert(0, demo_dir)
    return importlib.import_module("app")


class TestBreakdownReconciliation:
    """gross breakdown must reconcile when allowances carry months_per_year != nm."""

    def test_igiene_ambientale_d2_breakdown_reconciles(self) -> None:
        """igiene-ambientale D2 has 14 additional_months.

        The ratio gross_annual/gross_monthly approximates 13.9 due to rounding;
        reading additional_months from the CCNL parameters gives 14.  The breakdown
        table must use the exact contractual value so that base*nm + allowances_annual
        + other_components*nm equals gross_annual within one cent.
        """
        app = _import_demo_app()
        raw = app.compute_salary(
            "igiene-ambientale-utilitalia.json",
            "D2",
            "permanent",
            50,
        )
        r = json.loads(raw)
        assert "error" not in r, f"compute_salary returned error: {r.get('error')}"

        nm = r["additional_months"]
        assert abs(nm - 14.0) < 1e-9, (
            f"additional_months should be 14 (from CCNL), got {nm}. "
            "Check that demo/app.py reads from CCNL parameters, not ratio."
        )

        # The breakdown table formula: allowances_annual is derived from gross_annual
        # so that base*nm + allowances_annual + seniority*nm + ad_personam*nm
        # == gross_annual (when no RAL override).
        base_annual = r["base_monthly"] * nm
        seniority_annual = (r["seniority_monthly"] or 0) * nm
        ad_personam_annual = (r["ad_personam_monthly"] or 0) * nm
        allowances_annual = (
            r["gross_annual"] - base_annual - seniority_annual - ad_personam_annual
        )
        reconstructed = (
            base_annual + seniority_annual + allowances_annual + ad_personam_annual
        )
        assert abs(reconstructed - r["gross_annual"]) < 0.01, (
            f"Breakdown does not reconcile: reconstructed {reconstructed:.2f} "
            f"!= gross_annual {r['gross_annual']:.2f}"
        )


class TestHasL3Predicate:
    """hasL3 in renderBreakdown must cover leave and sick integration rows."""

    def _get_has_l3_stmt(self) -> str:
        """Extract the hasL3 assignment from renderBreakdown in ui.js.

        Returns:
            The text of the ``const hasL3 = ...`` statement, without the trailing
            semicolon.
        """
        js = _UI_JS.read_text(encoding="utf-8")
        func_idx = js.find("function renderBreakdown(")
        assert func_idx != -1, "renderBreakdown not found in ui.js"
        depth = 0
        func_end = func_idx
        for i, ch in enumerate(js[func_idx:], start=func_idx):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    func_end = i
                    break
        func_body = js[func_idx:func_end]
        has_l3_idx = func_body.find("const hasL3 =")
        assert has_l3_idx != -1, "hasL3 assignment not found inside renderBreakdown"
        stmt_end = func_body.find(";", has_l3_idx)
        return func_body[has_l3_idx:stmt_end]

    def test_has_l3_includes_leave_accrued(self) -> None:
        """hasL3 must reference leave_accrued_days_monthly.

        Without this, the leave-accrued row is unreachable when only
        ``LeaveInput`` is supplied.
        """
        stmt = self._get_has_l3_stmt()
        assert "leave_accrued_days_monthly" in stmt, (
            "hasL3 does not reference leave_accrued_days_monthly. "
            "The leave-accrued row is never shown when only leave is supplied."
        )

    def test_has_l3_includes_sick_company_integration(self) -> None:
        """hasL3 must reference sick_company_integration_monthly.

        Without this, the sick-integration row is unreachable when only
        ``SickInput`` triggers the company complement (not the INPS indemnity).
        """
        stmt = self._get_has_l3_stmt()
        assert "sick_company_integration_monthly" in stmt, (
            "hasL3 does not reference sick_company_integration_monthly. "
            "The row is never shown when only sick is supplied."
        )

    def test_has_l3_covers_all_rendered_rows(self) -> None:
        """Every field guarding a row in the L3 section must appear in hasL3.

        This prevents regressions where a new L3 row is added without
        updating the predicate.
        """
        js = _UI_JS.read_text(encoding="utf-8")
        func_idx = js.find("function renderBreakdown(")
        assert func_idx != -1
        depth = 0
        func_end = func_idx
        for i, ch in enumerate(js[func_idx:], start=func_idx):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    func_end = i
                    break
        func_body = js[func_idx:func_end]
        # Fields that guard their own row inside the hasL3 block.
        l3_gated_fields = [
            "overtime_supplement_monthly",
            "night_supplement_monthly",
            "holiday_supplement_monthly",
            "absence_deduction_monthly",
            "leave_accrued_days_monthly",
            "sick_inps_indemnity_monthly",
            "sick_company_integration_monthly",
            "fringe_benefit_annual",
            "welfare_annual",
            "bonus_annual",
        ]
        has_l3_idx = func_body.find("const hasL3 =")
        stmt_end = func_body.find(";", has_l3_idx)
        has_l3_stmt = func_body[has_l3_idx:stmt_end]
        missing = [f for f in l3_gated_fields if f not in has_l3_stmt]
        assert not missing, (
            f"hasL3 is missing these fields that guard L3 rows: {missing}. "
            "Add them to the predicate so those rows are reachable."
        )
