# Changelog

All notable changes to `ccnl-engine` are listed here, newest first. Each
release links the sections of the [migration guide](docs/migration.md) that
describe its breaking changes in detail. Versions follow
[Semantic Versioning](https://semver.org/) for the engine; the knowledge
bundle carries its own version (`ccnl_engine.knowledge.__version__`).

## [0.6.0] - not released yet

Engine 0.6.0, knowledge bundle 2026.3. This release rebuilds the payability
contract: a result is payable only when every fact and capability it needs
is known and computed, and nothing in the 2026 bundle is payable yet.

### Breaking changes

- **Result assurance replaces the result status.** `PeriodResult.status` is
  gone; read `result.is_payable`, `result.blockers`, `result.rulesets` and
  `result.assurance` (calculation, coverage, evidence, limitations).
- **Fail-closed payability.** A capability the run needs and does not
  compute, or rules out only through a default, blocks payment
  (`requirement_unresolved`). Unknown facts now block where they decide an
  amount: residence of a withholding employer, family composition and every
  condition of a dependant, the opening state of a run after the start of
  the employment, the base and the 1% IVS of other employers, the TFR fund
  and its destination, the pension fund enrolment on every CCNL but domestic
  work, the full time of stated weekly hours, roles, the suspension of
  accrual of an absence, the renewals and NASpI exclusion of a fixed term.
- **Required facts without a default.** `Employment.contract_type`,
  `Dependent.dependent_from` and `dependent_until`, and the `inps_bases`,
  `recoveries` and `surtax_obligations` of `OpeningBalances` must be stated.
- **Public names in four namespaces.** The root exports the common path;
  further facts are in `ccnl_engine.inputs`, events in `ccnl_engine.events`,
  assurance and decisions in `ccnl_engine.results`, contracts and readiness
  in `ccnl_engine.catalog`.
- **Competence and tax years.** `YearInput` is replaced by
  `CompetenceYearPlan` and `TaxYearPlan`; the state splits into an accrual
  state and a tax cash state (`PeriodState.SCHEMA_VERSION` 12).
- **Provenance labels.** A rule of an estimated ruleset, or without a cited
  source, cannot be `derived`; every `reviewed` CCNL became `exploratory`.

### Added

- `PayrollEngine.bundled(mode="operational")`, ruleset readiness in
  `list_contracts()` and `inspect_ruleset()`, validity windows of each CCNL
  and partial competence years.
- `PayrollEngine.list_levels()`, `ccnl_engine.catalog.supported_tax_years()`,
  `PeriodResult.paid_gross`, and the JSON form of a state
  (`period_state_to_json`, `period_state_from_json`); results pickle.
- `CurrentYearTaxFacts.exempt_regime_income`: the exempt share of the
  impatriati and researcher regimes, counted in the reddito complessivo of
  the somma esente (L. 207/2024 art. 1 c. 9).
- Fon.Te. on Commercio, Turismo (Confcommercio, Federalberghi), Pubblici
  esercizi and Agenzie di viaggio, on the TFR base
  (`EmployerFund.contribution_base`), with the employer rate of each CCNL
  and of apprentices (`EmployerFund.apprentice_rate`).
- Alifond on Alimentari Federalimentare; Alifond on Tabacco moves to the
  TFR base its statute names. Fondapi on Alimentari PMI; the Fondapi
  record of Tessile PMI, on a base the engine does not compute, is removed.
  Fonchim on Chimica farmaceutica; Fonchim on Vetro moves to the TFR base
  with the 0.25% insurance contribution and the 1.50% employee minimum.
- Payroll rules: per-run withholding under art. 23 DPR 600/1973, monthly
  1% additional IVS with year-end settlement, the INPS minimum base, the TFR
  net of the 0.50% additional IVS, the TFR revaluation and the Fondo
  Tesoreria, the NASpI surcharge with renewals and exclusions, the art. 13
  minimum (proportioned in the withholding), the trattamento integrativo on
  art. 12 and art. 13 deductions, Cassa Colf and board and lodging of
  domestic work, the Federmeccanica sickness tiers and comporto, the renewal
  substitute tax on the renewed minimo, separate taxation of arrears of
  earlier years.

### Fixed

- The art. 16-ter c. 5-bis reduction is no longer applied to the art. 12
  and art. 13 deductions, which it does not concern.
- A dependent's conditions, residence and opening state left unknown no
  longer compute a payable-looking amount.
- A sickness spanning a whole month, a late December payment and a
  same-year rehire compute; a negative net raises a typed error instead of
  `DataIntegrityError`; an input error never escapes as a bare `ValueError`.
- The 2026 municipal surtax table is refreshed from the MEF list, with
  inapplicable delibere skipped.

### Not yet covered

- Tax, INPS and surtax tables of 2027: a payment of 2027 raises
  `UnsupportedTaxYearError` until the 2027 sources are published.
- No bundled CCNL is `production` and no rule is `verified`: every amount is
  a simulation.

## [0.5.1] and earlier

See the [migration guide: earlier releases](docs/migration-earlier.md).
