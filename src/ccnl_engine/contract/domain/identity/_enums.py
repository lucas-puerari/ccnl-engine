"""Coverage, feature, and sector enumerations."""

from enum import StrEnum


class CoverageStatus(StrEnum):
    """Implementation status for a CCNL coverage layer."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    OUT_OF_SCOPE = "out_of_scope"
    NOT_IMPLEMENTED = "not_implemented"


class WorkRuleFeature(StrEnum):
    """Enumeration of work-rules payroll features."""

    OVERTIME = "overtime"
    NIGHT_WORK = "night_work"
    HOLIDAY_WORK = "holiday_work"
    ABSENCE = "absence"
    SICKNESS = "sickness"
    LEAVE = "leave"
    BONUS = "bonus"
    BENEFITS = "benefits"
    WELFARE = "welfare"
    FRINGE_BENEFITS = "fringe_benefits"
    FAMILY_DEDUCTIONS = "family_deductions"
    COMPANY_AGREEMENT = "company_agreement"
    TERRITORIAL_AGREEMENT = "territorial_agreement"


class NoteKind(StrEnum):
    """Semantic category of a coverage note."""

    SOURCE = "source"
    INFO = "info"
    SIMPLIFICATION = "simplification"
    MISSING = "missing"


class TaxSector(StrEnum):
    """INPS sector classification used to select the contribution-rate file."""

    TERZIARIO = "terziario"
    INDUSTRIA = "industria"
    EDILIZIA = "edilizia"
    CREDITO = "credito"
    ARTIGIANATO = "artigianato"
    PUBBLICA_AMMINISTRAZIONE = "pubblica-amministrazione"
    LAVORO_DOMESTICO = "lavoro-domestico"
    AGRICOLTURA = "agricoltura"
