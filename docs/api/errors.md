# Errors

Every error the engine raises for an input, a data gap or a bundle defect
is a `CcnlEngineError` exported at the root, with a stable `code` (one of
`ccnl_engine.errors.PUBLIC_ERROR_CODES`), the `feature` and the `ruleset` it concerns and a
`remediation`. None of them is a `ValueError`: catch `CcnlEngineError`, or
one of its subclasses.

| Error | `code` | Raised when |
|---|---|---|
| `InvalidInputError` | `invalid_input` | An input or a facade argument is not what it must be; `field` names it, e.g. `"PeriodFacts.events[2]"` or `"Employment.roles['x']"` |
| `UnknownCcnlError` | `unknown_ccnl` | The CCNL slug or code is not in the bundle |
| `UnknownLevelError` | `unknown_level` | The level code is not a level of the CCNL |
| `MissingRuleError` | `missing_rule` | The bundle has no value of a rule on the date a run reads it |
| `MissingRequiredFactError` | `missing_required_fact` | A computation path needs a fact the caller did not supply |
| `UnsupportedTaxYearError` | `unsupported_tax_year` | The bundle has no tax tables for the tax year of the payment |
| `OutOfScopeError` | `out_of_scope` | The engine does not model the requested computation |
| `DataIntegrityError` | `data_integrity` | A bundled file fails an integrity check, or a run breaks a state invariant |

Inputs are frozen dataclasses validated on construction by shared
validators: scalars by type and range (`Decimal` amounts finite and below
`1E+9` in magnitude, `int` fields never a `bool`, dates never a
`datetime`, enums as a member or its string value), collections element by
element and stored as tuples or frozensets once valid. A missing fact that
lowers a result is a `CalculationIssue` whose `fact` is the name of the
public field to set (`seniority`, `contribution_history`, `sector`,
`activity`, `agreement_signed_on`, `employment_income`).

::: ccnl_engine.CcnlEngineError

::: ccnl_engine.DataIntegrityError

::: ccnl_engine.InvalidInputError

::: ccnl_engine.MissingRequiredFactError

::: ccnl_engine.MissingRuleError

::: ccnl_engine.OutOfScopeError

::: ccnl_engine.UnknownCcnlError

::: ccnl_engine.UnknownLevelError

::: ccnl_engine.UnsupportedTaxYearError
