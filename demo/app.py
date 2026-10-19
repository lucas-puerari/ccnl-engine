# ruff: file-ignore[implicit-namespace-package]
"""ccnl-engine Pyodide glue: runs in the browser via Pyodide.

Every public function returns a JSON string, so that values cross the
Python/JS boundary without type ambiguity (Decimal, date, ...).  The demo
computes a whole competence year: the annual figures are the sum of its runs,
never a month multiplied by the number of monthly payments.
"""

from __future__ import annotations

import json
import operator
from collections import defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
)
from ccnl_engine.bundle.loaders import read_resource
from ccnl_engine.catalog import RulesetKind
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.inputs import (
    Apprentice,
    ContributableHours,
    ContributionHistory,
    FixedTerm,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)
from ccnl_engine.surtax.jurisdiction.types import REGION_CODES
from ccnl_engine.surtax.loaders import load_surtax_rules

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

#: First day of the cohort the IVS massimale applies to (L. 335/1995 art. 2 c. 18).
_IVS_COHORT_START = date(1996, 1, 1)
#: Weeks in a month, for the contributable hours of a domestic worker.
_WEEKS_PER_MONTH = Decimal(52) / Decimal(12)
_CENT = Decimal("0.01")
#: Ledger accounts the breakdown sums over the year.
_ACCOUNTS = (
    "employee_contributions",
    "ordinary_tax",
    "surtax",
    "credits",
    "bilateral_fund_employee",
    "pension_fund_employee",
    "employer_contributions",
    "bilateral_fund_employer",
    "pension_fund_employer",
    "tfr_accrual",
)
_EARNINGS = {
    "base_salary_earning": "base_salary",
    "seniority_earning": "seniority",
    "fixed_allowance_earning": "allowance",
    "conditional_allowance_earning": "allowance",
}


def _latest_bundled_year() -> int:
    """Return the most recent year fully covered by all knowledge families.

    Walks back from the current calendar year until it finds a year for which
    tax, INPS, and surtax data all exist in the bundle.  This prevents the
    demo from attempting a calculation with, e.g., surtax data for year N+1
    while tax and INPS data only go up to N.

    Returns:
        The latest year covered by all three rule families.

    Raises:
        RuntimeError: If no complete year is found >= 2020.
    """
    year = datetime.now(UTC).year
    while True:
        try:
            read_resource(f"sector/{year}/industria.json")
            read_resource(f"contribution/{year}/industria.json")
            read_resource(f"surtax/regional/{year}.json")
        except FileNotFoundError:
            year -= 1
            if year < 2020:
                msg = "No complete bundled data found for any year >= 2020"
                raise RuntimeError(msg) from None
        else:
            return year


_DEFAULT_YEAR = _latest_bundled_year()
_ENGINE = PayrollEngine.bundled()


def list_regioni() -> str:
    """Return JSON list of regions with addizionale regionale data.

    Returns:
        JSON-encoded list of ``{code, name}`` dicts ordered by name, where
        ``code`` is the region code the engine expects.
    """
    surtax = load_surtax_rules(_DEFAULT_YEAR)
    result = sorted(
        [
            {"code": code, "name": name}
            for code, name in REGION_CODES.items()
            if name in surtax.regionale
        ],
        key=operator.itemgetter("name"),
    )
    return json.dumps(result)


def list_comuni() -> str:
    """Return JSON list of comuni with addizionale comunale data.

    Returns:
        JSON-encoded sorted list of ``{code, name}`` dicts, one per comune
        that has a rate in the current year's data, ordered by name.
    """
    surtax = load_surtax_rules(_DEFAULT_YEAR)
    result = sorted(
        [{"code": code, "name": info.nome} for code, info in surtax.comunale.items()],
        key=operator.itemgetter("name"),
    )
    return json.dumps(result)


def list_ccnls() -> str:
    """Return JSON list of all available CCNLs, sorted by name.

    Returns:
        JSON-encoded list of ``{id, name, readiness}`` dicts, one per
        bundled CCNL, from :meth:`PayrollEngine.list_contracts`.
    """
    result = [
        {"id": c.ccnl_id, "name": c.name, "readiness": str(c.readiness)}
        for c in _ENGINE.list_contracts()
    ]
    result.sort(key=operator.itemgetter("name"))
    return json.dumps(result)


def load_ccnl_levels(ccnl_id: str) -> str:
    """Return JSON list of levels for a CCNL.

    Args:
        ccnl_id: Slug of the CCNL (e.g. ``metalmeccanico-federmeccanica``).

    Returns:
        JSON-encoded list of ``{code, description}`` dicts in the order of
        the CCNL.
    """
    return json.dumps([
        {"code": level.code, "description": level.description}
        for level in _ENGINE.list_levels(ccnl_id)
    ])


