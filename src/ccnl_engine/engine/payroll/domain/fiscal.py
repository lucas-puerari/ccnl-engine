"""Fiscal simplification tags for PayrollResult."""

from enum import StrEnum


class FiscalSimplification(StrEnum):
    """Items not computed by this engine, reported on every PayrollResult.

    Each value names a fiscal element that the engine omits. Callers can inspect
    ``PayrollResult.fiscal_simplifications`` to know which elements are absent from
    the net figure and should be handled by a separate fiscal layer.

    ``NO_ADDIZIONALE_*`` — jurisdiction not provided by the caller (excluded).
    ``ADDIZIONALE_*_UNKNOWN`` — jurisdiction provided but not found in the bundle;
    the addizionale is zero and the scope entry is ``not_computed``.
    ``NO_DETRAZIONI_ART15_MORTGAGE`` — Art. 15 mortgage interest not provided;
    cleared when ``scenario.art15_deductions.mortgage_interest`` is non-zero.
    ``PARTIAL_DETRAZIONI_ART15`` — always set; the engine models only mortgage
    interest (one of ~15 Art. 15 TUIR categories). Medical expenses, life
    insurance, funeral costs, charitable donations and the other categories are
    not computed; a separate fiscal layer must handle them.
    ``NO_SOMMA_ESENTE`` — always set when the tax data file does not carry
    ``somma_esente`` parameters (L. 207/2024 flat-rate net bonus for reddito
    complessivo up to 20 000 EUR); cleared when the bonus is present in the
    data regardless of the computed amount.
    ``NO_BILATERAL_FUNDS`` — no scenario-level bilateral fund contributions
    provided (``scenario.bilateral_funds`` is empty); cleared when at least one
    fund is present. Engine models only the post-tax net reduction; any
    pre-tax deductibility of the employee contribution must be handled by a
    separate fiscal layer.
    ``NO_ASSEGNO_UNICO`` — always present; assegno unico e universale
    (D.Lgs. 230/2021) is handled by INPS directly and is not modelled here.
    """

    NO_ADDIZIONALE_REGIONALE = "no_addizionale_regionale"
    NO_ADDIZIONALE_COMUNALE = "no_addizionale_comunale"
    ADDIZIONALE_REGIONALE_UNKNOWN = "addizionale_regionale_unknown"
    ADDIZIONALE_COMUNALE_UNKNOWN = "addizionale_comunale_unknown"
    NO_TRATTAMENTO_INTEGRATIVO = "no_trattamento_integrativo"
    NO_DETRAZIONI_FAMILIARI = "no_detrazioni_familiari"
    NO_DETRAZIONI_ART15_MORTGAGE = "no_detrazioni_art15_mortgage"
    PARTIAL_DETRAZIONI_ART15 = "partial_detrazioni_art15"
    NO_ULTERIORE_DETRAZIONE_LAVORO = "no_ulteriore_detrazione_lavoro"
    NO_SOMMA_ESENTE = "no_somma_esente"
    NO_BILATERAL_FUNDS = "no_bilateral_funds"
    NO_ASSEGNO_UNICO = "no_assegno_unico"
