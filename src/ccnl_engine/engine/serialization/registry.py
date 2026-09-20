"""Public type registry for payroll result serialisation.

Maps public result-type names to their classes so callers can round-trip
any registered type without coupling to its module path.

Types are registered lazily on first access to avoid circular imports
between the serialisation layer and the domain modules.
"""

from __future__ import annotations

_RESULT_TYPES: dict[str, type] | None = None


def result_types() -> dict[str, type]:
    """Return the registry of public payroll result types.

    Returns:
        A mapping of class name to class for every registered result type.
        Built lazily on first call to avoid circular imports.
    """
    global _RESULT_TYPES  # noqa: PLW0603
    if _RESULT_TYPES is None:
        from ccnl_engine.engine.payroll.domain.annual_result import (  # noqa: PLC0415
            AnnualEstimate,
        )
        from ccnl_engine.engine.payroll.domain.components import (  # noqa: PLC0415
            Contributions,
            Earnings,
            EmployerCost,
            Taxes,
        )
        from ccnl_engine.engine.payroll.domain.coverage import (  # noqa: PLC0415
            Coverage,
        )
        from ccnl_engine.engine.payroll.domain.period_result import (  # noqa: PLC0415
            PeriodPayroll,
        )

        _RESULT_TYPES = {
            "AnnualEstimate": AnnualEstimate,
            "PeriodPayroll": PeriodPayroll,
            "Earnings": Earnings,
            "Contributions": Contributions,
            "Taxes": Taxes,
            "EmployerCost": EmployerCost,
            "Coverage": Coverage,
        }
    return _RESULT_TYPES
