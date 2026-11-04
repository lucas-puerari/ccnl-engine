"""Oracles of observed payslips: Concia D2 and Metalmeccanico C3, 2026."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from tests.knowledge.ccnl_engine.irpef.oracles import net_irpef
from tests.knowledge.ccnl_engine.surtax.oracles import (
    municipal_advance,
    municipal_alghero,
    regional_sardegna,
)
from tests.knowledge.ccnl_engine.tax_credit.oracles import (
    somma_esente,
    trattamento_integrativo,
)

__all__ = [
    "CONCIA_D2_2026",
    "CONCIA_D2_JULY_HIRE_2026",
    "ConciaMidYear",
    "ConciaPayment",
    "ConciaYear",
]

_CENT = Decimal("0.01")

#: Allegato n. 1, minimo D2 at the expiry of 30 June 2023.
_MINIMUM_AT_EXPIRY = Decimal("1850.99")
#: Parte economica, D2 tranches of 1 March 2024, 1 January 2025 and 2026.
_TRANCHES = (Decimal("96.00"), Decimal("55.00"), Decimal("40.00"))
#: Allegato n. 1, minimo D2 from 1 January 2026.
_TABLE_MINIMUM_2026 = Decimal("2041.99")
_EDR_LIRE = Decimal(20_000)
_LIRE_PER_EURO = Decimal("1936.27")
_MONTHS_PAID = 13
_EMPLOYEE_IVS_RATE = Decimal("0.0919")
_EMPLOYEE_CIGS_RATE = Decimal("0.0030")
_TFR_DIVISOR = Decimal("13.5")
_TFR_EXTRA_IVS_RATE = Decimal("0.0050")
#: Art. 38 and 50 (CNEL 148617, pp. 60 and 69): 1 November 2026 falls on a
#: Sunday, "una giornata di retribuzione", the paga mensile over 25.
_SUNDAY_HOLIDAY_DIVISOR = Decimal(25)


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ConciaPayment:
    """The oracle figures of one payment, in EUR.

    Attributes:
        gross: Gross of the payment.
        allowances: Fixed allowances of the payment: the EDR and, in
            November, the quota of the holiday on a Sunday.
        inps_base: INPS base, the gross to the whole euro.
        inps: Employee INPS.
        tfr_quota: Art. 2120 c.c. TFR quota.
        tfr_deduction: The 0.50% additional IVS on the INPS base.
    """

    gross: Decimal
    allowances: Decimal
    inps_base: Decimal
    inps: Decimal
    tfr_quota: Decimal
    tfr_deduction: Decimal

    @property
    def tfr_net_of_extra_ivs(self) -> Decimal:
        """The TFR quota less the additional IVS."""
        return self.tfr_quota - self.tfr_deduction


def _inps(base: Decimal) -> Decimal:
    # One contribution at the whole employee rate, to cents once (FILCTEM
    # CGIL 2024 guide p. 21: "1.672 x 9,49% = 158,67").
    return _cents(base * (_EMPLOYEE_IVS_RATE + _EMPLOYEE_CIGS_RATE))


def _payment(gross: Decimal, allowances: Decimal) -> ConciaPayment:
    base = gross.quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return ConciaPayment(
        gross=gross,
        allowances=allowances,
        inps_base=base,
        inps=_inps(base),
        tfr_quota=_cents(gross / _TFR_DIVISOR),
        tfr_deduction=_cents(base * _TFR_EXTRA_IVS_RATE),
    )


@dataclass(frozen=True)
class ConciaYear:
    """The oracle figures of the scenario, in EUR.

    Attributes:
        minimum: Minimo tabellare D2 of every 2026 payment.
        edr: Elemento distinto della retribuzione of every payment.
        monthly_gross: Gross of each of the thirteen payments.
        inps_base: INPS base of each payment, the gross to the whole euro.
        monthly_inps: Employee INPS of each payment.
        tfr_divisor: Art. 2120 c.c. divisor of the yearly pay.
        tfr_quota: Art. 2120 c.c. TFR quota of each payment.
        tfr_deduction: The 0.50% additional IVS of the payment, on the
            INPS base (well under the IVS massimale), that L. 297/1982 art. 3
            c. 16 deducts from the quota.
        tfr_net_of_extra_ivs: The quota less ``tfr_deduction``.
        sunday_holiday: Quota of 1 November 2026, a holiday on a Sunday.
        november: The November payment, with ``sunday_holiday``.
        payments: Number of payments of the tax year.
        gross: Gross of the year.
        inps: Employee INPS of the year.
        taxable: IRPEF taxable income of the year.
        irpef: Net IRPEF of the year, all withheld by the conguaglio.
        net: Net pay of the year.
        regional: Regional surtax of 2026, withheld in 2027.
        municipal: Municipal surtax of 2026, withheld in 2027.
        municipal_advance: Municipal acconto of 2027.
    """

    minimum: Decimal
    edr: Decimal
    monthly_gross: Decimal
    inps_base: Decimal
    monthly_inps: Decimal
    tfr_divisor: Decimal
    tfr_quota: Decimal
    tfr_deduction: Decimal
    tfr_net_of_extra_ivs: Decimal
    sunday_holiday: Decimal
    november: ConciaPayment
    payments: int
    gross: Decimal
    inps: Decimal
    taxable: Decimal
    irpef: Decimal
    net: Decimal
    regional: Decimal
    municipal: Decimal
    municipal_advance: Decimal


def _year() -> ConciaYear:
    minimum = _MINIMUM_AT_EXPIRY + sum(_TRANCHES, Decimal(0))
    if minimum != _TABLE_MINIMUM_2026:
        msg = f"tranches give {minimum}, Allegato n. 1 states {_TABLE_MINIMUM_2026}"
        raise ValueError(msg)
    edr = _cents(_EDR_LIRE / _LIRE_PER_EURO)
    monthly_gross = minimum + edr
    base = monthly_gross.quantize(Decimal(1), rounding=ROUND_HALF_UP)
    monthly_inps = _inps(base)
    tfr_quota = _cents(monthly_gross / _TFR_DIVISOR)
    tfr_deduction = _cents(base * _TFR_EXTRA_IVS_RATE)
    sunday_holiday = _cents(monthly_gross / _SUNDAY_HOLIDAY_DIVISOR)
    november = _payment(monthly_gross + sunday_holiday, edr + sunday_holiday)
    gross = monthly_gross * (_MONTHS_PAID - 1) + november.gross
    inps = monthly_inps * (_MONTHS_PAID - 1) + november.inps
    taxable = gross - inps
    irpef = net_irpef(taxable)
    municipal = municipal_alghero(taxable, irpef)
    return ConciaYear(
        minimum=minimum,
        edr=edr,
        monthly_gross=monthly_gross,
        inps_base=base,
        monthly_inps=monthly_inps,
        tfr_divisor=_TFR_DIVISOR,
        tfr_quota=tfr_quota,
        tfr_deduction=tfr_deduction,
        tfr_net_of_extra_ivs=tfr_quota - tfr_deduction,
        sunday_holiday=sunday_holiday,
        november=november,
        payments=_MONTHS_PAID,
        gross=gross,
        inps=inps,
        taxable=taxable,
        irpef=irpef,
        net=gross - inps - irpef,
        regional=regional_sardegna(taxable, irpef),
        municipal=municipal,
        municipal_advance=municipal_advance(municipal),
    )


#: The oracle of the scenario described in the module docstring.
CONCIA_D2_2026 = _year()

#: Months of a hire on 1 July: July to December.
_JULY_HIRE_MONTHS = 6
#: Days of employment from 1 July to 31 December 2026.
_JULY_HIRE_DAYS = 184


@dataclass(frozen=True)
class ConciaMidYear:
    """The oracle figures of a Concia D2 hired on 1 July 2026, in EUR.

    Six regular months and a tredicesima of six twelfths, each item of the
    payslip (minimo, EDR) taken to cents on its own, as the payslip shows
    them.  The only income of the year is the employment, so the reddito
    complessivo is its taxable income: below 15,000 EUR, it takes the
    trattamento integrativo and the somma esente, both settled by the
    conguaglio.

    Attributes:
        monthly_gross: Gross of each regular month.
        monthly_inps: Employee INPS of each regular month but November.
        november: The November payment, with the holiday on a Sunday.
        thirteenth_gross: Gross of the tredicesima.
        thirteenth_inps: Employee INPS of the tredicesima.
        payments: Number of payments of the tax year.
        days: Days of employment in the tax year.
        gross: Gross of the year.
        inps: Employee INPS of the year.
        taxable: IRPEF taxable income of the year.
        irpef: Net IRPEF of the year, withheld by the conguaglio.
        trattamento: Trattamento integrativo of the year.
        somma_esente: Somma esente of the year.
        net: Net pay of the year, credits included.
        regional: Regional surtax of 2026, withheld in 2027.
        municipal: Municipal surtax of 2026, withheld in 2027.
    """

    monthly_gross: Decimal
    monthly_inps: Decimal
    november: ConciaPayment
    thirteenth_gross: Decimal
    thirteenth_inps: Decimal
    payments: int
    days: int
    gross: Decimal
    inps: Decimal
    taxable: Decimal
    irpef: Decimal
    trattamento: Decimal
    somma_esente: Decimal
    net: Decimal
    regional: Decimal
    municipal: Decimal


def _whole_euro(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal(1), rounding=ROUND_HALF_UP)


def _july_hire() -> ConciaMidYear:
    full = CONCIA_D2_2026
    share = Decimal(_JULY_HIRE_MONTHS) / 12
    thirteenth = _cents(full.minimum * share) + _cents(full.edr * share)
    thirteenth_inps = _inps(_whole_euro(thirteenth))
    gross = full.monthly_gross * (_JULY_HIRE_MONTHS - 1) + full.november.gross
    gross += thirteenth
    inps = full.monthly_inps * (_JULY_HIRE_MONTHS - 1) + full.november.inps
    inps += thirteenth_inps
    taxable = gross - inps
    irpef = net_irpef(taxable, _JULY_HIRE_DAYS)
    trattamento = trattamento_integrativo(taxable, _JULY_HIRE_DAYS)
    exempt = somma_esente(taxable, _JULY_HIRE_DAYS)
    return ConciaMidYear(
        monthly_gross=full.monthly_gross,
        monthly_inps=full.monthly_inps,
        november=full.november,
        thirteenth_gross=thirteenth,
        thirteenth_inps=thirteenth_inps,
        payments=_JULY_HIRE_MONTHS + 1,
        days=_JULY_HIRE_DAYS,
        gross=gross,
        inps=inps,
        taxable=taxable,
        irpef=irpef,
        trattamento=trattamento,
        somma_esente=exempt,
        net=gross - inps - irpef + trattamento + exempt,
        regional=regional_sardegna(taxable, irpef),
        municipal=municipal_alghero(taxable, irpef),
    )


#: The oracle of a Concia D2 hired on 1 July 2026.
CONCIA_D2_JULY_HIRE_2026 = _july_hire()


__all__ = ["C3_MINIMUM_FROM_JUNE_2026", "employee_taxable"]

C3_MINIMUM_FROM_JUNE_2026 = Decimal("2211.43")

_CENT = Decimal("0.01")
_EMPLOYEE_SHARES = (Decimal("0.0919"), Decimal("0.0030"))


def employee_taxable(gross: Decimal) -> Decimal:
    """Return the IRPEF taxable of a run: gross less employee INPS.

    Valid only for a gross below the IVS massimale and with no pension fund.

    Returns:
        ``gross`` less the IVS and CIGS shares of its whole-euro base, one
        contribution at their whole rate, to cents once.
    """
    base = gross.quantize(Decimal(1), rounding=ROUND_HALF_UP)
    rate = sum(_EMPLOYEE_SHARES, Decimal(0))
    return gross - (base * rate).quantize(_CENT, rounding=ROUND_HALF_UP)
