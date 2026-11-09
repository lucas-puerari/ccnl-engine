"""Result of deriving a contractual hourly base from sourced pay elements."""

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.working_time.supplement.models import HourlyBaseMethod


@dataclass(frozen=True)
class HourlyBase:
    """The hourly rate of a CCNL on one day and what it is made of.

    Attributes:
        rate: ``monthly / divisor``, unrounded.
        monthly: Sum of the monthly pay elements.
        divisor: Hourly divisor of the CCNL in force on the day.
        method: The elements the CCNL names.
        components: Each element and its full-time monthly amount.
        individual: ``included`` when the worker's individual elements
            are among :attr:`components`, ``not_included`` when the CCNL
            leaves them out, ``none`` without any.
        direct: Whether the rate is printed as an hourly minimum, rather
            than derived from monthly pay. The monthly and divisor fields
            are placeholders in that case and are not reported as inputs.
    """

    rate: Decimal
    monthly: Decimal
    divisor: Decimal
    method: HourlyBaseMethod
    components: tuple[tuple[str, Decimal], ...]
    individual: str = "none"
    direct: bool = False

    def inputs(self) -> dict[str, Decimal | str]:
        """Return the decision inputs that show how the rate was built.

        Returns:
            The method, each component, the monthly sum, the divisor, the
            rate and the individual elements left out.
        """
        if self.direct:
            return {
                "hourly_base_method": self.method.value,
                "hourly_minimum": self.rate,
                "hourly_base_rate": self.rate,
                "individual_elements": self.individual,
            }
        return {
            "hourly_base_method": self.method.value,
            **{f"hourly_base[{name}]": amount for name, amount in self.components},
            "hourly_base_monthly": self.monthly,
            "hourly_divisor": self.divisor,
            "hourly_base_rate": self.rate,
            "individual_elements": self.individual,
        }
