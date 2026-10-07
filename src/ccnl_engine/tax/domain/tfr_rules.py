"""TFR (severance pay) accrual rule models."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.primitives import PercentageRate


class TfrIvsDeduction(BaseModel):
    """Additional IVS contribution deducted from the TFR quota (L. 297/1982).

    Art. 3 c. 15 raises the employer IVS rate of the Fondo pensioni
    lavoratori dipendenti by 0.50% of the taxable pay; c. 16 has the
    employer deduct that contribution from the TFR quota of the same
    period, or from the contribution financing it when the TFR is paid to
    a complementary pension fund.  The rate is already inside the employer
    IVS rate of the INPS ruleset: the deduction only reduces the TFR.
    """

    model_config = ConfigDict(extra="forbid")

    rate: PercentageRate
    provenance: RuleProvenance | None = None


class TfrRules(BaseModel):
    """TFR (severance pay) accrual rules (Art. 2120 c.c.).

    ``additional_ivs`` is ``None`` where the bundle does not apply the
    deduction and the quota accrues whole: public administration (not
    insured with the FPLD), domestic work (named by c. 15, but paid by
    flat hourly contributions with no percentage IVS base to charge the
    0.50% on) and agricoltura (the composition of its employer rate is
    not sourced).
    """

    model_config = ConfigDict(extra="forbid")

    accrual_divisor: Decimal = Field(gt=Decimal(0))
    additional_ivs: TfrIvsDeduction | None = None
    provenance: RuleProvenance | None = None
