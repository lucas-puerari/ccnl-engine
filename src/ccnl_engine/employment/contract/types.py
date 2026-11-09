"""Employment contract variants and role validation."""

from dataclasses import dataclass, field
from typing import Literal

from ccnl_engine.employment.apprentice.inputs import Apprentice
from ccnl_engine.employment.fact.inputs import FEATURE
from ccnl_engine.employment.fixed_term.inputs import FixedTerm
from ccnl_engine.validators import require_str


@dataclass(frozen=True, slots=True)
class Permanent:
    """Open-ended contract; ``entry_pay`` takes the entry pay of the CCNL."""

    type: Literal["permanent"] = field(default="permanent", init=False)
    entry_pay: bool = False


#: Every supported employment contract type.
type Contract = Permanent | FixedTerm | Apprentice


def _role(value: object, path: str) -> str:
    require_str(value, path, feature=FEATURE, non_blank=True)
    return str(value)
