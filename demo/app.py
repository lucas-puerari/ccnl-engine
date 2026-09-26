# ruff: file-ignore[implicit-namespace-package]
"""ccnl-engine Pyodide glue — runs in the browser via Pyodide.

All public functions return JSON strings so that values cross the Python/JS
boundary without type ambiguity (Decimal, date, etc.).
"""

from __future__ import annotations

import importlib.resources
import json
import operator
from datetime import UTC, date, datetime
from decimal import Decimal

from ccnl_engine import (
    Apprentice,
    Employer,
    EmploymentFacts,
    FixedTerm,
    Headcount,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
    Permanent,
    SupplementaryAllowance,
)
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.io.service.bundled import read_bundled
from ccnl_engine.engine.surtax.service.loaders import load_surtax_rules
from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.jurisdiction import REGION_CODES


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
    tax_pkg = importlib.resources.files("ccnl_engine.knowledge.tax.data")
    inps_pkg = importlib.resources.files("ccnl_engine.knowledge.inps.data")
    surtax_pkg = importlib.resources.files("ccnl_engine.knowledge.surtax.data")
    year = datetime.now(UTC).year
    while True:
        try:
            read_bundled(tax_pkg, f"{year}-industria.json")
            read_bundled(inps_pkg, f"{year}-industria.json")
            read_bundled(surtax_pkg, f"regionale-{year}.json")
        except FileNotFoundError:
            year -= 1
            if year < 2020:
                msg = "No complete bundled data found for any year >= 2020"
                raise RuntimeError(msg) from None
        else:
            return year


_DEFAULT_YEAR = _latest_bundled_year()
_CALC_DATE = date(_DEFAULT_YEAR, 12, 31)
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
            json_name = name[:-3]  # strip .gz
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
        {
            lvl: int(cnt)
            for lvl, cnt in (getattr(si, "maximum_count_by_level", None) or {}).items()
        }
        if si
        else {}
    )
    cadence = int(si.cadence_months) if si else 0
    levels = sorted(ccnl.levels, key=lambda lv: lv.order)
    return json.dumps([
        {
            "code": lv.code,
            "description": lv.description,
            "order": lv.order,
            "max_seniority_count": by_level.get(lv.code, global_max),
            "seniority_cadence_months": cadence,
        }
        for lv in levels
    ])


def load_level_tracks(filename: str, level_code: str) -> str:
    """Return JSON list of apprenticeship tracks for a given level.

    When no apprenticeship data is available, returns an empty list.

    Args:
        filename: Bare CCNL filename.
        level_code: Level code within the CCNL.

    Returns:
        JSON-encoded list of track name strings, or ``[]`` when none exist.
    """
    try:
        ccnl = load_ccnl(filename)
        level = ccnl.level_by_code(level_code)
        tracks = [
            t.name
            for t in (ccnl.apprenticeship or [])
            if level.code in t.destination_levels
            or (hasattr(t, "levels") and level.code in t.levels)
        ]
        return json.dumps(tracks)
    except Exception:  # noqa: BLE001
        return json.dumps([])


