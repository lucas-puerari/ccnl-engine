# `ccnl_engine.inputs`

Every fact a caller passes beyond the common path of the root: optional
fields of `Employment`, `EmployerProfile` and `PeriodFacts`, tax facts, the
calendar, the engine mode, the opening state and imported balances. See
[Opening state and imported balances](../engine/opening-state.md) for the
state types.

## Contract type, hours and seniority

::: ccnl_engine.inputs.Apprentice

::: ccnl_engine.inputs.FixedTerm

::: ccnl_engine.inputs.NaspiExclusion

::: ccnl_engine.inputs.Permanent

::: ccnl_engine.inputs.WorkerCategory

::: ccnl_engine.inputs.EmploymentPeriod

::: ccnl_engine.inputs.EmploymentSpell

::: ccnl_engine.inputs.WeeklyHours

::: ccnl_engine.inputs.WorkPattern

::: ccnl_engine.inputs.ContributableHours

::: ccnl_engine.inputs.SeniorityFact

::: ccnl_engine.inputs.SenioritySource

::: ccnl_engine.inputs.ContributionHistory

::: ccnl_engine.inputs.EmploymentSector

::: ccnl_engine.inputs.PensionFundEnrolment

::: ccnl_engine.inputs.NoPensionFund

::: ccnl_engine.inputs.PublicEndOfService

::: ccnl_engine.inputs.TfrFundBalance

::: ccnl_engine.inputs.TfrQuotaYtd

::: ccnl_engine.inputs.EmployerActivity

::: ccnl_engine.inputs.AgriculturalZone

::: ccnl_engine.inputs.TaxSector

## Family and tax facts

::: ccnl_engine.inputs.FamilyComposition

::: ccnl_engine.inputs.Dependent

::: ccnl_engine.inputs.DependentRelationship

::: ccnl_engine.inputs.IndividualElement

::: ccnl_engine.inputs.PriorYearTaxFacts

::: ccnl_engine.inputs.CurrentYearTaxFacts

::: ccnl_engine.inputs.IncomeEstimateQuality

::: ccnl_engine.inputs.ForeignTaxPaid

::: ccnl_engine.inputs.ShortfallDeferralRequest

::: ccnl_engine.inputs.SubstituteTaxRegime

## Calendar and engine mode

::: ccnl_engine.inputs.WorkCalendar

::: ccnl_engine.inputs.CalendarOverride

::: ccnl_engine.inputs.CalendarOverrideReason

::: ccnl_engine.inputs.EngineMode

## Opening state and imported balances

::: ccnl_engine.inputs.PeriodState

::: ccnl_engine.inputs.period_state_from_json

::: ccnl_engine.inputs.period_state_to_json

::: ccnl_engine.inputs.OpeningBalances

::: ccnl_engine.inputs.InpsBaseYtd

::: ccnl_engine.inputs.PaymentId

::: ccnl_engine.inputs.PayrollRunId

::: ccnl_engine.inputs.RecoveryObligation

::: ccnl_engine.inputs.RecoveryPlan

::: ccnl_engine.inputs.SurtaxComponent

::: ccnl_engine.inputs.SurtaxObligation

::: ccnl_engine.inputs.DeferredShortfall

## JSON form of a request

`request_to_json` writes a `PeriodInput`, a `CompetenceYearPlan` or a
`TaxYearPlan` as JSON, and `request_from_json` reads it back equal, through
the constructors of every value, so a request read from JSON is validated
like one built in Python. Each value is tagged with its type
(`{"$type": "Employment", "fields": {...}}`, `{"$enum": ...}`); decimals
are strings (`{"$decimal": "1234.50"}`), dates ISO 8601
(`{"$date": "2026-01-28"}`), and run-keyed maps keep their `int` or `str`
keys (`{"$map": [[3, ...], ["2026-12-thirteenth", ...]]}`). The envelope
carries `schema_version`, bumped when a field changes; unlike a persisted
state, a request carries no engine or bundle version and reads across
releases.

::: ccnl_engine.inputs.request_to_json

::: ccnl_engine.inputs.request_from_json

`validate_request_json` reads the same JSON and returns every error at
once instead of raising the first, for a batch import that shows a row all
its problems: each `InvalidInputError` carries the path of the rejected
value from the root, e.g. `PeriodInput.facts.events[1].hours`, and an
empty tuple means the request reads. An object reports at most one error
of its own, and only once its children are valid; the CCNL and the level
are checked by the run, not here.

::: ccnl_engine.inputs.validate_request_json
