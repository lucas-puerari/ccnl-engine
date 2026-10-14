"""Load the bundled pay-item policy ruleset into a :class:`PolicyResolver`."""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import pairwise, starmap
from typing import get_args

from ccnl_engine.bundle.loaders import read_resource
from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.pay_item.models import PayItem
from ccnl_engine.pay_item.policies import (
    ContributionAxis,
    CostAxis,
    PolicyResolver,
    TaxAxis,
    TfrAxis,
    _Rule,
)

__all__ = ["load_policy_resolver"]

#: A ledger kind selected from ``BonusEvent`` while its public pay item remains
#: ``BonusEarning``. Every other policy kind is a PayItem discriminator.
_LEDGER_ONLY_KINDS = frozenset({"contract_renewal_earning"})


def _pay_item_kinds() -> frozenset[str]:
    """Return every discriminator of the public ``PayItem`` union.

    Returns:
        The kinds accepted by the public pay-item model.
    """
    union = get_args(PayItem)[0]
    return frozenset(
        str(model.model_fields["kind"].default) for model in get_args(union)
    )


def _rule(index: int, raw: object) -> _Rule:
    """Parse and validate one policy rule.

    Returns:
        The validated rule.

    Raises:
        DataIntegrityError: When the entry is malformed or contradictory.
    """
    if not isinstance(raw, dict):
        msg = f"pay-item policy entry {index} is not an object"
        raise DataIntegrityError(msg)
    try:
        rule = _Rule.from_dict(raw)
        TaxAxis(rule.tax)
        ContributionAxis(rule.contribution)
        TfrAxis(rule.tfr)
        CostAxis(rule.cost)
    except (KeyError, TypeError, ValueError) as exc:
        msg = f"invalid pay-item policy entry {index}: {exc}"
        raise DataIntegrityError(msg) from exc
    if not rule.policy_id or not rule.policy_version or not rule.legal_basis:
        msg = f"pay-item policy entry {index} has empty identity or legal basis"
        raise DataIntegrityError(msg)
    if not rule.kinds or any(not kind for kind in rule.kinds):
        msg = f"pay-item policy entry {index} has no non-empty kind"
        raise DataIntegrityError(msg)
    if len(rule.kinds) != len(set(rule.kinds)):
        msg = f"pay-item policy entry {index} repeats a kind"
        raise DataIntegrityError(msg)
    if rule.effective_until is not None and rule.effective_until < rule.effective_from:
        msg = f"pay-item policy entry {index} ends before it starts"
        raise DataIntegrityError(msg)
    return rule


def _validate_coverage(rules: list[_Rule]) -> None:
    """Require exact kind coverage and non-overlapping effective periods.

    Raises:
        DataIntegrityError: When a kind is unknown, absent or covered twice.
    """
    expected = _pay_item_kinds() | _LEDGER_ONLY_KINDS
    actual = {kind for rule in rules for kind in rule.kinds}
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        msg = (
            "pay-item policy kind coverage mismatch: "
            f"missing={missing}, unknown={unknown}"
        )
        raise DataIntegrityError(msg)
    by_kind: dict[str, list[_Rule]] = defaultdict(list)
    for rule in rules:
        for kind in rule.kinds:
            by_kind[kind].append(rule)
    for kind, candidates in by_kind.items():
        ordered = sorted(candidates, key=lambda candidate: candidate.effective_from)
        for previous, current in pairwise(ordered):
            if previous.effective_until is None or (
                current.effective_from <= previous.effective_until
            ):
                msg = f"pay-item policy periods overlap for kind {kind!r}"
                raise DataIntegrityError(msg)


def _parse_policy_rules(data: object) -> list[_Rule]:
    """Return the validated rules of a decoded policy document.

    Returns:
        The parsed rules in declaration order.

    Raises:
        DataIntegrityError: When the document is not a valid complete policy set.
    """
    if not isinstance(data, list):
        msg = "pay-item policy document must be a list"
        raise DataIntegrityError(msg)
    rules = list(starmap(_rule, enumerate(data)))
    _validate_coverage(rules)
    return rules


def load_policy_resolver() -> PolicyResolver:
    """Load the bundled Italian ruleset from ``knowledge/pay_item/italy.json``.

    Returns:
        A :class:`~ccnl_engine.pay_item.policies.PolicyResolver` backed by
        the built-in ``pay_item/italy.json`` file.

    Raises:
        DataIntegrityError: When the bundled document is invalid or incomplete.
    """
    raw = read_resource("pay_item/italy.json")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = "pay_item/italy.json is not valid JSON"
        raise DataIntegrityError(msg) from exc
    return PolicyResolver(_parse_policy_rules(data))
