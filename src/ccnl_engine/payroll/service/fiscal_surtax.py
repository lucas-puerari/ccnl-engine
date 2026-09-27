"""Surtax stage: addizionale regionale e comunale, with the decision taken.

Each jurisdiction the caller supplies yields one
:class:`~ccnl_engine.payroll.domain.decisions.CalculationDecision`.  The
surtax of the year is determined only by its conguaglio; any other run
takes ``determined_at_conguaglio`` (final, amount 0) for a known table and
``table_unknown`` for an unknown one.  On the conguaglio:

- ``no_irpef_due`` (final, amount 0): the IRPEF net of its deductions is
  zero, so no surtax is due (D.Lgs. 446/1997 art. 50 c. 2 for the regional,
  D.Lgs. 360/1998 art. 1 c. 4 for the municipal; the foreign tax credit
  they also net, art. 165 TUIR, is not modelled);
- ``below_exemption_threshold`` (final, amount 0): the regional or
  municipal exemption threshold covers the taxable income;
- ``table_applied`` (final): the bundled table of the tax year was
  applied; for a regional row this includes its whole-income rate and its
  income-only deductions;
- ``dependent_provisions_not_applied`` (provisional): the regional row has
  provisions for dependents or disability the engine does not apply, and
  the worker declares a child or a disabled dependent; the surtax without
  them is applied and a provisional issue quotes the provisions;
- ``prior_year_rates_applied`` (provisional): the municipal row holds the
  rates of an earlier year (no delibera of the tax year published, or a
  table of advance rates, D.Lgs. 360/1998 art. 1 c. 4), not those of the
  tax year the conguaglio needs; they are applied and a provisional
  :class:`~ccnl_engine.payroll.domain.decisions.CalculationIssue` names
  the rates year;
- ``specific_exemptions_not_applied`` (provisional): the municipal row
  has exemptions for a category of income only, which the engine does not
  apply; a provisional issue quotes them;
- ``table_unknown`` (incomplete, amount ``None``): the code is well formed
  but the tax year table has no row for it.  The amount withheld is zero
  and a :class:`~ccnl_engine.payroll.domain.decisions.CalculationIssue`
  marks the result as not payable.

Decision amounts are the annual surtax of the tax year, computed by its
conguaglio; how it is withheld is decided by
:mod:`~ccnl_engine.payroll.application.amounts._surtax`.
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
from ccnl_engine.payroll.service.surtax_table import (
    DEPENDENT_PROVISIONS_ISSUE,
    SPECIFIC_EXEMPTIONS_ISSUE,
    SurtaxTable,
    has_dependent_child_or_disability,
    regional_surtax_amount,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.tax.domain.surtax_rules import (
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


def _regional(
    table: SurtaxTable,
    entry: RegionaleEntry | None,
    irpef_due: Decimal,
    family: FamilyComposition | None,
) -> tuple[CalculationDecision, tuple[CalculationIssue, ...]]:
    if irpef_due == _ZERO:
        decision = table.decide("no_irpef_due", _ZERO)
    elif entry is None:
        decision = table.decide("table_unknown", None)
    elif table.taxable_income <= entry.exemption_threshold:
        decision = table.decide("below_exemption_threshold", _ZERO)
    else:
        amount = regional_surtax_amount(table.taxable_income, entry)
        if (
            entry.dependent_provisions is None
            or amount == _ZERO
            or not has_dependent_child_or_disability(family)
        ):
            decision = table.decide("table_applied", amount)
        else:
            decision = table.decide(
                "dependent_provisions_not_applied",
                amount,
                CalculationStatus.PROVISIONAL,
            )
            issue = table.provisional_issue(
                DEPENDENT_PROVISIONS_ISSUE,
                "the regional provisions for dependents or disability are not "
                f"applied and may lower the surtax: {entry.dependent_provisions}",
            )
            return decision, table.issues_of(decision, issue)
    return decision, table.issues_of(decision)


def _municipal(
    table: SurtaxTable,
    entry: ComunaleEntry | None,
    surtax: SurtaxRules,
    irpef_due: Decimal,
) -> tuple[CalculationDecision, tuple[CalculationIssue, ...]]:
    if irpef_due == _ZERO:
        decision = table.decide("no_irpef_due", _ZERO)
        return decision, table.issues_of(decision)
    if entry is None:
        decision = table.decide("table_unknown", None)
        return decision, table.issues_of(decision)
    threshold = entry.exemption_threshold
    if table.taxable_income <= threshold:
        decision = table.decide("below_exemption_threshold", _ZERO)
        return decision, table.issues_of(decision)
    amount = _irpef.surtax_from_brackets(
        table.taxable_income, entry.brackets, threshold
    )
    extra: tuple[CalculationIssue, ...] = ()
    if entry.specific_exemptions and amount > _ZERO:
        extra = (
            table.provisional_issue(
                SPECIFIC_EXEMPTIONS_ISSUE,
                "exemptions for a category of income are not applied and may "
                "cancel the surtax: " + "; ".join(entry.specific_exemptions),
            ),
        )
    rates_year = entry.rates_year
    if surtax.comunale_rates_are_advance:
        rates_year = surtax.year - 1
    if rates_year is not None and rates_year < surtax.year:
        decision = table.decide(
            "prior_year_rates_applied",
            amount,
            CalculationStatus.PROVISIONAL,
            rates_year=str(rates_year),
        )
    elif extra:
        decision = table.decide(
            "specific_exemptions_not_applied", amount, CalculationStatus.PROVISIONAL
        )
    else:
        decision = table.decide("table_applied", amount)
    return decision, table.issues_of(decision, *extra)


def _deferred(
    table: SurtaxTable, entry: object | None
) -> tuple[CalculationDecision, tuple[CalculationIssue, ...]]:
    if entry is None:
        decision = table.decide("table_unknown", None)
    else:
        decision = table.decide("determined_at_conguaglio", _ZERO)
    return decision, table.issues_of(decision)


def compute_surtax(
    taxable_income: Decimal,
    surtax: SurtaxRules,
    *,
    regione: str | None,
    comune_belfiore: str | None,
    irpef_due: Decimal,
    at_conguaglio: bool = True,
    family_composition: FamilyComposition | None = None,
) -> SurtaxOutcome:
    """Compute the annual regional and municipal surtax and their decisions.

    Args:
        taxable_income: Annual IRPEF taxable income of the conguaglio.
        surtax: Bundled surtax tables of the tax year.
        regione: Well-formed region code, or ``None`` to skip.
        comune_belfiore: Well-formed Belfiore code, or ``None`` to skip.
        irpef_due: Net annual IRPEF, gross less the deductions; no surtax
            is due when it is zero.
        at_conguaglio: Whether the run is the conguaglio of the tax year.
            On any other run the surtax is not determined: a known table
            yields ``determined_at_conguaglio`` with amount 0, an unknown
            one ``table_unknown`` as at the conguaglio.
        family_composition: Dependents of the worker; a declared child or
            disabled dependent makes a regional row with provisions for
            dependents provisional, since they are not applied.

    Returns:
        The annual amounts, one decision per supplied jurisdiction and the
        issues of each: unknown table, rates of an earlier year, provisions
        not applied.
    """
    decisions: list[CalculationDecision] = []
    issues: list[CalculationIssue] = []
    if regione is not None:
        name = region_table_name(regione)
        reg_entry = None if name is None else surtax.regionale.get(name)
        table = SurtaxTable(
            REGIONAL_SURTAX,
            _UNKNOWN_ISSUE_CODES[REGIONAL_SURTAX],
            regione,
            None if reg_entry is None else name,
            surtax.regional_ruleset,
            surtax.year,
            taxable_income,
        )
        decision, found = (
            _regional(table, reg_entry, irpef_due, family_composition)
            if at_conguaglio
            else _deferred(table, reg_entry)
        )
        decisions.append(decision)
        issues.extend(found)
    if comune_belfiore is not None:
        com_entry = surtax.comunale.get(comune_belfiore)
        table = SurtaxTable(
            MUNICIPAL_SURTAX,
            _UNKNOWN_ISSUE_CODES[MUNICIPAL_SURTAX],
            comune_belfiore,
            None if com_entry is None else com_entry.nome,
            surtax.municipal_ruleset,
            surtax.year,
            taxable_income,
        )
        decision, found = (
            _municipal(table, com_entry, surtax, irpef_due)
            if at_conguaglio
            else _deferred(table, com_entry)
        )
        decisions.append(decision)
        issues.extend(found)
    amounts = {d.capability: d.amount or _ZERO for d in decisions}
    return SurtaxOutcome(
        regional=amounts.get(REGIONAL_SURTAX, _ZERO),
        municipal=amounts.get(MUNICIPAL_SURTAX, _ZERO),
        decisions=tuple(decisions),
        issues=tuple(issues),
    )
