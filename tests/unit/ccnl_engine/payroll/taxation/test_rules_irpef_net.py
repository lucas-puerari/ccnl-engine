"""net_irpef: the art. 16-ter c. 5-bis TUIR reduction stays out of payroll.

L. 199/2025 art. 1 c. 4 (Gazzetta Ufficiale text, read on 7 October 2026)
inserts art. 16-ter c. 5-bis TUIR: "Per i contribuenti titolari di un
reddito complessivo superiore a 200.000 euro e' diminuito di un importo pari
a 440 euro l'ammontare della detrazione dall'imposta lorda [...] spettante
in relazione ai seguenti oneri: a) gli oneri la cui detraibilita' e' fissata
nella misura del 19 per cento [...], fatta eccezione per le spese sanitarie
[...]; b) le erogazioni liberali in favore dei partiti politici [...]; c) i
premi di assicurazione per rischio eventi calamitosi [...]".  The art. 12
and art. 13 TUIR deductions and the ulteriore detrazione of L. 207/2024
art. 1 c. 6 are not in the list.

Source: https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?\
art.codiceRedazionale=26A00149&art.dataPubblicazioneGazzetta=2026-01-21&\
art.flagTipoArticolo=0&art.idArticolo=1&art.idGruppo=1&art.idSottoArticolo=1&\
art.idSottoArticolo1=10&art.progressivo=1&art.versione=1
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.taxation.rules_irpef_net import net_irpef
from ccnl_engine.tax.income.models import WorkDeductionMinimum, WorkDeductionRules
from tests.unit.ccnl_engine.builders import make_year_rules

#: The rules carry the 16-ter block, so the test fails if the engine uses it.
_RULES = make_year_rules(
    sterilizzazione_detrazioni={"threshold": "200000.00", "reduction": "440.00"}
)


def test_family_deductions_above_200k_are_not_reduced() -> None:
    """Income 210,000 EUR with 500 EUR of art. 12 deductions keeps all 500.

    - gross (art. 11 c. 1 TUIR, 23% / 33% / 43%): 28,000 * 23% + 22,000 *
      33% + 160,000 * 43% = 6,440 + 7,260 + 68,800 = 82,500.00;
    - art. 13 c. 1 lett. c) TUIR: zero above 50,000;
    - art. 16-ter c. 5-bis TUIR: no 19% oneri, donation or catastrophe
      premium, nothing to reduce; the 500 stays 500 (the old reading cut
      it to 500 - 440 = 60);
    - net: 82,500.00 - 500 = 82,000.00.
    """
    result = net_irpef(
        Decimal(210_000),
        _RULES,
        family_deductions=Decimal(500),
        eligible_work_days=365,
        fixed_term=False,
    )
    assert result.gross == Decimal("82500.00")
    assert result.work_deduction == Decimal(0)
    assert result.total_deductions == Decimal(500)
    assert result.net == Decimal("82000.00")
    assert result.ulteriore_effect == Decimal(0)


def test_the_art13_minimum_of_the_rules_reaches_the_net() -> None:
    """A versioned minimum of 2,000 / 2,400 for 92 days of 10,000 EUR.

    2,000 * 92 / 365 = 504.11 and 2,400 * 92 / 365 = 604.93, both above
    1,955 * 92 / 365 = 492.77 (art. 13 c. 1 lett. a) TUIR).
    """
    rules = make_year_rules().model_copy(
        update={
            "work_deduction": WorkDeductionRules(
                minimum=WorkDeductionMinimum(
                    open_ended=Decimal(2000), fixed_term=Decimal(2400)
                )
            )
        }
    )

    def work(fixed_term: bool) -> Decimal:
        return net_irpef(
            Decimal(10_000),
            rules,
            family_deductions=Decimal(0),
            eligible_work_days=92,
            fixed_term=fixed_term,
        ).work_deduction

    assert (work(False), work(True)) == (Decimal("504.11"), Decimal("604.93"))


def test_the_ulteriore_removes_only_the_tax_left_after_art12_and_art13() -> None:
    """The ulteriore detrazione (L. 207/2024 art. 1 c. 6) removes what is left.

    Income 25,000 with 3,000 EUR of art. 12 deductions: the IRPEF left
    after art. 12 and art. 13 is below the 1,000 EUR of the ulteriore, so
    its effect is that residual, not the whole 1,000.
    """
    rules = make_year_rules(
        ulteriore_detrazione={
            "threshold_low": "20000",
            "threshold_mid": "32000",
            "threshold_high": "40000",
            "max_amount": "1000",
        }
    )
    result = net_irpef(
        Decimal(25_000),
        rules,
        family_deductions=Decimal(3000),
        eligible_work_days=365,
        fixed_term=False,
    )
    residual = result.gross - result.work_deduction - Decimal(3000)

    assert result.ulteriore is not None
    assert Decimal(0) < residual < result.ulteriore.amount
    assert result.ulteriore_effect == residual
