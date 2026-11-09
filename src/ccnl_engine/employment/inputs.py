"""Employment contract types and the employment relationship."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.collection.validators import frozenset_of
from ccnl_engine.compensation.individual.inputs import (
    IndividualElement,
    check_individual_elements,
)
from ccnl_engine.contribution.ceiling.inputs import ContributionHistory
from ccnl_engine.employment.apprentice.inputs import Apprentice
from ccnl_engine.employment.category.models import (
    WorkerCategory,
    parse_worker_category,
)
from ccnl_engine.employment.contract.types import Contract, Permanent, _role
from ccnl_engine.employment.fact.inputs import (
    FEATURE,
    PublicEndOfService,
    WeeklyHours,
    WorkPattern,
    check_pattern_hours,
    check_within_full_time,
)
from ccnl_engine.employment.field_specs import employment_fields
from ccnl_engine.employment.fixed_term.inputs import FixedTerm
from ccnl_engine.employment.level_start import check_level_start
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.employment.rest_day.inputs import Weekday, check_rest_day
from ccnl_engine.employment.rota.inputs import Rota, check_rota
from ccnl_engine.employment.week_days.inputs import check_week_days
from ccnl_engine.pension_fund.inputs import (
    NoPensionFund,
    PensionFundEnrolment,
)
from ccnl_engine.personal_withholding.inputs import (
    PersonalWithholding,
    check_personal_withholdings,
)
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.seniority.inputs import SeniorityFact
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.validators import (
    FieldSpec,
    parse_enum,
    reject,
    require_decimal,
    require_instances,
    require_str,
)

__all__ = ["Apprentice", "Contract", "Employment", "FixedTerm", "Permanent"]

#: A CCNL file name of the bundle: no directory, no other extension.
_CCNL_ID = re.compile(r"[a-z0-9][a-z0-9-]*|[A-Z][A-Z0-9]{3}")


@dataclass(frozen=True)
class Employment:
    """The employment relationship: contract, level and worker facts.

    Facts are validated on construction: a value of the wrong type or an
    impossible combination raises
    :class:`~ccnl_engine.errors.InvalidInputError` instead of
    producing a payslip.

    Attributes:
        ccnl_id: CCNL slug or CNEL code; ambiguous or unknown ids raise
            :class:`~ccnl_engine.errors.UnknownCcnlError` at the run.
        level_code: Contractual level code, e.g. ``"C3"``.
        contract_type: Permanent, fixed term or apprentice; determines NASpI
            surcharge and the art. 13 TUIR deduction minimum.
        category: Worker category, accepting string values. ``None`` uses the
            level's fixed category; incompatible or ambiguous categories raise.
        employment_period: Start and optional end of the employment. ``None`` when not
            tracked: a year then computes every run of the calendar with full ratei.
        level_started_on: Entry date for time-limited levels (Confetra 6J).
        weekly_hours: Contracted weekly hours.  Required for domestic CCNLs to select
            the INPS bracket; below ``full_time_weekly_hours`` it scales the pay for
            part time.
        full_time_weekly_hours: Full-time weekly hours of the contract. ``weekly_hours``
            must not exceed it.
        full_time_week_days: Working days of the full-time week, 5 or 6; a CCNL
            that sets the daily pay by the week (Pulizia art. 34: 22 or 26) uses
            it.  ``None`` keeps the CCNL default divisor.
        rota: Rota of a security guard (``5+1``, ``6+1+1``, ``5+2``); a CCNL
            that sets the ferie by rota (FEDERDAT art. 89: 25, 23 or 22 days)
            uses it.  ``None`` keeps the CCNL default days.
        work_pattern: Vertical or mixed part time: the hours of each day of the week,
            whose sum must equal ``weekly_hours``, and the months of the year the worker
            works.  A month not worked pays no monthly pay and accrues no extra-month
            rateo.  ``None`` for a horizontal part time or a full time worked every
            month.
        weekly_rest_day: Day of the week of the weekly rest, Sunday unless stated
            (L. 370/1934 art. 3); a CCNL that pays a holiday falling on the rest day
            pays it on this day.  A rest day that rotates is not modelled.
        seniority: Recognised seniority, aged by the engine to each run. ``None`` means
            not known: a run whose level pays seniority increments or service-gated
            allowances then has a ``missing_fact`` blocker, and its amounts leave them
            out.
        roles: Role codes for contractual allowances and legacy holiday clauses
            (``former_legal_operaio`` or ``former_part_one_2008``), each a
            non-blank string.  A set is accepted and stored as a frozenset; an empty set
            states that the worker holds no role. ``None`` means not known: a run whose
            level has an allowance restricted to a role then has a ``missing_fact``
            blocker, and its amounts leave the allowance out.
        contribution_history: First enrolment in a mandatory pension scheme and
            contributory option, from which the engine derives whether the IVS massimale
            applies.  ``None`` means not known: a run whose INPS base crosses the
            massimale then has an undetermined contribution and a ``missing_fact``
            blocker.
        sector: Private or public sector of the employment, for the regimes restricted
            to one sector.  ``None`` means not known: those regimes are then ``unknown``
            and the result provisional.  It is not derived from the CCNL: a public
            employer may apply a private CCNL.
        pension_fund: Enrolment in a complementary pension fund of the CCNL, or
            :class:`~ccnl_engine.pension_fund.inputs.NoPensionFund` to state that the
            worker is not enrolled: no fund contribution is computed, and on a CCNL that
            has funds the ``pension_fund_contribution`` capability records the reason
            ``not_enrolled``.  ``None`` means not known: on every CCNL but domestic work
            the contributions are undetermined and the run has a ``missing_fact``
            blocker.
        tfr_fund: TFR fund at 31 December of the year before the run, the base of the
            revaluation at 31 December (art. 2120 c. 4 c.c.). ``None`` means not known:
            the December run then has a ``missing_fact`` blocker, unless the employment
            starts in the year of the run (no fund to revalue).
        tfr_treasury_fund: Whether the TFR not paid to a pension fund is paid to the
            Fondo Tesoreria INPS (L. 296/2006 art. 1 c. 756): the employer is obliged by
            its size and the worker is not excluded (DM 30 gennaio 2007 art. 1 cc. 5-8).
            ``None`` means not known: a run that accrues TFR in the company then has a
            ``missing_fact`` blocker.  Domestic work and the public administrations are
            outside the Fondo: ``True`` there raises ``InvalidInputError``, ``None`` and
            ``False`` keep the TFR in the company.
        holiday_company_offset: Company holiday compensation already paid for the
            eligible former-worker holidays of this month. Zero states no
            offset; ``None`` means the company arrangement is unknown.
        prior_extra_month_amount: Annual extra remuneration month(s) already
            received beyond the thirteenth at the contract's entry, excluding
            merit bonuses. Zero states none; ``None`` is unknown. The amount
            is a full monthly amount, before accrual proration.
        erc_amount: Annual Elemento di Raccordo Contrattuale of the CCNL grafici
            editoriali (renewal of 19 January 2021), frozen in December 2020; zero when
            the worker has none.  It is paid with the tredicesima, by its months, and
            sets the Byblos employer rate (1.4% with one, 1.9% without).  ``None`` means
            not known, zero for an employment that started after December 2020: an
            enrolled run, or a run paying the tredicesima, on that CCNL has a
            ``missing_fact`` blocker.
        public_end_of_service: End-of-service regime of a public employee (TFS, TFR at
            INPS or TFR at the employer), which sets the contributions to INPS Gestione
            Dipendenti Pubblici and whether the run accrues the TFR.  ``None`` means not
            known: a run on a CCNL of the public administrations has a ``missing_fact``
            blocker.
        individual_elements: Pay elements agreed with the worker above the
            CCNL minimum (superminimo, assegno ad personam), each with its
            own code; a list is accepted and stored as a tuple.
        personal_withholdings: Garnishments and salary assignments notified
            to the employer, each a
            :class:`~ccnl_engine.personal_withholding.inputs.PersonalWithholding`
            with its own id; a list is accepted and stored as a tuple.

    Raises:
        InvalidInputError: When a field is not of its type, a role is not a
            non-blank string, ``weekly_hours`` exceeds ``full_time_weekly_hours``
            or differs from the weekday hours of ``work_pattern``, ``category``,
            ``sector`` or ``weekly_rest_day`` names no known value, the week
            days are not 5 or 6, the pattern
            states hours on the rest day, or two individual elements or
            withholdings share a code.
    """

    ccnl_id: str
    level_code: str
    contract_type: Permanent | Apprentice | FixedTerm
    category: WorkerCategory | None = None
    employment_period: EmploymentPeriod | None = None
    level_started_on: date | None = None
    weekly_hours: WeeklyHours | None = None
    full_time_weekly_hours: WeeklyHours | None = None
    full_time_week_days: int | None = None
    rota: Rota | None = None
    work_pattern: WorkPattern | None = None
    weekly_rest_day: Weekday = Weekday.SUNDAY
    seniority: SeniorityFact | None = None
    roles: frozenset[str] | None = None
    contribution_history: ContributionHistory | None = None
    sector: EmploymentSector | None = None
    pension_fund: PensionFundEnrolment | NoPensionFund | None = None
    tfr_fund: TfrFundBalance | None = None
    tfr_treasury_fund: bool | None = None
    erc_amount: Decimal | None = None
    prior_extra_month_amount: Decimal | None = None
    holiday_company_offset: Decimal | None = None
    public_end_of_service: PublicEndOfService | None = None
    individual_elements: tuple[IndividualElement, ...] = ()
    personal_withholdings: tuple[PersonalWithholding, ...] = ()

    def __post_init__(self) -> None:  # noqa: D105
        if not isinstance(self.ccnl_id, str) or not _CCNL_ID.fullmatch(self.ccnl_id):
            reject(
                "Employment.ccnl_id",
                "a CCNL slug such as 'metalmeccanico-federmeccanica' or a "
                "CNEL code such as 'E042'",
                self.ccnl_id,
                feature=FEATURE,
            )
        require_str(
            self.level_code, "Employment.level_code", feature=FEATURE, non_blank=True
        )
        require_instances("Employment", self._typed_fields(), feature=FEATURE)
        check_level_start(self.level_started_on, self.employment_period)
        if self.roles is not None:
            roles = frozenset_of(self.roles, "Employment.roles", _role, feature=FEATURE)
            object.__setattr__(self, "roles", roles)
        object.__setattr__(self, "category", parse_worker_category(self.category))
        if self.sector is not None:
            sector = parse_enum(
                self.sector, EmploymentSector, "Employment.sector", feature=FEATURE
            )
            object.__setattr__(self, "sector", sector)
        if self.public_end_of_service is not None:
            regime = parse_enum(
                self.public_end_of_service,
                PublicEndOfService,
                "Employment.public_end_of_service",
                feature=FEATURE,
            )
            object.__setattr__(self, "public_end_of_service", regime)
        check_within_full_time(self.weekly_hours, self.full_time_weekly_hours)
        check_pattern_hours(self.weekly_hours, self.work_pattern)
        rest = check_rest_day(self.weekly_rest_day, self.work_pattern)
        object.__setattr__(self, "weekly_rest_day", rest)
        check_week_days(self.full_time_week_days)
        object.__setattr__(self, "rota", check_rota(self.rota))
        elements = check_individual_elements(
            self.individual_elements, "Employment.individual_elements"
        )
        object.__setattr__(self, "individual_elements", elements)
        withholdings = check_personal_withholdings(
            self.personal_withholdings, "Employment.personal_withholdings"
        )
        object.__setattr__(self, "personal_withholdings", withholdings)
        require_decimal(
            self.holiday_company_offset,
            "Employment.holiday_company_offset",
            feature=FEATURE,
            minimum=Decimal(0),
            optional=True,
        )
        require_decimal(
            self.prior_extra_month_amount,
            "Employment.prior_extra_month_amount",
            feature=FEATURE,
            optional=True,
            minimum=Decimal(0),
        )
        require_decimal(
            self.erc_amount,
            "Employment.erc_amount",
            feature=FEATURE,
            minimum=Decimal(0),
            optional=True,
        )

    def check_seniority_in(self, year: int, month: int) -> None:
        """Reject a seniority whose recognised service starts after a month.

        The run of the month ages :attr:`seniority` to it; checking on the
        input rejects a seniority that cannot be aged to the first run
        before any calculation, with
        :class:`~ccnl_engine.errors.InvalidInputError`.

        Args:
            year: Year of the competence month of the run.
            month: Competence month of the run, 1-12.
        """
        if self.seniority is not None:
            self.seniority.months_in_month(year, month)

    def _typed_fields(self) -> tuple[FieldSpec, ...]:
        return employment_fields(self, (Permanent, Apprentice, FixedTerm))
