"""YearRules validators and the bundled 2026 tax rules loaded by load_year_rules.

The rate and band models YearRules is built from are tested in
``tests/unit/ccnl_engine/tax/domain/``.
"""

from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.tax.annual.loaders import load_year_rules
from ccnl_engine.tax.annual.loaders_resource import (
    read_inps_rules_raw,
    read_tax_rules_raw,
)
from ccnl_engine.tax.annual.models import YearRules, YearRulesRaw
from ccnl_engine.tax.contribution.models_tier import (
    InpsEmployeeTier,
)
from ccnl_engine.tax.contribution.rules_tier import (
    _assert_tier_integrity,
    _resolve_tier,
)
from ccnl_engine.tax.severance.models import TfrRules
from tests.unit.ccnl_engine.builders import (
    DOMESTIC_CONTRIBUTIONS,
    IRPEF_BRACKETS_2026,
)

# ---------------------------------------------------------------------------
# Minimal valid fixture helpers
# ---------------------------------------------------------------------------

_VALID_BRACKETS: list[dict[str, Any]] = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": "50000.00", "rate": "0.33"},
    {"up_to": None, "rate": "0.43"},
]

_VALID_INPS: dict[str, Any] = {
    "employee_rate": "0.0919",
    "employee_ivs_rate": "0.0919",
    "employer_rate": "0.2898",
    "employer_ivs_rate": "0.2381",
    "ceiling": None,
}

_VALID_APPRENTICE: dict[str, Any] = {
    "employee_rate": "0.0584",
    "employee_ivs_rate": "0.0584",
    "employer_rate_months_0_11": "0.0311",
    "employer_ivs_rate_months_0_11": "0.0150",
    "employer_rate_months_12_23": "0.0461",
    "employer_ivs_rate_months_12_23": "0.0300",
    "employer_rate_after": "0.1161",
    "employer_ivs_rate_after": "0.1000",
}


