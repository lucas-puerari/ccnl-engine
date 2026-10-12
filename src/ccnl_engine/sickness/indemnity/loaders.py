"""INPS sick-pay indemnity rates of the bundle."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.sector.raw.loaders import (
    _as_ruleset,
    _provenance_of,
    _read_json,
)
from ccnl_engine.sickness.indemnity.models import (
    FixedTermSickLimit,
    InpsSickPayRates,
    SickPayRegime,
)

_SICK_PAY_FILE = "sickness/indemnity/rates.json"


def load_sick_pay_rates() -> InpsSickPayRates:
    """Load INPS statutory sick-pay indemnity rates from the bundled data file.

    The file ``knowledge/sickness/indemnity/rates.json`` is not year- or
    sector-specific: statutory sick-pay rates change only by primary
    legislation (D.L. 663/1979, artt. 1-2, conv. L. 33/1980).

    Returns:
        An :class:`~ccnl_engine.sickness.indemnity.models.InpsSickPayRates`
        with the INPS carenza period, indemnity bands, annual maximum,
        coverage rules and provenance.
    """
    return sick_pay_rates_from(_read_json(_SICK_PAY_FILE), _SICK_PAY_FILE)


def _fixed_term(raw: dict[str, Any] | None) -> FixedTermSickLimit | None:
    if raw is None:
        return None
    return FixedTermSickLimit.model_validate({
        **{k: v for k, v in raw.items() if k != "description"},
        "provenance": _provenance_of(raw),
    })


def sick_pay_rates_from(raw: dict[str, Any], filename: str) -> InpsSickPayRates:
    """Return the sick-pay rates of the payload ``raw`` of ``filename``.

    ``carenza_days``, ``bands``, ``annual_max_days`` and ``coverage`` are
    required: a statutory table never takes a legal value it does not
    state.

    Returns:
        The validated rates.

    Raises:
        DataIntegrityError: When a required field is missing or a value is
            rejected, naming ``filename``.
    """
    try:
        return InpsSickPayRates(
            description=raw.get("description", ""),
            carenza_days=raw["carenza_days"],
            bands=raw["bands"],
            annual_max_days=raw["annual_max_days"],
            coverage=raw["coverage"],
            ruleset=_as_ruleset(raw),
            bands_provenance=_provenance_of({
                "provenance": raw.get("bands_provenance")
            }),
            regimes=tuple(
                SickPayRegime.model_validate({
                    **regime,
                    "provenance": _provenance_of(regime),
                })
                for regime in raw.get("regimes", ())
            ),
            fixed_term=_fixed_term(raw.get("fixed_term")),
        )
    except KeyError as exc:
        msg = f"{filename}: required field {exc.args[0]!r} is missing"
        raise DataIntegrityError(msg) from exc
    except ValidationError as exc:
        msg = f"{filename}: invalid sick-pay rates: {exc}"
        raise DataIntegrityError(msg) from exc
