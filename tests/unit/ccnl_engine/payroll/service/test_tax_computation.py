"""compute_tax: IRPEF breakdown of one period from in-memory year rules."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.service.period_withholding import PayPeriod
from ccnl_engine.payroll.service.tax_computation import compute_tax
from ccnl_engine.tax.income.models import SterilizzazioneDetrazioniRules
from ccnl_engine.tax.income.models_credit import (
    SommaEsenteBand,
    SommaEsenteRules,
    TrattamentoIntegrativoRules,
    UlterioreDetrazioneRules,
)
from tests.helpers import make_year_rules

_ZERO = Decimal(0)


class TestResolveTaxComputation:
    """compute_tax: IRPEF breakdown with rule_id and fonte annotation."""

    def test_ordinary_tax_positive_for_typical_income(self) -> None:
        """Typical income produces positive ordinary_tax and irpef_gross component."""
        rules = make_year_rules()
        tc = compute_tax(
            Decimal(25000),
            rules,
            opening_irpef_withheld=_ZERO,
            remaining_slots=12,
            period=PayPeriod(
                regular_taxable=Decimal("2083.33"), day_share=Decimal(31) / 365
            ),
        ).computation
        assert tc.ordinary_tax > _ZERO
        names = [c.name for c in tc.components]
        assert "irpef_gross" in names
        assert "work_deduction" in names

    def test_a_run_without_pay_withholds_nothing_before_the_conguaglio(self) -> None:
        """Art. 23 c. 2 DPR 600/1973 withholds on the pay of the period."""
        tc = compute_tax(Decimal(25000), make_year_rules(), remaining_slots=12)
        assert tc.computation.ordinary_tax == _ZERO

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
            remaining_slots=12,
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
            remaining_slots=12,
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
            remaining_slots=12,
        ).computation
        names = [c.name for c in tc.components]
        assert "ulteriore_detrazione" not in names

    def test_art_16ter_reduction_leaves_family_deductions_whole(self) -> None:
        """Above 200,000 EUR the trace keeps the art. 12 deductions in full.

        Art. 16-ter c. 5-bis TUIR (L. 199/2025 art. 1 c. 4) lowers only the
        19% oneri, party donations and catastrophe premiums, none of them
        computed here: no reduction line, family deductions 1,000.
        """
        rules = make_year_rules()
        steriliz = SterilizzazioneDetrazioniRules(
            threshold=Decimal(200000), reduction=Decimal(440)
        )
        rules_with_s = rules.model_copy(update={"sterilizzazione_detrazioni": steriliz})
        tc = compute_tax(
            Decimal(250000),
            rules_with_s,
            family_deductions=Decimal(1000),
            remaining_slots=12,
        ).computation
        amounts = {c.name: c.amount for c in tc.components}
        assert "sterilizzazione_detrazioni" not in amounts
        assert amounts["family_deductions"] == Decimal(1000)

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
            remaining_slots=12,
        ).computation
        names = [c.name for c in tc.components]
        assert "somma_esente" in names
