"""Hand oracles of a year and of a termination per contribution sector and CCNL.

Each scenario is a worker hired on 1 January 2026 by an employer in
Sardegna (Alghero), with no pension fund of their own, no family deduction
and a 2025 income of 40,000 EUR (no renewal substitute tax):

- industria: Metalmeccanico Federmeccanica C3 impiegato, 50 employees, two
  hours of weekday overtime on 10 March;
- terziario: Terziario Confesercenti IV, 50 employees, fourteen payments;
- commercio: Terziario Confcommercio 4th level, 50 employees, fourteen
  payments, a provincial element in force;
- edilizia: ANCE operaio of the 1st level, 30 employees, 173 hours a month;
- studi: Studi Professionali Confprofessioni 4th level, 10 employees,
  fourteen payments;
- turismo: Turismo Federalberghi 4th level, 10 employees, fourteen
  payments and the tranche of May;
- chimica: Chimica Farmaceutica Federchimica D1 impiegato, 50 employees,
  the tranche of July;
- alimentari: Industria Alimentare 3rd level impiegato, 50 employees,
  fourteen payments with the EDR on thirteen;
- dmo: Distribuzione Moderna Organizzata IV, 50 employees, a provincial
  element in force, fourteen payments;
- fipe: Pubblici Esercizi 4th level, 10 employees, the tranche of June
  and the 0.77% sickness supplement;
- ristorazione: Ristorazione Collettiva 4th level, 10 employees, the
  tranche of September;
- confapi: Metalmeccanico Unionmeccanica Confapi 5th level impiegato, 50
  employees, the tranche of June;
- edilizia-impiegati: ANCE impiegato of the 3rd level, 30 employees,
  fourteen payments, the EDR outside the TFR and the Prevedi contributo
  contrattuale.

Each runs for the whole year and, apart, until a termination on 30 June.

These are hand oracles from the same primary sources the bundle reads: the
signed tables, the statutes and the INPS rate tables, each cited where it
is used.  They check the pipeline of the engine (pay, INPS, TFR, employer
cost, IRPEF, credits and surtax at the conguaglio), not the transcription
of the sources, and they are no independent output: no oracle here is a
``verified`` reference case.  Nothing is read from the bundle or the engine.

Conventions, as the payslips print them: every pay item is taken to cents
on its own; the INPS base is the gross to the whole euro; the IVS share and
the other shares of the worker and of the employer are each taken to cents
(they part above the IVS massimale); the TFR quota is the TFR base over
13.5 (art. 2120 c.c.) less the 0.50% additional IVS of the INPS base the
employer offsets (L. 297/1982 art. 3 c. 16); the employer cost is the
gross, the employer INPS and the TFR accrued, plus the employer pension
contribution and its 10% solidarity contribution where the CCNL owes one.
It leaves out the INAIL premium, IRAP and the amounts the CCNL owes that
the engine does not compute (open ``owed`` limitations).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from tests.knowledge.ccnl_engine.irpef.oracles import (
    employment_deduction,
    gross_irpef,
    net_irpef,
)
from tests.knowledge.ccnl_engine.surtax.oracles import (
    municipal_alghero,
    regional_sardegna,
)
from tests.knowledge.ccnl_engine.tax_credit.oracles import (
    somma_esente,
    trattamento_integrativo,
)

__all__ = [
    "ALIMENTARI_JUNE",
    "ALIMENTARI_YEAR",
    "APPRENTICE_JUNE",
    "APPRENTICE_YEAR",
    "CHIMICA_JUNE",
    "CHIMICA_YEAR",
    "COMMERCIO_JUNE",
    "COMMERCIO_YEAR",
    "CONFAPI_JUNE",
    "CONFAPI_YEAR",
    "DMO_JUNE",
    "DMO_YEAR",
    "EDILIZIA_IMPIEGATI_JUNE",
    "EDILIZIA_IMPIEGATI_YEAR",
    "EDILIZIA_JUNE",
    "EDILIZIA_YEAR",
    "FIPE_JUNE",
    "FIPE_YEAR",
    "FIXED_TERM_JUNE",
    "FIXED_TERM_YEAR",
    "INDUSTRIA_JUNE",
    "INDUSTRIA_YEAR",
    "MID_MONTH_FROM",
    "MID_MONTH_UNTIL",
    "MID_MONTH_YEAR",
    "PART_TIME_JUNE",
    "PART_TIME_YEAR",
    "RISTORAZIONE_JUNE",
    "RISTORAZIONE_YEAR",
    "SICKNESS_YEAR",
    "SICK_FROM",
    "SICK_UNTIL",
    "STUDI_JUNE",
    "STUDI_YEAR",
    "TERZIARIO_JUNE",
    "TERZIARIO_YEAR",
    "TURISMO_JUNE",
    "TURISMO_YEAR",
    "Payment",
    "Rates",
    "SectorYear",
]

_CENT = Decimal("0.01")
_ZERO = Decimal(0)
_TFR_DIVISOR = Decimal("13.5")
_TFR_EXTRA_IVS = Decimal("0.0050")
_FULL_YEAR = 365
#: 1 January to 30 June 2026.
_HALF_YEAR = 181


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def _whole_euro(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal(1), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Rates:
    """INPS shares of a sector, tier and category, as fractions.

    ``employer_supplement`` is an employer contribution INPS charges apart,
    taken to cents on its own (the 0.77% sickness supplement of the
    pubblici esercizi).  ``tfr_offset`` is the additional IVS the employer
    deducts from the TFR quota: none for an apprentice.
    """

    employee_ivs: Decimal
    employee_other: Decimal
    employer_ivs: Decimal
    employer_other: Decimal
    employer_supplement: Decimal = _ZERO
    tfr_offset: Decimal = _TFR_EXTRA_IVS


@dataclass(frozen=True)
class HealthFund:
    """A fund the CCNL owes for every worker, with no alternative element.

    The employer pays it on every monthly payment, with the 10% INPS
    solidarity on it (an employer contribution); a welfare amount is made
    available once a year, in its month, outside the pay.

    Attributes:
        monthly: Employer share a month.
        welfare: Welfare amount of the year.
        welfare_month: Month the welfare amount is made available in.
    """

    monthly: Decimal
    welfare: Decimal = _ZERO
    welfare_month: int = 0


#: mètaSalute, 13 EUR a month (CCNL 5 February 2021 art. 16, p. 184), and
#: the flexible benefits of 250 EUR, made available by February in 2026
#: (ipotesi 22 November 2025, p. 3).
METASALUTE = HealthFund(Decimal(13), Decimal(250), 2)
#: EBM Salute, 8 EUR a month from 2022 (accordo 4 June 2026, p. 22).
EBM_SALUTE = HealthFund(Decimal(8))
_SOLIDARITY = Decimal("0.10")


@dataclass(frozen=True)
class Pay:
    """What one payment pays, from the cited tables.

    Attributes:
        run_id: Run of the engine the payment is.
        gross: Gross of the payment.
        tfr_base: Part of the gross in the TFR base.
        fund: Employer pension contribution, part of the employer cost.
        solidarity: The 10% solidarity contribution the employer pays to
            INPS on ``fund``: an employer contribution.
        cassa_net: Accrual paid through the Cassa Edile, net of the
            withholding the Cassa makes: in the gross, not in the cash.
        absence: Pay deducted for days of absence, which the run posts
            apart from the gross (the sick pay that replaces it is in the
            gross).
    """

    run_id: str
    gross: Decimal
    tfr_base: Decimal
    fund: Decimal = _ZERO
    solidarity: Decimal = _ZERO
    cassa_net: Decimal = _ZERO
    absence: Decimal = _ZERO


@dataclass(frozen=True)
class Payment:
    """The oracle figures of one payment."""

    run_id: str
    gross: Decimal
    inps_base: Decimal
    employee_inps: Decimal
    employer_inps: Decimal
    employer_contributions: Decimal
    tfr_quota: Decimal
    tfr_deduction: Decimal
    tfr_accrual: Decimal
    employer_cost: Decimal
    absence: Decimal = _ZERO


@dataclass(frozen=True)
class SectorYear:
    """The oracle figures of a scenario.

    Attributes:
        payments: Each payment, in payment order.
        days: Days of employment in the tax year.
        gross: Gross of the year.
        inps: Employee INPS of the year.
        taxable: IRPEF taxable income of the year.
        irpef: Net ordinary IRPEF of the year.
        credits: Trattamento integrativo and somma esente of the year.
        surtax: Regional and municipal surtax withheld in the year: the
            whole 2026 surtax at a termination, none otherwise.
        cassa_net: Pay settled through the Cassa Edile.
        net: Cash paid to the worker in the year.
        tfr: TFR accrued in the year.
        employer_cost: Employer cost of the year.
    """

    payments: tuple[Payment, ...]
    days: int
    gross: Decimal
    inps: Decimal
    taxable: Decimal
    irpef: Decimal
    credits: Decimal
    surtax: Decimal
    cassa_net: Decimal
    net: Decimal
    tfr: Decimal
    employer_cost: Decimal


def _with_fund(pay: Pay, health: HealthFund | None) -> Pay:
    """Add the employer share of ``health`` to a monthly payment.

    Returns:
        ``pay`` with the share and its solidarity, and the welfare in its
        month; unchanged for an extra month or without a fund.
    """
    if health is None or not pay.run_id.endswith(("regular", "termination")):
        return pay
    month = int(pay.run_id[5:7])
    welfare = health.welfare if month == health.welfare_month else _ZERO
    return replace(
        pay,
        fund=pay.fund + health.monthly + welfare,
        solidarity=pay.solidarity + _cents(health.monthly * _SOLIDARITY),
    )


def _payment(pay: Pay, rates: Rates) -> Payment:
    paid = pay.gross - pay.absence
    base = _whole_euro(paid)
    employee = _cents(base * rates.employee_ivs) + _cents(base * rates.employee_other)
    employer = (
        _cents(base * rates.employer_ivs)
        + _cents(base * rates.employer_other)
        + _cents(base * rates.employer_supplement)
    )
    quota = _cents(pay.tfr_base / _TFR_DIVISOR)
    deduction = _cents(base * rates.tfr_offset)
    accrual = quota - deduction
    return Payment(
        run_id=pay.run_id,
        gross=pay.gross,
        inps_base=base,
        employee_inps=employee,
        employer_inps=employer,
        employer_contributions=employer + pay.solidarity,
        tfr_quota=quota,
        tfr_deduction=deduction,
        tfr_accrual=accrual,
        employer_cost=paid + employer + pay.solidarity + accrual + pay.fund,
        absence=pay.absence,
    )


def _trattamento(taxable: Decimal, days: int) -> Decimal:
    """Return the trattamento integrativo, zero above 15,000 EUR when it is.

    Between 15,000 and 28,000 EUR it is due only when the deductions of
    art. 13 c. 1 TUIR (no family deduction here) exceed the gross tax (D.L.
    3/2020 art. 1 c. 1, second period); the oracle checks they do not.

    Returns:
        The credit of the year.

    Raises:
        ValueError: When the band above 15,000 EUR would grant it.
    """
    if taxable <= Decimal(15_000):
        return trattamento_integrativo(taxable, days)
    if taxable <= Decimal(28_000) and employment_deduction(taxable, days) > gross_irpef(
        taxable
    ):
        msg = f"the band above 15,000 EUR grants a credit at {taxable}"
        raise ValueError(msg)
    return _ZERO


def sector_year(
    pays: tuple[Pay, ...],
    rates: Rates,
    days: int,
    *,
    terminated: bool,
    health: HealthFund | None = None,
) -> SectorYear:
    """Return the oracle of the payments ``pays`` of one tax year.

    Returns:
        The figures of each payment and of the year.
    """
    payments = tuple(_payment(_with_fund(pay, health), rates) for pay in pays)
    gross = sum((p.gross for p in payments), _ZERO)
    absence = sum((p.absence for p in payments), _ZERO)
    inps = sum((p.employee_inps for p in payments), _ZERO)
    taxable = gross - absence - inps
    irpef = net_irpef(taxable, days)
    tax_credits = _trattamento(taxable, days) + somma_esente(taxable, days)
    surtax = (
        regional_sardegna(taxable, irpef) + municipal_alghero(taxable, irpef)
        if terminated
        else _ZERO
    )
    cassa_net = sum((pay.cassa_net for pay in pays), _ZERO)
    return SectorYear(
        payments=payments,
        days=days,
        gross=gross,
        inps=inps,
        taxable=taxable,
        irpef=irpef,
        credits=tax_credits,
        surtax=surtax,
        cassa_net=cassa_net,
        net=gross - absence - inps - irpef + tax_credits - surtax - cassa_net,
        tfr=sum((p.tfr_accrual for p in payments), _ZERO),
        employer_cost=sum((p.employer_cost for p in payments), _ZERO),
    )


def _run(month: int, kind: str = "regular") -> str:
    return f"2026-{month:02d}-{kind}"


# Industria: Metalmeccanico Federmeccanica C3.

#: C3 minimo from 1 June 2025, verbale of 12 June 2025, p. 1 (sha256
#: e60921cadc971b86632a284ae357f6e55804c9737b7d41be831112ff56349360):
#: "C3 2.158,26".
_C3_UNTIL_MAY = Decimal("2158.26")
#: C3 minimo from 1 June 2026, ipotesi of 22 November 2025, p. 2 (sha256
#: 37152685c30627ee755fa5593faee689db76fa42a70b87f30661e9561f40f4ec):
#: "C3 2.211,43 2.271,01 2.335,88".
_C3_FROM_JUNE = Decimal("2211.43")
#: Hourly divisor 173 and the first two hours of weekday overtime at 25%:
#: CCNL 5 February 2021, Sez. Quarta, Titolo III, Art. 7, p. 161 (sha256
#: ff182dd8aeb42b15b236c48775030a12720b9affabba460d38e426ec7be5c151):
#: "a) lavoro straordinario: prime due ore ... 25%"; the hours after are paid
#: 30%.  Two hours on one day stay within the first band under any reading.
_C3_HOURLY = (_C3_UNTIL_MAY / 173).quantize(Decimal("0.00001"), ROUND_HALF_UP)
OVERTIME_HOURS = Decimal(2)
_OVERTIME = _cents(OVERTIME_HOURS * _C3_HOURLY * Decimal("1.25"))
#: Industria impiegato, 16 to 50 employees: employer IVS 23.81 and CUAF
#: 0.68, NASpI 1.61, Fondo garanzia TFR 0.20, maternità 0.46, CIGO 1.70
#: (D.Lgs. 148/2015 art. 13 c. 1 lett. a) and CIGS 0.60 (art. 23 c. 1):
#: 5.25; worker IVS 9.19 and CIGS 0.30.  Assimpredil ANCE tables 1/2026 and
#: 2/2026 (sha256 83508e4e61d305be578ecb224a00bdf4f7628214578999a02d4763d93f58756f)
#: for the shares the industria shares with the edilizia.
_INDUSTRIA = Rates(
    employee_ivs=Decimal("0.0919"),
    employee_other=Decimal("0.0030"),
    employer_ivs=Decimal("0.2381"),
    employer_other=Decimal("0.0525"),
)
#: An occasional overtime is outside the TFR base: art. 2120 c. 2 c.c.
#: counts the sums paid "a titolo non occasionale".


def _industria_year() -> tuple[Pay, ...]:
    minima = [_C3_UNTIL_MAY if m < 6 else _C3_FROM_JUNE for m in range(1, 13)]
    months = [Pay(_run(m), pay, pay) for m, pay in enumerate(minima, start=1)]
    march = months[2]
    months[2] = Pay(march.run_id, march.gross + _OVERTIME, march.gross)
    #: Tredicesima of twelve twelfths of the December minimo: CCNL 2021,
    #: Sez. Quarta, Titolo IV, Art. 13 (additional_months 13).
    thirteenth = Pay(_run(12, "thirteenth"), _C3_FROM_JUNE, _C3_FROM_JUNE)
    return (*months, thirteenth)


def _industria_year_without_overtime() -> tuple[Pay, ...]:
    minima = [_C3_UNTIL_MAY if m < 6 else _C3_FROM_JUNE for m in range(1, 13)]
    months = [Pay(_run(m), pay, pay) for m, pay in enumerate(minima, start=1)]
    thirteenth = Pay(_run(12, "thirteenth"), _C3_FROM_JUNE, _C3_FROM_JUNE)
    return (*months, thirteenth)


def _industria_june() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _C3_UNTIL_MAY, _C3_UNTIL_MAY) for m in range(1, 6)]
    #: Six twelfths of the tredicesima are paid with the last month.
    ratei = _cents(_C3_FROM_JUNE * 6 / 12)
    june = _C3_FROM_JUNE + ratei
    return (*pays, Pay(_run(6), june, june))


INDUSTRIA_YEAR = sector_year(
    _industria_year(), _INDUSTRIA, _FULL_YEAR, terminated=False, health=METASALUTE
)
INDUSTRIA_JUNE = sector_year(
    _industria_june(), _INDUSTRIA, _HALF_YEAR, terminated=True, health=METASALUTE
)


# Part time: the same C3 impiegato on 20 of 40 weekly hours.

#: A part-time worker is paid the full-time pay in proportion to the
#: hours (D.Lgs. 81/2015 art. 7 c. 1; CCNL 5 February 2021, Sez. Quarta,
#: Titolo I, Art. 4): half of each minimo, taken to cents.
_HALF = Decimal("0.5")


def _part_time(pays: tuple[Pay, ...]) -> tuple[Pay, ...]:
    return tuple(
        Pay(p.run_id, _cents(p.gross * _HALF), _cents(p.tfr_base * _HALF)) for p in pays
    )


def _part_time_june() -> tuple[Pay, ...]:
    month = _cents(_C3_UNTIL_MAY * _HALF)
    pays = [Pay(_run(m), month, month) for m in range(1, 6)]
    last = _cents(_C3_FROM_JUNE * _HALF)
    #: Six twelfths of the part-time tredicesima, with the last month.
    june = last + _cents(last * 6 / 12)
    return (*pays, Pay(_run(6), june, june))


PART_TIME_YEAR = sector_year(
    _part_time(_industria_year_without_overtime()),
    _INDUSTRIA,
    _FULL_YEAR,
    terminated=False,
    health=METASALUTE,
)
PART_TIME_JUNE = sector_year(
    _part_time_june(), _INDUSTRIA, _HALF_YEAR, terminated=True, health=METASALUTE
)


# Terziario: Terziario Confesercenti IV.

#: Level IV, paga base and contingenza: accordo integrativo 28 March 2024,
#: tabelle 2023-2027, p. 3 (sha256
#: 31788db6977a060829e19b5f4a6f2ed5528d774a62c14be677e55cf2076b7870):
#: "IV 1257,46 524,22 1781,68" from 1 November 2025, "1292,46 524,22
#: 1816,68" from 1 November 2026.
_IV_UNTIL_OCTOBER = Decimal("1781.68")
_IV_FROM_NOVEMBER = Decimal("1816.68")
#: Terziario above 15 employees, INPS circ. 117/2022 all. 1 (sha256
#: 28e59dd5733b1ea15bdea8225c85412ca9913a3c39279e5ec59d1fc5b1d156da):
#: employer IVS 23.81 and NASpI 1.31 + 0.30, Fondo garanzia TFR 0.20, CUAF
#: 0.68, maternità 0.24, malattia 2.44, FIS 0.53333 (0.80 less the worker
#: third, D.Lgs. 148/2015 art. 29 c. 8, art. 33 c. 1) and CIGS 0.60 (art.
#: 20 c. 3-bis): 6.30333; worker IVS 9.19, FIS 0.26667 and CIGS 0.30.
_TERZIARIO = Rates(
    employee_ivs=Decimal("0.0919"),
    employee_other=Decimal("0.0056667"),
    employer_ivs=Decimal("0.2381"),
    employer_other=Decimal("0.0630333"),
)


# Apprentice: a professionalizzante apprentice of destination C3.

#: Professionalizzante of 36 months, 85% of the minimo of the destination
#: level in the first 12 months: CCNL 5 February 2021, Disciplina
#: dell'apprendistato professionalizzante, Art. 8, p. 267 ("36 12 85% 12
#: 90% 12 95%"), each pay taken to cents.
_APPRENTICE_PCT = Decimal("0.85")
#: Apprentice of an industria employer from 16 to 50 employees: employer
#: 10% (L. 296/2006 art. 1 c. 773) + NASpI 1.61% (L. 92/2012 art. 2 c. 36
#: and art. 25 L. 845/1978) + CIGO 1.70% and CIGS 0.60% (D.Lgs. 148/2015
#: artt. 13, 23, extended to apprentices by L. 234/2021), worker 5.84% +
#: CIGS 0.30%.  No additional 0.50% IVS is deducted from the TFR of an
#: apprentice (INPS circ. 70/2007, note 5).
_APPRENTICE = Rates(
    employee_ivs=Decimal("0.0584"),
    employee_other=Decimal("0.0030"),
    employer_ivs=Decimal("0.1000"),
    employer_other=Decimal("0.0391"),
    tfr_offset=_ZERO,
)


def _apprentice(pays: tuple[Pay, ...]) -> tuple[Pay, ...]:
    pct = _APPRENTICE_PCT
    return tuple(
        Pay(p.run_id, _cents(p.gross * pct), _cents(p.tfr_base * pct)) for p in pays
    )


def _apprentice_june() -> tuple[Pay, ...]:
    month = _cents(_C3_UNTIL_MAY * _APPRENTICE_PCT)
    pays = [Pay(_run(m), month, month) for m in range(1, 6)]
    last = _cents(_C3_FROM_JUNE * _APPRENTICE_PCT)
    #: Six twelfths of the apprentice tredicesima, with the last month.
    june = last + _cents(last * 6 / 12)
    return (*pays, Pay(_run(6), june, june))


APPRENTICE_YEAR = sector_year(
    _apprentice(_industria_year_without_overtime()),
    _APPRENTICE,
    _FULL_YEAR,
    terminated=False,
    health=METASALUTE,
)
APPRENTICE_JUNE = sector_year(
    _apprentice_june(), _APPRENTICE, _HALF_YEAR, terminated=True, health=METASALUTE
)


# Fixed term: the C3 impiegato on a fixed term of the year, no renewal.

#: The additional NASpI contribution of a fixed-term employment, 1.40% of
#: the INPS taxable pay (L. 92/2012 art. 2 c. 28), charged apart from the
#: rates of the industria impiegato.
_FIXED_TERM = replace(_INDUSTRIA, employer_supplement=Decimal("0.0140"))

FIXED_TERM_YEAR = sector_year(
    _industria_year_without_overtime(),
    _FIXED_TERM,
    _FULL_YEAR,
    terminated=True,
    health=METASALUTE,
)
FIXED_TERM_JUNE = sector_year(
    _industria_june(), _FIXED_TERM, _HALF_YEAR, terminated=True, health=METASALUTE
)


# Sickness: the C3 impiegato sick from 9 to 18 March.

#: Nine working days of sickness, Monday to Saturday, from 9 to 18 March:
#: the month deducts them at 1/26 of the minimo each and pays them back
#: at 100%, the three days of carenza and the six after: CCNL 5 February
#: 2021, Sez. Quarta, Art. 2 (Trattamento in caso di malattia), PDF p. 202:
#: "alla intera retribuzione globale per i primi 122 giorni di calendario".
#: INPS pays no sickness indemnity to the impiegati of the industria.
_SICK_DAYS = 9
_SICK_DAY = _cents(_C3_UNTIL_MAY / 26)
SICK_FROM = date(2026, 3, 9)
SICK_UNTIL = date(2026, 3, 18)


def _sickness_year() -> tuple[Pay, ...]:
    pays = list(_industria_year_without_overtime())
    absence = _SICK_DAY * _SICK_DAYS
    march = pays[2]
    pays[2] = Pay(march.run_id, march.gross + absence, march.tfr_base, absence=absence)
    return tuple(pays)


SICKNESS_YEAR = sector_year(
    _sickness_year(), _INDUSTRIA, _FULL_YEAR, terminated=False, health=METASALUTE
)


# Mid-month: the C3 impiegato hired on 10 March and leaving on 20 October.

#: A month employed in part pays 1/26 of the monthly pay for each working
#: day, Monday to Saturday (CCNL 5 February 2021, Sez. Quarta, Titolo III,
#: Art. 9, p. 164: "una quota giornaliera della retribuzione di fatto, pari
#: a 1/26 della retribuzione mensile fissa"): 19 days from 10 to 31 March,
#: 17 from 1 to 20 October.  The ratei of the tredicesima count a fraction
#: above 15 days as a month (Titolo IV, Art. 7 c. 3, p. 178): March to
#: October, eight twelfths, paid with the last month.
MID_MONTH_FROM = date(2026, 3, 10)
MID_MONTH_UNTIL = date(2026, 10, 20)
_MID_MONTH_DAYS = (MID_MONTH_UNTIL - MID_MONTH_FROM).days + 1


def _mid_month() -> tuple[Pay, ...]:
    march = _cents(_C3_UNTIL_MAY * 19 / 26)
    months = [Pay(_run(3), march, march)]
    for m in range(4, 10):
        pay = _C3_UNTIL_MAY if m < 6 else _C3_FROM_JUNE
        months.append(Pay(_run(m), pay, pay))
    october = _cents(_C3_FROM_JUNE * 17 / 26) + _cents(_C3_FROM_JUNE * 8 / 12)
    return (*months, Pay(_run(10), october, october))


MID_MONTH_YEAR = sector_year(
    _mid_month(), _INDUSTRIA, _MID_MONTH_DAYS, terminated=True, health=METASALUTE
)


def _iv(month: int) -> Decimal:
    return _IV_UNTIL_OCTOBER if month < 11 else _IV_FROM_NOVEMBER


def _terziario_year() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _iv(m), _iv(m)) for m in range(1, 13)]
    #: Quattordicesima: one twelfth for each month from July to June (Art.
    #: 221 of the Testo Unico 2019), six for a hire on 1 January, paid on 1
    #: July; tredicesima of twelve twelfths in December (Art. 220).
    fourteenth = _cents(_IV_UNTIL_OCTOBER * 6 / 12)
    pays.insert(6, Pay(_run(6, "fourteenth"), fourteenth, fourteenth))
    pays.insert(12, Pay(_run(12, "thirteenth"), _IV_FROM_NOVEMBER, _IV_FROM_NOVEMBER))
    return tuple(pays)


#: Residual leave paid on the last regular run (Testo Unico 12 December
#: 2019, sha256 18a2f10cf41209a56523473660321348214c1d8d54900257cf805ad8488f7ec0):
#: six whole months of 26 days of ferie (Art. 159, p. 126), 13 days at the
#: monthly pay over 26 (chiarimento a verbale, p. 127); six twelfths of the
#: 32 hours of ex festività (Art. 158 c. 1, p. 125), 16 hours at the monthly
#: pay over the hourly divisor 168; no ROL in the first two years of a
#: worker hired after 1 March 2011 (Art. 158, p. 126).
_TERZIARIO_LEAVE = _cents(Decimal(13) * _IV_UNTIL_OCTOBER / 26) + _cents(
    Decimal(16) * _IV_UNTIL_OCTOBER / 168
)


def _terziario_june() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _IV_UNTIL_OCTOBER, _IV_UNTIL_OCTOBER) for m in range(1, 6)]
    rateo = _cents(_IV_UNTIL_OCTOBER * 6 / 12)
    june = _IV_UNTIL_OCTOBER + rateo + _TERZIARIO_LEAVE
    return (
        *pays,
        Pay(_run(6), june, june),
        Pay(_run(6, "fourteenth"), rateo, rateo),
    )


TERZIARIO_YEAR = sector_year(
    _terziario_year(), _TERZIARIO, _FULL_YEAR, terminated=False
)
TERZIARIO_JUNE = sector_year(_terziario_june(), _TERZIARIO, _HALF_YEAR, terminated=True)


# Studi: Studi Professionali Confprofessioni, 4th level, 10 employees.

#: 4th level minimo tabellare: CCNL 16 February 2024, Art. 140, p. 72
#: (sha256 89c22bb20be410166e3538e3cdc14b011e712ce93d00ed94b54dfb67a4e8b544):
#: "4° 1.595,42 18,70 1.614,12", in force until 30 November 2026 and from
#: 1 December 2026.
_STUDI_UNTIL_NOVEMBER = Decimal("1595.42")
_STUDI_FROM_DECEMBER = Decimal("1614.12")
#: Studi professionali from 6 to 15 employees: the terziario shares of INPS
#: circ. 117/2022 all. 1 (employer IVS 23.81, NASpI 1.31 + 0.30, Fondo
#: garanzia TFR 0.20, CUAF 0.68, maternità 0.24, malattia 2.44; worker IVS
#: 9.19), with the Fondo di solidarietà bilaterale per le attività
#: professionali in place of the FIS: D.I. 21 May 2024 art. 6 c. 1 lett. b)
#: (sha256 fd1d01d5444dff1cfdd2cf5d0a12ff5b2ee5c1fca8a64758e61f4a7bee9c9bbf),
#: "0,80%, di cui due terzi a carico del datore di lavoro e un terzo a
#: carico del lavoratore" above five and up to fifteen employees.  No CIGS
#: up to 15 employees.  The worker is owed the INPS sickness indemnity (Art.
#: 120), so the employer pays the malattia share.
_STUDI = Rates(
    employee_ivs=Decimal("0.0919"),
    employee_other=Decimal("0.0026667"),
    employer_ivs=Decimal("0.2381"),
    employer_other=Decimal("0.0570333"),
)
#: Quattordicesima of one monthly pay "in atto allo stesso 30 giugno", in
#: twelfths for a worker hired within the year (Art. 143, p. 74, with Art.
#: 142): six for a hire on 1 January; tredicesima of one monthly pay at
#: Christmas (Art. 142).
_STUDI_FOURTEENTH = _cents(_STUDI_UNTIL_NOVEMBER * 6 / 12)


def _studi(month: int) -> Decimal:
    return _STUDI_UNTIL_NOVEMBER if month < 12 else _STUDI_FROM_DECEMBER


def _studi_year() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _studi(m), _studi(m)) for m in range(1, 13)]
    pays.insert(6, Pay(_run(6, "fourteenth"), _STUDI_FOURTEENTH, _STUDI_FOURTEENTH))
    thirteenth = _STUDI_FROM_DECEMBER
    pays.insert(12, Pay(_run(12, "thirteenth"), thirteenth, thirteenth))
    return tuple(pays)


def _studi_june() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _studi(m), _studi(m)) for m in range(1, 6)]
    #: Six twelfths of the tredicesima are paid with the last month.
    june = _STUDI_UNTIL_NOVEMBER + _cents(_STUDI_UNTIL_NOVEMBER * 6 / 12)
    return (
        *pays,
        Pay(_run(6), june, june),
        Pay(_run(6, "fourteenth"), _STUDI_FOURTEENTH, _STUDI_FOURTEENTH),
    )


STUDI_YEAR = sector_year(_studi_year(), _STUDI, _FULL_YEAR, terminated=False)
STUDI_JUNE = sector_year(_studi_june(), _STUDI, _HALF_YEAR, terminated=True)


# Turismo: Turismo Federalberghi, 4th level, 10 employees.

#: 4th level paga base nazionale conglobata: ipotesi of 5 July 2024, art.
#: 152 c. 1, p. 42 (sha256
#: a84052fc9e3063cf5379ae1e6374eaa0cbfdcd6de5abaf57513b0395805dea0b, a
#: scan read by OCR): "4 1.620,69 1.660,69 1.695,69 1.730,69 1.750,69"
#: from July 2024, June 2025, May 2026, April 2027 and November 2027.
_TURISMO_UNTIL_APRIL = Decimal("1660.69")
_TURISMO_FROM_MAY = Decimal("1695.69")
#: Terziario from 6 to 15 employees, INPS circ. 117/2022 all. 1: employer
#: IVS 23.81, NASpI 1.31 + 0.30, Fondo garanzia TFR 0.20, CUAF 0.68,
#: maternità 0.24, malattia 2.44 and FIS 0.53333 (0.80 above five
#: employees less the worker third, D.Lgs. 148/2015 art. 29 c. 8, art. 33
#: c. 1); worker IVS 9.19 and FIS 0.26667.  No CIGS up to 15 employees.
_TURISMO = Rates(
    employee_ivs=Decimal("0.0919"),
    employee_other=Decimal("0.0026667"),
    employer_ivs=Decimal("0.2381"),
    employer_other=Decimal("0.0570333"),
)
#: Quattordicesima of the pay "in atto al 30 giugno", in twelfths of the
#: twelve months before 1 July (art. 161 cc. 1, 4, p. 46): six for a hire
#: on 1 January; tredicesima of one monthly pay at Christmas (art. 160 c.
#: 1, p. 45).
_TURISMO_FOURTEENTH = _cents(_TURISMO_FROM_MAY * 6 / 12)


def _turismo(month: int) -> Decimal:
    return _TURISMO_UNTIL_APRIL if month < 5 else _TURISMO_FROM_MAY


def _turismo_year() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _turismo(m), _turismo(m)) for m in range(1, 13)]
    fourteenth = _TURISMO_FOURTEENTH
    pays.insert(6, Pay(_run(6, "fourteenth"), fourteenth, fourteenth))
    thirteenth = _TURISMO_FROM_MAY
    pays.append(Pay(_run(12, "thirteenth"), thirteenth, thirteenth))
    return tuple(pays)


def _turismo_june() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _turismo(m), _turismo(m)) for m in range(1, 6)]
    #: Six twelfths of the tredicesima are paid with the last month.
    june = _TURISMO_FROM_MAY + _cents(_TURISMO_FROM_MAY * 6 / 12)
    fourteenth = _TURISMO_FOURTEENTH
    return (
        *pays,
        Pay(_run(6), june, june),
        Pay(_run(6, "fourteenth"), fourteenth, fourteenth),
    )


TURISMO_YEAR = sector_year(_turismo_year(), _TURISMO, _FULL_YEAR, terminated=False)
TURISMO_JUNE = sector_year(_turismo_june(), _TURISMO, _HALF_YEAR, terminated=True)


# Chimica: Chimica Farmaceutica Federchimica D1 impiegato, 50 employees.

#: D1 trattamento economico minimo, minimo and IPO: ipotesi of 15 April
#: 2025, allegato TEM, p. 48 (sha256
#: 00f87d6fbef42494d47d90dab50146e353b31cbef4ca1f03d6f7ea37d97546ee, a
#: scan read by OCR): "D1 | ... | 2.008,03 352,23 | 2.053,03 367,23 |"
#: from 1 December 2025 and 1 July 2026.  D1 holds no EAR (art. 15 B 3)
#: and its EDR starts in July 2027.
_D1_UNTIL_JUNE = Decimal("2008.03") + Decimal("352.23")
_D1_FROM_JULY = Decimal("2053.03") + Decimal("367.23")


def _d1(month: int) -> Decimal:
    return _D1_UNTIL_JUNE if month < 7 else _D1_FROM_JULY


def _chimica_year() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _d1(m), _d1(m)) for m in range(1, 13)]
    #: Tredicesima of one monthly pay, paid "alla vigilia di Natale"
    #: before the December pay: CCNL 10 May 2006 (CNEL n. 579), art. 21.
    pays.insert(11, Pay(_run(12, "thirteenth"), _D1_FROM_JULY, _D1_FROM_JULY))
    return tuple(pays)


def _chimica_june() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _d1(m), _d1(m)) for m in range(1, 6)]
    #: Six twelfths of the tredicesima are paid with the last month.
    june = _D1_UNTIL_JUNE + _cents(_D1_UNTIL_JUNE * 6 / 12)
    return (*pays, Pay(_run(6), june, june))


CHIMICA_YEAR = sector_year(_chimica_year(), _INDUSTRIA, _FULL_YEAR, terminated=False)
CHIMICA_JUNE = sector_year(_chimica_june(), _INDUSTRIA, _HALF_YEAR, terminated=True)


# Alimentari: Industria Alimentare 3rd level impiegato, 50 employees.

#: CCNL 1 March 2024 (sha256
#: 11792ad3df71999684bae85fea8aaf1e3d492d477043eecc78545b5f41db842c, PDF
#: pages): minimo of the 3rd level from 1 January 2026, Art. 51 lett. A
#: (p. 116, "3 130 ... 1566,16 37,01 1603,17"); ex contingenza 522,32
#: (Art. 52, p. 121); EDR "di euro 10,33 mensili per 13 mensilità" (Art.
#: 52, p. 121); IAR 85,41 from 1 December 2023 (Art. 51 lett. D, p. 118).
_ALIMENTARI_ITEMS = (
    Decimal("1566.16"),
    Decimal("522.32"),
    Decimal("85.41"),
)
_ALIMENTARI_EDR = Decimal("10.33")
_ALIMENTARI = sum(_ALIMENTARI_ITEMS, _ALIMENTARI_EDR)


def _twelfths(items: tuple[Decimal, ...], months: int) -> Decimal:
    """Return ``months`` twelfths of a pay, each item taken to cents.

    Returns:
        The sum of the twelfths of the items.
    """
    return sum((_cents(item * months / 12) for item in items), _ZERO)


#: Tredicesima of the monthly pay at Christmas and quattordicesima of the
#: monthly pay (Art. 54, p. 123), both in twelfths for a hire within the
#: year; the quattordicesima leaves out the EDR, paid on 13 months, and
#: accrues from 1 July to 30 June as the gratifica speciale of the operai
#: (p. 215), paid with the June pay: six twelfths for a hire on 1 January.
_ALIMENTARI_FOURTEENTH = _twelfths(_ALIMENTARI_ITEMS, 6)


def _alimentari_year() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _ALIMENTARI, _ALIMENTARI) for m in range(1, 13)]
    fourteenth = _ALIMENTARI_FOURTEENTH
    pays.insert(6, Pay(_run(6, "fourteenth"), fourteenth, fourteenth))
    pays.append(Pay(_run(12, "thirteenth"), _ALIMENTARI, _ALIMENTARI))
    return tuple(pays)


def _alimentari_june() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _ALIMENTARI, _ALIMENTARI) for m in range(1, 6)]
    #: Six twelfths of the tredicesima are paid with the last month.
    rateo = _twelfths((*_ALIMENTARI_ITEMS, _ALIMENTARI_EDR), 6)
    june = _ALIMENTARI + rateo
    fourteenth = _ALIMENTARI_FOURTEENTH
    return (
        *pays,
        Pay(_run(6), june, june),
        Pay(_run(6, "fourteenth"), fourteenth, fourteenth),
    )


ALIMENTARI_YEAR = sector_year(
    _alimentari_year(), _INDUSTRIA, _FULL_YEAR, terminated=False
)
ALIMENTARI_JUNE = sector_year(
    _alimentari_june(), _INDUSTRIA, _HALF_YEAR, terminated=True
)


# DMO: Distribuzione Moderna Organizzata IV, 50 employees.

#: Level IV, paga base and contingenza + EDR: Testo Unico of 29 September
#: 2025, Allegato 11, PDF p. 98 (sha256
#: 9bb56adb31c2f6aa2c65c48dbe60774701367658177dd544391ccf2da70fbbaf):
#: "IV € 1257,46 - € 524,22 € 1781,68" from 1 November 2025, "IV € 1292,46
#: - € 524,22 € 1816,68" from 1 November 2026.  The terzo elemento
#: nazionale is not paid: a provincial element is in force (Art. 195).
_DMO_UNTIL_OCTOBER = Decimal("1257.46") + Decimal("524.22")
_DMO_FROM_NOVEMBER = Decimal("1292.46") + Decimal("524.22")
#: Quattordicesima of the pay "in atto al 30 giugno", paid on 1 July, in
#: twelfths of the twelve months before (Art. 205, PDF p. 59): six for a
#: hire on 1 January; tredicesima of one monthly pay (Art. 204).
_DMO_FOURTEENTH = _cents(_DMO_UNTIL_OCTOBER * 6 / 12)


def _dmo(month: int) -> Decimal:
    return _DMO_UNTIL_OCTOBER if month < 11 else _DMO_FROM_NOVEMBER


def _dmo_year() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _dmo(m), _dmo(m)) for m in range(1, 13)]
    pays.insert(6, Pay(_run(6, "fourteenth"), _DMO_FOURTEENTH, _DMO_FOURTEENTH))
    pays.insert(12, Pay(_run(12, "thirteenth"), _DMO_FROM_NOVEMBER, _DMO_FROM_NOVEMBER))
    return tuple(pays)


def _dmo_june() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _dmo(m), _dmo(m)) for m in range(1, 6)]
    #: Six twelfths of the tredicesima are paid with the last month.
    june = _DMO_UNTIL_OCTOBER + _cents(_DMO_UNTIL_OCTOBER * 6 / 12)
    return (
        *pays,
        Pay(_run(6), june, june),
        Pay(_run(6, "fourteenth"), _DMO_FOURTEENTH, _DMO_FOURTEENTH),
    )


DMO_YEAR = sector_year(_dmo_year(), _TERZIARIO, _FULL_YEAR, terminated=False)
DMO_JUNE = sector_year(_dmo_june(), _TERZIARIO, _HALF_YEAR, terminated=True)


# Commercio: Terziario Distribuzione e Servizi Confcommercio, 4th level.

#: 4th level, paga base and contingenza, as the table lists them apart:
#: accordo integrativo 28 March 2024, PDF p. 65 (sha256
#: 980356a766c5fad7450dd234052a9f311a2b66d732cb72b6632b354ffaf18001):
#: "IV 1257,46 524,22 1781,68" from 1 November 2025, "IV 1292,46 524,22
#: 1816,68" from 1 November 2026.  The terzo elemento nazionale (Art. 215)
#: is not paid: a provincial element is in force.
_COMMERCIO_CONTINGENZA = Decimal("524.22")
_COMMERCIO_UNTIL_OCTOBER = (Decimal("1257.46"), _COMMERCIO_CONTINGENZA)
_COMMERCIO_FROM_NOVEMBER = (Decimal("1292.46"), _COMMERCIO_CONTINGENZA)
#: Quattordicesima of one month of the retribuzione "in atto al 30 giugno",
#: paid on 1 July, in twelfths of the months from July to June: six for a
#: hire on 1 January (Testo Unico 30 July 2019, Art. 221, PDF p. 201,
#: sha256 76420e3a21e002e2cb37b71db515356ee260a239c7cf38e7df94f68b8f730016);
#: tredicesima of one month at Christmas (Art. 220, p. 200).
_COMMERCIO_FOURTEENTH = _twelfths(_COMMERCIO_UNTIL_OCTOBER, 6)


def _commercio(month: int) -> Decimal:
    items = _COMMERCIO_UNTIL_OCTOBER if month < 11 else _COMMERCIO_FROM_NOVEMBER
    return sum(items, _ZERO)


def _commercio_year() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _commercio(m), _commercio(m)) for m in range(1, 13)]
    fourteenth = _COMMERCIO_FOURTEENTH
    pays.insert(6, Pay(_run(6, "fourteenth"), fourteenth, fourteenth))
    pays.insert(12, Pay(_run(12, "thirteenth"), _commercio(12), _commercio(12)))
    return tuple(pays)


def _commercio_june() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _commercio(m), _commercio(m)) for m in range(1, 6)]
    #: Six twelfths of the tredicesima are paid with the last month.
    june = _commercio(6) + _twelfths(_COMMERCIO_UNTIL_OCTOBER, 6)
    fourteenth = _COMMERCIO_FOURTEENTH
    return (
        *pays,
        Pay(_run(6), june, june),
        Pay(_run(6, "fourteenth"), fourteenth, fourteenth),
    )


COMMERCIO_YEAR = sector_year(
    _commercio_year(), _TERZIARIO, _FULL_YEAR, terminated=False
)
COMMERCIO_JUNE = sector_year(_commercio_june(), _TERZIARIO, _HALF_YEAR, terminated=True)


# Pubblici Esercizi and Ristorazione Collettiva: 4th level, 10 employees.

#: 4th level contingenza and paga base: accordo integrativo of 26 June
#: 2024, pp. 1-3 (sha256
#: 0e6cb39be926cbf8f461e01a2a841e7141c2d0350b5714feb96176821aedc922): "4
#: 524,94 € 1.127,75 € 1.652,69 €" from June 2025 and "4 524,94 € 1.167,75
#: € 1.692,69 €" from June 2026; the ristorazione collettiva tables move
#: the same amounts to September 2025 and September 2026 (p. 3).
_FIPE_OLD = Decimal("524.94") + Decimal("1127.75")
_FIPE_NEW = Decimal("524.94") + Decimal("1167.75")
#: Terziario from 6 to 15 employees (INPS circ. 117/2022 all. 1, as for
#: the turismo above) and the additional sickness contribution of the
#: pubblici esercizi, "pari allo 0,77% della retribuzione imponibile"
#: (INPS msg. 2382/2024; D.M. 1 February 1957), charged apart.
_FIPE_RATES = Rates(
    employee_ivs=Decimal("0.0919"),
    employee_other=Decimal("0.0026667"),
    employer_ivs=Decimal("0.2381"),
    employer_other=Decimal("0.0570333"),
    employer_supplement=Decimal("0.0077"),
)
#: Quattordicesima of the pay "in atto al 30 giugno", paid with the July
#: pay, in ratei of the twelve months before 1 July (CCNL 8 February 2018,
#: art. 184, p. 128): six for a hire on 1 January; tredicesima of one
#: monthly pay at Christmas (art. 183).


def _fipe(month: int, tranche: int) -> Decimal:
    return _FIPE_OLD if month < tranche else _FIPE_NEW


def _fipe_year(tranche: int) -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _fipe(m, tranche), _fipe(m, tranche)) for m in range(1, 13)]
    fourteenth = _cents(_fipe(6, tranche) * 6 / 12)
    pays.insert(6, Pay(_run(6, "fourteenth"), fourteenth, fourteenth))
    pays.append(Pay(_run(12, "thirteenth"), _FIPE_NEW, _FIPE_NEW))
    return tuple(pays)


def _fipe_june(tranche: int) -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _fipe(m, tranche), _fipe(m, tranche)) for m in range(1, 6)]
    last = _fipe(6, tranche)
    #: Six twelfths of the tredicesima are paid with the last month.
    june = last + _cents(last * 6 / 12)
    fourteenth = _cents(last * 6 / 12)
    return (
        *pays,
        Pay(_run(6), june, june),
        Pay(_run(6, "fourteenth"), fourteenth, fourteenth),
    )


FIPE_YEAR = sector_year(_fipe_year(6), _FIPE_RATES, _FULL_YEAR, terminated=False)
FIPE_JUNE = sector_year(_fipe_june(6), _FIPE_RATES, _HALF_YEAR, terminated=True)
RISTORAZIONE_YEAR = sector_year(
    _fipe_year(9), _FIPE_RATES, _FULL_YEAR, terminated=False
)
RISTORAZIONE_JUNE = sector_year(_fipe_june(9), _FIPE_RATES, _HALF_YEAR, terminated=True)


# Confapi: Metalmeccanico Unionmeccanica Confapi 5th level, 50 employees.

#: 5th level minimo: accordo of 24 July 2025, p. 1 (sha256
#: 4ec057a5c4a209b5b52d9d582822c5df0e7229475ac74b2602d3a94a436cfc4c, a
#: scan read by OCR): "€ 2.145,87 | €27,90 | €2.173,77 | €22,10 |
#: €2.195,87 | €50,00 | € 2.245,87", 2,195.87 from 1 September 2025 and
#: 2,245.87 from 1 June 2026, confirmed by the verbale of 17 June 2026, p. 1
#: (sha256 61857a25fcb618e5df4353ee564a718c7b549919b37bf60734a722c2a69756f5):
#: "5 € 50,00 € 2.245,87".
_CONFAPI_UNTIL_MAY = Decimal("2195.87")
_CONFAPI_FROM_JUNE = Decimal("2245.87")


def _confapi(month: int) -> Decimal:
    return _CONFAPI_UNTIL_MAY if month < 6 else _CONFAPI_FROM_JUNE


def _confapi_year() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _confapi(m), _confapi(m)) for m in range(1, 13)]
    #: Tredicesima of one monthly pay at Christmas: CCNL 3 July 2017, art.
    #: 42, p. 119 (thirteen payments).
    thirteenth = _CONFAPI_FROM_JUNE
    return (*pays, Pay(_run(12, "thirteenth"), thirteenth, thirteenth))


def _confapi_june() -> tuple[Pay, ...]:
    pays = [Pay(_run(m), _confapi(m), _confapi(m)) for m in range(1, 6)]
    #: Six twelfths of the tredicesima are paid with the last month.
    june = _CONFAPI_FROM_JUNE + _cents(_CONFAPI_FROM_JUNE * 6 / 12)
    return (*pays, Pay(_run(6), june, june))


CONFAPI_YEAR = sector_year(
    _confapi_year(), _INDUSTRIA, _FULL_YEAR, terminated=False, health=EBM_SALUTE
)
CONFAPI_JUNE = sector_year(
    _confapi_june(), _INDUSTRIA, _HALF_YEAR, terminated=True, health=EBM_SALUTE
)


# Edilizia impiegati: ANCE impiegato of the 3rd level, 30 employees.

#: Minimo di stipendio of the 3rd level: ANCE, nuovi minimi of the CCNL 21
#: February 2025, p. 1 (sha256
#: d01c1635bf8f5185043f6c5509f0c829fb58bdb1d9ef2943f554d825f60d1710): "III
#: 1.387,56 1.452,56 1.517,56" from 1 February 2025, 1 March 2026 and 1
#: March 2027.  Contingenza 519,16 and EDR 10,33 of the impiegati of the
#: 3rd level: ANCE Centro Nord Sardegna, tabella n. 2/2025 impiegati,
#: provincia di Sassari, p. 1 (sha256
#: b681a3f867cd31d4cef09e5234d85a2b6f183a72c66054ed6ff8bd326d88f715).  The
#: EDR bears on no other institute: outside the TFR base, in the extra
#: months too.
_IMP_ITEMS = {"minimo": Decimal("1387.56"), "contingenza": Decimal("519.16")}
_IMP_FROM_MARCH = Decimal("1452.56")
_IMP_EDR = Decimal("10.33")
#: Prevedi contributo contrattuale of an impiegato of the 3rd level, 13,00
#: EUR a month, "applicato anche per 13° e 14° mensilità" in proportion to
#: their ratei (Prevedi nota informativa, sha256
#: 195f6e83abef137bc3ad9ad832af61b633e1c923f202623d6bc16fdef2900de6; CNCE
#: vademecum, Comunicazione 559), with the 10% solidarity contribution of
#: the employer (L. 166/1991 art. 9-bis).
_IMP_PREVEDI = Decimal("13.00")


def _imp_items(month: int) -> tuple[Decimal, ...]:
    minimo = _IMP_ITEMS["minimo"] if month < 3 else _IMP_FROM_MARCH
    return (minimo, _IMP_ITEMS["contingenza"])


def _imp_pay(run_id: str, months: int, month: int, *, extra: bool = False) -> Pay:
    """Return twelfths of the pay of ``month``, each item to cents.

    Returns:
        ``months`` twelfths of the pay, with the EDR outside the TFR base
        and the Prevedi amount of the same twelfths.
    """
    items = _imp_items(month)
    pay = sum((_cents(i * months / 12) for i in items), _ZERO)
    edr = _cents(_IMP_EDR * months / 12)
    fund = _cents(_IMP_PREVEDI * months / 12) if extra else _IMP_PREVEDI
    return Pay(run_id, pay + edr, pay, fund=fund, solidarity=_cents(fund / 10))


def _imp_year() -> tuple[Pay, ...]:
    pays = [_imp_pay(_run(m), 12, m) for m in range(1, 13)]
    #: Premio annuo (quattordicesima) of the service from 1 July to 30
    #: June, paid at the end of June: six twelfths for a hire on 1 January
    #: (CCNL 19 April 2010, art. 64); tredicesima of one monthly pay at
    #: Christmas (art. 63), paid before the December pay.
    pays.insert(6, _imp_pay(_run(6, "fourteenth"), 6, 6, extra=True))
    pays.insert(12, _imp_pay(_run(12, "thirteenth"), 12, 12, extra=True))
    return tuple(pays)


def _imp_june() -> tuple[Pay, ...]:
    pays = [_imp_pay(_run(m), 12, m) for m in range(1, 6)]
    month = _imp_pay(_run(6), 12, 6)
    #: Six twelfths of the tredicesima are paid with the last month, with
    #: their Prevedi amount.
    ratei = _imp_pay(_run(6), 6, 6, extra=True)
    june = Pay(
        month.run_id,
        month.gross + ratei.gross,
        month.tfr_base + ratei.tfr_base,
        fund=month.fund + ratei.fund,
        solidarity=_cents((month.fund + ratei.fund) / 10),
    )
    return (*pays, june, _imp_pay(_run(6, "fourteenth"), 6, 6, extra=True))


#: Edilizia impiegato from 16 to 50 employees: the shares of the industria
#: impiegato above, read on the same Assimpredil ANCE table 2/2026.
EDILIZIA_IMPIEGATI_YEAR = sector_year(
    _imp_year(), _INDUSTRIA, _FULL_YEAR, terminated=False
)
EDILIZIA_IMPIEGATI_JUNE = sector_year(
    _imp_june(), _INDUSTRIA, _HALF_YEAR, terminated=True
)


# Edilizia: ANCE operaio of the 1st level, 173 hours.

#: Minimo of the 1st level: ANCE, nuovi minimi of the CCNL 21 February 2025,
#: p. 1 (sha256 d01c1635bf8f5185043f6c5509f0c829fb58bdb1d9ef2943f554d825f60d1710):
#: "I 1.067,36 1.117,36 1.167,36" from 1 February 2025, 1 March 2026 and
#: 1 March 2027.
_OPERAIO_UNTIL_FEBRUARY = Decimal("1067.36")
_OPERAIO_FROM_MARCH = Decimal("1117.36")
#: Contingenza 512,87 and EDR 10,33 of the 1st level: ANCE Centro Nord
#: Sardegna, tabella retributiva, provincia di Sassari, p. 1 (sha256
#: b681a3f867cd31d4cef09e5234d85a2b6f183a72c66054ed6ff8bd326d88f715).
_CONTINGENZA = Decimal("512.87")
_EDR = Decimal("10.33")
#: Riposi annui 4.95% (CCNL 19 April 2010, p. 27) and the Cassa Edile
#: accrual for ferie and gratifica natalizia 18.5% (p. 37), on minimo and
#: contingenza (sha256
#: ddd11bb850de2e7c642eb662b59e40e36c66e3a534162c505aa1c9a94ac5a00b); the
#: accrual is "accantonat[o] al netto delle ritenute di legge secondo il
#: criterio" of Allegato D (p. 38), the net rate of Allegato D point 2 (p.
#: 172), which the ANCE Ragusa table of 1 March 2026 prints as "pari al
#: 14,20%".
_RIPOSI = Decimal("0.0495")
_CASSA = Decimal("0.185")
_CASSA_NET = Decimal("0.142")
#: Prevedi contributo contrattuale of an operaio comune: 0,0685 EUR an hour
#: worked, rounded to the euro (Prevedi nota informativa, sha256
#: 195f6e83abef137bc3ad9ad832af61b633e1c923f202623d6bc16fdef2900de6), and the
#: 10% solidarity contribution of the employer (L. 166/1991 art. 9-bis).
_HOURS = Decimal(173)
_PREVEDI = _whole_euro(_HOURS * Decimal("0.0685"))
_SOLIDARITY = _cents(_PREVEDI / 10)
#: Edilizia operaio, 16 to 50 employees: Assimpredil ANCE table 1/2026
#: (sha256 83508e4e61d305be578ecb224a00bdf4f7628214578999a02d4763d93f58756f):
#: employer 34.28, of which IVS 23.81; worker IVS 9.19 and CIGS 0.30.
_EDILIZIA = Rates(
    employee_ivs=Decimal("0.0919"),
    employee_other=Decimal("0.0030"),
    employer_ivs=Decimal("0.2381"),
    employer_other=Decimal("0.1047"),
)


def _operaio(month: int) -> Pay:
    minimo = _OPERAIO_UNTIL_FEBRUARY if month < 3 else _OPERAIO_FROM_MARCH
    base = minimo + _CONTINGENZA
    gross = base + _EDR + _cents(base * _RIPOSI) + _cents(base * _CASSA)
    #: The EDR of the Protocollo of 31 July 1992 bears on no other
    #: institute: outside the TFR base.
    return Pay(
        _run(month),
        gross,
        gross - _EDR,
        fund=_PREVEDI,
        solidarity=_SOLIDARITY,
        cassa_net=_cents(base * _CASSA_NET),
    )


EDILIZIA_YEAR = sector_year(
    tuple(_operaio(m) for m in range(1, 13)), _EDILIZIA, _FULL_YEAR, terminated=False
)
EDILIZIA_JUNE = sector_year(
    tuple(_operaio(m) for m in range(1, 7)), _EDILIZIA, _HALF_YEAR, terminated=True
)
