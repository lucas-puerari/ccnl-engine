"""Validation helpers for CCNL cross-field checks."""

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from ccnl_engine.engine.contract.domain.seniority import SeniorityIncrements
from ccnl_engine.engine.contract.domain.validity import SalaryGapError
from ccnl_engine.engine.provenance.domain.source import SourceKind


def _check_salary_ordering_at_date(sorted_levels: list[Any], check_date: date) -> None:
    """Verify that base salaries are non-decreasing across levels on one date.

    Raises:
        ValueError: If any level earns less than a lower-ordered level on that date.
    """
    prev_value: Decimal | None = None
    prev_code: str = ""
    for lv in sorted_levels:
        try:
            value = lv.base_salary.value_at(check_date)
        except SalaryGapError:
            continue
        except ValueError:
            continue
        if prev_value is not None and value < prev_value:
            msg = (
                f"salary ordering violated on {check_date}: "
                f"level {lv.code!r} (order={lv.order}) "
                f"earns {value} < level {prev_code!r} earns {prev_value}"
            )
            raise ValueError(msg)
        prev_value = value
        prev_code = lv.code


def _assert_level_provenance(level: Any) -> None:  # noqa: ANN401
    """Check that all non-gap salary periods and allowances carry provenance.

    Gap periods are exempt: they hold no source data.

    Raises:
        ValueError: If provenance is missing on the level itself, any non-gap
            salary period, or any fixed allowance.
    """
    prefix = f"level {level.code!r}"
    if level.provenance is None:
        msg = f"{prefix}: provenance is required"
        raise ValueError(msg)
    for i, period in enumerate(level.base_salary.periods):
        if period.is_gap:
            continue
        if period.provenance is None:
            msg = f"{prefix}: base_salary.periods[{i}].provenance is required"
            raise ValueError(msg)
    for allowance in level.fixed_allowances:
        if allowance.provenance is None:
            msg = f"{prefix}: allowance {allowance.code!r}.provenance is required"
            raise ValueError(msg)


def _check_flat_level_codes(existing: set[str], si: SeniorityIncrements) -> None:
    for field_name, mapping in (
        ("amount_by_level", si.amount_by_level),
        ("maximum_count_by_level", si.maximum_count_by_level),
        ("first_cadence_months_by_level", si.first_cadence_months_by_level),
    ):
        for code in mapping:
            if code not in existing:
                msg = (
                    f"seniority_increments.{field_name} references level "
                    f"code {code!r} which does not exist in levels"
                )
                raise ValueError(msg)


def _check_category_level_codes(existing: set[str], si: SeniorityIncrements) -> None:
    for cat, cat_amounts in si.amount_by_level_by_category.items():
        for code in cat_amounts:
            if code not in existing:
                msg = (
                    f"seniority_increments.amount_by_level_by_category"
                    f"[{cat!r}] references level code {code!r} which "
                    f"does not exist in levels"
                )
                raise ValueError(msg)


def _check_tier_level_codes(existing: set[str], si: SeniorityIncrements) -> None:
    for i, tier in enumerate(si.tiers):
        for code in tier.amount_by_level:
            if code not in existing:
                msg = (
                    f"seniority_increments.tiers[{i}].amount_by_level "
                    f"references level code {code!r} which does not exist "
                    f"in levels"
                )
                raise ValueError(msg)


def _assert_unique(field: str, values: list[object]) -> None:
    if len(values) != len(set(values)):
        msg = f"level {field} values must be unique, got: {values}"
        raise ValueError(msg)


def _collect_transition_dates(levels: list[Any]) -> set[date]:
    all_dates: set[date] = set()
    for lv in levels:
        all_dates.update(period.valid_from for period in lv.base_salary.periods)
    return all_dates


def _coerce_legacy_source(source: dict[str, Any]) -> dict[str, Any]:
    """Shape a legacy ``meta.sources`` entry (schema 0.4) into a SourceDocument.

    Returns:
        A dict shaped for :class:`SourceDocument`.
    """
    url = source.get("url", "")
    doc_id = _slugify_url(url) or "source"
    kind = _legacy_source_kind(source.get("type"))
    return {
        "document_id": doc_id,
        "title": source.get("notes") or url or doc_id,
        "kind": kind,
        "url": url,
        "pages": [],
        "published_on": (
            source["agreement_date"] if source.get("agreement_date") else None
        ),
    }


def _slugify_url(url: str) -> str:
    slug = (
        url
        .strip()
        .lower()
        .replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
    )
    keep: list[str] = [ch if ch.isalnum() or ch in "-_" else "-" for ch in slug]
    squashed = "".join(keep).strip("-").strip("_")
    return squashed[:80]


def _legacy_source_kind(raw: str | None) -> SourceKind:  # noqa: PLR0911
    value = (raw or "").lower()
    if any(token in value for token in ("tabella", "table", "salary", "wage")):
        return SourceKind.TABELLA_RETRIBUTIVA
    if "gazzetta" in value:
        return SourceKind.GAZZETTA
    if "cnel" in value:
        return SourceKind.CNEL
    if any(token in value for token in ("circolar", "circular")):
        return SourceKind.INPS_CIRCOLARE
    if "legge" in value:
        return SourceKind.LEGGE
    if "dpr" in value:
        return SourceKind.DPR
    if any(token in value for token in ("dl ", "decreto")):
        return SourceKind.DL
    if any(token in value for token in ("associazion", "aggregator")):
        return SourceKind.ASSOCIAZIONE
    return SourceKind.ALTRO


def _coerce_legacy_extraction(
    extraction: dict[str, Any], meta: dict[str, Any]
) -> dict[str, Any]:
    """Shape a legacy ``meta.extraction`` block (schema 0.4) into an ExtractionTrace.

    ``effective_from`` is inferred from ``meta.validity`` when present, else
    set to a pre-agreement epoch so the trace always carries a date.

    Returns:
        A dict shaped for :class:`ExtractionTrace`.
    """
    human_reviewed = bool(extraction.get("human_reviewed"))
    raw_validity = meta.get("validity")
    validity: dict[str, Any] = raw_validity if isinstance(raw_validity, dict) else {}
    timestamp = extraction.get("timestamp") or datetime.now(tz=UTC).isoformat()
    return {
        "method": extraction.get("method") or "manual",
        "model": extraction.get("model"),
        "extraction_timestamp": timestamp,
        "verification_status": "verified" if human_reviewed else "unverified",
        "effective_from": validity.get("valid_from") or "1970-01-01",
    }
