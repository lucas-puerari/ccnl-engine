"""Load the bundled pay-item policy ruleset into a :class:`PolicyResolver`."""

from __future__ import annotations

import json

from ccnl_engine.knowledge.loaders_manifest import read_resource
from ccnl_engine.payroll.amount.policies import PolicyResolver, _Rule

__all__ = ["load_policy_resolver"]


def load_policy_resolver() -> PolicyResolver:
    """Load the bundled Italian ruleset from ``knowledge/policy/italy.json``.

    Returns:
        A :class:`~ccnl_engine.payroll.amount.policies.PolicyResolver` backed by
        the built-in ``policy/italy.json`` file.
    """
    raw = read_resource("policy/italy.json")
    data: list[dict[str, object]] = json.loads(raw)
    return PolicyResolver([_Rule.from_dict(r) for r in data])
