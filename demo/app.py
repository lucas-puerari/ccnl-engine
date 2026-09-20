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
    Agreement,
    AnnualEstimateInput,
    Apprentice,
    Employee,
    Employer,
    Employment,
    FixedTerm,
    Jurisdiction,
    OvertimeHours,
    PeriodPayrollInput,
    Permanent,
    RalOverride,
    SeniorityByCount,
    SeniorityByMonths,
    SupplementaryAllowance,
    WeeklyOvertimeHours,
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.io.service.bundled import read_bundled
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    SickInput,
    WelfareInput,
)
from ccnl_engine.engine.surtax.service.loaders import load_surtax_rules


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


def list_regioni() -> str:
    """Return JSON list of Italian region names with addizionale regionale data.

    Returns:
        JSON-encoded sorted list of region name strings.
    """
    surtax = load_surtax_rules(_DEFAULT_YEAR)
    return json.dumps(sorted(surtax.regionale.keys()))


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


def load_level_tracks(filename: str, level_code: str) -> str:
    """Return JSON list of apprenticeship track names available for a level.

    When the CCNL has no apprenticeship module or the level has no tracks,
    returns an empty list.  The UI uses this to show a track selector only
    when more than one track is available.

    Args:
        filename: Bare CCNL filename (e.g. ``"metalmeccanico-federmeccanica.json"``).
        level_code: Destination level code within the CCNL.

    Returns:
        JSON-encoded list of track-name strings.
    """
    try:
        ccnl = load_ccnl(filename)
        tracks = ccnl.apprenticeship_tracks_for(level_code)
        return json.dumps([t.name for t in tracks])
    except (KeyError, ValueError, LookupError):
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


def _build_time_supplements(
    weekday_hours: float,
    night_hours: float,
    holiday_hours: float,
    night_holiday_hours: float,
    weeks_json: str = "",
) -> OvertimeHours | None:
    """Build OvertimeHours when any overtime input is non-zero.

    When *weeks_json* is a non-empty JSON array of per-week objects the monthly
    totals are derived automatically via :meth:`OvertimeHours.from_weeks` and
    the four scalar arguments are ignored.

    Args:
        weekday_hours: Daytime weekday overtime hours (monthly total).
        night_hours: Weekday night hours (monthly total).
        holiday_hours: Daytime public-holiday hours (monthly total).
        night_holiday_hours: Night hours on a public holiday (monthly total).
        weeks_json: Optional JSON array of per-week hour objects.  Each entry
            may contain any subset of ``weekday_hours``, ``night_hours``,
            ``holiday_hours``, ``night_holiday_hours``,
            ``supplementare_hours``; missing keys default to zero.

    Returns:
        An :class:`OvertimeHours` instance, or ``None`` when all are zero.
    """
    if weeks_json:
        raw: list[dict[str, float]] = json.loads(weeks_json)
        weeks = tuple(
            WeeklyOvertimeHours(
                weekday_hours=Decimal(str(w.get("weekday_hours", 0))),
                night_hours=Decimal(str(w.get("night_hours", 0))),
                holiday_hours=Decimal(str(w.get("holiday_hours", 0))),
                night_holiday_hours=Decimal(str(w.get("night_holiday_hours", 0))),
                supplementare_hours=Decimal(str(w.get("supplementare_hours", 0))),
            )
            for w in raw
        )
        if not any(
            getattr(wk, f)
            for wk in weeks
            for f in (
                "weekday_hours",
                "night_hours",
                "holiday_hours",
                "night_holiday_hours",
                "supplementare_hours",
            )
        ):
            return None
        return OvertimeHours.from_weeks(weeks)
    if not any([weekday_hours, night_hours, holiday_hours, night_holiday_hours]):
        return None
    return OvertimeHours(
        weekday_hours=Decimal(str(weekday_hours)),
        night_hours=Decimal(str(night_hours)),
        holiday_hours=Decimal(str(holiday_hours)),
        night_holiday_hours=Decimal(str(night_holiday_hours)),
    )


