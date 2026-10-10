"""Tests for the IRPEF credits: TI, ulteriore detrazione and somma esente.

Covers trattamento_integrativo(), ulteriore_detrazione_lavoro() and
somma_esente(), for a full year and pro rata, including the TI requisito
logic.
"""

from decimal import Decimal

from ccnl_engine.payroll.service.irpef_credits import (
    somma_esente,
    trattamento_integrativo,
    ulteriore_detrazione_lavoro,
)
from ccnl_engine.tax.income.models_credit import (
    SommaEsenteBand,
    SommaEsenteRules,
    TrattamentoIntegrativoRules,
    UlterioreDetrazioneRules,
)

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# trattamento_integrativo — Art. 1 D.L. 3/2020 as updated by L. 207/2024
# ---------------------------------------------------------------------------

_TI_RULES = TrattamentoIntegrativoRules(
    threshold_mid=Decimal(15000),
    threshold_upper=Decimal(28000),
    max_amount=Decimal(1200),
)


class TestTrattamentoIntegrativo:
    """Unit tests for trattamento_integrativo()."""

    # -- RC > 28 000 ----------------------------------------------------------

    def test_above_upper_threshold_zero(self) -> None:
        """RC > 28 000: bonus is always zero."""
        result = trattamento_integrativo(
            Decimal(30000),
            Decimal(5000),
            Decimal(1800),
            Decimal(1800),
            _TI_RULES,
        )
        assert result == Decimal("0.00")

    # -- RC ≤ 15 000 ----------------------------------------------------------

    def test_lower_band_bonus_granted(self) -> None:
        """RC=8300, IRPEF=1909, detr=1955 (full year): 1909 > 1955-75=1880.

        Regression: this once returned zero instead of 1200.
        """
        result = trattamento_integrativo(
            Decimal(8300),
            Decimal(1909),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_lower_band_bonus_denied(self) -> None:
        """RC=10000, IRPEF=300, detr=1955: 300 ≤ 1880 → no bonus."""
        result = trattamento_integrativo(
            Decimal(10000),
            Decimal(300),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("0.00")

    def test_lower_band_exactly_at_threshold(self) -> None:
        """RC=10000, IRPEF=1880, detr=1955: 1880 = 1955-75 → not strictly >."""
        result = trattamento_integrativo(
            Decimal(10000),
            Decimal(1880),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("0.00")

    def test_lower_band_one_above_threshold(self) -> None:
        """RC=10000, IRPEF=1881: 1881 > 1955-75=1880 → bonus = 1200."""
        result = trattamento_integrativo(
            Decimal(10000),
            Decimal(1881),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    # -- 15 000 < RC ≤ 28 000 -------------------------------------------------

    def test_mid_band_requisito_not_met(self) -> None:
        """RC=20000, IRPEF=4600, relevant=2642.21: IRPEF > deductions → 0.

        Regression: this once returned 738.46 (wrong linear taper).
        """
        result = trattamento_integrativo(
            Decimal(20000),
            Decimal(4600),
            Decimal("2642.21"),
            Decimal("2642.21"),
            _TI_RULES,
        )
        assert result == Decimal("0.00")

    def test_mid_band_requisito_met_capped(self) -> None:
        """RC=20000, relevant_deductions > IRPEF by more than 1200: cap at 1200."""
        result = trattamento_integrativo(
            Decimal(20000),
            Decimal(1000),
            Decimal(2500),
            Decimal(3000),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_mid_band_requisito_met_partial(self) -> None:
        """RC=20000, relevant - IRPEF = 500: bonus = 500."""
        result = trattamento_integrativo(
            Decimal(20000),
            Decimal(2000),
            Decimal(2500),
            Decimal(2500),
            _TI_RULES,
        )
        assert result == Decimal("500.00")

    def test_mid_band_exactly_at_mid_threshold(self) -> None:
        """RC exactly at 15000 uses the lower-band check (≤ threshold_mid)."""
        # IRPEF=1909, detr=1955, corrective=75: 1909 > 1955-75=1880 → 1200
        result = trattamento_integrativo(
            Decimal(15000),
            Decimal(1909),
            Decimal(1955),
            Decimal(1955),
            _TI_RULES,
        )
        assert result == Decimal("1200.00")

    def test_mid_band_exactly_at_upper_threshold(self) -> None:
        """RC exactly at 28000: above upper → zero (> threshold_upper check)."""
        result = trattamento_integrativo(
            Decimal(28001),
            Decimal(3000),
            Decimal(2000),
            Decimal(2000),
            _TI_RULES,
        )
        assert result == Decimal("0.00")


# ---------------------------------------------------------------------------
# ulteriore_detrazione_lavoro — Art. 1 c. 6 L. 207/2024
# ---------------------------------------------------------------------------

_UD_RULES = UlterioreDetrazioneRules(
    threshold_low=Decimal(20000),
    threshold_mid=Decimal(32000),
    threshold_high=Decimal(40000),
    max_amount=Decimal(1000),
)


class TestUlterioreDedrazioneLavoro:
    """Unit tests for ulteriore_detrazione_lavoro()."""

    def test_below_threshold_low_returns_zero(self) -> None:
        """Income at threshold_low: no deduction (band is exclusive on the left)."""
        assert ulteriore_detrazione_lavoro(Decimal(20000), _UD_RULES) == Decimal(0)

    def test_just_above_threshold_low(self) -> None:
        """Income just above threshold_low: full max_amount."""
        assert ulteriore_detrazione_lavoro(Decimal("20000.01"), _UD_RULES) == Decimal(
            1000
        )

    def test_mid_band(self) -> None:
        """Income in the middle of the flat band: max_amount."""
        assert ulteriore_detrazione_lavoro(Decimal(27000), _UD_RULES) == Decimal(1000)

    def test_at_threshold_mid(self) -> None:
        """Income at threshold_mid (inclusive): max_amount — no discontinuity."""
        assert ulteriore_detrazione_lavoro(Decimal(32000), _UD_RULES) == Decimal(1000)

    def test_just_above_threshold_mid_taper_starts(self) -> None:
        """Income just above threshold_mid: taper begins, rounds to max_amount.

        1 000 * 7 999.99 / 8 000 = 999.99875, not truncated, in cents 1 000.00.
        """
        result = ulteriore_detrazione_lavoro(Decimal("32000.01"), _UD_RULES)
        assert result == Decimal("1000.00")

    def test_taper_interior_36204(self) -> None:
        """Taper at 36 204: 1000 * (40000 - 36204) / 8000 = 474.50."""
        result = ulteriore_detrazione_lavoro(Decimal(36204), _UD_RULES)
        assert result == Decimal("474.50")

    def test_at_threshold_high_returns_zero(self) -> None:
        """Income at threshold_high: taper reaches zero."""
        assert ulteriore_detrazione_lavoro(Decimal(40000), _UD_RULES) == Decimal(0)

    def test_above_threshold_high_returns_zero(self) -> None:
        """Income above threshold_high: no deduction."""
        assert ulteriore_detrazione_lavoro(Decimal("40000.01"), _UD_RULES) == Decimal(0)

    def test_well_above_band_returns_zero(self) -> None:
        """High income: no deduction."""
        assert ulteriore_detrazione_lavoro(Decimal(80000), _UD_RULES) == Decimal(0)

    def test_zero_income_returns_zero(self) -> None:
        """Zero income is below threshold_low: no deduction."""
        assert ulteriore_detrazione_lavoro(Decimal(0), _UD_RULES) == Decimal(0)


_SE_RULES = SommaEsenteRules(
    bands=[
        SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.071")),
        SommaEsenteBand(up_to=Decimal(15000), rate=Decimal("0.053")),
        SommaEsenteBand(up_to=Decimal(20000), rate=Decimal("0.048")),
    ]
)


class TestSommaEsente:
    """Unit tests for somma_esente() (L. 207/2024 net bonus)."""

    def test_zero_income_returns_zero(self) -> None:
        """Zero income: benefit is zero."""
        assert somma_esente(Decimal(0), _SE_RULES) == Decimal(0)

    def test_negative_income_returns_zero(self) -> None:
        """Negative income: benefit is zero."""
        assert somma_esente(Decimal(-1), _SE_RULES) == Decimal(0)

    def test_first_band_mid(self) -> None:
        """Income 5 000 (first band, up_to 8 500): 5000 * 7.1% = 355.00."""
        assert somma_esente(Decimal(5000), _SE_RULES) == Decimal("355.00")

    def test_at_first_band_ceiling(self) -> None:
        """Income exactly 8 500: still first band. 8500 * 7.1% = 603.50."""
        assert somma_esente(Decimal(8500), _SE_RULES) == Decimal("603.50")

    def test_second_band_mid(self) -> None:
        """Income 12 000 (second band, up_to 15 000): 12000 * 5.3% = 636.00."""
        assert somma_esente(Decimal(12000), _SE_RULES) == Decimal("636.00")

    def test_at_second_band_ceiling(self) -> None:
        """Income exactly 15 000: still second band. 15000 * 5.3% = 795.00."""
        assert somma_esente(Decimal(15000), _SE_RULES) == Decimal("795.00")

    def test_third_band_mid(self) -> None:
        """Income 18 000 (third band, up_to 20 000): 18000 * 4.8% = 864.00."""
        assert somma_esente(Decimal(18000), _SE_RULES) == Decimal("864.00")

    def test_at_third_band_ceiling(self) -> None:
        """Income exactly 20 000: last band applies. 20000 * 4.8% = 960.00."""
        assert somma_esente(Decimal(20000), _SE_RULES) == Decimal("960.00")

    def test_above_ceiling_returns_zero(self) -> None:
        """Income above highest band ceiling: benefit is zero."""
        assert somma_esente(Decimal("20000.01"), _SE_RULES) == Decimal(0)

    def test_well_above_ceiling_returns_zero(self) -> None:
        """High income: benefit is zero."""
        assert somma_esente(Decimal(50000), _SE_RULES) == Decimal(0)

    def test_percentage_follows_the_annualised_income(self) -> None:
        """Circolare AdE 4/E of 16 May 2025, esempio 1: 2,000 EUR in 62 days.

        Annualised 2,000 / 62 * 365 = 11,774.19 (the circolare prints
        11.744,19), in the 8,500 to 15,000 band: 5.3% of the 2,000 EUR
        actually earned is 106 EUR.  On the unannualised income the rate
        would be 7.1% (142 EUR).
        """
        amount = somma_esente(Decimal(2000), _SE_RULES, eligible_work_days=62)
        assert amount == Decimal("106.000")

    def test_annualised_income_above_every_band_takes_the_last_rate(self) -> None:
        """12,000 EUR in 151 days: annualised 29,006.62, above 20,000.

        The reddito complessivo (12,000) is within the 20,000 EUR limit, so
        the credit is due at the rate for income above 15,000: 4.8% of
        12,000 = 576 EUR (L. 207/2024 art. 1 c. 4 lett. c) and c. 5).
        """
        amount = somma_esente(Decimal(12000), _SE_RULES, eligible_work_days=151)
        assert amount == Decimal("576.000")


class TestUlterioreDetrazioneProrata:
    """ulteriore_detrazione_lavoro() with eligible_work_days < 365."""

    def test_flat_band_prorata(self) -> None:
        """RC in (20000, 32000]: full_year=1000, part-year is proportionally less."""
        full = ulteriore_detrazione_lavoro(Decimal(25000), _UD_RULES)
        part = ulteriore_detrazione_lavoro(
            Decimal(25000), _UD_RULES, eligible_work_days=182
        )
        assert part < full
        assert part > Decimal(0)

    def test_taper_band_prorata(self) -> None:
        """RC in (32000, 40000]: tapered full-year is further scaled by days."""
        full = ulteriore_detrazione_lavoro(Decimal(36000), _UD_RULES)
        part = ulteriore_detrazione_lavoro(
            Decimal(36000), _UD_RULES, eligible_work_days=90
        )
        assert part < full
        assert part > Decimal(0)


class TestTrattamentoIntegrativoProrata:
    """trattamento_integrativo() with eligible_work_days < 365."""

    def test_low_band_prorata_max_amount_scaled(self) -> None:
        """RC <= 15000: max_amount is scaled by days/365.

        Full-year: irpef_gross (2300) > threshold (1955-75=1880) → max_amount 1200.
        Half-year (182d): prorata≈0.4986, seventy_five≈37.39, threshold≈940.61;
        irpef_gross (2300) > 940.61 → scaled max_amount (≈598).
        """
        full = trattamento_integrativo(
            Decimal(10000), Decimal(2300), Decimal(1955), Decimal(1955), _TI_RULES
        )
        part = trattamento_integrativo(
            Decimal(10000),
            Decimal(2300),
            Decimal(978),
            Decimal(978),
            _TI_RULES,
            eligible_work_days=182,
        )
        assert full == Decimal(1200)
        assert part < full
        assert part > Decimal(0)

    def test_mid_band_prorata(self) -> None:
        """RC in (15000, 28000]: bonus is capped by scaled max_amount."""
        part = trattamento_integrativo(
            Decimal(20000),
            Decimal(1500),
            Decimal(800),
            Decimal(2000),
            _TI_RULES,
            eligible_work_days=182,
        )
        assert part > Decimal(0)
        assert part <= Decimal(1200)

    def test_income_beyond_the_employment_removes_the_entitlement(self) -> None:
        """18,000 of employment and 2,500 of rent: reddito complessivo 20,500.

        Eligibility is on the reddito complessivo (L. 207/2024 art. 1 c. 4:
        "che hanno un reddito complessivo non superiore a 20.000 euro"),
        above the limit here, so nothing is due although the employment
        income alone (18,000) is within it.
        """
        amount = somma_esente(Decimal(18000), _SE_RULES, external_income=Decimal(2500))
        assert amount == Decimal(0)

    def test_income_beyond_the_employment_does_not_move_the_rate(self) -> None:
        """18,000 of employment and 1,000 of rent: 19,000, within 20,000.

        The amount applies the percentage "al reddito di lavoro dipendente
        del contribuente" (c. 4): 4.8% of 18,000 = 864.00, as without the
        rent.
        """
        amount = somma_esente(Decimal(18000), _SE_RULES, external_income=Decimal(1000))
        assert amount == Decimal("864.00")
