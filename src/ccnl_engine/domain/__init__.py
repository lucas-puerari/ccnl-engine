"""Domain models shared across ccnl_engine subsystems."""

from ccnl_engine.domain.ccnl import CCNL
from ccnl_engine.domain.employee import Employee
from ccnl_engine.domain.employer import Employer
from ccnl_engine.domain.employment import Employment

__all__ = ["CCNL", "Employee", "Employer", "Employment"]
