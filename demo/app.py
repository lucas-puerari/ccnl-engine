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

from ccnl_engine.engine.contract.domain.ccnl import SupplementaryAllowance
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.io.bundled import read_bundled
from ccnl_engine.engine.payroll.domain.employee import (
    RalOverride,
    SeniorityByCount,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PayrollScenario,
)
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.surtax.service.loaders import load_surtax_rules

_DEFAULT_YEAR = datetime.now(UTC).year


def list_regioni() -> str:
    """Return JSON list of Italian region names with addizionale regionale data.

    Returns:
        JSON-encoded sorted list of region name strings.
    """
    surtax = load_surtax_rules(_DEFAULT_YEAR)
    return json.dumps(sorted(surtax.regionale.keys()))


def list_ccnls() -> str:
    """Return JSON list of all available CCNLs, sorted by name.

    Works for both editable installs (plain ``.json``) and installed wheels
    (compressed ``.json.gz``): iterates the data package, normalises the name,
    then reads via :func:`~ccnl_engine.engine.io.bundled.read_bundled`.

    Returns:
        JSON-encoded list of ``{file, id, name, tax_sector}`` dicts.
    """
    data_pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
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
            "id": meta["ccnl_id"],
            "name": meta["name"],
            "tax_sector": meta["tax_sector"],
        })
    result.sort(key=operator.itemgetter("name"))
    return json.dumps(result)


def load_ccnl_levels(filename: str) -> str:
    """Return JSON list of levels for a CCNL.

    Includes ``max_seniority_count`` (the maximum number of seniority
    increments allowed for that level) and ``seniority_cadence_months``
    so the UI can constrain the seniority input and show a useful hint.

    Args:
        filename: Bare filename (e.g. ``metalmeccanico-federmeccanica.json``).

    Returns:
        JSON-encoded list of ``{code, description, order,
        max_seniority_count, seniority_cadence_months}`` dicts ordered by
        ``order``.
    """
    ccnl = load_ccnl(filename)
    si = ccnl.parameters.seniority_increments
    global_max = int(si.maximum_count) if si else 0
    by_level: dict[str, int] = (
        {k: int(v) for k, v in si.maximum_count_by_level.items()} if si else {}
    )
    cadence: int = int(si.cadence_months) if si else 0
    levels = [
        {
            "code": lv.code,
            "description": lv.description or lv.code,
            "order": lv.order,
            "max_seniority_count": by_level.get(lv.code, global_max),
            "seniority_cadence_months": cadence,
        }
        for lv in ccnl.levels
    ]
    levels.sort(key=operator.itemgetter("order"))
    return json.dumps(levels)


def _build_contract(
    employment_type: str,
    months_elapsed: int,
) -> tuple[Permanent | FixedTerm | Apprentice | None, str]:
    """Construct a contract instance or return (None, error_message).

    Returns:
        A ``(contract, "")`` pair on success or ``(None, error)`` on failure.
    """
    if employment_type == "permanent":
        return Permanent(), ""
    if employment_type == "fixed_term":
        return FixedTerm(), ""
    if employment_type == "apprentice":
        return Apprentice(months_elapsed=months_elapsed), ""
    return None, f"Tipo di contratto non supportato: {employment_type!r}"


def _build_jurisdiction(
    regione: str,
    comune_belfiore: str,
    ivs_ceiling_applies: bool,
) -> Jurisdiction | None:
    """Build a Jurisdiction when locality data or IVS flag is provided.

    Returns:
        A :class:`Jurisdiction` instance, or ``None`` when no locality keys
        are given and IVS ceiling does not apply.
    """
    has_locality = bool(regione or comune_belfiore)
    if not has_locality and not ivs_ceiling_applies:
        return None
    return Jurisdiction(
        regione=regione or None,
        comune_belfiore=comune_belfiore or None,
    )


