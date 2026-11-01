"""TFR fund of the employment: the balance at 31 December and the year's quotas."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import ROUND_HALF_UP, Decimal

from ccnl_engine.collection.validators import items_of_type, tuple_of
from ccnl_engine.employment.fact.inputs import FEATURE
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import (
    reject,
    require_decimal,
    require_int,
)

__all__ = ["TfrFundBalance", "TfrQuotaYtd"]

_CENT = Decimal("0.01")
_ZERO = Decimal(0)


def _require_cents(value: Decimal | None, path: str, *, signed: bool = False) -> None:
    """Reject a value that is not ``None`` or an amount in cents.

    The amount must be non-negative unless ``signed``.
    """
    minimum = None if signed else _ZERO
    require_decimal(value, path, feature=FEATURE, minimum=minimum, optional=True)
    if value is not None and value != value.quantize(_CENT, rounding=ROUND_HALF_UP):
        reject(path, "an amount with at most two decimals", value, feature=FEATURE)


@dataclass(frozen=True, slots=True)
class TfrFundBalance:
    """TFR the worker has accrued with the employer at 31 December of a year.

    The fund at 31 December of ``year``, after the revaluation of that date
    and net of the substitute tax charged to it, less the advances paid:
    the TFR the next year revalues (art. 2120 c. 4 c.c.: the quota accrued
    in the year is excluded).  It includes the part paid to the Fondo
    Tesoreria INPS, whose share the Fondo pays out under art. 2120 c.c.
    (DM 30 gennaio 2007 art. 2 c. 1), and excludes the TFR paid to a
    complementary pension fund.

    The separate taxation of the TFR at the termination (art. 19 c. 1
    TUIR) needs two more facts of the same fund: the revaluations it
    holds, already taxed at the substitute rate and left out of the
    taxable, and whether advances were paid out of it.

    Attributes:
        year: Year at whose 31 December the balance is struck.
        amount: Balance in EUR, non-negative, with at most two decimals.
        revaluations: Part of ``amount`` that comes from the revaluations
            of the past years, net of their substitute tax; ``None`` when
            not known.
        advances: Advances paid out of the fund over the employment (art.
            2120 c. 6 c.c.), already deducted from ``amount``; ``None``
            when not known, ``0`` when none was paid.
        advances_taxable: The taxable of those advances at their separate
            taxation: their amount less the revaluations they held, already
            taxed at the substitute rate (art. 19 c. 4 TUIR); ``None`` when
            not known.
        advances_tax: The IRPEF withheld on those advances, which the
            termination takes back in the conguaglio of art. 19 c. 4 TUIR;
            ``None`` when not known.

    Raises:
        InvalidInputError: When ``year`` is not an int from 1900, an amount
            is not a non-negative Decimal in cents, ``revaluations``
            exceeds ``amount`` or ``advances_taxable`` exceeds ``advances``.
    """

    year: int
    amount: Decimal
    revaluations: Decimal | None = None
    advances: Decimal | None = None
    advances_taxable: Decimal | None = None
    advances_tax: Decimal | None = None

    def __post_init__(self) -> None:  # noqa: D105
        require_int(self.year, "TfrFundBalance.year", feature=FEATURE, minimum=1900)
        require_decimal(
            self.amount, "TfrFundBalance.amount", feature=FEATURE, minimum=_ZERO
        )
        _require_cents(self.amount, "TfrFundBalance.amount")
        _require_cents(self.revaluations, "TfrFundBalance.revaluations")
        for name in ("advances", "advances_taxable", "advances_tax"):
            _require_cents(getattr(self, name), f"TfrFundBalance.{name}")
        if self.revaluations is not None and self.revaluations > self.amount:
            reject(
                "TfrFundBalance.revaluations",
                f"an amount within the fund ({self.amount})",
                self.revaluations,
                feature=FEATURE,
            )
        advances, taxable = self.advances, self.advances_taxable
        if advances is not None and taxable is not None and taxable > advances:
            reject(
                "TfrFundBalance.advances_taxable",
                f"an amount within the advances ({advances})",
                taxable,
                feature=FEATURE,
            )


@dataclass(frozen=True, slots=True)
class TfrQuotaYtd:
    """TFR the runs of one competence year accrued with the employer.

    The quotas of art. 2120 c. 1 c.c. net of the additional IVS of L.
    297/1982, posted to the company accrual or to the Fondo Tesoreria
    INPS, as :class:`TfrFundBalance` counts them; the TFR paid to a
    complementary pension fund is left out.  The quotas of a year enter
    the fund at its 31 December: until then the settlement of a
    termination adds them to the fund of the year before.

    Attributes:
        year: The competence year.
        amount: Sum of the quotas of the runs of :attr:`year`; an
            adjustment run that lowers the TFR base posts a negative quota.

    Raises:
        InvalidInputError: When ``year`` is not an int from 1970 to 9999 or
            ``amount`` is not a finite Decimal in cents.
    """

    year: int
    amount: Decimal = _ZERO

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.year, "TfrQuotaYtd.year", feature=FEATURE, minimum=1970, maximum=9999
        )
        require_decimal(self.amount, "TfrQuotaYtd.amount", feature=FEATURE)
        _require_cents(self.amount, "TfrQuotaYtd.amount", signed=True)

    def plus(self, quota: Decimal) -> TfrQuotaYtd:
        """Return the quotas with ``quota`` of one more run added.

        Returns:
            A new record of the same year.
        """
        return replace(self, amount=self.amount + quota)


def checked_quotas(
    value: object, path: str, known_from: object
) -> tuple[TfrQuotaYtd, ...]:
    """Validate the TFR quotas of a state: one per year, in year order.

    ``known_from`` is the first year they count in full, ``None`` for all.

    Returns:
        The quotas as a tuple.

    Raises:
        InvalidInputError: When a quota is not a :class:`TfrQuotaYtd` or two
            are of the same year or out of year order.
    """
    quotas = tuple_of(
        value, path, items_of_type(TfrQuotaYtd, feature=FEATURE), feature=FEATURE
    )
    years = [q.year for q in quotas]
    if years != sorted(set(years)):
        msg = f"tfr_quotas must hold one quota per year, in year order; got {years}"
        raise InvalidInputError(msg, field=path, feature=FEATURE)
    require_int(
        known_from,
        f"{path}_known_from",
        feature=FEATURE,
        minimum=1970,
        maximum=9999,
        optional=True,
    )
    return quotas


def quota_of(
    quotas: tuple[TfrQuotaYtd, ...], known_from: int | None, year: int
) -> TfrQuotaYtd | None:
    """Return the quotas of ``year``.

    Returns:
        The quotas of the year, zero when none is recorded; ``None`` for a
        year before ``known_from``.
    """
    if known_from is not None and year < known_from:
        return None
    return next((q for q in quotas if q.year == year), TfrQuotaYtd(year))


def quotas_with(
    quotas: tuple[TfrQuotaYtd, ...], year: int, quota: Decimal
) -> tuple[TfrQuotaYtd, ...]:
    """Return ``quotas`` with ``quota`` added to the quotas of ``year``.

    Returns:
        The quotas, one per year in year order.
    """
    current = next((q for q in quotas if q.year == year), TfrQuotaYtd(year))
    others = [q for q in quotas if q.year != year]
    return tuple(sorted((*others, current.plus(quota)), key=lambda q: q.year))
