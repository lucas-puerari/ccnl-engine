"""Statutory parameters of the contributions to a complementary pension fund."""

from pydantic import BaseModel, ConfigDict

from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.primitives import PercentageRate, PositiveCeiling


class ComplementaryPensionRules(BaseModel):
    """Tax and INPS parameters of complementary pension contributions.

    Attributes:
        deduction_cap: Annual amount of the employee and employer
            contributions that is deductible from the income (D.Lgs.
            252/2005 art. 8 c. 4, via TUIR art. 10 c. 1 lett. e-bis and
            art. 51 c. 2 lett. h).  The TFR paid to the fund does not count.
        solidarity_rate: INPS solidarity contribution on the employer
            contributions, TFR excluded (D.Lgs. 252/2005 art. 16 c. 1;
            art. 9-bis D.L. 103/1991, conv. L. 166/1991).
        provenance: Source of both values.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    deduction_cap: PositiveCeiling
    solidarity_rate: PercentageRate
    provenance: RuleProvenance | None = None
