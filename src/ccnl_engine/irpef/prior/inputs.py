"""An earlier employment of the tax year the worker asks to conguagliare.

Art. 23 c. 4 DPR 600/1973: at the request of the worker, who hands over the
certificazione unica of the other payer, the conguaglio also takes in the
employment income of earlier relationships of the year.  The amounts are
the ones the CU certifies: facts of the worker, not computed.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.employment.spell.models import EmploymentSpell
from ccnl_engine.validators import require_decimal, require_instance

__all__ = ["PriorEmployerIncome"]

_OWNER = "PriorEmployerIncome"
_FEATURE = "additional_irpef_base"
_ZERO = Decimal(0)


@dataclass(frozen=True, slots=True)
class PriorEmployerIncome:
    """An ended employment of the tax year, as its CU certifies it.

    Attributes:
        spell: The days of the employment in the tax year: the art. 13
            TUIR deduction counts the union with this employment's days.
        taxable: Employment income the CU certifies, the IRPEF base.
        irpef_withheld: IRPEF the other payer withheld on it.
        trattamento_paid: Trattamento integrativo (D.L. 3/2020) the other
            payer paid.

    Raises:
        InvalidInputError: When a field is not of its type or an amount is
            negative.
    """

    spell: EmploymentSpell
    taxable: Decimal
    irpef_withheld: Decimal
    trattamento_paid: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        require_instance(
            self.spell, EmploymentSpell, f"{_OWNER}.spell", feature=_FEATURE
        )
        for name in ("taxable", "irpef_withheld", "trattamento_paid"):
            require_decimal(
                getattr(self, name), f"{_OWNER}.{name}", feature=_FEATURE, minimum=_ZERO
            )
