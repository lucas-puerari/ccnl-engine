"""Backward-compatible re-export from ccnl_engine.payroll.service.family_deductions."""

from ccnl_engine.payroll.service.family_deductions import *  # noqa: F403
from ccnl_engine.payroll.service.family_deductions import (
    _child_is_eligible as _child_is_eligible,
)
from ccnl_engine.payroll.service.family_deductions import (
    _children_deduction as _children_deduction,
)
from ccnl_engine.payroll.service.family_deductions import (
    _deduction_from_breakpoints as _deduction_from_breakpoints,
)
from ccnl_engine.payroll.service.family_deductions import (
    _interpolate as _interpolate,
)
from ccnl_engine.payroll.service.family_deductions import (
    _other_deduction as _other_deduction,
)
from ccnl_engine.payroll.service.family_deductions import (
    _spouse_deduction as _spouse_deduction,
)
