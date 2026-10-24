r"""Build the validation dossier a release attaches to itself.

A release is validated by evidence spread over CI jobs, workflow artifacts
that expire, and files of the repository.  The dossier gathers it, for the
commit the release publishes, in one machine-readable file and one page a
person reads, both attached to the GitHub release so they outlive the CI:

- identity: commit, version, SHA-256 of ``uv.lock`` and of the knowledge
  manifest (the bundle);
- gates: the outcome of each job the release waited for (tests with 100%
  coverage, types, lint, SAST, dependency audit, build and smoke tests);
- mutation: the score of the full campaign on the same commit, refused
  when it measured another commit or another perimeter;
- evidence: the ``(ccnl, output, independence)`` coverage of each
  ``production`` CCNL, the baselines and exceptions still open, the
  deadlines of the next 60 days and the staleness of the bundle;
- known differences: every divergence closed as an accepted variance, with
  its owner and review date;
- gold cases: the verified reference cases and the validation packets, with
  the provider of each;
- sign-off: the CCNLs a person signed off, and the AI reviews.

The script reads raw JSON with the standard library only.

Run with::

    python scripts/distribution/dossier/generate.py --gate gates=success \\
        --gate mutation=success --mutation mutants/mutation-score.json \\
        --out dist/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess  # noqa: S404
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.documentation.validation_matrix.generate import INDEPENDENCE, matrix
from scripts.provenance.evidence.check import deadline_errors
from scripts.provenance.readiness.check import load_baseline
from scripts.provenance.reference_case.check import AXES, index
from scripts.provenance.rules import KNOWLEDGE_DIR
from scripts.provenance.staleness.report import staleness
from scripts.provenance.validation_packet.check import PACKETS_DIR
from scripts.quality.mutation.check import (
    EQUIVALENT,
    RECORD,
    load_floors,
    source_paths,
)

ROOT: Final = Path(__file__).resolve().parents[3]
#: Days ahead the dossier lists deadlines and staleness for.
HORIZON_DAYS: Final = 60

Json = dict[str, Any]


class DossierError(ValueError):
    """The evidence does not belong to the commit the release publishes."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    ).stdout.strip()


def identity(commit: str) -> Json:
    """Return what the release is: commit, version and the hashes it pins.

    Returns:
        The identity section.
    """
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return {
        "commit": commit,
        "version": project["project"]["version"],
        "uv_lock_sha256": _sha256(ROOT / "uv.lock"),
        "bundle_manifest_sha256": _sha256(KNOWLEDGE_DIR / "manifest.json"),
    }


def mutation(record: Json, commit: str) -> Json:
    """Return the mutation section, from the campaign of the same commit.

    Returns:
        The commit, perimeter, minimum, scores and equivalents of the campaign.

    Raises:
        DossierError: When the campaign measured another commit or another
            perimeter.
    """
    if record.get("commit") != commit:
        msg = f"mutation campaign of {record.get('commit')}, not of {commit}"
        raise DossierError(msg)
    if record.get("perimeter") != list(source_paths()):
        msg = "mutation campaign perimeter differs from [tool.mutmut] source_paths"
        raise DossierError(msg)
    equivalent = json.loads(EQUIVALENT.read_text(encoding="utf-8"))["mutants"]
    return {
        "commit": record["commit"],
        "date": record["date"],
        "min_score": record["min_score"],
        "perimeter": record["perimeter"],
        "scores": record["scores"],
        "floors": load_floors(),
        "equivalent_mutants": len(equivalent),
    }


def evidence() -> Json:
    """Return the per-output coverage of each production CCNL and what is open.

    Returns:
        Coverage, baselines, deadlines and staleness.
    """
    rows = matrix()
    coverage = {
        ccnl: {
            output: max(row.outputs[output], key=INDEPENDENCE.index)
            if output in row.outputs
            else None
            for output in AXES
        }
        for ccnl, row in rows.items()
        if row.readiness == "production"
    }
    readiness = {
        level: {ccnl: sorted(axes) for ccnl, axes in gaps.items()}
        for level, gaps in load_baseline().items()
    }
    weak = json.loads((ROOT / "scripts/provenance/baseline.json").read_text("utf-8"))
    today = datetime.now(tz=UTC).date()
    return {
        "production_coverage": coverage,
        "readiness_baseline": readiness,
        "weak_rules_baseline": sum(len(v) for v in weak["weak_rules"].values()),
        "open_limitations_baseline": sum(
            len(v) for v in weak["open_limitations"].values()
        ),
        "deadlines": deadline_errors(KNOWLEDGE_DIR, today, HORIZON_DAYS),
        "staleness": [
            f"{f.file}: {f.reason}" for f in staleness(today=today, within=HORIZON_DAYS)
        ],
    }


