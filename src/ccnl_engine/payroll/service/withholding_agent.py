"""Payroll taxes of an employer that is not a withholding agent.

Only the sostituti d'imposta listed by art. 23 c. 1 D.P.R. 600/1973 (in
force until 31 December 2026) and, from 1 January 2027, by art. 33 c. 1 of
the testo unico of D.Lgs. 33/2025 (art. 243 as amended by D.L. 200/2025
art. 4) withhold IRPEF on employment income.  A household employer (datore
di lavoro domestico) is not among them, so on its payslips:

- no IRPEF is withheld and no conguaglio is run;
- no regional or municipal surtax is withheld: both are determined and
  withheld by the sostituti of art. 23 (D.Lgs. 446/1997 art. 50 c. 4,
  D.Lgs. 360/1998 art. 1 c. 5);
- no trattamento integrativo is paid: the sostituti of art. 23 recognize it
  (D.L. 3/2020 art. 1 c. 3);
- no somma esente and no ulteriore detrazione are recognized: the sostituti
  of art. 23 recognize them (L. 207/2024 art. 1 c. 7);
- no substitute tax is withheld: the regimes are applied by the withholding
  agent.

The worker declares the income personally.  Each skipped capability records
a final decision with reason :data:`NOT_WITHHOLDING_AGENT` and a nil amount.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.provenance.domain.source import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = [
    "NOT_WITHHOLDING_AGENT",
    "PAYROLL_TAX_CAPABILITIES",
    "not_withholding_agent_decision",
    "not_withholding_agent_decisions",
]

#: Reason code of every capability a non-withholding employer skips.
NOT_WITHHOLDING_AGENT = "not_withholding_agent"

#: Capabilities only a withholding agent computes on the payslip.
PAYROLL_TAX_CAPABILITIES = (
    "irpef",
    "family_deductions",
    "ulteriore_detrazione_lavoro",
    "trattamento_integrativo",
    "somma_esente",
    "addizionale_regionale",
    "addizionale_comunale",
)

#: First tax year of the testo unico of D.Lgs. 33/2025 (art. 243).
_TESTO_UNICO_FROM = 2027
_ZERO = Decimal(0)

_DPR_600 = SourceLocation(
    source_document=SourceDocument(
        document_id="dpr-600-1973",
        title="D.P.R. 29 settembre 1973, n. 600",
        kind=SourceKind.DPR,
        url=(
            "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:"
            "decreto.del.presidente.della.repubblica:1973-09-29;600~art23"
        ),
    ),
    section="art. 23 c. 1",
)
_DLGS_33 = SourceLocation(
    source_document=SourceDocument(
        document_id="dlgs-33-2025",
        title=("D.Lgs. 24 marzo 2025, n. 33, testo unico versamenti e riscossione"),
        kind=SourceKind.DLGS,
        url="https://www.gazzettaufficiale.it/eli/id/2025/03/26/25G00044/sg",
    ),
    section="art. 33 c. 1",
)


def _rule(tax_year: int) -> tuple[str, SourceLocation]:
    """Return the rule id and source listing the withholding agents.

    Returns:
        Art. 33 D.Lgs. 33/2025 from 2027, art. 23 D.P.R. 600/1973 before.
    """
    if tax_year >= _TESTO_UNICO_FROM:
        return "dlgs33-2025-art33-c1", _DLGS_33
    return "dpr600-1973-art23-c1", _DPR_600


def not_withholding_agent_decision(
    capability: str,
    tax_year: int,
    inputs: Mapping[str, Decimal | str] | None = None,
) -> CalculationDecision:
    """Return the decision that ``capability`` does not apply to the employer.

    Args:
        capability: Catalog feature the employer does not compute.
        tax_year: Tax year of the run, the rule version.
        inputs: Inputs to record, e.g. the amount left to ordinary income.

    Returns:
        A final decision with reason :data:`NOT_WITHHOLDING_AGENT` and a
        nil amount.
    """
    rule, source = _rule(tax_year)
    return CalculationDecision(
        capability=capability,
        status=CalculationStatus.FINAL,
        reason_code=NOT_WITHHOLDING_AGENT,
        rule=rule,
        rule_version=str(tax_year),
        inputs=inputs or {},
        source=source,
        amount=_ZERO,
    )


def not_withholding_agent_decisions(tax_year: int) -> tuple[CalculationDecision, ...]:
    """Return one decision per payroll tax capability the employer skips.

    Returns:
        The decisions of :data:`PAYROLL_TAX_CAPABILITIES`, in order.
    """
    return tuple(
        not_withholding_agent_decision(c, tax_year) for c in PAYROLL_TAX_CAPABILITIES
    )
