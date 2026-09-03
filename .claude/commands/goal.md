# /goal — Multi-session goal: add N new CCNLs to the repo

This project uses a git-history-based goal system, not the LLM evaluation of the built-in `/goal`.

A project-local Stop hook counts `feat(...): add CCNL ...` commits on main after each turn.
The goal is reached when enough of them exist beyond the baseline.
State persists in `.claude/GOAL.md` (local, not committed) — it works across sessions.

---

## Set a new goal

If the user has specified how many contracts to add (e.g. `/goal 5`):

1. Count the current baseline (source of truth: contract JSON files):
   ```bash
   ls src/ccnl_engine/contracts/data/*.json | grep -v '__init__' | wc -l
   ```

2. Create `.claude/GOAL.md`:
   ```markdown
   ---
   status: active
   baseline: <number counted in step 1>
   target: <N requested by the user>
   created: <ISO date>
   ---

   Add <N> new CCNLs to the repo following the process in `.claude/commands/new-contract.md`.

   Each contract must:
   - Be merged to main via PR
   - Have a commit with the format: `feat(<slug>): add CCNL <name> (<code>) payroll engine`
   - Appear in `git log main --oneline`

   Proceed in order, one contract at a time. Choose those with the highest number of covered workers not yet present in the repo.
   ```

3. Start working immediately following `/new-contract`.

---

## Show status (no argument)

Read `.claude/GOAL.md` and display:
- `status`, `baseline`, `target`
- Current count: `git log main --oneline | grep -c "feat(.*): add CCNL"`
- How many added and how many remain

---

## Clear goal (`/goal clear`)

Update `status: cancelled` in `.claude/GOAL.md`.

---

## Constraints

- Do not create an explicit "goal done" commit — completion is detected automatically by the Stop hook counting feat commits.
- Do not declare the goal complete until `git log main` shows the expected commits.
- Always use `/new-contract` to add each individual CCNL.
