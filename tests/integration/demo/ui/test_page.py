"""The demo page, its script and its two languages stay consistent.

The script reads elements by id and strings by key: a missing one breaks the
page at runtime with no build error, as a removed ``inp-ot-weeks`` field once
did.  The examples are run through ``demo/app.py``, so that each one computes.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine.catalog import RulesetReadiness, VerificationStatus
from ccnl_engine.provenance.source.models import SourceKind

if TYPE_CHECKING:
    import types

_DEMO = Path(__file__).resolve().parents[4] / "demo"
_HTML = (_DEMO / "index.html").read_text(encoding="utf-8")
_JS = (_DEMO / "ui.js").read_text(encoding="utf-8")
_LANGS = {
    path.stem: json.loads(path.read_text(encoding="utf-8"))
    for path in sorted((_DEMO / "localization").glob("*.json"))
}
#: Ids the script creates: the visible input of each combobox.
_CREATED_IDS = {
    "sel-ccnl-input",
    "sel-regione-input",
    "sel-comune-input",
    "cmp-ccnl-input",
}


def _function(name: str) -> str:
    """Return the source of the top-level function ``name`` of ui.js.

    Returns:
        From ``function name(`` to its matching closing brace.

    Raises:
        AssertionError: When the function has no closing brace.
    """
    start = _JS.index(f"function {name}(")
    depth = 0
    for index in range(_JS.index("{", start), len(_JS)):
        depth += {"{": 1, "}": -1}.get(_JS[index], 0)
        if depth == 0:
            return _JS[start : index + 1]
    raise AssertionError(name)  # pragma: no cover


def _examples() -> list[dict[str, Any]]:
    """Return the EXAMPLES of ui.js, parsed from their object literal.

    Returns:
        One ``{key, params}`` per example.
    """
    literal = _JS[_JS.index("const EXAMPLES = [") + len("const EXAMPLES = ") :]
    literal = literal[: literal.index("];") + 1]
    literal = re.sub(r"(\w+):", r'"\1":', literal)
    literal = re.sub(r",(\s*[}\]])", r"\1", literal)
    examples: list[dict[str, Any]] = json.loads(literal)
    return examples


def test_every_element_the_script_reads_exists() -> None:
    """Each ``getElementById`` names an id of the page."""
    used = set(re.findall(r'getElementById\("([\w-]+)"\)', _JS))
    defined = set(re.findall(r'id="([\w-]+)"', _HTML)) | _CREATED_IDS

    assert used
    assert used <= defined


def test_both_languages_have_the_same_keys() -> None:
    """Italian and English translate the same strings."""
    assert set(_LANGS) == {"it", "en"}
    assert set(_LANGS["it"]) == set(_LANGS["en"])


def _dynamic_keys() -> set[str]:
    """Return the keys the script builds from values.

    Returns:
        The keys of examples, contract types, readiness, confidence, source
        kinds, trace categories and omission topics.
    """
    topics = set(
        re.findall(r':\s*"(\w+)",', _JS[_JS.index("MATERIAL_FACTS") :].split("};")[0])
    )
    readiness = [*(r.value for r in RulesetReadiness), "untracked"]
    return {
        *(
            f"example.{ex['key']}.{part}"
            for ex in _examples()
            for part in ("title", "sub", "why")
        ),
        *(f"contract.{c}" for c in ("permanent", "fixed_term", "apprentice")),
        *(f"reliability.head.{r}" for r in readiness),
        *(f"reliability.ruleset.{r}" for r in readiness),
        *(f"readiness.{r.value}" for r in RulesetReadiness),
        *(f"confidence.{v.value}" for v in VerificationStatus),
        *(f"sources.kind.{k.value}" for k in SourceKind),
        *(
            f"trace.{part}.{c}"
            for part in ("cat", "label")
            for c in ("base_salary", "seniority", "allowance", "gross")
        ),
        *(f"reliability.omission.{topic}" for topic in topics),
    }


@pytest.mark.parametrize("lang", sorted(_LANGS))
def test_every_string_the_page_shows_is_translated(lang: str) -> None:
    """Static keys of page and script and the keys built from values exist."""
    static = (
        set(re.findall(r'data-i18n(?:-tip|-placeholder|-aria)?="([\w.]+)"', _HTML))
        | set(re.findall(r'\bt\("([\w.]+)"', _JS))
        | set(
            re.findall(r'(?:setProgress\(\d+, |makeCombobox\([^)]*, )"([\w.]+)"\)', _JS)
        )
    )

    missing = (static | _dynamic_keys()) - set(_LANGS[lang])
    assert missing == set()


def test_no_untranslated_label_in_the_script() -> None:
    """User-facing text of the script goes through ``t``, not literals."""
    assert "FEATURE_LABELS" not in _JS
    assert "Simulation only" not in _JS
    assert not re.search(r'textContent = "[A-Za-z]', _JS)


@pytest.fixture(scope="module")
def demo_app() -> types.ModuleType:
    """Load demo/app.py without adding demo/ to sys.path permanently.

    Returns:
        The loaded demo app module.
    """
    spec = importlib.util.spec_from_file_location("_test_demo_ui_app", _DEMO / "app.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_test_demo_ui_app"] = module
    spec.loader.exec_module(module)
    return module


def test_the_four_examples_compute(demo_app: types.ModuleType) -> None:
    """Each example runs, states its seniority and names a different case."""
    examples = _examples()

    assert [ex["key"] for ex in examples] == [
        "full_time",
        "part_time",
        "apprentice",
        "domestic",
    ]
    for ex in examples:
        result = json.loads(demo_app.compute_salary(json.dumps(ex["params"])))
        assert "error" not in result, (ex["key"], result)
        assert "seniority_months" in ex["params"]
    assert examples[0]["params"]["ccnl"] == "metalmeccanico-federmeccanica"


def test_do_compute_catches_pyodide_errors() -> None:
    """An exception from the Python bridge becomes an error result."""
    body = _function("doCompute")

    assert "try {" in body
    assert "catch" in body


def test_compare_errors_stay_in_the_compare_panel() -> None:
    """A compare error must not hide the result it is compared with."""
    assert "showCompareError(" in _function("initCompare")
    assert "showError(" not in _function("initCompare")
    assert "clearCompareError(" in _function("clearCompare")
    compare = _HTML.index('id="compare"')
    assert compare < _HTML.index('id="compare-error"')


def test_readiness_shows_in_the_picker_and_the_compare_panel() -> None:
    """A tier is visible before calculating and for the compared contract."""
    assert "TIER_SYMBOL[c.readiness]" in _JS
    compare = _function("initCompare")
    assert 'getElementById("cmp-readiness")' in compare
    assert "r.ruleset.readiness" in compare
    assert 'id="cmp-readiness"' in _HTML
    for strings in _LANGS.values():
        assert {"form.ccnl.tiers", "compare.readiness"} <= strings.keys()


def test_blocker_copy_separates_missing_facts_from_rule_limits() -> None:
    """The page never blames the user for a limit no input can lift."""
    sentences = _function("blockerSentences")
    assert "reliability.blockers.facts" in sentences
    assert "reliability.blockers.limits" in sentences
    for strings in _LANGS.values():
        assert "{n}" not in strings["reliability.estimate"]
        assert "verificate" not in strings["reliability.ruleset.production"]
        assert "are verified" not in strings["reliability.ruleset.production"]


def test_the_page_names_both_versions_and_a_per_deploy_wheel() -> None:
    """The scenario shows engine and data versions; a deploy never reuses a wheel."""
    assert "r.engine_version" in _JS
    assert "r.bundle_version" in _JS
    assert "./wheels/WHEEL_BUILD/" in _JS
    assert "./app.py?build=WHEEL_BUILD" in _JS
    for strings in _LANGS.values():
        assert {"{engine}", "{bundle}"} <= set(
            re.findall(r"\{\w+\}", strings["results.engine"])
        )
