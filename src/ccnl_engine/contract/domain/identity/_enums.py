"""Coverage-note and sector enumerations."""

from enum import StrEnum


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
