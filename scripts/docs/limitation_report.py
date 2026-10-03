"""Render the model limitations of a CCNL for its documentation page.

The "Known simplifications" section of a contract page is generated from the
limitation registry: the limitations the simplification notes of the CCNL
declare, then the engine limitations whose rulesets include it.  The
simplification notes without a monetary impact follow, as plain notes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.identity import NoteKind
from ccnl_engine.knowledge.service.limitation_loader import load_engine_limitations

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.shared.domain.limitation import LimitationScope, ModelLimitation

_INTRO = (
    "Each simplification below is a model limitation of the registry. An open "
    "limitation with a monetary impact (`yes` or `unknown`) makes every result "
    "it applies to not payable, with an `open_limitation` blocker; the result "
    "lists every applicable limitation in `assurance.limitations`."
)


def ccnl_registry(ccnl: CCNL) -> tuple[ModelLimitation, ...]:
    """Return the limitations of the registry that concern *ccnl*.

    Returns:
        The limitations of its notes, then the engine limitations whose
        rulesets include it.
    """
    engine = tuple(
        lim for lim in load_engine_limitations() if ccnl.meta.ccnl_id in lim.rulesets
    )
    return (*ccnl.limitations, *engine)


def _scope_text(capability: str, scope: LimitationScope) -> str:
    if scope.trigger == "outside_input":
        return "a fact the request cannot express: never recorded on a run"
    parts = [f"`{capability}` applies"]
    if scope.trigger == "path":
        parts.append("the run takes the engine code path")
    for label, values in (
        ("contract type", scope.contract_types),
        ("level", scope.levels),
        ("category", scope.worker_categories),
        ("run kind", scope.run_kinds),
    ):
        if values is not None:
            parts.append(f"{label} in {', '.join(sorted(values))}")
    if scope.seniority_months_from is not None:
        parts.append(f"seniority of at least {scope.seniority_months_from} months")
    if scope.effective_from is not None:
        parts.append(f"from {scope.effective_from.isoformat()}")
    if scope.effective_until is not None:
        parts.append(f"before {scope.effective_until.isoformat()}")
    return "; ".join(parts)


def _limitation_block(lim: ModelLimitation) -> list[str]:
    kind = "warning" if lim.blocks else "note"
    title = f"{lim.id} · {lim.capability} · impact {lim.monetary_impact} · {lim.status}"
    return [
        f'!!! {kind} "{title}"',
        *(f"    {line}" for line in lim.summary.splitlines()),
        "",
        f"    **Applies when:** {_scope_text(lim.capability, lim.applies_when)}.",
        "",
        f"    **Remediation:** {lim.remediation}",
        "",
    ]


def limitation_lines(ccnl: CCNL) -> list[str]:
    """Render the Known simplifications section of the page of *ccnl*.

    Returns:
        Markdown lines, empty when the CCNL has no simplification.
    """
    registry = ccnl_registry(ccnl)
    plain = [
        note.text
        for note in ccnl.coverage.notes
        if note.kind is NoteKind.SIMPLIFICATION and note.limitation is None
    ]
    if not registry and not plain:
        return []
    lines = ["## Known simplifications", "", _INTRO, ""]
    for lim in registry:
        lines.extend(_limitation_block(lim))
    if plain:
        lines.extend(["### Without monetary impact", ""])
        for text in plain:
            lines.append('!!! note ""')
            lines.extend(f"    {line}" for line in text.splitlines())
            lines.append("")
    return lines
