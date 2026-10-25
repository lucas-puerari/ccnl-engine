# Payroll terms

The Italian terms the pages use, what they mean and where the engine holds
them. For the engine's own concepts (accrual, settlement, assurance) see the
[Glossary](glossary.md).

| Term | Meaning | In the engine |
|---|---|---|
| Paga base (minimo tabellare) | The minimum monthly pay of a CCNL level | `base_salary_earning` pay item; total `base_salary` |
| Superminimo | Pay above the CCNL minimum agreed with the worker | `Employment.individual_elements` |
| Scatti di anzianità | Seniority increments the CCNL grants by years of service | `Employment.seniority`; pay item `seniority_earning` |
| Quadri, impiegati, operai | Middle managers, white-collar and blue-collar workers: the categories that change INPS rates and some CCNL rules | `Employment.category` (`WorkerCategory`) |
| Tredicesima, quattordicesima | The 13th and 14th monthly payments | Extra-month runs (`PayrollRun.thirteenth`, `.fourteenth`) |
| Straordinari | Overtime hours, paid with the CCNL supplement | `OvertimeEvent` |
| Ferie, permessi, ex festività | Annual leave, paid leave hours, hours for abolished holidays | `LeaveTakenEvent`; balances in the state |
| Malattia | Sickness: INPS indemnity and the employer integration | `SickLeaveEvent`, `SicknessEpisode` |
| Maternità | Maternity leave and its INPS indemnity | `MaternityLeaveEvent` |
| Infortunio | Work injury: INAIL indemnity | Not computed (INAIL is outside the engine) |
| Una tantum | A one-off amount a CCNL renewal pays | Not computed as such; state it as a `BonusEvent` |
| Arretrati | Arrears of earlier periods, taxed separately when of earlier years | `ArrearsEvent` |
| Premio di risultato | Performance bonus of a second-level agreement, with its substitute tax | `BonusEvent` of kind `productivity_bonus` |
| TFR | Severance pay accrued every month and paid at the end of the employment | Total `tfr`; `TerminationTFREvent` |
| Previdenza complementare | Supplementary pension fund (Fon.Te., Cometa, ...) | `Employment.pension_fund` (`PensionFundEnrolment`) |
| Enti bilaterali, fondi sanitari | Bilateral bodies and health funds of a CCNL | `EmployerProfile.contractual_funds`; health funds outside a CCNL are not computed |
| Conguaglio | The year-end (or termination) recalculation of IRPEF and credits | The last withholding slot of the year |
| Addizionali regionale e comunale | Regional and municipal IRPEF surtaxes | `PeriodFacts.regione`, `comune_belfiore` |
| Detrazioni (art. 12, 13 TUIR) | Tax deductions for dependants and for employment income | `PeriodFacts.family_composition`; art. 13 rules of the year |
| Trattamento integrativo | The credit up to 1,200 EUR a year for low incomes | Credit `trattamento_integrativo` |
| Convivente | Live-in domestic worker | `lavoro-domestico-convivente` CCNLs |
| CNEL, ARAN | The national register of CCNLs; the agency that signs the public-sector ones | `ContractSummary.cnel_code` |
| UniEmens, F24, CU | The monthly INPS return, the tax payment form, the yearly tax certificate | Not produced: `remittance_summary()` gives the F24 amounts by codice tributo |
