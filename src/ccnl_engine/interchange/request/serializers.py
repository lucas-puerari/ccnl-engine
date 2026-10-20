"""JSON form of the requests of :class:`~ccnl_engine.PayrollEngine`.

A :class:`~ccnl_engine.PeriodInput`, a
:class:`~ccnl_engine.CompetenceYearPlan` or a
:class:`~ccnl_engine.TaxYearPlan` is written as the tagged tree of
:mod:`ccnl_engine.codec.serializers`, in an envelope that carries
its schema version, and read back through the constructors of
:data:`REQUEST_TYPES`, so a request read from JSON is validated like one
built in Python.

Unlike a persisted state, a request carries no engine or bundle version: it
states facts, not balances computed by a version of the rules, so a request
written by one release is read by the next as long as its schema holds.
"""

from __future__ import annotations

import json
from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.absence.inputs import AbsenceEvent, SickLeaveEvent
from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.balance.serializers import STATE_TYPES
from ccnl_engine.calendar.inputs import CalendarOverride, CalendarOverrideReason
from ccnl_engine.calendar.models import WorkCalendar
from ccnl_engine.codec.serializers import encode, loads, reject
from ccnl_engine.codec.tree.serializers import read_tree
from ccnl_engine.compensation.individual.inputs import IndividualElement
from ccnl_engine.contribution.ceiling.inputs import ContributionHistory
from ccnl_engine.contribution.zone.models import AgriculturalZone
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.change.inputs import EmploymentChange
from ccnl_engine.employment.fact.inputs import (
    ContributableHours,
    EmploymentPeriod,
    PublicEndOfService,
    WeeklyHours,
    WorkPattern,
)
from ccnl_engine.employment.fixed_term.inputs import FixedTerm, NaspiExclusion
from ccnl_engine.employment.inputs import Apprentice, Employment, Permanent
from ccnl_engine.extra_month.schedule.models import (
    ExtraMonthKind,
    ExtraMonthSchedule,
)
from ccnl_engine.family.inputs import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.irpef.declaration.inputs import PriorYearTaxFacts
from ccnl_engine.irpef.other_income.inputs import (
    CurrentYearTaxFacts,
    IncomeEstimateQuality,
)
from ccnl_engine.leave.inputs import LeaveTakenEvent
from ccnl_engine.pension_fund.inputs import NoPensionFund, PensionFundEnrolment
from ccnl_engine.period.inputs import PeriodFacts, PeriodInput
from ccnl_engine.regime.models import (
    EmployerActivity,
    EmploymentSector,
    SubstituteTaxRegime,
)
from ccnl_engine.run.models import PayrollRun
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import (
    EarnedIncrements,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.tax_credit.foreign.inputs import ForeignTaxPaid
from ccnl_engine.termination.inputs import TerminationTFREvent
from ccnl_engine.variable_pay.inputs import (
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    TravelAllowanceEvent,
    WelfareEvent,
)
from ccnl_engine.withholding.deferral.inputs import ShortfallDeferralRequest
from ccnl_engine.working_time.inputs import (
    HolidayWorkEvent,
    HolidayWorkKind,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftKind,
    ShiftWorkEvent,
)
from ccnl_engine.working_time.standby.inputs import StandbyEvent, StandbyKind
from ccnl_engine.year.competence.inputs import CompetenceYearPlan
from ccnl_engine.year.tax_year.inputs import TaxYearPlan

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.errors import InvalidInputError

__all__ = [
    "REQUEST_SCHEMA_VERSION",
    "REQUEST_TYPES",
    "Request",
    "read_request",
    "request_from_json",
    "request_to_json",
]

#: Version of the JSON form of a request: bumped when a field of a request
#: type is renamed, removed or changes meaning.  Version 2 names the CCNL of
#: an ``Employment`` by ``ccnl_id`` (version 1: ``ccnl_slug``, never merged).
REQUEST_SCHEMA_VERSION = 2

_FEATURE = "request_json"
_SUBJECT = "the request"

#: A request of :class:`~ccnl_engine.PayrollEngine`.
type Request = PeriodInput | CompetenceYearPlan | TaxYearPlan

#: Every type a request may contain, keyed by the tag it is written with:
#: the request types, what they hold and the types of an opening state.
REQUEST_TYPES: Mapping[str, type] = MappingProxyType({
    **STATE_TYPES,
    **{
        cls.__name__: cls
        for cls in (
            AbsenceEvent,
            AgriculturalZone,
            Apprentice,
            ArrearsEvent,
            BilateralFundEvent,
            BonusEvent,
            CalendarOverride,
            CalendarOverrideReason,
            CompetenceYearPlan,
            ContributableHours,
            ContributionHistory,
            CurrentYearTaxFacts,
            Dependent,
            DependentRelationship,
            EmployerActivity,
            EmployerProfile,
            Employment,
            EarnedIncrements,
            EmploymentChange,
            EmploymentPeriod,
            EmploymentSector,
            ExtraMonthKind,
            ExtraMonthSchedule,
            FamilyComposition,
            FixedTerm,
            ForeignTaxPaid,
            FringeEvent,
            Headcount,
            HolidayWorkEvent,
            HolidayWorkKind,
            IncomeEstimateQuality,
            IndividualElement,
            LeaveTakenEvent,
            NaspiExclusion,
            NightShiftEvent,
            NoPensionFund,
            OvertimeEvent,
            OvertimeKind,
            PayrollRun,
            PensionFundEnrolment,
            PeriodFacts,
            PeriodId,
            PeriodInput,
            Permanent,
            PriorYearTaxFacts,
            PublicEndOfService,
            SeniorityFact,
            SenioritySource,
            ShiftKind,
            ShiftWorkEvent,
            ShortfallDeferralRequest,
            SickLeaveEvent,
            StandbyEvent,
            StandbyKind,
            SubstituteTaxRegime,
            TaxSector,
            TaxYearPlan,
            TerminationTFREvent,
            TfrFundBalance,
            TravelAllowanceEvent,
            WeeklyHours,
            WelfareEvent,
            WorkCalendar,
            WorkerCategory,
            WorkPattern,
        )
    },
})

_NAMES: Mapping[type, str] = MappingProxyType({
    cls: name for name, cls in REQUEST_TYPES.items()
})


def request_to_json(request: Request) -> str:
    """Return ``request`` as JSON text, with its schema version.

    Decimals are written as strings and dates in ISO 8601, so the text
    reads back equal with :func:`request_from_json`.

    Returns:
        The JSON text of the request.
    """
    payload = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "request": encode(request, _NAMES),
    }
    return json.dumps(payload, sort_keys=True)


