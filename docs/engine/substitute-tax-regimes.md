# Substitute-tax regimes

A preferential regime replaces ordinary IRPEF and the regional and municipal
surtaxes with a flat substitute tax (*imposta sostitutiva*) on the pay items it
covers. The engine models each regime as data (`PreferentialTaxRegime`, read
from `knowledge/tax/data/variable-pay-rules.json`) and checks every covered pay
item against the worker facts of the request before applying it.

## The regime model

| Field | Meaning |
|---|---|
| `regime_id` | Stable identifier, e.g. `rinnovo` |
| `eligible_kinds` | Pay item kinds the regime covers |
| `valid_from_year`, `valid_until_year` | Tax years the regime is in force (tax year of the payment) |
| `flat_tax_rate` | Substitute rate |
| `annual_cap` | Largest amount per tax year at the substitute rate, `null` when uncapped; the excess is ordinary income |
| `income_ceiling`, `income_reference_year` | Largest employment income of the reference year that keeps the worker eligible (the ceiling itself is eligible) |
| `required_sector` | `private` or `public`, `null` when every sector qualifies |
| `waivable` | Whether the worker may renounce the regime in writing |
| `source` | Normative source: document, section and verbatim quote |

## Eligibility decision

Each covered pay item gets one of three outcomes, recorded as a
`CalculationDecision` in `result.decisions` with a stable `reason_code`:

| Outcome | Reason codes | Taxation | Result status |
|---|---|---|---|
| `eligible` | `requirements_met` | substitute rate on the eligible amount, ordinary on any excess over the cap | final |
| `ineligible` | `regime_not_in_force`, `waived_by_worker`, `sector_not_eligible`, `prior_income_above_ceiling` | ordinary | final |
| `unknown` | `sector_unknown`, `prior_income_unknown` | ordinary | provisional |

A definite ineligibility wins over a missing fact: a public-sector worker is
ineligible whatever the prior-year income. An `unknown` outcome also adds a
`CalculationIssue` coded `<regime_id>_eligibility_unknown`, so the result
status becomes `provisional`: the substitute rate is never applied to a worker
who may turn out ineligible, and the amounts change once the missing fact is
provided.

The decision `inputs` hold the normalized facts it was taken from:
`eligibility`, `tax_year`, `prior_income` and `sector` (`unknown` when
missing), `waived`, `eligible_amount` and `ordinary_amount`. Its `amount` is
the substitute tax posted.

## Contract renewal increments (rinnovo)

L. 199/2025 art. 1 c. 7: salary increments paid in 2026 under CCNL renewals
signed from 1 January 2024 to 31 December 2026 are taxed at 5% instead of
IRPEF and surtaxes. The regime applies only to private-sector employees whose
2025 employment income (*reddito di lavoro dipendente*) does not exceed
33,000 EUR, unless the worker renounces it in writing. There is no annual cap.

The facts come from the request:

| Requirement | Input |
|---|---|
| 2025 employment income | `BonusEvent.prior_income`, the same field the PdR regime reads |
| Private sector | the tax sector of the CCNL: a public administration contract (`pubblica-amministrazione`) is public, every other bundled contract is private |
| Written renunciation | `BonusEvent.substitute_tax_waived` |

```python
from datetime import date
from decimal import Decimal

from ccnl_engine.events import BonusEvent

renewal = BonusEvent(
    event_date=date(2026, 3, 10),
    amount=Decimal(2_000),
    kind="contract_renewal",
    prior_income=Decimal(20_000),  # 2025 employment income
)
# Substitute tax 2,000 x 5% = 100.00 on a private-sector CCNL.
# prior_income=Decimal(100_000) or substitute_tax_waived=True: ordinary IRPEF.
# prior_income=None: ordinary IRPEF and a provisional result.
```

The engine does not receive the signing date of a renewal: declaring the
increment as `kind="contract_renewal"` asserts that it falls under a renewal
signed within the window, which the data record as `agreements_signed_from`
and `agreements_signed_until`.

## Other regimes

The PdR regime (productivity bonus) and the night and shift supplement regime
still use their dedicated rules (`PdRRules`, `NotteTurnoRules`); they fail
closed to ordinary IRPEF when `prior_income` is not provided.
