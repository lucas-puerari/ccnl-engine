# /batch — Add N CCNLs in one continuous session

Uses a Stop hook to prevent the session from ending between contracts.
Progress is tracked in `.claude/GOAL.md` (local, not committed).

---

## Usage

- `/batch N` — start a new batch: add N CCNLs sequentially, one at a time
- `/batch resume` — resume an interrupted batch
- `/batch status` — show progress
- `/batch clear` — cancel the active batch

---

## Start: `/batch N`

1. Count the current baseline (source of truth — contract JSON files):
   ```bash
   ls src/ccnl_engine/contracts/data/*.json | grep -v '__init__' | wc -l
   ```

2. Create `.claude/GOAL.md`:
   ```
   ---
   status: active
   baseline: <number from step 1>
   target: <N>
   started: <ISO date>
   ---

   Add <N> new CCNLs following `.claude/commands/new-contract.md`.
   Proceed in order, one contract at a time. Choose those with the highest
   number of covered workers not yet present in the repo.
   ```

3. Begin the loop immediately. For each contract:
   - Follow every step in `.claude/commands/new-contract.md` exactly.
   - After the PR is merged and main is synced, proceed to the next contract.
   - Do not stop or wait for user input between contracts.

4. When all N contracts are merged, update `status: done` in `.claude/GOAL.md`
   and report completion.

---

## Resume: `/batch resume`

1. Read `.claude/GOAL.md`. If missing or `status` is `done` or `cancelled`,
   report that there is nothing to resume.

2. Count current contracts:
   ```bash
   ls src/ccnl_engine/contracts/data/*.json | grep -v '__init__' | wc -l
   ```

3. Check for open PRs — a contract may be in flight:
   ```bash
   gh pr list --state open
   ```
   If a PR is open, merge it first before counting.

4. Compute: `remaining = (baseline + target) - current`.
   If `remaining <= 0`, update `status: done` and report.

5. Continue the loop for the remaining contracts (same rules as Start).

---

## Status: `/batch status`

Read `.claude/GOAL.md`, count current JSON files, and report:
- Baseline, target, current count
- Contracts added so far, remaining

---

## Clear: `/batch clear`

Set `status: cancelled` in `.claude/GOAL.md`.

---

## Constraints

- Source of truth for progress: `ls src/ccnl_engine/contracts/data/*.json | grep -v '__init__' | wc -l`.
- Follow `.claude/commands/new-contract.md` exactly for each iteration.
- Never push directly to `main`.
- The Stop hook re-injects this goal automatically after each contract; do not
  wait for user instructions between iterations.
