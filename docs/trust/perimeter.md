# Perimeter and tolerance

What an adopter compares when it runs ccnl-engine next to its own payroll:
which amounts the engine owns, which the adopter adds, and how close two
amounts must be to count as the same. A comparison that ignores this page
reports differences that are not errors, or hides errors as rounding.

## What the engine owns

The eight totals of the definition of done (see
[Validation packets](validation-packet.md)): base salary, gross, employee
and employer INPS contributions, tax (IRPEF and surtaxes withheld in the
run), net, TFR accrual and employer cost, each with the perimeter its
packet output states.

## What the adopter adds

The engine does not compute these; the
[capability matrix](../contracts/capability-matrix.md) lists them as
unsupported or outside the input. A comparison takes them out of the
provider's figures, or adds them to the engine's, before comparing:

| Item | Effect on the totals |
|---|---|
| INAIL premium | Employer cost |
| Contribution exemptions and hiring incentives | Employer contributions, employer cost |
| Supplementary health funds | Gross or net (employee share), employer cost |
| Contractual una tantum | Gross, contributions, tax, net |
| Personal withholdings (garnishments, salary-backed loans) | Net only |
| Conguaglio of a 730 or of other withholding agents | Tax, net |
| Art. 15 TUIR deductions | Tax, net |
| Rounding of the net to the euro | Net only |

Company and territorial elements are not in that list: state them as
`SecondLevelElement` on the employer (see
[Second-level bargaining](../engine/second-level.md)) and the engine pays
them; their amounts rest on the adopter.

## Tolerance

| Amount | Tolerance |
|---|---|
| Base salary and fixed allowances of the tables | 0.00 EUR |
| Each line of contributions and tax | 0.01 EUR, with the rounding the packet declares (`half_up_cents`, `half_even_cents`, `truncate_cents`, `whole_euro`) |
| Totals | The sum of the tolerances of their lines |
| Net | Compared before the rounding of the net to the euro |

A difference above the tolerance is an engine bug or an error of the other
output. It is never accepted as rounding or as an "explained variance"
without a cited source and a dated review: the packet records
`explained_difference` only with its explanation, and the review that
closes it (see [Readiness](readiness.md#review-log)).
