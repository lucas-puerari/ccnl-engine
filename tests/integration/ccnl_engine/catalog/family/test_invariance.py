"""The contract family classifies a CCNL; it never changes the pay.

``meta.family`` is read by the catalog only (listing and search).  A CCNL
moved to another family computes the same run: the same pay items, the
same contributions (their selection reads ``tax_sector`` and the employer
facts, not the family) and the same taxes.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.agreement.family.models import FamilyAssignment
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.results import result_to_json

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

_HIRED = date(2025, 1, 1)
_RUN = PeriodInput(
    run=PayrollRun.regular(2026, 3),
    payment_date=date(2026, 3, 27),
    employment=Employment(
        ccnl_id="commercio-confcommercio",
        level_code="4",
        category=WorkerCategory.IMPIEGATO,
        contract_type=Permanent(),
        employment_period=EmploymentPeriod(_HIRED, None),
        seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
        pension_fund=NoPensionFund(),
        tfr_treasury_fund=False,
    ),
    employer=EmployerProfile(headcount=Headcount(20)),
    facts=PeriodFacts(),
)


class _OtherFamily(BundledKnowledgeRepository):
    """The bundled repository with every CCNL moved to the edilizia family."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        """Return the bundled CCNL in another family.

        Returns:
            The CCNL whose ``meta.family`` is edilizia.
        """
        ccnl = super().load_ccnl(ccnl_id)
        family = FamilyAssignment(id="edilizia", reason="moved by the test")
        meta = ccnl.meta.model_copy(update={"family": family})
        return ccnl.model_copy(update={"meta": meta})


def test_another_family_computes_the_same_run() -> None:
    """Commercio moved to edilizia pays, contributes and is taxed the same."""
    repository = _OtherFamily()
    moved = PayrollEngine(repository=repository)
    family = repository.load_ccnl("commercio-confcommercio").meta.family
    assert family.id == "edilizia"

    bundled = PayrollEngine.bundled().calculate_period(_RUN)
    other = moved.calculate_period(_RUN)

    assert result_to_json(other) == result_to_json(bundled)
