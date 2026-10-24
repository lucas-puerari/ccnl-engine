"""Enforce provenance on payable rules and on reference case fixtures.

Two gates judge the payable rules of the bundled knowledge data (see
:mod:`scripts.provenance.rules`), rule by rule:

- Schema gate: every payable rule carries a provenance record with a known
  status, ``verified``, ``derived``, ``assumed`` or ``missing``, and every
  record carries the fields its status or readiness requires (see
  :func:`scripts.provenance.evidence.check.schema_errors`).  A ``missing``
  record is allowed in the data but listed, because the engine marks any
  result that reads it incomplete.  No label may outrun its evidence (see
  :mod:`scripts.provenance.label.check`): a ``derived`` or ``verified``
  record that is estimated or cites no source, and a ``reviewed`` or
  ``production`` CCNL with weak rules or an unverified confidence, fail.
- Evidence gate: a shrink-only ratchet against ``baseline.json``.
  It fails on an ``assumed`` or ``missing`` rule or an open model
  limitation the baseline does not list, on a rule weaker than its
  baseline status, and on a baseline entry that no longer holds.
  It prints the rules per capability and the CCNL files with the most weak
  rules.

Reference cases: every case in
``tests/knowledge/ccnl_engine/period/reference_case/`` declares a
top-level ``verification`` field, ``verified`` or ``source_linked``, a
non-empty ``source`` object and the ``axes`` it validates; a ``verified``
case also names the independent output it was checked against (see
:mod:`scripts.provenance.reference_case.check`). Expected values produced
by the engine itself are not a status: they detect no systematic error, so
such cases are rejected.  The schema gate also fails a ``production`` CCNL
that no valid or no ``verified`` reference case runs, and one whose
evidence in the validation matrix misses an output its readiness baseline
does not list (see :mod:`scripts.provenance.readiness.check`).

Modes:

- default (new fixtures): each file must be valid.
- ``--modified``: each file must be valid and must not drop a ``source``
  object it had at ``--base`` (default ``HEAD~1``).
- ``--schema``: the schema gate only.
- ``--evidence``: the evidence gate only.
- ``--rules``: both gates.
- ``--all``: both gates and every case in the fixture directory.
- ``--update-baseline``: rewrite the baseline from the bundle.  It refuses
  a baseline that grows unless ``--allow-growth`` is given.
- ``--index``: print the reference cases of each CCNL as JSON, with the
  readiness of the CCNL, its verification status and axes.
- ``--deadlines``: fail when a CCNL is past its ``review_due``, an accepted
  variance past its ``review_by``, or a file with divergences has no
  owner.  ``--within DAYS`` also fails on the deadlines of the next DAYS
  days.  The quality gates of CI and of the release run it; the weekly
  freshness job runs it with ``--within 60`` to warn ahead of time.

Every case mode prints the number of checked cases per verification status.
The script uses the standard library only, so CI can run it without
installing the project.

Usage::

    python scripts/provenance/check.py new.json ...
    python scripts/provenance/check.py --modified changed.json ...
    python scripts/provenance/check.py --schema
    python scripts/provenance/check.py --evidence
    python scripts/provenance/check.py --rules
    python scripts/provenance/check.py --all
    python scripts/provenance/check.py --update-baseline [--allow-growth]
    python scripts/provenance/check.py --index
    python scripts/provenance/check.py --deadlines [--within DAYS]

Exit codes:
    0   All checks pass.
    1   One or more checks fail.
"""

from __future__ import annotations

import argparse
import json
import subprocess  # noqa: S404
import sys
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.provenance import rules as payable_rules
from scripts.provenance.evidence import check as provenance_evidence
from scripts.provenance.label import check as provenance_labels
from scripts.provenance.readiness import check as readiness_matrix
from scripts.provenance.reference_case import check as reference_cases
from scripts.provenance.reference_case.check import (
    CASES_DIR,
    STATUSES,
    verification_errors,
)
from scripts.provenance.replay import check as replays


def _parse(text: str) -> dict[str, object] | None:
    data: object = json.loads(text)
    return data if isinstance(data, dict) else None


