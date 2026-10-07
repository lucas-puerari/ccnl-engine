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
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.service.irpef_net import net_irpef
from tests.helpers import make_year_rules

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
