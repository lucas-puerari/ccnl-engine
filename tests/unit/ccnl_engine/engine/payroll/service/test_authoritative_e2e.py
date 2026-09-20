"""Authoritative E2E reference tests for the payroll engine pipeline.

Each test is a certified scenario with expected values derived from primary
sources (CCNL texts, official INPS/MEF tables, Art. 12 TUIR) or from engine
output cross-validated against those sources. The scenario, source, and
expected values are co-located for readability.

These complement the JSON reference suite (tests/reference/) with explicit
Python assertions that are easier to review and extend than flat JSON diffs.

Scenarios covered:
  1. Ordinary full-time permanent worker (Alimentari Federalimentare L3).
  2. Apprentice under-level (Autoscuole UNASCA L3, 20 months elapsed).
  3. Apprentice part-time 50% (Metalmeccanico Artigianato L3, 12 months).
  4. High-earning worker above IVS ceiling (Metalmeccanico Federmeccanica C3).
  5. Family deductions: spouse (Metalmeccanico Federmeccanica C2).
  6. Family deductions: child aged 21+ (Metalmeccanico Federmeccanica C2).
  7. Regional + municipal surcharge (Federmeccanica C3, Lombardia + Agordo).
  8. Fringe benefit above standard threshold (Federmeccanica C2, €1 400).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.payroll.domain.employee import RalOverride
from ccnl_engine.engine.payroll.domain.employment import Apprentice, Permanent
from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PayrollScenario,
)
from ccnl_engine.engine.payroll.domain.supplements import FringeBenefitInput
from ccnl_engine.engine.payroll.service.orchestrator import compute


def _run(scenario: PayrollScenario) -> object:
    """Call compute() and return the AnnualEstimate result.

    Returns:
        The AnnualEstimate from the Calculation.
    """
    return compute(scenario).result


# ---------------------------------------------------------------------------
# 1. Ordinary full-time permanent worker
# ---------------------------------------------------------------------------


class TestOrdinaryFullTimePermanent:
    """CCNL Alimentari Industria Federalimentare (E004), Level 3, 2026-01-01.

    Source: sindacato.it, tabelle retributive Federalimentare 2026.
    4th tranche (2026-01-01): TEM 1566.16 EUR.
    Split: base=1566.16, contingenza=522.32, EDR=10.33, IAR=85.41.
    Additional months: 14 (tredicesima + quattordicesima).
    INPS employer rate 30.20% (16-50 employees, 2026-industria.json).
    IRPEF 2026 brackets: 23% up to 28000, 33% up to 50000 (L. 199/2025).
    """

    def _scenario(self) -> PayrollScenario:
        return PayrollScenario(
            employee=Employee(level_code="3"),
            employment=Employment(
                ccnl="alimentari-federalimentare.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 1, 1),
            ),
        )

    def test_gross_monthly(self) -> None:
        """gross_monthly: 1566.16 + 618.06 = 2184.22 EUR."""
        result = _run(self._scenario())
        assert result.earnings.gross_monthly == Decimal("2184.22")  # type: ignore[attr-defined]

    def test_gross_annual(self) -> None:
        """gross_annual: 2184.22 * 14 additional months = 30579.08 EUR."""
        result = _run(self._scenario())
        assert result.earnings.gross_annual == Decimal("30579.08")  # type: ignore[attr-defined]

    def test_net_annual(self) -> None:
        """net_annual after INPS + IRPEF + ulteriore detrazione."""
        result = _run(self._scenario())
        assert result.net_annual == Decimal("24315.90")  # type: ignore[attr-defined]

    def test_employer_cost_annual(self) -> None:
        """employer_cost: gross + INPS 30.20% + TFR 7.41%."""
        result = _run(self._scenario())
        assert result.employer_cost.employer_cost_annual == Decimal("42079.08")  # type: ignore[attr-defined]

    def test_inps_employee_annual(self) -> None:
        """Employee INPS: 9.49% of contribution_base."""
        result = _run(self._scenario())
        assert result.contributions.inps_employee_annual == Decimal("2901.95")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# 2. Apprentice under-level (under-classification track)
# ---------------------------------------------------------------------------


class TestApprenticeUnderLevel:
    """CCNL Autoscuole UNASCA/CONFARCA (IC91), Level 3 apprentice, 20 months.

    Source: CCNL Autoscuole track L3-48m; months 16-31: levels_below=1.
    Base: level 2 paga base (938.41) + contingenza (439.83) + EDR (10.33).
    Destination level: 3; pay level: 2 (one below destination).
    """

    def _scenario(self) -> PayrollScenario:
        return PayrollScenario(
            employee=Employee(level_code="3"),
            employment=Employment(
                ccnl="autoscuole-unasca.json",
                contract=Apprentice(months_elapsed=20),
                employer=Employer(num_employees=50),
                as_of=date(2026, 6, 1),
            ),
        )

    def test_apprenticeship_under_level_code(self) -> None:
        """Pay is at level 2 (one below destination 3)."""
        result = _run(self._scenario())
        assert result.earnings.apprenticeship_under_level_code == "2"  # type: ignore[attr-defined]

    def test_gross_monthly(self) -> None:
        """gross_monthly: base 938.41 + allowances 450.16 = 1388.57."""
        result = _run(self._scenario())
        assert result.earnings.gross_monthly == Decimal("1388.57")  # type: ignore[attr-defined]

    def test_gross_annual(self) -> None:
        """gross_annual: 1388.57 * 14 = 19439.98."""
        result = _run(self._scenario())
        assert result.earnings.gross_annual == Decimal("19439.98")  # type: ignore[attr-defined]

    def test_somma_esente(self) -> None:
        """somma_esente: 878.63 (apprentice IRPEF exemption)."""
        result = _run(self._scenario())
        assert result.taxes.somma_esente == Decimal("878.63")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# 3. Apprentice part-time 50%
# ---------------------------------------------------------------------------


class TestApprenticePartTime50:
    """CCNL Metalmeccanico Artigianato (H049), Level 3, 12 months, 50%.

    Source: CCNL Metalmeccanico Artigianato percentage track.
    Apprentice pct at month 12: 75% of destination wage.
    Part-time ratio 0.5 applied to all scalable components.
    Small firm (12 employees): apprentice INPS rate.
    """

    def _scenario(self) -> PayrollScenario:
        return PayrollScenario(
            employee=Employee(level_code="3", part_time_ratio=Decimal("0.5")),
            employment=Employment(
                ccnl="metalmeccanico-artigianato.json",
                contract=Apprentice(months_elapsed=12),
                employer=Employer(num_employees=12),
                as_of=date(2026, 1, 1),
            ),
        )

    def test_apprenticeship_pct(self) -> None:
        """Apprentice pct at month 12: 75%."""
        result = _run(self._scenario())
        assert result.earnings.apprenticeship_pct == Decimal("0.75")  # type: ignore[attr-defined]

    def test_gross_monthly(self) -> None:
        """gross_monthly: destination * 0.75 * 0.50 = 649.31 EUR."""
        result = _run(self._scenario())
        assert result.earnings.gross_monthly == Decimal("649.31")  # type: ignore[attr-defined]

    def test_gross_annual(self) -> None:
        """gross_annual: 649.31 * 13 additional months = 8441.03 EUR."""
        result = _run(self._scenario())
        assert result.earnings.gross_annual == Decimal("8441.03")  # type: ignore[attr-defined]

    def test_irpef_net_zero(self) -> None:
        """irpef_net: 0 (work deduction exceeds IRPEF gross at this income)."""
        result = _run(self._scenario())
        assert result.taxes.irpef_net == Decimal("0.00")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# 4. High-earning worker above IVS ceiling
# ---------------------------------------------------------------------------


class TestIvsCeilingHighEarner:
    """CCNL Metalmeccanico Federmeccanica (H041), C3, RAL 130 000 EUR.

    Source: INPS circular 2026 — massimale contribuzione IVS.
    ivs_ceiling_applies=True: two-rate IVS structure applied.
    Gross_annual = negotiated_ral = 130 000 EUR (RAL override).
    trattamento_integrativo = 0 (RAL > 28 000).
    IRPEF 2026 brackets applied (L. 199/2025).
    """

    def _scenario(self) -> PayrollScenario:
        return PayrollScenario(
            employee=Employee(
                level_code="C3",
                ivs_ceiling_applies=True,
                agreement=Agreement(ral_override=RalOverride(value=Decimal(130000))),
            ),
            employment=Employment(
                ccnl="metalmeccanico-federmeccanica.json",
                contract=Permanent(),
                employer=Employer(num_employees=200),
                as_of=date(2026, 1, 1),
            ),
        )

    def test_gross_annual(self) -> None:
        """gross_annual: equals negotiated RAL = 130 000.00 EUR."""
        result = _run(self._scenario())
        assert result.earnings.gross_annual == Decimal("130000.00")  # type: ignore[attr-defined]

    def test_inps_employee_annual(self) -> None:
        """Employee INPS: two-rate IVS above massimale = 12 289.62 EUR."""
        result = _run(self._scenario())
        assert result.contributions.inps_employee_annual == Decimal("12289.62")  # type: ignore[attr-defined]

    def test_net_annual(self) -> None:
        """net_annual: gross - INPS - IRPEF 33%/43% brackets."""
        result = _run(self._scenario())
        assert result.net_annual == Decimal("74894.92")  # type: ignore[attr-defined]

    def test_trattamento_integrativo_zero(self) -> None:
        """trattamento_integrativo: 0 (RAL > 28 000 threshold)."""
        result = _run(self._scenario())
        assert result.taxes.trattamento_integrativo == Decimal(0)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# 5. Family deductions: fiscally dependent spouse
# ---------------------------------------------------------------------------


class TestFamilySpouseDeduction:
    """CCNL Metalmeccanico Federmeccanica (H041), C2, spouse at charge.

    Source: Art. 12 TUIR (D.P.R. 917/1986), c. 1 lett. a.
    Taxable income bracket 15 001-40 000: spouse deduction = EUR 690 flat.
    (Sub-band supplements not modelled; fiscal simplification declared.)
    """

    def _scenario(self) -> PayrollScenario:
        return PayrollScenario(
            employee=Employee(level_code="C2"),
            employment=Employment(
                ccnl="metalmeccanico-federmeccanica.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 9, 1),
            ),
            family=FamilyComposition(
                dependents=(Dependent(relationship=DependentRelationship.SPOUSE),)
            ),
        )

    def test_family_deduction_spouse_annual(self) -> None:
        """Spouse deduction: EUR 690.00 (bracket 15 001-40 000, flat)."""
        result = _run(self._scenario())
        assert result.taxes.family_deduction_spouse_annual == Decimal("690.00")  # type: ignore[attr-defined]

    def test_family_deduction_children_zero(self) -> None:
        """No child dependents declared: children deduction = 0."""
        result = _run(self._scenario())
        assert result.taxes.family_deduction_children_annual == Decimal(0)  # type: ignore[attr-defined]

    def test_irpef_net(self) -> None:
        """irpef_net reduced by spouse deduction vs no-family scenario."""
        result = _run(self._scenario())
        assert result.taxes.irpef_net == Decimal("1649.05")  # type: ignore[attr-defined]

    def test_net_annual(self) -> None:
        """net_annual after family deduction benefit."""
        result = _run(self._scenario())
        assert result.net_annual == Decimal("22646.95")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# 6. Family deductions: child aged 21+ (post-AUU rules)
# ---------------------------------------------------------------------------


class TestFamilyChildOver21:
    """CCNL Metalmeccanico Federmeccanica (H041), C2, one child born 2001-01-01.

    Source: Art. 12 TUIR c. 1 lett. c — deduction for children aged 21+.
    Taper formula: max(0, (95 000 - taxable_income) / 95 000).
    taxable_income = 24 296.00; taper = (95000-24296)/95000 ≈ 0.74426.
    deduction = money(950 * taper) = 707.04 EUR.
    """

    def _scenario(self) -> PayrollScenario:
        return PayrollScenario(
            employee=Employee(level_code="C2"),
            employment=Employment(
                ccnl="metalmeccanico-federmeccanica.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 9, 1),
            ),
            family=FamilyComposition(
                dependents=(
                    Dependent(
                        relationship=DependentRelationship.CHILD,
                        birth_date=date(2001, 1, 1),
                    ),
                )
            ),
        )

    def test_family_deduction_children_annual(self) -> None:
        """Child 21+ deduction: money(950 * taper) = 707.04 EUR."""
        result = _run(self._scenario())
        assert result.taxes.family_deduction_children_annual == Decimal("707.04")  # type: ignore[attr-defined]

    def test_family_deduction_spouse_zero(self) -> None:
        """No spouse declared: spouse deduction = 0."""
        result = _run(self._scenario())
        assert result.taxes.family_deduction_spouse_annual == Decimal(0)  # type: ignore[attr-defined]

    def test_net_annual(self) -> None:
        """net_annual after child deduction benefit."""
        result = _run(self._scenario())
        assert result.net_annual == Decimal("22663.99")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# 7. Regional + municipal surcharge (surtax)
# ---------------------------------------------------------------------------


class TestSurtaxRegionaleAndComunale:
    """CCNL Metalmeccanico Federmeccanica (H041), C3, Lombardia + Agordo (A083).

    Source: MEF addizionale-regionale-2026.json and addizionale-comunale-2026.json.
    Regionale Lombardia 2026: 1.23% on all income (single bracket up to 28 000).
    Comunale Agordo (A083): 0.63% up to 15 000; 0.76% from 15 001 to 28 000.
    Acconto 2026 (30%): advance withheld using 2025 rates as base.
    Taxable income: 25 394.73 EUR.
    """

    def _scenario(self) -> PayrollScenario:
        return PayrollScenario(
            employee=Employee(
                level_code="C3",
                jurisdiction=Jurisdiction(
                    regione="Lombardia",
                    comune_belfiore="A083",
                ),
            ),
            employment=Employment(
                ccnl="metalmeccanico-federmeccanica.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 1, 1),
            ),
        )

    def test_addizionale_regionale_annual(self) -> None:
        """Regionale Lombardia: 1.23% * 25 394.73 = 312.36 EUR."""
        result = _run(self._scenario())
        assert result.taxes.addizionale_regionale_annual == Decimal("312.36")  # type: ignore[attr-defined]

    def test_addizionale_comunale_annual(self) -> None:
        """Comunale Agordo: advance only (addizionale_comunale_advance_only)."""
        result = _run(self._scenario())
        assert result.taxes.addizionale_comunale_annual == Decimal("52.05")  # type: ignore[attr-defined]

    def test_net_annual(self) -> None:
        """net_annual after regionale + comunale surcharges."""
        result = _run(self._scenario())
        assert result.net_annual == Decimal("22403.01")  # type: ignore[attr-defined]

    def test_gross_annual(self) -> None:
        """gross_annual: 2158.26 * 13 additional months = 28057.38 EUR."""
        result = _run(self._scenario())
        assert result.earnings.gross_annual == Decimal("28057.38")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# 8. Fringe benefit above standard threshold
# ---------------------------------------------------------------------------


class TestFringeBenefitAboveThreshold:
    """CCNL Metalmeccanico Federmeccanica (H041), C2, fringe €1 400 (no children).

    Source: Art. 51 c. 3 TUIR — esenzione fringe benefit 2026.
    Standard threshold (no dependent children): EUR 1 000.
    Entire benefit amount taxable (amount > threshold, rule R15).
    fringe_benefit_taxable_annual = 1 400 EUR (full amount taxable).
    IRPEF increase: 1400 * 23% = 322 EUR (23% bracket at this income).
    """

    def _scenario(self) -> PayrollScenario:
        return PayrollScenario(
            employee=Employee(level_code="C2"),
            employment=Employment(
                ccnl="metalmeccanico-federmeccanica.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 9, 1),
            ),
            fringe_benefit_input=FringeBenefitInput(
                annual_amount=Decimal(1400),
                has_dependent_children=False,
            ),
        )

    def test_fringe_benefit_taxable_annual(self) -> None:
        """Entire 1 400 EUR is taxable (amount > 1 000 threshold)."""
        result = _run(self._scenario())
        assert result.fringe_benefit_taxable_annual == Decimal("1400.00")  # type: ignore[attr-defined]

    def test_fringe_benefit_threshold_annual(self) -> None:
        """Standard threshold (no children): EUR 1 000.00."""
        result = _run(self._scenario())
        assert result.fringe_benefit_threshold_annual == Decimal("1000.00")  # type: ignore[attr-defined]

    def test_irpef_net(self) -> None:
        """irpef_net higher than no-fringe scenario (1 400 fully taxable)."""
        result = _run(self._scenario())
        assert result.taxes.irpef_net == Decimal("2724.21")  # type: ignore[attr-defined]

    def test_net_annual(self) -> None:
        """net_annual reduced by full IRPEF on 1 400 fringe."""
        result = _run(self._scenario())
        assert result.net_annual == Decimal("21571.79")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# 9. Conguaglio IRPEF — R3 regression
# ---------------------------------------------------------------------------


class TestConguaglioNetAnnualR3:
    """Regression for R3: prior_period_irpef_withheld must not reduce net_annual.

    The settlement delta (conguaglio_annual) is informational: it shows how
    much IRPEF remains to withhold for the period, but annual net must always
    reflect the full-year tax liability (irpef_net), regardless of prior
    withholdings.  Bug: net_annual was incorrectly reduced by conguaglio_annual
    a second time on top of the already-subtracted irpef_net.
    """

    def _scenario(self, prior: Decimal | None = None) -> PayrollScenario:
        return PayrollScenario(
            employee=Employee(level_code="3"),
            employment=Employment(
                ccnl="alimentari-federalimentare.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 1, 1),
            ),
            prior_period_irpef_withheld=prior,
        )

    def test_no_prior_withholding_conguaglio_zero(self) -> None:
        """With no prior withholding, conguaglio_annual is zero."""
        result = _run(self._scenario())
        assert result.taxes.conguaglio_annual == Decimal(0)  # type: ignore[attr-defined]

    def test_net_annual_unchanged_under_withholding(self) -> None:
        """net_annual must not change when prior_period_irpef_withheld < irpef_net."""
        base = _run(self._scenario())
        under = _run(self._scenario(prior=Decimal("1000.00")))
        assert under.net_annual == base.net_annual  # type: ignore[attr-defined]

    def test_net_annual_unchanged_over_withholding(self) -> None:
        """net_annual must not change when prior_period_irpef_withheld > irpef_net."""
        base = _run(self._scenario())
        irpef_net = base.taxes.irpef_net  # type: ignore[attr-defined]
        over = _run(self._scenario(prior=irpef_net + Decimal("500.00")))
        assert over.net_annual == base.net_annual  # type: ignore[attr-defined]

    def test_conguaglio_under_withheld_is_positive(self) -> None:
        """conguaglio_annual > 0 when more tax is owed than was pre-withheld."""
        prior = Decimal("1000.00")
        base_irpef = _run(self._scenario()).taxes.irpef_net  # type: ignore[attr-defined]
        result = _run(self._scenario(prior=prior))
        assert result.taxes.conguaglio_annual == base_irpef - prior  # type: ignore[attr-defined]

    def test_conguaglio_over_withheld_is_negative(self) -> None:
        """conguaglio_annual < 0 when more was pre-withheld than total liability."""
        base_irpef = _run(self._scenario()).taxes.irpef_net  # type: ignore[attr-defined]
        prior = base_irpef + Decimal("500.00")
        result = _run(self._scenario(prior=prior))
        assert result.taxes.conguaglio_annual == Decimal("-500.00")  # type: ignore[attr-defined]
