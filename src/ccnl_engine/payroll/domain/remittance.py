"""F24 codici tributo of the withholding agent and the summary of a ledger.

The withholding agent remits the tax it withholds and offsets the credits
it paid on the F24, section "Erario" or "Regioni" by codice tributo.  Each
code below is quoted from the Agenzia delle Entrate act that institutes or
lists it:

- Allegato 1 to the provvedimento of the Direttore dell'Agenzia of 31
  January 2025 prot. n. 25978/2025, "Codici tributo relativi alle
  ritenute/trattenute operate": 1001, 1002, 1012, 1053, 1701, 1704, 3802,
  3847, 3848, at
  https://www.agenziaentrate.gov.it/portale/documents/20143/8647956/allegato+1+-+codici+tributo.pdf/c30b8847-5d55-4a04-7664-9d726e706c61
  ;
- ris. 35/E of 26 June 2020 (1701), ris. 6/E of 28 January 2021 (1066),
  ris. 9/E of 31 January 2025 (1704), ris. 2/E (1076) and 3/E (1075) of
  29 January 2026.  Ris. 6/E/2021 is at
  https://www.agenziaentrate.gov.it/portale/documents/20143/3057149/codici+F24+ritenute+post+conguaglio+.pdf/3b930114-6599-a163-0d15-4e5d3a8bf6ec
  .

Only the national codes are used: the variants for tax due in or remitted
from Sicily, Sardinia and Valle d'Aosta (e.g. 1301, 1609, 1610) are not
selected.  Amounts whose code the engine cannot tell are left uncoded:

- surtax carried from an earlier run for lack of pay: the shortfall is
  not tracked by component;
- trattamento integrativo recovered from the worker: ris. 35/E/2020 gives
  1701 for the credit column only;
- an ulteriore detrazione of an earlier year recovered by installments;
- IRPEF and surtax refunded by the conguaglio and a recovery given back
  for lack of pay, which are not remitted.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType

from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry

__all__ = [
    "ACCOUNT_CODES",
    "ARREARS_WITHHOLDING",
    "CODED_ACCOUNTS",
    "IRPEF_WITHHOLDING",
    "MUNICIPAL_SURTAX_ADVANCE",
    "MUNICIPAL_SURTAX_BALANCE",
    "PDR_SUBSTITUTE_TAX",
    "POST_CONGUAGLIO_WITHHOLDING",
    "REGIME_CODES",
    "REGIONAL_SURTAX",
    "REMITTANCE_ACCOUNTS",
    "SEVERANCE_WITHHOLDING",
    "SOMMA_ESENTE_CREDIT",
    "TRATTAMENTO_CREDIT",
    "RemittanceColumn",
    "RemittanceLine",
    "remittance_summary",
]

#: "RITENUTE SU RETRIBUZIONI PENSIONI TRASFERTE MENSILITA' AGGIUNTIVE E
#: RELATIVO CONGUAGLIO" (Allegato 1, provv. 31/01/2025).
IRPEF_WITHHOLDING = "1001"
#: "Ritenute sui trattamenti pensionistici e redditi da lavoro dipendente e
#: assimilati, operate dopo il relativo conguaglio di fine anno" (ris. AdE
#: 6/E/2021, instituted for the withholding of art. 23 c. 3 second sentence
#: DPR 600/1973): the IRPEF of a conguaglio deferred on written request.
POST_CONGUAGLIO_WITHHOLDING = "1066"
#: "RITENUTE SU EMOLUMENTI ARRETRATI" (Allegato 1, provv. 31/01/2025).
ARREARS_WITHHOLDING = "1002"
#: "RITENUTE SU INDENNITA' PER CESSAZIONE DI RAPPORTO DI LAVORO E
#: PRESTAZIONI IN FORMA DI CAPITALE SOGGETTE A TASSAZIONE SEPARATA"
#: (Allegato 1, provv. 31/01/2025).
SEVERANCE_WITHHOLDING = "1012"
#: "IMPOSTA SOSTITUTIVA IRPEF E ADDIZIONALI REGIONALI E COMUNALI SU PREMI
#: DI RISULTATO E PARTECIPAZIONE AGLI UTILI" (Allegato 1, provv. 31/01/2025).
PDR_SUBSTITUTE_TAX = "1053"
#: "Credito maturato dai sostituti d'imposta per l'erogazione del
#: trattamento integrativo", column "importi a credito compensati"
#: (ris. 35/E/2020).
TRATTAMENTO_CREDIT = "1701"
#: "Credito maturato dai sostituti d'imposta per l'erogazione ai lavoratori
#: dipendenti della somma di cui all'articolo 1, comma 4, della legge 30
#: dicembre 2024, n. 207": column "importi a credito compensati" for the
#: amount paid and "importi a debito versati" for the amount "già erogata e
#: poi recuperata in capo al dipendente" (ris. 9/E/2025).
SOMMA_ESENTE_CREDIT = "1704"
#: "ADDIZIONALE REGIONALE ALL'IMPOSTA SUL REDDITO DELLE PERSONE FISICHE
#: SOSTITUTI D'IMPOSTA" (Allegato 1, provv. 31/01/2025).
REGIONAL_SURTAX = "3802"
#: "ADDIZIONALE COMUNALE ALL'IRPEF TRATTENUTA DAL SOSTITUTO D'IMPOSTA -
#: ACCONTO - RIS. N. 368/E DEL 12/12/2007" (Allegato 1, provv. 31/01/2025).
MUNICIPAL_SURTAX_ADVANCE = "3847"
#: "ADDIZIONALE COMUNALE ALL'IRPEF TRATTENUTA DAL SOSTITUTO D'IMPOSTA -
#: SALDO - RIS. N. 368/E DEL 12/12/2007" (Allegato 1, provv. 31/01/2025).
MUNICIPAL_SURTAX_BALANCE = "3848"

#: Code of the substitute tax of each preferential regime, by regime id:
#: 1075 for the incrementi retributivi of L. 199/2025 art. 1 c. 7
#: (ris. 3/E/2026) and 1076 for the maggiorazioni and indennità of c. 10
#: and 11 (ris. 2/E/2026).  A regime not listed is left uncoded.
REGIME_CODES: Mapping[str, str] = MappingProxyType({
    "rinnovo": "1075",
    "notte_festivi_turni": "1076",
})


class RemittanceColumn(StrEnum):
    """F24 column an amount is reported in."""

    DEBIT = "debit"
    """"importi a debito versati": tax withheld or credit recovered."""
    CREDIT = "credit"
    """"importi a credito compensati": credit paid to the worker."""


#: Tax and credit accounts, in summary order, with the F24 column of a
#: coded amount; ``None`` for an account that is never remitted.
_COLUMNS: Mapping[AccountKind, RemittanceColumn | None] = MappingProxyType({
    AccountKind.ORDINARY_TAX: RemittanceColumn.DEBIT,
    AccountKind.TAX_REFUNDS: None,
    AccountKind.SURTAX: RemittanceColumn.DEBIT,
    AccountKind.SURTAX_REFUNDS: None,
    AccountKind.SUBSTITUTE_TAX: RemittanceColumn.DEBIT,
    AccountKind.SEPARATE_TAX: RemittanceColumn.DEBIT,
    AccountKind.CREDITS: RemittanceColumn.CREDIT,
    AccountKind.CREDIT_RECOVERIES: RemittanceColumn.DEBIT,
    AccountKind.CREDIT_RECOVERY_SHORTFALL: None,
})

#: Accounts :func:`remittance_summary` reports, in its order.
REMITTANCE_ACCOUNTS: tuple[AccountKind, ...] = tuple(_COLUMNS)

#: Codes an entry of each account may carry.  An account not listed is
#: never coded.
ACCOUNT_CODES: Mapping[AccountKind, frozenset[str]] = MappingProxyType({
    AccountKind.ORDINARY_TAX: frozenset({
        IRPEF_WITHHOLDING,
        POST_CONGUAGLIO_WITHHOLDING,
    }),
    AccountKind.SURTAX: frozenset({
        REGIONAL_SURTAX,
        MUNICIPAL_SURTAX_ADVANCE,
        MUNICIPAL_SURTAX_BALANCE,
    }),
    AccountKind.SUBSTITUTE_TAX: frozenset({PDR_SUBSTITUTE_TAX, *REGIME_CODES.values()}),
    AccountKind.SEPARATE_TAX: frozenset({ARREARS_WITHHOLDING, SEVERANCE_WITHHOLDING}),
    AccountKind.CREDITS: frozenset({TRATTAMENTO_CREDIT, SOMMA_ESENTE_CREDIT}),
    AccountKind.CREDIT_RECOVERIES: frozenset({SOMMA_ESENTE_CREDIT}),
})

#: Accounts every entry of which carries a code: the engine always knows it.
CODED_ACCOUNTS: frozenset[AccountKind] = frozenset({
    AccountKind.ORDINARY_TAX,
    AccountKind.SEPARATE_TAX,
    AccountKind.CREDITS,
})


@dataclass(frozen=True)
class RemittanceLine:
    """Total of one account and codice tributo over a set of entries.

    Attributes:
        account: Tax or credit account of the entries.
        remittance_code: Their codice tributo, ``None`` when not verified.
        column: F24 column of a coded amount; ``None`` for an uncoded line
            or an account that is never remitted.
        amount: Sum of the entries, in EUR.
    """

    account: AccountKind
    remittance_code: str | None
    column: RemittanceColumn | None
    amount: Decimal


def remittance_summary(entries: Iterable[LedgerEntry]) -> tuple[RemittanceLine, ...]:
    """Group the tax and credit entries by account and codice tributo.

    Returns:
        One line per account and code with a non-zero total, in the order
        of :data:`REMITTANCE_ACCOUNTS`, coded lines first by code, then
        the uncoded line of the account.
    """
    totals: dict[tuple[AccountKind, str | None], Decimal] = {}
    for entry in entries:
        if entry.account in _COLUMNS:
            key = (entry.account, entry.remittance_code)
            totals[key] = totals.get(key, Decimal(0)) + entry.amount
    order = {account: i for i, account in enumerate(REMITTANCE_ACCOUNTS)}
    keys = sorted(
        (key for key, amount in totals.items() if amount),
        key=lambda k: (order[k[0]], k[1] is None, k[1] or ""),
    )
    return tuple(
        RemittanceLine(
            account=account,
            remittance_code=code,
            column=None if code is None else _COLUMNS[account],
            amount=totals[account, code],
        )
        for account, code in keys
    )
