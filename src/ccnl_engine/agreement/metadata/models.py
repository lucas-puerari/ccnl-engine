"""CCNLVerification, CCNLValidity, and CCNLMeta models."""

from __future__ import annotations

import datetime as dt
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.metadata.review.models import CCNLReview
from ccnl_engine.agreement.types import PublicPensionFund, TaxSector
from ccnl_engine.agreement.validators import (
    _coerce_legacy_extraction,
    _coerce_legacy_source,
)
from ccnl_engine.provenance.ruleset.models import (
    RulesetReadiness,
    VerificationStatus,
)
from ccnl_engine.provenance.source.extraction.models import ExtractionTrace
from ccnl_engine.provenance.source.models import SourceDocument


class CCNLVerification(BaseModel):
    """Review confidence and traceability for a CCNL data file.

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
        verified_cases: Number of ``verified`` reference cases of the CCNL,
            checked against an output the engine did not produce; the
            schema gate keeps it equal to the cases.
        reviews: Review log, oldest first. An entry is appended for each
            review and never rewritten.
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
    reviews: tuple[CCNLReview, ...] = ()
    owner: str | None = None
    review_due: dt.date | None = None

    @property
    def last_reviewed(self) -> dt.date | None:
        """Day of the latest review, ``None`` when the log is empty."""
        return self.reviews[-1].date if self.reviews else None

    @model_validator(mode="after")
    def _check_log(self) -> Self:
        ids = [review.id for review in self.reviews]
        if len(set(ids)) != len(ids):
            msg = f"verification.reviews ids must be unique: {ids}"
            raise ValueError(msg)
        dates = [review.date for review in self.reviews]
        if dates != sorted(dates):
            msg = "verification.reviews must be ordered oldest first"
            raise ValueError(msg)
        return self


class CCNLValidity(BaseModel):
    """Contractual validity window of the modelled agreement."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    valid_from: dt.date
    valid_until: dt.date | None = None


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
        public_pension_fund: Pension fund of INPS Gestione Dipendenti
            Pubblici the workers enrol in, which sets their INPS rates;
            ``None`` outside the public administrations.
        public_life_insurance: Whether the employers of the CCNL enrol their
            staff in the Assicurazione Sociale Vita, when the CCNL decides
            it (the State does not); ``None`` when its employers differ.
        inps_sectors: INPS sectors the employers applying the CCNL are
            classified in by the activity they carry out (art. 49 L.
            88/1989), when more than one; ``tax_sector`` is among them and
            ``EmployerProfile.inps_sector`` chooses.  ``None``: every
            employer is in ``tax_sector``.
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
    public_pension_fund: PublicPensionFund | None = None
    public_life_insurance: bool | None = None
    inps_sectors: frozenset[TaxSector] | None = Field(None, min_length=2)

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

    @model_validator(mode="after")
    def _check_public_fund(self) -> CCNLMeta:
        public = self.tax_sector is TaxSector.PUBBLICA_AMMINISTRAZIONE
        stated = (self.public_pension_fund, self.public_life_insurance)
        if any(value is not None for value in stated) and not public:
            msg = "public funds are for the public administrations only"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_inps_sectors(self) -> CCNLMeta:
        sectors = self.inps_sectors
        if sectors is not None and self.tax_sector not in sectors:
            msg = f"inps_sectors must include the tax_sector {self.tax_sector}"
            raise ValueError(msg)
        return self

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
