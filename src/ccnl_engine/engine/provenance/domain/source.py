"""Source-document models for the provenance chain.

The provenance chain walks from a physical source document, through the
specific clause (page/section), to the extracted rule that a domain model
embodies.  :class:`SourceDocument` identifies a document once; every rule
that cites it references the same instance so a single document's details
live in one place.
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SourceKind(StrEnum):
    """Category of a source document."""

    GAZZETTA = "gazzetta"
    CNEL = "cnel"
    ASSOCIAZIONE = "associazione"
    INPS_CIRCOLARE = "inps_circolare"
    LEGGE = "legge"
    DPR = "dpr"
    DL = "dl"
    DPR_DECRETO = "dpr_decreto"
    TABELLA_RETRIBUTIVA = "tabella_retributiva"
    RIVISTA = "rivista"
    ALTRO = "altro"


class SourceDocument(BaseModel):
    """A primary source document for one or more extracted rules.

    Attributes:
        document_id: Stable slug identifying the document across rulesets
            (e.g. ``"inps-circolare-9-2026"``).
        title: Human-readable title of the document.
        kind: Category of the document (see :class:`SourceKind`).
        url: Locator for the document (or ``"unavailable"`` if not recorded).
        pages: Page ranges (e.g. ``["12-14"]``) that hold the cited content.
        published_on: Publication date of the document, when known.
        jurisdiction: Legal jurisdiction (defaults to ``"it"``).
    """

    model_config = ConfigDict(extra="forbid")

    document_id: str
    title: str
    kind: SourceKind
    url: str = Field(default="unavailable")
    pages: list[str] = Field(default=[])
    published_on: date | None = None
    jurisdiction: str = "it"


class SourceLocation(BaseModel):
    """A precise pointer into a :class:`SourceDocument`.

    Attributes:
        source_document: The document being cited.
        page: Page (or page range) holding the cited content; ``None`` when
            the document is not paginated.
        section: Article/clause reference (e.g. ``"Art. 3 c. 773 L. 296/2006"``);
            ``None`` when the whole document applies.
        quote: Exact excerpt of the source text backing the rule.
    """

    model_config = ConfigDict(extra="forbid")

    source_document: SourceDocument
    page: str | None = None
    section: str | None = None
    quote: str | None = None
