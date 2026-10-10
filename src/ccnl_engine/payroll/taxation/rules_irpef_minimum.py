"""Decision on the art. 13 minimum the withholding proportions to the days.

Art. 13 c. 1 lett. a) TUIR: up to 15,000 EUR the deduction "non può essere
inferiore a 690 euro", 1,380 EUR for a fixed-term employment.  For an
employment shorter than the year the withholding agent proportions the
minimum to the days of work and tells the worker, with code AN of the
Certificazione Unica, that the tax return grants it for the whole year
(Agenzia delle Entrate, istruzioni CU 2026, punto 367, p. 33, and Tabella F,
p. 93).  The 730 grants the minimum whole, not proportioned to the days
(Allegato C to the 730/2026 instructions, par. 19.9.1).  The decision
records the part of the minimum left to the tax return.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationStatus,
)
from ccnl_engine.payroll.taxation.rules_irpef_deduction import (
    minimum_left_to_tax_return,
)
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)

if TYPE_CHECKING:
    from ccnl_engine.tax.annual.models import YearRules

__all__ = ["MINIMUM_PROPORTIONED", "minimum_decision"]

#: Reason of the decision: the minimum was proportioned to the days.
MINIMUM_PROPORTIONED = "minimum_proportioned_to_days"

_CAPABILITY = "irpef"
_RULE = "tuir-art13-c1-a-minimum"
_ZERO = Decimal(0)

_CU_INSTRUCTIONS = SourceLocation(
    source_document=SourceDocument(
        document_id="ade-istruzioni-cu-2026",
        title=(
            "Agenzia delle Entrate, Certificazione Unica 2026, istruzioni per "
            "la compilazione, aggiornate al 24 febbraio 2026"
        ),
        kind=SourceKind.AMMINISTRAZIONE,
        url=(
            "https://www.agenziaentrate.gov.it/portale/documents/20143/9602395/"
            "CU_istr_2026_agg+24+02.pdf/4184818b-05a3-acce-5956-70811c7d2233"
        ),
        pages=("33", "93"),
        sha256="a6ccf7cf53edcbd0d084c2266868649f8d17c348644401b540efd5e3fc95e841",
    ),
    page="33",
    section="punto 367; Tabella F, codice AN",
    quote=(
        "Nel caso di rapporti di lavoro a tempo determinato o a tempo "
        "indeterminato di durata inferiore all'anno (inizio o cessazione del "
        "rapporto di lavoro nel corso dell'anno), limitatamente ai redditi di "
        "cui ai punti 1 e 2, il sostituto deve ragguagliare anche la "
        "detrazione minima al periodo di lavoro"
    ),
)


def minimum_decision(
    rules: YearRules, taxable: Decimal, days: int, *, fixed_term: bool
) -> CalculationDecision | None:
    """Return the decision on the minimum left to the tax return, if any.

    Args:
        rules: Year rules of the withholding.
        taxable: Annual taxable income of the withholding.
        days: Days of work in the tax year, at most 365.
        fixed_term: Whether an employment of the year is fixed-term.

    Returns:
        A final ``irpef`` decision with reason ``minimum_proportioned_to_days``
        when the whole minimum exceeds the deduction of the withholding; its
        ``tax_return_balance`` input is the difference the tax return
        grants.  ``None`` otherwise.  It carries no amount: the withholding
        posts none for it.
    """
    constants = rules.work_deduction
    balance = minimum_left_to_tax_return(
        taxable, days, constants, fixed_term=fixed_term
    )
    if balance <= _ZERO:
        return None
    floor = constants.minimum
    return CalculationDecision(
        capability=_CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code=MINIMUM_PROPORTIONED,
        rule=_RULE,
        rule_version=(
            str(rules.year) if rules.ruleset is None else rules.ruleset.version
        ),
        inputs={
            "taxable_income": taxable,
            "eligible_work_days": str(days),
            "contract": "fixed_term" if fixed_term else "open_ended",
            "minimum": floor.fixed_term if fixed_term else floor.open_ended,
            "tax_return_balance": balance,
        },
        source=_CU_INSTRUCTIONS,
    )
