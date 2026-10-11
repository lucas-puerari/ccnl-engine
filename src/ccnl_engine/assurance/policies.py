"""Mode of a payroll engine: the payability policy its results follow.

Both modes run the same calculation and return the same amounts; they differ
only in what may be paid:

- ``simulation`` (the default): a result is payable when nothing in the run
  blocks it.  The readiness of the rulesets is reported, not enforced.
- ``operational``: in addition, every ruleset that tracks a readiness tier
  must be ``production``, with a confidence that agrees.  A run that reads a
  ruleset short of that is returned with a ``ruleset_not_production``
  blocker, its amounts still inspectable.
"""

from __future__ import annotations

from enum import StrEnum

__all__ = ["EngineMode"]


class EngineMode(StrEnum):
    """Payability policy of a payroll engine.

    Attributes:
        SIMULATION: Amounts with their assurance; readiness is reported only.
        OPERATIONAL: Amounts are payable only from ``production`` rulesets.
    """

    SIMULATION = "simulation"
    OPERATIONAL = "operational"
