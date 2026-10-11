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

__all__ = ["CONCIA_D2_2026", "ConciaYear"]

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


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


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
    monthly_inps = _cents(base * _EMPLOYEE_IVS_RATE) + _cents(
        base * _EMPLOYEE_CIGS_RATE
    )
    tfr_quota = _cents(monthly_gross / _TFR_DIVISOR)
    tfr_deduction = _cents(base * _TFR_EXTRA_IVS_RATE)
    gross = monthly_gross * _MONTHS_PAID
    inps = monthly_inps * _MONTHS_PAID
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


__all__ = ["C3_MINIMUM_FROM_JUNE_2026", "employee_taxable"]

C3_MINIMUM_FROM_JUNE_2026 = Decimal("2211.43")

_CENT = Decimal("0.01")
_EMPLOYEE_SHARES = (Decimal("0.0919"), Decimal("0.0030"))


def employee_taxable(gross: Decimal) -> Decimal:
    """Return the IRPEF taxable of a run: gross less employee INPS.

    Valid only for a gross below the IVS massimale and with no pension fund.

    Returns:
        ``gross`` less the IVS and CIGS shares of its whole-euro base.
    """
    base = gross.quantize(Decimal(1), rounding=ROUND_HALF_UP)
    inps = sum(
        (
            (base * share).quantize(_CENT, rounding=ROUND_HALF_UP)
            for share in _EMPLOYEE_SHARES
        ),
        Decimal(0),
    )
    return gross - inps
