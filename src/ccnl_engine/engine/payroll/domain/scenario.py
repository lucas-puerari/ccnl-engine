"""PayrollScenario and its constituent domain types.

The two root entities:

- :class:`Employee` — who the worker is: classification level, seniority,
  working hours, fiscal residency, individual salary agreements.
- :class:`Employment` — the employment relationship: which CCNL applies,
  what contract type, who the employer is, and the reference date.

These compose into :class:`PayrollScenario`, the single argument to
:func:`~ccnl_engine.engine.payroll.service.orchestrator.compute`.

Helper sub-objects:

- :class:`Jurisdiction` — region and municipality codes for surtax.
- :class:`Agreement` — individual RAL override or ad-personam supplement.
- :class:`Employer` — employer headcount and second-level allowances.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.engine.contract.domain.ccnl import (
    LevelCategory,
    SupplementaryAllowance,
)
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.employee import (
    DestinationRalOverride,
    RalOverride,
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.family import FamilyComposition
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WelfareInput,
)

_ZERO: Decimal = Decimal(0)
_ONE: Decimal = Decimal(1)


@dataclass(frozen=True)
class Jurisdiction:
    """Fiscal residency of the worker.

    Used to compute addizionale regionale and addizionale comunale IRPEF.
    Both fields are optional: when both are ``None``, no surtax is loaded.

    Attributes:
        regione: Italian region name (e.g. ``"Lombardia"``).
        comune_belfiore: Belfiore (codice catastale) of the worker's
            municipality of residence (e.g. ``"F205"`` for Milan).
    """

    regione: str | None = None
    comune_belfiore: str | None = None


@dataclass(frozen=True)
class Agreement:
    """Individual salary terms that override the CCNL tables.

    Attributes:
        ral_override: When set, replaces the CCNL-derived gross annual
            salary. Use :class:`~ccnl_engine.engine.payroll.domain.employee\
.RalOverride` for any employment type, or
            :class:`~ccnl_engine.engine.payroll.domain.employee\
.DestinationRalOverride` for a percentage-track apprentice.
        ad_personam_monthly: Individual frozen monthly supplement added
            directly to gross (e.g. a pre-abolition seniority increment).
            Not scaled by ``part_time_pct``. Must be ``>= 0``.
    """

    ral_override: RalOverride | DestinationRalOverride | None = None
    ad_personam_monthly: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that ad_personam_monthly is non-negative.

        Raises:
            ValueError: If ad_personam_monthly is negative.
        """
        if self.ad_personam_monthly < _ZERO:
            msg = f"ad_personam_monthly must be >= 0, got {self.ad_personam_monthly}"
            raise ValueError(msg)