def load_level_tracks(ccnl_id: str, level_code: str) -> str:
    """Return JSON list of apprenticeship tracks for a given level.

    Args:
        ccnl_id: Slug of the CCNL.
        level_code: Level code within the CCNL.

    Returns:
        JSON-encoded list of track names, ``[]`` when none exist.
    """
    ccnl = load_ccnl(ccnl_id)
    return json.dumps([
        track.name
        for track in ccnl.apprenticeship or []
        if level_code in track.destination_levels
    ])


def _contract(params: dict[str, Any]) -> Permanent | FixedTerm | Apprentice:
    """Return the contract type the parameters name.

    Returns:
        The contract instance of ``params["contract"]``.

    Raises:
        ValueError: When the contract type is not one the demo offers.
    """
    kind = params.get("contract", "permanent")
    if kind == "permanent":
        return Permanent()
    if kind == "fixed_term":
        return FixedTerm()
    if kind == "apprentice":
        return Apprentice(
            months_elapsed=int(params.get("apprentice_months") or 0),
            track=str(params.get("track") or "") or None,
        )
    msg = f"Tipo di contratto non supportato: {kind!r}"
    raise ValueError(msg)


def _hours(params: dict[str, Any]) -> tuple[WeeklyHours | None, WeeklyHours | None]:
    """Return the weekly and full-time weekly hours of the employment.

    Full time with no stated hours is the full time of the CCNL: no hours are
    passed, except for a domestic CCNL, which always needs them.

    Returns:
        ``(weekly_hours, full_time_weekly_hours)``, both ``None`` for a
        full-time employment of a non-domestic CCNL.
    """
    full_time = int(params.get("full_time_hours") or 40)
    pct = int(params.get("part_time_pct") or 100)
    if pct >= 100 and not params.get("domestic"):
        return None, None
    weekly = max(1, round(full_time * pct / 100))
    return WeeklyHours(weekly), WeeklyHours(full_time)


def _employment(params: dict[str, Any], ccnl_id: str) -> Employment:
    """Build the employment from the parameters of the form.

    Returns:
        The :class:`Employment` of the scenario.
    """
    months = params.get("seniority_months")
    seniority = (
        SeniorityFact(
            int(months), date(_DEFAULT_YEAR, 1, 1), SenioritySource.EMPLOYER_RECORDS
        )
        if months not in {None, ""}
        else None
    )
    history = (
        ContributionHistory(first_enrolled_on=_IVS_COHORT_START)
        if params.get("first_enrolled_after_1995")
        else None
    )
    weekly, full_time = _hours(params)
    return Employment(
        ccnl_id=ccnl_id,
        level_code=str(params["level"]),
        contract_type=_contract(params),
        seniority=seniority,
        contribution_history=history,
        weekly_hours=weekly,
        full_time_weekly_hours=full_time,
    )


def _accounts(year: CompetenceYearResult) -> dict[str, float]:
    """Sum the ledger entries of the year per account.

    Returns:
        The annual amount of each account of :data:`_ACCOUNTS`.
    """
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for result in year.period_results:
        for entry in result.ledger_entries:
            totals[entry.account.value] += entry.amount
    return {account: float(totals[account]) for account in _ACCOUNTS}


def _irpef(year: CompetenceYearResult) -> dict[str, float]:
    """Return the annual IRPEF figures the last run of the year settles on.

    Returns:
        ``taxable_income``, ``irpef_gross``, ``work_deduction`` and
        ``ulteriore_detrazione``; empty when no run withholds IRPEF (a
        household employer is not a withholding agent).
    """
    keys = {
        "projected_taxable": "taxable_income",
        "irpef_gross": "irpef_gross",
        "work_deduction": "work_deduction",
        "ulteriore_detrazione": "ulteriore_detrazione",
    }
    for result in reversed(year.period_results):
        for decision in result.decisions:
            if decision.capability == "irpef" and "irpef_gross" in decision.inputs:
                return {
                    name: float(Decimal(str(decision.inputs.get(key, 0))))
                    for key, name in keys.items()
                }
    return {}


def _reference_month(year: CompetenceYearResult) -> PeriodResult:
    """Return the last regular run of the year: the monthly pay shown.

    Returns:
        The result of the last regular run, or the last run of the year.
    """
    regular = [
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind == "regular"
    ]
    return (regular or list(year.period_results))[-1]


