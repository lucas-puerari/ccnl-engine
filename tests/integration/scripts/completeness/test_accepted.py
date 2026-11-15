"""Capabilities left to the caller that the completeness report accepts."""

from __future__ import annotations

import pytest

from ccnl_engine.capability.loaders import load_capability_catalog
from ccnl_engine.capability.registry.models import CapabilityImplementation
from ccnl_engine.catalog.loaders import load_ccnl
from scripts.completeness import report
from scripts.completeness.accepted import BY_DESIGN, RULE_BACKED, accepted


def test_every_accepted_capability_is_caller_supplied_with_a_reason() -> None:
    """An accepted entry names a catalog capability a caller value replaces."""
    catalog = {c.feature: c for c in load_capability_catalog(2026).capabilities}

    for feature in (*BY_DESIGN, *RULE_BACKED):
        implementation = catalog[feature].implementation
        assert implementation is CapabilityImplementation.CALLER_SUPPLIED, feature
    assert all(reason.strip() for reason in BY_DESIGN.values())


@pytest.mark.parametrize(
    ("ccnl_id", "holds"),
    [
        ("studi-professionali-confprofessioni", True),
        ("metalmeccanico-federmeccanica", True),
        ("commercio-confcommercio", False),
    ],
)
def test_the_travel_allowance_is_a_gap_where_the_ccnl_holds_no_amounts(
    ccnl_id: str, holds: bool
) -> None:
    """Without the CCNL bands the caller must state every daily amount."""
    ccnl = load_ccnl(ccnl_id)

    assert accepted("travel_allowance", ccnl) is holds
    gaps = report.non_native(ccnl, (2026,))
    assert ("travel_allowance" in gaps) is not holds


@pytest.mark.parametrize(
    "feature", ["overtime", "night_work", "holiday_work", "shift_work", "absence"]
)
def test_alimentari_holds_its_working_time_rules(feature: str) -> None:
    """Overtime bands, night, holiday and shift supplements, absence rules."""
    assert accepted(feature, load_ccnl("alimentari-federalimentare"))


@pytest.mark.parametrize(
    ("feature", "holds"),
    [("night_work", False), ("shift_work", False), ("holiday_work", True)],
)
def test_a_supplement_without_its_band_stays_a_gap(feature: str, holds: bool) -> None:
    """Agenti immobiliari holds holiday bands, no ordinary night or shift band."""
    assert accepted(feature, load_ccnl("agenti-immobiliari-fiaip")) is holds


@pytest.mark.parametrize("feature", ["night_work", "shift_work", "holiday_work"])
def test_federmeccanica_holds_its_night_and_shift_bands(feature: str) -> None:
    """Art. 7: night before and after 22, the shift workers' night hours."""
    assert accepted(feature, load_ccnl("metalmeccanico-federmeccanica"))


def test_a_second_level_supplement_is_accepted_by_design() -> None:
    """A company agreement is a fact of the employer, whatever the CCNL."""
    ccnl = load_ccnl("metalmeccanico-federmeccanica")

    assert accepted("company_supplement", ccnl)
    assert not accepted("art15_deductions", ccnl)


@pytest.mark.parametrize("feature", sorted(RULE_BACKED))
def test_a_ccnl_without_work_rules_holds_none(feature: str) -> None:
    """No work rules: every rule-backed capability stays a gap."""
    ccnl = load_ccnl("alimentari-federalimentare").model_copy(
        update={"work_rules": None}
    )

    assert not accepted(feature, ccnl)


@pytest.mark.parametrize("feature", ["bilateral_funds", "contract_renewal_arrears"])
def test_an_employer_fact_is_accepted_by_design(feature: str) -> None:
    """A territorial fund and earlier payslips are facts of the employer."""
    assert accepted(feature, load_ccnl("commercio-confcommercio"))


@pytest.mark.parametrize(
    ("feature", "holds"), [("overtime", True), ("travel_allowance", True)]
)
def test_a_capability_handed_to_the_employer_is_accepted(
    feature: str, holds: bool
) -> None:
    """AFAM: overtime to the integrative bargaining, travel suppressed by law."""
    afam = load_ccnl("afam-aran")
    assert afam.work_rules is not None

    assert accepted(feature, afam) is holds
    assert feature in afam.work_rules.capability_basis
    assert (feature in report.non_native(afam, (2026,))) is not holds
