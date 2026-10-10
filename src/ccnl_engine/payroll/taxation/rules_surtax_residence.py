"""Surtax a withholding run cannot place for lack of the worker's residence.

The regional and municipal surtax is due to the region and to the
municipality of the worker's domicilio fiscale on 1 January of the tax
year (D.Lgs. 446/1997 art. 50 c. 5, D.Lgs. 360/1998 art. 1 c. 4).  A
request that leaves ``regione`` or ``comune_belfiore`` unset does not say
that no surtax is due: it leaves the jurisdiction, hence the scope of the
surtax, undetermined.  Each such run of a withholding agent records a
``residence_unknown`` decision (incomplete, amount ``None``) naming the
missing fact, in the notation of the
``requirement_unresolved`` blocker it comes with.
"""

from __future__ import annotations

from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationStatus,
)
from ccnl_engine.payroll.taxation.rules_surtax_stage import (
    MUNICIPAL_SURTAX,
    REGIONAL_SURTAX,
)
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)

__all__ = ["RESIDENCE_UNKNOWN", "residence_unknown_decisions"]

#: Reason of a surtax decision left undetermined by an unset residence fact.
RESIDENCE_UNKNOWN = "residence_unknown"

_REGIONAL_SOURCE = SourceLocation(
    source_document=SourceDocument(
        document_id="dlgs-446-1997",
        title="D.Lgs. 15 dicembre 1997, n. 446",
        kind=SourceKind.DLGS,
        url=(
            "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:"
            "decreto.legislativo:1997-12-15;446~art50"
        ),
    ),
    section="art. 50 c. 5",
    quote=(
        "alla regione in cui il contribuente ha il domicilio fiscale alla "
        "data del 1° gennaio dell'anno cui si riferisce l'addizionale stessa"
    ),
)
_MUNICIPAL_SOURCE = SourceLocation(
    source_document=SourceDocument(
        document_id="dlgs-360-1998",
        title="D.Lgs. 28 settembre 1998, n. 360",
        kind=SourceKind.DLGS,
        url=(
            "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:"
            "decreto.legislativo:1998-09-28;360~art1"
        ),
    ),
    section="art. 1 c. 4",
    quote=(
        "L'addizionale è dovuta alla provincia e al comune nel quale il "
        "contribuente ha il domicilio fiscale alla data del 1° gennaio "
        "dell'anno cui si riferisce l'addizionale stessa"
    ),
)

#: Capability, request fact, rule id and source of each surtax.
_JURISDICTIONS = (
    (REGIONAL_SURTAX, "facts.regione", "dlgs446-1997-art50-c5", _REGIONAL_SOURCE),
    (
        MUNICIPAL_SURTAX,
        "facts.comune_belfiore",
        "dlgs360-1998-art1-c4",
        _MUNICIPAL_SOURCE,
    ),
)


def residence_unknown_decisions(
    regione: str | None, comune_belfiore: str | None, tax_year: int
) -> tuple[CalculationDecision, ...]:
    """Return one decision per surtax whose jurisdiction the request omits.

    Args:
        regione: Region code of the request, ``None`` when not supplied.
        comune_belfiore: Belfiore code of the request, ``None`` when not
            supplied.
        tax_year: Tax year of the run, the rule version.

    Returns:
        A ``residence_unknown`` decision, incomplete with amount ``None``,
        for the regional surtax when ``regione`` is ``None`` and for the
        municipal surtax when ``comune_belfiore`` is ``None``; its
        ``inputs["fact"]`` names the fact to supply.
    """
    supplied = {REGIONAL_SURTAX: regione, MUNICIPAL_SURTAX: comune_belfiore}
    return tuple(
        CalculationDecision(
            capability=capability,
            status=CalculationStatus.INCOMPLETE,
            reason_code=RESIDENCE_UNKNOWN,
            rule=rule,
            rule_version=str(tax_year),
            inputs={"fact": fact, "tax_year": str(tax_year)},
            source=source,
            amount=None,
        )
        for capability, fact, rule, source in _JURISDICTIONS
        if supplied[capability] is None
    )
