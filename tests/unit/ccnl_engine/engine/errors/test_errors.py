"""Tests for the ccnl-engine structured error hierarchy."""

from __future__ import annotations

import pytest

from ccnl_engine.engine.errors import (
    CcnlEngineError,
    UnknownCcnlError,
    UnknownLevelError,
)


class TestCcnlEngineError:
    """CcnlEngineError is the base exception class."""

    def test_is_exception(self) -> None:
        """CcnlEngineError subclasses Exception."""
        assert issubclass(CcnlEngineError, Exception)

    def test_can_raise(self) -> None:
        """CcnlEngineError can be raised and caught.

        Raises:
            CcnlEngineError: deliberately, to verify it propagates.
        """
        msg = "base error"
        with pytest.raises(CcnlEngineError):
            raise CcnlEngineError(msg)


class TestUnknownCcnlError:
    """UnknownCcnlError reports an unresolvable CCNL identifier."""

    def test_is_ccnl_engine_error(self) -> None:
        """UnknownCcnlError is a CcnlEngineError."""
        assert issubclass(UnknownCcnlError, CcnlEngineError)

    def test_stores_ccnl_id(self) -> None:
        """ccnl_id attribute holds the rejected identifier."""
        err = UnknownCcnlError("bad-id")
        assert err.ccnl_id == "bad-id"

    def test_no_suggestions(self) -> None:
        """Message omits the Did-you-mean clause when no suggestions given."""
        err = UnknownCcnlError("bad-id")
        assert err.suggestions == ()
        assert "bad-id" in str(err)
        assert "Did you mean" not in str(err)

    def test_with_suggestions(self) -> None:
        """Message includes suggestions when provided."""
        err = UnknownCcnlError("metal", ("metalmeccanico", "metallurgico"))
        assert "Did you mean" in str(err)
        assert "metalmeccanico" in str(err)

    def test_suggestions_capped_at_three(self) -> None:
        """Message shows at most three suggestions regardless of tuple length."""
        suggestions = ("a", "b", "c", "d", "e")
        err = UnknownCcnlError("x", suggestions)
        assert err.suggestions == suggestions
        msg = str(err)
        assert "'d'" not in msg
        assert "'e'" not in msg


class TestUnknownLevelError:
    """UnknownLevelError reports a missing level code within a CCNL."""

    def test_is_ccnl_engine_error(self) -> None:
        """UnknownLevelError is a CcnlEngineError."""
        assert issubclass(UnknownLevelError, CcnlEngineError)

    def test_stores_fields(self) -> None:
        """level_code and ccnl_id attributes are stored."""
        err = UnknownLevelError("Q1", "metalmeccanico-federmeccanica")
        assert err.level_code == "Q1"
        assert err.ccnl_id == "metalmeccanico-federmeccanica"

    def test_message(self) -> None:
        """Both level_code and ccnl_id appear in the error message."""
        err = UnknownLevelError("Q1", "metalmeccanico-federmeccanica")
        assert "Q1" in str(err)
        assert "metalmeccanico-federmeccanica" in str(err)
