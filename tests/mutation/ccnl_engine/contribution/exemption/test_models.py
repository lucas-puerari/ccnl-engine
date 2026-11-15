"""The part of an employer rate the contribution exemptions do not cut.

INPS circ. 82/2026 p. 5: no exemption cuts the 0.30% of continuing training
(L. 845/1978 art. 25 c. 4) nor the solidarity funds of D.Lgs. 148/2015 artt.
26, 27 and 29.  In the terziario up to five employees that is 0.30% plus
the employer FIS share 0.33333%: 0.63333%.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.contribution.exemption.models import ReliefExclusion
from ccnl_engine.contribution.fis.models import FisReduction, with_fis_reduction
from ccnl_engine.contribution.rate.models import InpsRates
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance
from ccnl_engine.sector.loaders import load_year_rules

_PROVENANCE = RuleProvenance(status=ProvenanceStatus.MISSING)
_EXCLUSION = ReliefExclusion(
    rate=Decimal("0.0063333"),
    rate_by_category={
        WorkerCategory.DIRIGENTE: None,
        WorkerCategory.QUADRO: Decimal("0.0030"),
    },
    provenance=_PROVENANCE,
)


def test_a_category_takes_its_rate_or_the_tier_one() -> None:
    """Listed: its own rate or open; not listed or unknown: the tier rate."""
    assert _EXCLUSION.for_category(WorkerCategory.QUADRO) == Decimal("0.0030")
    assert _EXCLUSION.for_category(WorkerCategory.DIRIGENTE) is None
    assert _EXCLUSION.for_category(WorkerCategory.OPERAIO) == Decimal("0.0063333")
    assert _EXCLUSION.for_category(None) == Decimal("0.0063333")


def test_the_fis_cut_lowers_the_excluded_fis() -> None:
    """Art. 29 c. 8-bis: 0.63333% - 0.13% = 0.50333%; open stays open."""
    cut = FisReduction(
        max_employees=5,
        employer_rate=Decimal("0.0013"),
        employee_rate=Decimal("0.0007"),
    )
    rates = InpsRates(
        employee_rate=Decimal("0.0935667"),
        employee_ivs_rate=Decimal("0.0919"),
        employer_rate=Decimal("0.2931333"),
        employer_ivs_rate=Decimal("0.2381"),
        ceiling=None,
        fis_reduction=cut,
        relief_excluded=_EXCLUSION,
    )
    excluded = with_fis_reduction(rates, reduced=True, headcount=5).relief_excluded
    assert excluded is not None
    assert excluded.rate == Decimal("0.0050333")
    assert excluded.rate_by_category == {
        WorkerCategory.DIRIGENTE: None,
        WorkerCategory.QUADRO: Decimal("0.0017"),
    }
    plain = rates.model_copy(update={"relief_excluded": None})
    assert with_fis_reduction(plain, reduced=True, headcount=5).relief_excluded is None


def test_the_bundle_reads_the_tier_of_the_headcount() -> None:
    """Terziario: 0.63333% up to five employees, 0.83333% above."""
    for headcount, rate in ((5, "0.0063333"), (6, "0.0083333"), (16, "0.0083333")):
        inps = load_year_rules(2026, TaxSector.TERZIARIO, headcount).inps
        assert inps is not None
        assert inps.relief_excluded is not None
        assert inps.relief_excluded.rate == Decimal(rate)
        assert inps.relief_excluded.for_category(WorkerCategory.DIRIGENTE) is None
