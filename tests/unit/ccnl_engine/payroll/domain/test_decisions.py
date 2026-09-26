"""Unit tests for calculation status, issues and decisions on results."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.engine.provenance.domain.source import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.payroll.application.calculate_year import (
    YearResult,
    calculate_year,
)
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from tests.helpers import year_input

_FINAL = CalculationStatus.FINAL
_PROVISIONAL = CalculationStatus.PROVISIONAL
_INCOMPLETE = CalculationStatus.INCOMPLETE
_REJECTED = CalculationStatus.REJECTED

_SOURCE = SourceLocation(
    source_document=SourceDocument(
        document_id="dlgs-360-1998",
        title="D.Lgs. 360/1998",
        kind=SourceKind.LEGGE,
    ),
    section="Art. 1",
)


def _issue(
    status: CalculationStatus, code: str = "surtax_table_unknown"
) -> CalculationIssue:
    return CalculationIssue(code=code, message="table not found", status=status)


def _decision(**overrides: Any) -> CalculationDecision:  # noqa: ANN401
    base = CalculationDecision(
        capability="regional_surtax",
        status=_FINAL,
        reason_code="table_found",
        rule="regional_surtax_brackets",
        rule_version="2026",
        inputs={"regione": "ER", "taxable": Decimal("25000.00")},
        amount=Decimal("412.50"),
    )
    return replace(base, **overrides)


@pytest.fixture(scope="module")
def year_result() -> YearResult:
    """Compute the standard year (13 runs) through the real pipeline.

    Returns:
        The year result of a metalmeccanico C3 worker in 2026.
    """
    return calculate_year(year_input(2026, "metalmeccanico-federmeccanica.json", "C3"))


class TestCalculationStatus:
    """Severity order and aggregation of statuses."""

    def test_severity_follows_declaration_order(self) -> None:
        """Final is the least severe status, rejected the most severe."""
        ranks = [s.severity for s in CalculationStatus]
        assert ranks == [0, 1, 2, 3]
        assert list(CalculationStatus) == [
            _FINAL,
            _PROVISIONAL,
            _INCOMPLETE,
            _REJECTED,
        ]

    def test_values_are_stable_strings(self) -> None:
        """Values are the lower-case names callers serialize."""
        assert [s.value for s in CalculationStatus] == [
            "final",
            "provisional",
            "incomplete",
            "rejected",
        ]

    def test_worst_of_nothing_is_final(self) -> None:
        """An empty collection of statuses is final."""
        assert CalculationStatus.worst([]) is _FINAL

    @pytest.mark.parametrize(
        ("statuses", "expected"),
        [
            ((_FINAL,), _FINAL),
            ((_REJECTED, _PROVISIONAL), _REJECTED),
            ((_PROVISIONAL, _INCOMPLETE), _INCOMPLETE),
            ((_FINAL, _PROVISIONAL, _FINAL), _PROVISIONAL),
        ],
    )
    def test_worst_uses_severity_not_alphabetical_order(
        self,
        statuses: tuple[CalculationStatus, ...],
        expected: CalculationStatus,
    ) -> None:
        """Worst picks by severity; alphabetically 'provisional' > 'incomplete'."""
        assert CalculationStatus.worst(iter(statuses)) is expected


class TestCalculationIssue:
    """Validation and immutability of issues."""

    def test_stores_fields(self) -> None:
        """Code, message, status and source are kept as given."""
        issue = CalculationIssue(
            code="surtax_table_unknown",
            message="no table for region ZZ",
            status=_INCOMPLETE,
            source=_SOURCE,
        )
        assert issue.code == "surtax_table_unknown"
        assert issue.status is _INCOMPLETE
        assert issue.source == _SOURCE

    def test_source_defaults_to_none(self) -> None:
        """An issue without a normative source is allowed."""
        assert _issue(_PROVISIONAL).source is None

    @pytest.mark.parametrize("code", ["", "Unknown", "unknown-table", "1st", "a b"])
    def test_rejects_non_snake_case_code(self, code: str) -> None:
        """Codes must be lower snake case to stay machine-readable."""
        with pytest.raises(ValueError, match="lower snake case"):
            _issue(_INCOMPLETE, code=code)

    def test_rejects_empty_message(self) -> None:
        """An issue must explain itself."""
        with pytest.raises(ValueError, match="message must not be empty"):
            CalculationIssue(code="x", message="", status=_INCOMPLETE)

    def test_is_frozen(self) -> None:
        """Issues cannot be mutated after construction."""
        issue = _issue(_INCOMPLETE)
        with pytest.raises(FrozenInstanceError):
            issue.code = "other"  # type: ignore[misc]


class TestCalculationDecision:
    """Validation and immutability of decisions."""

    def test_stores_fields(self) -> None:
        """All fields are kept, inputs as a read-only mapping."""
        decision = _decision(source=_SOURCE)
        assert decision.capability == "regional_surtax"
        assert decision.reason_code == "table_found"
        assert decision.inputs == {"regione": "ER", "taxable": Decimal("25000.00")}
        assert decision.rule_version == "2026"
        assert decision.amount == Decimal("412.50")
        assert decision.source == _SOURCE

    def test_defaults(self) -> None:
        """Inputs default to empty; source and amount to None."""
        decision = CalculationDecision(
            capability="regional_surtax",
            status=_INCOMPLETE,
            reason_code="table_unknown",
            rule="regional_surtax_brackets",
            rule_version="2026",
        )
        assert decision.inputs == {}
        assert decision.source is None
        assert decision.amount is None

    def test_inputs_are_frozen(self) -> None:
        """The inputs mapping cannot be mutated in place."""
        decision = _decision()
        with pytest.raises(TypeError):
            decision.inputs["regione"] = "ZZ"  # type: ignore[index]

    def test_inputs_are_copied(self) -> None:
        """Mutating the caller's mapping does not change the decision."""
        inputs: dict[str, Decimal | str] = {"regione": "ER"}
        decision = _decision(inputs=inputs)
        inputs["regione"] = "ZZ"
        assert decision.inputs == {"regione": "ER"}

    def test_rejects_non_snake_case_reason_code(self) -> None:
        """Reason codes must be lower snake case."""
        with pytest.raises(ValueError, match="reason_code"):
            _decision(reason_code="Table Found")

    @pytest.mark.parametrize("field", ["capability", "rule", "rule_version"])
    def test_rejects_empty_identifiers(self, field: str) -> None:
        """Capability, rule and rule version are required and non-empty."""
        with pytest.raises(ValueError, match=f"{field} must not be empty"):
            _decision(**{field: ""})

    @pytest.mark.parametrize("amount", ["NaN", "Infinity"])
    def test_rejects_non_finite_amount(self, amount: str) -> None:
        """Amounts must be finite."""
        with pytest.raises(ValueError, match="amount must be finite"):
            _decision(amount=Decimal(amount))

    def test_is_frozen(self) -> None:
        """Decisions cannot be mutated after construction."""
        decision = _decision()
        with pytest.raises(FrozenInstanceError):
            decision.amount = Decimal(0)  # type: ignore[misc]


