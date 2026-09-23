"""Tests for the ccnl-engine structured error hierarchy."""

from __future__ import annotations

import pytest

from ccnl_engine.engine.errors import (
    PUBLIC_ERROR_CODES,
    CcnlEngineError,
    DataIntegrityError,
    InvalidInputError,
    OutOfScopeError,
    UnknownCcnlError,
    UnknownLevelError,
)


class TestCcnlEngineError:
    """CcnlEngineError is the base exception class."""

    def test_is_exception(self) -> None:
        """CcnlEngineError subclasses Exception."""
        assert issubclass(CcnlEngineError, Exception)

    def test_structured_fields(self) -> None:
        """All structured fields are stored as attributes."""
        err = CcnlEngineError(
            "test",
            code="test_code",
            feature="payroll",
            ruleset="metalmeccanico",
            remediation="fix it",
            result_usable=True,
        )
        assert err.code == "test_code"
        assert err.feature == "payroll"
        assert err.ruleset == "metalmeccanico"
        assert err.remediation == "fix it"
        assert err.result_usable is True

    def test_defaults_to_non_usable_result(self) -> None:
        """result_usable defaults to False."""
        err = CcnlEngineError("test", code="x")
        assert err.result_usable is False
        assert err.feature is None
        assert err.ruleset is None
        assert err.remediation is None


class TestUnknownCcnlError:
    """UnknownCcnlError reports an unresolvable CCNL identifier."""

    def test_is_ccnl_engine_error(self) -> None:
        """UnknownCcnlError is a CcnlEngineError."""
        assert issubclass(UnknownCcnlError, CcnlEngineError)

    def test_stores_ccnl_id(self) -> None:
        """ccnl_id attribute holds the rejected identifier."""
        err = UnknownCcnlError("bad-id")
        assert err.ccnl_id == "bad-id"

    def test_code_is_unknown_ccnl(self) -> None:
        """Code is 'unknown_ccnl'."""
        err = UnknownCcnlError("bad-id")
        assert err.code == "unknown_ccnl"

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

    def test_code_is_unknown_level(self) -> None:
        """Code is 'unknown_level'."""
        err = UnknownLevelError("Q1", "metalmeccanico")
        assert err.code == "unknown_level"

    def test_ruleset_set_to_ccnl_id(self) -> None:
        """Ruleset attribute is set to the ccnl_id for context."""
        err = UnknownLevelError("Q1", "metalmeccanico")
        assert err.ruleset == "metalmeccanico"

    def test_message(self) -> None:
        """Both level_code and ccnl_id appear in the error message."""
        err = UnknownLevelError("Q1", "metalmeccanico-federmeccanica")
        assert "Q1" in str(err)
        assert "metalmeccanico-federmeccanica" in str(err)


class TestOutOfScopeError:
    """OutOfScopeError signals that a computation is outside CCNL scope."""

    def test_is_ccnl_engine_error(self) -> None:
        """OutOfScopeError is a CcnlEngineError."""
        assert issubclass(OutOfScopeError, CcnlEngineError)

    def test_is_not_value_error(self) -> None:
        """OutOfScopeError does not subclass ValueError."""
        assert not issubclass(OutOfScopeError, ValueError)

    def test_stores_reason_and_feature(self) -> None:
        """reason, feature, ruleset are stored; code is always 'out_of_scope'."""
        err = OutOfScopeError(
            "no track found",
            reason="no_track",
            feature="apprenticeship",
            ruleset="metalmeccanico",
        )
        assert err.code == "out_of_scope"
        assert err.reason == "no_track"
        assert err.feature == "apprenticeship"
        assert err.ruleset == "metalmeccanico"
        assert err.result_usable is False

    def test_no_reason_defaults_to_none(self) -> None:
        """Reason defaults to None when not supplied."""
        err = OutOfScopeError("out of scope")
        assert err.code == "out_of_scope"
        assert err.reason is None

    def test_no_track_reason(self) -> None:
        """reason='no_track' is storable and retrievable.

        Raises:
            OutOfScopeError: always (this is the point of the test).
        """
        msg = "no track"
        with pytest.raises(OutOfScopeError) as exc_info:
            raise OutOfScopeError(msg, reason="no_track", feature="apprenticeship")
        assert exc_info.value.reason == "no_track"
        assert exc_info.value.code == "out_of_scope"

    def test_ambiguous_track_reason(self) -> None:
        """reason='ambiguous_track' is storable.

        Raises:
            OutOfScopeError: always (this is the point of the test).
        """
        msg = "ambiguous"
        with pytest.raises(OutOfScopeError) as exc_info:
            raise OutOfScopeError(
                msg, reason="ambiguous_track", feature="apprenticeship"
            )
        assert exc_info.value.reason == "ambiguous_track"

    def test_no_period_reason(self) -> None:
        """reason='no_period' is storable.

        Raises:
            OutOfScopeError: always (this is the point of the test).
        """
        msg = "no period"
        with pytest.raises(OutOfScopeError) as exc_info:
            raise OutOfScopeError(msg, reason="no_period", feature="apprenticeship")
        assert exc_info.value.reason == "no_period"


