"""Employment contract types and the employment relationship."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from ccnl_engine.contract.domain.category import (
    WorkerCategory,
    parse_worker_category,
)
from ccnl_engine.payroll.domain.eligibility import ContributionHistory
from ccnl_engine.payroll.domain.employment_facts import (
    FEATURE,
    EmploymentPeriod,
    WeeklyHours,
    check_within_full_time,
)
from ccnl_engine.payroll.domain.pension_fund import (
    PENSION_FUND_TYPES,
    NoPensionFund,
    PensionFundEnrolment,
)
from ccnl_engine.payroll.domain.seniority_fact import SeniorityFact
from ccnl_engine.payroll.domain.tfr_fund import TfrFundBalance
from ccnl_engine.shared.domain.collection_validation import frozenset_of
from ccnl_engine.shared.domain.validation import (
    FieldSpec,
    parse_enum,
    reject,
    require_instances,
    require_int,
    require_str,
)
from ccnl_engine.tax.domain.preferential_regime import EmploymentSector

_CONTRACT_FEATURE = "contract_type"
#: A CCNL file name of the bundle: no directory, no other extension.
_SLUG = re.compile(r"[a-z0-9][a-z0-9-]*\.json")


@dataclass(frozen=True, slots=True)
class Permanent:
    """Standard open-ended (permanent) employment contract."""

    type: Literal["permanent"] = field(default="permanent", init=False)


@dataclass(frozen=True, slots=True)
class FixedTerm:
    """Fixed-term contract; attracts NASpI addizionale on employer INPS."""

    type: Literal["fixed_term"] = field(default="fixed_term", init=False)


@dataclass(frozen=True, slots=True)
class Apprentice:
    """Apprenticeship contract; salary is derived from CCNL apprenticeship rules.

    Attributes:
        months_elapsed: Months of apprenticeship service elapsed so far,
            ``>= 0``.  Used to look up the applicable ``apprenticeship_pct``
            in the CCNL percentage track, or the under-classification level
            in under-classification tracks.
        track: Name of the CCNL apprenticeship track to apply. Required
            only when more than one track covers the destination level;
            ``None`` lets the engine select the unique applicable track.

    Raises:
        InvalidInputError: When ``months_elapsed`` is not a non-negative
            int or ``track`` is not a non-blank string.
    """

    months_elapsed: int
    track: str | None = None
    type: Literal["apprentice"] = field(default="apprentice", init=False)

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.months_elapsed,
            "Apprentice.months_elapsed",
            feature=_CONTRACT_FEATURE,
            minimum=0,
        )
        require_str(
            self.track,
            "Apprentice.track",
            feature=_CONTRACT_FEATURE,
            non_blank=True,
            optional=True,
        )


#: Every supported employment contract type.
type Contract = Permanent | FixedTerm | Apprentice


def _role(value: object, path: str) -> str:
    require_str(value, path, feature=FEATURE, non_blank=True)
    return str(value)


@dataclass(frozen=True)
class Employment:
    """The employment relationship: contract, level and worker facts.

    Facts are validated on construction: a value of the wrong type or an
    impossible combination raises
    :class:`~ccnl_engine.shared.domain.errors.InvalidInputError` instead of
    producing a payslip.

    Attributes:
        ccnl_slug: Knowledge-bundle CCNL filename, e.g.
            ``"metalmeccanico-federmeccanica.json"``: lower-case letters,
            digits and hyphens, then ``.json``.  A name the bundle does not
            hold raises :class:`~ccnl_engine.shared.domain.errors\
.UnknownCcnlError` when the run loads it.
        level_code: Contractual level code, e.g. ``"C3"``.
        contract_type: :class:`Permanent`, :class:`FixedTerm` or
            :class:`Apprentice`.
        category: Worker category; its string value (e.g. ``"operaio"``) is
            accepted and normalized.  ``None`` takes the category fixed by
            the level, if any.  The calculation raises when the category
            differs from the one the level fixes, or when it is ``None`` and
            seniority increments for the level differ by category.
        employment_period: Start and optional end of the employment.
            ``None`` when not tracked: a year then computes every run of the
            calendar with full ratei.
        weekly_hours: Contracted weekly hours.  Required for domestic CCNLs
            to select the INPS bracket; below ``full_time_weekly_hours`` it
            scales the pay for part time.
        full_time_weekly_hours: Full-time weekly hours of the contract.
            ``weekly_hours`` must not exceed it.
        seniority: Recognised seniority, aged by the engine to each run.
            ``None`` means not known: a run whose level pays seniority
            increments or service-gated allowances then has a
            ``missing_fact`` blocker, and its amounts leave them out.
        roles: Role codes that unlock role-specific contractual allowances,
            each a non-blank string.  A set is accepted and stored as a
            frozenset; an empty set states that the worker holds no role.
            ``None`` means not known: a run whose level has an allowance
            restricted to a role then has a ``missing_fact`` blocker, and
            its amounts leave the allowance out.
        contribution_history: First enrolment in a mandatory pension scheme
            and contributory option, from which the engine derives whether
            the IVS massimale applies.  ``None`` means not known: a run whose
            INPS base crosses the massimale then has an undetermined
            contribution and a ``missing_fact`` blocker.
        sector: Private or public sector of the employment, for the regimes
            restricted to one sector.  ``None`` means not known: those
            regimes are then ``unknown`` and the result provisional.  It is
            not derived from the CCNL: a public employer may apply a private
            CCNL.
        pension_fund: Enrolment in a complementary pension fund of the CCNL,
            or :class:`~ccnl_engine.payroll.domain.pension_fund.NoPensionFund`
            to state that the worker is not enrolled: no fund contribution is
            computed, and on a CCNL that has funds the
            ``pension_fund_contribution`` capability records the reason
            ``not_enrolled``.  ``None`` means not known: on a CCNL that has
            funds the contributions are undetermined and the run has a
            ``missing_fact`` blocker.
        tfr_fund: TFR fund at 31 December of the year before the run, the
            base of the revaluation at 31 December (art. 2120 c. 4 c.c.).
            ``None`` means not known: the December run then has a
            ``missing_fact`` blocker, unless the employment starts in the
            year of the run (no fund to revalue).
        tfr_treasury_fund: Whether the TFR not paid to a pension fund is
            paid to the Fondo Tesoreria INPS (L. 296/2006 art. 1 c. 756):
            the employer is obliged by its size and the worker is not
            excluded (DM 30 gennaio 2007 art. 1 cc. 5-8).  ``None`` means not
            known: a run that accrues TFR in the company then has a
            ``missing_fact`` blocker.  Domestic work and the public
            administrations are outside the Fondo: ``True`` there raises
            ``InvalidInputError``, ``None`` and ``False`` keep the TFR in
            the company.

    Raises:
        InvalidInputError: When a field is not of its type, a role is not a
            non-blank string, ``weekly_hours`` exceeds
            ``full_time_weekly_hours``, or ``category`` or ``sector`` names
            no known value.
    """

    ccnl_slug: str
    level_code: str
    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    category: WorkerCategory | None = None
    employment_period: EmploymentPeriod | None = None
    weekly_hours: WeeklyHours | None = None
    full_time_weekly_hours: WeeklyHours | None = None
    seniority: SeniorityFact | None = None
    roles: frozenset[str] | None = None
    contribution_history: ContributionHistory | None = None
    sector: EmploymentSector | None = None
    pension_fund: PensionFundEnrolment | NoPensionFund | None = None
    tfr_fund: TfrFundBalance | None = None
    tfr_treasury_fund: bool | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if not isinstance(self.ccnl_slug, str) or not _SLUG.fullmatch(self.ccnl_slug):
            reject(
                "Employment.ccnl_slug",
                "a bundle file name such as 'metalmeccanico-federmeccanica.json'",
                self.ccnl_slug,
                feature=FEATURE,
            )
        require_str(
            self.level_code, "Employment.level_code", feature=FEATURE, non_blank=True
        )
        require_instances("Employment", self._typed_fields(), feature=FEATURE)
        if self.roles is not None:
            roles = frozenset_of(self.roles, "Employment.roles", _role, feature=FEATURE)
            object.__setattr__(self, "roles", roles)
        object.__setattr__(self, "category", parse_worker_category(self.category))
        if self.sector is not None:
            sector = parse_enum(
                self.sector, EmploymentSector, "Employment.sector", feature=FEATURE
            )
            object.__setattr__(self, "sector", sector)
        check_within_full_time(self.weekly_hours, self.full_time_weekly_hours)

    def check_seniority_in(self, year: int, month: int) -> None:
        """Reject a seniority whose recognised service starts after a month.

        The run of the month ages :attr:`seniority` to it; checking on the
        input rejects a seniority that cannot be aged to the first run
        before any calculation, with
        :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.

        Args:
            year: Year of the competence month of the run.
            month: Competence month of the run, 1-12.
        """
        if self.seniority is not None:
            self.seniority.months_in_month(year, month)

    def _typed_fields(self) -> tuple[FieldSpec, ...]:
        return (
            (
                "contract_type",
                self.contract_type,
                (Permanent, Apprentice, FixedTerm),
                False,
            ),
            ("employment_period", self.employment_period, EmploymentPeriod, True),
            ("weekly_hours", self.weekly_hours, WeeklyHours, True),
            ("full_time_weekly_hours", self.full_time_weekly_hours, WeeklyHours, True),
            ("seniority", self.seniority, SeniorityFact, True),
            (
                "contribution_history",
                self.contribution_history,
                ContributionHistory,
                True,
            ),
            ("pension_fund", self.pension_fund, PENSION_FUND_TYPES, True),
            ("tfr_fund", self.tfr_fund, TfrFundBalance, True),
            ("tfr_treasury_fund", self.tfr_treasury_fund, bool, True),
        )
