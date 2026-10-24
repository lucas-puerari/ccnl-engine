"""Check the validation packets: one certified comparison per output.

A validation packet (``tests/knowledge/ccnl_engine/period/validation_packet/``)
records one case the engine is compared on, as the certification protocol
of the validation review asks:

- ``artifact``: what the engine is compared with, its identity, SHA-256 and
  ``kind``; the kind fixes its independence (:data:`INDEPENDENCE_OF`);
- ``provenance``: where it comes from, why it is independent of the engine
  and of the sources of the bundle, how it was anonymised and the right to
  keep it;
- ``inputs``: every fact that rebuilds the case, so a provider can compute
  it and the engine can replay it: the ``scenario`` and the facts of a
  request, with the keys of an observed payslip replay
  (:data:`scripts.provenance.replay.check.INPUT_KEYS`);
- ``outputs``: one entry per compared output, each with its value, the
  perimeter of the total, the tolerance, the rounding and the
  ``result`` of the comparison;
- ``review``: reviewer, date, owner and the date the packet is looked at
  again;
- ``versions``: engine, bundle and provider the comparison ran on.

Each output is judged on its own: a rate never stands for the total it
sets, a base salary never for the gross, a net never for the employer
cost.  An output is ``covered`` only with ``result`` ``match`` or
``explained_difference``; ``engine_bug`` and ``artifact_error`` cover
nothing.  :func:`coverage` returns the ``(ccnl, output, independence)``
triples the packets cover, the shape the readiness gate reads.

The module reads raw JSON with the standard library only.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.provenance.reference_case.check import AXES
from scripts.provenance.replay.check import input_errors

__all__ = [
    "INDEPENDENCE_OF",
    "PACKETS_DIR",
    "RESULTS",
    "check_all",
    "coverage",
    "packet_errors",
]

REPO_ROOT: Final = Path(__file__).resolve().parents[3]
PACKETS_DIR: Final = REPO_ROOT / "tests/knowledge/ccnl_engine/period/validation_packet"
#: The independence each kind of artifact stands for.
INDEPENDENCE_OF: Final = {
    "provider_output": "provider output",
    "official_worked_example": "provider output",
    "hand_oracle": "hand oracle",
    "engine_provisional": None,
}
#: Outcomes of a comparison, and whether each covers the output.
RESULTS: Final = {
    "match": True,
    "explained_difference": True,
    "engine_bug": False,
    "artifact_error": False,
    "pending": False,
}
#: The scenarios a packet may describe.
SCENARIOS: Final = (
    "ordinary_month",
    "partial_month",
    "variable",
    "extra_month",
    "annual_conguaglio",
    "termination",
    "employer_cost",
)
_SECTIONS: Final = ("artifact", "provenance", "inputs", "outputs", "review", "versions")
_SHA256: Final = re.compile(r"^[0-9a-f]{64}$")
_AMOUNT: Final = re.compile(r"^-?\d+\.\d{2}$")
_ROUNDINGS: Final = ("half_up_cents", "half_even_cents", "truncate_cents", "whole_euro")

Json = dict[str, Any]


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _day(value: object) -> date | None:
    try:
        return date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def _artifact_errors(artifact: Json) -> list[str]:
    errors = [
        f"artifact.{k} missing" for k in ("id", "kind") if not _text(artifact.get(k))
    ]
    if artifact.get("kind") not in INDEPENDENCE_OF:
        errors.append(f"artifact.kind {artifact.get('kind')!r} unknown")
    sha = artifact.get("sha256")
    if artifact.get("kind") != "engine_provisional" and not (
        isinstance(sha, str) and _SHA256.match(sha)
    ):
        errors.append("artifact.sha256 is not a SHA-256")
    return errors


def _provenance_errors(provenance: Json) -> list[str]:
    errors = [
        f"provenance.{k} missing"
        for k in ("source", "independence", "anonymisation", "retention")
        if not _text(provenance.get(k))
    ]
    if _day(provenance.get("obtained_on")) is None:
        errors.append("provenance.obtained_on is not a date")
    return errors


def _inputs_errors(inputs: Json) -> list[str]:
    errors = []
    if inputs.get("scenario") not in SCENARIOS:
        errors.append(f"inputs.scenario {inputs.get('scenario')!r} unknown")
    facts = {k: v for k, v in inputs.items() if k != "scenario"}
    errors += [f"inputs: {e}" for e in input_errors(facts)]
    return errors


def _output_errors(index: int, output: Json) -> list[str]:
    where = f"outputs[{index}]"
    errors: list[str] = []
    if output.get("output") not in AXES:
        errors.append(f"{where}.output {output.get('output')!r} is not a total")
    errors.extend(
        f"{where}.{key} is not an amount with cents"
        for key in ("value", "tolerance")
        if not (isinstance(output.get(key), str) and _AMOUNT.match(output[key]))
    )
    if not _text(output.get("perimeter")):
        errors.append(f"{where}.perimeter missing")
    if output.get("rounding") not in _ROUNDINGS:
        errors.append(f"{where}.rounding {output.get('rounding')!r} unknown")
    result = output.get("result")
    if result not in RESULTS:
        errors.append(f"{where}.result {result!r} unknown")
    if result in {"explained_difference", "engine_bug", "artifact_error"} and not _text(
        output.get("explanation")
    ):
        errors.append(f"{where}: {result} without explanation")
    return errors


def _review_errors(review: Json) -> list[str]:
    errors = [
        f"review.{k} missing" for k in ("reviewer", "owner") if not _text(review.get(k))
    ]
    day, by = _day(review.get("date")), _day(review.get("review_by"))
    if day is None:
        errors.append("review.date is not a date")
    if by is None or (day is not None and by <= day):
        errors.append("review.review_by is not a date after review.date")
    return errors


def _versions_errors(packet: Json) -> list[str]:
    versions = packet["versions"]
    keys = ["engine", "bundle"]
    if packet["artifact"].get("kind") != "engine_provisional":
        keys.append("provider")
    return [f"versions.{k} missing" for k in keys if not _text(versions.get(k))]


def _outputs_errors(outputs: list[object]) -> list[str]:
    names = [str(o.get("output")) for o in outputs if isinstance(o, dict)]
    errors = [
        f"outputs: {n} compared twice"
        for n in sorted({n for n in names if names.count(n) > 1})
    ]
    for index, output in enumerate(outputs):
        errors += _output_errors(index, output if isinstance(output, dict) else {})
    return errors


def packet_errors(packet: object) -> list[str]:
    """Return what a validation packet lacks.

    Returns:
        One reason per missing or invalid field; empty for a valid packet.
    """
    if not isinstance(packet, dict):
        return ["not a JSON object"]
    missing = [s for s in _SECTIONS if not isinstance(packet.get(s), (dict, list))]
    if missing:
        return [f"{s} missing" for s in missing]
    errors = [
        *_artifact_errors(packet["artifact"]),
        *_provenance_errors(packet["provenance"]),
        *_inputs_errors(packet["inputs"]),
        *_review_errors(packet["review"]),
    ]
    outputs = packet["outputs"]
    if not isinstance(outputs, list) or not outputs:
        return [*errors, *_versions_errors(packet), "outputs is empty"]
    return [*errors, *_outputs_errors(outputs), *_versions_errors(packet)]


def _packets(folder: Path) -> list[tuple[Path, object]]:
    return [
        (p, json.loads(p.read_text(encoding="utf-8")))
        for p in sorted(folder.glob("*.json"))
    ]


def coverage(folder: Path = PACKETS_DIR) -> set[tuple[str, str, str]]:
    """Return the ``(ccnl, output, independence)`` triples the packets cover.

    Only a valid packet whose artifact is independent counts, and only the
    outputs it matched or explained.

    Returns:
        The covered triples.
    """
    found: set[tuple[str, str, str]] = set()
    for _, packet in _packets(folder):
        if not isinstance(packet, dict) or packet_errors(packet):
            continue
        independence = INDEPENDENCE_OF[packet["artifact"]["kind"]]
        if independence is None:
            continue
        found |= {
            (packet["inputs"]["ccnl_id"], o["output"], independence)
            for o in packet["outputs"]
            if RESULTS[o["result"]]
        }
    return found


def check_all(folder: Path = PACKETS_DIR) -> list[str]:
    """Return the errors of every packet of ``folder``.

    Returns:
        ``"<file>: <reason>"`` messages; empty when every packet is valid.
    """
    return [
        f"{path.name}: {e}"
        for path, packet in _packets(folder)
        for e in packet_errors(packet)
    ]


def main() -> int:
    """Print the errors of the packets.

    Returns:
        1 when a packet is invalid, else 0.
    """
    errors = check_all()
    for error in errors:
        print(f"  {error}", file=sys.stderr)
    count = len(list(PACKETS_DIR.glob("*.json")))
    print(f"Validation packets checked: {count}, {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
