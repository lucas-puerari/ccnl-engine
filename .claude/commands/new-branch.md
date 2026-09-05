# /new-branch — Create a CI-valid branch

## Usage

`/new-branch <type> <slug>`

Examples:
- `/new-branch chore ccnl-chimici-industria`
- `/new-branch fix salary-table-edilizia`
- `/new-branch docs update-readme`

For new contracts, always use `chore` with `{id}-{datoriale}` as slug.

---

## Steps

### 1. Validate the type

Allowed types (CI-enforced by `.github/workflows/branch-name.yml`):

```
feature | fix | chore | ci | docs | refactor | perf | test | revert
```

If the type is not in this list, stop and report the error. Do not create the branch.

### 2. Check for open PRs

```bash
gh pr list --state open
```

If any open PRs are found, warn the user. Per `.claude/commands/new-contract.md`
Step 0, open PRs should be merged before starting new work.

### 3. Sync main and create the branch

```bash
git checkout main
git pull
git checkout -b {type}/{slug}
```

### 4. Confirm and remind

Report the branch name created. Then remind:

**Commit format rules:**
- Format: `<type>(<scope>): <description>` — conventional commits
- Single line only (the git hook rejects multi-line messages)
- Max 100 characters total
- No trailers of any kind: no `Co-authored-by`, no `Signed-off-by`, no AI attribution

Note: branch prefix (`feature/`) and commit type (`feat`) are different — for commits
use `feat`, for branches use `feature/`. The CI validates them independently.

**PR body rules:**
- Must not mention `Claude Code`, `claude.ai`, or `Anthropic`
- PR title must follow conventional commits format
