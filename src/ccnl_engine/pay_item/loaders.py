"""Load the bundled pay-item policy ruleset into a :class:`PolicyResolver`."""

from __future__ import annotations

import json

from ccnl_engine.knowledge.loaders import read_resource
from ccnl_engine.pay_item.policies import PolicyResolver, _Rule

__all__ = ["load_policy_resolver"]


def load_policy_resolver() -> PolicyResolver:
    """Load the bundled Italian ruleset from ``knowledge/pay_item/italy.json``.

    Returns:
        A :class:`~ccnl_engine.pay_item.policies.PolicyResolver` backed by
        the built-in ``pay_item/italy.json`` file.
    """
    raw = read_resource("pay_item/italy.json")
    data: list[dict[str, object]] = json.loads(raw)
    return PolicyResolver([_Rule.from_dict(r) for r in data])