def _build_seniority(
    mode: str,
    value: int,
) -> SeniorityByCount | SeniorityByMonths | None:
    """Build a seniority object from mode + value.

    Args:
        mode: ``"count"`` for explicit increments, ``"months"`` for service
            months (the engine derives the count from the CCNL cadence).
        value: The count or months value. Zero means no seniority.

    Returns:
        A :class:`SeniorityByCount` or :class:`SeniorityByMonths` instance,
        or ``None`` when value is zero.
    """
    if value <= 0:
        return None
    if mode == "months":
        return SeniorityByMonths(value=value)
    return SeniorityByCount(value=value)


def _build_agreement(
    ad_personam_monthly: float,
    ral_override: float,
) -> Agreement | None:
    """Build an Agreement from optional ad-personam and RAL inputs.

    Args:
        ad_personam_monthly: Individual frozen monthly supplement in EUR.
            Zero means no supplement.
        ral_override: Custom agreed annual gross (RAL) in EUR.
            Zero means use the CCNL tables.

    Returns:
        An :class:`Agreement` instance, or ``None`` when both are zero.
    """
    if ad_personam_monthly <= 0 and ral_override <= 0:
        return None
    return Agreement(
        ral_override=RalOverride(value=Decimal(str(ral_override)))
        if ral_override > 0
        else None,
        ad_personam_monthly=Decimal(str(ad_personam_monthly))
        if ad_personam_monthly > 0
        else Decimal(0),
    )


def _build_employer(
    num_employees: int,
    second_level_monthly: float,
) -> Employer:
    """Build an Employer, optionally with a single second-level allowance.

    Args:
        num_employees: Employer headcount.
        second_level_monthly: Monthly amount from the territorial or company
            second-level agreement in EUR. Zero means no second-level.

    Returns:
        An :class:`Employer` instance.
    """
    if second_level_monthly <= 0:
        return Employer(num_employees=num_employees)
    return Employer(
        num_employees=num_employees,
        second_level_allowances=(
            SupplementaryAllowance(
                code="SL",
                description="Second-level agreement",
                monthly=Decimal(str(second_level_monthly)),
            ),
        ),
    )


