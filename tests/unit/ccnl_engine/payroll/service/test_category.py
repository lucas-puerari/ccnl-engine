"""Worker category resolution against CCNL levels and seniority rules."""

from __future__ import annotations

import pytest

from ccnl_engine.contract.domain.category import (
    WorkerCategory,
    parse_worker_category,
)
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.payroll.domain.employment_facts import SeniorityMonths
from ccnl_engine.payroll.service.category import resolve_worker_category
from ccnl_engine.shared.domain.errors import InvalidInputError

_FISE = load_ccnl("servizi-postali-appalto-fise.json")
_COMMERCIO = load_ccnl("commercio-confcommercio.json")
_SIXTY_MONTHS = SeniorityMonths(60)


class TestParseWorkerCategory:
    """String values are normalized; unknown values are rejected."""

    def test_none_stays_none(self) -> None:
        """No category stays absent."""
        assert parse_worker_category(None) is None

    def test_string_value_becomes_member(self) -> None:
        """The lowercase string value maps to its member."""
        assert parse_worker_category("impiegato") is WorkerCategory.IMPIEGATO

    def test_unknown_value_raises(self) -> None:
        """A value outside the enum is rejected."""
        with pytest.raises(InvalidInputError, match="unknown worker category"):
            parse_worker_category("manager")


class TestRequiresCategory:
    """A level needs a category when its increments exist only per category."""

    def test_fise_levels_require_category(self) -> None:
        """Every FISE level has increments only per category."""
        si = _FISE.parameters.seniority_increments
        assert all(si.requires_category(level.code) for level in _FISE.levels)

    def test_level_without_category_amounts_does_not(self) -> None:
        """Commercio increments do not depend on the category."""
        si = _COMMERCIO.parameters.seniority_increments
        assert not si.requires_category("4")


class TestResolveWorkerCategory:
    """Declared category, level category and seniority rules combine here."""

    def test_declared_category_is_used_on_open_level(self) -> None:
        """A level open to several categories uses the declared one."""
        level = _FISE.level_by_code("2")
        resolved = resolve_worker_category(
            _FISE, level, WorkerCategory.IMPIEGATO, seniority=_SIXTY_MONTHS
        )
        assert resolved is WorkerCategory.IMPIEGATO

    def test_missing_category_rejected_when_seniority_needs_it(self) -> None:
        """FISE increments cannot be priced without a category."""
        level = _FISE.level_by_code("2")
        with pytest.raises(InvalidInputError, match="worker category is required"):
            resolve_worker_category(_FISE, level, None, seniority=_SIXTY_MONTHS)

    def test_missing_category_accepted_without_seniority(self) -> None:
        """Without months of service no increment needs a category."""
        level = _FISE.level_by_code("2")
        assert resolve_worker_category(_FISE, level, None, seniority=None) is None

    def test_missing_category_accepted_when_seniority_ignores_it(self) -> None:
        """Category-independent increments need no category."""
        level = _COMMERCIO.level_by_code("4")
        resolved = resolve_worker_category(
            _COMMERCIO, level, None, seniority=_SIXTY_MONTHS
        )
        assert resolved is None

    def test_level_fixes_category_when_none_declared(self) -> None:
        """A single-category level supplies its category."""
        level = _COMMERCIO.level_by_code("Q")
        resolved = resolve_worker_category(_COMMERCIO, level, None, seniority=None)
        assert resolved is WorkerCategory.QUADRO

    def test_declared_category_matching_level_is_accepted(self) -> None:
        """Declaring the level category is accepted."""
        level = _COMMERCIO.level_by_code("Q")
        resolved = resolve_worker_category(_COMMERCIO, level, "quadro", seniority=None)
        assert resolved is WorkerCategory.QUADRO

    def test_declared_category_conflicting_with_level_raises(self) -> None:
        """A category the level does not admit is rejected."""
        level = _COMMERCIO.level_by_code("Q")
        with pytest.raises(InvalidInputError, match="not admitted by level 'Q'"):
            resolve_worker_category(
                _COMMERCIO, level, WorkerCategory.IMPIEGATO, seniority=None
            )