@dataclass(frozen=True)
class Employee:
    """Worker-side inputs for payroll computation.

    Encodes who the worker is: their CCNL classification level, seniority,
    working-time arrangement, fiscal residency, and any individually agreed
    salary terms.

    Attributes:
        level_code: Classification level code as defined in the CCNL
            (e.g. ``"D3"``). Must match a level in the applied CCNL.
        seniority: Seniority expressed as an explicit increment count
            (:class:`~ccnl_engine.engine.payroll.domain.employee\
.SeniorityByCount`), as months of service
            (:class:`~ccnl_engine.engine.payroll.domain.employee\
.SeniorityByMonths`), or as a hire date
            (:class:`~ccnl_engine.engine.payroll.domain.employee\
.SeniorityByDate`). ``None`` means no increment applies.
        part_time_pct: Part-time coefficient in the range ``(0, 1]``.
            Full-time workers use the default ``1``.
        weekly_hours: Contractual weekly hours. Required when the tax-rules
            file uses ``domestic_contributions`` (lavoro domestico).
            Must be ``> 0`` when provided.
        category: Worker category override (``"operaio"``, ``"impiegato"``,
            etc.). Required when a level hosts multiple categories.
            Defaults to the level's own category when ``None``.
        roles: Set of role identifiers the worker holds (e.g.
            ``{"capoturno"}``). Selects role-restricted allowances.
        ivs_ceiling_applies: Set to ``True`` when the worker's gross is
            above the INPS IVS ceiling and only the IVS-specific
            contribution rate should apply.
        jurisdiction: Fiscal residency for addizionale regionale/comunale
            computation. ``None`` means no surtax is computed.
        agreement: Individual salary terms overriding the CCNL tables.
            ``None`` means the CCNL tables are used unchanged.
    """

    level_code: str
    seniority: SeniorityByCount | SeniorityByMonths | SeniorityByDate | None = None
    part_time_pct: Decimal = _ONE
    weekly_hours: Decimal | None = None
    category: LevelCategory | None = None
    roles: frozenset[str] = frozenset()
    ivs_ceiling_applies: bool = False
    jurisdiction: Jurisdiction | None = None
    agreement: Agreement | None = None

    def __post_init__(self) -> None:
        """Validate part_time_pct and weekly_hours ranges.

        Raises:
            ValueError: If part_time_pct is not in (0, 1] or weekly_hours <= 0.
        """
        if not (_ZERO < self.part_time_pct <= _ONE):
            msg = f"part_time_pct must be in (0, 1], got {self.part_time_pct}"
            raise ValueError(msg)
        if self.weekly_hours is not None and self.weekly_hours <= _ZERO:
            msg = f"weekly_hours must be > 0, got {self.weekly_hours}"
            raise ValueError(msg)

    @property
    def seniority_count(self) -> int | None:
        """Explicit increment count, or ``None`` when expressed as months."""
        return (
            self.seniority.value
            if isinstance(self.seniority, SeniorityByCount)
            else None
        )

    @property
    def seniority_months(self) -> int | None:
        """Service months elapsed, or ``None`` when expressed as a count or date.

        For date-based seniority, use :meth:`seniority_months_as_of` instead.
        """
        return (
            self.seniority.value
            if isinstance(self.seniority, SeniorityByMonths)
            else None
        )

    def seniority_months_as_of(self, as_of: date) -> int | None:
        """Return service months elapsed at *as_of*, resolving all variants.

        - :class:`~ccnl_engine.engine.payroll.domain.employee.SeniorityByMonths`:
          returns the stored months value directly.
        - :class:`~ccnl_engine.engine.payroll.domain.employee.SeniorityByDate`:
          computes the calendar-month gap between the hire date and *as_of*.
        - :class:`~ccnl_engine.engine.payroll.domain.employee.SeniorityByCount`
          or ``None``: returns ``None`` (months not applicable).

        Args:
            as_of: The reference date, typically
                :attr:`~ccnl_engine.engine.payroll.domain.scenario\
.Employment.calculation_date`.

        Returns:
            Months of service, or ``None`` when seniority is expressed as
            a count or not provided.
        """
        if isinstance(self.seniority, SeniorityByMonths):
            return self.seniority.value
        if isinstance(self.seniority, SeniorityByDate):
            hire = self.seniority.value
            return (as_of.year - hire.year) * 12 + (as_of.month - hire.month)
        return None


@dataclass(frozen=True)
class Employer:
    """Employer-side inputs for payroll computation.

    Attributes:
        num_employees: Employer headcount. Required — used to select the
            INPS contribution tier. Must be ``>= 1``.
        second_level_allowances: Allowances from a territorial or company
            second-level agreement (*contrattazione di secondo livello*).
            Each item is scaled by ``part_time_pct``; whether the
            apprenticeship percentage also applies is controlled per-item
            by ``apprenticeship_pct_relevant``. Mutually exclusive with
            :attr:`Agreement.ral_override`.
    """

    num_employees: int
    second_level_allowances: tuple[SupplementaryAllowance, ...] = ()

    def __post_init__(self) -> None:
        """Validate that num_employees is at least 1.

        Raises:
            ValueError: If num_employees is less than 1.
        """
        if self.num_employees < 1:
            msg = f"num_employees must be >= 1, got {self.num_employees}"
            raise ValueError(msg)


