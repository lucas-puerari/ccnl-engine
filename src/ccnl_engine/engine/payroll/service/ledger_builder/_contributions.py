"""Post contributions and taxes to the ledger."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.engine.payroll.service.ledger_builder._earnings import _last_day

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay

_ZERO = Decimal(0)


def post_contributions_and_taxes(
    fiscal: FiscalPay, as_of: date, ledger: Ledger
) -> None:
    """Post INPS contributions and IRPEF as ledger entries.

    Posts employee INPS to EMPLOYEE_CONTRIBUTIONS, employer INPS and INAIL to
    EMPLOYER_CONTRIBUTIONS, and net IRPEF to ORDINARY_TAX.  Zero-amount entries
    are silently skipped.

    Args:
        fiscal: The resolved fiscal-pay components.
        as_of: The competence date used to derive the year/month for the entries.
        ledger: The ledger to append to.
    """
    period = CompetencePeriod(year=as_of.year, month=as_of.month)
    yymm = f"{period.year}_{period.month:02d}"
    payment = _last_day(as_of)

    if fiscal.inps_employee_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"inps_employee_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"inps_employee_{yymm}",
                pay_item_kind="inps_employee_contribution",
                account=AccountKind.EMPLOYEE_CONTRIBUTIONS,
                amount=fiscal.inps_employee_annual,
                source_item_id=f"inps_employee_{yymm}",
                policy_decision_id="it/contribution/employee",
            )
        )

    if fiscal.inps_employer_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"inps_employer_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"inps_employer_{yymm}",
                pay_item_kind="inps_employer_contribution",
                account=AccountKind.EMPLOYER_CONTRIBUTIONS,
                amount=fiscal.inps_employer_annual,
                source_item_id=f"inps_employer_{yymm}",
                policy_decision_id="it/contribution/employer",
            )
        )

    if fiscal.inail_employer_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"inail_employer_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"inail_employer_{yymm}",
                pay_item_kind="inail_employer_contribution",
                account=AccountKind.EMPLOYER_CONTRIBUTIONS,
                amount=fiscal.inail_employer_annual,
                source_item_id=f"inail_employer_{yymm}",
                policy_decision_id="it/contribution/employer",
            )
        )

    if fiscal.irpef_net != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"irpef_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"irpef_{yymm}",
                pay_item_kind="irpef",
                account=AccountKind.ORDINARY_TAX,
                amount=fiscal.irpef_net,
                source_item_id=f"irpef_{yymm}",
            )
        )
