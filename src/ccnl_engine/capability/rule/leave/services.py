"""The CCNL rules the leave of a run read: accrual, leave taken, residual."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.capability.rule.services import Rule
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.provenance.ruleset.models import RulesetIdentity
    from ccnl_engine.provenance.source.rule.models import RuleProvenance


def _name(ruleset: RulesetIdentity | None, fallback: str) -> str:
    return fallback if ruleset is None else ruleset.id


def _provenance(block: object) -> RuleProvenance | None:
    provenance: RuleProvenance | None = getattr(block, "provenance", None)
    return provenance


def _leave_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the CCNL leave rules the accrual and the leave taken read.

    Returns:
        ``<ccnl>:work_rules.leave_rules`` with its record, then the ferie
        accrual and each permit bucket with theirs.
    """
    ccnl = ctx.contract.ccnl
    name = _name(ccnl.ruleset, f"ccnl/{ccnl.meta.ccnl_id}")
    work = ccnl.work_rules
    rules = None if work is None else work.leave_rules
    prefix = f"{name}:work_rules.leave_rules"
    if rules is None:
        return ((prefix, None),)
    blocks: list[tuple[str, object]] = [
        ("", rules),
        (".ferie_accrual", rules.ferie_accrual),
    ]
    for permit in rules.permits:
        blocks.extend((
            (f".permits[{permit.bucket}]", permit),
            (f".permits[{permit.bucket}].ramp", permit.ramp),
        ))
    return tuple(
        (f"{prefix}{path}", _provenance(block))
        for path, block in blocks
        if block is not None
    )


def _termination_leave_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the leave rules and the basis of the residual paid.

    Returns:
        The rules of :func:`_leave_rules` and
        ``<ccnl>:work_rules.leave_rules.termination`` with its record.
    """
    ccnl = ctx.contract.ccnl
    name = _name(ccnl.ruleset, f"ccnl/{ccnl.meta.ccnl_id}")
    work = ccnl.work_rules
    rules = None if work is None else work.leave_rules
    basis = None if rules is None else rules.termination
    return (
        *_leave_rules(ctx),
        (
            f"{name}:work_rules.leave_rules.termination",
            None if basis is None else basis.provenance,
        ),
    )
