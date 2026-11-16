"""Capabilities left to the caller that the completeness report accepts."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ccnl_engine.capability.loaders import load_capability_catalog
from ccnl_engine.capability.registry.models import CapabilityImplementation
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.working_time.hourly.components import derives_hourly_base
from ccnl_engine.working_time.models import TimeSupplementKind
from scripts.completeness import report
from scripts.completeness.accepted import BY_DESIGN, RULE_BACKED, accepted

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL


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
        ("commercio-confcommercio", True),
        ("logistica-trasporto-confetra", False),
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


def _with(ccnl_id: str, **band: object) -> CCNL:
    ccnl = load_ccnl(ccnl_id)
    rules = ccnl.work_rules
    assert rules is not None
    supplements = rules.time_supplements
    assert supplements is not None
    first = supplements.supplement_bands[0].model_copy(update=band)
    changed = supplements.model_copy(update={"supplement_bands": (first,)})
    work = rules.model_copy(update={"time_supplements": changed})
    return ccnl.model_copy(update={"work_rules": work})


def _without_base(ccnl: CCNL) -> CCNL:
    rules = ccnl.work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    supplements = rules.time_supplements.model_copy(
        update={"hourly_base_provenance": None}
    )
    levels = tuple(
        level.model_copy(update={"hourly_base_provenance": None})
        for level in ccnl.levels
    )
    work = rules.model_copy(update={"time_supplements": supplements})
    return ccnl.model_copy(update={"work_rules": work, "levels": levels})


def test_a_percentage_band_needs_the_hourly_base() -> None:
    """Without a verified base the night share computes nothing: a gap."""
    ccnl = _with("commercio-confcommercio")
    assert derives_hourly_base(ccnl)
    assert accepted("night_work", ccnl)
    assert not derives_hourly_base(_without_base(ccnl))
    assert not accepted("night_work", _without_base(ccnl))
    assert not accepted("overtime", _without_base(ccnl))


def test_a_fixed_band_computes_without_the_base() -> None:
    """A fixed amount per hour needs no hourly base."""
    ccnl = _without_base(_with("commercio-confcommercio", fixed_per_hour=True))
    assert accepted("night_work", ccnl)


@pytest.mark.parametrize(
    ("apart", "holds"), [(True, True), (False, True), (None, False)]
)
def test_hours_due_apart_are_settled_or_a_gap(apart: bool | None, holds: bool) -> None:
    """A night band silent on its hours leaves them to the caller."""
    ccnl = _with("commercio-confcommercio", hours_paid_apart=apart)
    assert accepted("night_work", ccnl) is holds


def test_hours_apart_need_a_base_to_price_them() -> None:
    """A fixed band paying the hours apart has no rate for the hours."""
    ccnl = _without_base(
        _with("commercio-confcommercio", fixed_per_hour=True, hours_paid_apart=True)
    )
    assert not accepted("night_work", ccnl)


def test_overtime_of_fixed_amounts_needs_no_base() -> None:
    """Only a percentage overtime band reads the hourly base."""
    ccnl = _without_base(load_ccnl("commercio-confcommercio"))
    rules = ccnl.work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    fixed = tuple(
        b.model_copy(update={"kind": TimeSupplementKind.INDENNITA_PER_HOUR})
        for b in rules.time_supplements.overtime_bands
    )
    supplements = rules.time_supplements.model_copy(update={"overtime_bands": fixed})
    work = rules.model_copy(update={"time_supplements": supplements})
    assert accepted("overtime", ccnl.model_copy(update={"work_rules": work}))


def test_a_level_without_a_divisor_has_no_base() -> None:
    """The divisor of the CCNL or of the level is needed too."""
    ccnl = load_ccnl("commercio-confcommercio")
    empty = ccnl.parameters.hourly_divisor.model_copy(update={"periods": ()})
    parameters = ccnl.parameters.model_copy(update={"hourly_divisor": empty})
    assert not derives_hourly_base(ccnl.model_copy(update={"parameters": parameters}))