def _agreements() -> list[tuple[str, Json]]:
    return [
        (path.stem, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted((KNOWLEDGE_DIR / "agreement").glob("*.json"))
    ]


def known_differences() -> list[Json]:
    """Return every accepted variance of the review logs, with its owner.

    Returns:
        One entry per accepted variance.
    """
    found: list[Json] = []
    for ccnl, data in _agreements():
        verification = data.get("verification") or {}
        for review in verification.get("reviews") or []:
            found.extend(
                {
                    "ccnl": ccnl,
                    "subject": divergence.get("subject"),
                    "cause": divergence.get("cause"),
                    "owner": verification.get("owner"),
                    "review_by": divergence.get("review_by"),
                }
                for divergence in review.get("divergences") or []
                if divergence.get("decision") == "accepted_external_variance"
            )
    return found


def gold_cases() -> Json:
    """Return the verified reference cases and the validation packets.

    Returns:
        Each verified case by CCNL, and each packet with its artifact kind
        and provider.
    """
    verified = {
        ccnl: [c.file for c in cases if c.verification == "verified"]
        for ccnl, cases in index().items()
    }
    packets = []
    for path in sorted(PACKETS_DIR.glob("*.json")):
        packet = json.loads(path.read_text(encoding="utf-8"))
        packets.append({
            "packet": path.stem,
            "kind": packet["artifact"]["kind"],
            "provider": packet["versions"].get("provider"),
        })
    return {
        "verified_reference_cases": {c: n for c, n in verified.items() if n},
        "validation_packets": packets,
    }


def sign_off() -> Json:
    """Return who reviewed the CCNLs: people independent of the extraction, or AI.

    Returns:
        The CCNLs with a human sign-off and the count of AI reviews.
    """
    human, ai = [], 0
    for ccnl, data in _agreements():
        reviews = (data.get("verification") or {}).get("reviews") or []
        if any(r.get("independence") == "human" for r in reviews):
            human.append(ccnl)
        ai += sum(r.get("reviewer_kind") == "ai" for r in reviews)
    return {"human_signed_off": human, "ai_reviews": ai}


def build(gates: dict[str, str], record: Json, commit: str) -> Json:
    """Return the dossier of the release.

    Returns:
        Every section of the dossier.
    """
    return {
        "generated_at": datetime.now(tz=UTC).isoformat(timespec="seconds"),
        "identity": identity(commit),
        "gates": gates,
        "mutation": mutation(record, commit),
        "evidence": evidence(),
        "known_differences": known_differences(),
        "gold_cases": gold_cases(),
        "sign_off": sign_off(),
    }


def render(dossier: Json) -> str:
    """Render the dossier as a page a person reads.

    Returns:
        The Markdown of the dossier.
    """
    ident, mut, ev = dossier["identity"], dossier["mutation"], dossier["evidence"]
    cases, packets = dossier["gold_cases"], dossier["gold_cases"]["validation_packets"]
    unproven = sum(len(v) for v in ev["readiness_baseline"]["provider output"].values())
    verified = sum(len(v) for v in cases["verified_reference_cases"].values())
    provided = sum(p["kind"] != "engine_provisional" for p in packets)
    signed = len(dossier["sign_off"]["human_signed_off"])
    coverage = [
        f"| `{ccnl}` | " + " | ".join(cov[a] or "-" for a in AXES) + " |"
        for ccnl, cov in sorted(ev["production_coverage"].items())
    ]
    lines = [
        f"# Validation dossier {ident['version']}",
        "",
        f"Commit `{ident['commit']}`, generated {dossier['generated_at']}.",
        (
            f"`uv.lock` {ident['uv_lock_sha256']}; bundle manifest "
            f"{ident['bundle_manifest_sha256']}."
        ),
        "",
        "## Gates",
        "",
        *(f"- {job}: {result}" for job, result in sorted(dossier["gates"].items())),
        "",
        "## Mutation",
        "",
        (
            f"Campaign of {mut['date']} on the same commit, "
            f"{len(mut['perimeter'])} modules, minimum {mut['min_score']}% per "
            f"module; core {mut['scores']['core']['score']}%; "
            f"{len(mut['floors'])} floors; {mut['equivalent_mutants']} "
            "equivalent mutants classified."
        ),
        "",
        "## Coverage of the production CCNLs",
        "",
        "| CCNL | " + " | ".join(AXES) + " |",
        "|---|" + "---|" * len(AXES),
        *coverage,
        "",
        "## Open",
        "",
        (
            f"- Weak rules in the baseline: {ev['weak_rules_baseline']}; open "
            f"limitations: {ev['open_limitations_baseline']}."
        ),
        f"- Outputs of production CCNLs without a provider output: {unproven}.",
        f"- Deadlines in the next {HORIZON_DAYS} days: {len(ev['deadlines'])}.",
        f"- Staleness findings: {len(ev['staleness'])}.",
        f"- Accepted variances: {len(dossier['known_differences'])}.",
        "",
        "## Gold cases and sign-off",
        "",
        f"- Verified reference cases: {verified}.",
        f"- Validation packets: {len(packets)}, with a provider output: {provided}.",
        (
            f"- CCNLs signed off by a person: {signed}; AI reviews: "
            f"{dossier['sign_off']['ai_reviews']}."
        ),
        "",
    ]
    return "\n".join(lines)


def _gates(values: list[str]) -> dict[str, str]:
    gates = {}
    for value in values:
        job, sep, result = value.partition("=")
        if not sep or not job or not result:
            msg = f"--gate takes JOB=RESULT, not {value!r}"
            raise DossierError(msg)
        gates[job] = result
    return gates


def main(argv: list[str] | None = None) -> int:
    """Write ``dossier.json`` and ``dossier.md`` into ``--out``.

    Returns:
        0 when written, 1 when the evidence belongs to another commit or a
        gate did not succeed.
    """
    parser = argparse.ArgumentParser(description="Build the validation dossier.")
    parser.add_argument("--gate", action="append", default=[], metavar="JOB=RESULT")
    parser.add_argument("--mutation", type=Path, default=RECORD)
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    args = parser.parse_args(argv)
    try:
        gates = _gates(args.gate)
        record = json.loads(args.mutation.read_text(encoding="utf-8"))
        dossier = build(gates, record, _commit())
    except DossierError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    failed = sorted(job for job, result in gates.items() if result != "success")
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "dossier.json").write_text(
        json.dumps(dossier, indent=2, default=str) + "\n", encoding="utf-8"
    )
    (args.out / "dossier.md").write_text(render(dossier), encoding="utf-8")
    if failed:
        print(f"ERROR: gates not passed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"Written {args.out / 'dossier.json'} and {args.out / 'dossier.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
