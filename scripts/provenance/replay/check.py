"""Rules of the replay of an observed payslip: what it may compare and credit.

Each record of ``tests/knowledge/ccnl_engine/period/observed_payslip/``
states in ``replay`` whether the engine can replay it:

- ``full``: the request states every fact the payslip rests on
  (``unknown_inputs`` is empty) and ``expected`` compares every complete
  output of :data:`~scripts.provenance.reference_case.check.AXES`, but
  those ``outside_perimeter`` names with the reason the payslip does not
  print them;
- ``partial``: some facts have no field in the request.  Each entry of
  ``unknown_inputs`` names one (``input``) and the totals, components and
  rates it can move (``affects``); no expected value may read one of them,
  so an unknown fact never contaminates a credited axis;
- ``not_replayable``: ``reason`` says why, and nothing else is stated.

Each expected value names the field of the payslip it was ``printed`` in,
its ``value`` and ``tolerance``; a key of :data:`PERIMETER_KEYS`, whose
name does not say what the total includes, states it in ``perimeter``.
Only the facts of :data:`INPUT_KEYS` build the request: there is no
generic override that could force an output and make the replay circular.
A difference is accepted only while ``known_differences`` lists it with
its reason, its owner and a date not yet past.

The module reads raw JSON with the standard library only.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from scripts.provenance.reference_case.check import AXES, AXIS_OF, ELEMENTS

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

__all__ = [
    "EVENT_TYPES",
    "INPUT_KEYS",
    "PAYSLIPS_DIR",
    "PERIMETER_KEYS",
    "REPLAYABILITY",
    "REPLAY_KEYS",
    "credited_records",
    "input_errors",
    "load_records",
    "record_errors",
    "replay_errors",
]

REPO_ROOT: Final = Path(__file__).resolve().parents[3]
PAYSLIPS_DIR: Final = REPO_ROOT / "tests/knowledge/ccnl_engine/period/observed_payslip"
REPLAYABILITY: Final = ("full", "partial", "not_replayable")
#: Expected values a replay can compare: each has a reader in the runner.
REPLAY_KEYS: Final = frozenset(AXIS_OF) - {"hourly_percentages"}
#: Totals whose name leaves their scope open: the record states it.
PERIMETER_KEYS: Final = frozenset({"employer_cost", "tfr_accrual"})
#: Facts a request is built from, each a field of the public API.
INPUT_KEYS: Final = frozenset({
    "ccnl_id",
    "level_code",
    "year",
    "month",
    "headcount",
    "contract_type",
    "category",
    "public_life_insurance",
    "hired_on",
    "terminated_on",
    "weekly_hours",
    "full_time_weekly_hours",
    "regione",
    "comune_belfiore",
    "prior_year_employment_income",
    "tfr_treasury_fund",
    "public_end_of_service",
    "run_kind",
    "seniority_months",
    "seniority_as_of",
    "pension_fund",
    "current_year_employment_only_on",
    "events",
})
#: Events a record may state, each a line the payslip prints.  A sick pay
#: override (``SickLeaveEvent``) and a TFR payout (``TerminationTFREvent``)
#: are amounts the engine would otherwise compute: stating them would make
#: the replay circular, so a record lists them in ``unknown_inputs``.
EVENT_TYPES: Final = frozenset({
    "AbsenceEvent",
    "OvertimeEvent",
    "NightShiftEvent",
    "HolidayWorkEvent",
    "ShiftWorkEvent",
    "StandbyEvent",
    "BonusEvent",
    "FringeEvent",
    "WelfareEvent",
    "ArrearsEvent",
    "BilateralFundEvent",
    "TravelAllowanceEvent",
})
_REQUIRED_INPUTS: Final = ("ccnl_id", "level_code", "year", "month", "headcount")
_CONTRACT_TYPES: Final = ("permanent", "fixed_term")
_RUN_KINDS: Final = ("regular", "thirteenth", "fourteenth")
#: Fields of a pension fund enrolment a record states.
_FUND_FIELDS: Final = frozenset({"fund_code", "employee_rate", "tfr_to_fund"})
_SPEC_FIELDS: Final = ("printed", "value", "tolerance")
_LABELS: Final = frozenset(AXES + ELEMENTS)


def _iso_date(value: object) -> date | None:
    try:
        return date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def input_errors(inputs: object) -> list[str]:
    """Return what the facts of a request lack, as a replay states them.

    The validation packets state their inputs with the same keys.

    Returns:
        One reason per unknown, missing or invalid fact.
    """
    return list(_inputs_errors(inputs))


def _inputs_errors(inputs: object) -> Iterator[str]:
    if not isinstance(inputs, dict):
        yield "'inputs' must be an object"
        return
    yield from (f"unknown input {k!r}" for k in sorted(set(inputs) - INPUT_KEYS))
    yield from (f"missing input {k!r}" for k in _REQUIRED_INPUTS if k not in inputs)
    if inputs.get("contract_type") not in _CONTRACT_TYPES:
        yield f"'contract_type' must be one of {list(_CONTRACT_TYPES)}"
    yield from _typed_inputs_errors(inputs)


def _typed_inputs_errors(inputs: Mapping[str, object]) -> Iterator[str]:
    if inputs.get("run_kind", "regular") not in _RUN_KINDS:
        yield f"'run_kind' must be one of {list(_RUN_KINDS)}"
    if ("seniority_months" in inputs) != ("seniority_as_of" in inputs):
        yield "'seniority_months' and 'seniority_as_of' are stated together"
    for key in ("hired_on", "terminated_on", "seniority_as_of"):
        if key in inputs and _iso_date(inputs[key]) is None:
            yield f"{key!r} must be an ISO date"
    if "current_year_employment_only_on" in inputs and (
        _iso_date(inputs["current_year_employment_only_on"]) is None
    ):
        yield "'current_year_employment_only_on' must be an ISO date"
    yield from _events_errors(inputs.get("events", []))
    fund = inputs.get("pension_fund", "none")
    if fund != "none" and not (isinstance(fund, dict) and set(fund) == _FUND_FIELDS):
        yield "'pension_fund' is \"none\" or states " + ", ".join(sorted(_FUND_FIELDS))


def _events_errors(events: object) -> Iterator[str]:
    if not isinstance(events, list):
        yield "'events' must be a list"
        return
    for position, event in enumerate(events):
        kind = event.get("type") if isinstance(event, dict) else None
        if kind not in EVENT_TYPES:
            yield f"event {position} has no type of {sorted(EVENT_TYPES)}"
        elif _iso_date(event.get("event_date")) is None:
            yield f"event {position} ({kind}) needs an ISO 'event_date'"


def _spec_errors(key: str, spec: object) -> Iterator[str]:
    if key not in AXIS_OF:
        yield f"expected value {key!r} belongs to no axis or element"
    elif key not in REPLAY_KEYS:
        yield f"expected value {key!r} has no reader in the replay"
    if not isinstance(spec, dict):
        yield f"expected value {key!r} must be an object"
        return
    missing = [f for f in _SPEC_FIELDS if not spec.get(f)]
    if missing:
        yield f"expected value {key!r} lacks " + ", ".join(missing)
    if key in PERIMETER_KEYS and not spec.get("perimeter"):
        yield f"expected value {key!r} must state its 'perimeter'"


def _expected_errors(expected: object) -> Iterator[str]:
    if not isinstance(expected, dict) or not expected:
        yield "'expected' must be a non-empty object"
        return
    for key, spec in expected.items():
        yield from _spec_errors(key, spec)


def _unknown_errors(
    unknown: object, labels: Mapping[str, str], replayability: str
) -> Iterator[str]:
    if not isinstance(unknown, list):
        yield "'unknown_inputs' must be a list"
        return
    if replayability == "partial" and not unknown:
        yield "a partial replay names its 'unknown_inputs'"
    if replayability == "full" and unknown:
        yield "a full replay has no 'unknown_inputs'"
    for entry in unknown:
        if not (isinstance(entry, dict) and entry.get("input")):
            yield "each unknown input states its 'input' and what it 'affects'"
            continue
        affects = entry.get("affects")
        if not isinstance(affects, list) or not affects:
            yield f"unknown input {entry['input']!r} must list what it 'affects'"
            continue
        yield from (
            f"unknown input {entry['input']!r} affects unknown label {a!r}"
            for a in affects
            if a not in _LABELS
        )
        yield from (
            f"expected value {key!r} reads {label!r}, which the unknown input "
            f"{entry['input']!r} affects"
            for key, label in labels.items()
            if label in affects
        )


def _perimeter_errors(replay: Mapping[str, object], labels: set[str]) -> Iterator[str]:
    outside = replay.get("outside_perimeter", {})
    if not isinstance(outside, dict):
        yield "'outside_perimeter' must be an object"
        return
    yield from (
        f"'outside_perimeter' names {axis!r}, no complete output with a reason"
        for axis, reason in outside.items()
        if axis not in AXES or not reason
    )
    if replay["replayability"] == "full":
        yield from (
            f"a full replay compares {axis!r} or puts it outside its perimeter"
            for axis in AXES
            if axis not in labels and axis not in outside
        )


def _differences_errors(
    differences: object, expected: object, today: date
) -> Iterator[str]:
    if not isinstance(differences, list):
        yield "'known_differences' must be a list"
        return
    keys = expected if isinstance(expected, dict) else {}
    for known in differences:
        key = known.get("key") if isinstance(known, dict) else None
        if key not in keys:
            yield f"known difference {key!r} is no expected value"
            continue
        if not (known.get("reason") and known.get("owner")):
            yield f"known difference {key!r} states its reason and owner"
        until = _iso_date(known.get("accepted_until"))
        if until is None or until < today:
            yield f"known difference {key!r} is expired or has no 'accepted_until'"


def replay_errors(replay: Mapping[str, object], today: date) -> list[str]:
    """Return every rule the ``replay`` block of a record violates.

    Args:
        replay: The ``replay`` object of an observed payslip.
        today: Day the accepted differences are checked against.

    Returns:
        Human-readable messages; empty when the replay is valid.
    """
    replayability = replay.get("replayability")
    if replayability not in REPLAYABILITY:
        return [f"'replayability' must be one of {list(REPLAYABILITY)}"]
    errors = [] if replay.get("reason") else ["a replay states its 'reason'"]
    if replayability == "not_replayable":
        extra = sorted(set(replay) - {"replayability", "reason"})
        return errors + [f"a not_replayable record states no {k!r}" for k in extra]
    expected = replay.get("expected")
    labels = {
        key: AXIS_OF[key]
        for key in (expected if isinstance(expected, dict) else {})
        if key in AXIS_OF
    }
    errors += [
        *_inputs_errors(replay.get("inputs")),
        *_expected_errors(expected),
        *_unknown_errors(replay.get("unknown_inputs"), labels, str(replayability)),
        *_perimeter_errors(replay, set(labels.values())),
        *_differences_errors(replay.get("known_differences"), expected, today),
    ]
    return errors


def load_records(folder: Path = PAYSLIPS_DIR) -> dict[str, dict[str, Any]]:
    """Read every observed payslip of ``folder``.

    Returns:
        The records by file stem, in file order.
    """
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(folder.glob("*.json"))
    }


def credited_records(
    today: date, folder: Path = PAYSLIPS_DIR
) -> dict[str, dict[str, Any]]:
    """Return the replays that may credit evidence: replayable and valid.

    Returns:
        The ``replay`` object of each such record, by file stem.
    """
    found: dict[str, dict[str, Any]] = {}
    for pid, record in load_records(folder).items():
        replay = record.get("replay")
        if not isinstance(replay, dict) or replay.get("replayability") not in {
            "full",
            "partial",
        }:
            continue
        if not replay_errors(replay, today):
            found[pid] = replay
    return found


def record_errors(today: date, folder: Path = PAYSLIPS_DIR) -> list[str]:
    """Return the replay errors of every observed payslip of ``folder``.

    Returns:
        ``"observed_payslip/<id>.json: ..."`` messages.
    """
    errors: list[str] = []
    for pid, record in load_records(folder).items():
        replay = record.get("replay")
        if not isinstance(replay, dict):
            errors.append(f"observed_payslip/{pid}.json: missing 'replay' object")
            continue
        errors += [
            f"observed_payslip/{pid}.json: {e}" for e in replay_errors(replay, today)
        ]
    return errors
