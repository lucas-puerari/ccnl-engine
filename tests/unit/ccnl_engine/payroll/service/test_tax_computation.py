"""compute_tax: IRPEF breakdown of one period from in-memory year rules."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
from ccnl_engine.payroll.service.tax_computation import compute_tax
from ccnl_engine.tax.domain.credit_rules import (
    SommaEsenteBand,
    SommaEsenteRules,
    TrattamentoIntegrativoRules,
    UlterioreDetrazioneRules,
)
from ccnl_engine.tax.domain.irpef_rules import SterilizzazioneDetrazioniRules
from tests.helpers import make_year_rules

_ZERO = Decimal(0)

_TWELVE_SLOTS = WithholdingSchedule.from_calendar(WorkCalendar(year=2026))


class TestResolveTaxComputation:
    """compute_tax: IRPEF breakdown with rule_id and fonte annotation."""

    def test_ordinary_tax_positive_for_typical_income(self) -> None:
        """Typical income produces positive ordinary_tax and irpef_gross component."""
        rules = make_year_rules()
        tc = compute_tax(
            Decimal(25000),
            rules,
            opening_irpef_withheld=_ZERO,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        assert tc.ordinary_tax > _ZERO
        names = [c.name for c in tc.components]
        assert "irpef_gross" in names
        assert "work_deduction" in names

    def test_trattamento_integrativo_emitted_when_eligible(self) -> None:
        """Low-income worker with positive irpef: trattamento component emitted."""
        rules = make_year_rules()
        ti = TrattamentoIntegrativoRules(
            threshold_mid=Decimal(15000),
            threshold_upper=Decimal(28000),
            max_amount=Decimal(1200),
        )
        rules_with_ti = rules.model_copy(update={"trattamento_integrativo": ti})
        tc = compute_tax(
            Decimal(10000),
            rules_with_ti,
            opening_irpef_withheld=_ZERO,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "trattamento_integrativo" in names
        assert tc.trattamento_integrativo > _ZERO

    def test_no_trattamento_when_rules_absent(self) -> None:
        """When trattamento_integrativo rules are absent the period credit is zero."""
        rules = make_year_rules()
        # Default make_year_rules() has trattamento_integrativo=None
        tc = compute_tax(
            Decimal(10000),
            rules,
            opening_irpef_withheld=_ZERO,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "trattamento_integrativo" not in names
        assert tc.trattamento_integrativo == _ZERO

    def test_ulteriore_detrazione_zero_not_emitted(self) -> None:
        """ulteriore_detrazione configured but income outside range: not emitted."""
        rules = make_year_rules()
        ud_rules = UlterioreDetrazioneRules(
            threshold_low=Decimal(20000),
            threshold_mid=Decimal(32000),
            threshold_high=Decimal(40000),
            max_amount=Decimal(720),
        )
        rules_with_ud = rules.model_copy(update={"ulteriore_detrazione": ud_rules})
        # taxable=10000 <= threshold_low → zero
        tc = compute_tax(
            Decimal(10000),
            rules_with_ud,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "ulteriore_detrazione" not in names

    def test_sterilizzazione_reduces_deductions_for_high_earner(self) -> None:
        """sterilizzazione_detrazioni: high-income worker gets reduced deductions."""
        rules = make_year_rules()
        steriliz = SterilizzazioneDetrazioniRules(
            threshold=Decimal(200000), reduction=Decimal(440)
        )
        rules_with_s = rules.model_copy(update={"sterilizzazione_detrazioni": steriliz})
        # taxable > 200000 + non-zero deductions so reduction is applied
        tc = compute_tax(
            Decimal(250000),
            rules_with_s,
            family_deductions=Decimal(1000),
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "sterilizzazione_detrazioni" in names

    def test_somma_esente_emitted_for_low_income(self) -> None:
        """somma_esente: low-income worker receives positive bonus component."""
        rules = make_year_rules()
        se_rules = SommaEsenteRules(
            bands=[SommaEsenteBand(up_to=Decimal(20000), rate=Decimal("0.07"))]
        )
        rules_with_se = rules.model_copy(update={"somma_esente": se_rules})
        tc = compute_tax(
            Decimal(10000),
            rules_with_se,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "somma_esente" in names