def _trace(month: PeriodResult) -> list[dict[str, Any]]:
    """Return the earnings of the reference month, in pay item order.

    Returns:
        One ``{category, code, amount}`` per earning, then the gross.
    """
    steps: list[dict[str, Any]] = [
        {
            "category": _EARNINGS[item.kind],
            "code": getattr(item, "allowance_code", "") or "",
            "amount": float(item.amount),
        }
        for item in month.pay_items
        if item.kind in _EARNINGS and item.amount
    ]
    steps.append({"category": "gross", "code": "", "amount": float(month.period_gross)})
    return steps


def _ruleset(year: CompetenceYearResult) -> dict[str, Any]:
    """Return readiness and confidence of the CCNL ruleset the year read.

    Returns:
        ``{readiness, confidence, production}``; ``readiness`` is ``None``
        when the CCNL has no ruleset identity.
    """
    for ruleset in year.rulesets:
        if ruleset.kind is RulesetKind.CCNL:
            return {
                "readiness": str(ruleset.readiness) if ruleset.readiness else None,
                "confidence": str(ruleset.confidence),
                "production": ruleset.is_production,
            }
    return {"readiness": None, "confidence": None, "production": False}


def _sources(ccnl_id: str) -> list[dict[str, Any]]:
    """Return the documents the CCNL file cites.

    Returns:
        One ``{title, url, kind, date}`` per source; ``url`` is ``None``
        unless it is a public HTTP address.
    """
    meta = load_ccnl(ccnl_id).meta
    return [
        {
            "title": source.title,
            "url": source.url
            if source.url.startswith(("http://", "https://"))
            else None,
            "kind": str(source.kind),
            "date": source.published_on.isoformat() if source.published_on else None,
        }
        for source in meta.sources
    ]


def _facts(params: dict[str, Any], employment: Employment) -> PeriodFacts:
    """Return the facts every run of the year shares.

    A domestic worker is assumed to work and be paid the contractual weekly
    hours in every month.

    Returns:
        The default :class:`PeriodFacts` of the plan.
    """
    hours = (
        ContributableHours(
            (Decimal(employment.weekly_hours.value) * _WEEKS_PER_MONTH).quantize(_CENT)
        )
        if params.get("domestic") and employment.weekly_hours is not None
        else None
    )
    return PeriodFacts(
        regione=str(params.get("regione") or "") or None,
        comune_belfiore=str(params.get("comune") or "") or None,
        contributable_hours=hours,
    )


def compute_salary(params_json: str) -> str:
    """Compute the competence year of a scenario.

    Args:
        params_json: JSON object with ``ccnl`` (slug), ``level``,
            ``contract`` (``permanent``, ``fixed_term`` or ``apprentice``),
            ``headcount``, and optionally ``part_time_pct``,
            ``full_time_hours``, ``seniority_months`` (months of service on
            1 January; ``null`` when not stated), ``apprentice_months``,
            ``track``, ``regione``, ``comune`` and
            ``first_enrolled_after_1995``.

    Returns:
        JSON-encoded result dict or ``{"error": "..."}`` on failure.
    """
    try:
        params: dict[str, Any] = json.loads(params_json)
        ccnl_id = str(params["ccnl"])
        ccnl = load_ccnl(ccnl_id)
        params["domestic"] = not ccnl.meta.withholding_agent
        employment = _employment(params, ccnl_id)
        year = _ENGINE.calculate_competence_year(
            CompetenceYearPlan(
                year=_DEFAULT_YEAR,
                employment=employment,
                employer=EmployerProfile(
                    headcount=Headcount(int(params.get("headcount") or 1))
                ),
                default_facts=_facts(params, employment),
            )
        )
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": str(exc)})
    return json.dumps(_payload(params, ccnl_id, ccnl.meta.name, year))


def _payload(
    params: dict[str, Any],
    ccnl_id: str,
    ccnl_name: str,
    year: CompetenceYearResult,
) -> dict[str, Any]:
    """Return the figures the demo shows for a computed year.

    Returns:
        The JSON-ready result of :func:`compute_salary`.
    """
    month = _reference_month(year)
    runs = len(year.period_results)
    annual_net = float(year.annual_net)
    return {
        "ccnl_id": ccnl_id,
        "ccnl_name": ccnl_name,
        "level_code": params["level"],
        "contract": params.get("contract", "permanent"),
        "part_time_pct": int(params.get("part_time_pct") or 100),
        "year": _DEFAULT_YEAR,
        "engine_version": year.bundle_version or "",
        "runs": runs,
        "monthly_gross": float(month.period_gross),
        "trace": _trace(month),
        "annual_gross": float(year.annual_gross),
        "annual_net": annual_net,
        "net_average": annual_net / runs if runs else 0.0,
        "annual_employer_cost": float(year.annual_employer_cost),
        "accounts": _accounts(year),
        "irpef": _irpef(year),
        "withholding_agent": not params["domestic"],
        "ruleset": _ruleset(year),
        "rulesets": [
            {
                "id": r.identity.id,
                "version": r.identity.version,
                "readiness": str(r.readiness) if r.readiness else None,
                "confidence": str(r.confidence),
            }
            for r in year.rulesets
        ],
        "sources": _sources(ccnl_id),
        "payability": str(year.assurance.payability),
        "blockers": [
            {"code": str(b.code), "feature": b.feature, "detail": b.detail}
            for b in year.blockers
        ],
        "issues": [{"code": i.code, "message": i.message} for i in year.issues],
        "decisions": sorted({(d.capability, str(d.status)) for d in year.decisions}),
    }


