"""The contribution exemption the employer was admitted to for a worker.

Whether a hire qualifies (the worker's past employment, the net growth of
the headcount, the site, the INPS admission) is known to the employer
alone: the request states the measure and the facts that set its rate and
duration, and the engine applies the caps, durations and exclusions of the
law.  The measures:

- ``young``: DL 60/2024 art. 22, hires of workers under 35 until 30 April
  2026; 70% of the employer contributions, 100% with a net headcount
  growth, up to 500 EUR a month (650 at the sites of c. 3), 24 months.
- ``women``: art. 23, hires of disadvantaged women until 31 December 2026;
  100%, up to 650 EUR a month, 24 months.
- ``zes``: art. 24, hires in the ZES unica until 30 April 2026; 70%, 100%
  with a net headcount growth, up to 650 EUR a month, 24 months.
- ``mothers``: L. 199/2025 art. 1 cc. 210-213, hires in 2026 of mothers of
  at least three minors; 100%, up to 8,000 EUR a year, 12 months for a
  fixed-term hire, 18 from the hire for one made permanent, 24 for a
  permanent hire.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.validators import parse_enum, reject, require_bool, require_date

__all__ = ["EXEMPTION_FEATURE", "ContributionExemption", "ExemptionMeasure"]

EXEMPTION_FEATURE = "contribution_exemption"
_SHARES = frozenset({Decimal("0.7"), Decimal(1)})


class ExemptionMeasure(StrEnum):
    """The exemption measure the employer applies."""

    YOUNG = "young"
    WOMEN = "women"
    ZES = "zes"
    MOTHERS = "mothers"


@dataclass(frozen=True)
class ContributionExemption:
    """The exemption of the employer contributions for one worker.

    Attributes:
        measure: The measure the employer was admitted to.
        start: The hire, or the conversion to a permanent contract, the
            exemption runs from.
        share: The share of the contributions exempted: 0.7, or 1 with a
            net headcount growth (``young`` and ``zes``); 1 otherwise.
        territorial: The site is in a region of DL 60/2024 art. 22 c. 3
            (``young``: 650 EUR a month) or in the ZES unica (``women``:
            the code of the ZES).
        made_permanent: A ``mothers`` hire made permanent: 18 months from
            ``start``, the first hire.

    Raises:
        InvalidInputError: When a field is not of its type, ``share`` is
            not 0.7 or 1, or a measure is given a fact it does not read.
    """

    measure: ExemptionMeasure
    start: date
    share: Decimal = Decimal(1)
    territorial: bool = False
    made_permanent: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        owner = "ContributionExemption"
        measure = parse_enum(
            self.measure,
            ExemptionMeasure,
            f"{owner}.measure",
            feature=EXEMPTION_FEATURE,
        )
        object.__setattr__(self, "measure", measure)
        require_date(self.start, f"{owner}.start", feature=EXEMPTION_FEATURE)
        for name in ("territorial", "made_permanent"):
            require_bool(
                getattr(self, name), f"{owner}.{name}", feature=EXEMPTION_FEATURE
            )
        partial = measure in {ExemptionMeasure.YOUNG, ExemptionMeasure.ZES}
        shares = _SHARES if partial else frozenset({Decimal(1)})
        if not isinstance(self.share, Decimal) or self.share not in shares:
            expected = "0.7 or 1" if partial else "1"
            reject(f"{owner}.share", expected, self.share, feature=EXEMPTION_FEATURE)
        local = {ExemptionMeasure.YOUNG, ExemptionMeasure.WOMEN}
        if self.territorial and measure not in local:
            reject(f"{owner}.territorial", "False", True, feature=EXEMPTION_FEATURE)
        if self.made_permanent and measure is not ExemptionMeasure.MOTHERS:
            reject(f"{owner}.made_permanent", "False", True, feature=EXEMPTION_FEATURE)
