"""The tax years from which the testi unici replace the earlier statutes.

Two consolidation decrees renumber the rules the engine cites from the
same year: the testo unico of the income taxes (D.Lgs. 117/2026), which
replaces the TUIR articles on separate taxation and the foreign tax
credit, and the testo unico of the payments and withholdings (D.Lgs.
33/2025, art. 243), which replaces art. 23 D.P.R. 600/1973.  The amounts do
not change; the rule ids and citations of the decisions do.  One constant
per decree, read by every module that cites them.
"""

from __future__ import annotations

from typing import Final

__all__ = ["INCOME_TAX_CODE_FROM", "WITHHOLDING_CODE_FROM"]

#: First tax year of the testo unico of the income taxes, D.Lgs. 117/2026.
INCOME_TAX_CODE_FROM: Final = 2027
#: First tax year of the testo unico of the payments, D.Lgs. 33/2025 art. 243.
WITHHOLDING_CODE_FROM: Final = 2027
