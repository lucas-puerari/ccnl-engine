"""Load the bundled pay-item policy ruleset into a :class:`PolicyResolver`."""

from __future__ import annotations

import importlib.resources
import json

from ccnl_engine.knowledge.service.bundled import read_bundled
from ccnl_engine.payroll.domain.policy import PolicyResolver, _Rule

__all__ = ["load_policy_resolver"]


def load_policy_resolver() -> PolicyResolver:
    """Load the bundled Italian ruleset from ``knowledge/policies/data/``.

    Returns:
        A :class:`~ccnl_engine.payroll.domain.policy.PolicyResolver` backed by
        the built-in ``it.json`` file.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.policies.data")
    raw = read_bundled(pkg, "it.json")
    data: list[dict[str, object]] = json.loads(raw)
    return PolicyResolver([_Rule.from_dict(r) for r in data])
