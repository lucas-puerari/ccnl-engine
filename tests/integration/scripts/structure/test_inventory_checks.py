"""Tests for the contract checks of layout_inventory.py.

Each check rejects one way a target can break the architecture contract:
a duplicate, an underscore basename, a technical directory, the depth, the
role names, the trees and the dissolved package markers.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import types

_SCRIPT = Path(__file__).resolve().parents[4] / "scripts" / "structure" / "inventory.py"
_MODULE = "_ci_layout_inventory"


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

#: Code trees the test targets below may mirror.
_TREES = {
    "ccnl_engine": {"", "payroll", "payroll/ledger"},
    "demo": {""},
    "scripts": {"", "structure"},
}


@pytest.mark.parametrize(
    "target",
    [
        "src/ccnl_engine/__init__.py",
        "src/ccnl_engine/py.typed",
        "src/ccnl_engine/api.py",
        "src/ccnl_engine/validation_collection.py",
        "src/ccnl_engine/payroll/ledger/models.py",
        "src/ccnl_engine/payroll/ledger/services_base_line.py",
        "src/ccnl_engine/knowledge/social_security/contribution/2026/industria.json",
        "src/ccnl_engine/payroll/ledger/__init__.py",
        "tests/conftest.py",
        "tests/README.md",
        "tests/unit/ccnl_engine/payroll/ledger/test_models.py",
        "tests/unit/ccnl_engine/builders.py",
        "tests/knowledge/ccnl_engine/payroll/oracles_irpef_2026.py",
        "tests/integration/scripts/structure/support_imports.py",
        "tests/knowledge/ccnl_engine/payroll/ledger/payslip/p01.json",
        "tests/knowledge/ccnl_engine/payroll/ledger/notes.md",
        "scripts/structure/check.py",
        "demo/app.py",
        "demo/localization/en.json",
    ],
)
def test_conforming_targets_pass(target: str) -> None:
    """Targets that follow the contract raise no problem."""
    assert li.target_problems(target, _TREES) == []


@pytest.mark.parametrize(
    ("target", "reason"),
    [
        ("src/ccnl_engine/payroll/_ledger.py", "basename starts with an underscore"),
        (
            "tests/unit/ccnl_engine/payroll/ledger/__init__.py",
            "basename starts with an underscore",
        ),
        ("src/ccnl_engine/payroll/domain/models.py", "technical directory 'domain'"),
        ("src/ccnl_engine/a/b/c/d/models.py", "4 directories under the package"),
        ("src/ccnl_engine/payroll/misc/models.py", "not in the target tree"),
        ("src/ccnl_engine/payroll/ledger/ledger.py", "name is not a technical role"),
        ("src/ccnl_engine/helpers.py", "name is not a technical role"),
        ("src/ccnl_engine/payroll/table.json", "resource outside a knowledge"),
        ("src/ccnl_engine/knowledge/x.json", "resource outside a knowledge"),
        ("src/ccnl_engine/knowledge/misc/x.json", "resource outside a knowledge"),
        ("src/ccnl_engine/notes.txt", "unexpected file type"),
        ("src/other/models.py", "outside src/ccnl_engine"),
        ("tests/helpers.py", "file at the top of tests"),
        ("tests/acceptance/ccnl_engine/test_a.py", "category 'acceptance'"),
        ("tests/unit/test_a.py", "mirror root not in"),
        ("tests/unit/other/test_a.py", "mirror root not in"),
        ("tests/unit/ccnl_engine/a/b/c/d/test_a.py", "6 directories under tests"),
        ("tests/unit/ccnl_engine/payroll/misc/test_a.py", "mirrors no code directory"),
        ("tests/unit/ccnl_engine/payroll/helpers.py", "not a test, conftest"),
        ("tests/unit/ccnl_engine/misc/case/a.json", "sits under no code directory"),
        ("scripts/check.py", "script outside an operational domain"),
        ("scripts/ci/check.py", "directory 'ci' not in"),
        ("scripts/structure/deep/check.py", "more than one directory level"),
        ("demo/i18n/en.json", "directory 'i18n' not in"),
        ("docs/index.md", "root 'docs' not in"),
    ],
)
def test_broken_targets_report_the_reason(target: str, reason: str) -> None:
    """Each broken rule is named in the problems of the target."""
    problems = li.target_problems(target, _TREES)
    assert any(reason in problem for problem in problems), problems


def test_duplicate_targets_fail(tmp_path: Path) -> None:
    """Two paths cannot land on the same target."""
    mapping = {
        "a.py": "scripts/structure/check.py",
        "b.py": "scripts/structure/check.py",
    }
    assert li.check_mapping(mapping, tmp_path) == [
        "scripts/structure/check.py: target of 2 paths"
    ]


def _marker(root: Path, rel: str, text: str) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


def test_dissolve_rules(tmp_path: Path) -> None:
    """Only a code-free marker dissolves, into a directory of the target tree."""
    target = "src/ccnl_engine/payroll/ledger/models.py"
    empty = _marker(tmp_path, "a/__init__.py", '"""Doc."""\n')
    future = _marker(tmp_path, "b/__init__.py", "from __future__ import annotations\n")
    code = _marker(tmp_path, "c/__init__.py", "from x import y\n")
    module = _marker(tmp_path, "d/models.py", '"""Doc."""\n')
    stray = _marker(tmp_path, "e/__init__.py", "")
    mapping = {
        "f.py": target,
        empty: {"dissolve": "src/ccnl_engine/payroll"},
        future: {"dissolve": "src/ccnl_engine/payroll/ledger"},
        code: {"dissolve": "src/ccnl_engine"},
        module: {"dissolve": "src/ccnl_engine"},
        stray: {"dissolve": "src/ccnl_engine/payroll/misc"},
    }
    assert li.check_mapping(mapping, tmp_path) == [
        "c/__init__.py: holds code: give it a file target",
        "d/models.py: only a package marker can dissolve",
        (
            "e/__init__.py: dissolves into 'src/ccnl_engine/payroll/misc', "
            "not a target dir"
        ),
    ]


def test_code_free_reads_docstrings_and_future_imports() -> None:
    """Strings and ``from __future__`` are not code; anything else is."""
    assert li.code_free('"""Doc."""\n"""More."""\n')
    assert li.code_free("")
    assert not li.code_free("import os\n")
    assert not li.code_free("from os import path\n")
    assert not li.code_free("X = 1\n")


def test_test_targets_mirror_the_target_code_tree(tmp_path: Path) -> None:
    """A test directory must exist in the target tree of the code it mirrors."""
    mapping = {
        "a.py": "src/ccnl_engine/payroll/ledger/models.py",
        "b.py": "tests/unit/ccnl_engine/payroll/ledger/test_models.py",
        "c.py": "tests/unit/ccnl_engine/payroll/period/test_models.py",
    }
    assert li.check_mapping(mapping, tmp_path) == [
        "c.py: directory 'payroll/period' mirrors no code directory"
    ]