def _build_period_input(
    time_supplements: OvertimeHours | None,
    absence: AbsenceDays | None,
    leave: LeaveInput | None,
    sick: SickInput | None,
    fringe: FringeBenefitInput | None,
    welfare: WelfareInput | None,
    bonus: BonusInput | None,
) -> PeriodPayrollInput | None:
    """Return a PeriodPayrollInput when any period field is set, else None.

    Returns:
        A populated PeriodPayrollInput, or None when all inputs are absent.
    """
    if not any((time_supplements, absence, leave, sick, fringe, welfare, bonus)):
        return None
    return PeriodPayrollInput(
        time_supplements=time_supplements,
        absence_days=absence,
        leave_input=leave,
        sick_input=sick,
        fringe_benefit_input=fringe,
        welfare_input=welfare,
        bonus_input=bonus,
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

    seniority = _build_seniority(seniority_mode, seniority_value)
    jurisdiction = _build_jurisdiction(regione, comune_belfiore, ivs_ceiling_applies)
    agreement = _build_agreement(ad_personam_monthly, ral_override)
    employer = _build_employer(num_employees, second_level_monthly)

    ccnl_name, weekly_hours_domestic = _resolve_ccnl_meta(filename, part_time_ratio)

    try:
        time_supplements = _build_time_supplements(
            overtime_weekday_hours,
            overtime_night_hours,
            overtime_holiday_hours,
            overtime_night_holiday_hours,
            overtime_weeks,
        )
    except Exception as exc:  # ruff: ignore[blind-except]
        return json.dumps({"error": f"overtime_weeks: {exc}"})
    absence = (
        AbsenceDays(unpaid_days=Decimal(str(absence_unpaid_days)))
        if absence_unpaid_days > 0
        else None
    )
    leave = (
        LeaveInput(taken_days=Decimal(str(leave_taken_days)))
        if leave_taken_days > 0
        else None
    )
    sick = SickInput(sick_days=Decimal(str(sick_days))) if sick_days > 0 else None
    fringe = (
        FringeBenefitInput(annual_amount=Decimal(str(fringe_benefit_annual)))
        if fringe_benefit_annual > 0
        else None
    )
    welfare = (
        WelfareInput(annual_amount=Decimal(str(welfare_annual)))
        if welfare_annual > 0
        else None
    )
    bonus = (
        BonusInput(
            annual_amount=Decimal(str(bonus_annual)),
            eligible_for_pdr=bonus_pdr_eligible,
        )
        if bonus_annual > 0
        else None
    )

    try:
        annual = AnnualEstimateInput(
            employee=Employee(
                level_code=level_code,
                seniority=seniority,
                part_time_ratio=Decimal(str(round(part_time_ratio, 4))),
                weekly_hours=weekly_hours_domestic,
                ivs_ceiling_applies=ivs_ceiling_applies,
                jurisdiction=jurisdiction,
                agreement=agreement,
            ),
            employment=Employment(
                ccnl=filename,
                contract=contract,
                employer=employer,
                as_of=_CALC_DATE,
            ),
        )
        period = _build_period_input(
            time_supplements, absence, leave, sick, fringe, welfare, bonus
        )
        calculation = (
            estimate_annual(annual)
            if period is None
            else estimate_period_effects(annual, period)
        )
        payroll = calculation.result
    except Exception as exc:  # ruff: ignore[blind-except]
        return json.dumps({"error": str(exc)})

    return json.dumps({
        # metadata
        "ccnl_id": payroll.ccnl_id,
        "weekly_hours": (
            str(weekly_hours_domestic) if weekly_hours_domestic is not None else None
        ),
        "ccnl_name": ccnl_name,
        "level_code": payroll.level_code,
        "employment_type": payroll.employment_type,
        "year": payroll.year,
        "as_of": payroll.as_of.isoformat(),
        "part_time_ratio": float(payroll.part_time_ratio),
        # provenance
        "engine_version": calculation.engine_version,
        "ruleset_version": dict(calculation.ruleset_version),
        # pay components
        "base_monthly": float(payroll.earnings.base_monthly),
        "seniority_monthly": float(payroll.earnings.seniority_monthly),
        "allowances_monthly": float(payroll.earnings.allowances_monthly),
        "ad_personam_monthly": float(payroll.earnings.ad_personam_monthly),
        "second_level_monthly": float(payroll.earnings.second_level_monthly),
        "gross_monthly": float(payroll.earnings.gross_monthly),
        "gross_annual": float(payroll.earnings.gross_annual),
        "hourly_rate": float(payroll.earnings.hourly_rate),
        "seniority_count": payroll.earnings.seniority_count,
        # apprenticeship
        "apprenticeship_pct": (
            float(payroll.earnings.apprenticeship_pct)
            if payroll.earnings.apprenticeship_pct is not None
            else None
        ),
        "apprenticeship_under_level_code": payroll.earnings.apprenticeship_under_level_code,
        # mensilità — read from CCNL parameters (not derived from ratio, which
        # loses precision when allowances carry per-component months_per_year).
        "additional_months": float(
            load_ccnl(filename).parameters.additional_months.value_at(payroll.as_of)
        ),
        # employee deductions
        "inps_employee_annual": float(payroll.contributions.inps_employee_annual),
        "taxable_income": float(payroll.taxes.taxable_income),
        "irpef_gross": float(payroll.taxes.irpef_gross),
        "work_income_deduction": float(payroll.taxes.work_income_deduction),
        "ulteriore_detrazione_lavoro": float(payroll.taxes.ulteriore_detrazione_lavoro),
        "irpef_net": float(payroll.taxes.irpef_net),
        "addizionale_regionale_annual": float(
            payroll.taxes.addizionale_regionale_annual
        ),
        "addizionale_comunale_annual": float(payroll.taxes.addizionale_comunale_annual),
        "trattamento_integrativo": float(payroll.taxes.trattamento_integrativo),
        "somma_esente": float(payroll.taxes.somma_esente),
        "bilateral_employee_annual": float(
            payroll.contributions.bilateral_employee_annual
        ),
        # net
        "net_annual": float(payroll.net_annual),
        "net_monthly": float(payroll.net_monthly),
        # employer
        "inps_employer_annual": float(payroll.contributions.inps_employer_annual),
        "employer_funds_annual": float(payroll.contributions.employer_funds_annual),
        "tfr_annual": float(payroll.contributions.tfr_annual),
        "bilateral_employer_annual": float(
            payroll.contributions.bilateral_employer_annual
        ),
        "employer_cost_annual": float(payroll.employer_cost.employer_cost_annual),
        "overtime_supplement_monthly": float(
            getattr(payroll, "overtime_supplement_monthly", 0)
        ),
        "night_supplement_monthly": float(
            getattr(payroll, "night_supplement_monthly", 0)
        ),
        "holiday_supplement_monthly": float(
            getattr(payroll, "holiday_supplement_monthly", 0)
        ),
        "absence_deduction_monthly": float(
            getattr(payroll, "absence_deduction_monthly", 0)
        ),
        "effective_gross_monthly": float(
            getattr(payroll, "effective_gross_monthly", payroll.net_monthly)
        ),
        "leave_accrued_days_monthly": float(
            getattr(payroll, "leave_accrued_days_monthly", 0)
        ),
        "leave_balance_days": float(getattr(payroll, "leave_balance_days", 0)),
        "sick_inps_indemnity_monthly": float(
            getattr(payroll, "sick_inps_indemnity_monthly", 0)
        ),
        "sick_company_integration_monthly": float(
            getattr(payroll, "sick_company_integration_monthly", 0)
        ),
        "fringe_benefit_annual": float(getattr(payroll, "fringe_benefit_annual", 0)),
        "welfare_annual": float(getattr(payroll, "welfare_annual", 0)),
        "bonus_annual": float(getattr(payroll, "bonus_annual", 0)),
        "bonus_pdr_flat_tax_annual": float(
            getattr(payroll, "bonus_pdr_flat_tax_annual", 0)
        ),
        # flags
        "employer_withholds_irpef": payroll.taxes.employer_withholds_irpef,
        "fiscal_simplifications": sorted(
            str(s) for s in payroll.taxes.fiscal_simplifications
        ),
        # trust — calculation trace
        "trace": calculation.trace.to_dict(),
        # trust — sources cited by the engine
        "provenance": [
            {
                "title": p.location.source_document.title,
                "kind": str(p.location.source_document.kind),
                "authority": str(p.location.source_document.authority),
                "url": p.location.source_document.url,
                "section": p.location.section,
                "quote": p.location.quote,
                "method": str(p.extraction.method),
                "verification_status": str(p.extraction.verification_status),
            }
            for p in payroll.provenance
        ],
        # trust — result quality signals
        "confidence": payroll.coverage.confidence,
        "warnings": list(payroll.coverage.warnings),
        "calculation_scope": [
            {
                "feature": s.feature,
                "calculation_status": s.calculation_status,
                "gross_integrated": s.gross_integrated,
                "contribution_integrated": s.contribution_integrated,
                "tax_integrated": s.tax_integrated,
                "net_integrated": s.net_integrated,
                "cost_integrated": s.cost_integrated,
                "eligibility_status": s.eligibility_status,
                "source_quality": s.source_quality,
            }
            for s in payroll.coverage.calculation_scope
        ],
    })
