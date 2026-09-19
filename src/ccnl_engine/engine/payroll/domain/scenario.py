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

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.ccnl import (
    LevelCategory,
    SupplementaryAllowance,
)
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.bilateral_funds import BilateralFundInput
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
from ccnl_engine.engine.primitives.domain.primitives import StrictDecimal

_ZERO: Decimal = Decimal(0)
_ONE: Decimal = Decimal(1)


class Jurisdiction(BaseModel):
    """Fiscal residency of the worker.

    Used to compute addizionale regionale and addizionale comunale IRPEF.
    Both fields are optional: when both are ``None``, no surtax is loaded.

    Attributes:
        regione: Italian region name (e.g. ``"Lombardia"``).
        comune_belfiore: Codice catastale of the worker's municipality of
            residence (e.g. ``"F205"`` for Milan).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    regione: str | None = None
    comune_belfiore: str | None = None


class Agreement(BaseModel):
    """Individual salary terms that override the CCNL tables.

    Attributes:
        ral_override: When set, replaces the CCNL-derived gross annual
            salary. Use :class:`~ccnl_engine.engine.payroll.domain.employee\
.RalOverride` for any employment type, or
            :class:`~ccnl_engine.engine.payroll.domain.employee\
.DestinationRalOverride` for a percentage-track apprentice.
        ad_personam_monthly: Individual frozen monthly supplement added
            directly to gross (e.g. a pre-abolition seniority increment).
            Not scaled by ``part_time_ratio``. Must be ``>= 0``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ral_override: (
        Annotated[
            RalOverride | DestinationRalOverride,
            Field(discriminator="type"),
        ]
        | None
    ) = None
    ad_personam_monthly: StrictDecimal = _ZERO

    @model_validator(mode="after")
    def _check_non_negative(self) -> Agreement:
        if self.ad_personam_monthly < _ZERO:
            msg = f"ad_personam_monthly must be >= 0, got {self.ad_personam_monthly}"
            raise ValueError(msg)
        return self


class Employee(BaseModel):
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
        part_time_ratio: Part-time coefficient in the range ``(0, 1]``.
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

    model_config = ConfigDict(frozen=True, extra="forbid")

    level_code: str
    seniority: (
        Annotated[
            SeniorityByCount | SeniorityByMonths | SeniorityByDate,
            Field(discriminator="type"),
        ]
        | None
    ) = None
    part_time_ratio: StrictDecimal = _ONE
    weekly_hours: StrictDecimal | None = None
    category: LevelCategory | None = None
    roles: frozenset[str] = frozenset()
    ivs_ceiling_applies: bool = False
    jurisdiction: Jurisdiction | None = None
    agreement: Agreement | None = None

    @model_validator(mode="after")
    def _check_ranges(self) -> Employee:
        if not (_ZERO < self.part_time_ratio <= _ONE):
            msg = f"part_time_ratio must be in (0, 1], got {self.part_time_ratio}"
            raise ValueError(msg)
        if self.weekly_hours is not None and self.weekly_hours <= _ZERO:
            msg = f"weekly_hours must be > 0, got {self.weekly_hours}"
            raise ValueError(msg)
        return self

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
.Employment.as_of`.

        Returns:
            Months of service, or ``None`` when seniority is expressed as
            a count or not provided.

        Raises:
            ValueError: If hire_date is after *as_of* (future employee).
        """
        if isinstance(self.seniority, SeniorityByMonths):
            return self.seniority.value
        if isinstance(self.seniority, SeniorityByDate):
            hire = self.seniority.value
            if hire > as_of:
                msg = (
                    f"hire_date {hire} is after as_of {as_of}: "
                    "cannot compute seniority for a future employee"
                )
                raise ValueError(msg)
            return (as_of.year - hire.year) * 12 + (as_of.month - hire.month)
        return None


class Employer(BaseModel):
    """Employer-side inputs for payroll computation.

    Attributes:
        num_employees: Employer headcount. Required — used to select the
            INPS contribution tier. Must be ``>= 1``.
        second_level_allowances: Allowances from a territorial or company
            second-level agreement (*contrattazione di secondo livello*).
            Each item is scaled by ``part_time_ratio``; whether the
            apprenticeship percentage also applies is controlled per-item
            by ``apprenticeship_pct_relevant``. Mutually exclusive with
            :attr:`Agreement.ral_override`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    num_employees: int = Field(ge=1)
    second_level_allowances: tuple[SupplementaryAllowance, ...] = ()


class Employment(BaseModel):
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
        as_of: Reference date for all time-series lookups (base pay,
            seniority amounts, allowances, additional months). Also the
            upper bound for deriving months of service when seniority is
            expressed as a :class:`~ccnl_engine.engine.payroll.domain\