def request_from_json[R: (PeriodInput, CompetenceYearPlan, TaxYearPlan)](
    text: str, kind: type[R]
) -> R:
    """Return the request of type ``kind`` written by :func:`request_to_json`.

    Every value is rebuilt through its constructor, so the request is
    validated as if built in Python.  A text that is not such JSON, of
    another schema version or holding another kind of request raises
    :class:`~ccnl_engine.errors.InvalidInputError`, and so does the first
    rejected value, with its path, e.g.
    ``"PeriodInput.facts.events[1].hours"``, as field.

    Args:
        text: The JSON text.
        kind: :class:`~ccnl_engine.PeriodInput`,
            :class:`~ccnl_engine.CompetenceYearPlan` or
            :class:`~ccnl_engine.TaxYearPlan`.

    Returns:
        The request.
    """
    request, errors = read_request(text, kind)
    if errors:
        raise errors[0]
    return request


def read_request[R: (PeriodInput, CompetenceYearPlan, TaxYearPlan)](
    text: str, kind: type[R]
) -> tuple[R, tuple[InvalidInputError, ...]]:
    """Read the request of type ``kind`` and every error of its values.

    A text that is not such JSON, of another schema version or holding
    another kind of request raises
    :class:`~ccnl_engine.errors.InvalidInputError`: no value can be read.

    Returns:
        The request, meaningless when there is an error, and one error per
        rejected value, each with its path as field.
    """
    payload = loads(text, subject=_SUBJECT, feature=_FEATURE)
    version = payload.get("schema_version")
    if version != REQUEST_SCHEMA_VERSION:
        reject(
            _SUBJECT,
            f"schema_version {version!r}, expected {REQUEST_SCHEMA_VERSION!r}",
            feature=_FEATURE,
        )
    tree = payload.get("request")
    if not isinstance(tree, dict) or tree.get("$type") != kind.__name__:
        reject(_SUBJECT, f"not a {kind.__name__}", feature=_FEATURE)
    request, errors = read_tree(
        tree, kind.__name__, types=REQUEST_TYPES, subject=_SUBJECT, feature=_FEATURE
    )
    return request, errors