def _load(path: Path) -> dict[str, object] | None:
    try:
        return _parse(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return None


def _load_at(ref: str, path: Path) -> dict[str, object] | None:
    """Read the case as it was at git ``ref``.

    Returns:
        The decoded case, or ``None`` if it did not exist or was invalid.
    """
    result = subprocess.run(  # noqa: S603
        ["git", "show", f"{ref}:{path.as_posix()}"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        return _parse(result.stdout)
    except json.JSONDecodeError:
        return None


def check(
    paths: list[Path], *, mode: str, base: str
) -> tuple[list[tuple[Path, str]], Counter[str]]:
    """Validate ``paths`` under ``mode``.

    Returns:
        ``(failures, counts)``: failing ``(path, reason)`` pairs and the
        number of readable cases per verification status.
    """
    failures: list[tuple[Path, str]] = []
    counts: Counter[str] = Counter()
    for path in paths:
        case = _load(path)
        if case is None:
            failures.append((path, "unreadable or not a JSON object"))
            continue
        counts[str(case.get("verification"))] += 1
        reason = "; ".join(verification_errors(case)) or None
        if reason is None and mode == "modified":
            previous = _load_at(base, path)
            if previous and previous.get("source") and not case.get("source"):
                reason = f"lost 'source' object present at {base}"
        if reason is not None:
            failures.append((path, reason))
    return failures, counts


def _print_counts(counts: Counter[str]) -> None:
    total = sum(counts.values())
    print(f"Reference cases checked: {total}")
    for status in STATUSES:
        print(f"  {status}: {counts[status]}")
    other = total - sum(counts[status] for status in STATUSES)
    if other:
        print(f"  invalid or missing: {other}")


def check_rules(root: Path = payable_rules.KNOWLEDGE_DIR) -> bool:
    """Check the payable rules of the bundle and print their statuses.

    Args:
        root: Knowledge directory to scan.

    Returns:
        ``True`` when every payable rule has a record with a known status.
    """
    rules = payable_rules.inventory(root)
    counts = payable_rules.count_by_status(rules)
    print(f"Payable rules checked: {len(rules)}")
    for status in payable_rules.STATUSES:
        print(f"  {status}: {counts[status]}")
    missing = [rule for rule in rules if rule.status == "missing"]
    for rule in missing:
        print(f"  missing source: {rule.file}: {rule.path}")
    errors = payable_rules.rule_errors(rules)
    if errors:
        print(
            f"\n{len(errors)} payable rule(s) without a provenance record:\n"
            + "\n".join(f"  {error}" for error in errors),
            file=sys.stderr,
        )
        print(
            "\nGive each rule a 'provenance' record with a 'status'; use "
            '"missing" when no source backs the value.',
            file=sys.stderr,
        )
    evidence = [
        *provenance_evidence.schema_errors(rules, root),
        *provenance_labels.label_errors(root),
        *provenance_labels.readiness_errors(rules, root),
        *reference_cases.production_errors(root),
        *(
            [
                *readiness_matrix.readiness_errors(),
                *replays.record_errors(datetime.now(tz=UTC).date()),
            ]
            if root == payable_rules.KNOWLEDGE_DIR
            else ()
        ),
    ]
    if evidence:
        print(
            f"\n{len(evidence)} record(s) without the evidence they claim:\n"
            + "\n".join(f"  {error}" for error in evidence),
            file=sys.stderr,
        )
    return not errors and not evidence


def _print_ratchet(ratchet: provenance_evidence.Ratchet) -> None:
    if ratchet.grown:
        print(
            f"\n{len(ratchet.grown)} weak evidence entry(ies) the baseline "
            "does not allow:\n" + "\n".join(f"  {e}" for e in ratchet.grown),
            file=sys.stderr,
        )
        print(
            "\nSource the rule with a located citation or resolve the "
            "limitation. If the weak entry is "
            "intended, run --update-baseline --allow-growth and justify it "
            "in the pull request.",
            file=sys.stderr,
        )
    if ratchet.stale:
        print(
            f"\n{len(ratchet.stale)} baseline entry(ies) no longer hold:\n"
            + "\n".join(f"  {e}" for e in ratchet.stale),
            file=sys.stderr,
        )
        print("\nRun --update-baseline to shrink the baseline.", file=sys.stderr)


def _summary(current: provenance_evidence.Snapshot) -> str:
    rules = sum(len(paths) for paths in current.weak_rules.values())
    limitations = sum(len(ids) for ids in current.open_limitations.values())
    return f"Weak rules: {rules}; open limitations: {limitations}"


def check_evidence(
    root: Path = payable_rules.KNOWLEDGE_DIR,
    baseline: Path = provenance_evidence.BASELINE,
) -> bool:
    """Compare the weak evidence of the bundle with the baseline.

    Args:
        root: Knowledge directory to scan.
        baseline: Baseline file.

    Returns:
        ``True`` when the bundle matches the baseline exactly.
    """
    rules = payable_rules.inventory(root)
    current = provenance_evidence.snapshot(root, rules)
    print("\n".join(provenance_evidence.report_lines(rules)))
    print(_summary(current))
    try:
        stored = provenance_evidence.load_baseline(baseline)
    except (OSError, ValueError, TypeError) as exc:
        print(f"ERROR: cannot read baseline {baseline}: {exc}", file=sys.stderr)
        return False
    ratchet = provenance_evidence.compare(current, stored)
    _print_ratchet(ratchet)
    return ratchet.ok


def update_baseline(
    root: Path = payable_rules.KNOWLEDGE_DIR,
    baseline: Path = provenance_evidence.BASELINE,
    *,
    allow_growth: bool = False,
) -> bool:
    """Rewrite the baseline from the bundle.

    Args:
        root: Knowledge directory to scan.
        baseline: Baseline file to write.
        allow_growth: Accept entries the current baseline does not list;
            required to create the baseline.

    Returns:
        ``True`` when the baseline was written.
    """
    current = provenance_evidence.snapshot(root)
    try:
        grown = provenance_evidence.compare(
            current, provenance_evidence.load_baseline(baseline)
        ).grown
    except (OSError, ValueError, TypeError) as exc:
        grown = (f"no readable baseline ({exc})",)
    if grown and not allow_growth:
        print(
            "Refusing to grow the baseline without --allow-growth:\n"
            + "\n".join(f"  {entry}" for entry in grown),
            file=sys.stderr,
        )
        return False
    provenance_evidence.write_baseline(current, baseline)
    print(f"Wrote {baseline}. {_summary(current)}")
    return True


def check_deadlines(
    root: Path = payable_rules.KNOWLEDGE_DIR,
    today: date | None = None,
    within: int = 0,
) -> bool:
    """Print the deadlines of the bundle that are overdue or due ``within`` days.

    Returns:
        ``True`` when nothing is overdue or due.
    """
    day = today or datetime.now(tz=UTC).date()
    errors = provenance_evidence.deadline_errors(root, day, within)
    for error in errors:
        print(f"  {error}", file=sys.stderr)
    print(f"Deadlines checked on {day} within {within} days: {len(errors)} found.")
    return not errors


def print_index(root: Path = payable_rules.KNOWLEDGE_DIR) -> None:
    """Print each CCNL with its readiness and reference cases, as JSON."""
    cases = reference_cases.index()
    readiness = provenance_evidence.readiness_by_ccnl(root)
    ids = sorted(set(cases) | set(readiness))
    print(
        json.dumps(
            {
                ccnl: {
                    "readiness": readiness.get(ccnl),
                    "reference_cases": [c.to_json() for c in cases.get(ccnl, ())],
                }
                for ccnl in ids
            },
            indent=2,
        )
    )


def _parser() -> argparse.ArgumentParser:
    """Return the command-line parser.

    Returns:
        The parser of the modes, the base ref and the case files.
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--modified",
        action="store_true",
        help="Check modified fixtures: valid status, no source removed.",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help=f"Check the payable rules and every case in {CASES_DIR}.",
    )
    group.add_argument(
        "--rules",
        action="store_true",
        help="Run the schema and evidence gates on the payable rules.",
    )
    group.add_argument(
        "--schema",
        action="store_true",
        help="Run the schema gate: records and the evidence they claim.",
    )
    group.add_argument(
        "--evidence",
        action="store_true",
        help="Run the evidence gate: the shrink-only weak evidence ratchet.",
    )
    group.add_argument(
        "--deadlines",
        action="store_true",
        help="Fail on an overdue review, an overdue accepted variance or an "
        "unowned divergence.",
    )
    group.add_argument(
        "--index",
        action="store_true",
        help="Print the reference cases of each CCNL as JSON.",
    )
    group.add_argument(
        "--update-baseline",
        action="store_true",
        help="Rewrite the evidence baseline from the bundle (shrink only).",
    )
    parser.add_argument(
        "--within",
        type=int,
        default=0,
        metavar="DAYS",
        help="With --deadlines, also fail on the deadlines of the next DAYS days.",
    )
    parser.add_argument(
        "--allow-growth",
        action="store_true",
        help="With --update-baseline, accept new weak evidence entries.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=provenance_evidence.BASELINE,
        help="Evidence baseline file (default: %(default)s).",
    )
    parser.add_argument(
        "--base",
        default="HEAD~1",
        help="Git ref to compare modified fixtures against (default: HEAD~1).",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        metavar="case_file",
        help="Reference case JSON files to check.",
    )
    return parser


def _gates(args: argparse.Namespace) -> bool | None:
    """Run the rule gates the arguments select.

    Returns:
        Whether they pass, or ``None`` when the mode runs none.
    """
    if args.update_baseline:
        return update_baseline(baseline=args.baseline, allow_growth=args.allow_growth)
    schema = args.schema or args.rules or args.all
    evidence = args.evidence or args.rules or args.all
    if not (schema or evidence):
        return None
    schema_ok = check_rules() if schema else True
    evidence_ok = check_evidence(baseline=args.baseline) if evidence else True
    return schema_ok and evidence_ok


def _report_failures(failures: list[tuple[Path, str]], mode: str) -> None:
    print(
        f"\n{len(failures)} {mode} reference case(s) failed provenance check:\n"
        + "\n".join(f"  {p}: {reason}" for p, reason in failures),
        file=sys.stderr,
    )
    print(
        "\nEach case needs a top-level 'verification' field. Example:\n"
        '  "verification": "source_linked",\n'
        '  "source": {\n'
        '    "document": "CCNL ...",\n'
        '    "url": "https://...",\n'
        '    "section": "Art. ...",\n'
        '    "notes": "Expected values computed by the engine"\n'
        "  }",
        file=sys.stderr,
    )


def _report(args: argparse.Namespace) -> None:
    """Run a report mode, ``--index`` or ``--deadlines``, and exit.

    Raises:
        SystemExit: Always, with status 1 when a deadline is overdue.
    """
    if args.index:
        print_index()
        raise SystemExit(0)
    raise SystemExit(0 if check_deadlines(within=args.within) else 1)


def _case_paths(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> tuple[list[Path], str]:
    """Return the reference cases the arguments select and their mode.

    Returns:
        Every case under ``--all``, else the files given, new or modified.
    """
    if args.all:
        return sorted(CASES_DIR.glob("*.json")), "all"
    if not args.files:
        parser.error("case_file arguments are required without a gate mode")
    return list(args.files), "modified" if args.modified else "new"


def main() -> None:
    """Entry point."""
    parser = _parser()
    args = parser.parse_args()
    if args.allow_growth and not args.update_baseline:
        parser.error("--allow-growth requires --update-baseline")
    if args.within and not args.deadlines:
        parser.error("--within requires --deadlines")
    if args.within < 0:
        parser.error("--within must not be negative")

    if args.index or args.deadlines:
        _report(args)
    gates = _gates(args)
    if gates is not None and not args.all:
        sys.exit(0 if gates else 1)
    paths, mode = _case_paths(args, parser)
    failures, counts = check(paths, mode=mode, base=args.base)
    _print_counts(counts)
    if failures:
        _report_failures(failures, mode)
    if failures or gates is False:
        sys.exit(1)
    print(f"OK: {len(paths)} {mode} file(s) checked.")


if __name__ == "__main__":
    main()
