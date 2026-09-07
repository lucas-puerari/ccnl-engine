"""RuleProvenance — the leaf of the provenance chain.

A :class:`RuleProvenance` ties one extracted rule to the exact source
document, page and section it came from, together with the extraction
trace that produced it.  Domain models that embody a rule carry one; values
that add a per-period override carry their own.
"""

from pydantic import BaseModel, ConfigDict

from ccnl_engine.engine.provenance.domain.extraction import ExtractionTrace
from ccnl_engine.engine.provenance.domain.source import SourceLocation


class RuleProvenance(BaseModel):
    """Provenance of a single extracted rule.

    Attributes:
        location: Pointer into the source document (page/section/quote).
        extraction: How the rule was extracted and who verified it.
        note: Free-form context (e.g. a known simplification).
    """

    model_config = ConfigDict(extra="forbid")

    location: SourceLocation
    extraction: ExtractionTrace
    note: str | None = None
