"""Tests for contribution rate resolution."""

from decimal import Decimal

import pytest

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.payroll.contribution.rules_rate import resolve_rates
from ccnl_engine.payroll.employment.inputs import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.payroll.employment.inputs_fixed_term import NaspiExclusion
from tests.unit.ccnl_engine.builders import make_domestic_year_rules
from tests.unit.ccnl_engine.payroll.contribution.builders_contribution_rules import (
    inps_year_rules,
)

_D = Decimal
_ZERO = Decimal(0)


class TestResolveRates:
    """resolve_rates() by employment type and worker category."""

    def test_permanent(self) -> None:
        """Permanent: sector rates unchanged."""
        r = resolve_rates(inps_year_rules(), Permanent(), None)
        assert (r.employee_rate, r.employer_rate) == (_D("0.0919"), _D("0.2898"))

    def test_permanent_category_override(self) -> None:
        """Category-specific employer rate applies when the category matches."""
        assert resolve_rates(
            inps_year_rules(), Permanent(), WorkerCategory.IMPIEGATO
        ).employer_rate == _D("0.2471")
        assert resolve_rates(
            inps_year_rules(), Permanent(), WorkerCategory.OPERAIO
        ).employer_rate == _D("0.2898")

    def test_fixed_term_adds_naspi(self) -> None:
        """Fixed term renewed once: employer rate + 1.4% + 0.5% (L. 92/2012 c. 28)."""
        contract = FixedTerm(renewals=1, naspi_exclusion=NaspiExclusion.NONE)
        r = resolve_rates(inps_year_rules(), contract, None)
        assert r.employer_rate == _D("0.2898") + _D("0.014") + _D("0.005")
        assert r.employer_ivs_rate == _D("0.2381")

    def test_excluded_fixed_term_keeps_the_permanent_rates(self) -> None:
        """A replacement worker (c. 29 lett. a) pays the permanent rates."""
        contract = FixedTerm(naspi_exclusion=NaspiExclusion.REPLACEMENT)
        assert resolve_rates(inps_year_rules(), contract, None) == resolve_rates(
            inps_year_rules(), Permanent(), None
        )

    def test_fixed_term_takes_the_fixed_term_rate_of_its_category(self) -> None:
        """An operaio agricolo a tempo determinato owes no Fondo garanzia TFR.

        INPS circ. 43/2026: OTI 25.453%, OTD 25.253% net of INAIL; the
        operai agricoli are outside L. 92/2012 art. 2, so no surcharge.
        """
        rules = inps_year_rules()
        assert rules.inps is not None
        inps = rules.inps.model_copy(
            update={
                "employer_fixed_term_rate_by_category": {
                    WorkerCategory.OPERAIO: _D("0.25253")
                },
                "employer_rate": _D("0.25453"),
            }
        )
        agricoltura = rules.model_copy(
            update={
                "inps": inps,
                "fixed_term_exempt_categories": frozenset({WorkerCategory.OPERAIO}),
            }
        )
        contract = FixedTerm(naspi_exclusion=NaspiExclusion.NONE)
        assert resolve_rates(
            agricoltura, contract, WorkerCategory.OPERAIO
        ).employer_rate == _D("0.25253")
        assert resolve_rates(
            agricoltura, Permanent(), WorkerCategory.OPERAIO
        ).employer_rate == _D("0.25453")

    def test_apprentice_by_months(self) -> None:
        """Apprentice: statutory employee rate, employer rate stepping by months."""
        rules = inps_year_rules()
        assert resolve_rates(rules, Apprentice(months_elapsed=0), None) == (
            resolve_rates(rules, Apprentice(months_elapsed=11), None)
        )
        assert resolve_rates(
            rules, Apprentice(months_elapsed=0), None
        ).employee_rate == (_D("0.0584"))
        assert [
            resolve_rates(
                rules, Apprentice(months_elapsed=m), WorkerCategory.IMPIEGATO
            ).employer_rate
            for m in (0, 12, 24)
        ] == [_D("0.0311"), _D("0.0461"), _D("0.1161")]


class TestResolveRatesGuard:
    """resolve_rates() raises when rules.inps or rules.apprentice is None."""

    def test_none_inps_raises(self) -> None:
        """Domestic rules (inps=None) must raise TypeError from resolve_rates."""
        domestic_rules = make_domestic_year_rules()
        with pytest.raises(TypeError, match="resolve_rates requires standard INPS"):
            resolve_rates(domestic_rules, Permanent(), None)
