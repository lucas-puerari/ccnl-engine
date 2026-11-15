"""Price the work of the run with the supplement rates the employer states."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance
from ccnl_engine.working_time.models import TimeSupplements
from ccnl_engine.working_time.supplement.employer.inputs import RateUnit
from ccnl_engine.working_time.supplement.models import SupplementBand

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.working_time.supplement.employer.inputs import SecondLevelRate

__all__ = ["with_second_level_rates"]


def _band(rate: SecondLevelRate) -> SupplementBand:
    agreement = f"{rate.agreement.value} agreement"
    document = SourceDocument(
        document_id=f"employer-{rate.agreement.value}-agreement",
        title=f"The employer's {agreement} (EmployerProfile.second_level_rates)",
        kind=SourceKind.ALTRO,
    )
    return SupplementBand(
        code=f"EMPLOYER_{rate.work.value.upper()}",
        description=f"{rate.work.value} supplement of the {agreement}",
        work=rate.work,
        rate=TimeSeries(
            periods=(
                ValidityPeriod(
                    valid_from=rate.valid_from,
                    valid_until=rate.valid_until,
                    value=rate.rate,
                ),
            )
        ),
        fixed_per_hour=rate.unit is RateUnit.PER_HOUR,
        per_shift=rate.unit is RateUnit.PER_SHIFT,
        hours_paid_apart=rate.hours_paid_apart,
        provenance=RuleProvenance(
            status=ProvenanceStatus.DERIVED,
            location=SourceLocation(source_document=document, section=agreement),
            transformation="A rate the employer states for its agreement.",
        ),
    )


def with_second_level_rates(
    ccnl: CCNL, level_code: str, rates: tuple[SecondLevelRate, ...], day: date
) -> CCNL:
    """Return the CCNL with the employer's rates in place of its bands of the work.

    Returns:
        ``ccnl`` unchanged when no rate applies on ``day``; else a copy
        whose supplement bands of each priced work are the employer's.
    """
    paid = tuple(r for r in rates if r.applies_to(level_code, day))
    work = ccnl.work_rules
    if not paid or work is None:
        return ccnl
    supplements = work.time_supplements or TimeSupplements()
    priced = {r.work for r in paid}
    bands = (
        *(b for b in supplements.supplement_bands if b.work not in priced),
        *(_band(r) for r in paid),
    )
    changed = supplements.model_copy(update={"supplement_bands": bands})
    rules = work.model_copy(update={"time_supplements": changed})
    return ccnl.model_copy(update={"work_rules": rules})