.employee.SeniorityByDate`.
        tax_year: Override the fiscal year used for tax/INPS rule loading.
            When ``None`` (default), ``as_of.year`` is used.
            Set explicitly when applying a specific year's tax rules to a
            date in a different calendar year (e.g. computing a late-2025
            payslip with 2026 tax rules already in force).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ccnl: str
    contract: Annotated[
        Permanent | FixedTerm | Apprentice,
        Field(discriminator="type"),
    ]
    employer: Employer
    as_of: date
    tax_year: int | None = None


class PayrollScenario(BaseModel):
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
                as_of=date(2026, 1, 1),
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
            When provided, the engine computes family deductions and
            subtracts them from ``irpef_net`` (reducing ``net_annual``).
            ``None`` means no family deductions are applied and
            ``FiscalSimplification.NO_DETRAZIONI_FAMILIARI`` is reported.
        art15_deductions: Optional Art. 15 TUIR oneri detraibili declared
            by the worker.  When provided, the engine computes the tax
            credit (19 % on eligible expenditure up to the statutory
            ceiling) and subtracts it from ``irpef_net`` (reducing
            ``net_annual``).  ``None`` means no mortgage deductions are
            applied and
            ``FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE`` is
            reported.
            ``FiscalSimplification.PARTIAL_DETRAZIONI_ART15`` is always
            reported: only mortgage interest is modelled.
            Art. 1 c. 3-4 L. 199/2025 sterilizzazione applies to Art. 15
            TUIR oneri detraibili al 19 % (lett. a, b, d, e; not lett. c
            spese sanitarie): for reddito complessivo > EUR 200 000 the
            credit is reduced by EUR 440. The resulting clawback is
            reported in
            ``PayrollResult.sterilizzazione_clawback_annual``.
        bilateral_funds: Scenario-level bilateral fund contributions (fondi
            bilaterali). Each entry is either a fixed monthly amount
            (:class:`~ccnl_engine.engine.payroll.domain.bilateral_funds\
.FlatMonthlyFund`) or a rate applied to an annual base
            (:class:`~ccnl_engine.engine.payroll.domain.bilateral_funds\
.RateFund`). The employee portion reduces ``net_annual``; the employer
            portion enters ``employer_cost_annual``. Both reductions are
            post-tax only — the engine does not model any pre-tax
            deductibility of the employee contribution.
            ``FiscalSimplification.NO_BILATERAL_FUNDS`` is reported when
            the tuple is empty.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

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
    bilateral_funds: tuple[BilateralFundInput, ...] = ()


class PayPeriod(BaseModel):
    """Period-specific payroll events for a single pay period.

    Passed to :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects` alongside an :class:`AnnualPayrollScenario` to supply
    the month's variable events (overtime, absences, sick leave, benefits).

    All fields are optional — a ``PayPeriod()`` with no arguments represents
    a standard month with no special events.

    Attributes:
        time_supplements: Overtime, night, and holiday hours for the period.
            ``None`` means no supplement computation.
        absence_days: Unpaid absence days in the period. ``None`` means none.
        leave_input: Ferie/permessi days taken in the period. ``None`` means
            no leave tracking.
        sick_input: Sick-leave days in the period. ``None`` means no sickness.
        fringe_benefit_input: Annual fringe-benefit amount (Art. 51 c. 3
            TUIR). Reported per-period but compared against the annual
            threshold. ``None`` means no fringe computation.
        welfare_input: Annual welfare amount (Art. 51 c. 2 TUIR). ``None``
            means no welfare.
        bonus_input: Annual bonus / PdR data. ``None`` means no bonus.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    time_supplements: OvertimeHours | None = None
    absence_days: AbsenceDays | None = None
    leave_input: LeaveInput | None = None
    sick_input: SickInput | None = None
    fringe_benefit_input: FringeBenefitInput | None = None
    welfare_input: WelfareInput | None = None
    bonus_input: BonusInput | None = None


class AnnualPayrollScenario(BaseModel):
    """Structural payroll scenario without period-specific events.

    Use :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_annual` to compute annual gross-to-net figures, or
    :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects` together with a :class:`PayPeriod` to include
    the month's variable events in the result fields.

    Compared to the legacy :class:`PayrollScenario`, this class holds only
    the structural fields that describe *who the worker is* and *what the
    employment relationship is*.  Period-specific events (overtime, absences,
    sick leave, fringe benefits, bonuses) live in :class:`PayPeriod`.

    Attributes:
        employee: Worker-side inputs.
        employment: Employment relationship inputs.
        family: Optional family composition for Art. 12 TUIR deductions.
        art15_deductions: Optional Art. 15 TUIR oneri detraibili.
        bilateral_funds: Bilateral fund contributions (fondi bilaterali).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    employee: Employee
    employment: Employment
    family: FamilyComposition | None = None
    art15_deductions: Art15Deductions | None = None
    bilateral_funds: tuple[BilateralFundInput, ...] = ()

    def to_dict(self) -> dict[str, object]:
        """Serialise to a JSON-compatible dictionary.

        Returns:
            A dict with only JSON-native types.
        """
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Serialise to a compact JSON string.

        Returns:
            A compact JSON string. See :meth:`to_dict` for encoding rules.
        """
        return self.model_dump_json()

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> AnnualPayrollScenario:
        """Reconstruct from a :meth:`to_dict` dictionary.

        Args:
            data: A dict as produced by :meth:`to_dict`.

        Returns:
            A new :class:`AnnualPayrollScenario` with all fields restored.
        """
        return cls.model_validate(data)

    @classmethod
    def from_json(cls, raw: str) -> AnnualPayrollScenario:
        """Reconstruct from a JSON string.

        Args:
            raw: A JSON string as returned by :meth:`to_json`.

        Returns:
            A new :class:`AnnualPayrollScenario` with all fields restored.
        """
        return cls.model_validate_json(raw)
