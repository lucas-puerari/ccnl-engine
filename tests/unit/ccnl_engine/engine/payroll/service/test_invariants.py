"""Property-based tests for payroll computation invariants.

Covers five economic/actuarial invariants using Hypothesis:

1. Monotonicity — gross_annual increases → net_annual never decreases.
2. Part-time scaling — net_annual at 50% < net_annual at 100%.
3. INPS isolation — a ``contribution_relevant=False`` supplement does not
   change the INPS contribution base.
4. TFR isolation — a ``tfr_relevant=False`` supplement does not change
   tfr_annual.
5. Surtax isolation — changing the regional surtax rate does not alter
   irpef_net or inps_employee_annual.

All five tests use in-memory CCNL and tax-rules fixtures (no I/O).
Loaders are patched with ``unittest.mock.patch``; monkeypatch is avoided
because Hypothesis ``@given`` tests cannot use pytest fixtures directly.
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

from hypothesis import given, settings
from hypothesis import strategies as st

from ccnl_engine.engine.contract.domain.ccnl import SupplementaryAllowance
from ccnl_engine.engine.payroll.domain.scenario import (
    Jurisdiction,
    PayrollScenario,
)
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.primitives import Bracket
from ccnl_engine.engine.surtax.domain.rules import (
    RegionaleEntry,
    SurtaxRules,
)
from tests.helpers import make_minimal_ccnl, make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import _req

# ---------------------------------------------------------------------------
# Module-level shared fixtures (built once, reused across all @given calls)
# ---------------------------------------------------------------------------

_CCNL = make_minimal_ccnl()
_RULES = make_year_rules()
_REF_DATE_YEAR = 2026

_PATCH_CCNL = "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl"
_PATCH_RULES = "ccnl_engine.engine.payroll.service.orchestrator.load_year_rules"
_PATCH_SURTAX = "ccnl_engine.engine.payroll.service.orchestrator.load_surtax_rules"

# ---------------------------------------------------------------------------
# Shared strategies
# ---------------------------------------------------------------------------

_ral_st = st.integers(min_value=15_000, max_value=200_000).map(Decimal)
_allowance_st = st.integers(min_value=0, max_value=5_000).map(Decimal)
_seniority_st = st.integers(min_value=0, max_value=10)
_rate_st = st.decimals(
    min_value=Decimal("0.00"),
    max_value=Decimal("0.05"),
    places=4,
    allow_nan=False,
    allow_infinity=False,
)

# ---------------------------------------------------------------------------
# Shared builder helpers
# ---------------------------------------------------------------------------


def _surtax_with_rate(rate: Decimal) -> SurtaxRules:
    """Build a minimal SurtaxRules with one flat-rate region and no comunale.

    Returns:
        A :class:`SurtaxRules` with a single flat-rate region.
    """
    return SurtaxRules(
        year=_REF_DATE_YEAR,
        regionale={
            "TestRegione": RegionaleEntry(brackets=[Bracket(up_to=None, rate=rate)])
        },
        comunale={},
    )


def _scenario_with_ral(ral: Decimal) -> PayrollScenario:
    """Return a level-4 scenario with an explicit RAL override.

    Returns:
        A :class:`PayrollScenario` using *ral* as the annual gross.
    """
    return _req(level_code="4", negotiated_ral=ral, seniority_count=0)


def _scenario_with_supplement(
    monthly: Decimal,
    *,
    contribution_relevant: bool = True,
    tfr_relevant: bool = True,
) -> PayrollScenario:
    """Return a level-4 scenario with one caller-supplied supplementary allowance.

    Returns:
        A :class:`PayrollScenario` carrying the given allowance.
    """
    allowance = SupplementaryAllowance(
        code="TEST-SUPP",
        description="Test supplement",
        monthly=monthly,
        contribution_relevant=contribution_relevant,
        tfr_relevant=tfr_relevant,
    )
    return _req(
        level_code="4",
        seniority_count=0,
        second_level_allowances=(allowance,),
    )


def _scenario_with_jurisdiction(region: str) -> PayrollScenario:
    """Return a level-4 scenario with fiscal residency in *region* (no comune).

    Returns:
        A :class:`PayrollScenario` with the given region set.
    """
    return _req(
        level_code="4",
        seniority_count=0,
        jurisdiction=Jurisdiction(regione=region),
    )


# ---------------------------------------------------------------------------
# Invariant 1 — gross-to-net monotonicity
# ---------------------------------------------------------------------------


class TestMonotonicity:
    """Increasing gross_annual never decreases net_annual."""

    @settings(max_examples=50)
    @given(ral_low=_ral_st, ral_delta=st.integers(min_value=1, max_value=50_000))
    def test_net_does_not_decrease_when_gross_increases(
        self, ral_low: Decimal, ral_delta: int
    ) -> None:
        """net_annual at RAL + Δ is at least as large as net_annual at RAL.

        Invariant: net(RAL + Δ) >= net(RAL)
        """
        ral_high = ral_low + Decimal(ral_delta)

        with (
            patch(_PATCH_CCNL, return_value=_CCNL),
            patch(_PATCH_RULES, return_value=_RULES),
            patch(_PATCH_SURTAX, return_value=None),
        ):
            net_low = compute(_scenario_with_ral(ral_low)).result.net_annual
            net_high = compute(_scenario_with_ral(ral_high)).result.net_annual

        assert net_high >= net_low, (
            f"net_annual decreased when gross increased: "
            f"ral_low={ral_low}, net_low={net_low}, "
            f"ral_high={ral_high}, net_high={net_high}"
        )


# ---------------------------------------------------------------------------
# Invariant 2 — part-time scaling
# ---------------------------------------------------------------------------


class TestPartTimeScaling:
    """Part-time at 50% always produces a strictly lower net than full-time."""

    @settings(max_examples=30)
    @given(seniority_count=_seniority_st)
    def test_half_time_net_below_full_time(self, seniority_count: int) -> None:
        """net_annual at 50% part-time is strictly less than at 100%.

        The CCNL table salary (including seniority increments) drives the
        comparison; only the part-time coefficient differs.

        Invariant: net(0.50) < net(1.00) for every seniority level
        """
        scenario_half = _req(
            level_code="4",
            seniority_count=seniority_count,
            part_time_pct=Decimal("0.50"),
        )
        scenario_full = _req(
            level_code="4",
            seniority_count=seniority_count,
            part_time_pct=Decimal(1),
        )

        with (
            patch(_PATCH_CCNL, return_value=_CCNL),
            patch(_PATCH_RULES, return_value=_RULES),
            patch(_PATCH_SURTAX, return_value=None),
        ):
            net_half = compute(scenario_half).result.net_annual
            net_full = compute(scenario_full).result.net_annual

        assert net_half < net_full, (
            f"Expected net at 50% part-time < net at 100%, "
            f"got net_half={net_half}, net_full={net_full} "
            f"(seniority_count={seniority_count})"
        )


# ---------------------------------------------------------------------------
# Invariant 3 — INPS isolation
# ---------------------------------------------------------------------------


class TestInpsIsolation:
    """contribution_relevant=False supplements must not alter inps_employee_annual."""

    @settings(max_examples=50)
    @given(monthly=_allowance_st)
    def test_supplement_excluded_from_inps_base(self, monthly: Decimal) -> None:
        """inps_employee_annual is unchanged when a supplement is INPS-excluded.

        We compare two otherwise identical scenarios: one with no supplement,
        one with a supplement marked contribution_relevant=False.

        Invariant: inps(with supplement, contribution_relevant=False)
                   == inps(without supplement)
        """
        scenario_base = _req(level_code="4", seniority_count=0)
        scenario_with = _scenario_with_supplement(
            monthly, contribution_relevant=False, tfr_relevant=True
        )

        with (
            patch(_PATCH_CCNL, return_value=_CCNL),
            patch(_PATCH_RULES, return_value=_RULES),
            patch(_PATCH_SURTAX, return_value=None),
        ):
            inps_base = compute(scenario_base).result.inps_employee_annual
            inps_with = compute(scenario_with).result.inps_employee_annual

        assert inps_with == inps_base, (
            f"INPS changed despite contribution_relevant=False: "
            f"monthly={monthly}, inps_base={inps_base}, inps_with={inps_with}"
        )


# ---------------------------------------------------------------------------
# Invariant 4 — TFR isolation
# ---------------------------------------------------------------------------


class TestTfrIsolation:
    """tfr_relevant=False supplements must not alter tfr_annual."""

    @settings(max_examples=50)
    @given(monthly=_allowance_st)
    def test_supplement_excluded_from_tfr_base(self, monthly: Decimal) -> None:
        """tfr_annual is unchanged when a supplement is TFR-excluded.

        Invariant: tfr(with supplement, tfr_relevant=False)
                   == tfr(without supplement)
        """
        scenario_base = _req(level_code="4", seniority_count=0)
        scenario_with = _scenario_with_supplement(
            monthly, contribution_relevant=True, tfr_relevant=False
        )

        with (
            patch(_PATCH_CCNL, return_value=_CCNL),
            patch(_PATCH_RULES, return_value=_RULES),
            patch(_PATCH_SURTAX, return_value=None),
        ):
            tfr_base = compute(scenario_base).result.tfr_annual
            tfr_with = compute(scenario_with).result.tfr_annual

        assert tfr_with == tfr_base, (
            f"TFR changed despite tfr_relevant=False: "
            f"monthly={monthly}, tfr_base={tfr_base}, tfr_with={tfr_with}"
        )


# ---------------------------------------------------------------------------
# Invariant 5 — surtax isolation
# ---------------------------------------------------------------------------


class TestSurtaxIsolation:
    """Changing addizionale regionale must not alter irpef_net or INPS."""

    @settings(max_examples=50)
    @given(rate_a=_rate_st, rate_b=_rate_st)
    def test_regional_surtax_rate_does_not_affect_irpef_or_inps(
        self, rate_a: Decimal, rate_b: Decimal
    ) -> None:
        """irpef_net and inps_employee_annual are invariant to the surtax rate.

        addizionale regionale is settled after irpef_net and inps are fixed.
        It is a separate levy on net_annual and must not feed back into the
        standard IRPEF or INPS computations.

        Invariant:
            irpef_net(rate_a) == irpef_net(rate_b)
            inps_employee_annual(rate_a) == inps_employee_annual(rate_b)
        """
        scenario = _scenario_with_jurisdiction("TestRegione")

        with (
            patch(_PATCH_CCNL, return_value=_CCNL),
            patch(_PATCH_RULES, return_value=_RULES),
            patch(_PATCH_SURTAX, return_value=_surtax_with_rate(rate_a)),
        ):
            result_a = compute(scenario).result

        with (
            patch(_PATCH_CCNL, return_value=_CCNL),
            patch(_PATCH_RULES, return_value=_RULES),
            patch(_PATCH_SURTAX, return_value=_surtax_with_rate(rate_b)),
        ):
            result_b = compute(scenario).result

        assert result_a.irpef_net == result_b.irpef_net, (
            f"irpef_net changed when surtax rate changed: "
            f"rate_a={rate_a}, rate_b={rate_b}, "
            f"irpef_a={result_a.irpef_net}, irpef_b={result_b.irpef_net}"
        )
        assert result_a.inps_employee_annual == result_b.inps_employee_annual, (
            f"inps_employee_annual changed when surtax rate changed: "
            f"rate_a={rate_a}, rate_b={rate_b}, "
            f"inps_a={result_a.inps_employee_annual}, "
            f"inps_b={result_b.inps_employee_annual}"
        )
