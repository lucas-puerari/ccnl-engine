"""Credit for foreign taxes applied by the withholding agent at the conguaglio.

Art. 23 c. 3 DPR 600/1973 (art. 33 c. 4 D.Lgs. 33/2025 from 2027) admits
the foreign taxes paid "a titolo definitivo" on employment income produced
abroad "in detrazione fino a concorrenza dell'imposta relativa ai predetti
redditi prodotti all'estero", separately for each State.  Art. 165 c. 1
TUIR sets the measure: the foreign taxes "sono ammesse in detrazione
dall'imposta netta dovuta fino alla concorrenza della quota d'imposta
corrispondente al rapporto tra i redditi prodotti all'estero ed il reddito
complessivo".  Circ. AdE 9/E/2015 par. 3.1 reads two limits, the quota of
Italian tax (LIMITE 1) and the imposta netta of the year (LIMITE 2).  The
instructions of Redditi PF 2026 (fascicolo 3, quadro CE, sezione I-A) take
the quota on the imposta lorda: the credit "spetta fino a concorrenza della
quota d'imposta lorda italiana corrispondente al rapporto tra il reddito
prodotto all'estero ed il reddito complessivo [...] e sempre comunque nel
limite dell'imposta netta italiana", the ratio brought back to 1 when it
exceeds it.  So, for each State:

    credit = min(foreign tax, imposta lorda x min(1, income / taxable))

and the credits of all States together at most the imposta netta.  The
withholding agent knows only the employment income it pays, so the
reddito complessivo is the annual taxable income of the conguaglio.

Not modelled, left to the tax return: foreign income taxed in Italy in an
earlier year (art. 165 c. 7, allowed at the conguaglio by the second
sentence of the art. 23 rule), the carry-over of the excess foreign tax
(art. 165 c. 6) and the refund of a credit above the imposta netta (art. 11
c. 4 TUIR).  The regional and municipal surtax are due only when the IRPEF
net of this credit is due (D.Lgs. 446/1997 art. 50 c. 2, "crediti di cui
agli articoli 14 e 15" of the TUIR in its former numbering; D.Lgs. 360/1998
art. 1 c. 4, "credito di cui all'articolo 165").  From 1 January 2027 the
testo unico of D.Lgs. 117/2026 carries art. 165 TUIR as its art. 185
("Credito d'imposta per i redditi prodotti all'estero"), c. 1 unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationStatus,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.taxation.inputs_foreign_tax import ForeignTaxPaid
    from ccnl_engine.payroll.taxation.rules_irpef_net import NetIrpef
    from ccnl_engine.tax.annual.models import YearRules

__all__ = ["CAPABILITY", "ForeignCredit", "foreign_credit_rule", "foreign_tax_credit"]

CAPABILITY = "foreign_tax_credit"
#: First tax year of the testo unico of D.Lgs. 117/2026.
_TESTO_UNICO_FROM = 2027
_ZERO = Decimal(0)
_ONE = Decimal(1)


def foreign_credit_rule(tax_year: int) -> tuple[str, str]:
    """Return the rule id and the citation of the credit for ``tax_year``.

    Returns:
        Art. 185 c. 1 D.Lgs. 117/2026 from 2027, art. 165 c. 1 TUIR before.
    """
    if tax_year >= _TESTO_UNICO_FROM:
        return "dlgs117-2026-art185-c1", "Art. 185 D.Lgs. 117/2026"
    return "tuir-art165-c1", "Art. 165 TUIR"


@dataclass(frozen=True, slots=True)
class ForeignCredit:
    """Foreign tax credit of the conguaglio and the decision behind it.

    Attributes:
        amount: Credit deducted from the imposta netta.
        decision: How it was computed, per State.
    """

    amount: Decimal
    decision: CalculationDecision


def _quota(gross: Decimal, income: Decimal, taxable: Decimal) -> Decimal:
    """Return the Italian tax on ``income``: LIMITE 1 of circ. 9/E/2015.

    Returns:
        ``gross`` times the ratio of ``income`` to ``taxable``, at most 1;
        zero without taxable income.
    """
    if taxable <= _ZERO:
        return _ZERO
    return money(gross * min(_ONE, income / taxable))


def foreign_tax_credit(
    taxes: tuple[ForeignTaxPaid, ...],
    taxable: Decimal,
    annual: NetIrpef,
    rules: YearRules,
) -> ForeignCredit | None:
    """Return the credit of ``taxes`` against the IRPEF of the conguaglio.

    Args:
        taxes: Foreign taxes paid, one per State.
        taxable: Annual taxable income of the conguaglio.
        annual: Net annual IRPEF before the credit.
        rules: Year rules, whose version the decision records.

    Returns:
        ``None`` without foreign taxes.  Otherwise the credit, with reason
        ``credit_applied`` or ``limited_to_net_tax`` when the imposta netta
        is below the credits of the States.
    """
    if not taxes:
        return None
    inputs: dict[str, Decimal | str] = {
        "taxable_income": taxable,
        "irpef_gross": annual.gross,
        "irpef_net": annual.net_before_credit,
    }
    total = _ZERO
    for paid in taxes:
        quota = _quota(annual.gross, paid.income, taxable)
        credit = min(paid.tax, quota)
        total += credit
        key = paid.country.lower()
        inputs[f"{key}_income"] = paid.income
        inputs[f"{key}_tax"] = paid.tax
        inputs[f"{key}_quota"] = quota
        inputs[f"{key}_credit"] = credit
    amount = min(total, annual.net_before_credit)
    decision = CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code="credit_applied" if amount == total else "limited_to_net_tax",
        rule=foreign_credit_rule(rules.year)[0],
        rule_version=(
            str(rules.year) if rules.ruleset is None else rules.ruleset.version
        ),
        inputs=inputs,
        amount=amount,
    )
    return ForeignCredit(amount, decision)
