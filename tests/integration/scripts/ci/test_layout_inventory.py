"""Tests for the rules, the mapping and the command line of layout_inventory.py."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import types

_SCRIPT = Path(__file__).resolve().parents[4] / "scripts" / "ci" / "layout_inventory.py"
_MODULE = "_ci_layout_inventory"
_GIT = shutil.which("git") or "git"


def _load() -> types.ModuleType:
    """Load the script once; its dataclasses need a ``sys.modules`` entry.

    Returns:
        The loaded module.
    """
    if _MODULE in sys.modules:
        return sys.modules[_MODULE]
    spec = importlib.util.spec_from_file_location(_MODULE, _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE] = module
    spec.loader.exec_module(module)
    return module


li = _load()

_MIRROR_RULE = {
    "pattern": "^tests/(?P<category>unit|integration)/"
    "(?P<root>ccnl_engine|demo|scripts)/(?P<path>.+)$",
    "mirror": "{category}",
}
_RULES: dict[str, object] = {
    "rules": [
        {
            "pattern": "^src/ccnl_engine/(?P<name>__init__\\.py)$",
            "target": "src/ccnl_engine/{name}",
        },
        {
            "pattern": "^src/ccnl_engine/knowledge/ccnl/data/(?P<n>[a-z]+\\.json)$",
            "target": "src/ccnl_engine/knowledge/contract/agreement/{n}",
        },
        _MIRROR_RULE,
    ],
    "overrides": {
        "src/ccnl_engine/payroll/__init__.py": {"dissolve": "src/ccnl_engine/payroll"},
        "src/ccnl_engine/payroll/domain/_ledger.py": (
            "src/ccnl_engine/payroll/ledger/models.py"
        ),
        "src/ccnl_engine/payroll/family/__init__.py": {
            "dissolve": "src/ccnl_engine/payroll/family"
        },
        "src/ccnl_engine/payroll/family/spouse.py": (
            "src/ccnl_engine/payroll/family/rules_spouse.py"
        ),
        "scripts/ci/check_structure.py": "scripts/structure/check.py",
    },
}


def _rules(tmp_path: Path, data: object = None) -> Path:
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(_RULES if data is None else data), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Rules file
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ([], "expected a JSON object"),
        ({"rules": {}, "overrides": {}}, "expected a 'rules' list"),
        ({"rules": [1], "overrides": {}}, "rule 0: expected an object"),
        ({"rules": [{"pattern": "x"}], "overrides": {}}, "exactly one of"),
        (
            {
                "rules": [{"pattern": "x", "target": "a", "mirror": "b"}],
                "overrides": {},
            },
            "exactly one of",
        ),
        ({"rules": [{"pattern": "x", "target": 1}], "overrides": {}}, "are strings"),
        ({"rules": [], "overrides": {"a": 1}}, "a: expected a path"),
        ({"rules": [], "overrides": {"a": {"dissolve": 1}}}, "a: expected a path"),
        ({"rules": [], "overrides": {"a": {"move": "b"}}}, "a: expected a path"),
    ],
)
def test_invalid_rules_are_rejected(tmp_path: Path, data: object, message: str) -> None:
    """A malformed rules file raises with the reason."""
    with pytest.raises(ValueError, match=message):
        li.load_rules(_rules(tmp_path, data))


def test_rules_load_in_order_with_overrides(tmp_path: Path) -> None:
    """Rules keep their order; dissolve overrides stay objects."""
    rules = li.load_rules(_rules(tmp_path))
    assert [rule.mirror for rule in rules.rules] == [None, None, "{category}"]
    assert rules.overrides["src/ccnl_engine/payroll/__init__.py"] == {
        "dissolve": "src/ccnl_engine/payroll"
    }


# ---------------------------------------------------------------------------
# Mapping
# ---------------------------------------------------------------------------

_FILES = [
    "src/ccnl_engine/__init__.py",
    "src/ccnl_engine/knowledge/ccnl/data/metal.json",
    "src/ccnl_engine/payroll/__init__.py",
    "src/ccnl_engine/payroll/domain/_ledger.py",
    "src/ccnl_engine/payroll/family/__init__.py",
    "src/ccnl_engine/payroll/family/spouse.py",
    "scripts/ci/check_structure.py",
    "tests/unit/ccnl_engine/__init__.py",
    "tests/unit/ccnl_engine/payroll/__init__.py",
    "tests/unit/ccnl_engine/payroll/domain/test_ledger.py",
    "tests/unit/ccnl_engine/payroll/domain/test_ledger_balance.py",
    "tests/unit/ccnl_engine/payroll/test_family_spouse.py",
    "tests/integration/scripts/ci/test_check_structure_targets.py",
    "tests/unit/ccnl_engine/payroll/domain/helpers.py",
    "tests/unit/ccnl_engine/payroll/domain/test_unknown.py",
    "tests/unit/ccnl_engine/payroll/domain/__init__.py",
    "tests/integration/demo/test_app.py",
    "README.md",
]

#: Paths of :data:`_FILES` that no override, rule or mirror maps.
_UNMAPPED = [
    "README.md",
    "tests/integration/demo/test_app.py",
    "tests/unit/ccnl_engine/payroll/domain/__init__.py",
    "tests/unit/ccnl_engine/payroll/domain/helpers.py",
    "tests/unit/ccnl_engine/payroll/domain/test_unknown.py",
]


def test_build_maps_overrides_rules_and_mirrors(tmp_path: Path) -> None:
    """Every path resolves through an override, a rule or the mirror."""
    mapping, unmapped = li.build(_FILES, li.load_rules(_rules(tmp_path)))
    assert mapping == {
        "scripts/ci/check_structure.py": "scripts/structure/check.py",
        "src/ccnl_engine/__init__.py": "src/ccnl_engine/__init__.py",
        "src/ccnl_engine/knowledge/ccnl/data/metal.json": (
            "src/ccnl_engine/knowledge/contract/agreement/metal.json"
        ),
        "src/ccnl_engine/payroll/__init__.py": {"dissolve": "src/ccnl_engine/payroll"},
        "src/ccnl_engine/payroll/domain/_ledger.py": (
            "src/ccnl_engine/payroll/ledger/models.py"
        ),
        "src/ccnl_engine/payroll/family/__init__.py": {
            "dissolve": "src/ccnl_engine/payroll/family"
        },
        "src/ccnl_engine/payroll/family/spouse.py": (
            "src/ccnl_engine/payroll/family/rules_spouse.py"
        ),
        "tests/integration/scripts/ci/test_check_structure_targets.py": (
            "tests/integration/scripts/structure/test_check_targets.py"
        ),
        "tests/unit/ccnl_engine/__init__.py": {"dissolve": "tests/unit/ccnl_engine"},
        "tests/unit/ccnl_engine/payroll/__init__.py": {
            "dissolve": "tests/unit/ccnl_engine/payroll"
        },
        "tests/unit/ccnl_engine/payroll/domain/test_ledger.py": (
            "tests/unit/ccnl_engine/payroll/ledger/test_models.py"
        ),
        "tests/unit/ccnl_engine/payroll/domain/test_ledger_balance.py": (
            "tests/unit/ccnl_engine/payroll/ledger/test_models_balance.py"
        ),
        "tests/unit/ccnl_engine/payroll/test_family_spouse.py": (
            "tests/unit/ccnl_engine/payroll/family/test_family_spouse.py"
        ),
    }
    assert unmapped == _UNMAPPED


def test_mirror_prefers_the_longest_module_name() -> None:
    """``test_a_b`` mirrors module ``a_b`` before module ``a``."""
    files = [
        "src/ccnl_engine/x/a.py",
        "src/ccnl_engine/x/_a_b.py",
        "tests/unit/ccnl_engine/x/test_a_b_c.py",
    ]
    mapping = {
        "src/ccnl_engine/x/a.py": "src/ccnl_engine/y/rules.py",
        "src/ccnl_engine/x/_a_b.py": "src/ccnl_engine/y/rules_ab.py",
    }
    mirror = li.Mirror("unit", "ccnl_engine", "x/test_a_b_c.py")
    assert mirror.target(mapping, li._children(files)) == (
        "tests/unit/ccnl_engine/y/test_rules_ab_c.py"
    )


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ("elsewhere/rules.py", None),
        ({"dissolve": "elsewhere"}, None),
        ("src/ccnl_engine/rules.py", "tests/unit/ccnl_engine/test_rules.py"),
    ],
)
def test_mirror_outside_the_code_root_is_unmapped(
    entry: object, expected: str | None
) -> None:
    """A module mapped outside its code root cannot be mirrored."""
    files = ["src/ccnl_engine/x/a.py", "tests/unit/ccnl_engine/x/test_a.py"]
    mapping = {"src/ccnl_engine/x/a.py": entry}
    mirror = li.Mirror("unit", "ccnl_engine", "x/test_a.py")
    assert mirror.target(mapping, li._children(files)) == expected


def test_mirror_of_a_marker_outside_the_code_root_is_unmapped() -> None:
    """A test package marker follows its source marker, inside the root only."""
    mapping = {"src/ccnl_engine/x/__init__.py": {"dissolve": "elsewhere"}}
    mirror = li.Mirror("unit", "ccnl_engine", "x/__init__.py")
    assert mirror.target(mapping, {}) is None


def test_unmapped_source_leaves_its_test_unmapped() -> None:
    """A test of a module without a target has no target either."""
    files = ["src/ccnl_engine/x/a.py", "tests/unit/ccnl_engine/x/test_a.py"]
    mirror = li.Mirror("unit", "ccnl_engine", "x/test_a.py")
    assert mirror.target({}, li._children(files)) is None


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_render_and_summary() -> None:
    """The file is indented JSON; the summary counts areas and subdomains."""
    mapping = {
        "a.py": "src/ccnl_engine/payroll/ledger/models.py",
        "b.py": "src/ccnl_engine/payroll/ledger/rules.py",
        "c.py": "src/ccnl_engine/tax/income/models.py",
        "d.py": "tests/conftest.py",
        "e.py": {"dissolve": "src/ccnl_engine"},
    }
    document = json.loads(li.render(mapping))
    assert document["files"] == mapping
    assert li.render(mapping).endswith("}\n")
    assert li.summary(mapping) == [
        "dissolved package markers: 1",
        "src/ccnl_engine/payroll/ledger: 2",
        "src/ccnl_engine/tax: 1",
        "tests: 1",
    ]


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def _git(root: Path, *args: str) -> None:
    """Run git in the throwaway repository at *root*, never in the caller's.

    Inside a git hook ``GIT_DIR`` and ``GIT_INDEX_FILE`` point at the
    repository being committed; :func:`git_environment` drops them.
    """
    subprocess.run(
        [_GIT, *args],
        cwd=root,
        env=li.git_environment(),
        check=True,
        capture_output=True,
    )


def test_git_environment_drops_repository_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hook variables never leak into a git command for another directory."""
    monkeypatch.setenv("GIT_DIR", "/elsewhere/.git")
    monkeypatch.setenv("GIT_INDEX_FILE", "/elsewhere/index")
    monkeypatch.setenv("KEEP_ME", "1")
    environment = li.git_environment()
    assert "GIT_DIR" not in environment
    assert "GIT_INDEX_FILE" not in environment
    assert environment["KEEP_ME"] == "1"


