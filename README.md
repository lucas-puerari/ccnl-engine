# ccnl-engine

[![PyPI version](https://img.shields.io/pypi/v/ccnl-engine?logo=pypi&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![Python](https://img.shields.io/pypi/pyversions/ccnl-engine?logo=python&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![CI](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![Coverage](https://lucas-puerari.github.io/ccnl-engine/coverage-badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/lucas-puerari/ccnl-engine/blob/main/LICENSE)

A Python engine for auditable Italian payroll. It computes gross, net and
employer cost according to the CCNL from versioned rules with cited sources,
and every result says whether its amounts can be paid as they are.

> **Alpha.** The API can change between minor versions. Most bundled CCNLs
> are extracted and not yet reviewed: use the amounts for simulation unless a
> result says `is_payable`.

## Installation

```bash
pip install ccnl-engine
```

Python 3.12 or later. No other service is needed: the CCNL data ship with the
package.

## Example

```python
from ccnl_engine import CompetenceYearPlan, EmployerProfile, Employment, Headcount, PayrollEngine
from ccnl_engine.catalog import search_ccnls
from ccnl_engine.inputs import Permanent

engine = PayrollEngine.bundled()

# Find the CCNL and its levels: no file name to know in advance.
(contract,) = search_ccnls("terziario, distribuzione")
print(contract.ccnl_id, [level.code for level in engine.list_levels(contract.ccnl_id)])

year = engine.calculate_competence_year(
    CompetenceYearPlan(
        year=2026,
        employment=Employment(
            ccnl_slug=contract.ccnl_id, level_code="4", contract_type=Permanent()
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    )
)
print(year.annual_gross, year.annual_net, year.annual_employer_cost)
print(year.is_payable)  # False: the facts left unstated are in year.blockers
for blocker in year.blockers[:3]:
    print(blocker.code.value, blocker.feature, blocker.detail)
```

This example runs in CI. More in
[Getting started](https://lucas-puerari.github.io/ccnl-engine/docs/getting-started/)
and the [examples](https://lucas-puerari.github.io/ccnl-engine/docs/examples/).

## What it does

- Gross pay from the CCNL tables: base salary, seniority increments,
  allowances, extra monthly payments, part time and apprenticeship.
- Net pay: INPS contributions, IRPEF with deductions and credits, regional and
  municipal surtaxes, TFR.
- Employer cost: employer contributions, contractual funds, TFR.
- Single runs, competence years and tax years, with the state carried between
  them and the conguaglio.
- Work events: overtime, night and holiday work, absences, sickness, bonuses.
- An answer on every result: `is_payable`, the `blockers` and the decisions
  taken, each traced to a ruleset version and a source.

## What it does not do

- It is not legal or tax advice, and it does not replace a payroll provider.
- It files nothing: no F24, UniEmens or Certificazione Unica.
- Second-level (company or territorial) agreements are not bundled.
- It does not guess facts: an unstated fact that changes an amount blocks
  payment instead of taking a default.

## Links

- [Documentation](https://lucas-puerari.github.io/ccnl-engine/docs/)
- [Demo](https://lucas-puerari.github.io/ccnl-engine/demo/), in the browser
- [CCNL catalog](https://lucas-puerari.github.io/ccnl-engine/docs/contracts/)
  and [capability matrix](https://lucas-puerari.github.io/ccnl-engine/docs/contracts/capability-matrix/)
- [How reliable is a result](https://lucas-puerari.github.io/ccnl-engine/docs/trust/confidence/)

## License

[MIT](https://github.com/lucas-puerari/ccnl-engine/blob/main/LICENSE). The
figures come from publicly available CCNL tables and statutory rates as of the
dates in the data files: verify them against official sources or a qualified
payroll professional.