class TestPeriodResultStatus:
    """Status of a period result is derived from its issues."""

    def test_computed_result_is_final_without_issues(
        self, year_result: YearResult
    ) -> None:
        """No capability raises issues yet: every result is final."""
        period = year_result.period_results[0]
        assert period.issues == ()
        assert period.status is _FINAL

    def test_status_is_worst_issue_status(self, year_result: YearResult) -> None:
        """The period status is the most severe status among its issues."""
        period = replace(
            year_result.period_results[0],
            issues=(_issue(_PROVISIONAL), _issue(_INCOMPLETE), _issue(_PROVISIONAL)),
        )
        assert period.status is _INCOMPLETE


class TestYearResultStatus:
    """Status and issues of a year result aggregate its periods."""

    def test_computed_year_is_final_without_issues(
        self, year_result: YearResult
    ) -> None:
        """A year of issue-free periods is final."""
        assert year_result.issues == ()
        assert year_result.status is _FINAL

    def test_empty_year_is_final(self, year_result: YearResult) -> None:
        """A year without periods has no issues and is final."""
        empty = replace(year_result, period_results=())
        assert empty.issues == ()
        assert empty.status is _FINAL

    def test_status_is_worst_period_status(self, year_result: YearResult) -> None:
        """The year status is the worst period status; issues keep run order."""
        first_run, *middle_runs, last_run = year_result.period_results
        first = _issue(_PROVISIONAL, code="first")
        second = _issue(_REJECTED, code="second")
        third = _issue(_INCOMPLETE, code="third")
        year = replace(
            year_result,
            period_results=(
                replace(first_run, issues=(first,)),
                *middle_runs,
                replace(last_run, issues=(second, third)),
            ),
        )
        assert year.status is _REJECTED
        assert year.issues == (first, second, third)


def test_year_issues_are_listed_once(year_result: YearResult) -> None:
    """An issue repeated on every run is listed once, at its first run.

    The same code with another message is a different issue and is kept.
    """
    first_run, second_run, *rest = year_result.period_results
    repeated = _issue(_PROVISIONAL, code="repeated")
    other = CalculationIssue(
        code="repeated", message="another message", status=_PROVISIONAL
    )
    year = replace(
        year_result,
        period_results=(
            replace(first_run, issues=(repeated,)),
            replace(second_run, issues=(repeated, other)),
            *(replace(r, issues=(repeated,)) for r in rest),
        ),
    )
    assert year.issues == (repeated, other)