def scenario_snippet(params_json: str) -> str:
    """Return the Python code that computes the scenario with the public API.

    Args:
        params_json: The parameters of :func:`compute_salary`.

    Returns:
        JSON-encoded ``{"code": "..."}``: a script that prints the annual
        gross, net and employer cost :func:`compute_salary` shows.
    """
    params: dict[str, Any] = json.loads(params_json)
    ccnl_id = str(params["ccnl"])
    params["domestic"] = not load_ccnl(ccnl_id).meta.withholding_agent
    employment = _employment(params, ccnl_id)
    facts = _facts(params, employment)
    inputs = {"Permanent", "FixedTerm", "Apprentice"} & {
        type(employment.contract_type).__name__
    }
    fields = [
        f"ccnl_id={json.dumps(ccnl_id)}",
        f"level_code={json.dumps(employment.level_code)}",
        f"contract_type={_contract_code(employment)}",
    ]
    if employment.seniority is not None:
        inputs |= {"SeniorityFact", "SenioritySource"}
        fields.append(
            f"seniority=SeniorityFact({employment.seniority.months}, "
            f"date({_DEFAULT_YEAR}, 1, 1), SenioritySource.EMPLOYER_RECORDS)"
        )
    if employment.contribution_history is not None:
        inputs.add("ContributionHistory")
        fields.append(
            "contribution_history=ContributionHistory("
            "first_enrolled_on=date(1996, 1, 1))"
        )
    if employment.weekly_hours is not None and employment.full_time_weekly_hours:
        inputs.add("WeeklyHours")
        fields.extend((
            f"weekly_hours=WeeklyHours({employment.weekly_hours.value})",
            f"full_time_weekly_hours=WeeklyHours({employment.full_time_weekly_hours.value})",
        ))
    fact_fields = []
    if facts.regione:
        fact_fields.append(f"regione={json.dumps(facts.regione)}")
    if facts.comune_belfiore:
        fact_fields.append(f"comune_belfiore={json.dumps(facts.comune_belfiore)}")
    if facts.contributable_hours is not None:
        inputs.add("ContributableHours")
        fact_fields.append(
            "contributable_hours=ContributableHours("
            f"Decimal({json.dumps(str(facts.contributable_hours.value))}))"
        )
    lines = [
        *(["from datetime import date"] if "date(" in "".join(fields) else []),
        *(["from decimal import Decimal"] if facts.contributable_hours else []),
        "",
        "from ccnl_engine import (",
        "    CompetenceYearPlan,",
        "    EmployerProfile,",
        "    Employment,",
        "    Headcount,",
        "    PayrollEngine,",
        "    PeriodFacts,",
        ")",
        f"from ccnl_engine.inputs import {', '.join(sorted(inputs))}",
        "",
        "engine = PayrollEngine.bundled()",
        "year = engine.calculate_competence_year(",
        "    CompetenceYearPlan(",
        f"        year={_DEFAULT_YEAR},",
        "        employment=Employment(",
        *(f"            {field}," for field in fields),
        "        ),",
        (
            "        employer=EmployerProfile("
            f"headcount=Headcount({int(params.get('headcount') or 1)})),"
        ),
        f"        default_facts=PeriodFacts({', '.join(fact_fields)}),",
        "    )",
        ")",
        'print("Gross:", year.annual_gross)',
        'print("Net:", year.annual_net)',
        'print("Employer cost:", year.annual_employer_cost)',
        'print("Payable:", year.is_payable)',
    ]
    return json.dumps({"code": "\n".join(lines).lstrip("\n") + "\n"})


def _contract_code(employment: Employment) -> str:
    """Return the constructor call of the contract type of ``employment``.

    Returns:
        ``Permanent()``, ``FixedTerm()`` or ``Apprentice(...)``.
    """
    contract = employment.contract_type
    if isinstance(contract, Apprentice):
        track = f", track={json.dumps(contract.track)}" if contract.track else ""
        return f"Apprentice(months_elapsed={contract.months_elapsed}{track})"
    return f"{type(contract).__name__}()"
