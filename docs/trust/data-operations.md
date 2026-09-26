# Data operations policy

This page documents how CCNL and statutory data is kept current, how errors
are corrected, and what compatibility guarantees the knowledge base provides.

---

## Ruleset states

Every CCNL ruleset is classified by two orthogonal signals:

| Signal | Field | Values | Meaning |
|---|---|---|---|
| Readiness | `verification.readiness` | `exploratory` / `reviewed` / `production` | Whether the ruleset has been human-reviewed for a given use context |
| Verification | `verification.status` | `unverified` / `verified` / `needs_review` | Per-value data verification of the source values; not folded into the result, whose reliability is `result.status` |

See [Readiness](readiness.md) for promotion criteria between tiers and the
current classification of each contract.

---

## Update targets (non-binding)

The following are engineering targets, not contractual SLAs.

| Event | Target update window |
|---|---|
| CCNL renewal published | Within 60 days of the official signing date |
| Salary table update (mid-agreement tranche) | Within 30 days of the effective date |
| IRPEF bracket / deduction change | Within 14 days of the Gazzetta Ufficiale publication |
| INPS rate change | Within 14 days of the INPS circular |

When a renewal is in progress but not yet modelled, the active ruleset's
`effective_until` is left open and a `needs_review` flag is set on the
affected salary table values.

---

## Changelog and economic diff

Every dataset release ships a `CHANGELOG.md` at the repository root.
Entries follow the format:

```
## [<version>] — <date>

### CCNL <name> (<CNEL code>)
- Salary table updated: effective from <date>
  - Level 3: 1 850,00 → 1 920,00 EUR/month (+70,00)
  - ...
```

The diff is expressed in absolute EUR values for salary table entries and
as percentage points for rate changes (INPS, IRPEF). This makes it possible
to assess the economic impact of a knowledge-base update without running
simulations.

Programmatic consumers can parse the changelog or watch GitHub releases,
which carry the same information as release notes.

---

## Reporting errors

To report a data error (wrong salary value, missing allowance, incorrect rate):

1. Open a GitHub issue with the label `data-error`.
2. Include: the CCNL name, the CNEL code, the incorrect value, the correct
   value, and a link to the authoritative source (CCNL text, official table,
   or Gazzetta Ufficiale).
3. Critical corrections (value wrong by more than 5%) are prioritised over
   the standard update window.

For errors in statutory rates (IRPEF, INPS) that affect many contracts,
open an issue with the label `statutory-rate-error`.

---

## Deprecation and version compatibility

**Knowledge-base versions** follow `YYYY.N` (e.g. `2026.2`). Every
`PeriodResult` and `YearResult` records the version in `bundle_version`, and
each decision names the ruleset it applied (`rule`, `rule_version`), so any
figure can be reproduced by pinning that version.

**Deprecation policy:**

- A knowledge-base version is supported for as long as the matching
  `ccnl-engine` package release is on PyPI.
- When a CCNL is removed (contract terminated or superseded), it is marked
  `effective_until` in its last dataset version and absent from the next.
- No breaking changes to the JSON schema are introduced within a minor
  knowledge-base release. Schema changes are announced in the changelog
  and in a GitHub discussion at least 30 days before they take effect.

**Engine API compatibility:**

The Python API follows semantic versioning. Patch releases are backwards
compatible. Minor releases may add fields to `PeriodResult` or new values
to existing enums (callers must handle unknown values defensively). Major
releases may break the public API and will be announced with a migration
guide.
