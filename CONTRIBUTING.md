# Contributing

## PR and commit conventions

### Commit message format

```
<type>(<scope>): <description> (#<PR>)
```

- `type`: `feat` | `fix` | `refactor` | `chore` | `docs`
- `scope`: kebab-case slug matching the contract filename (for CCNL additions) or the affected package/subsystem (e.g. `core`, `ci`, `hooks`)
- `(#<PR>)`: GitHub PR number appended by the squash-merge

Examples:
```
feat(metalmeccanico-federmeccanica): add CCNL Metalmeccanici e Installatori di Impianti (C011) payroll engine (#2)
refactor(core): ergonomics, validation fixes, and project structure (#14)
chore(ci): enforce branch naming and strip AI tool trailers (#1)
```

> **Transition note**: commits before PR #1 (sha prefixes `e42976b`, `f2b42ba`, `7764afa`, `ce2f7ba`) predate the PR workflow and do not carry a `(#N)` trailer. All subsequent commits do.

### PR body structure

Every PR must use the following four-section structure, in English:

```markdown
## What
<bullet list of files added or changed>

## Why
<business context: sector, worker count, CNEL code, agreement date>

## How
<technical implementation: salary model, divisor, seniority, apprenticeship, simplifications>

## Verification
<N tests passed, 100% branch coverage, ruff clean, mypy strict>
```

### Branch naming

```
chore/<contract-slug>     # for new CCNL additions
fix/<short-description>   # for bug fixes or patches
docs/<short-description>  # for documentation-only changes
```

Direct pushes to `main` are blocked by the pre-push hook. All changes go through PRs.

## Adding a new CCNL

Follow the `/new-contract` skill — it codifies the full research, implementation, test, and PR workflow.


## Git history normalization (one-time)

In September 2026, a `git filter-repo` pass rewrote 15 early commits to:
- Add `(#N)` trailer to all commits that had a corresponding PR but lacked the reference
- Fix scope slugs (`metalmeccanico` → `metalmeccanico-federmeccanica`, `turismo` → `turismo-confcommercio`, etc.)
- Align CCNL names and codes with the standardized PR titles set in PR #38
- Add `payroll engine` suffix where missing

Commits before PR #1 (`091533f`, `3587bc4`, `d99fc29`) predate the PR workflow and intentionally have no `(#N)` trailer.
