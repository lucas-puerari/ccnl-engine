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
    """

    NO_ADDIZIONALE_REGIONALE = "no_addizionale_regionale"
    NO_ADDIZIONALE_COMUNALE = "no_addizionale_comunale"
    ADDIZIONALE_REGIONALE_UNKNOWN = "addizionale_regionale_unknown"
    ADDIZIONALE_COMUNALE_UNKNOWN = "addizionale_comunale_unknown"
    NO_TRATTAMENTO_INTEGRATIVO = "no_trattamento_integrativo"
    NO_DETRAZIONI_FAMILIARI = "no_detrazioni_familiari"
    NO_DETRAZIONI_ART15 = "no_detrazioni_art15"
