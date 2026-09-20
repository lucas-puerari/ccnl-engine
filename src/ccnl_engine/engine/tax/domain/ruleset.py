"""YearRulesRaw and YearRules — aggregate tax parameter models for a fiscal year."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.metadata import RulesetIdentity
from ccnl_engine.engine.primitives import PercentageRate
from ccnl_engine.engine.provenance.domain.extraction import ExtractionTrace
from ccnl_engine.engine.provenance.domain.source import SourceDocument
from ccnl_engine.engine.tax.domain.contribution_rules import (
    ApprenticeRates,
    ApprenticeRawRates,
    DomesticInpsRates,
    InpsRates,
    InpsRawRates,
)
from ccnl_engine.engine.tax.domain.credit_rules import (
    SommaEsenteRules,
    TrattamentoIntegrativoRules,
    UlterioreDetrazioneRules,
)
from ccnl_engine.engine.tax.domain.irpef_rules import (
    IrpefBracket,
    SterilizzazioneDetrazioniRules,
    WorkDeductionRules,
)
from ccnl_engine.engine.tax.domain.tfr_rules import TfrRules


class YearRulesRaw(BaseModel):
    """Full deserialization model for a tax/data/<year>-<sector>.json file.

    Either ``inps`` + ``apprentice`` (standard percentage model) or
    ``domestic_contributions`` (flat per-hour domestic model) must be present.
    Both combinations are validated by ``_check_contribution_model``.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    sector: TaxSector
    ruleset: RulesetIdentity | None = None
    irpef_brackets: list[IrpefBracket]
    fixed_term_additional_rate: PercentageRate
    inps: InpsRawRates | None = None
    apprentice: ApprenticeRawRates | None = None
    domestic_contributions: DomesticInpsRates | None = None
    tfr: TfrRules
    trattamento_integrativo: TrattamentoIntegrativoRules | None = None
    ulteriore_detrazione: UlterioreDetrazioneRules | None = None
    somma_esente: SommaEsenteRules | None = None
    sterilizzazione_detrazioni: SterilizzazioneDetrazioniRules | None = None
    work_deduction: WorkDeductionRules = Field(default_factory=WorkDeductionRules)
    notes: list[str] = Field(default_factory=list)
    sources: list[SourceDocument] = Field(default_factory=list)
    extraction: ExtractionTrace | None = None
    inps_sources: list[SourceDocument] = Field(default_factory=list)
    inps_extraction: ExtractionTrace | None = None

    @model_validator(mode="after")
    def _check_contribution_model(self) -> Self:
        has_inps = self.inps is not None
        has_apprentice = self.apprentice is not None
        has_domestic = self.domestic_contributions is not None
        if has_inps != has_apprentice:
            msg = (
                "'inps' and 'apprentice' must both be present "
                "(standard model) or both absent; "
                "found one without the other"
            )
            raise ValueError(msg)
        has_standard = has_inps
        if not has_standard and not has_domestic:
            msg = (
                "tax file must contain either 'inps' + 'apprentice' "
                "(standard model) or 'domestic_contributions' (domestic model)"
            )
            raise ValueError(msg)
        if has_standard and has_domestic:
            msg = (
                "tax file must not mix 'inps'+'apprentice' (standard model) "
                "with 'domestic_contributions' (domestic model): "
                "the two contribution models are mutually exclusive"
            )
            raise ValueError(msg)
        return self


class YearRules(BaseModel):
    """All statutory tax and contribution parameters for a single fiscal year.

    ``inps`` and ``apprentice`` are set for standard sectors; ``None`` for
    domestic sectors where ``domestic_contributions`` carries the flat-rate
    table instead.  Exactly one contribution model is present (enforced by
    the loader, which mirrors ``YearRulesRaw._check_contribution_model``).
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    ruleset: RulesetIdentity | None = None
    inps_ruleset: RulesetIdentity | None = None
    irpef_brackets: list[IrpefBracket]
    fixed_term_additional_rate: PercentageRate
    inps: InpsRates | None = None
    apprentice: ApprenticeRates | None = None
    domestic_contributions: DomesticInpsRates | None = None
    tfr: TfrRules
    trattamento_integrativo: TrattamentoIntegrativoRules | None = None
    ulteriore_detrazione: UlterioreDetrazioneRules | None = None
    somma_esente: SommaEsenteRules | None = None
    sterilizzazione_detrazioni: SterilizzazioneDetrazioniRules | None = None
    work_deduction: WorkDeductionRules = Field(default_factory=WorkDeductionRules)
    notes: list[str] = Field(default_factory=list)
    sources: list[SourceDocument] = Field(default_factory=list)
    extraction: ExtractionTrace | None = None
    inps_sources: list[SourceDocument] = Field(default_factory=list)
    inps_extraction: ExtractionTrace | None = None

    @model_validator(mode="after")
    def _validate_sequences(self) -> Self:
        self._check_irpef_brackets()
        self._check_contribution_model()
        return self

    def _check_contribution_model(self) -> None:
        has_inps = self.inps is not None
        has_apprentice = self.apprentice is not None
        has_domestic = self.domestic_contributions is not None
        if has_inps != has_apprentice:
            msg = (
                "'inps' and 'apprentice' must both be present "
                "(standard model) or both absent; "
                "found one without the other"
            )
            raise ValueError(msg)
        has_standard = has_inps
        if not has_standard and not has_domestic:
            msg = (
                "YearRules must contain either 'inps' + 'apprentice' "
                "(standard model) or 'domestic_contributions' (domestic model)"
            )
            raise ValueError(msg)
        if has_standard and has_domestic:
            msg = (
                "YearRules must not mix standard model ('inps'+'apprentice') "
                "with 'domestic_contributions': mutually exclusive"
            )
            raise ValueError(msg)

    def _check_irpef_brackets(self) -> None:
        brackets = self.irpef_brackets
        if not brackets:
            msg = "irpef_brackets must not be empty"
            raise ValueError(msg)
        for i, b in enumerate(brackets[:-1]):
            if b.up_to is None:
                msg = (
                    f"only the last irpef_bracket may have up_to=None "
                    f"(bracket {i} is not the last)"
                )
                raise ValueError(msg)
            next_b = brackets[i + 1]
            if next_b.up_to is not None and next_b.up_to <= b.up_to:
                msg = (
                    f"irpef_brackets must have strictly ascending up_to: "
                    f"bracket {i} up_to={b.up_to} >= "
                    f"bracket {i + 1} up_to={next_b.up_to}"
                )
                raise ValueError(msg)
        if brackets[-1].up_to is not None:
            msg = (
                "last irpef_bracket must be unbounded (up_to=None), "
                f"got up_to={brackets[-1].up_to}"
            )
            raise ValueError(msg)
