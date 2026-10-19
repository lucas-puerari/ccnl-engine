"""Find a CCNL and its level before the first run.

A caller does not need to know a file name: search the bundled contracts by
name or slug, pick one by slug or CNEL code, list its levels, then pass the
slug and a level code to :class:`Employment`.
"""

from ccnl_engine import Employment, PayrollEngine
from ccnl_engine.catalog import get_ccnl, search_ccnls
from ccnl_engine.inputs import Permanent

engine = PayrollEngine.bundled()

# Every bundled contract, or a search on name and slug.
print(f"Bundled CCNLs: {len(engine.list_contracts())}")
for candidate in search_ccnls("commercio"):
    print(candidate.ccnl_id, candidate.cnel_code, candidate.name)

# By slug or by CNEL code.  A CNEL code can cover more than one bundled
# contract (H052: Turismo Confcommercio, Federalberghi and Agenzie di viaggio
# Fiavet); a shared code raises UnknownCcnlError with the slugs to choose from.
contract = get_ccnl("H011")
print(f"\n{contract.name}: {contract.readiness}")

for level in engine.list_levels(contract.ccnl_id):
    print(level.code, level.description)

employment = Employment(
    ccnl_id=contract.ccnl_id,
    level_code="4",
    contract_type=Permanent(),
)
print(f"\nEmployment on {employment.ccnl_id}, level {employment.level_code}")
