"""Tests for contribution rate resolution."""

from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.payroll.service._contributions_rates import resolve_rates
from tests.fixtures.contribution_rules import inps_year_rules
from tests.helpers import make_domestic_year_rules

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
        """Fixed-term: employer rate + fixed_term_additional_rate."""
        r = resolve_rates(inps_year_rules(), FixedTerm(), None)
        assert r.employer_rate == _D("0.3038")

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
