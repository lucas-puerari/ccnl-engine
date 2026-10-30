"""Report how complete the model of every CCNL is, apart from its readiness.

A CCNL is complete when its census lists its requirements and nothing the
model owes it is open: no requirement row still open, no weak payable rule
(``assumed`` or ``missing``) it reads, no open limitation with a monetary
impact, none whose fact has no input (``outside_input``), and no capability
the engine leaves to the caller or does not compute.  Readiness, the review
of the sources, and the comparison with real payslips are separate axes:
the report shows readiness for reference only and never derives one from
the other.

A requirement row is open when its rule is ``absent`` or ``unverified``,
when an implemented row names no scenario, or when a limitation it links is
still open or a rule it links is still weak.  A scenario, a limitation or a
rule a row names and the bundle does not hold is a census error.

Usage::

    uv run python scripts/completeness/report.py           # write the page
    uv run python scripts/completeness/report.py --check   # fail on drift
    uv run python scripts/completeness/report.py --strict  # fail if incomplete

``--strict`` fails while any CCNL is incomplete: it is the gate of the
completion plan, not of every pull request.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ccnl_engine.agreement.census.loaders import load_census
from ccnl_engine.agreement.census.models import RuleState
from ccnl_engine.capability.loaders import load_capability_catalog
from ccnl_engine.capability.registry.models import CapabilityImplementation
from ccnl_engine.capability.support.services import ccnl_capabilities
from ccnl_engine.catalog.loaders import list_contracts, load_ccnl
from ccnl_engine.limitation.loaders import load_engine_limitations
from ccnl_engine.limitation.models import (
    LimitationStatus,
    LimitationTrigger,
    ModelLimitation,
)
from ccnl_engine.sector.raw.loaders import supported_tax_years
from scripts.provenance.rules import PayableRule, inventory

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from ccnl_engine.agreement.census.models import Census
    from ccnl_engine.agreement.facade import CCNL

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "trust" / "completeness.md"
WEAK = frozenset({"assumed", "missing"})
#: Implementations that leave an amount to the caller or do not compute it.
NOT_NATIVE = frozenset({
    CapabilityImplementation.CALLER_SUPPLIED,
    CapabilityImplementation.PARTIAL,
    CapabilityImplementation.UNSUPPORTED,
})
#: Census states whose rule is still open.
OPEN_STATES = frozenset({RuleState.ABSENT, RuleState.UNVERIFIED})
REFERENCE_CASES = (
    ROOT / "tests" / "knowledge" / "ccnl_engine" / "period" / "reference_case"
)


@dataclass(frozen=True)
class Weakness:
    """The weak payable rules of the bundle, by the CCNLs that read them.

    Attributes:
        ids: Every weak rule as ``<file>#<path>``.
        by_ccnl: Weak rules of each CCNL file, by slug.
        by_sector: Weak rules of the yearly INPS and sector files, by
            INPS sector.
        common: Weak rules of the files every CCNL reads.
    """

    ids: frozenset[str]
    by_ccnl: Mapping[str, int]
    by_sector: Mapping[str, int]
    common: int


def rule_id(rule: PayableRule) -> str:
    """Return the id a census row links a payable rule by.

    Returns:
        ``<file>#<path>``.
    """
    return f"{rule.file}#{rule.path}"


def weakness(rules: Iterable[PayableRule]) -> Weakness:
    """Return the weak rules of *rules*, split by the CCNLs that read them.

    Returns:
        The weak rules by CCNL, by INPS sector and common to every CCNL.
    """
    weak = [rule for rule in rules if rule.status in WEAK]
    by_ccnl: Counter[str] = Counter()
    by_sector: Counter[str] = Counter()
    common = 0
    for rule in weak:
        parts = Path(rule.file).with_suffix("").parts
        if parts[0] == "agreement":
            by_ccnl[parts[-1]] += 1
        elif parts[0] in {"contribution", "sector"}:
            by_sector[parts[-1]] += 1
        else:
            common += 1
    return Weakness(frozenset(map(rule_id, weak)), by_ccnl, by_sector, common)


@dataclass(frozen=True)
class CcnlCompleteness:
    """How complete the model of one CCNL is.

    Attributes:
        ccnl_id: Slug of the CCNL.
        family: Its contract family.
        readiness: Its readiness tier, shown apart, never used.
        census_rows: Requirement rows of its census, ``None`` without one.
        open_rows: Ids of the rows still open.
        census_errors: Scenarios, limitations or rules the census names
            and the bundle does not hold.
        weak_rules: Weak rules of the CCNL file.
        shared_weak_rules: Weak rules of the shared files the CCNL reads.
        limitations: Open limitations with a monetary impact that a run
            can meet.
        outside_input: Open limitations whose fact has no input.
        capabilities: Capabilities left to the caller, partial or not
            computed for the CCNL.
    """

    ccnl_id: str
    family: str
    readiness: str
    census_rows: int | None
    open_rows: tuple[str, ...]
    census_errors: tuple[str, ...]
    weak_rules: int
    shared_weak_rules: int
    limitations: tuple[str, ...]
    outside_input: tuple[str, ...]
    capabilities: tuple[str, ...]

    @property
    def gaps(self) -> tuple[str, ...]:
        """Every reason the CCNL is not complete, empty when it is."""
        found = [
            "census missing" if self.census_rows is None else "",
            _count("open requirement", len(self.open_rows)),
            _count("census error", len(self.census_errors)),
            _count("weak rule", self.weak_rules),
            _count("shared weak rule", self.shared_weak_rules),
            _count("monetary limitation", len(self.limitations)),
            _count("outside_input limitation", len(self.outside_input)),
            _count(
                "non-native capability",
                len(self.capabilities),
                "non-native capabilities",
            ),
        ]
        return tuple(gap for gap in found if gap)

    @property
    def complete(self) -> bool:
        """Whether nothing the model owes the CCNL is open."""
        return not self.gaps


def _count(what: str, n: int, plural: str = "") -> str:
    """Return a count of *what*.

    Returns:
        ``"<n> <what>"``, pluralised, or ``""`` for zero.
    """
    if not n:
        return ""
    return f"{n} {what if n == 1 else plural or what + 's'}"


def _blocking(limitation: ModelLimitation) -> bool:
    return limitation.status is LimitationStatus.OPEN and limitation.blocks


def ccnl_limitations(
    ccnl: CCNL, engine: Iterable[ModelLimitation]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return the open monetary limitations of *ccnl*, by whether a run meets them.

    The limitations the CCNL declares and the engine ones that list it.

    Returns:
        The ids a run can meet and the ids whose fact has no input.
    """
    ccnl_id = ccnl.meta.ccnl_id
    own = (lim for lim in ccnl.limitations if _blocking(lim))
    shared = (lim for lim in engine if _blocking(lim) and ccnl_id in lim.rulesets)
    met: list[str] = []
    outside: list[str] = []
    for limitation in (*own, *shared):
        trigger = limitation.applies_when.trigger
        (outside if trigger is LimitationTrigger.OUTSIDE_INPUT else met).append(
            limitation.id
        )
    return tuple(met), tuple(outside)


