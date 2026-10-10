"""The renewal regime on the minimo, against the bundled 2026 regime.

L. 199/2025 art. 1 c. 7 (Gazzetta Ufficiale, serie generale, 21 January
2026): "gli incrementi retributivi corrisposti ai lavoratori dipendenti
nell'anno 2026, in attuazione di rinnovi contrattuali sottoscritti dal 1°
gennaio 2024 al 31 dicembre 2026, sono assoggettati, salva espressa rinuncia
scritta del prestatore di lavoro, a un'imposta sostitutiva [...] pari al 5
per cento [...] soltanto ai lavoratori del settore privato con un reddito di
lavoro dipendente, nell'anno 2025, non superiore a 33.000 euro."
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.identity.rules_validity import (
    SalaryGapKind,
    TimeSeries,
    ValidityPeriod,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.service.regime_requirements import RegimeFacts
from ccnl_engine.payroll.service.renewal_minimum import (
    INCREMENT_UNQUANTIFIED,
    RenewalMinimum,
    assess_renewal_minimum,
    renewal_table_from,
)
from ccnl_engine.tax.annual.loaders_optional import load_variable_pay_rules
from ccnl_engine.tax.regime.models import EmploymentSector

_RINNOVO = load_variable_pay_rules(2026).rinnovo
_PRIVATE = EmploymentSector.PRIVATE
_PAID = RenewalMinimum(minimum=Decimal("2211.43"), table_from=date(2024, 6, 1))
_ZERO = Decimal(0)


def _series(*tables: tuple[date, date | None]) -> TimeSeries:
    return TimeSeries(
        periods=tuple(
            ValidityPeriod(valid_from=start, valid_until=end, value=Decimal(1_000))
            for start, end in tables
        )
    )


#: Tables of 1 June 2023, 1 June 2024 and 1 June 2026.
_TABLES = _series(
    (date(2023, 6, 1), date(2024, 6, 1)),
    (date(2024, 6, 1), date(2026, 6, 1)),
    (date(2026, 6, 1), None),
)


class TestRenewalTableFrom:
    """The first table of the minimo dated within 2024-01-01 .. 2026-12-31."""

    def test_first_table_within_the_window(self) -> None:
        """A June 2026 run reads the 2024 table as the first in the window."""
        assert renewal_table_from(_TABLES, _RINNOVO, date(2026, 6, 15)) == date(
            2024, 6, 1
        )

    def test_no_table_before_the_competence_date(self) -> None:
        """In May 2024 only the 2023 table is in force: no renewal table yet."""
        assert renewal_table_from(_TABLES, _RINNOVO, date(2024, 5, 31)) is None

    def test_table_after_the_window_is_left_out(self) -> None:
        """A 2027 table is outside the window even when in force."""
        series = _series((date(2023, 1, 1), date(2027, 1, 1)), (date(2027, 1, 1), None))
        assert renewal_table_from(series, _RINNOVO, date(2027, 3, 1)) is None

    def test_gap_table_is_left_out(self) -> None:
        """A table with no value carries no increment."""
        series = TimeSeries(
            periods=(
                ValidityPeriod(
                    valid_from=date(2023, 1, 1),
                    valid_until=date(2025, 1, 1),
                    value=Decimal(1_000),
                ),
                ValidityPeriod(
                    valid_from=date(2025, 1, 1),
                    valid_until=None,
                    gap_kind=SalaryGapKind.MISSING,
                ),
            )
        )
        assert renewal_table_from(series, _RINNOVO, date(2026, 6, 1)) is None

    def test_regime_without_signing_window(self) -> None:
        """A regime with no signing window ties no table to a renewal."""
        regime = _RINNOVO.model_copy(
            update={"agreements_signed_from": None, "agreements_signed_until": None}
        )
        assert renewal_table_from(_TABLES, regime, date(2026, 6, 15)) is None


def _assess(
    income: Decimal | None, sector: EmploymentSector | None = _PRIVATE
) -> tuple[str, CalculationStatus, list[tuple[str, str | None]]]:
    assessed = assess_renewal_minimum(
        _RINNOVO, RegimeFacts(prior_income=income, sector=sector), 2026, _PAID
    )
    decision = assessed.decision
    assert decision.capability == "rinnovo_substitute_tax"
    assert decision.amount == _ZERO
    return (
        decision.reason_code,
        decision.status,
        [(issue.code, issue.fact) for issue in assessed.issues],
    )


class TestAssessRenewalMinimum:
    """The worker facts decide; the increment itself is never taxed."""

    def test_income_above_the_ceiling_is_final(self) -> None:
        """2025 income 33,000.01 > 33,000: excluded, no issue."""
        assert _assess(Decimal("33000.01")) == (
            "prior_income_above_ceiling",
            CalculationStatus.FINAL,
            [],
        )

    def test_public_sector_is_final(self) -> None:
        """Only "lavoratori del settore privato": excluded whatever the income."""
        assert _assess(None, EmploymentSector.PUBLIC) == (
            "sector_not_eligible",
            CalculationStatus.FINAL,
            [],
        )

    def test_unknown_income_is_a_missing_fact(self) -> None:
        """Unknown 2025 income: provisional, the income is the missing fact."""
        assert _assess(None) == (
            "prior_income_unknown",
            CalculationStatus.PROVISIONAL,
            [("rinnovo_eligibility_unknown", "employment_income")],
        )

    def test_every_missing_fact_is_reported(self) -> None:
        """Unknown sector and income: one issue each, the sector first."""
        assert _assess(None, None) == (
            "sector_unknown",
            CalculationStatus.PROVISIONAL,
            [
                ("rinnovo_eligibility_unknown", "sector"),
                ("rinnovo_eligibility_unknown", "employment_income"),
            ],
        )

    def test_eligible_worker_leaves_the_increment_unquantified(self) -> None:
        """2025 income of exactly 33,000 ("non superiore") is eligible."""
        assert _assess(Decimal(33_000)) == (
            INCREMENT_UNQUANTIFIED,
            CalculationStatus.PROVISIONAL,
            [("rinnovo_minimum_increment_unquantified", None)],
        )

    def test_decision_records_the_minimo_and_its_table(self) -> None:
        """The inputs name the minimo, its table and the facts read."""
        decision = assess_renewal_minimum(
            _RINNOVO, RegimeFacts(sector=_PRIVATE), 2026, _PAID
        ).decision
        assert decision.inputs["paid_in"] == "minimum"
        assert decision.inputs["minimum"] == Decimal("2211.43")
        assert decision.inputs["table_from"] == "2024-06-01"
        assert decision.inputs["prior_income"] == "unknown"
        assert decision.inputs["sector"] == "private"
        assert decision.source == _RINNOVO.source

    @pytest.mark.parametrize("with_ruleset", [True, False])
    def test_rule_is_the_ruleset_or_the_regime(self, with_ruleset: bool) -> None:
        """The rule is the ruleset of the regime, or its id and the tax year."""
        regime = (
            _RINNOVO if with_ruleset else _RINNOVO.model_copy(update={"ruleset": None})
        )
        decision = assess_renewal_minimum(
            regime, RegimeFacts(sector=_PRIVATE), 2026, _PAID
        ).decision
        ruleset = _RINNOVO.ruleset
        assert ruleset is not None
        expected = (
            (ruleset.id, ruleset.version) if with_ruleset else ("rinnovo", "2026")
        )
        assert (decision.rule, decision.rule_version) == expected
