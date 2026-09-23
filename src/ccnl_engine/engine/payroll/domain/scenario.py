"""Re-exports of public split domain types.

All types formerly in this monolithic module are now in their own files.
This module exists only for import compatibility.

Root entities:

- :class:`Employee` — who the worker is.
- :class:`Employment` — the employment relationship.

Helper sub-objects:

- :class:`Jurisdiction` — region and municipality codes for surtax.
- :class:`Agreement` — individual RAL override or ad-personam supplement.
- :class:`Employer` — employer headcount and second-level allowances.
- :class:`AnnualizedAssumption` — full-year fiscal assumption for estimates.
- :class:`TaxPeriod` — actual work-period data for period payroll pro-rata.
"""

from __future__ import annotations

from ccnl_engine.engine.payroll.domain.annual_input import (
    AnnualEstimateInput as AnnualEstimateInput,
)
from ccnl_engine.engine.payroll.domain.employee import (
    Agreement as Agreement,
)
from ccnl_engine.engine.payroll.domain.employee import (
    Employee as Employee,
)
from ccnl_engine.engine.payroll.domain.employee import (
    Jurisdiction as Jurisdiction,
)
from ccnl_engine.engine.payroll.domain.employer import (
    Employer as Employer,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Employment as Employment,
)
from ccnl_engine.engine.payroll.domain.period_input import (
    PeriodPayrollInput as PeriodPayrollInput,
)
from ccnl_engine.engine.payroll.domain.tax_basis import (
    AnnualizedAssumption as AnnualizedAssumption,
)
from ccnl_engine.engine.payroll.domain.tax_basis import (
    TaxPeriod as TaxPeriod,
)
