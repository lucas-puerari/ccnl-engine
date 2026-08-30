# ccnl-engine

## Setup

```bash
make setup
```

Attiva i git hooks locali (conventional commits, single-line).

## Commit format

```
<type>(<scope>): <description>
```

Types: `feat` `fix` `docs` `style` `refactor` `perf` `test` `chore` `ci` `build` `revert`

Examples:
```
feat(telemetry): add satellite ping endpoint
fix(auth): handle expired token edge case
chore: update dependencies
```