def compute_salary(
    filename: str,
    level_code: str,
    employment_type: str,
    num_employees: int,
    part_time_pct: float = 1.0,
    seniority_value: int = 0,
    seniority_mode: str = "count",
    months_elapsed: int = 0,
    regione: str = "",
    comune_belfiore: str = "",
    ivs_ceiling_applies: bool = False,
    ad_personam_monthly: float = 0.0,
    ral_override: float = 0.0,
    second_level_monthly: float = 0.0,
) -> str:
    """Compute gross-to-net and employer cost.

    Args:
        filename: Bare CCNL filename.
        level_code: Level code within the CCNL.
        employment_type: ``"permanent"``, ``"fixed_term"``, or ``"apprentice"``.
        num_employees: Employer headcount (drives INPS rate tier).
        part_time_pct: Part-time fraction in (0, 1], default full-time.
        seniority_value: Seniority quantity (increments or months, per mode).
        seniority_mode: ``"count"`` (default) or ``"months"``.
        months_elapsed: Months elapsed in apprenticeship (apprentice only).
        regione: Italian region name for addizionale regionale computation.
            When empty, the surtax is not computed.
        comune_belfiore: Belfiore code (codice catastale) of the worker's
            municipality for addizionale comunale computation. When empty,
            the surtax is not computed.
        ivs_ceiling_applies: Set to True when the worker's gross exceeds the
            INPS IVS ceiling and only the IVS-specific contribution rate
            should apply.
        ad_personam_monthly: Individual frozen monthly supplement in EUR
            (e.g. pre-abolition seniority). Not scaled by part-time.
        ral_override: Custom agreed annual gross (RAL) in EUR. When set,
            replaces the CCNL-derived salary. Mutually exclusive with
            second_level_monthly.
        second_level_monthly: Monthly amount from a territorial or company
            second-level agreement in EUR. Mutually exclusive with
            ral_override.

    Returns:
        JSON-encoded result dict or ``{"error": "..."}`` on failure.
    """
    contract, err = _build_contract(employment_type, months_elapsed)
    if contract is None:
        return json.dumps({"error": err})

    seniority = _build_seniority(seniority_mode, seniority_value)
    jurisdiction = _build_jurisdiction(regione, comune_belfiore, ivs_ceiling_applies)
    agreement = _build_agreement(ad_personam_monthly, ral_override)
    employer = _build_employer(num_employees, second_level_monthly)

    # Detect lavoro domestico to auto-supply weekly_hours.
    try:
        ccnl_meta = load_ccnl(filename).meta
        is_domestic = getattr(ccnl_meta, "tax_sector", "") == "lavoro-domestico"
    except Exception:  # ruff: ignore[blind-except]
        is_domestic = False

    try:
        scenario = PayrollScenario(
            employee=Employee(
                level_code=level_code,
                seniority=seniority,
                part_time_pct=Decimal(str(round(part_time_pct, 4))),
                weekly_hours=Decimal(40) if is_domestic else None,
                ivs_ceiling_applies=ivs_ceiling_applies,
                jurisdiction=jurisdiction,
                agreement=agreement,
            ),
            employment=Employment(
                ccnl=filename,
                contract=contract,
                employer=employer,
                date=datetime.now(tz=UTC).date(),
            ),
        )
        calculation = compute(scenario)
        payroll = calculation.result
    except Exception as exc:  # ruff: ignore[blind-except]
        return json.dumps({"error": str(exc)})

    return json.dumps({
        # metadata
        "ccnl_id": payroll.ccnl_id,
        "level_code": payroll.level_code,
        "employment_type": payroll.employment_type,
        "year": payroll.year,
        "as_of": payroll.as_of.isoformat(),
        "part_time_pct": float(payroll.part_time_pct),
        # provenance
        "engine_version": calculation.engine_version,
        "ruleset_version": calculation.ruleset_version,
        # pay components
        "base_monthly": float(payroll.base_monthly),
        "seniority_monthly": float(payroll.seniority_monthly),
        "allowances_monthly": float(payroll.allowances_monthly),
        "ad_personam_monthly": float(payroll.ad_personam_monthly),
        "second_level_monthly": float(payroll.second_level_monthly),
        "gross_monthly": float(payroll.gross_monthly),
        "gross_annual": float(payroll.gross_annual),
        "hourly_rate": float(payroll.hourly_rate),
        "seniority_count": payroll.seniority_count,
        # apprenticeship
        "apprenticeship_pct": (
            float(payroll.apprenticeship_pct)
            if payroll.apprenticeship_pct is not None
            else None
        ),
        "apprenticeship_under_level_code": payroll.apprenticeship_under_level_code,
        # employee deductions
        "inps_employee_annual": float(payroll.inps_employee_annual),
        "taxable_income": float(payroll.taxable_income),
        "irpef_gross": float(payroll.irpef_gross),
        "work_income_deduction": float(payroll.work_income_deduction),
        "irpef_net": float(payroll.irpef_net),
        "addizionale_regionale_annual": float(payroll.addizionale_regionale_annual),
        "addizionale_comunale_annual": float(payroll.addizionale_comunale_annual),
        "trattamento_integrativo": float(payroll.trattamento_integrativo),
        # net
        "net_annual": float(payroll.net_annual),
        "net_monthly": float(payroll.net_monthly),
        # employer
        "inps_employer_annual": float(payroll.inps_employer_annual),
        "employer_funds_annual": float(payroll.employer_funds_annual),
        "tfr_annual": float(payroll.tfr_annual),
        "employer_cost_annual": float(payroll.employer_cost_annual),
        # flags
        "employer_withholds_irpef": payroll.employer_withholds_irpef,
        "fiscal_simplifications": sorted(
            str(s) for s in payroll.fiscal_simplifications
        ),
    })
