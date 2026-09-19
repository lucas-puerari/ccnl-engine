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
- :class:`AnnualizedAssumption` — full-year fiscal assumption for estimates.
- :class:`TaxPeriod` — actual work-period data for period payroll pro-rata.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

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
_DAYS_IN_YEAR: int = 365


class AnnualizedAssumption(BaseModel):
    """Full-year fiscal assumption for annual estimate computations.

    Used by :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_annual` to indicate that all fiscal formulas (Art. 13
    work-income deduction, ulteriore detrazione, trattamento integrativo)
    are applied at 365/365, i.e. a full calendar year is assumed.

    Attributes:
        type: Discriminator literal ``"annualized"``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["annualized"] = "annualized"


class TaxPeriod(BaseModel):
    """Actual work-period data required for period payroll fiscal pro-rata.

    When provided, fiscal formulas are scaled by
    ``eligible_work_days / 365`` instead of assuming a full year.
    Required when calling
    :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects`.

    ``eligible_work_days`` counts calendar days in the **tax year** for
    which the worker is employed, not days in the pay period alone.  For
    a worker hired on 1 March, the correct value for the March payslip is
    ``(31 Dec - 1 Mar).days + 1 = 306``, not ``31``.

    Attributes:
        type: Discriminator literal ``"tax_period"``.
        start: First day of employment in the tax year (inclusive).
        end: Last day of employment in the tax year (inclusive).
        eligible_work_days: Calendar days in the tax year the worker is
            employed.  Must be ``>= 1`` and ``<= (end - start).days + 1``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["tax_period"] = "tax_period"
    start: date
    end: date
    eligible_work_days: int

    @model_validator(mode="after")
    def _check(self) -> TaxPeriod:
        if self.start > self.end:
            msg = f"TaxPeriod.start {self.start} is after end {self.end}"
            raise ValueError(msg)
        max_days = (self.end - self.start).days + 1
        if self.eligible_work_days < 1:
            msg = f"eligible_work_days must be >= 1, got {self.eligible_work_days}"
            raise ValueError(msg)
        if self.eligible_work_days > max_days:
            msg = (
                f"eligible_work_days {self.eligible_work_days} exceeds "
                f"period span {max_days} days ({self.start} to {self.end})"
            )
            raise ValueError(msg)
        return self


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
        inail_rate: Caller-supplied INAIL tariff rate (e.g. ``Decimal("0.015")``
            for 1.5%). When set, the engine computes the INAIL employer
            contribution as ``gross_annual * inail_rate`` and adds it to
            ``employer_cost_annual``. Must be ``>= 0``. ``None`` means INAIL
            is not modelled (reported as ``not_computed`` in the scope).
            The INAIL massimale and minimale retributivi are not applied;
            the caller is responsible for providing the correct net rate.
        inps_employer_exemption_annual: Caller-declared annual INPS employer
            contribution exemption (e.g. Esonero contributivo, Decontribuzione
            Sud). When set, the engine subtracts this amount from
            ``employer_cost_annual``, capped at ``inps_employer_annual``
            (cannot exceed the contribution itself). Must be ``>= 0``.
            ``None`` means no exemption is applied.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    num_employees: int = Field(ge=1)
    second_level_allowances: tuple[SupplementaryAllowance, ...] = ()
    inail_rate: StrictDecimal | None = None
    inps_employer_exemption_annual: StrictDecimal | None = None

    @model_validator(mode="after")
    def _check_rates(self) -> Employer:
        if self.inail_rate is not None and self.inail_rate < _ZERO:
            msg = f"inail_rate must be >= 0, got {self.inail_rate}"
            raise ValueError(msg)
        if (
            self.inps_employer_exemption_annual is not None
            and self.inps_employer_exemption_annual < _ZERO
        ):
            msg = (
                "inps_employer_exemption_annual must be >= 0, "
                f"got {self.inps_employer_exemption_annual}"
            )
            raise ValueError(msg)
        return self


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
            ``AnnualEstimate.sterilizzazione_clawback_annual``.
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
    tax_basis: Annotated[
        AnnualizedAssumption | TaxPeriod,
        Field(discriminator="type"),
    ] = AnnualizedAssumption()
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
    prior_period_irpef_withheld: StrictDecimal | None = None
    maternity_inps_indemnity_annual: StrictDecimal | None = None
    workplace_injury_inail_indemnity_annual: StrictDecimal | None = None
    termination_residual_leave_payout_annual: StrictDecimal | None = None
    termination_tfr_liquidation_annual: StrictDecimal | None = None
    contract_renewal_arrears_annual: StrictDecimal | None = None

    @model_validator(mode="after")
    def _check_prior_irpef(self) -> PayrollScenario:
        if (
            self.prior_period_irpef_withheld is not None
            and self.prior_period_irpef_withheld < _ZERO
        ):
            msg = (
                "prior_period_irpef_withheld must be >= 0, "
                f"got {self.prior_period_irpef_withheld}"
            )
            raise ValueError(msg)
        if (
            self.maternity_inps_indemnity_annual is not None
            and self.maternity_inps_indemnity_annual < _ZERO
        ):
            msg = (
                "maternity_inps_indemnity_annual must be >= 0, "
                f"got {self.maternity_inps_indemnity_annual}"
            )
            raise ValueError(msg)
        if (
            self.workplace_injury_inail_indemnity_annual is not None
            and self.workplace_injury_inail_indemnity_annual < _ZERO
        ):
            msg = (
                "workplace_injury_inail_indemnity_annual must be >= 0, "
                f"got {self.workplace_injury_inail_indemnity_annual}"
            )
            raise ValueError(msg)
        if (
            self.termination_residual_leave_payout_annual is not None
            and self.termination_residual_leave_payout_annual < _ZERO
        ):
            msg = (
                "termination_residual_leave_payout_annual must be >= 0, "
                f"got {self.termination_residual_leave_payout_annual}"
            )
            raise ValueError(msg)
        if (
            self.termination_tfr_liquidation_annual is not None
            and self.termination_tfr_liquidation_annual < _ZERO
        ):
            msg = (
                "termination_tfr_liquidation_annual must be >= 0, "
                f"got {self.termination_tfr_liquidation_annual}"
            )
            raise ValueError(msg)
        if (
            self.contract_renewal_arrears_annual is not None
            and self.contract_renewal_arrears_annual < _ZERO
        ):
            msg = (
                "contract_renewal_arrears_annual must be >= 0, "
                f"got {self.contract_renewal_arrears_annual}"
            )
            raise ValueError(msg)
        return self


class PeriodPayrollInput(BaseModel):
    """Period-specific payroll events for a single pay period.

    Passed to :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects` alongside an :class:`AnnualEstimateInput` to supply
    the month's variable events (overtime, absences, sick leave, benefits).

    All fields are optional — a ``PeriodPayrollInput()`` with no arguments represents
    a standard month with no special events.

    Attributes:
        tax_period: Work-period data for fiscal pro-rata.  Required when
            calling :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects`; the function raises
            :exc:`~ccnl_engine.engine.errors.InvalidInputError` when absent.
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

    tax_period: TaxPeriod | None = None
    time_supplements: OvertimeHours | None = None
    absence_days: AbsenceDays | None = None
    leave_input: LeaveInput | None = None
    sick_input: SickInput | None = None
    fringe_benefit_input: FringeBenefitInput | None = None
    welfare_input: WelfareInput | None = None
    bonus_input: BonusInput | None = None


class AnnualEstimateInput(BaseModel):
    """Structural payroll scenario without period-specific events.

    Use :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_annual` to compute annual gross-to-net figures, or
    :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.estimate_period_effects` together with a :class:`PeriodPayrollInput` to include
    the month's variable events in the result fields.

    Compared to the legacy :class:`PayrollScenario`, this class holds only
    the structural fields that describe *who the worker is* and *what the
    employment relationship is*.  Period-specific events (overtime, absences,
    sick leave, fringe benefits, bonuses) live in :class:`PeriodPayrollInput`.

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
