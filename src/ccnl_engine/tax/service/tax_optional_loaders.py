"""Optional tax rule loaders: sick pay, variable pay, family, TFR revaluation."""

from __future__ import annotations

import importlib.resources
from decimal import Decimal
from typing import Any

from pydantic import ValidationError

from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.errors import (
    DataIntegrityError,
    UnsupportedTaxYearError,
)
from ccnl_engine.tax.domain.family import FamilyDeductionRules
from ccnl_engine.tax.domain.preferential_regime import PreferentialTaxRegime
from ccnl_engine.tax.domain.sick_pay import (
    InpsSickPayRates,
    SickPayBand,
    SickPayCoverage,
)
from ccnl_engine.tax.domain.tfr_revaluation import TfrRevaluationRules
from ccnl_engine.tax.domain.variable_pay import (
    FringeBenefitRules,
    PdRRules,
    VariablePayRules,
)
from ccnl_engine.tax.service.tax_resource_reader import (
    _as_ruleset,
    _read_json,
    _try_ruleset,
    read_year_json,
)


def load_sick_pay_rates() -> InpsSickPayRates:
    """Load INPS statutory sick-pay indemnity rates from the bundled data file.

    The file ``knowledge/inps/data/sick-pay-rates.json`` is not year- or
    sector-specific: statutory sick-pay rates change only by primary
    legislation (D.L. 663/1979, artt. 1-2, conv. L. 33/1980).

    Returns:
        An :class:`~ccnl_engine.tax.domain.sick_pay.InpsSickPayRates`
        with the INPS carenza period, indemnity bands, annual maximum,
        coverage rules and provenance.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.inps.data")
    raw = _read_json(pkg, "sick-pay-rates.json")
    return InpsSickPayRates(
        description=raw.get("description", ""),
        carenza_days=int(raw.get("carenza_days", 3)),
        bands=[SickPayBand(**b) for b in raw.get("bands", [])],
        annual_max_days=int(raw.get("annual_max_days", 180)),
        coverage=tuple(
            SickPayCoverage.model_validate(rule) for rule in raw.get("coverage", [])
        ),
        ruleset=_as_ruleset(raw),
        bands_provenance=_provenance_of({"provenance": raw.get("bands_provenance")}),
    )


def _provenance_of(block: dict[str, Any]) -> RuleProvenance | None:
    """Return the provenance record of a raw data block.

    Returns:
        The validated record, or ``None`` when the block carries none.
    """
    record = block.get("provenance")
    return None if record is None else RuleProvenance.model_validate(record)


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
        A :class:`~ccnl_engine.tax.domain.variable_pay.VariablePayRules`
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
    work_time_raw = raw["notte_festivi_turni"]
    return VariablePayRules(
        year=int(raw["year"]),
        description=raw.get("description", ""),
        fringe_benefit=FringeBenefitRules(
            threshold_standard=Decimal(str(fb_raw["threshold_standard"])),
            threshold_with_children=Decimal(str(fb_raw["threshold_with_children"])),
            ruleset=_as_ruleset(raw),
            provenance=_provenance_of(fb_raw),
        ),
        pdr=PdRRules(
            max_amount=Decimal(str(pdr_raw["max_amount"])),
            flat_tax_rate=Decimal(str(pdr_raw["flat_tax_rate"])),
            income_ceiling=Decimal(str(pdr_raw["income_ceiling"])),
            provenance=_provenance_of(pdr_raw),
        ),
        rinnovo=PreferentialTaxRegime.model_validate({
            **{k: v for k, v in rinnovo_raw.items() if k != "description"},
            "ruleset": _as_ruleset(raw),
        }),
        notte_festivi_turni=PreferentialTaxRegime.model_validate({
            **{k: v for k, v in work_time_raw.items() if k != "description"},
            "ruleset": _as_ruleset(raw),
        }),
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
        A :class:`~ccnl_engine.tax.domain.family.FamilyDeductionRules`
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

    try:
        return FamilyDeductionRules.model_validate({
            **raw,
            "ruleset": _try_ruleset(raw),
        })
    except ValidationError as exc:
        msg = f"{filename} is not a valid family deduction table: {exc}"
        raise DataIntegrityError(msg) from exc


def load_tfr_revaluation_rules(year: int) -> TfrRevaluationRules | None:
    """Load the TFR revaluation rules at 31 December of *year*.

    The file ``knowledge/tax/data/tfr-revaluation-{year}.json`` carries the
    rate of art. 2120 c. 4 c.c., the ISTAT FOI indexes it is computed from
    and the substitute tax of D.Lgs. 47/2000 art. 11.  These are pure law
    and statistics, not sector-specific.

    Args:
        year: Year of the revaluation (e.g. ``2026``).

    Returns:
        The validated rules, or ``None`` when the bundle has no file for
        *year*.

    Raises:
        DataIntegrityError: If the file's ``year`` does not match *year* or
            the file is not a valid revaluation table.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.tax.data")
    filename = f"tfr-revaluation-{year}.json"
    try:
        raw = read_year_json(pkg, filename, year)
    except UnsupportedTaxYearError:
        return None
    try:
        rules = TfrRevaluationRules.model_validate({
            **{k: v for k, v in raw.items() if k != "description"},
            "ruleset": _try_ruleset(raw),
        })
    except ValidationError as exc:
        msg = f"{filename} is not a valid TFR revaluation table: {exc}"
        raise DataIntegrityError(msg) from exc
    if rules.year != year:
        msg = f"{filename} year={rules.year!r} does not match requested year={year!r}"
        raise DataIntegrityError(msg)
    return rules
