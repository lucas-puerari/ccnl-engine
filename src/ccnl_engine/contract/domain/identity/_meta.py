"""CCNLVerification, CCNLValidity, and CCNLMeta models."""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.contract.domain.identity._enums import TaxSector
from ccnl_engine.contract.domain.validation import (
    _coerce_legacy_extraction,
    _coerce_legacy_source,
)
from ccnl_engine.provenance.domain.extraction import ExtractionTrace
from ccnl_engine.provenance.domain.ruleset_identity import (
    RulesetReadiness,
    VerificationStatus,
)
from ccnl_engine.provenance.domain.source import SourceDocument


class CCNLVerification(BaseModel):
    """Human-review confidence and traceability for a CCNL data file.

    Measures *how trustworthy* the values are, orthogonal to field completeness.
    See :class:`CCNLCoverage` for implementation-completeness flags.

    Attributes:
        confidence: Editorial confidence in the data values — ``verified``,
            ``unverified``, or ``needs_review``.
        readiness: Production readiness of the ruleset as a whole —
            ``exploratory``, ``reviewed``, or ``production``. Separate from
            ``confidence``: a ruleset can be ``confidence=verified`` for its
            key values but still ``readiness=exploratory`` if it lacks an
            owner, reference cases, or an update-policy entry. Defaults to
            ``exploratory`` for all unclassified rulesets.
        verified_cases: Number of end-to-end payroll scenarios manually
            cross-checked against a reference payslip or official source.
        last_reviewed: ISO date of the most recent human review.
        human_reviewed_by: Identifier (name or email) of the reviewer.
        owner: Identifier of the person accountable for keeping the
            ruleset current; required for ``production`` by the CI
            evidence gate.
        review_due: ISO date by which the next review is due (the update
            SLA); required for ``production`` by the CI evidence gate.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    confidence: VerificationStatus = VerificationStatus.UNVERIFIED
    readiness: RulesetReadiness = RulesetReadiness.EXPLORATORY
    verified_cases: int = 0
    last_reviewed: date | None = None
    human_reviewed_by: str | None = None
    owner: str | None = None
    review_due: date | None = None


class CCNLValidity(BaseModel):
    """Contractual validity window of the modelled agreement."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    valid_from: date
    valid_until: date | None = None


class CCNLMeta(BaseModel):
    """Identifying metadata for a CCNL.

    Attributes:
        ccnl_id: Unique slug for the contract
            (e.g. ``"metalmeccanico-federmeccanica"``). Used as
            ``AnnualEstimate.ccnl_id``.
        name: Full name of the collective agreement.
        cnel_code: CNEL registry code for the agreement.
        sector: Human-readable industry sector (e.g. ``"Industria metalmeccanica"``).
        tax_sector: INPS sector classification used to select the contribution-rate
            file. Pass this to ``load_year_rules``.
        signatories: List of employer associations and unions that signed the agreement.
        sources: Primary source references (official gazette, CNEL,
            association websites) as :class:`SourceDocument` objects.
        extraction: Metadata about how the data file was produced.
        agreement_date: Date of the most recent renewal agreement, ISO 8601 string.
            ``None`` if not yet modelled.
        validity: Contractual validity window. ``None`` if not specified.
        workers_estimate: Approximate number of workers covered by this agreement,
            as a human-readable string (e.g. ``"~800k"``). Based on CNEL and INPS
            estimates. Empty string when unknown.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    ccnl_id: str
    name: str
    cnel_code: str
    sector: str
    tax_sector: TaxSector
    signatories: tuple[str, ...]
    sources: tuple[SourceDocument, ...]
    extraction: ExtractionTrace
    agreement_date: str | None = None
    validity: CCNLValidity | None = None
    workers_estimate: str = ""

    @property
    def withholding_agent(self) -> bool:
        """Whether the employers of this CCNL withhold IRPEF (sostituto d'imposta).

        The withholding agents are listed by art. 23 c. 1 D.P.R. 600/1973
        (in force until 31 December 2026) and, from 1 January 2027, by
        art. 33 c. 1 of the testo unico of D.Lgs. 33/2025 (art. 243 as
        amended by D.L. 200/2025 art. 4): entities, companies, partnerships,
        individuals running a business or a profession, and the condominium.
        A household employer (datore di lavoro domestico) is a private
        individual outside that list, so a domestic worker declares the
        income personally.  Derived from :attr:`tax_sector` so that no data
        file can contradict it.
        """
        return self.tax_sector is not TaxSector.LAVORO_DOMESTICO

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_meta(cls, data: Any) -> Any:  # noqa: ANN401
        if not isinstance(data, dict):
            return data
        sources = data.get("sources")
        if isinstance(sources, list) and any(
            isinstance(s, dict) and "document_id" not in s for s in sources
        ):
            data = {**data, "sources": [_coerce_legacy_source(s) for s in sources]}
        extraction = data.get("extraction")
        if isinstance(extraction, dict) and "extraction_timestamp" not in extraction:
            data = {**data, "extraction": _coerce_legacy_extraction(extraction, data)}
        return data