def non_native(ccnl: CCNL, years: Iterable[int]) -> tuple[str, ...]:
    """Return the capabilities the engine does not compute natively for *ccnl*.

    Returns:
        Capability names, sorted, over every supported year.
    """
    found = {
        row.feature
        for year in years
        for row in ccnl_capabilities(load_capability_catalog(year), ccnl)
        if row.implementation in NOT_NATIVE
    }
    return tuple(sorted(found))


def scenario_exists(scenario: str, root: Path = ROOT) -> bool:
    """Return whether a scenario a census row names exists.

    A scenario is a pytest node id (``tests/...py::test_name``) or a
    reference case id (``reference_case:<name>``).

    Returns:
        ``True`` when the test function or the case file is there.
    """
    kind, _, name = scenario.partition(":")
    if kind == "reference_case":
        return (REFERENCE_CASES / f"{name}.json").is_file()
    file, _, node = scenario.partition("::")
    path = root / file
    test = node.split("::")[-1].split("[")[0]
    return bool(test) and path.is_file() and f"def {test}(" in path.read_text("utf-8")


@dataclass(frozen=True)
class Evidence:
    """What the census rows are checked against.

    Attributes:
        weakness: The weak rules of the bundle.
        rules: Every payable rule id of the bundle.
        limitations: Every limitation id, of the CCNLs and of the engine.
        open_limitations: The ids of the limitations still open.
    """

    weakness: Weakness
    rules: frozenset[str]
    limitations: frozenset[str]
    open_limitations: frozenset[str]


