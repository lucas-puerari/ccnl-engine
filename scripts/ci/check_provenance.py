"""Enforce provenance on payable rules and on reference case fixtures.

Two gates judge the payable rules of the bundled knowledge data (see
:mod:`scripts.ci.payable_rules`), rule by rule:

- Schema gate: every payable rule carries a provenance record with a known
  status, ``verified``, ``derived``, ``assumed`` or ``missing``, and every
  record carries the fields its status or readiness requires (see
  :func:`scripts.ci.provenance_evidence.schema_errors`).  A ``missing``
  record is allowed in the data but listed, because the engine marks any
  result that reads it incomplete.
- Evidence gate: a shrink-only ratchet against ``provenance_baseline.json``.
  It fails on an ``assumed`` or ``missing`` rule, an open model limitation
  or a readiness contradiction the baseline does not list, on a rule weaker
  than its baseline status, and on a baseline entry that no longer holds.
  It prints the rules per capability and the CCNL files with the most weak
  rules.

Reference cases: every case in ``tests/fixtures/reference_tables/`` declares a
top-level ``verification`` field, ``verified`` or ``source_linked``, and
carries a non-empty ``source`` object. Expected values produced by the
engine itself are not a status: they detect no systematic error, so such
cases are rejected.

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

Every case mode prints the number of checked cases per verification status.
The script uses the standard library only, so CI can run it without
installing the project.

Usage::

    python scripts/ci/check_provenance.py new.json ...
    python scripts/ci/check_provenance.py --modified changed.json ...
    python scripts/ci/check_provenance.py --schema
    python scripts/ci/check_provenance.py --evidence
    python scripts/ci/check_provenance.py --rules
    python scripts/ci/check_provenance.py --all
    python scripts/ci/check_provenance.py --update-baseline [--allow-growth]

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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ci import payable_rules, provenance_evidence

CASES_DIR = (
    Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "reference_tables"
)
STATUSES = ("verified", "source_linked")


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


def verification_error(case: dict[str, object]) -> str | None:
    """Check the verification status against the ``source`` block.

    Returns:
        The first violated rule, or ``None`` when the case is valid.
    """
    status = case.get("verification")
    if status is None:
        return "missing 'verification' field"
    if status not in STATUSES:
        return f"unknown verification {status!r}; allowed: {list(STATUSES)}"
    source = case.get("source")
    if source is not None and not isinstance(source, dict):
        return "'source' must be a JSON object"
    if not source:
        return f"verification {status!r} requires a non-empty 'source' object"
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
        reason = verification_error(case)
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
    evidence = provenance_evidence.schema_errors(rules, root)
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
            "\nSource the rule with a located citation, resolve the limitation "
            "or align readiness and confidence. If the weak entry is "
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
    contradictions = len(current.readiness_contradictions)
    return (
        f"Weak rules: {rules}; open limitations: {limitations}; "
        f"readiness contradictions: {contradictions}"
    )


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
        "--update-baseline",
        action="store_true",
        help="Rewrite the evidence baseline from the bundle (shrink only).",
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


def main() -> None:
    """Entry point."""
    parser = _parser()
    args = parser.parse_args()
    if args.allow_growth and not args.update_baseline:
        parser.error("--allow-growth requires --update-baseline")

    gates = _gates(args)
    if gates is not None and not args.all:
        sys.exit(0 if gates else 1)
    if args.all:
        paths = sorted(CASES_DIR.glob("*.json"))
        mode = "all"
    elif args.files:
        paths = args.files
        mode = "modified" if args.modified else "new"
    else:
        parser.error("case_file arguments are required without a gate mode")

    failures, counts = check(paths, mode=mode, base=args.base)
    _print_counts(counts)
    if failures:
        _report_failures(failures, mode)
    if failures or gates is False:
        sys.exit(1)
    print(f"OK: {len(paths)} {mode} file(s) checked.")


if __name__ == "__main__":
    main()