def _repository(root: Path) -> Path:
    """Create a git repository with one mapped package; return its rules.

    Returns:
        The rules file of the repository.
    """
    package = root / "src" / "ccnl_engine"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('"""Root."""\n', encoding="utf-8")
    (root / "src" / "notes.txt").write_text("x\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "add", ".")
    return _rules(
        root,
        {
            "rules": [
                {
                    "pattern": "^src/ccnl_engine/__init__\\.py$",
                    "target": "src/ccnl_engine/__init__.py",
                }
            ],
            "overrides": {"src/notes.txt": "src/ccnl_engine/knowledge/policy/x.json"},
        },
    )


def _main(root: Path, rules: Path, *extra: str) -> int:
    inventory = root / "inventory.json"
    return int(
        li.main([
            "--root",
            str(root),
            "--rules",
            str(rules),
            "--inventory",
            str(inventory),
            *extra,
        ])
    )


def test_write_then_check_passes_and_drift_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A written inventory checks clean; a stale one fails with the command."""
    rules = _repository(tmp_path)
    assert li.tracked_files(tmp_path) == [
        "src/ccnl_engine/__init__.py",
        "src/notes.txt",
    ]
    assert _main(tmp_path, rules, "--check") == 1
    assert "inventory.json is out of date" in capsys.readouterr().err
    assert _main(tmp_path, rules) == 0
    assert _main(tmp_path, rules, "--check") == 0
    assert _main(tmp_path, rules, "--summary") == 0
    assert "src/ccnl_engine/knowledge: 1" in capsys.readouterr().out
    (tmp_path / "inventory.json").write_text("{}\n", encoding="utf-8")
    assert _main(tmp_path, rules, "--check") == 1


def test_unmapped_path_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A tracked file no rule maps fails the check."""
    rules = _repository(tmp_path)
    (tmp_path / "demo").mkdir()
    (tmp_path / "demo" / "app.py").write_text("", encoding="utf-8")
    _git(tmp_path, "add", "demo/app.py")
    assert _main(tmp_path, rules) == 1
    assert "FAIL: demo/app.py: no rule maps it" in capsys.readouterr().err


def test_unreadable_input_exits_with_two(
    tmp_path: Path,
    tmp_path_factory: pytest.TempPathFactory,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Missing rules or a directory outside git is an error."""
    rules = _repository(tmp_path)
    assert _main(tmp_path, tmp_path / "absent.json") == 2
    assert _main(tmp_path_factory.mktemp("plain"), rules) == 2
    assert capsys.readouterr().err.startswith("ERROR:")


def test_repository_inventory_is_complete_and_current(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Every tracked file has a conforming target and the JSON is current."""
    assert li.main(["--check"]) == 0, capsys.readouterr().err
