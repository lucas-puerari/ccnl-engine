"""Tests for PayrollBundle and _compute_bundle_hash."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest

from ccnl_engine.engine.contract.domain.ccnl import CCNL
from ccnl_engine.engine.payroll.domain.bundle import (
    _compute_bundle_hash,
    make_bundle,
)
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualPayrollScenario,
    Employee,
    Employer,
    Employment,
    PayPeriod,
)
from ccnl_engine.engine.payroll.service.bundle_loader import load_payroll_bundle
from ccnl_engine.engine.payroll.service.orchestrator import (
    compute,
    compute_month,
    estimate_annual,
)
from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
from tests.helpers import (
    TEST_RULESET_VERIFIED,
    make_ccnl_dict,
    make_domestic_year_rules,
    make_minimal_ccnl,
    make_year_rules,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _CCNL_FILENAME,
    _req,
)

_SCENARIO = AnnualPayrollScenario(
    employee=Employee(level_code="4"),
    employment=Employment(
        ccnl=_CCNL_FILENAME,
        contract=Permanent(),
        employer=Employer(num_employees=50),
        as_of=date(2026, 6, 1),
    ),
)
_PERIOD = PayPeriod()


def _make_empty_surtax() -> SurtaxRules:
    """Return a SurtaxRules with empty regional and municipal tables.

    Returns:
        A SurtaxRules instance with no rates defined.
    """
    return SurtaxRules.model_validate({"year": 2026, "regionale": {}, "comunale": {}})


def _make_ccnl_with_ruleset() -> CCNL:
    """Return a minimal CCNL that has a ruleset identity attached.

    Returns:
        A CCNL instance with a verified ruleset identity.
    """
    raw = make_ccnl_dict()
    raw["ruleset"] = TEST_RULESET_VERIFIED
    return CCNL.model_validate(raw)


class TestComputeBundleHash:
    """Tests for _compute_bundle_hash branch coverage."""

    def test_fallback_to_knowledge_version_when_no_rulesets(self) -> None:
        """Hash is produced even when no ruleset identities are present."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules(ruleset=None, inps_ruleset=None)
        bh = _compute_bundle_hash(ccnl, rules, surtax=None)
        assert isinstance(bh, str)
        assert len(bh) == 64

    def test_with_ruleset_ids_present(self) -> None:
        """Hash is produced when tax ruleset identity is present."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        bh = _compute_bundle_hash(ccnl, rules, surtax=None)
        assert len(bh) == 64

    def test_ccnl_with_ruleset_id_uses_str_repr(self) -> None:
        """CCNL ruleset str() is used in hash when the identity is set."""
        ccnl_with = _make_ccnl_with_ruleset()
        ccnl_without = make_minimal_ccnl()
        rules = make_year_rules()
        bh_with = _compute_bundle_hash(ccnl_with, rules, surtax=None)
        bh_without = _compute_bundle_hash(ccnl_without, rules, surtax=None)
        assert len(bh_with) == 64
        assert bh_with != bh_without

    def test_hash_is_deterministic(self) -> None:
        """Same inputs always produce the same hash."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        bh1 = _compute_bundle_hash(ccnl, rules, surtax=None)
        bh2 = _compute_bundle_hash(ccnl, rules, surtax=None)
        assert bh1 == bh2

    def test_hash_differs_when_rulesets_differ(self) -> None:
        """Different tax ruleset identity produces a different hash."""
        ccnl = make_minimal_ccnl()
        bh_with = _compute_bundle_hash(ccnl, make_year_rules(), surtax=None)
        bh_without = _compute_bundle_hash(
            ccnl, make_year_rules(ruleset=None), surtax=None
        )
        assert bh_with != bh_without

    def test_domestic_contributions_omits_inps(self) -> None:
        """Domestic contribution model omits the INPS key from the hash."""
        ccnl = make_minimal_ccnl()
        rules = make_domestic_year_rules()
        bh = _compute_bundle_hash(ccnl, rules, surtax=None)
        assert len(bh) == 64

    def test_with_surtax_no_ruleset_ids(self) -> None:
        """Hash is produced with a surtax object that has no ruleset ids."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        surtax = _make_empty_surtax()
        bh = _compute_bundle_hash(ccnl, rules, surtax=surtax)
        assert len(bh) == 64

    def test_hash_differs_with_and_without_surtax(self) -> None:
        """Adding surtax changes the hash."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        surtax = _make_empty_surtax()
        bh_no_surtax = _compute_bundle_hash(ccnl, rules, surtax=None)
        bh_with_surtax = _compute_bundle_hash(ccnl, rules, surtax=surtax)
        assert bh_no_surtax != bh_with_surtax

    def test_inps_absent_in_standard_model_gets_fallback(self) -> None:
        """Standard model with no inps_ruleset gets a knowledge-version fallback."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules(inps_ruleset=None)
        bh = _compute_bundle_hash(ccnl, rules, surtax=None)
        assert len(bh) == 64


class TestMakeBundle:
    """Tests for make_bundle factory."""

    def test_bundle_hash_matches_expected(self) -> None:
        """Bundle hash equals the direct _compute_bundle_hash call."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        bundle = make_bundle(ccnl, rules, None)
        expected = _compute_bundle_hash(ccnl, rules, None)
        assert bundle.bundle_hash == expected

    def test_bundle_fields_preserved(self) -> None:
        """Bundle carries the exact objects passed to the factory."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        bundle = make_bundle(ccnl, rules, None)
        assert bundle.ccnl is ccnl
        assert bundle.rules is rules
        assert bundle.surtax is None

    def test_bundle_with_surtax(self) -> None:
        """Bundle preserves the surtax object when provided."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        surtax = _make_empty_surtax()
        bundle = make_bundle(ccnl, rules, surtax)
        assert bundle.surtax is surtax

    def test_bundle_is_frozen(self) -> None:
        """PayrollBundle is immutable after construction."""
        bundle = make_bundle(make_minimal_ccnl(), make_year_rules(), None)
        with pytest.raises((TypeError, AttributeError)):
            bundle.bundle_hash = "tampered"  # type: ignore[misc]


