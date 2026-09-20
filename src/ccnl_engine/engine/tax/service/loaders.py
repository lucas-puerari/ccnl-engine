"""Tax year rules loader — re-exports from split modules for backwards compatibility."""

from __future__ import annotations

from ccnl_engine.engine.tax.service.tax_annual_assembler import (
    _load_year_rules_cached as _load_year_rules_cached,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_annual_assembler import (
    load_year_rules as load_year_rules,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_optional_loaders import (
    load_art15_deduction_rules as load_art15_deduction_rules,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_optional_loaders import (
    load_family_deduction_rules as load_family_deduction_rules,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_optional_loaders import (
    load_sick_pay_rates as load_sick_pay_rates,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_optional_loaders import (
    load_variable_pay_rules as load_variable_pay_rules,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_resource_reader import (
    _try_ruleset as _try_ruleset,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_resource_reader import (
    _verify_ruleset_hash as _verify_ruleset_hash,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_resource_reader import (
    read_inps_rules_raw as read_inps_rules_raw,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_resource_reader import (
    read_tax_rules_raw as read_tax_rules_raw,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_tier_resolver import (
    _assert_tier_integrity as _assert_tier_integrity,  # noqa: PLC0414
)
from ccnl_engine.engine.tax.service.tax_tier_resolver import (
    _resolve_tier as _resolve_tier,  # noqa: PLC0414
)

__all__ = [
    "_assert_tier_integrity",
    "_load_year_rules_cached",
    "_resolve_tier",
    "_try_ruleset",
    "_verify_ruleset_hash",
    "load_art15_deduction_rules",
    "load_family_deduction_rules",
    "load_sick_pay_rates",
    "load_variable_pay_rules",
    "load_year_rules",
    "read_inps_rules_raw",
    "read_tax_rules_raw",
]
