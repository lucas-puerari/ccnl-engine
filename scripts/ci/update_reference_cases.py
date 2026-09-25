"""Stub: reference-case regeneration is no longer used.

The golden reference case test suite (``tests/reference/test_reference.py``)
was removed when the legacy ``engine.payroll`` pipeline was deleted.
Reference cases are now validated through the integration test suite in
``tests/integration/cases/``.

This script is retained as a no-op so that existing CI job definitions
continue to resolve the file path without error.
"""

from __future__ import annotations

import sys


def main() -> int:
    """Exit 0: nothing to verify.

    Returns:
        Always 0.
    """
    print("Reference-case verification is inactive (test_reference.py removed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
