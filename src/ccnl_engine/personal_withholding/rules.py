"""Legal limits of the deductions from the net pay paid to third parties.

Art. 545 c.p.c. (Normattiva, in force on 31 October 2026):

- c. 3: the pay "possono essere pignorate per crediti alimentari nella
  misura autorizzata dal presidente del tribunale o da un giudice da lui
  delegato";
- c. 4: "Tali somme possono essere pignorate nella misura di un quinto per i
  tributi dovuti allo Stato, alle province e ai comuni, ed in eguale misura
  per ogni altro credito";
- c. 5: "Il pignoramento per il simultaneo concorso delle cause indicate
  precedentemente non può estendersi oltre alla metà dell'ammontare delle
  somme predette."

Art. 72-ter c. 1-2 DPR 602/1973, in force until 31 December 2026, and art.
171 c. 1-2 D.Lgs. 33/2025 from 1 January 2027, in the same words: the
agente della riscossione garnishes the pay "in misura pari ad un decimo per
importi fino a 2.500 euro e in misura pari ad un settimo per importi
superiori a 2.500 euro e non superiori a 5.000 euro", and the fifth of art.
545 c. 4 above 5,000 euro.

D.P.R. 180/1950, which covers the pay "le aziende private corrispondono ai
loro impiegati" too (art. 1; Normattiva page sha256
dc8fe33f7922e6e1cc0dc900acf4171c47969f9fd21ec025d1bca6fb31eece4a):

- art. 2 measures each limit on the pay "valutato al netto di ritenute"
  (page sha256
  b25d83946762b9e411313a1c720ae29204ff4967b00c3369491e1b52385a2bfa);
- art. 5: a loan is repaid "con cessione di quote dello stipendio o del
  salario fino al quinto dell'ammontare di tali emolumenti valutato al netto
  di ritenute";
- art. 68: "Quando preesistono sequestri o pignoramenti, la cessione, fermo
  restando il limite di cui al primo comma dell'art. 5, non può essere fatta
  se non limitatamente alla differenza tra i due quinti dello stipendio o
  salario valutati al netto delle ritenute e la quota colpita da sequestri o
  pignoramenti.  Qualora i sequestri o i pignoramenti abbiano luogo dopo una
  cessione perfezionata e debitamente notificata, non si può sequestrare o
  pignorare se non la differenza fra la metà dello stipendio o salario
  valutati al netto di ritenute e la quota ceduta";
- art. 69 sets the same half between a delegazione and a garnishment, in
  either order, and art. 70 between a cessione and a delegazione.

The engine reads them as follows:

- the base is the net pay of the run before these deductions: the pay less
  the contributions and the taxes withheld.  The TFR the run settles and its
  separate tax are left out
  (:mod:`~ccnl_engine.personal_withholding.services`);
- the 2,500 and 5,000 euro of the agente della riscossione are compared
  with the same base, the "importi" of the pay "al netto di ritenute";
- the deductions are taken in the order of notification: each keeps its
  amount, and a later one takes what its own limit and the combined limits
  leave after the earlier ones.  The half of art. 545 c. 5 and art. 68-70
  binds every deduction that follows another one;
- two garnishments of the same kind, or two cessioni, share the fifth (or
  tenth, or seventh) of their kind in the order of notification: no text
  read says how the measure is split (engine limitation
  ``personal_withholding_same_kind``);
- each limit is rounded down to the cent: art. 545 makes a garnishment
  beyond its limits "parzialmente inefficace".
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
from typing import TYPE_CHECKING

from ccnl_engine.personal_withholding.inputs import PersonalWithholdingKind
from ccnl_engine.personal_withholding.limit.rules import (
    ASSIGNMENT_LIMIT,
    ASSIGNMENTS,
    FIFTH_LIMIT,
    INSTALLMENT_LIMITS,
    half_rule,
    tax_collection_limit,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ccnl_engine.personal_withholding.limit.rules import LegalLimit

__all__ = ["DueWithholding", "Withheld", "allocate", "tax_collection_fraction"]

_ZERO = Decimal(0)
_CENT = Decimal("0.01")
_LOW_BAND = Decimal(2500)
_HIGH_BAND = Decimal(5000)
_FIFTH = Decimal(1) / Decimal(5)
_K = PersonalWithholdingKind


def _down(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_DOWN)


def tax_collection_fraction(base: Decimal) -> Decimal:
    """Return the fraction the agente della riscossione garnishes of ``base``.

    Returns:
        One tenth up to 2,500 euro, one seventh above it up to 5,000 euro,
        one fifth above 5,000 euro.
    """
    if base <= _LOW_BAND:
        return Decimal(1) / Decimal(10)
    if base <= _HIGH_BAND:
        return Decimal(1) / Decimal(7)
    return _FIFTH


@dataclass(frozen=True)
class DueWithholding:
    """A deduction a run may withhold, in the order of notification.

    Attributes:
        kind: Its kind.
        installment: Stated monthly amount; ``None`` for a legal fraction.
        residual: What is still due to the creditor, at least zero.
    """

    kind: PersonalWithholdingKind
    installment: Decimal | None
    residual: Decimal


@dataclass(frozen=True)
class Withheld:
    """What a run withholds of one deduction.

    Attributes:
        amount: Amount withheld.
        limit: Legal limit of the deduction on the run, before its
            installment and residual.
        rule: Rule of that limit.
    """

    amount: Decimal
    limit: Decimal
    rule: LegalLimit


def _own_limit(
    due: DueWithholding, base: Decimal, year: int
) -> tuple[Decimal, LegalLimit]:
    """Return the limit of ``due`` alone, before the earlier deductions.

    Returns:
        A fifth of the base for a salary assignment and an ordinary or tax
        garnishment, the fraction of :func:`tax_collection_fraction` for the
        agente della riscossione, the stated amount for a maintenance order
        and a delegation; with its rule.
    """
    if due.kind is _K.TAX_COLLECTION:
        fraction = tax_collection_fraction(base)
        return _down(base * fraction), tax_collection_limit(year)
    if due.kind in INSTALLMENT_LIMITS and due.installment is not None:
        return due.installment, INSTALLMENT_LIMITS[due.kind]
    rule = ASSIGNMENT_LIMIT if due.kind is _K.SALARY_ASSIGNMENT else FIFTH_LIMIT
    return _down(base * _FIFTH), rule


def _combined_limit(
    due: DueWithholding,
    taken: Sequence[tuple[PersonalWithholdingKind, Decimal]],
    base: Decimal,
) -> tuple[Decimal, LegalLimit] | None:
    """Return the limit the earlier deductions of the run leave to ``due``.

    Returns:
        ``None`` for the first deduction; otherwise half the base less the
        earlier ones, or, for a salary assignment after a garnishment, two
        fifths less the garnishments when lower, with its rule.
    """
    if not taken:
        return None
    left = _down(base / 2) - sum((a for _, a in taken), _ZERO)
    garnished = sum((a for k, a in taken if k not in ASSIGNMENTS), _ZERO)
    if due.kind is _K.SALARY_ASSIGNMENT and garnished:
        left = min(left, _down(base * 2 * _FIFTH) - garnished)
    return left, half_rule(due.kind, frozenset(k for k, _ in taken))


def allocate(
    base: Decimal, dues: Sequence[DueWithholding], year: int
) -> tuple[Withheld, ...]:
    """Return what a run withholds of each deduction, in the order given.

    Args:
        base: Net pay of the run the limits are measured on.
        dues: Deductions active on the run, in the order of notification.
        year: Year of the payment, which selects the text of the
            tax-collection limit.

    Returns:
        Per deduction, the amount withheld with its limit and rule.  A
        deduction of a kind already withheld takes what is left of the
        measure of its kind (the stated amount of a maintenance order or a
        delegation is its own); a deduction after another one at most what
        :func:`_combined_limit` leaves.  The installment and the residual
        cap the amount, and the deductions never exceed the base: the first
        one at most the base, a later one at most the half of it the
        combined limit leaves.
    """
    base = max(_ZERO, base)
    taken: list[tuple[PersonalWithholdingKind, Decimal]] = []
    out: list[Withheld] = []
    for due in dues:
        limit, rule = _own_limit(due, base, year)
        if due.kind not in INSTALLMENT_LIMITS:
            limit -= sum((a for k, a in taken if k is due.kind), _ZERO)
        combined = _combined_limit(due, taken, base)
        if combined is not None and combined[0] < limit:
            limit, rule = combined
        limit = max(_ZERO, min(limit, base))
        amount = min(limit, due.residual)
        if due.installment is not None:
            amount = min(amount, due.installment)
        out.append(Withheld(amount, limit, rule))
        taken.append((due.kind, amount))
    return tuple(out)
