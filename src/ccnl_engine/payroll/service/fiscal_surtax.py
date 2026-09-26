"""Surtax stage: addizionale regionale e comunale, with the decision taken.

Each jurisdiction the caller supplies yields one
:class:`~ccnl_engine.payroll.domain.decisions.CalculationDecision`:

- ``no_irpef_due`` (final, amount 0): the IRPEF net of its deductions is
  zero, so no surtax is due (D.Lgs. 446/1997 art. 50 c. 2 for the regional,
  D.Lgs. 360/1998 art. 1 c. 4 for the municipal; the foreign tax credit
  they also net is not modelled);
- ``below_exemption_threshold`` (final, amount 0): the municipal exemption
  threshold covers the taxable income;
- ``table_applied`` or ``advance_applied`` (final): the bundled table was
  applied, the second one when the municipal rates only give the advance;
- ``table_unknown`` (incomplete, amount ``None``): the code is well formed
  but the tax year table has no row for it.  The amount withheld is zero
  and a :class:`~ccnl_engine.payroll.domain.decisions.CalculationIssue`
  marks the result as not payable.

Decision amounts are annual amounts for the tax year, before the split over
the withholding slots.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.jurisdiction import region_table_name
from ccnl_engine.payroll.service import irpef as _irpef
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.metadata import RulesetIdentity
    from ccnl_engine.engine.surtax.domain.rules import (
        ComunaleEntry,
        RegionaleEntry,
        SurtaxRules,
    )

__all__ = [
    "MUNICIPAL_SURTAX",
    "REGIONAL_SURTAX",
    "SurtaxOutcome",
    "compute_surtax",
]

_ZERO = Decimal(0)

#: Capability of the regional surtax decision, as named in the catalog.
REGIONAL_SURTAX = "addizionale_regionale"
#: Capability of the municipal surtax decision, as named in the catalog.
MUNICIPAL_SURTAX = "addizionale_comunale"

_UNKNOWN_ISSUE_CODES = {
    REGIONAL_SURTAX: "regional_surtax_unknown",
    MUNICIPAL_SURTAX: "municipal_surtax_unknown",
}


@dataclass(frozen=True, slots=True)
class SurtaxOutcome:
    """Annual surtax amounts with the decisions and issues behind them.

    Attributes:
        regional: Annual regional surtax; zero when not due or unknown.
        municipal: Annual municipal surtax; zero when not due or unknown.
        decisions: One decision per jurisdiction supplied, regional first.
        issues: One incomplete issue per jurisdiction without a table.
    """

    regional: Decimal = _ZERO
    municipal: Decimal = _ZERO
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()

    @property
    def total(self) -> Decimal:
        """Regional plus municipal annual surtax."""
        return self.regional + self.municipal


@dataclass(frozen=True, slots=True)
class _Table:
    """The bundled table of one jurisdiction, as looked up for a code."""

    capability: str
    code: str
    name: str | None
    ruleset: RulesetIdentity | None
    tax_year: int
    taxable_income: Decimal

    def decide(
        self,
        reason_code: str,
        amount: Decimal | None,
        **extra: Decimal | str,
    ) -> CalculationDecision:
        default_rule = f"surtax/{self.tax_year}/{self.capability}"
        return CalculationDecision(
            capability=self.capability,
            status=(
                CalculationStatus.FINAL
                if amount is not None
                else CalculationStatus.INCOMPLETE
            ),
            reason_code=reason_code,
            rule=default_rule if self.ruleset is None else self.ruleset.id,
            rule_version=(
                str(self.tax_year) if self.ruleset is None else self.ruleset.version
            ),
            inputs={
                "code": self.code,
                "table": "unknown" if self.name is None else self.name,
                "tax_year": str(self.tax_year),
                "taxable_income": self.taxable_income,
                **extra,
            },
            amount=amount,
        )

    def issues_of(self, decision: CalculationDecision) -> tuple[CalculationIssue, ...]:
        if decision.amount is not None:
            return ()
        issue = CalculationIssue(
            code=_UNKNOWN_ISSUE_CODES[self.capability],
            message=(
                f"{self.capability}: no {self.tax_year} table for code "
                f"{self.code!r}; the surtax is not withheld and the result "
                "must not be paid as is"
            ),
            status=CalculationStatus.INCOMPLETE,
        )
        return (issue,)


def _regional(
    table: _Table, entry: RegionaleEntry | None, irpef_due: Decimal
) -> CalculationDecision:
    if irpef_due == _ZERO:
        return table.decide("no_irpef_due", _ZERO)
    if entry is None:
        return table.decide("table_unknown", None)
    amount = _irpef.surtax_from_brackets(table.taxable_income, entry.brackets)
    return table.decide("table_applied", amount)


def _municipal(
    table: _Table,
    entry: ComunaleEntry | None,
    surtax: SurtaxRules,
    irpef_due: Decimal,
) -> CalculationDecision:
    if irpef_due == _ZERO:
        return table.decide("no_irpef_due", _ZERO)
    if entry is None:
        return table.decide("table_unknown", None)
    threshold = entry.exemption_threshold
    if table.taxable_income <= threshold:
        return table.decide("below_exemption_threshold", _ZERO)
    amount = _irpef.surtax_from_brackets(
        table.taxable_income, entry.brackets, threshold
    )
    if not surtax.comunale_rates_are_advance:
        return table.decide("table_applied", amount)
    fraction = surtax.comunale_advance_fraction
    return table.decide(
        "advance_applied", money(amount * fraction), advance_fraction=fraction
    )


def compute_surtax(
    taxable_income: Decimal,
    surtax: SurtaxRules,
    *,
    regione: str | None,
    comune_belfiore: str | None,
    irpef_due: Decimal,
) -> SurtaxOutcome:
    """Compute the annual regional and municipal surtax and their decisions.

    Args:
        taxable_income: Projected annual IRPEF taxable income.
        surtax: Bundled surtax tables of the tax year.
        regione: Well-formed region code, or ``None`` to skip.
        comune_belfiore: Well-formed Belfiore code, or ``None`` to skip.
        irpef_due: Net annual IRPEF, gross less the deductions; no surtax
            is due when it is zero.

    Returns:
        The annual amounts, one decision per supplied jurisdiction and one
        incomplete issue per jurisdiction whose table is unknown.
    """
    decisions: list[CalculationDecision] = []
    issues: list[CalculationIssue] = []
    if regione is not None:
        name = region_table_name(regione)
        reg_entry = None if name is None else surtax.regionale.get(name)
        table = _Table(
            REGIONAL_SURTAX,
            regione,
            None if reg_entry is None else name,
            surtax.regional_ruleset,
            surtax.year,
            taxable_income,
        )
        decisions.append(_regional(table, reg_entry, irpef_due))
        issues.extend(table.issues_of(decisions[-1]))
    if comune_belfiore is not None:
        com_entry = surtax.comunale.get(comune_belfiore)
        table = _Table(
            MUNICIPAL_SURTAX,
            comune_belfiore,
            None if com_entry is None else com_entry.nome,
            surtax.municipal_ruleset,
            surtax.year,
            taxable_income,
        )
        decisions.append(_municipal(table, com_entry, surtax, irpef_due))
        issues.extend(table.issues_of(decisions[-1]))
    amounts = {d.capability: d.amount or _ZERO for d in decisions}
    return SurtaxOutcome(
        regional=amounts.get(REGIONAL_SURTAX, _ZERO),
        municipal=amounts.get(MUNICIPAL_SURTAX, _ZERO),
        decisions=tuple(decisions),
        issues=tuple(issues),
    )
