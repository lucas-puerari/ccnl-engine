"""Pure factory functions shared across the test suite.

These are plain functions (not pytest fixtures) so they can be imported
from any module, including non-pytest code such as builders.py.
"""

from __future__ import annotations

import copy
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from ccnl_engine.engine.contract.domain.identity import CCNL
from ccnl_engine.engine.tax.domain.ruleset import YearRules
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Employment
from ccnl_engine.payroll.domain.inputs import PeriodFacts, YearInput
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.tax_year import DEFAULT_PAYMENT_DAY

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.payroll.domain.calendar_override import CalendarOverride
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.period import PeriodState

# ---------------------------------------------------------------------------
# Shared raw data — canonical source for inline fixtures across the test suite
# ---------------------------------------------------------------------------

#: 2026 IRPEF marginal tax brackets (Art. 11 TUIR post L. 207/2024).
IRPEF_BRACKETS_2026: list[dict[str, Any]] = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": "50000.00", "rate": "0.33"},
    {"up_to": None, "rate": "0.43"},
]

#: INPS rates for terziario sector (no ceiling, simplified).
INPS_RATES_TERZIARIO: dict[str, Any] = {
    "employee_rate": "0.0919",
    "employee_ivs_rate": "0.0919",
    "employer_rate": "0.2898",
    "employer_ivs_rate": "0.2381",
    "ceiling": None,
}

#: Apprentice rates for a large firm (L. 296/2006 art. 1 c. 773 + NASpI).
APPRENTICE_RATES_LARGE_FIRM: dict[str, Any] = {
    "employee_rate": "0.0584",
    "employee_ivs_rate": "0.0584",
    "employer_rate_months_0_11": "0.1161",
    "employer_ivs_rate_months_0_11": "0.1000",
    "employer_rate_months_12_23": "0.1161",
    "employer_ivs_rate_months_12_23": "0.1000",
    "employer_rate_after": "0.1161",
    "employer_ivs_rate_after": "0.1000",
}

#: Flat per-hour domestic contribution table (INPS Circ. 9/2026, con CUAF).
DOMESTIC_CONTRIBUTIONS: dict[str, Any] = {
    "weekly_hours_threshold": 24,
    "hours_bracket": {
        "employee_per_hour": "0.31",
        "employer_per_hour": "0.93",
        "employer_per_hour_fixed_term": "1.01",
    },
    "wage_brackets": [
        {
            "hourly_rate_up_to": "9.61",
            "employee_per_hour": "0.43",
            "employer_per_hour": "1.27",
            "employer_per_hour_fixed_term": "1.39",
        },
        {
            "hourly_rate_up_to": "11.70",
            "employee_per_hour": "0.48",
            "employer_per_hour": "1.44",
            "employer_per_hour_fixed_term": "1.57",
        },
        {
            "hourly_rate_up_to": None,
            "employee_per_hour": "0.59",
            "employer_per_hour": "1.75",
            "employer_per_hour_fixed_term": "1.91",
        },
    ],
}

#: Percentage track: destination level 4 paid at 80% throughout.
TRACK_PERCENTAGE: dict[str, Any] = {
    "type": "percentage",
    "name": "standard",
    "destination_levels": ["4"],
    "periods": [{"months_from": 0, "months_until": None, "percentage": "0.80"}],
}

#: Under-classification track: destination level 4 paid one level below.
TRACK_UNDER_CLASSIFICATION: dict[str, Any] = {
    "type": "under_classification",
    "name": "standard",
    "destination_levels": ["4"],
    "periods": [{"months_from": 0, "months_until": None, "levels_below": 1}],
}


#: Verified ruleset identity dict for test fixtures.
TEST_RULESET_VERIFIED: dict[str, Any] = {
    "id": "test/rules",
    "version": "2026.2",
    "effective_from": "2026-01-01",
    "effective_until": None,
    "published_at": "2026-01-01",
    "source": "https://example.com",
    "source_type": "official_primary",
    "source_hash": "e" * 64,
    "verification_status": "verified",
}

