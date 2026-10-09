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


class PublicPensionFund(StrEnum):
    """Pension fund of INPS Gestione Dipendenti Pubblici a CCNL enrols in.

    CTPS: the employees of the State (ministeri, scuola, agenzie); CPDEL:
    those of the enti locali and of the Servizio sanitario nazionale; CPS:
    the doctors and veterinarians of the Servizio sanitario nazionale; CPI
    and CPUG: the teachers of the scuole materne and elementari paritarie
    of the enti locali and the ufficiali giudiziari.
    """

    CTPS = "ctps"
    CPDEL = "cpdel"
    CPS = "cps"
    CPI = "cpi"
    CPUG = "cpug"