def census_state(
    census: Census, evidence: Evidence
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return the open rows of *census* and the objects it names that do not exist.

    Returns:
        The ids of the open rows, and one message per missing scenario,
        limitation or rule.
    """
    open_rows: list[str] = []
    errors: list[str] = []
    for row in census.requirements:
        links = row.links
        errors.extend(
            f"{row.id}: no scenario {s}"
            for s in row.scenarios
            if not scenario_exists(s)
        )
        errors.extend(
            f"{row.id}: no limitation {i}"
            for i in links.limitations
            if i not in evidence.limitations
        )
        errors.extend(
            f"{row.id}: no rule {r}" for r in links.rules if r not in evidence.rules
        )
        if (
            row.state in OPEN_STATES
            or (row.state is RuleState.IMPLEMENTED and not row.scenarios)
            or evidence.open_limitations.intersection(links.limitations)
            or evidence.weakness.ids.intersection(links.rules)
        ):
            open_rows.append(row.id)
    return tuple(open_rows), tuple(errors)


def _sectors(ccnl: CCNL) -> frozenset[str]:
    meta = ccnl.meta
    return frozenset(meta.inps_sectors or {meta.tax_sector})


def assess(
    ccnl: CCNL,
    evidence: Evidence,
    engine: Iterable[ModelLimitation],
    years: Iterable[int],
) -> CcnlCompleteness:
    """Return how complete the model of *ccnl* is.

    Returns:
        Its census state, weak rules, limitations and capabilities.
    """
    meta = ccnl.meta
    census = load_census(meta.ccnl_id)
    open_rows, errors = ((), ()) if census is None else census_state(census, evidence)
    met, outside = ccnl_limitations(ccnl, engine)
    weak = evidence.weakness
    return CcnlCompleteness(
        ccnl_id=meta.ccnl_id,
        family=meta.family.id,
        readiness=str(ccnl.verification.readiness),
        census_rows=None if census is None else len(census.requirements),
        open_rows=open_rows,
        census_errors=errors,
        weak_rules=weak.by_ccnl.get(meta.ccnl_id, 0),
        shared_weak_rules=weak.common
        + sum(weak.by_sector.get(sector, 0) for sector in _sectors(ccnl)),
        limitations=met,
        outside_input=outside,
        capabilities=non_native(ccnl, years),
    )


@dataclass(frozen=True)
class Report:
    """The completeness of every CCNL and the totals of the bundle.

    Attributes:
        rows: One per CCNL, sorted by slug.
        weak_rules: Weak payable rules of the bundle.
        open_limitations: Open limitations, each counted once.
        monetary_limitations: Those of them with a monetary impact.
    """

    rows: tuple[CcnlCompleteness, ...]
    weak_rules: int
    open_limitations: int
    monetary_limitations: int

    @property
    def complete(self) -> tuple[CcnlCompleteness, ...]:
        """The complete CCNLs."""
        return tuple(row for row in self.rows if row.complete)

    @property
    def census_errors(self) -> tuple[str, ...]:
        """Every census error, prefixed by its CCNL."""
        return tuple(f"{r.ccnl_id}/{e}" for r in self.rows for e in r.census_errors)


def build_report() -> Report:
    """Assess every bundled CCNL.

    Returns:
        The report of the bundle.
    """
    rules = inventory()
    ccnls = [load_ccnl(summary.ccnl_id) for summary in list_contracts()]
    engine = load_engine_limitations()
    every = (*engine, *(lim for ccnl in ccnls for lim in ccnl.limitations))
    opened = [lim for lim in every if lim.status is LimitationStatus.OPEN]
    evidence = Evidence(
        weakness=weakness(rules),
        rules=frozenset(map(rule_id, rules)),
        limitations=frozenset(lim.id for lim in every),
        open_limitations=frozenset(lim.id for lim in opened),
    )
    years = supported_tax_years()
    return Report(
        rows=tuple(assess(ccnl, evidence, engine, years) for ccnl in ccnls),
        weak_rules=len(evidence.weakness.ids),
        open_limitations=len(evidence.open_limitations),
        monetary_limitations=sum(1 for lim in opened if lim.blocks),
    )


_HEADER = """\
# Model completeness

<!-- Generated by scripts/completeness/report.py; do not edit by hand. -->

Whether the model of each CCNL is complete, so that only the comparison
with real payslips is left. A CCNL is complete when its census lists its
requirements and nothing the model owes it is open: no open requirement,
no weak payable rule (`assumed` or `missing`) it reads, no open limitation
with a monetary impact, none whose fact has no input (`outside_input`),
and no capability left to the caller, partial or not computed.
Completeness is not readiness and not external validation: readiness is
shown for reference only, and
[the validation matrix](validation-matrix.md) tracks the comparisons.
`scripts/completeness/report.py --strict` fails while any CCNL is
incomplete.
"""


def render(report: Report) -> str:
    """Return the Markdown page of *report*.

    Returns:
        The page, ending with a newline.
    """
    lines = [
        _HEADER,
        (
            f"**Complete: {len(report.complete)}/{len(report.rows)} CCNLs.** "
            f"Bundle: {report.weak_rules} weak rules, {report.open_limitations} "
            f"open limitations ({report.monetary_limitations} with a monetary "
            "impact)."
        ),
        "",
        "| CCNL | Family | Readiness | Census | Gaps |",
        "|---|---|---|---|---|",
    ]
    for row in report.rows:
        census = "missing" if row.census_rows is None else f"{row.census_rows} rows"
        gaps = "; ".join(row.gaps) or "complete"
        lines.append(
            f"| [{row.ccnl_id}](../contracts/{row.ccnl_id}.md) | `{row.family}` "
            f"| {row.readiness} | {census} | {gaps} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Write the page, or check it with ``--check`` or ``--strict``.

    Returns:
        ``0`` on success; ``1`` on drift, on a census error, or with
        ``--strict`` while a CCNL is incomplete.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on drift")
    parser.add_argument("--strict", action="store_true", help="fail if incomplete")
    args = parser.parse_args(argv)
    report = build_report()
    for error in report.census_errors:
        print(f"census error: {error}")
    text = render(report)
    status = 1 if report.census_errors else 0
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text("utf-8") != text:
            print(f"FAIL: {OUTPUT.relative_to(ROOT)} is out of date: run {__file__}")
            status = 1
    else:
        OUTPUT.write_text(text, encoding="utf-8")
    complete = len(report.complete)
    print(f"Complete: {complete}/{len(report.rows)} CCNLs.")
    if args.strict and complete < len(report.rows):
        status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
