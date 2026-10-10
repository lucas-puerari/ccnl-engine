"""Generate one usage example per bundled CCNL in docs/examples/contracts/.

Each contract page embeds its example (see ``gen_contract_pages.py``), and
``tests/acceptance/public_api/test_docs_examples.py`` runs every one of them.
The examples are built from the CCNL and INPS data only, never from engine
output, so the same data always yields the same files.

Rules of every example:

- level: the middle entry of the ``levels`` list of the CCNL JSON,
  ``levels[len(levels) // 2]``;
- run: the regular run of September 2026, paid on 25 September 2026; every
  2026 salary tranche of the bundle starts on or before that month;
- employment: full-time, permanent;
- employer: 50 employees; one for domestic CCNLs, whose employer is a
  household;
- geography: worker resident in Milan (region ``IT-25``, Belfiore ``F205``);
- worker category: ``operaio`` when the level fixes none and the INPS
  employer rate of the sector depends on the category, so the example does
  not rest on an assumed rate; when the seniority increments of the level
  exist only per category, ``operaio`` if it is paid them, otherwise the
  first category that is;
- seniority: recognised from 1 September 2026, a new hire, so the run
  states the fact its increments need and no increment is due;
- domestic CCNLs: weekly hours, stated as the full time too, and
  contributable hours of a full-time month, both derived from the
  ``hourly_divisor`` of the CCNL.

Run with::

    uv run python scripts/documentation/generate_contract_examples.py

Check for drift without writing (for CI)::

    uv run python scripts/documentation/generate_contract_examples.py --check
"""

from __future__ import annotations

import json
import operator
import sys
import textwrap
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE = ROOT / "src" / "ccnl_engine" / "knowledge"
CCNL_DIR = KNOWLEDGE / "contract" / "agreement"
INPS_DIR = KNOWLEDGE / "social_security" / "contribution"
OUT_DIR = ROOT / "docs" / "examples" / "contracts"
PACKAGE_INIT = "__init__.py"

YEAR = 2026
MONTH = 9
MONTH_NAME = "September"
PAYMENT_DAY = 25
HEADCOUNT = 50
DOMESTIC_HEADCOUNT = 1
DOMESTIC_SECTOR = "lavoro-domestico"
DEFAULT_CATEGORY = "OPERAIO"
REGION = "IT-25"
MUNICIPALITY = "F205"
WEEKS_PER_MONTH = Decimal(52) / Decimal(12)
DOCSTRING_WIDTH = 76


@dataclass(frozen=True)
class ExampleSpec:
    """Inputs of one generated example, all taken from the bundled data.

    Attributes:
        slug: CCNL identifier, the JSON file name without extension.
        name: Display name of the CCNL.
        cnel_code: CNEL code of the CCNL.
        level_code: Level of the example.
        category: ``WorkerCategory`` member to declare, or ``None``.
        weekly_hours: Weekly hours for a domestic CCNL, else ``None``.
        contributable_hours: Monthly contributable hours for a domestic
            CCNL, else ``None``.
    """

    slug: str
    name: str
    cnel_code: str
    level_code: str
    category: str | None
    weekly_hours: int | None
    contributable_hours: int | None

    @property
    def domestic(self) -> bool:
        """Whether the CCNL is a domestic-work contract."""
        return self.contributable_hours is not None