def _year_rules(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a minimal valid YearRules dict, with optional field overrides.

    Returns:
        A dict suitable for passing to YearRules.model_validate().
    """
    base: dict[str, Any] = {
        "year": 2026,
        "irpef_brackets": _VALID_BRACKETS,
        "fixed_term_additional_rate": "0.014",
        "fixed_term_renewal_increment": "0.005",
        "inps": _VALID_INPS,
        "apprentice": _VALID_APPRENTICE,
        "tfr": {"accrual_divisor": "13.5"},
    }
    if overrides:
        base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# YearRules — IRPEF bracket validators
# ---------------------------------------------------------------------------


class TestYearRulesIrpefBrackets:
    """YearRules validation for irpef_brackets."""

    def test_valid_three_brackets(self) -> None:
        """Three brackets with ascending up_to and open-ended last are valid."""
        yr = YearRules.model_validate(_year_rules())
        assert len(yr.irpef_brackets) == 3
        assert yr.irpef_brackets[-1].up_to is None

    def test_empty_brackets_raises(self) -> None:
        """An empty irpef_brackets list must raise ValidationError."""
        with pytest.raises(ValidationError, match="irpef_brackets must not be empty"):
            YearRules.model_validate(_year_rules({"irpef_brackets": []}))

    def test_non_last_bracket_open_ended_raises(self) -> None:
        """An intermediate bracket with up_to=None must raise ValidationError."""
        bad = [
            {"up_to": None, "rate": "0.23"},
            {"up_to": None, "rate": "0.43"},
        ]
        with pytest.raises(ValidationError, match="only the last irpef_bracket"):
            YearRules.model_validate(_year_rules({"irpef_brackets": bad}))

    def test_non_ascending_up_to_raises(self) -> None:
        """Non-ascending up_to values must raise ValidationError."""
        bad = [
            {"up_to": "50000.00", "rate": "0.23"},
            {"up_to": "28000.00", "rate": "0.33"},
            {"up_to": None, "rate": "0.43"},
        ]
        with pytest.raises(ValidationError, match="strictly ascending up_to"):
            YearRules.model_validate(_year_rules({"irpef_brackets": bad}))

    def test_last_bracket_not_open_ended_raises(self) -> None:
        """A last bracket with finite up_to must raise ValidationError."""
        bad = [
            {"up_to": "28000.00", "rate": "0.23"},
            {"up_to": "50000.00", "rate": "0.43"},
        ]
        with pytest.raises(
            ValidationError, match="last irpef_bracket must be unbounded"
        ):
            YearRules.model_validate(_year_rules({"irpef_brackets": bad}))

    def test_single_open_ended_bracket_valid(self) -> None:
        """A single unbounded bracket is valid (loop body never executes)."""
        single = [{"up_to": None, "rate": "0.23"}]
        yr = YearRules.model_validate(_year_rules({"irpef_brackets": single}))
        assert len(yr.irpef_brackets) == 1

    def test_two_brackets_second_open_ended_skips_ascending_check(self) -> None:
        """With two brackets, the ascending check is skipped for the last pair."""
        two = [
            {"up_to": "28000.00", "rate": "0.23"},
            {"up_to": None, "rate": "0.43"},
        ]
        yr = YearRules.model_validate(_year_rules({"irpef_brackets": two}))
        assert len(yr.irpef_brackets) == 2


# ---------------------------------------------------------------------------
# YearRules — 2026.json round-trip
# ---------------------------------------------------------------------------


class TestYearRules2026Json:
    """Validates that the 2026-terziario.json data file loads via load_year_rules."""

    def test_2026_json_loads(self) -> None:
        """load_year_rules(2026, terziario, 50) must return correct YearRules."""
        yr = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert yr.year == 2026
        assert len(yr.irpef_brackets) == 3
        assert yr.irpef_brackets[0].rate == Decimal("0.23")
        assert yr.irpef_brackets[1].rate == Decimal("0.33")
        assert yr.irpef_brackets[2].rate == Decimal("0.43")
        assert yr.inps is not None
        assert yr.inps.employee_rate == Decimal("0.0976")
        assert yr.inps.employer_rate == Decimal("0.3011")
        assert yr.inps.ceiling == Decimal("122295.00")
        assert yr.fixed_term_additional_rate == Decimal("0.014")
        assert yr.tfr.accrual_divisor == Decimal("13.5")
        assert yr.apprentice is not None
        assert yr.apprentice.employer_rate_after == Decimal("0.1274")
        assert yr.apprentice.employer_rate_months_0_11 == Decimal("0.1274")

    @pytest.mark.parametrize(
        ("headcount", "employee", "employer"),
        [
            (5, "0.0936", "0.2931"),
            (15, "0.0946", "0.2951"),
            (16, "0.0976", "0.3011"),
        ],
    )
    def test_terziario_tiers_add_fis_and_cigs(
        self, headcount: int, employee: str, employer: str
    ) -> None:
        """Terziario: FIS at every size, CIGS above 15 (INPS circ. 117/2022 all. 1).

        Employee 9.19 IVS + FIS 0.17 up to 5, 0.27 above, + CIGS 0.30 above
        15; employer 28.98 + FIS 0.33 up to 5, 0.53 above, + CIGS 0.60 above
        15 (D.Lgs. 148/2015 artt. 23 c. 1-bis, 29 c. 8, 33 c. 1).
        """
        yr = load_year_rules(2026, TaxSector.TERZIARIO, headcount)
        assert yr.inps is not None
        assert yr.inps.employee_rate == Decimal(employee)
        assert yr.inps.employer_rate == Decimal(employer)

    def test_small_firm_apprentice_rates(self) -> None:
        """Firms with at most 9 employees get the reduced apprentice rates.

        10% less 8.5 and 7 points (L. 296/2006 art. 1 c. 773) + NASpI 1.61%
        + the FIS employer share of an employer above five, 0.53% (INPS
        circ. 117/2022 all. 1).
        """
        yr = load_year_rules(2026, TaxSector.TERZIARIO, 9)
        assert yr.apprentice is not None
        assert yr.apprentice.employer_rate_months_0_11 == Decimal("0.0364")
        assert yr.apprentice.employer_rate_months_12_23 == Decimal("0.0514")
        assert yr.apprentice.employer_rate_after == Decimal("0.1214")

    def test_artigianato_category_rates(self) -> None:
        """Artigianato: lower employer rate for impiegati/quadri (kitech.it source)."""
        yr = load_year_rules(2026, TaxSector.ARTIGIANATO, 10)
        assert yr.inps is not None
        assert yr.inps.employer_rate_by_category == {
            "impiegato": Decimal("0.2471"),
            "quadro": Decimal("0.2471"),
        }

    def test_domestic_2026_loads(self) -> None:
        """load_year_rules(2026, LAVORO_DOMESTICO, 1) returns domestic_contributions."""
        yr = load_year_rules(2026, TaxSector.LAVORO_DOMESTICO, 1)
        assert yr.inps is None
        assert yr.apprentice is None
        assert yr.domestic_contributions is not None
        assert yr.domestic_contributions.weekly_hours_threshold == 24
        assert yr.domestic_contributions.hours_bracket.employee_per_hour == Decimal(
            "0.31"
        )

    def test_no_open_tier_raises(self) -> None:
        """_assert_tier_integrity raises when no open tier is present."""
        tiers = [
            InpsEmployeeTier(
                max_employees=10, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            )
        ]
        with pytest.raises(DataIntegrityError, match="exactly one open tier"):
            _assert_tier_integrity(tiers, "employee")

    def test_no_open_tier_covered_headcount_still_raises(self) -> None:
        """_assert_tier_integrity raises even when headcount fits a bounded tier."""
        tiers = [
            InpsEmployeeTier(
                max_employees=10, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            )
        ]
        # Without the fix, headcount=5 would succeed; now it must fail
        # because the structural defect (no open band) is caught up front.
        with pytest.raises(DataIntegrityError, match="exactly one open tier"):
            _resolve_tier(tiers, 5, "employee")

    def test_single_open_tier_accepted(self) -> None:
        """_assert_tier_integrity accepts a list with exactly one open tier."""
        tiers = [
            InpsEmployeeTier(
                max_employees=15, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            ),
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.10"), ivs_rate=Decimal("0.09")
            ),
        ]
        # Must not raise; verifies the happy path.
        _assert_tier_integrity(tiers, "employee")

    def test_multiple_open_tiers_raises(self) -> None:
        """_assert_tier_integrity raises when more than one open tier exists."""
        tiers = [
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            ),
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.10"), ivs_rate=Decimal("0.09")
            ),
        ]
        with pytest.raises(DataIntegrityError, match=r"exactly one open tier"):
            _assert_tier_integrity(tiers, "employee")

    def test_duplicate_max_employees_raises(self) -> None:
        """_assert_tier_integrity raises if max_employees values are duplicated."""
        tiers = [
            InpsEmployeeTier(
                max_employees=15, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            ),
            InpsEmployeeTier(
                max_employees=15, rate=Decimal("0.10"), ivs_rate=Decimal("0.09")
            ),
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.11"), ivs_rate=Decimal("0.09")
            ),
        ]
        with pytest.raises(DataIntegrityError, match="duplicate max_employees=15"):
            _assert_tier_integrity(tiers, "employee")

    def test_tfr_rules(self) -> None:
        """TfrRules accrual_divisor is parsed as Decimal."""
        tfr = TfrRules(accrual_divisor=Decimal("13.5"))
        assert tfr.accrual_divisor == Decimal("13.5")

    def test_tfr_rules_zero_divisor_raises(self) -> None:
        """TfrRules rejects accrual_divisor=0."""
        with pytest.raises(ValidationError, match="greater than 0"):
            TfrRules(accrual_divisor=Decimal(0))

    def test_tfr_rules_negative_divisor_raises(self) -> None:
        """TfrRules rejects negative accrual_divisor."""
        with pytest.raises(ValidationError, match="greater than 0"):
            TfrRules(accrual_divisor=Decimal(-1))


_RAW_BASE: dict[str, Any] = {
    "year": 2026,
    "sector": "terziario",
    "irpef_brackets": IRPEF_BRACKETS_2026,
    "fixed_term_additional_rate": "0.014",
    "fixed_term_renewal_increment": "0.005",
    "tfr": {"accrual_divisor": "13.5"},
}


class TestYearRulesRawContributionModel:
    """YearRulesRaw validator: must have inps+apprentice or domestic_contributions."""

    def test_missing_both_raises(self) -> None:
        """Neither inps+apprentice nor domestic_contributions → ValidationError."""
        with pytest.raises(ValidationError, match="domestic_contributions"):
            YearRulesRaw.model_validate(_RAW_BASE)

    def test_both_models_raises(self) -> None:
        """Having both standard and domestic models is rejected."""
        # Merge a real standard-sector tax + inps dict (guaranteed parseable),
        # then also inject domestic_contributions to trigger the
        # mutual-exclusion guard.
        tax = read_tax_rules_raw(2026, TaxSector.TERZIARIO)
        inps = read_inps_rules_raw(2026, TaxSector.TERZIARIO)
        both = {**tax, **inps, "domestic_contributions": DOMESTIC_CONTRIBUTIONS}
        with pytest.raises(ValidationError, match="mutually exclusive"):
            YearRulesRaw.model_validate(both)

    def test_inps_without_apprentice_raises(self) -> None:
        """'inps' present without 'apprentice' must raise ValidationError."""
        inps = read_inps_rules_raw(2026, TaxSector.TERZIARIO)
        # Build a base with 'inps' but no 'apprentice'.
        data = {**_RAW_BASE, "inps": inps["inps"]}
        with pytest.raises(ValidationError, match="both absent"):
            YearRulesRaw.model_validate(data)

    def test_sector_file_cannot_carry_the_somma_esente(self) -> None:
        """The somma esente is read only from its own year file.

        L. 207/2024 art. 1 c. 4 sets it for every employee, whatever the
        sector, so a sector file holding a copy is rejected.
        """
        tax = read_tax_rules_raw(2026, TaxSector.TERZIARIO)
        inps = read_inps_rules_raw(2026, TaxSector.TERZIARIO)
        bands = [{"up_to": "8500", "rate": "0.071"}]
        with pytest.raises(ValidationError, match="somma_esente"):
            YearRulesRaw.model_validate({
                **tax,
                **inps,
                "somma_esente": {"bands": bands},
            })

    def test_apprentice_without_inps_raises(self) -> None:
        """'apprentice' present without 'inps' must raise ValidationError."""
        inps_raw = read_inps_rules_raw(2026, TaxSector.TERZIARIO)
        data = {**_RAW_BASE, "apprentice": inps_raw["apprentice"]}
        with pytest.raises(ValidationError, match="both absent"):
            YearRulesRaw.model_validate(data)


class TestYearRulesContributionModel:
    """YearRules validator mirrors YearRulesRaw contribution-model checks."""

    def test_inps_without_apprentice_raises(self) -> None:
        """'inps' without 'apprentice' in YearRules must raise ValidationError."""
        with pytest.raises(ValidationError, match="both absent"):
            YearRules.model_validate(_year_rules({"apprentice": None}))

    def test_no_model_raises(self) -> None:
        """Neither model in YearRules must raise ValidationError."""
        with pytest.raises(ValidationError, match="standard model"):
            YearRules.model_validate(_year_rules({"inps": None, "apprentice": None}))

    def test_standard_and_domestic_raises(self) -> None:
        """Mixing standard and domestic in YearRules must raise ValidationError."""
        with pytest.raises(ValidationError, match="mutually exclusive"):
            YearRules.model_validate(
                _year_rules({"domestic_contributions": DOMESTIC_CONTRIBUTIONS})
            )


# ---------------------------------------------------------------------------
# fixed_term_additional_rate: PercentageRate constraint
# ---------------------------------------------------------------------------


class TestFixedTermAdditionalRate:
    """YearRulesRaw and YearRules reject negative / >1 fixed_term_additional_rate."""

    def test_negative_rate_in_year_rules_raises(self) -> None:
        """Negative fixed_term_additional_rate must raise ValidationError."""
        with pytest.raises(ValidationError):
            YearRules.model_validate(
                _year_rules({"fixed_term_additional_rate": "-0.01"})
            )

    def test_rate_above_one_in_year_rules_raises(self) -> None:
        """fixed_term_additional_rate > 1 must raise ValidationError."""
        with pytest.raises(ValidationError):
            YearRules.model_validate(_year_rules({"fixed_term_additional_rate": "1.5"}))

    def test_zero_rate_accepted(self) -> None:
        """fixed_term_additional_rate = 0 (PA sector) must be accepted."""
        r = YearRules.model_validate(
            _year_rules({"fixed_term_additional_rate": "0.000"})
        )
        assert r.fixed_term_additional_rate == Decimal(0)


class TestYearRules2026SectorRates:
    """Sector rates of the 2026 INPS files that differ by headcount or category."""

    @pytest.mark.parametrize(
        ("sector", "headcount", "first", "second", "after", "employee"),
        [
            # 10% + NASpI 1.61% + CIGO 1.70%, + CIGS 0.60% / 0.30% above 15,
            # CIGO 2.00% above 50 (D.Lgs. 148/2015 art. 13 c. 1 lett. a-b).
            (TaxSector.INDUSTRIA, 9, "0.0481", "0.0631", "0.1331", "0.0584"),
            (TaxSector.INDUSTRIA, 15, "0.1331", "0.1331", "0.1331", "0.0584"),
            (TaxSector.INDUSTRIA, 50, "0.1391", "0.1391", "0.1391", "0.0614"),
            (TaxSector.INDUSTRIA, 51, "0.1421", "0.1421", "0.1421", "0.0614"),
            # FIS 0.33% / 0.17% up to 5, 0.53% / 0.27% above (circ. 117/2022).
            (TaxSector.TERZIARIO, 5, "0.0344", "0.0494", "0.1194", "0.0601"),
            (TaxSector.TERZIARIO, 15, "0.1214", "0.1214", "0.1214", "0.0611"),
            (TaxSector.TERZIARIO, 16, "0.1274", "0.1274", "0.1274", "0.0641"),
            # Assimpredil ANCE tables 1/2026 and 2/2026: CIGO edile 4.70%.
            (TaxSector.EDILIZIA, 9, "0.0781", "0.0931", "0.1631", "0.0584"),
            (TaxSector.EDILIZIA, 15, "0.1631", "0.1631", "0.1631", "0.0584"),
            (TaxSector.EDILIZIA, 16, "0.1691", "0.1691", "0.1691", "0.0614"),
        ],
    )
    def test_apprentice_rates_add_the_wage_integration_shares(
        self,
        sector: TaxSector,
        headcount: int,
        first: str,
        second: str,
        after: str,
        employee: str,
    ) -> None:
        """Apprentices pay CIGO, CIGS or FIS since 2022 (INPS circ. 76/2022).

        The shares are not IVS: the IVS portions stay the statutory ones.
        """
        yr = load_year_rules(2026, sector, headcount)
        assert yr.apprentice is not None
        assert yr.apprentice.employer_rate_months_0_11 == Decimal(first)
        assert yr.apprentice.employer_rate_months_12_23 == Decimal(second)
        assert yr.apprentice.employer_rate_after == Decimal(after)
        assert yr.apprentice.employee_rate == Decimal(employee)
        assert yr.apprentice.employee_ivs_rate == Decimal("0.0584")
        assert yr.apprentice.employer_ivs_rate_after == Decimal("0.1000")

    @pytest.mark.parametrize(
        ("headcount", "operai", "impiegati"),
        [(15, "0.3368", "0.2846"), (50, "0.3428", "0.2906"), (51, "0.3428", "0.2936")],
    )
    def test_edilizia_rates_by_category(
        self, headcount: int, operai: str, impiegati: str
    ) -> None:
        """Edilizia: Assimpredil ANCE tables 1/2026 and 2/2026.

        Operai pay the CIGO edile 4.70% and malattia 2.22%; impiegati and
        quadri the CIGO 1.70% (2.00% above 50); dirigenti no CIGO.
        """
        yr = load_year_rules(2026, TaxSector.EDILIZIA, headcount)
        assert yr.inps is not None
        assert yr.inps.employer_rate == Decimal(operai)
        assert yr.inps.employer_rate_by_category == {
            "impiegato": Decimal(impiegati),
            "quadro": Decimal(impiegati),
            "dirigente": Decimal("0.2696"),
        }

    def test_credito_operai_rate(self) -> None:
        """Credito: operai (salariati) 38.50% - 9.19% = 29.31% with malattia."""
        yr = load_year_rules(2026, TaxSector.CREDITO, 100)
        assert yr.inps is not None
        assert yr.inps.employer_rate == Decimal("0.2676")
        assert yr.inps.employer_rate_by_category == {"operaio": Decimal("0.2931")}
