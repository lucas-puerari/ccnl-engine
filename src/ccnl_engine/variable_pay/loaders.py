"""Statutory variable-pay rules of a tax year from the bundle."""

from __future__ import annotations

from decimal import Decimal
from functools import cache

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.regime.models import PreferentialTaxRegime
from ccnl_engine.sector.raw.loaders import (
    _as_ruleset,
    _provenance_of,
    read_year_json,
)
from ccnl_engine.variable_pay.models import (
    FringeBenefitRules,
    PdRRules,
    TravelAllowanceRules,
    VariablePayRules,
)


@cache
def load_variable_pay_rules(year: int) -> VariablePayRules:
    """Load statutory variable-pay rules for *year*.

    The file ``knowledge/variable_pay/<year>.json`` is not
    sector-specific.  It carries Art. 51 c. 3 TUIR thresholds, PdR flat-tax
    parameters and the L. 199/2025 substitute-tax regimes, which vary by
    fiscal year but not by sector or CCNL.

    Args:
        year: Fiscal year (e.g. ``2026``); the ``year`` field inside the
            file is validated to match.

    Returns:
        A :class:`~ccnl_engine.variable_pay.models.VariablePayRules`
        with thresholds and PdR parameters already validated.

    Raises:
        DataIntegrityError: If the file's ``year`` field does not match *year*.

    A year without a file raises
    :class:`~ccnl_engine.errors.UnsupportedTaxYearError`.
    """
    filename = f"variable_pay/{year}.json"
    raw = read_year_json(filename, year)
    if raw.get("year") != year:
        msg = (
            f"{filename} year={raw.get('year')!r} "
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
        travel_allowance=TravelAllowanceRules.model_validate({
            **{k: v for k, v in raw["travel_allowance"].items() if k != "description"},
            "ruleset": _as_ruleset(raw),
        }),
        ruleset=_as_ruleset(raw),
    )
