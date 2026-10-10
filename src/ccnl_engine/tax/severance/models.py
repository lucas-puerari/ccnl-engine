"""TFR (severance pay) accrual rule models."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.primitives import PercentageRate
from ccnl_engine.provenance.source.models_chain import RuleProvenance


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


class TfrCompensation(BaseModel):
    """Compensations of an employer whose TFR leaves the company.

    When the TFR maturando goes to a complementary pension fund or to the
    Fondo Tesoreria INPS the employer is exempted, in the same percentage
    of the TFR conferred, from the Fondo di garanzia TFR contribution
    (D.Lgs. 252/2005 art. 10 c. 2: ``guarantee_fund_rate``, 0.40% for the
    categories of ``guarantee_fund_rate_by_category``) and from the social
    contributions of ``relief_rate`` points (D.L. 203/2005 art. 8 and its
    Tabella A).  Both rates apply to the INPS taxable base of the period.
    """

    model_config = ConfigDict(extra="forbid")

    guarantee_fund_rate: PercentageRate
    guarantee_fund_rate_by_category: dict[WorkerCategory, PercentageRate] = {}
    relief_rate: PercentageRate
    provenance: RuleProvenance | None = None

    def guarantee_fund_rate_for(self, category: WorkerCategory | None) -> Decimal:
        """Return the Fondo di garanzia rate of a worker of ``category``.

        Returns:
            The rate of the category when the sector gives one, else the
            general rate.
        """
        if category is None:
            return self.guarantee_fund_rate
        return self.guarantee_fund_rate_by_category.get(
            category, self.guarantee_fund_rate
        )


class TfrRules(BaseModel):
    """TFR (severance pay) accrual rules (Art. 2120 c.c.).

    ``additional_ivs`` is ``None`` where the bundle does not apply the
    deduction and the quota accrues whole: public administration (not
    insured with the FPLD), domestic work (named by c. 15, but paid by
    flat hourly contributions with no percentage IVS base to charge the
    0.50% on) and agricoltura (the composition of its employer rate is
    not sourced).  ``compensation`` is ``None`` where the bundle applies
    no compensation for the TFR conferred: public administration and
    domestic work (outside the Fondo di garanzia) and agricoltura (its
    rates by contract are not modelled).
    """

    model_config = ConfigDict(extra="forbid")

    accrual_divisor: Decimal = Field(gt=Decimal(0))
    additional_ivs: TfrIvsDeduction | None = None
    compensation: TfrCompensation | None = None
    provenance: RuleProvenance | None = None
