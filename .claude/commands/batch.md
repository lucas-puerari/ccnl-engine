# /batch — Repeat a command N times without stopping

Runs a sub-command N times in sequence, tracking progress in `.claude/GOAL.md`.
A Stop hook prevents the session from ending between iterations.

---

## Usage

- `/batch N <command> [progress_cmd]` — start a batch (classic mode)
- `/batch <command> <code1> <code2> ...` — start a queue batch (see below)
- `/batch resume` — resume an interrupted batch
- `/batch status` — show progress
- `/batch clear` — cancel the active batch

`progress_cmd` is a bash one-liner that outputs the current count of completed
items (integer). If omitted and `command` is a known project command, use its
default (see below). If unknown, ask the user for a progress_cmd before starting.

### Known defaults

| command | default progress_cmd |
|---------|---------------------|
| `/new-contract` | `ls src/ccnl_engine/contracts/data/*.json \| grep -v '__init__' \| wc -l` |

---

## Queue mode: `/batch <command> <item1> <item2> ...`

Use this form when you have an explicit ordered list of items to process and
the sub-command knows how to pick the next item from the queue.

The queue is embedded directly in GOAL.md — no separate file. The Stop hook
re-injects GOAL.md on every session restart, so the list is always in context.

Steps:

1. Parse the list of items after the command name. Set `N` = count of items.

2. Set `progress_cmd` = `grep -cE '^\- \[(x|B)\]' .claude/GOAL.md`.

3. Create `.claude/GOAL.md`:
   ```
   ---
   status: active
   baseline: 0
   target: <N>
   command: <command>
   progress_cmd: grep -cE '^\- \[(x|B)\]' .claude/GOAL.md
   started: <ISO date>
   ---

   Process each item below in order. Update its status before moving on.
   [ ] = to do | [~] = in progress | [x] = done | [B] = blocked

   - [ ] <item1>
   - [ ] <item2>
   ...
   ```

4. Invoke `<command>` immediately. After each iteration completes, proceed to
   the next without waiting for user input. The Stop hook re-injects this goal
   automatically — do not stop voluntarily between iterations.

5. When `progress_cmd` returns `N`, update `status: done` and report completion.

---

## Start: `/batch N <command>`

1. Run `progress_cmd` to get the current baseline count.

2. Create `.claude/GOAL.md`:
   ```
   ---
   status: active
   baseline: <count from step 1>
   target: <N>
   command: <command>
   progress_cmd: <progress_cmd>
   started: <ISO date>
   ---

   Run <command> <N> times, one at a time, without stopping between iterations.
   ```

3. Invoke `<command>` immediately. After each iteration completes, proceed to
   the next without waiting for user input. The Stop hook re-injects this goal
   automatically — do not stop voluntarily between iterations.

4. When `progress_cmd` returns `baseline + target`, update `status: done` and
   report completion.

---

## Resume: `/batch resume`

1. Read `.claude/GOAL.md`. If missing or `status` is `done` or `cancelled`,
   report that there is nothing to resume.

2. Run `progress_cmd` to get the current count.

3. Compute: `remaining = (baseline + target) - current`.
   If `remaining <= 0`, update `status: done` and report.

4. Continue the loop for the remaining iterations.

---

## Status: `/batch status`

Read `.claude/GOAL.md`, run `progress_cmd`, and report:
- command, baseline, target, current count
- iterations completed, remaining

---

## Clear: `/batch clear`

Set `status: cancelled` in `.claude/GOAL.md`.