class TestDataIntegrityError:
    """DataIntegrityError signals corrupted or inconsistent knowledge-base data."""

    def test_is_ccnl_engine_error(self) -> None:
        """DataIntegrityError is a CcnlEngineError."""
        assert issubclass(DataIntegrityError, CcnlEngineError)

    def test_is_not_value_error(self) -> None:
        """DataIntegrityError does not subclass ValueError."""
        assert not issubclass(DataIntegrityError, ValueError)

    def test_code_is_data_integrity(self) -> None:
        """Code is always 'data_integrity'."""
        err = DataIntegrityError("hash mismatch")
        assert err.code == "data_integrity"

    def test_can_raise(self) -> None:
        """DataIntegrityError can be raised and caught as CcnlEngineError.

        Raises:
            DataIntegrityError: always (this is the point of the test).
        """
        msg = "mismatch"
        with pytest.raises(CcnlEngineError):
            raise DataIntegrityError(msg)

    def test_stores_remediation(self) -> None:
        """Remediation attribute is stored when provided."""
        err = DataIntegrityError("mismatch", remediation="rerun rehash script")
        assert err.remediation == "rerun rehash script"


class TestInvalidInputError:
    """InvalidInputError signals invalid caller-supplied inputs."""

    def test_is_ccnl_engine_error(self) -> None:
        """InvalidInputError is a CcnlEngineError."""
        assert issubclass(InvalidInputError, CcnlEngineError)

    def test_is_value_error(self) -> None:
        """InvalidInputError is a ValueError for backward compatibility."""
        assert issubclass(InvalidInputError, ValueError)

    def test_code_is_invalid_input(self) -> None:
        """Code is always 'invalid_input'."""
        err = InvalidInputError("bad date range")
        assert err.code == "invalid_input"

    def test_caught_as_value_error(self) -> None:
        """Raising InvalidInputError is caught by except ValueError.

        Raises:
            InvalidInputError: always (this is the point of the test).
        """
        msg = "bad input"
        with pytest.raises(ValueError, match="bad input"):
            raise InvalidInputError(msg)

    def test_stores_feature_and_remediation(self) -> None:
        """Feature and remediation are stored when provided."""
        err = InvalidInputError("bad", feature="payroll", remediation="check inputs")
        assert err.feature == "payroll"
        assert err.remediation == "check inputs"


class TestPublicErrorCodes:
    """PUBLIC_ERROR_CODES is a stable contract."""

    _EXPECTED: frozenset[str] = frozenset({
        "unknown_ccnl",
        "unknown_level",
        "out_of_scope",
        "data_integrity",
        "invalid_input",
        "missing_required_fact",
    })

    def test_exact_set(self) -> None:
        """PUBLIC_ERROR_CODES matches the declared expected set exactly."""
        assert PUBLIC_ERROR_CODES == self._EXPECTED

    def test_is_frozenset(self) -> None:
        """PUBLIC_ERROR_CODES is immutable."""
        assert isinstance(PUBLIC_ERROR_CODES, frozenset)

    def test_known_classes_use_public_codes(self) -> None:
        """All structured error classes use codes from PUBLIC_ERROR_CODES."""
        instances = [
            UnknownCcnlError("x"),
            UnknownLevelError("L1", "ccnl/x"),
            OutOfScopeError("x"),
            DataIntegrityError("x"),
            InvalidInputError("x"),
        ]
        for err in instances:
            assert err.code in PUBLIC_ERROR_CODES, (
                f"{type(err).__name__}.code={err.code!r} not in PUBLIC_ERROR_CODES"
            )
