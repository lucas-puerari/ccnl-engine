# ruff: file-ignore[implicit-namespace-package]
"""ccnl-engine Pyodide glue — runs in the browser via Pyodide.

All public functions return JSON strings so that values cross the Python/JS
boundary without type ambiguity (Decimal, date, etc.).
"""

from __future__ import annotations

import importlib.resources
import json
import operator
from datetime import UTC, datetime
from decimal import Decimal

from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.engine.compute import Scenario, compute
from ccnl_engine.io.bundled import read_bundled
from ccnl_engine.models.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.tax.loaders import load_year_rules

_DEFAULT_YEAR = 2026


def list_ccnls() -> str:
    """Return JSON list of all available CCNLs, sorted by name.

    Works for both editable installs (plain ``.json``) and installed wheels
    (compressed ``.json.gz``): iterates the data package, normalises the name,
    then reads via :func:`~ccnl_engine.io.bundled.read_bundled`.

    Returns:
        JSON-encoded list of ``{file, id, name, tax_sector}`` dicts.
    """
    data_pkg = importlib.resources.files("ccnl_engine.contracts.data")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for entry in data_pkg.iterdir():
        name = entry.name
        if name.endswith(".json.gz"):
            json_name = name[:-3]  # strip .gz → plain filename
        elif name.endswith(".json"):
            json_name = name
        else:
            continue
        if json_name in seen:
            continue
        seen.add(json_name)
        raw = json.loads(read_bundled(data_pkg, json_name))
        meta = raw["meta"]
        result.append({
            "file": json_name,
            "id": meta["id"],
            "name": meta["name"],
            "tax_sector": meta["tax_sector"],
        })
    result.sort(key=operator.itemgetter("name"))
    return json.dumps(result)


def load_ccnl_levels(filename: str) -> str:
    """Return JSON list of levels for a CCNL.

    Args:
        filename: Bare filename (e.g. ``metalmeccanico-federmeccanica.json``).

    Returns:
        JSON-encoded list of ``{code, description, order}`` dicts ordered by
        ``order``.
    """
    ccnl = load_ccnl(filename)
    levels = [
        {
            "code": lv.code,
            "description": lv.description or lv.code,
            "order": lv.order,
        }
        for lv in ccnl.levels
    ]
    levels.sort(key=operator.itemgetter("order"))
    return json.dumps(levels)


def _build_employment(
    employment_type: str,
    months_elapsed: int,
) -> tuple[Permanent | FixedTerm | Apprentice | None, str]:
    """Construct an Employment instance or return (None, error_message).

    Returns:
        A ``(employment, "")`` pair on success or ``(None, error)`` on failure.
    """
    if employment_type == "permanent":
        return Permanent(), ""
    if employment_type == "fixed_term":
        return FixedTerm(), ""
    if employment_type == "apprentice":
        return Apprentice(months_elapsed=months_elapsed), ""
    return None, f"Tipo di contratto non supportato: {employment_type!r}"


def compute_salary(
    filename: str,
    level_code: str,
    employment_type: str,
    num_employees: int,
    part_time_pct: float = 1.0,
    seniority_count: int = 0,
    months_elapsed: int = 0,
) -> str:
    """Compute gross-to-net and employer cost.

    Args:
        filename: Bare CCNL filename.
        level_code: Level code within the CCNL.
        employment_type: ``"permanent"``, ``"fixed_term"``, or ``"apprentice"``.
        num_employees: Employer headcount (drives INPS rate tier and Scenario).
        part_time_pct: Part-time fraction in (0, 1], default full-time.
        seniority_count: Number of seniority increments (*scatti di anzianità*).
        months_elapsed: Months elapsed in apprenticeship (apprentice only).

    Returns:
        JSON-encoded result dict or ``{"error": "..."}`` on failure.
    """
    employment, err = _build_employment(employment_type, months_elapsed)
    if employment is None:
        return json.dumps({"error": err})

    try:
        ccnl = load_ccnl(filename)
        rules = load_year_rules(_DEFAULT_YEAR, ccnl.meta.tax_sector, num_employees)
        scenario = Scenario(
            level_code=level_code,
            as_of=datetime.now(tz=UTC).date(),
            employment=employment,
            num_employees=num_employees,
            part_time_pct=Decimal(str(round(part_time_pct, 4))),
            seniority_count=seniority_count,
        )
        result = compute(ccnl, rules, scenario)
    except Exception as exc:  # ruff: ignore[blind-except]
        return json.dumps({"error": str(exc)})

    return json.dumps({
        "base_monthly": float(result.base_monthly),
        "seniority_monthly": float(result.seniority_monthly),
        "allowances_monthly": float(result.allowances_monthly),
        "gross_monthly": float(result.gross_monthly),
        "gross_annual": float(result.gross_annual),
        "hourly_rate": float(result.hourly_rate),
        "seniority_count": result.seniority_count,
        "inps_employee_annual": float(result.inps_employee_annual),
        "inps_employer_annual": float(result.inps_employer_annual),
        "employer_funds_annual": float(result.employer_funds_annual),
        "tfr_annual": float(result.tfr_annual),
        "taxable_income": float(result.taxable_income),
        "irpef_gross": float(result.irpef_gross),
        "work_income_deduction": float(result.work_income_deduction),
        "irpef_net": float(result.irpef_net),
        "trattamento_integrativo": float(result.trattamento_integrativo),
        "fiscal_simplifications": sorted(str(s) for s in result.fiscal_simplifications),
        "net_annual": float(result.net_annual),
        "net_monthly": float(result.net_monthly),
        "employer_cost_annual": float(result.employer_cost_annual),
        "employer_withholds_irpef": result.employer_withholds_irpef,
        "apprenticeship_pct": (
            float(result.apprenticeship_pct)
            if result.apprenticeship_pct is not None
            else None
        ),
    })
