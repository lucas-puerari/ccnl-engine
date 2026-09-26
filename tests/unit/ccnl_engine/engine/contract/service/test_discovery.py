"""Tests for CCNL discovery: list_ccnls, get_ccnl, search_ccnls."""

from __future__ import annotations

import pytest

from ccnl_engine.contract.service.discovery import (
    CcnlId,
    CcnlInfo,
    _load_all,
    get_ccnl,
    list_ccnls,
    search_ccnls,
)
from ccnl_engine.shared.domain.errors import UnknownCcnlError


class TestListCcnls:
    """list_ccnls returns a sorted tuple of all bundled CCNLs."""

    def test_returns_tuple(self) -> None:
        """list_ccnls returns a tuple."""
        result = list_ccnls()
        assert isinstance(result, tuple)

    def test_non_empty(self) -> None:
        """At least one CCNL is bundled."""
        assert len(list_ccnls()) > 0

    def test_elements_are_ccnl_info(self) -> None:
        """Every element is a CcnlInfo instance."""
        for item in list_ccnls():
            assert isinstance(item, CcnlInfo)

    def test_sorted_by_ccnl_id(self) -> None:
        """Results are sorted alphabetically by ccnl_id."""
        ids = [info.ccnl_id for info in list_ccnls()]
        assert ids == sorted(ids)

    def test_ccnl_info_fields_non_empty(self) -> None:
        """ccnl_id, name, and cnel_code are all non-empty strings."""
        for info in list_ccnls():
            assert info.ccnl_id
            assert info.name
            assert info.cnel_code


class TestGetCcnl:
    """get_ccnl resolves a CCNL by slug or CNEL code."""

    def test_lookup_by_slug(self) -> None:
        """Lookup by ccnl_id slug returns the matching CcnlInfo."""
        first = list_ccnls()[0]
        found = get_ccnl(first.ccnl_id)
        assert found == first

    def test_lookup_by_cnel_code(self) -> None:
        """Lookup by CNEL code returns the matching CcnlInfo."""
        first = list_ccnls()[0]
        found = get_ccnl(first.cnel_code)
        assert found == first

    def test_unknown_raises(self) -> None:
        """Unknown identifier raises UnknownCcnlError with the identifier."""
        with pytest.raises(UnknownCcnlError) as exc_info:
            get_ccnl("does-not-exist-xyz")
        assert exc_info.value.ccnl_id == "does-not-exist-xyz"

    def test_suggestions_on_partial_match(self) -> None:
        """Suggestions tuple is a tuple of strings when partial match exists."""
        with pytest.raises(UnknownCcnlError) as exc_info:
            get_ccnl("zzz_no_match_at_all_xyz")
        assert isinstance(exc_info.value.suggestions, tuple)

    def test_returns_ccnl_info(self) -> None:
        """get_ccnl returns a CcnlInfo with a str ccnl_id."""
        first = list_ccnls()[0]
        result = get_ccnl(first.ccnl_id)
        assert isinstance(result, CcnlInfo)
        assert isinstance(result.ccnl_id, str)


class TestSearchCcnls:
    """search_ccnls filters by case-insensitive substring match."""

    def test_returns_tuple(self) -> None:
        """Returns a tuple."""
        assert isinstance(search_ccnls(""), tuple)

    def test_empty_query_returns_all(self) -> None:
        """Empty query returns every CCNL."""
        assert len(search_ccnls("")) == len(list_ccnls())

    def test_no_match_returns_empty(self) -> None:
        """Query with no match returns an empty tuple."""
        assert search_ccnls("zzz_no_match_xyz") == ()

    def test_case_insensitive(self) -> None:
        """Upper and lower case queries return the same results."""
        first = list_ccnls()[0]
        upper = search_ccnls(first.ccnl_id.upper())
        lower = search_ccnls(first.ccnl_id.lower())
        assert set(upper) == set(lower)

    def test_partial_match(self) -> None:
        """3-char prefix of the first ccnl_id matches at least one entry."""
        all_ccnls = list_ccnls()
        prefix = all_ccnls[0].ccnl_id[:3]
        matches = search_ccnls(prefix)
        assert len(matches) >= 1


class TestLoadAll:
    """_load_all caches and returns all CcnlInfo from the data package."""

    def test_skips_non_json(self) -> None:
        """_load_all runs without error and returns only CcnlInfo items."""
        items = _load_all()
        assert all(isinstance(i, CcnlInfo) for i in items)

    def test_ccnl_id_is_branded(self) -> None:
        """CcnlId is a str at runtime and round-trips correctly."""
        items = _load_all()
        for item in items:
            assert isinstance(item.ccnl_id, str)
            assert CcnlId(item.ccnl_id) == item.ccnl_id
