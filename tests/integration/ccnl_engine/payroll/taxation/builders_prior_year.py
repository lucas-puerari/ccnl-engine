"""Prior-year tax facts for requests whose subject is not the renewal regime.

A 2026 run of a CCNL whose minimo has a table dated within the signing
window of L. 199/2025 art. 1 c. 7 (agreements signed from 1 January 2024 to
31 December 2026) may pay renewal increments inside the minimo, so the run
takes a ``rinnovo_substitute_tax`` decision on it.  Unless a known fact
excludes the worker, that decision is provisional: an unknown 2025 income or
sector is a missing fact, and an eligible worker leaves the increment
unquantified.  A test that checks the status or the gaps of another
capability states a written waiver of the renewal regime ("salva espressa
rinuncia scritta"), which excludes the worker and touches nothing else:
the 2025 income stays unknown, as for the other regimes.
"""

from __future__ import annotations

from ccnl_engine.inputs import PriorYearTaxFacts, SubstituteTaxRegime

__all__ = ["RENEWAL_WAIVED"]

#: 2025 income unknown, the renewal regime waived in writing.
RENEWAL_WAIVED = PriorYearTaxFacts(
    waived_regimes=frozenset({SubstituteTaxRegime.RINNOVO})
)