#: Minimal provenance dict for test fixtures — method "manual", unverified.
TEST_PROV: dict[str, Any] = {
    "location": {
        "source_document": {
            "document_id": "test-doc",
            "title": "Test Source",
            "kind": "tabella_retributiva",
            "url": "https://example.com",
        },
        "section": "Test section",
    },
    "extraction": {
        "method": "manual",
        "extraction_timestamp": "2026-01-01T00:00:00",
        "verification_status": "unverified",
        "effective_from": "2020-01-01",
    },
}


def _series(value: str, valid_from: str = "2020-01-01") -> dict[str, Any]:
    return {
        "periods": [{"valid_from": valid_from, "valid_until": None, "value": value}]
    }


def _series_with_prov(value: str, valid_from: str = "2020-01-01") -> dict[str, Any]:
    """Like _series but includes provenance on each period (required by validator).

    Returns:
        A TimeSeries-compatible dict with a single provenance-bearing period.
    """
    return {
        "periods": [
            {
                "valid_from": valid_from,
                "valid_until": None,
                "value": value,
                "provenance": TEST_PROV,
            }
        ]
    }


def _level(code: str, order: int, salary: str) -> dict[str, Any]:
    return {
        "code": code,
        "order": order,
        "description": f"Level {code}",
        "base_salary": _series_with_prov(salary),
        "fixed_allowances": [],
        "provenance": TEST_PROV,
    }


def make_year_rules(
    brackets: list[dict[str, Any]] | None = None,
    inps: dict[str, Any] | None = None,
    apprentice: dict[str, Any] | None = None,
    sterilizzazione_detrazioni: dict[str, Any] | None = None,
    ulteriore_detrazione: dict[str, Any] | None = None,
    ruleset: dict[str, Any] | None = TEST_RULESET_VERIFIED,
    inps_ruleset: dict[str, Any] | None = TEST_RULESET_VERIFIED,
) -> YearRules:
    """Build a YearRules instance for testing. Defaults to the 2026 terziario values.

    Args:
        brackets: IRPEF bracket list; defaults to 2026 statutory values.
        inps: Raw INPS rates dict; defaults to terziario rates.
        apprentice: Raw apprentice rates dict; defaults to large-firm values.
        sterilizzazione_detrazioni: Optional override for sterilizzazione
            rules (Art. 1 c. 3-4 L. 199/2025). Pass ``{"threshold": ...,
            "reduction": ...}`` to activate or a custom threshold for tests.
        ulteriore_detrazione: Optional override for ulteriore detrazione
            rules (Art. 1 c. 6 L. 207/2024). Pass ``{"threshold_low": ...,
            "threshold_mid": ..., "threshold_high": ...,
            "max_amount": ...}`` to activate.
        ruleset: Ruleset identity dict for the tax rules; defaults to a
            verified identity so orchestrator tests can reach ``"high"``
            confidence. Pass ``None`` to simulate absent identity.
        inps_ruleset: Ruleset identity dict for the INPS rules; same
            default and semantics as ``ruleset``.

    Returns:
        A validated YearRules instance.
    """
    raw: dict[str, Any] = {
        "year": 2026,
        "irpef_brackets": brackets or IRPEF_BRACKETS_2026,
        "fixed_term_additional_rate": "0.014",
        "inps": inps or INPS_RATES_TERZIARIO,
        "apprentice": apprentice or APPRENTICE_RATES_LARGE_FIRM,
        "tfr": {"accrual_divisor": "13.5"},
    }
    if ruleset is not None:
        raw["ruleset"] = ruleset
    if inps_ruleset is not None:
        raw["inps_ruleset"] = inps_ruleset
    if sterilizzazione_detrazioni is not None:
        raw["sterilizzazione_detrazioni"] = sterilizzazione_detrazioni
    if ulteriore_detrazione is not None:
        raw["ulteriore_detrazione"] = ulteriore_detrazione
    return YearRules.model_validate(raw)


