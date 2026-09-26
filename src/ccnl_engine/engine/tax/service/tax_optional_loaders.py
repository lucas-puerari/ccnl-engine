"""Optional tax rule loaders: sick pay, variable pay, family, Art. 15."""

from __future__ import annotations

import importlib.resources
from decimal import Decimal

from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.engine.tax.domain.art15 import (
    Art15DeductionRules,
    MortgageInterestRules,
)
from ccnl_engine.engine.tax.domain.family import (
    ChildrenDeductionRules,
    FamilyDeductionRules,
    OtherDependentRules,
    SpouseDeductionRules,
)
from ccnl_engine.engine.tax.domain.rules import DeductionBreakpoint
from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates, SickPayBand
from ccnl_engine.engine.tax.domain.variable_pay import (
    FringeBenefitRules,
    NotteTurnoRules,
    PdRRules,
    RinnovoRules,
    VariablePayRules,
)
from ccnl_engine.engine.tax.service.tax_resource_reader import (
    _as_ruleset,
    _read_json,
    _try_ruleset,
    read_year_json,
)


def load_sick_pay_rates() -> InpsSickPayRates:
    """Load INPS statutory sick-pay indemnity rates from the bundled data file.

    The file ``knowledge/inps/data/sick-pay-rates.json`` is not year- or
    sector-specific: statutory sick-pay rates are cross-sector and change
    only by primary legislation (D.Lgs. 151/2001, artt. 68-71).

    Returns:
        An :class:`~ccnl_engine.engine.tax.domain.sick_pay.InpsSickPayRates`
        with the INPS carenza period, indemnity bands, and provenance.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.inps.data")
    raw = _read_json(pkg, "sick-pay-rates.json")
    bands = [SickPayBand(**b) for b in raw.get("bands", [])]
    return InpsSickPayRates(
        description=raw.get("description", ""),
        carenza_days=int(raw.get("carenza_days", 3)),
        bands=bands,
        ruleset=_as_ruleset(raw),
    )


def load_variable_pay_rules(year: int) -> VariablePayRules:
    """Load statutory variable-pay rules for *year*.

    The file ``knowledge/tax/data/variable-pay-rules.json`` is not
    sector-specific.  It carries Art. 51 c. 3 TUIR thresholds, PdR flat-tax
    parameters and the L. 199/2025 substitute-tax regimes, which vary by
    fiscal year but not by sector or CCNL.

    Args:
        year: Fiscal year (e.g. ``2026``).  The filename is looked up as
            ``variable-pay-rules.json``; the ``year`` field inside the file
            is validated to match.

    Returns:
        A :class:`~ccnl_engine.engine.tax.domain.variable_pay.VariablePayRules`
        with thresholds and PdR parameters already validated.

    Raises:
        DataIntegrityError: If the file's ``year`` field does not match *year*.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.tax.data")
    raw = _read_json(pkg, "variable-pay-rules.json")
    if raw.get("year") != year:
        msg = (
            f"variable-pay-rules.json year={raw.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)
    fb_raw = raw["fringe_benefit"]
    pdr_raw = raw["pdr"]
    rinnovo_raw = raw["rinnovo"]
    notte_raw = raw["notte_turno"]
    return VariablePayRules(
        year=int(raw["year"]),
        description=raw.get("description", ""),
        fringe_benefit=FringeBenefitRules(
            threshold_standard=Decimal(str(fb_raw["threshold_standard"])),
            threshold_with_children=Decimal(str(fb_raw["threshold_with_children"])),
        ),
        pdr=PdRRules(
            max_amount=Decimal(str(pdr_raw["max_amount"])),
            flat_tax_rate=Decimal(str(pdr_raw["flat_tax_rate"])),
            income_ceiling=Decimal(str(pdr_raw["income_ceiling"])),
        ),
        rinnovo=RinnovoRules.model_validate({
            **{k: v for k, v in rinnovo_raw.items() if k != "description"},
            "ruleset": _as_ruleset(raw),
        }),
        notte_turno=NotteTurnoRules(
            flat_tax_rate=Decimal(str(notte_raw["flat_tax_rate"])),
            income_ceiling=Decimal(str(notte_raw["income_ceiling"])),
        ),
        ruleset=_as_ruleset(raw),
    )


def load_family_deduction_rules(year: int) -> FamilyDeductionRules:
    """Load Art. 12 TUIR family deduction rules for *year*.

    The file ``knowledge/tax/data/family-deductions-{year}.json`` carries
    spouse, children and other-dependent deduction parameters.  These are
    pure law, not CCNL-specific.

    Args:
        year: Fiscal year (e.g. ``2026``).

    Returns:
        A :class:`~ccnl_engine.engine.tax.domain.family.FamilyDeductionRules`
        with all deduction parameters validated.

    Raises:
        DataIntegrityError: If the file's ``year`` field does not match *year*.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.tax.data")
    filename = f"family-deductions-{year}.json"
    raw = read_year_json(pkg, filename, year)
    if raw.get("year") != year:
        msg = (
            f"{filename} year={raw.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)

    sp_raw = raw["spouse"]
    ch_raw = raw["children"]
    od_raw = raw["other_dependents"]

    bp_list = [
        DeductionBreakpoint(
            income_up_to=(
                Decimal(str(bp["income_up_to"]))
                if bp["income_up_to"] is not None
                else None
            ),
            deduction=Decimal(str(bp["deduction"])),
        )
        for bp in sp_raw["breakpoints"]
    ]

    return FamilyDeductionRules(
        year=int(raw["year"]),
        description=raw.get("description", ""),
        ruleset=_try_ruleset(raw),
        spouse=SpouseDeductionRules(
            dependent_income_threshold=Decimal(
                str(sp_raw["dependent_income_threshold"])
            ),
            breakpoints=bp_list,
            notes=sp_raw.get("notes", ""),
        ),
        children=ChildrenDeductionRules(
            auu_age_cutoff=int(ch_raw["auu_age_cutoff"]),
            base_amount=Decimal(str(ch_raw["base_amount"])),
            income_ceiling=Decimal(str(ch_raw["income_ceiling"])),
            income_ceiling_increment_per_child=Decimal(
                str(ch_raw["income_ceiling_increment_per_child"])
            ),
            notes=ch_raw.get("notes", ""),
        ),
        other_dependents=OtherDependentRules(
            dependent_income_threshold=Decimal(
                str(od_raw["dependent_income_threshold"])
            ),
            amount=Decimal(str(od_raw["amount"])),
            income_ceiling=Decimal(str(od_raw["income_ceiling"])),
            notes=od_raw.get("notes", ""),
        ),
    )


def load_art15_deduction_rules(year: int) -> Art15DeductionRules:
    """Load Art. 15 TUIR oneri detraibili rules for *year*.

    The file ``knowledge/tax/data/art15-deductions-{year}.json`` carries
    mortgage interest ceiling and rate parameters.  These are pure law,
    not CCNL-specific.

    Args:
        year: Fiscal year (e.g. ``2026``).

    Returns:
        An :class:`~ccnl_engine.engine.tax.domain.art15.Art15DeductionRules`
        with all deduction parameters validated.

    Raises:
        DataIntegrityError: If the file's ``year`` field does not match *year*.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.tax.data")
    filename = f"art15-deductions-{year}.json"
    raw = read_year_json(pkg, filename, year)
    if raw.get("year") != year:
        msg = (
            f"{filename} year={raw.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)

    mi_raw = raw["mortgage_interest"]
    return Art15DeductionRules(
        year=int(raw["year"]),
        description=raw.get("description", ""),
        ruleset=_try_ruleset(raw),
        mortgage_interest=MortgageInterestRules(
            ceiling=Decimal(str(mi_raw["ceiling"])),
            rate=Decimal(str(mi_raw["rate"])),
            notes=mi_raw.get("notes", ""),
        ),
    )
