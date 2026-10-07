"""Bundled 2026 surtax tables against the MEF Dipartimento delle Finanze data.

Regional expected values are computed by hand from the MEF 2026 page of each
region (``addregirpef.php?reg=NN&anno=2026``, retrieved on 2026-09-27);
municipal ones from the MEF ``elenco generale`` CSV of 2026, 2025 and 2024
(``nuova_addcomirpef/download/download.php?anno=YYYY``, retrieved on
2026-10-07) and the MEF page of each municipality
(``nuova_addcomirpef/risultato.htm?...&cc=<code>&anno=YYYY``).  Brackets
are marginal: each rate applies to the slice of income inside its band.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.jurisdiction import REGION_CODES
from ccnl_engine.payroll.service.fiscal_surtax import compute_surtax
from ccnl_engine.provenance.domain.chain import ProvenanceStatus
from ccnl_engine.tax.service.surtax_loaders import load_surtax_rules

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.surtax_rules import SurtaxRules

_D = Decimal
_MEF_REGIONAL = (
    "https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/"
    "fiscalitalocale/addregirpef/addregirpef.php?reg="
)


@pytest.fixture(scope="module")
def rules() -> SurtaxRules:
    """Load the bundled surtax tables once for the module.

    Returns:
        The 2026 regional and municipal tables.
    """
    return load_surtax_rules(2026)


def _regional(rules: SurtaxRules, code: str, income: str) -> tuple[Decimal, str]:
    outcome = compute_surtax(
        _D(income), rules, regione=code, comune_belfiore=None, irpef_due=_D(1)
    )
    (decision,) = outcome.decisions
    assert decision.amount is not None
    return decision.amount, decision.reason_code


class TestRegionalRows:
    """Every row of the regional table matches its MEF 2026 page."""

    def test_rows_are_the_region_codes(self, rules: SurtaxRules) -> None:
        """One row per region and autonomous province, keyed by its name."""
        assert set(rules.regionale) == set(REGION_CODES.values())

    def test_every_row_cites_its_mef_page(self, rules: SurtaxRules) -> None:
        """Each row is ``derived`` from its own MEF page, with the access date."""
        for name, entry in rules.regionale.items():
            record = entry.provenance
            assert record is not None, name
            assert record.status is ProvenanceStatus.DERIVED, name
            assert record.location is not None, name
            url = record.location.source_document.url
            assert url.startswith(_MEF_REGIONAL), name
            assert "&anno=2026" in url, name
            assert record.location.source_document.published_on is not None, name
            assert record.extraction is not None, name
            assert record.extraction.extraction_timestamp.date().isoformat() == (
                "2026-09-27"
            )

    def test_table_is_derived_from_mef(self, rules: SurtaxRules) -> None:
        """The table record and ruleset name the MEF as official source."""
        assert rules.regional_provenance is not None
        assert rules.regional_provenance.status is ProvenanceStatus.DERIVED
        assert rules.regional_ruleset is not None
        assert rules.regional_ruleset.source.startswith("https://www1.finanze.gov.it/")


@pytest.mark.parametrize(
    ("code", "income", "expected"),
    [
        # Veneto (reg=21): 1.23% aliquota unica. 30,000 x 1.23% = 369.00.
        ("IT-34", "30000", "369.00"),
        # Lombardia (reg=10): 1.23 / 1.58 / 1.72 / 1.73%.
        # 15,000 x 1.23% = 184.50; 13,000 x 1.58% = 205.40;
        # 2,000 x 1.72% = 34.40; total 424.30.
        ("IT-25", "30000", "424.30"),
        # Toscana (reg=17): 1.42 / 1.43 / 3.32 / 3.33%.
        # 15,000 x 1.42% = 213.00; 13,000 x 1.43% = 185.90;
        # 2,000 x 3.32% = 66.40; total 465.30.
        ("IT-52", "30000", "465.30"),
        # Emilia-Romagna (reg=06): 1.33 / 1.93 / 2.78 / 3.33%.
        # 199.50 + 250.90 + 55.60 = 506.00.
        ("IT-45", "30000", "506.00"),
        # Piemonte (reg=13): 1.62 / 2.68 / 3.31 / 3.33%.
        # 243.00 + 348.40 + 66.20 = 657.60.
        ("IT-21", "30000", "657.60"),
        # Molise (reg=12, delibera published 19-06-2026): 2.03 / 2.23 / 3.63%.
        # 304.50 + 289.90 + 72.60 = 667.00.
        ("IT-67", "30000", "667.00"),
        # Puglia (reg=14, delibera published 29-05-2026): 1.33 / 2.13 / 3.23%.
        # 199.50 + 276.90 + 64.60 = 541.00.
        ("IT-75", "30000", "541.00"),
        # Abruzzo (reg=01): 1.67% up to 28,000, 2.87% up to 50,000.
        # 467.60 + 57.40 = 525.00.
        ("IT-65", "30000", "525.00"),
        # Lombardia above the last band: 184.50 + 205.40 + 22,000 x 1.72%
        # (378.40) + 50,000 x 1.73% (865.00) = 1,633.30.
        ("IT-25", "100000", "1633.30"),
    ],
)
def test_bracket_rows(
    rules: SurtaxRules, code: str, income: str, expected: str
) -> None:
    """Marginal brackets of the MEF 2026 pages, computed by hand."""
    assert _regional(rules, code, income) == (_D(expected), "table_applied")


@pytest.mark.parametrize(
    ("code", "income", "expected", "reason"),
    [
        # Friuli-Venezia Giulia (reg=07): 0.70% on the whole income up to
        # 15,000, 1.23% on the whole income above.
        # 15,000 x 0.70% = 105.00.
        ("IT-36", "15000", "105.00", "table_applied"),
        # 15,000.01 x 1.23% = 184.500123, rounded 184.50.
        ("IT-36", "15000.01", "184.50", "table_applied"),
        # 30,000 x 1.23% = 369.00.
        ("IT-36", "30000", "369.00", "table_applied"),
        # Lazio (reg=08): 1.73% on the whole income up to 28,000.
        # 28,000 x 1.73% = 484.40.
        ("IT-62", "28000", "484.40", "table_applied"),
        # Above 28,000: 15,000 x 1.73% = 259.50 and 15,000 x 3.33% = 499.50,
        # 759.00, less the 60 euro detrazione (28,001 to 30,000): 699.00.
        ("IT-62", "30000", "699.00", "table_applied"),
        # 30,500: 259.50 + 15,500 x 3.33% (516.15) = 775.65, no detrazione.
        ("IT-62", "30500", "775.65", "table_applied"),
        # Umbria (reg=19): without the increases up to 28,000 the rate is
        # 1.73 - 0.50 = 3.02 - 1.79 = 1.23% on the whole income.
        # 28,000 x 1.23% = 344.40.
        ("IT-55", "28000", "344.40", "table_applied"),
        # 30,000: 15,000 x 1.73% = 259.50; 13,000 x 3.02% = 392.60;
        # 2,000 x 3.12% = 62.40; 714.50 less 150 (28,001 to 50,000) = 564.50.
        ("IT-55", "30000", "564.50", "table_applied"),
        # Provincia di Trento (reg=18): a deduction of 30,000 euro for a
        # taxable income up to 30,000 leaves no base.
        ("IT-TN", "30000", "0", "below_exemption_threshold"),
        # 30,000.01: 1.23% up to 50,000 on the whole: 369.000123 = 369.00.
        ("IT-TN", "30000.01", "369.00", "table_applied"),
        # Valle d'Aosta (reg=20): exempt up to 15,000, then 1.23% on all.
        ("IT-23", "15000", "0", "below_exemption_threshold"),
        # 20,000 x 1.23% = 246.00.
        ("IT-23", "20000", "246.00", "table_applied"),
        # Provincia di Bolzano (reg=03): 1.23% up to 50,000, 1.73% above;
        # detrazione a) 430.50 up to 90,000; b) 125 x (income - 50,000) /
        # 25,000, at most 125.
        # 30,000 x 1.23% = 369.00 less 430.50: floored at 0.
        ("IT-BZ", "30000", "0.00", "table_applied"),
        # 60,000: 615.00 + 10,000 x 1.73% = 788.00; less 430.50 and
        # 125 x 10,000 / 25,000 = 50.00: 307.50.
        ("IT-BZ", "60000", "307.50", "table_applied"),
        # 100,000: 615.00 + 865.00 = 1,480.00; no a) above 90,000;
        # b) capped at 125.00: 1,355.00.
        ("IT-BZ", "100000", "1355.00", "table_applied"),
    ],
)
def test_income_only_provisions(
    rules: SurtaxRules, code: str, income: str, expected: str, reason: str
) -> None:
    """Whole-income rates, exemptions and detrazioni of the MEF pages."""
    assert _regional(rules, code, income) == (_D(expected), reason)


class TestMunicipalRows:
    """Municipal rows against the MEF CSV lists of 2026 and 2025."""

    def test_table_holds_the_rates_of_the_tax_year(self, rules: SurtaxRules) -> None:
        """The table is of 2026; rows without a 2026 delibera say so."""
        assert rules.comunale_rates_are_advance is False
        assert rules.municipal_provenance is not None
        assert rules.municipal_provenance.status is ProvenanceStatus.DERIVED

    def test_single_rate_with_exemption(self, rules: SurtaxRules) -> None:
        """A006 Abbadia San Salvatore, 2026 list (published 22/01/2026).

        CSV: ``ALIQUOTA`` 0 "Esenzione per redditi imponibili fino a euro
        12.000,00"; ``ALIQUOTA_2`` ",6" "Aliquota unica"; ``FLAG_NUOVA`` 2,
        ``IMPORTO_ESENTE`` 12000.
        """
        entry = rules.comunale["A006"]
        assert [(b.up_to, b.rate) for b in entry.brackets] == [(None, _D("0.006"))]
        assert entry.exemption_threshold == _D("12000")
        assert entry.rates_year is None

    def test_single_rate(self, rules: SurtaxRules) -> None:
        """G273 Palermo, 2026 list (published 22/07/2026).

        CSV: ``ALIQUOTA`` "1,03" "Aliquota unica"; ``FLAG_NUOVA`` 1.
        30,000 x 1.03% = 309.00, final.
        """
        outcome = compute_surtax(
            _D(30000), rules, regione=None, comune_belfiore="G273", irpef_due=_D(1)
        )
        (decision,) = outcome.decisions
        assert (decision.reason_code, decision.amount) == (
            "table_applied",
            _D("309.00"),
        )
        assert decision.status is CalculationStatus.FINAL

    def test_brackets_with_exemption(self, rules: SurtaxRules) -> None:
        """E965 Marnate, 2026 list (published 14/09/2026, FLAG_NUOVA 0).

        CSV: "0,76" up to 15000,00; ",77" 15000,01 to 28000,00; ",78"
        28000,01 to 50000,00; ",8" over 50000,00; "Esenzione per reddito
        imponibile fino A euro 13000,00".
        30,000: 15,000 x 0.76% = 114.00; 13,000 x 0.77% = 100.10;
        2,000 x 0.78% = 15.60; total 229.70.
        """
        entry = rules.comunale["E965"]
        assert [(b.up_to, b.rate) for b in entry.brackets] == [
            (_D("15000"), _D("0.0076")),
            (_D("28000"), _D("0.0077")),
            (_D("50000"), _D("0.0078")),
            (None, _D("0.008")),
        ]
        assert entry.exemption_threshold == _D("13000")
        outcome = compute_surtax(
            _D(30000), rules, regione=None, comune_belfiore="E965", irpef_due=_D(1)
        )
        assert outcome.municipal == _D("229.70")

    def test_row_without_2026_delibera_carries_2025(self, rules: SurtaxRules) -> None:
        """H501 Roma: ``0*`` in the 2026 list; 2025 list (published 24/01/2025).

        2025 CSV: 0 "Esenzione per redditi imponibili fino a euro
        14.000,00"; ",9" "Aliquota unica"; ``IMPORTO_ESENTE`` 14000.
        30,000 x 0.9% = 270.00, provisional on the 2025 rates.
        """
        entry = rules.comunale["H501"]
        assert entry.rates_year == 2025
        assert entry.provenance is not None
        assert entry.provenance.status is ProvenanceStatus.ASSUMED
        outcome = compute_surtax(
            _D(30000), rules, regione=None, comune_belfiore="H501", irpef_due=_D(1)
        )
        (decision,) = outcome.decisions
        assert (decision.reason_code, decision.amount) == (
            "prior_year_rates_applied",
            _D("270.00"),
        )
        assert decision.inputs["rates_year"] == "2025"
        assert decision.status is CalculationStatus.PROVISIONAL

    def test_category_exemptions_are_kept_as_published(
        self, rules: SurtaxRules
    ) -> None:
        """B950 Cascina, 2026 list (published 18/09/2026, FLAG_NUOVA 6).

        The exemptions for lavoro dipendente and pensioni up to 12,000 euro
        and other incomes up to 11,000 are not computed; the row keeps them.
        """
        entry = rules.comunale["B950"]
        assert len(entry.specific_exemptions) == 2
        assert entry.exemption_threshold == 0

    def test_every_municipality_of_the_list_has_a_row(self, rules: SurtaxRules) -> None:
        """The 2026 list has 7,897 municipalities; one has no rates to read.

        M439 Castegnero Nanto is ``0*`` in 2026 and absent from the 2025
        list (created by merging Castegnero, 0.65%, and Nanto, 0.75%): its
        code is unknown to the table rather than taxed at 0.
        """
        assert len(rules.comunale) == 7896
        assert "M439" not in rules.comunale

    def test_merged_municipality_is_not_computed(self, rules: SurtaxRules) -> None:
        """M439 Castegnero Nanto: no amount and an incomplete issue, never 0."""
        outcome = compute_surtax(
            _D(30000), rules, regione=None, comune_belfiore="M439", irpef_due=_D(1)
        )
        (decision,) = outcome.decisions
        assert decision.amount is None
        assert decision.status is CalculationStatus.INCOMPLETE
        assert [issue.code for issue in outcome.issues] == ["municipal_surtax_unknown"]

    def test_brackets_of_a_2026_delibera(self, rules: SurtaxRules) -> None:
        """F430 Montasola, delibera n. 5 del 28-02-2026 (published 30-09-2026).

        MEF page: 0.2% up to 15,000; 0.4% to 28,000; 0.6% to 50,000; 0.8%
        above; exempt up to 8,500.  60,000: 15,000 x 0.2% = 30.00;
        13,000 x 0.4% = 52.00; 22,000 x 0.6% = 132.00; 10,000 x 0.8% =
        80.00; total 294.00 (the 2025 flat 0.8% gave 480.00).
        """
        outcome = compute_surtax(
            _D(60000), rules, regione=None, comune_belfiore="F430", irpef_due=_D(1)
        )
        (decision,) = outcome.decisions
        assert (decision.reason_code, decision.amount) == (
            "table_applied",
            _D("294.00"),
        )
        assert rules.comunale["F430"].exemption_threshold == _D("8500")

    @pytest.mark.parametrize(
        ("code", "expected", "rates_year"),
        [
            # B097 Bova: 2026 delibera n. 7 (0.8%) "atto oltre termine -
            # aliquote inapplicabili per il 2026"; 2025 delibera n. 05 del
            # 28-03-2025, 0.5%: 30,000 x 0.5% = 150.00.
            ("B097", "150.00", "2025"),
            # L676 Varco Sabino: no 2026 delibera; the 2025 one (0.8%) is
            # "inapplicabile per il 2025"; 2024 delibera n. 9, 0.4%:
            # 30,000 x 0.4% = 120.00.
            ("L676", "120.00", "2024"),
        ],
    )
    def test_inapplicable_delibera_keeps_the_rates_in_force(
        self, rules: SurtaxRules, code: str, expected: str, rates_year: str
    ) -> None:
        """A delibera adopted after the deadline does not change the rates."""
        outcome = compute_surtax(
            _D(30000), rules, regione=None, comune_belfiore=code, irpef_due=_D(1)
        )
        (decision,) = outcome.decisions
        assert (decision.reason_code, decision.amount) == (
            "prior_year_rates_applied",
            _D(expected),
        )
        assert decision.inputs["rates_year"] == rates_year
