"""Fiscal simplification tags for Payslip."""

from enum import StrEnum


class FiscalSimplification(StrEnum):
    """Items not computed by this engine, reported on every Payslip.

    Each value names a fiscal element that the engine omits. Callers can inspect
    ``Payslip.fiscal_simplifications`` to know which elements are absent from
    the net figure and should be handled by a separate fiscal layer.
    """

    NO_ADDIZIONALI = "no_addizionali"
    NO_TRATTAMENTO_INTEGRATIVO = "no_trattamento_integrativo"
    NO_DETRAZIONI_FAMILIARI = "no_detrazioni_familiari"
    NO_STERILIZZAZIONE_DETRAZIONI = "no_sterilizzazione_detrazioni"
