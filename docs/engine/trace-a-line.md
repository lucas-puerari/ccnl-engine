# Tracing a payslip line

Where each total of a run is computed, from the facade to the rule, so a
wrong amount on a payslip leads to its code. Every step below is a
function you can set a breakpoint on; the decisions of the result
(`result.decisions`) name the rule and the inputs each one used.

## The common path of every run

1. `api.py`: `PayrollEngine.calculate_period` checks the input and opens
   the decimal context of the call.
2. `period/input/services.py`: `period_request` turns the public
   `PeriodInput` into the internal `PeriodCalculationRequest`.
3. `period/services.py`: `calculate_period` runs the pipeline of the run:
   context, events, amounts, posting, result.
4. `period/context/request/services.py`: `build_context` loads the CCNL,
   the level and the year rules into the `RunContext`.
5. `period/step/services.py`: `run_events` prices the events;
   `run_amounts` computes the amounts of the run.
6. `period/step/input/services.py`: `amounts_input` gathers what the
   amounts read into `_AmountsInput` (pay, days, state, facts).
7. `period/amount/services.py`: `_compute_amounts` computes, in order,
   contributions, TFR, taxable income, IRPEF and surtax.

## From there, by total

| Total | Function | Rules |
|---|---|---|
| Gross and pay items | `period/step/services.py` `run_events`, then the pay items of `compensation/` | CCNL tables of the level (`agreement/`), seniority (`seniority/`), extra months (`extra_month/`) |
| INPS contributions | `contribution/services.py` `run_contributions` | `contribution/rules.py`, rates of the year in `YearRules.inps` (tier by headcount in `contribution/headcount/rules.py`) |
| TFR accrual | `contribution/services.py` `tfr_accrual` | `severance/` (divisor, 0.50% IVS deduction, compensation in `severance/relief/services.py`) |
| Taxable income | `irpef/taxable/services.py` | Untaxed amounts in `withholding/agent/services.py` |
| IRPEF | `irpef/services.py` `withhold_irpef`, then `irpef/computation/services.py` `compute_tax` | Brackets (`irpef/rules.py`), art. 13 deduction (`irpef/deduction/rules.py`), net IRPEF (`irpef/net/rules.py`), credits (`tax_credit/`) |
| Surtaxes | `surtax/rules.py` `run_surtax` | Tables of `surtax/stage/rules.py`, conguaglio and acconto in `surtax/conguaglio/rules.py` |
| Net | `withholding/cap/services.py` `run_net` | The ledger entries the posting of `period/posting/services.py` wrote |
| Employer cost | `period/result/services.py` `assemble_result` | Employer contributions, TFR, funds and INAIL-free employer items of the ledger |

## Reading a decision

A result carries one `CalculationDecision` per capability it decided:
`capability`, `rule` and `rule_version` name the rule, `inputs` the values
it read, `reason_code` why the amount is what it is. Start from the
decision of the wrong total, then open the rule it names in the table
above.
