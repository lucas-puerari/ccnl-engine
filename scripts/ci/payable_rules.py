"""Inventory of the payable rules in the bundled knowledge data.

A payable rule is a bundled value that the payroll run reads to compute a
posted amount: CCNL salary tables, fixed allowances, seniority increments,
extra-month entitlements, the extra-month accrual threshold, the ERC paid
with the tredicesima, the first-tier
overtime bands, the absence rule (daily quota of partial months and sick
days), the sickness rule, employer pension fund rates and the assistance
contribution charged per paid hour; the INPS sick-pay
indemnity bands; INPS
contribution rates (ordinary, apprentice, domestic, fixed-term
addizionale); IRPEF brackets, the Art. 13 work deduction and its
sterilizzazione; the trattamento integrativo, the ulteriore detrazione and
the somma esente; the TFR divisor and the TFR revaluation (rate, ISTAT
index and substitute tax); the regional and municipal surtax
tables; the Art. 12 family deductions; the complementary pension deduction
cap and solidarity rate; the fringe-benefit thresholds and the PdR limits;
the parameters of the substitute-tax regimes.

Bundled values the run does not read are not payable: the other CCNL work
rules (overtime bands beyond an hour threshold or conditional on another
work kind, bands paid per hour or per shift, leave), apprenticeship tracks
and the Art. 15 deductions.

Each payable rule must carry a provenance record.  CCNL rules carry one per
rule (salary period, allowance, seniority block, additional-months period,
accrual rule, overtime band, absence and sickness rule, employer fund); a
salary period or an
allowance without its own record inherits the one of its level, a fund rate
period the one of its fund.  A CCNL without ``parameters.accrual_rule``
runs on the engine default threshold, which no CCNL source backs: the
inventory lists it as ``missing``.
Fiscal files carry one per data block: the block object holds
``provenance``, except the IRPEF bracket list and the fixed-term scalar,
and the sick-pay bands, whose record sits in the sibling
``<block>_provenance`` key, the surtax
tables, whose record is the file-level ``provenance``, and the substitute
tax regimes, whose record is their ``source`` with its ``source_status``.
A sub-block with its own record inside a fiscal block (the Art. 13
minimum ``work_deduction.minimum``, the TFR additional IVS
``tfr.additional_ivs``, the 1% employee IVS ``inps.employee_additional``,
the INPS minimum base ``inps.minimum_base``) is
a rule of its own, with the capabilities of its block.

The module reads raw JSON with the standard library only, so the CI check
runs without installing the project.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

KNOWLEDGE_DIR: Final = (
    Path(__file__).resolve().parents[2] / "src" / "ccnl_engine" / "knowledge"
)
STATUSES: Final = ("verified", "derived", "assumed", "missing")
#: Code prefix of the overtime bands; other bands are ordinary work supplements.
OVERTIME_PREFIX: Final = "OT_"

_INPS = ("inps_employee", "inps_employer")

#: Blocks of a fiscal file: key (dotted for a nested block), capabilities,
#: and whether the record sits in the sibling ``<key>_provenance`` instead
#: of the block itself.
type _Blocks = tuple[tuple[str, tuple[str, ...], bool], ...]

#: Blocks of a ``tax/data/<year>-<sector>.json`` file.
_TAX_BLOCKS: Final[_Blocks] = (
    ("irpef_brackets", ("irpef",), True),
    ("work_deduction", ("irpef",), False),
    ("fixed_term_additional_rate", ("inps_employer",), True),
    ("tfr", ("tfr",), False),
    ("trattamento_integrativo", ("trattamento_integrativo",), False),
    ("ulteriore_detrazione", ("ulteriore_detrazione_lavoro",), False),
    ("complementary_pension", ("pension_fund_contribution",), False),
)
_INPS_BLOCKS: Final[_Blocks] = (
    ("inps", _INPS, False),
    ("apprentice", _INPS, False),
    ("domestic_contributions", _INPS, False),
)
_NAMED_BLOCKS: Final[dict[str, _Blocks]] = {
    "tax/data/family-deductions-": (
        ("spouse", ("family_deductions",), False),
        ("spouse_increases", ("family_deductions",), False),
        ("children", ("family_deductions",), False),
        ("other_dependents", ("family_deductions",), False),
    ),
    "tax/data/variable-pay-rules": (
        ("fringe_benefit", ("fringe_benefit",), False),
        ("pdr", ("bonus_pdr",), False),
    ),
    "tax/data/somma-esente-": (("somma_esente", ("somma_esente",), False),),
    "tax/data/tfr-revaluation-": (
        ("rate", ("tfr_revaluation",), False),
        ("price_index", ("tfr_revaluation",), False),
        ("substitute_tax", ("tfr_revaluation",), False),
    ),
    "inps/data/sick-pay-rates": (("bands", ("sickness",), True),),
}
#: CCNL work rules read by every run that needs them: key and capabilities.
_WORK_RULES: Final = (
    ("absence_rules", ("base_salary", "sickness")),
    ("sickness_rules", ("sickness",)),
)
_REGIMES: Final = {
    "rinnovo": "rinnovo_substitute_tax",
    "notte_festivi_turni": "notte_festivi_turni_substitute_tax",
}
_WHOLE_FILE: Final = {
    "surtax/data/regionale-": ("rates", "addizionale_regionale"),
    "surtax/data/comunale-": ("rates", "addizionale_comunale"),
}


@dataclass(frozen=True)
class PayableRule:
    """One payable rule found in the bundle.

    Attributes:
        file: Data file, relative to the knowledge directory.
        path: Location of the rule inside the file.
        capabilities: Catalog features whose amounts the rule feeds.
        status: Provenance status, or ``None`` when no record exists.
        record: The raw provenance record, ``None`` when there is none or
            the status is not read from a record.
    """

    file: str
    path: str
    capabilities: tuple[str, ...]
    status: str | None
    record: Mapping[str, object] | None = field(default=None, compare=False, repr=False)


def _rule(
    file: str, path: str, capabilities: tuple[str, ...], record: object
) -> PayableRule:
    """Return the rule at ``path`` with the status of ``record``.

    Returns:
        The rule, carrying ``record`` when it is a JSON object.
    """
    raw = record if isinstance(record, dict) else None
    return PayableRule(file, path, capabilities, _status(record), raw)


def _by_prefix[T](table: Mapping[str, T], file: str) -> T | None:
    """Return the entry of ``table`` whose key starts ``file``, if any.

    Returns:
        The matching value, or ``None``.
    """
    return next((v for k, v in table.items() if file.startswith(k)), None)


def _status(record: object) -> str | None:
    """Return the ``status`` of a provenance record.

    Returns:
        The status string, or ``None`` when ``record`` is not a record.
    """
    if not isinstance(record, dict):
        return None
    status = record.get("status")
    return status if isinstance(status, str) else None


def _periods(series: object) -> Iterator[dict[str, object]]:
    """Yield the non-gap periods of a raw time series.

    Yields:
        Each period that holds a value.
    """
    periods = series.get("periods", []) if isinstance(series, dict) else []
    for period in periods:
        if isinstance(period, dict) and period.get("value") is not None:
            yield period


def _level_rules(file: str, level: dict[str, object]) -> Iterator[PayableRule]:
    """Yield the salary periods and fixed allowances of one CCNL level.

    Yields:
        One rule per non-gap salary period and per fixed allowance.
    """
    code = level.get("code")
    inherited = level.get("provenance")
    for period in _periods(level.get("base_salary")):
        record = period.get("provenance") or inherited
        path = f"levels[{code}].base_salary[{period.get('valid_from')}]"
        yield _rule(file, path, ("base_salary",), record)
    allowances = level.get("fixed_allowances") or []
    for allowance in allowances if isinstance(allowances, list) else []:
        record = allowance.get("provenance") or inherited
        path = f"levels[{code}].fixed_allowances[{allowance.get('code')}]"
        yield _rule(file, path, ("base_salary",), record)


def ccnl_rules(file: str, data: Mapping[str, object]) -> Iterator[PayableRule]:
    """Yield the payable rules of one CCNL file.

    Args:
        file: File name, relative to the knowledge directory.
        data: Decoded CCNL JSON.

    Yields:
        One rule per salary period, allowance, seniority block,
        additional-months period, the accrual rule, the absence and
        sickness rules, one per first-tier overtime band, one per
        employer fund rate period and the assistance contribution.
    """
    levels = data.get("levels")
    for level in levels if isinstance(levels, list) else []:
        yield from _level_rules(file, level)
    params = data.get("parameters")
    params = params if isinstance(params, dict) else {}
    seniority = params.get("seniority_increments")
    if isinstance(seniority, dict):
        record = seniority.get("provenance")
        yield _rule(file, "seniority_increments", ("seniority",), record)
    for period in _periods(params.get("additional_months")):
        path = f"additional_months[{period.get('valid_from')}]"
        yield _rule(file, path, ("base_salary",), period.get("provenance"))
    accrual = params.get("accrual_rule")
    if isinstance(accrual, dict):
        yield _rule(file, "accrual_rule", ("base_salary",), accrual.get("provenance"))
    else:
        yield PayableRule(file, "accrual_rule", ("base_salary",), "missing")
    raccordo = params.get("raccordo_element")
    if isinstance(raccordo, dict):
        record = raccordo.get("provenance")
        yield _rule(file, "raccordo_element", ("base_salary",), record)
    yield from _work_rules(file, data.get("work_rules"))
    yield from _overtime_rules(file, data.get("work_rules"))
    yield from _fund_rules(file, params.get("employer_funds"))
    yield from _contractual_rules(file, params.get("contractual_fund_contribution"))
    assistance = params.get("assistance_contribution")
    if isinstance(assistance, dict):
        record = assistance.get("provenance")
        yield _rule(
            file, "assistance_contribution", ("assistance_contribution",), record
        )


def _work_rules(file: str, work_rules: object) -> Iterator[PayableRule]:
    """Yield the absence and sickness rules of a CCNL that holds them.

    Yields:
        One rule per work rule block present in ``work_rules``.
    """
    rules = work_rules if isinstance(work_rules, dict) else {}
    for key, capabilities in _WORK_RULES:
        block = rules.get(key)
        if isinstance(block, dict):
            path = f"work_rules.{key}"
            yield _rule(file, path, capabilities, block.get("provenance"))


def _is_first_tier(band: dict[str, object]) -> bool:
    """Return whether ``band`` can give the multiplier of an overtime event.

    Returns:
        ``True`` for an ``OT_*`` percentage band with no hour threshold and
        no context condition.
    """
    return (
        str(band.get("code", "")).startswith(OVERTIME_PREFIX)
        and band.get("kind") == "percentage"
        and band.get("hour_threshold_per_day") is None
        and band.get("hour_threshold_per_week") is None
        and not band.get("required_context_kinds")
    )


def _overtime_rules(file: str, work_rules: object) -> Iterator[PayableRule]:
    """Yield the first-tier overtime bands of a CCNL.

    Yields:
        One ``overtime`` rule per band an event without a multiplier can be
        paid with.
    """
    rules = work_rules if isinstance(work_rules, dict) else {}
    supplements = rules.get("time_supplements")
    bands = supplements.get("overtime_bands") if isinstance(supplements, dict) else []
    for band in bands if isinstance(bands, list) else []:
        if isinstance(band, dict) and _is_first_tier(band):
            path = f"overtime_bands[{band.get('code')}]"
            yield _rule(file, path, ("overtime",), band.get("provenance"))


#: Rate series of an employer fund.
_FUND_SERIES = (
    "rate",
    "employee_min_rate",
    "apprentice_rate",
    "young_member_rate",
    "erc_holder_rate",
    "enrolled_monthly",
)


def _fund_rules(file: str, funds: object) -> Iterator[PayableRule]:
    """Yield the rate periods of the employer pension funds of a CCNL.

    Yields:
        One rule per non-gap period of each fund rate series.
    """
    for fund in funds if isinstance(funds, list) else []:
        inherited = fund.get("provenance")
        tiers = fund.get("employer_rate_tiers") or []
        series = {key: fund.get(key) for key in _FUND_SERIES} | {
            f"employer_rate_tiers[{tier.get('employee_from')}]": tier.get("rate")
            for tier in tiers
        }
        for key, values in series.items():
            for period in _periods(values):
                path = (
                    f"employer_funds[{fund.get('code')}].{key}"
                    f"[{period.get('valid_from')}]"
                )
                record = period.get("provenance") or inherited
                yield _rule(file, path, ("pension_fund_contribution",), record)


def _contractual_rules(file: str, spec: object) -> Iterator[PayableRule]:
    """Yield the monthly amounts of the contractual fund contribution.

    Yields:
        One rule per non-gap period of the amount of each level, of the
        apprentices and of a worker not enrolled voluntarily.
    """
    if not isinstance(spec, dict):
        return
    amounts = spec.get("monthly_by_level")
    by_key = dict(amounts if isinstance(amounts, dict) else {})
    if spec.get("apprentice_monthly") is not None:
        by_key["apprentice"] = spec["apprentice_monthly"]
    hourly = spec.get("hourly_by_level")
    for level, series in (hourly if isinstance(hourly, dict) else {}).items():
        by_key[f"hourly[{level}]"] = series
    if spec.get("apprentice_hourly") is not None:
        by_key["hourly[apprentice]"] = spec["apprentice_hourly"]
    if spec.get("not_enrolled_monthly") is not None:
        by_key["not_enrolled"] = spec["not_enrolled_monthly"]
    for level, series in by_key.items():
        for period in _periods(series):
            path = f"contractual_fund_contribution[{level}][{period.get('valid_from')}]"
            record = period.get("provenance") or spec.get("provenance")
            yield _rule(file, path, ("pension_fund_contribution",), record)


def _at(data: Mapping[str, object], key: str) -> object:
    """Return the value at the dotted ``key`` of ``data``.

    Returns:
        The value, or ``None`` when a step of the path is missing.
    """
    node: object = data
    for part in key.split("."):
        node = node.get(part) if isinstance(node, dict) else None
    return node


def _block_rules(
    file: str,
    data: Mapping[str, object],
    blocks: _Blocks,
) -> Iterator[PayableRule]:
    """Yield one rule per block of a fiscal file that is present.

    Yields:
        One rule per block of ``blocks`` found in ``data``.
    """
    for key, capabilities, sibling in blocks:
        block = _at(data, key)
        if block is None:
            continue
        record = (
            data.get(f"{key}_provenance")
            if sibling
            else (block.get("provenance") if isinstance(block, dict) else None)
        )
        yield _rule(file, key, capabilities, record)
        yield from _nested_rules(file, key, block, capabilities)


def _nested_rules(
    file: str, path: str, block: object, capabilities: tuple[str, ...]
) -> Iterator[PayableRule]:
    """Yield the sub-blocks of a fiscal block that carry their own record.

    Yields:
        One rule per nested object holding a ``provenance`` record, at
        ``<block>.<key>``, depth first.
    """
    for key, child in block.items() if isinstance(block, dict) else ():
        if key == "provenance" or not isinstance(child, dict):
            continue
        child_path = f"{path}.{key}"
        if isinstance(child.get("provenance"), dict):
            yield _rule(file, child_path, capabilities, child["provenance"])
        yield from _nested_rules(file, child_path, child, capabilities)


def fiscal_rules(file: str, data: Mapping[str, object]) -> Iterator[PayableRule]:
    """Yield the payable rules of one tax, INPS or surtax file.

    Args:
        file: File name, relative to the knowledge directory.
        data: Decoded JSON.

    Yields:
        One rule per payable data block.
    """
    whole_file = _by_prefix(_WHOLE_FILE, file)
    if whole_file is not None:
        key, capability = whole_file
        yield _rule(file, key, (capability,), data.get("provenance"))
        return
    if file.startswith("tax/data/20"):
        yield from _block_rules(file, data, _TAX_BLOCKS)
    elif file.startswith("inps/data/20"):
        yield from _block_rules(file, data, _INPS_BLOCKS)
    yield from _block_rules(file, data, _by_prefix(_NAMED_BLOCKS, file) or ())
    for key, capability in _REGIMES.items():
        regime = data.get(key)
        if isinstance(regime, dict):
            status = regime.get("source_status") if regime.get("source") else None
            yield PayableRule(
                file, key, (capability,), status if isinstance(status, str) else None
            )


def inventory(root: Path = KNOWLEDGE_DIR) -> tuple[PayableRule, ...]:
    """Return every payable rule of the knowledge data under ``root``.

    Args:
        root: Knowledge directory holding ``ccnl``, ``tax``, ``inps`` and
            ``surtax`` data.

    Returns:
        The rules, CCNL files first, each group in file-name order.
    """
    rules: list[PayableRule] = []
    for path in sorted((root / "ccnl" / "data").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rules.extend(ccnl_rules(path.relative_to(root).as_posix(), data))
    for group in ("tax", "inps", "surtax"):
        for path in sorted((root / group / "data").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            rules.extend(fiscal_rules(path.relative_to(root).as_posix(), data))
    return tuple(rules)


def rule_errors(rules: tuple[PayableRule, ...]) -> list[str]:
    """Return one error per rule without a valid provenance record.

    Returns:
        ``"<file>: <path>: <reason>"`` messages; empty when every rule has
        a record with a known status.
    """
    errors: list[str] = []
    for rule in rules:
        if rule.status is None:
            errors.append(f"{rule.file}: {rule.path}: no provenance record")
        elif rule.status not in STATUSES:
            errors.append(f"{rule.file}: {rule.path}: unknown status {rule.status!r}")
    return errors


def count_by_status(rules: tuple[PayableRule, ...]) -> dict[str, int]:
    """Count rules per provenance status, ``none`` for rules without a record.

    Returns:
        A mapping with every known status, in canonical order, then ``none``.
    """
    counts = Counter(rule.status or "none" for rule in rules)
    return {status: counts[status] for status in (*STATUSES, "none")}


def count_by_capability(
    rules: tuple[PayableRule, ...],
) -> dict[str, dict[str, int]]:
    """Count rules per capability and provenance status.

    Returns:
        Capability to status counts; a rule feeding two capabilities counts
        once in each.
    """
    counts: dict[str, Counter[str]] = {}
    for rule in rules:
        for capability in rule.capabilities:
            counts.setdefault(capability, Counter())[rule.status or "none"] += 1
    return {
        capability: {status: bucket[status] for status in (*STATUSES, "none")}
        for capability, bucket in counts.items()
    }


def count_by_file(rules: tuple[PayableRule, ...]) -> dict[str, dict[str, int]]:
    """Count rules per data file and provenance status.

    Returns:
        File, relative to the knowledge directory, to status counts, in
        inventory order.
    """
    counts: dict[str, Counter[str]] = {}
    for rule in rules:
        counts.setdefault(rule.file, Counter())[rule.status or "none"] += 1
    return {
        file: {status: bucket[status] for status in (*STATUSES, "none")}
        for file, bucket in counts.items()
    }
