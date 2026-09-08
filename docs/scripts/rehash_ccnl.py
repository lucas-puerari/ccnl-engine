"""Recompute source_hash for all CCNL JSON files.

Idempotent: running it twice produces the same result.
Run with::

    make rehash

Or directly::

    uv run python docs/scripts/rehash_ccnl.py
"""

import json
from pathlib import Path

from ccnl_engine.engine.metadata import source_hash

data_dir = Path("src/ccnl_engine/knowledge/ccnl/data")
updated = 0
skipped = 0

for json_file in sorted(data_dir.glob("*.json")):
    data = json.loads(json_file.read_text())
    ruleset = data.get("ruleset")
    if not isinstance(ruleset, dict) or "source_hash" not in ruleset:
        skipped += 1
        continue
    new_hash = source_hash(data)
    if ruleset["source_hash"] == new_hash:
        skipped += 1
        continue
    data["ruleset"]["source_hash"] = new_hash
    json_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    updated += 1
    print(f"  rehashed {json_file.name}")

print(f"Done: {updated} updated, {skipped} already correct")
