"""Naming rules: directory = domain of the glossary, file = technical role."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.structure.naming.rules import (
    Vocabulary,
    directory_offends,
    file_offends,
    vocabulary,
)

_GLOSSARY = """# Glossary

## Terms

`ignored` is a term, not a directory.

## Directory names

**Concepts** (roots): `sickness`,
`contribution`.

**Subdomains**: `indemnity`, `rate`.

## Anti-patterns

`also_ignored`.
"""
_WORDS = Vocabulary(
    concepts=frozenset({"sickness", "contribution"}),
    names=frozenset({"sickness", "contribution", "indemnity", "rate"}),
)


def test_vocabulary_reads_the_directory_names_section(tmp_path: Path) -> None:
    """Only the section's names count; the Concepts paragraph is apart."""
    glossary = tmp_path / "docs" / "domain" / "glossary.md"
    glossary.parent.mkdir(parents=True)
    glossary.write_text(_GLOSSARY, encoding="utf-8")
    assert vocabulary(tmp_path) == _WORDS


def test_vocabulary_without_glossary_is_empty(tmp_path: Path) -> None:
    """A tree without a glossary admits no domain name."""
    assert vocabulary(tmp_path) == Vocabulary(frozenset(), frozenset())


@pytest.mark.parametrize(
    "path",
    [
        "src/ccnl_engine/__init__.py",
        "src/ccnl_engine/api.py",
        "src/ccnl_engine/types.py",
        "src/ccnl_engine/sickness/models.py",
        "src/ccnl_engine/sickness/indemnity/loaders.py",
        "src/ccnl_engine/sickness/__init__.py",
        "tests/conftest.py",
        "tests/unit/ccnl_engine/sickness/builders.py",
        "tests/unit/ccnl_engine/sickness/test_rules.py",
        "tests/integration/ccnl_engine/test_api.py",
        "tests/integration/scripts/structure/test_check.py",
        "tests/integration/demo/test_app.py",
        "scripts/structure/check.py",
        "scripts/provenance/rules.py",
        "demo/app.py",
    ],
)
def test_role_names_are_accepted(path: str) -> None:
    """Roles, root modules, tests of them, helpers, actions and the demo."""
    assert not file_offends(Path(path))


@pytest.mark.parametrize(
    "path",
    [
        "src/ccnl_engine/catalog.py",
        "src/ccnl_engine/sickness/api.py",
        "src/ccnl_engine/sickness/rules_day.py",
        "src/ccnl_engine/sickness/day_rules.py",
        "tests/unit/ccnl_engine/sickness/test_rules_day.py",
        "tests/unit/ccnl_engine/sickness/builders_day.py",
        "tests/unit/ccnl_engine/sickness/rules.py",
        "tests/integration/ccnl_engine/test_engine_modes.py",
        "scripts/documentation/generate_trust_counts.py",
        "scripts/quality/smoke_test.py",
        "demo/ui.py",
    ],
)
def test_mixed_and_descriptive_names_offend(path: str) -> None:
    """A suffix, a prefix or a name outside the roles offends."""
    assert file_offends(Path(path))


@pytest.mark.parametrize(
    ("path", "offends"),
    [
        ("src/ccnl_engine/sickness", False),
        ("src/ccnl_engine/indemnity", True),
        ("tests/unit/ccnl_engine/contribution", False),
        ("tests/unit/ccnl_engine/rate", True),
        ("src/ccnl_engine/sickness/indemnity", False),
        ("src/ccnl_engine/sickness/contribution", False),
        ("src/ccnl_engine/sickness/day", True),
        ("tests/unit/ccnl_engine", False),
        ("tests/integration", False),
        ("scripts/structure", True),
    ],
)
def test_directories_are_named_after_domains(path: str, offends: bool) -> None:
    """Below the package root a concept; deeper any admitted name or root."""
    assert directory_offends(Path(path), _WORDS) is offends