def _build_contract(
    employment_type: str,
    months_elapsed: int,
    track: str = "",
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
        return Apprentice(
            months_elapsed=months_elapsed,
            track=track or None,
        ), ""
    return None, f"Tipo di contratto non supportato: {employment_type!r}"


def _resolve_ccnl_meta(
    filename: str, part_time_ratio: float
) -> tuple[str, Decimal | None]:
    """Return (ccnl_name, weekly_hours_domestic).

    Loads the CCNL once to resolve both the display name and, for domestic
    contracts, the scaled weekly hours. Falls back to the filename when
    loading fails. ``weekly_hours_domestic`` is None for non-domestic CCNLs.

    Returns:
        Tuple of (display name, weekly hours or None).
    """
    try:
        ccnl = load_ccnl(filename)
    except Exception:  # noqa: BLE001
        return filename, None
    is_domestic = getattr(ccnl.meta, "tax_sector", "") == "lavoro-domestico"
    if not is_domestic:
        return ccnl.meta.name, None
    divisor = ccnl.parameters.hourly_divisor.value_at(_CALC_DATE)
    weekly = (
        divisor * Decimal(12) / Decimal(52) * Decimal(str(round(part_time_ratio, 4)))
    )
    return ccnl.meta.name, weekly


def _validate_time_supplements(
    weekday_hours: float,
    night_hours: float,
    holiday_hours: float,
    night_holiday_hours: float,
    weeks_json: str = "",
) -> None:
    """Validate overtime inputs, raising on any invalid value.

    Args:
        weekday_hours: Daytime weekday overtime hours (monthly total).
        night_hours: Weekday night hours (monthly total).
        holiday_hours: Daytime public-holiday hours (monthly total).
        night_holiday_hours: Night hours on a public holiday (monthly total).
        weeks_json: Optional JSON array of per-week hour objects.

    Raises:
        json.JSONDecodeError: When weeks_json is not valid JSON.
        AttributeError: When a list element is not a dict.
        ValueError: When any hour value is negative.
    """
    if not weeks_json:
        return
    raw: list[dict[str, float]] = json.loads(weeks_json)
    for w in raw:
        for field in (
            "weekday_hours",
            "night_hours",
            "holiday_hours",
            "night_holiday_hours",
            "supplementare_hours",
        ):
            val = Decimal(str(w.get(field, 0)))
            if val < 0:
                msg = f"{field} must be >= 0, got {val}"
                raise ValueError(msg)


def _build_employment_facts(
    contract: Permanent | FixedTerm | Apprentice,
    seniority_mode: str,
    seniority_value: int,
    ivs_ceiling_applies: bool,
    weekly_hours_domestic: Decimal | None,
) -> EmploymentFacts:
    """Build EmploymentFacts from component inputs.

    Returns:
        An :class:`EmploymentFacts` instance.
    """
    seniority_months: int | None = None
    if seniority_value > 0:
        if seniority_mode == "months":
            seniority_months = seniority_value
    ceiling = (
        ContributionCeilingStatus.OPTED_IN
        if ivs_ceiling_applies
        else ContributionCeilingStatus.UNKNOWN
    )
    weekly_hours_int: int | None = (
        int(weekly_hours_domestic) if weekly_hours_domestic is not None else None
    )
    return EmploymentFacts(
        contract_type=contract,
        seniority_months=seniority_months,
        ceiling_status=ceiling,
        weekly_hours=weekly_hours_int,
    )


def compute_salary(
    filename: str,
    level_code: str,
    employment_type: str,
    num_employees: int,
    part_time_ratio: float = 1.0,
    seniority_value: int = 0,
    seniority_mode: str = "count",
    months_elapsed: int = 0,
    regione: str = "",
    comune_belfiore: str = "",
    ivs_ceiling_applies: bool = False,
    ad_personam_monthly: float = 0.0,
    ral_override: float = 0.0,
    second_level_monthly: float = 0.0,
    overtime_weekday_hours: float = 0.0,
    overtime_night_hours: float = 0.0,
    overtime_holiday_hours: float = 0.0,
    overtime_night_holiday_hours: float = 0.0,
    overtime_weeks: str = "",
    absence_unpaid_days: float = 0.0,
    leave_taken_days: float = 0.0,
    sick_days: float = 0.0,
    fringe_benefit_annual: float = 0.0,
    welfare_annual: float = 0.0,
    bonus_annual: float = 0.0,
    bonus_pdr_eligible: bool = False,
    track: str = "",
) -> str:
    """Compute gross-to-net and employer cost.

    Args:
        filename: Bare CCNL filename.
        level_code: Level code within the CCNL.
        employment_type: ``"permanent"``, ``"fixed_term"``, or ``"apprentice"``.
        num_employees: Employer headcount (drives INPS rate tier).
        part_time_ratio: Part-time fraction in (0, 1], default full-time.
        seniority_value: Seniority months of service (seniority_mode="months").
        seniority_mode: ``"count"`` (deprecated) or ``"months"``.
        months_elapsed: Months elapsed in apprenticeship (apprentice only).
        regione: Region code (e.g. ``"ER"``) for addizionale regionale.
            When empty, the surtax is not computed.
        comune_belfiore: Belfiore code (codice catastale) of the worker's
            municipality for addizionale comunale computation. When empty,
            the surtax is not computed.
        ivs_ceiling_applies: Set to True when the worker's gross exceeds the
            INPS IVS ceiling and only the IVS-specific contribution rate
            should apply.
        ad_personam_monthly: Individual frozen monthly supplement in EUR
            (reserved for future use; not currently applied).
        ral_override: Custom agreed annual gross (RAL) in EUR
            (reserved for future use; not currently applied).
        second_level_monthly: Monthly amount from a territorial or company
            second-level agreement in EUR.
        overtime_weekday_hours: Daytime weekday overtime hours (L3).
        overtime_night_hours: Weekday night hours (L3).
        overtime_holiday_hours: Daytime public-holiday hours (L3).
        overtime_night_holiday_hours: Night hours on a public holiday (L3).
        overtime_weeks: Optional JSON array of per-week hour objects for
            accurate tiered-band partitioning (L3).  When provided, the
            four scalar overtime arguments above are ignored.
        absence_unpaid_days: Days absent without pay in the period (L3).
        leave_taken_days: Leave days consumed in the period (L3).
        sick_days: Calendar days of illness in the period (L3).
        fringe_benefit_annual: Total fringe-benefit value for the year (L3).
        welfare_annual: Welfare annual amount (L3, always tax-exempt).
        bonus_annual: Total annual bonus (L3).
        bonus_pdr_eligible: Whether the bonus qualifies for PdR flat tax (L3).
        track: Apprenticeship track name. Required when the CCNL defines
            more than one track for the destination level; empty string
            lets the engine pick the unique applicable track.

    Returns:
        JSON-encoded result dict or ``{"error": "..."}`` on failure.
    """
    contract, err = _build_contract(employment_type, months_elapsed, track)
    if contract is None:
        return json.dumps({"error": err})

    try:
        _validate_time_supplements(
            overtime_weekday_hours,
            overtime_night_hours,
            overtime_holiday_hours,
            overtime_night_holiday_hours,
            overtime_weeks,
        )
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"overtime_weeks: {exc}"})

    ccnl_name, weekly_hours_domestic = _resolve_ccnl_meta(filename, part_time_ratio)

    try:
        ccnl = load_ccnl(filename)
        additional_months = float(
            ccnl.parameters.additional_months.value_at(_CALC_DATE)
        )

        employment_facts = _build_employment_facts(
            contract=contract,
            seniority_mode=seniority_mode,
            seniority_value=seniority_value,
            ivs_ceiling_applies=ivs_ceiling_applies,
            weekly_hours_domestic=weekly_hours_domestic,
        )

        supplementary_allowances: tuple[SupplementaryAllowance, ...] = ()
        if second_level_monthly > 0:
            supplementary_allowances = (
                SupplementaryAllowance(
                    code="SL",
                    description="Second-level agreement",
                    monthly=Decimal(str(second_level_monthly)),
                ),
            )

        req = PayrollRequest(
            run=PayrollRun.regular(_DEFAULT_YEAR, 12),
            payment_date=date(_DEFAULT_YEAR, 12, 28),
            ccnl_slug=filename,
            level_code=level_code,
            employment_facts=employment_facts,
            employer=Employer(headcount=Headcount(num_employees)),
            regione=regione or None,
            comune_belfiore=comune_belfiore or None,
        )
        result = _ENGINE.calculate(req)

        base_monthly = float(
            sum(
                pi.amount
                for pi in result.pay_items
                if pi.kind == "base_salary_earning" and pi.amount
            )
        )
        seniority_monthly_val = float(
            sum(
                pi.amount
                for pi in result.pay_items
                if pi.kind == "seniority_earning" and pi.amount
            )
        )
        allowances_monthly = float(
            sum(
                pi.amount
                for pi in result.pay_items
                if pi.kind
                in ("fixed_allowance_earning", "conditional_allowance_earning")
                and pi.amount
            )
        )
        gross_monthly = float(result.period_gross)
        gross_annual = gross_monthly * additional_months
        net_monthly = float(result.period_net)
        net_annual = net_monthly * additional_months
        employer_cost_monthly = float(result.period_employer_cost)

        irpef_gross = 0.0
        work_deduction = 0.0
        ulteriore_detrazione = 0.0
        trattamento_integrativo = 0.0
        if result.tax_computation:
            trattamento_integrativo = float(
                result.tax_computation.trattamento_integrativo
            )
            for comp in result.tax_computation.components:
                if comp.name == "irpef_gross":
                    irpef_gross = float(comp.amount)
                elif comp.name == "work_deduction":
                    work_deduction = float(comp.amount)
                elif comp.name == "ulteriore_detrazione":
                    ulteriore_detrazione = float(comp.amount)

        inps_employee = 0.0
        inps_employer = 0.0
        if result.contribution_breakdown:
            inps_employee = float(result.contribution_breakdown.employee)
            inps_employer = float(result.contribution_breakdown.employer)

        irpef_net = irpef_gross - work_deduction - ulteriore_detrazione

        addizionale_regionale = 0.0
        addizionale_comunale = 0.0
        irpef_withholding = 0.0
        if result.tax_computation:
            irpef_withholding = float(result.tax_computation.ordinary_tax)

        capability_entries: list[dict[str, object]] = []

        return json.dumps({
            "ccnl_name": ccnl_name,
            "level_code": level_code,
            "employment_type": employment_type,
            "year": _DEFAULT_YEAR,
            "as_of": _CALC_DATE.isoformat(),
            "part_time_ratio": part_time_ratio,
            "engine_version": result.bundle_version or "",
            "ruleset_version": {},
            "base_monthly": base_monthly,
            "seniority_monthly": seniority_monthly_val or None,
            "allowances_monthly": allowances_monthly,
            "ad_personam_monthly": float(ad_personam_monthly)
            if ad_personam_monthly > 0
            else None,
            "second_level_monthly": float(second_level_monthly)
            if second_level_monthly > 0
            else None,
            "gross_monthly": gross_monthly,
            "gross_annual": gross_annual,
            "hourly_rate": 0.0,
            "seniority_count": None,
            "apprenticeship_pct": None,
            "apprenticeship_under_level_code": None,
            "additional_months": additional_months,
            "inps_employee_annual": inps_employee * additional_months,
            "taxable_income": 0.0,
            "irpef_gross": irpef_gross,
            "work_income_deduction": work_deduction,
            "ulteriore_detrazione_lavoro": ulteriore_detrazione,
            "irpef_net": irpef_net,
            "addizionale_regionale_annual": addizionale_regionale,
            "addizionale_comunale_annual": addizionale_comunale,
            "trattamento_integrativo": trattamento_integrativo,
            "somma_esente": 0.0,
            "bilateral_employee_annual": 0.0,
            "net_annual": net_annual,
            "net_monthly": net_monthly,
            "inps_employer_annual": inps_employer * additional_months,
            "employer_funds_annual": 0.0,
            "tfr_annual": float(
                sum(
                    pi.amount
                    for pi in result.pay_items
                    if pi.kind == "tfr_accrual_item" and pi.amount
                )
            )
            * additional_months,
            "bilateral_employer_annual": 0.0,
            "employer_cost_annual": employer_cost_monthly * additional_months,
            "overtime_supplement_monthly": 0.0,
            "night_supplement_monthly": 0.0,
            "holiday_supplement_monthly": 0.0,
            "absence_deduction_monthly": 0.0,
            "effective_gross_monthly": gross_monthly,
            "leave_accrued_days_monthly": 0.0,
            "leave_balance_days": 0.0,
            "sick_inps_indemnity_monthly": 0.0,
            "sick_company_integration_monthly": 0.0,
            "fringe_benefit_annual": 0.0,
            "welfare_annual": 0.0,
            "bonus_annual": 0.0,
            "bonus_pdr_flat_tax_annual": 0.0,
            "employer_withholds_irpef": True,
            "fiscal_simplifications": [],
            "trace": {},
            "provenance": [],
            "confidence": 1.0,
            "warnings": [],
            "calculation_scope": capability_entries,
            "ccnl_id": getattr(ccnl.meta, "ccnl_id", ""),
            "weekly_hours": (
                str(weekly_hours_domestic)
                if weekly_hours_domestic is not None
                else None
            ),
        })
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": str(exc)})