class TestLoadPayrollBundle:
    """Tests for load_payroll_bundle loader."""

    def test_load_without_surtax(self) -> None:
        """load_surtax_rules is not called when load_surtax=False."""
        with (
            patch(
                "ccnl_engine.engine.payroll.service.bundle_loader.load_ccnl",
                return_value=make_minimal_ccnl(),
            ),
            patch(
                "ccnl_engine.engine.payroll.service.bundle_loader.load_year_rules",
                return_value=make_year_rules(),
            ),
            patch(
                "ccnl_engine.engine.payroll.service.bundle_loader.load_surtax_rules"
            ) as mock_surtax,
        ):
            bundle = load_payroll_bundle(
                _CCNL_FILENAME, 2026, num_employees=50, load_surtax=False
            )
        mock_surtax.assert_not_called()
        assert bundle.surtax is None
        assert len(bundle.bundle_hash) == 64

    def test_load_with_surtax(self) -> None:
        """load_surtax_rules is called and its result stored when load_surtax=True."""
        fake_surtax = _make_empty_surtax()
        with (
            patch(
                "ccnl_engine.engine.payroll.service.bundle_loader.load_ccnl",
                return_value=make_minimal_ccnl(),
            ),
            patch(
                "ccnl_engine.engine.payroll.service.bundle_loader.load_year_rules",
                return_value=make_year_rules(),
            ),
            patch(
                "ccnl_engine.engine.payroll.service.bundle_loader.load_surtax_rules",
                return_value=fake_surtax,
            ),
        ):
            bundle = load_payroll_bundle(
                _CCNL_FILENAME, 2026, num_employees=50, load_surtax=True
            )
        assert bundle.surtax is fake_surtax


class TestComputeWithBundle:
    """Tests for bundle injection into compute / estimate_annual / compute_month."""

    def test_compute_with_bundle_skips_loaders(self) -> None:
        """Loaders are never called when a bundle is supplied."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        bundle = make_bundle(ccnl, rules, None)
        req = _req()
        with (
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl"
            ) as mock_ccnl,
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_year_rules"
            ) as mock_rules,
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_surtax_rules"
            ) as mock_surtax,
        ):
            calc = compute(req, bundle)
        mock_ccnl.assert_not_called()
        mock_rules.assert_not_called()
        mock_surtax.assert_not_called()
        assert calc is not None

    def test_compute_without_bundle_uses_loaders(self) -> None:
        """Loaders are called when no bundle is supplied."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        req = _req()
        with (
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl",
                return_value=ccnl,
            ) as mock_ccnl,
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_year_rules",
                return_value=rules,
            ),
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_surtax_rules",
                return_value=None,
            ),
        ):
            compute(req, None)
        mock_ccnl.assert_called_once()

    def test_estimate_annual_with_bundle(self) -> None:
        """estimate_annual skips loaders when a bundle is supplied."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        bundle = make_bundle(ccnl, rules, None)
        with (
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl"
            ) as mock_ccnl,
        ):
            calc = estimate_annual(_SCENARIO, bundle)
        mock_ccnl.assert_not_called()
        assert calc is not None

    def test_estimate_annual_without_bundle(self) -> None:
        """estimate_annual calls loaders when no bundle is supplied."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        with (
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl",
                return_value=ccnl,
            ) as mock_ccnl,
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_year_rules",
                return_value=rules,
            ),
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_surtax_rules",
                return_value=None,
            ),
        ):
            estimate_annual(_SCENARIO)
        mock_ccnl.assert_called_once()

    def test_compute_month_with_bundle(self) -> None:
        """compute_month skips loaders when a bundle is supplied."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        bundle = make_bundle(ccnl, rules, None)
        with (
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl"
            ) as mock_ccnl,
        ):
            calc = compute_month(_SCENARIO, _PERIOD, bundle)
        mock_ccnl.assert_not_called()
        assert calc is not None

    def test_compute_month_without_bundle(self) -> None:
        """compute_month calls loaders when no bundle is supplied."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        with (
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl",
                return_value=ccnl,
            ) as mock_ccnl,
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_year_rules",
                return_value=rules,
            ),
            patch(
                "ccnl_engine.engine.payroll.service.orchestrator.load_surtax_rules",
                return_value=None,
            ),
        ):
            compute_month(_SCENARIO, _PERIOD, None)
        mock_ccnl.assert_called_once()