def make_domestic_year_rules() -> YearRules:
    """Build a YearRules with domestic flat-hour contributions (no standard INPS).

    Returns:
        A validated YearRules with domestic_contributions set and inps=None.
    """
    return YearRules.model_validate({
        "year": 2026,
        "irpef_brackets": IRPEF_BRACKETS_2026,
        "fixed_term_additional_rate": "0.014",
        "domestic_contributions": DOMESTIC_CONTRIBUTIONS,
        "tfr": {"accrual_divisor": "13.5"},
    })


def make_ccnl_dict(*, app_type: str = "percentage") -> dict[str, Any]:
    """Return a minimal three-level CCNL dict (levels 2, 3, 4) as raw data.

    Level 4 has a seniority increment of 20.00; levels 2 and 3 have none.

    Returns:
        A dict suitable for passing to CCNL.model_validate().
    """
    if app_type == "percentage":
        tracks = [copy.deepcopy(TRACK_PERCENTAGE)]
    elif app_type == "under_classification":
        tracks = [copy.deepcopy(TRACK_UNDER_CLASSIFICATION)]
    else:
        tracks = []
    return {
        "schema_version": "0.4",
        "meta": {
            "ccnl_id": "test",
            "name": "Test CCNL",
            "cnel_code": "X001",
            "sector": "test",
            "tax_sector": "terziario",
            "signatories": ["A", "B"],
            "sources": [{"url": "https://example.com", "type": "ccnl"}],
            "extraction": {
                "method": "manual",
                "model": None,
                "timestamp": "2026-01-01T00:00:00Z",
                "human_reviewed": True,
            },
        },
        "coverage": {
            "gross": "implemented",
            "net": "implemented" if tracks else "partial",
            "notes": (
                []
                if tracks
                else [{"kind": "missing", "text": "apprenticeship not modelled."}]
            ),
        },
        "parameters": {
            "hourly_divisor": _series("168"),
            "additional_months": _series("12"),
            "seniority_increments": {
                "cadence_months": 36,
                "maximum_count": 10,
                "amount_by_level": {"4": _series("20.00")},
                "provenance": TEST_PROV,
            },
        },
        "levels": [
            _level("2", 2, "600.00"),
            _level("3", 3, "800.00"),
            _level("4", 4, "1000.00"),
        ],
        "apprenticeship": tracks,
    }


def make_minimal_ccnl(*, app_type: str = "percentage") -> CCNL:
    """Build a minimal three-level CCNL with configurable apprenticeship type.

    Returns:
        A validated CCNL instance.
    """
    return CCNL.model_validate(make_ccnl_dict(app_type=app_type))


# ---------------------------------------------------------------------------
# Payroll inputs
# ---------------------------------------------------------------------------

#: Employer of 50 employees, the headcount the fixtures assume.
EMPLOYER_50 = EmployerProfile(headcount=Headcount(50))


def year_input(
    year: int,
    ccnl_slug: str,
    level_code: str,
    *,
    employer: EmployerProfile = EMPLOYER_50,
    facts: PeriodFacts | None = None,
    events: Mapping[int, tuple[WorkEvent, ...]]
    | Mapping[str, tuple[WorkEvent, ...]]
    | Mapping[int | str, tuple[WorkEvent, ...]]
    | None = None,
    prior_year: PriorYearTaxFacts | None = None,
    calendar_override: CalendarOverride | None = None,
    payment_day: int = DEFAULT_PAYMENT_DAY,
    opening_state: PeriodState | None = None,
    **employment: Any,  # noqa: ANN401
) -> YearInput:
    """Build a :class:`YearInput` whose runs share the same facts.

    Every run takes ``facts``; a run keyed in ``events`` takes ``facts`` with
    those events.  ``employment`` holds the :class:`Employment` fields other
    than the CCNL and the level.

    Returns:
        The year input.
    """
    base = facts if facts is not None else PeriodFacts()
    return YearInput(
        year=year,
        employment=Employment(ccnl_slug=ccnl_slug, level_code=level_code, **employment),
        employer=employer,
        prior_year=prior_year if prior_year is not None else PriorYearTaxFacts(),
        periods={
            key: replace(base, events=run_events)
            for key, run_events in (events or {}).items()
        },
        default_facts=base,
        calendar_override=calendar_override,
        payment_day=payment_day,
        opening_state=opening_state,
    )