def _read_json(path: Path) -> dict[str, Any]:
    """Read one JSON object from ``path``.

    Returns:
        The decoded object.

    Raises:
        TypeError: When the file does not hold a JSON object.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"{path} does not hold a JSON object"
        raise TypeError(msg)
    return data


def _rates_by_category(tax_sector: str) -> bool:
    """Whether the INPS employer rate of ``tax_sector`` depends on category.

    Returns:
        ``True`` when an employer tier of the year sets ``rate_by_category``.
    """
    path = INPS_DIR / str(YEAR) / f"{tax_sector}.json"
    if not path.exists():
        return False
    tiers = _read_json(path).get("inps", {}).get("employer_tiers", [])
    return any(tier.get("rate_by_category") for tier in tiers)


def _latest_divisor(parameters: dict[str, Any]) -> Decimal:
    """Return the latest monthly hourly divisor of a domestic CCNL.

    Returns:
        The divisor of the most recent period.

    Raises:
        ValueError: When the CCNL has no ``hourly_divisor`` period.
    """
    periods = parameters.get("hourly_divisor", {}).get("periods", [])
    if not periods:
        msg = "domestic CCNL without hourly_divisor periods"
        raise ValueError(msg)
    latest = max(periods, key=operator.itemgetter("valid_from"))
    return Decimal(str(latest["value"]))


def _seniority_category(increments: dict[str, Any], level_code: str) -> str | None:
    """Return the category the seniority increments of a level need.

    Returns:
        ``None`` when the level has a category-independent amount or no
        category amount; otherwise ``operaio`` when it is paid on the
        level, else the first category that is, as a member name.
    """
    by_category = increments.get("amount_by_level_by_category", {})
    paid = [cat for cat, amounts in by_category.items() if level_code in amounts]
    if level_code in increments.get("amount_by_level", {}) or not paid:
        return None
    default = DEFAULT_CATEGORY.lower()
    return (default if default in paid else paid[0]).upper()


def build_spec(path: Path) -> ExampleSpec:
    """Derive the example inputs of the CCNL stored at ``path``.

    Returns:
        The inputs of its example.

    Raises:
        ValueError: When the CCNL has no level.
    """
    data = _read_json(path)
    meta = data.get("meta", {})
    levels = data.get("levels", [])
    if not levels:
        msg = f"{path.name} has no level"
        raise ValueError(msg)
    level = levels[len(levels) // 2]
    tax_sector = meta.get("tax_sector", "")
    category = None
    if level.get("category") is None:
        category = _seniority_category(
            data.get("parameters", {}).get("seniority_increments", {}),
            str(level["code"]),
        )
        if category is None and _rates_by_category(tax_sector):
            category = DEFAULT_CATEGORY
    weekly_hours = contributable_hours = None
    if tax_sector == DOMESTIC_SECTOR:
        divisor = _latest_divisor(data.get("parameters", {}))
        weekly = (divisor / WEEKS_PER_MONTH).quantize(Decimal(1), ROUND_HALF_UP)
        weekly_hours, contributable_hours = int(weekly), int(divisor)
    return ExampleSpec(
        slug=path.stem,
        name=str(meta.get("name", path.stem)),
        cnel_code=str(meta.get("cnel_code", "")),
        level_code=str(level["code"]),
        category=category,
        weekly_hours=weekly_hours,
        contributable_hours=contributable_hours,
    )


def _docstring(spec: ExampleSpec) -> str:
    """Build the module docstring of an example.

    Returns:
        The docstring, quotes included, ending with a newline.
    """
    name = spec.name.replace("\\", "/").replace('"', "'").replace("\u2014", "-")
    code = f" ({spec.cnel_code})" if spec.cnel_code else ""
    employer = "a household employer" if spec.domestic else f"{HEADCOUNT} employees"
    scenario = (
        f"Level {spec.level_code} (middle of the level list), regular run of "
        f"September {YEAR}, full-time permanent employment, {employer}, "
        f"worker resident in Milan (region {REGION}, municipality "
        f"{MUNICIPALITY}), seniority recognised from 1 {MONTH_NAME} {YEAR}."
    )
    paragraphs = [
        f"{name}.",
        (
            "Generated by scripts/documentation/generate_contract_examples.py from the "
            "bundled data; edit the generator, not this file."
        ),
        scenario,
    ]
    if spec.category is not None:
        paragraphs.append(
            f"The worker category is declared ({spec.category.lower()}): the "
            "INPS employer rate or the seniority increments depend on it."
        )
    if spec.domestic:
        paragraphs.append(
            f"Domestic work: {spec.weekly_hours} weekly hours and "
            f"{spec.contributable_hours} contributable hours in the month; "
            "the household employer withholds no IRPEF."
        )
    wrapped = [
        "\n".join(textwrap.wrap(p, DOCSTRING_WIDTH, break_on_hyphens=False))
        for p in paragraphs
    ]
    summary = f"Usage example: {spec.slug}{code}."
    return '"""' + summary + "\n\n" + "\n\n".join(wrapped) + '\n"""\n'


def _imports(spec: ExampleSpec) -> str:
    """Build the import block of an example.

    Returns:
        The import statements, ending with a newline.
    """
    root = {
        "EmployerProfile",
        "Employment",
        "Headcount",
        "PayrollEngine",
        "PayrollRun",
        "PeriodFacts",
        "PeriodInput",
    }
    inputs = {"Permanent", "SeniorityFact", "SenioritySource"}
    if spec.category is not None:
        inputs.add("WorkerCategory")
    if spec.domestic:
        inputs.update({"ContributableHours", "WeeklyHours"})
    stdlib = "from datetime import date\n"
    if spec.domestic:
        stdlib += "from decimal import Decimal\n"
    return f"{stdlib}\n{_import_block('ccnl_engine', root)}" + _import_block(
        "ccnl_engine.inputs", inputs
    )


def _import_block(module: str, names: set[str]) -> str:
    """Build one ``from module import (...)`` statement.

    Returns:
        The statement, one name per line, ending with a newline.
    """
    listed = "".join(f"    {name},\n" for name in sorted(names))
    return f"from {module} import (\n{listed})\n"


def _call(spec: ExampleSpec) -> str:
    """Build the engine call of an example.

    Returns:
        The call statements, ending with a newline.
    """
    employment = [
        "ccnl_slug=CCNL",
        "level_code=LEVEL",
        "contract_type=Permanent()",
        "seniority=SENIORITY",
    ]
    facts = [f'regione="{REGION}"', f'comune_belfiore="{MUNICIPALITY}"']
    headcount = HEADCOUNT
    if spec.category is not None:
        employment.append(f"category=WorkerCategory.{spec.category}")
    if spec.domestic:
        hours = f"WeeklyHours({spec.weekly_hours})"
        employment.extend((
            f"weekly_hours={hours}",
            f"full_time_weekly_hours={hours}",
        ))
        facts.insert(
            0,
            "contributable_hours=ContributableHours("
            f"Decimal({spec.contributable_hours}))",
        )
        headcount = DOMESTIC_HEADCOUNT
    employment_args = "".join(f"            {arg},\n" for arg in employment)
    facts_args = "".join(f"            {arg},\n" for arg in facts)
    return (
        "engine = PayrollEngine.bundled()\n"
        "result = engine.calculate_period(\n"
        "    PeriodInput(\n"
        f"        run=PayrollRun.regular(year={YEAR}, month={MONTH}),\n"
        f"        payment_date=date({YEAR}, {MONTH}, {PAYMENT_DAY}),\n"
        f"        employment=Employment(\n{employment_args}        ),\n"
        f"        employer=EmployerProfile(headcount=Headcount({headcount})),\n"
        f"        facts=PeriodFacts(\n{facts_args}        ),\n"
        "    )\n"
        ")\n"
    )


_REPORT = """\
issues = ", ".join(sorted(issue.code for issue in result.issues)) or "none"
blockers = ", ".join(sorted({b.code.value for b in result.blockers})) or "none"
readiness = engine.inspect_ruleset(CCNL.removesuffix(".json")).readiness
print(f"Gross:         {result.period_gross} EUR")
print(f"Contributions: {result.contribution_breakdown.employee} EUR")
print(f"IRPEF:         {result.tax_computation.ordinary_tax} EUR")
print(f"Net:           {result.period_net} EUR")
print(f"Payable:       {result.is_payable}")
print(f"Readiness:     {readiness}")
print(f"Blockers:      {blockers}")
print(f"Issues:        {issues}")
"""


def render_example(spec: ExampleSpec) -> str:
    """Render the Python source of the example described by ``spec``.

    Returns:
        The full source, ending with a newline.
    """
    constants = (
        f'CCNL = "{spec.slug}.json"\nLEVEL = "{spec.level_code}"\n'
        f"SENIORITY = SeniorityFact.since(date({YEAR}, {MONTH}, 1), "
        "SenioritySource.EMPLOYER_RECORDS)\n"
    )
    return "\n".join((
        _docstring(spec),
        _imports(spec),
        constants,
        _call(spec),
        _REPORT,
    ))


def expected_examples() -> dict[str, str]:
    """Render the example of every bundled CCNL.

    Returns:
        Mapping of example file name to its source, sorted by name.
    """
    return {
        f"{path.stem}.py": render_example(build_spec(path))
        for path in sorted(CCNL_DIR.glob("*.json"))
    }


def _committed_examples() -> set[str]:
    """Return the example file names currently in ``OUT_DIR``.

    Returns:
        File names, the package ``__init__.py`` excluded.
    """
    return {p.name for p in OUT_DIR.glob("*.py") if p.name != PACKAGE_INIT}


def drift(expected: dict[str, str]) -> list[str]:
    """List the differences between ``expected`` and the committed files.

    Returns:
        One line per missing, stale or orphan example; empty when none.
    """
    problems: list[str] = []
    committed = _committed_examples()
    for name, source in expected.items():
        path = OUT_DIR / name
        if name not in committed:
            problems.append(f"missing: {name}")
        elif path.read_text(encoding="utf-8") != source:
            problems.append(f"stale: {name}")
    problems.extend(f"orphan: {name}" for name in sorted(committed - set(expected)))
    return problems


def write(expected: dict[str, str]) -> None:
    """Write every example and remove examples of CCNLs no longer bundled."""
    for name in sorted(_committed_examples() - set(expected)):
        (OUT_DIR / name).unlink()
    for name, source in expected.items():
        (OUT_DIR / name).write_text(source, encoding="utf-8")


def main() -> None:
    """Write the examples, or check them for drift with ``--check``."""
    expected = expected_examples()
    if "--check" not in sys.argv:
        write(expected)
        print(f"Written {len(expected)} examples to {OUT_DIR}.")
        return
    problems = drift(expected)
    if problems:
        print("docs/examples/contracts/ is out of date:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "Run: uv run python scripts/documentation/generate_contract_examples.py",
            file=sys.stderr,
        )
        print("and commit the result.", file=sys.stderr)
        sys.exit(1)
    print(f"OK: docs/examples/contracts/ is up to date ({len(expected)} examples).")


if __name__ == "__main__":
    main()