@dataclass(frozen=True)
class Employment:
    """The employment relationship.

    Ties together which CCNL applies, the contract type, the employer
    (with headcount), and the reference date for all time-series lookups.

    Attributes:
        ccnl: Bundled CCNL filename (e.g.
            ``"metalmeccanico-federmeccanica.json"``).
        contract: Contract type — :class:`~ccnl_engine.engine.payroll\
.domain.employment.Permanent`,
            :class:`~ccnl_engine.engine.payroll.domain.employment.FixedTerm`,
            or :class:`~ccnl_engine.engine.payroll.domain.employment\
.Apprentice`.
        employer: Employer-side inputs including headcount.
        calculation_date: Reference date for all time-series lookups (base pay,
            seniority amounts, allowances, additional months). Also the
            upper bound for deriving months of service when seniority is
            expressed as a :class:`~ccnl_engine.engine.payroll.domain\
.employee.SeniorityByDate`.
        tax_year: Override the fiscal year used for tax/INPS rule loading.
            When ``None`` (default), ``calculation_date.year`` is used.
            Set explicitly when applying a specific year's tax rules to a
            date in a different calendar year (e.g. computing a late-2025
            payslip with 2026 tax rules already in force).
    """

    ccnl: str
    contract: Permanent | FixedTerm | Apprentice
    employer: Employer
    calculation_date: date
    tax_year: int | None = None


@dataclass(frozen=True)
class PayrollScenario:
    """A complete payroll computation scenario.

    Composes the worker (:class:`Employee`) and the employment relationship
    (:class:`Employment`) into a single object. Pass it to
    :func:`~ccnl_engine.engine.payroll.service.orchestrator.compute`::

        from datetime import date
        from decimal import Decimal

        result = compute(PayrollScenario(
            employee=Employee(level_code="C2"),
            employment=Employment(
                ccnl="metalmeccanico-federmeccanica.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                calculation_date=date(2026, 1, 1),
            ),
        ))

    Attributes:
        employee: Worker-side inputs.
        employment: Employment relationship inputs.
        time_supplements: Optional Layer 3 supplement hours for the pay
            period (overtime, night, holiday). ``None`` when not requested.
        absence_days: Optional Layer 3 absence data for the pay period
            (unpaid days absent). ``None`` when not requested.
        leave_input: Optional Layer 3 leave data for the pay period
            (ferie / permessi taken). ``None`` when not requested.
        sick_input: Optional Layer 3 sick leave data for the pay period
            (malattia ordinaria). ``None`` when not requested.
        fringe_benefit_input: Optional fringe-benefit data for the fiscal
            year (Art. 51 c. 3 TUIR). ``None`` when not requested.
        welfare_input: Optional welfare data for the fiscal year
            (Art. 51 c. 2 TUIR). ``None`` when not requested.
        bonus_input: Optional bonus / PdR data for the fiscal year.
            ``None`` when not requested.
        family: Optional family composition for Art. 12 TUIR deductions.
            When provided, the engine computes family deductions and subtracts
            them from ``irpef_net`` (reducing ``net_annual``).  ``None`` means
            no family deductions are applied and
            ``FiscalSimplification.NO_DETRAZIONI_FAMILIARI`` is reported.
        art15_deductions: Optional Art. 15 TUIR oneri detraibili declared by
            the worker.  When provided, the engine computes the tax credit
            (19 % on eligible expenditure up to the statutory ceiling) and
            subtracts it from ``irpef_net`` (reducing ``net_annual``).
            ``None`` means no Art. 15 deductions are applied and
            ``FiscalSimplification.NO_DETRAZIONI_ART15`` is reported.
            Art. 1 c. 3-4 L. 199/2025 sterilizzazione does NOT apply to
            Art. 15 (it targets only Art. 12 + Art. 13 TUIR).
    """

    employee: Employee
    employment: Employment
    time_supplements: OvertimeHours | None = None
    absence_days: AbsenceDays | None = None
    leave_input: LeaveInput | None = None
    sick_input: SickInput | None = None
    fringe_benefit_input: FringeBenefitInput | None = None
    welfare_input: WelfareInput | None = None
    bonus_input: BonusInput | None = None
    family: FamilyComposition | None = None
    art15_deductions: Art15Deductions | None = None
