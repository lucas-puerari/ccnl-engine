"""The engine reads the injected repository for its catalog and its runs.

A repository with one CCNL the bundle does not hold: the engine lists it,
inspects it, lists its levels and computes a run of it, and stamps every
result with the version of that repository instead of the package bundle.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    bundle_version,
)
from ccnl_engine.agreement.family.models import FamilyAssignment
from ccnl_engine.errors import InvalidInputError, UnknownCcnlError
from ccnl_engine.inputs import Permanent
from tests.integration.ccnl_engine.catalog.builders import (
    SYNTHETIC_BUNDLE_VERSION,
    SYNTHETIC_CNEL_CODE,
    SYNTHETIC_ID,
    SyntheticCcnlRepository,
)

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

_ENGINE = PayrollEngine(repository=SyntheticCcnlRepository())


def _june(ccnl_id: str, engine: PayrollEngine = _ENGINE) -> PeriodInput:
    return PeriodInput(
        run=PayrollRun.regular(2026, 6),
        payment_date=date(2026, 6, 27),
        employment=Employment(
            ccnl_id=ccnl_id, level_code="C3", contract_type=Permanent()
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    )


def test_the_catalog_lists_the_contract_of_the_repository() -> None:
    """The extra CCNL is listed; the bundled engine does not know it."""
    listed = {summary.ccnl_id for summary in _ENGINE.list_contracts()}
    bundled = {summary.ccnl_id for summary in PayrollEngine.bundled().list_contracts()}

    assert listed == bundled | {SYNTHETIC_ID}


@pytest.mark.parametrize("ccnl_id", [SYNTHETIC_ID, SYNTHETIC_CNEL_CODE])
def test_the_ruleset_and_levels_come_from_the_repository(ccnl_id: str) -> None:
    """Slug and CNEL code both resolve against the injected repository."""
    assert _ENGINE.inspect_ruleset(ccnl_id).id == f"ccnl/{SYNTHETIC_ID}"
    assert "C3" in {level.code for level in _ENGINE.list_levels(ccnl_id)}


@pytest.mark.parametrize("ccnl_id", [SYNTHETIC_ID, SYNTHETIC_CNEL_CODE])
def test_a_run_computes_and_carries_the_repository_version(ccnl_id: str) -> None:
    """The run computes the same amounts as its source CCNL, stamped apart."""
    result = _ENGINE.calculate_period(_june(ccnl_id))
    source = PayrollEngine.bundled().calculate_period(
        _june("metalmeccanico-federmeccanica")
    )

    assert result.period_net == source.period_net
    assert result.bundle_version == SYNTHETIC_BUNDLE_VERSION
    assert source.bundle_version == bundle_version
    assert f"ccnl/{SYNTHETIC_ID}" in {ruleset.id for ruleset in result.rulesets}


def test_the_bundled_engine_does_not_know_the_extra_contract() -> None:
    """The extra CCNL lives in the injected repository only."""
    with pytest.raises(UnknownCcnlError):
        PayrollEngine.bundled().inspect_ruleset(SYNTHETIC_ID)
    with pytest.raises(UnknownCcnlError):
        PayrollEngine.bundled().calculate_period(_june(SYNTHETIC_CNEL_CODE))


def test_the_family_filter_reads_the_repository() -> None:
    """The extra CCNL is listed under its family, the bundled engine lacks it."""
    listed = {s.ccnl_id for s in _ENGINE.list_contracts(family="metalmeccanica")}
    bundled = {
        s.ccnl_id
        for s in PayrollEngine.bundled().list_contracts(family="metalmeccanica")
    }

    assert listed == bundled | {SYNTHETIC_ID}
    with pytest.raises(InvalidInputError, match="not a contract family"):
        _ENGINE.list_contracts(family="metalworking")


class _RefamiliedRepository(SyntheticCcnlRepository):
    """The synthetic CCNL moved to another family, every rule unchanged."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        ccnl = super().load_ccnl(ccnl_id)
        if ccnl_id != SYNTHETIC_ID:
            return ccnl
        family = FamilyAssignment(id="edilizia", reason="Moved for the test.")
        meta = ccnl.meta.model_copy(update={"family": family})
        return ccnl.model_copy(update={"meta": meta})


def test_the_family_does_not_change_a_run() -> None:
    """The family selects no rule: the same CCNL in another family pays alike."""
    moved = PayrollEngine(repository=_RefamiliedRepository())
    result = moved.calculate_period(_june(SYNTHETIC_ID, moved))
    source = _ENGINE.calculate_period(_june(SYNTHETIC_ID))

    assert result.pay_items == source.pay_items
    assert result.contribution_breakdown == source.contribution_breakdown
    assert result.period_employer_cost == source.period_employer_cost
    assert result.decisions == source.decisions
