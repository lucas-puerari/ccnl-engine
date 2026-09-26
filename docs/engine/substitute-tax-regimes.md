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

## Night, holiday and shift supplements

L. 199/2025 art. 1 cc. 10-11: for tax year 2026 the supplements paid for
night work, for work on public holidays and weekly rest days, and for shift
work are taxed at 15% instead of IRPEF and surtaxes, within 1,500 EUR a year.
The regime applies only to private-sector employers ("sostituti d'imposta del
settore privato") and to workers whose 2025 employment income does not exceed
40,000 EUR, unless the worker renounces it in writing. The part above the
annual cap is ordinary income.

| Letter of c. 10 | Pay | Event |
|---|---|---|
| a) | maggiorazioni and indennita for night work (D.Lgs. 66/2003 art. 1 c. 2, CCNL) | `NightShiftEvent` |
| b) | maggiorazioni and indennita for work on public holidays and weekly rest days (CCNL) | `HolidayWorkEvent` |
| c) | indennita di turno and other shift-work pay (CCNL) | `ShiftWorkEvent` |

The three events post the pay item kind `night_holiday_shift_earning`, which
is the one kind the regime covers. Each carries the same facts as the renewal
regime: `prior_income` (2025 employment income) and `substitute_tax_waived`
(written renunciation); the sector comes from the CCNL tax sector.

```python
from datetime import date
from decimal import Decimal

from ccnl_engine.events import HolidayWorkEvent, NightShiftEvent

night = NightShiftEvent(
    event_date=date(2026, 3, 10),
    supplement_amount=Decimal(2_000),
    prior_income=Decimal(20_000),  # 2025 employment income
)
# Substitute tax 1,500 x 15% = 225.00; the other 500 is ordinary income.
holiday = HolidayWorkEvent(
    event_date=date(2026, 3, 1),
    supplement_amount=Decimal(500),
    prior_income=Decimal(20_000),
)
# Alone: 500 x 15% = 75.00.  After the night supplement above, in the same
# run or a later run of 2026: the cap is used up and the 500 is ordinary.
```

### Annual cap account

The used part of the cap is a year-to-date account of the tax year state,
`PayrollState.ytd.work_time_regime` (`RegimeCapAccount.used`). It restarts
at zero when `close_tax_year()` opens the next tax year. Each supplement
gets the substitute rate only on `min(amount, cap - used)`; the rest is
ordinary. The account grows by the eligible amount after every supplement,
within a run and across runs through the closing state, so the cap is shared
by all night, holiday and shift supplements of the tax year. Ineligible and
unknown supplements do not consume the cap. Premi di risultato do not count
toward it (c. 11), since they are a separate pay item kind.

The account rejects a negative used amount. Each decision of a capped regime
records `annual_cap` and `cap_available` (the part of the cap left before
that supplement) among its inputs. The reconciliation invariant
`substitute_tax_plafond` checks that the closing account equals the opening
one plus the eligible amounts of the run and never exceeds the annual cap,
that each decision sees the cap the earlier ones left and takes no more than
it, and that the PdR eligible YTD advances by the `bonus_pdr` decision and
stays within the PdR annual limit. The invariant `substitute_tax_eligibility`
checks that the `SUBSTITUTE_TAX` posted equals the substitute tax of the
decisions, and that a decision that is not `eligible` taxes nothing at the
substitute rate.

### Not modelled

- The activities c. 11 excludes by reference to c. 18 (food and beverage
  service, tourism, thermal establishments): the engine has no fact for the
  employer activity, so the regime is not excluded automatically for them.
- Pay that, although called a supplement, replaces ordinary salary is excluded
  by c. 11; declaring it as a night, holiday or shift event is the caller's
  responsibility.
- The written statement of 2025 income owed when another employer issued the
  2025 certificazione unica is a caller obligation; the engine reads the
  declared `prior_income`.

## Other regimes

The PdR regime (productivity bonus) still uses its dedicated rules
(`PdRRules`); it fails closed to ordinary IRPEF when `prior_income` is not
provided.
