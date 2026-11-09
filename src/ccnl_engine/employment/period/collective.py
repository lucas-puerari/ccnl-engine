"""Facts about a collective dismissal."""

from dataclasses import dataclass

from ccnl_engine.validators import require_bool


@dataclass(frozen=True, slots=True)
class CollectiveDismissal:
    """A dismissal at the end of a collective procedure (L. 223/1991 art. 4).

    Attributes:
        union_agreement: Whether the declaration of redundancy was the
            object of a union agreement; without one the contribution is
            three times (L. 92/2012 art. 2 c. 35).
        cigs_employer: Whether the employer owes the CIGS contribution (art.
            23 D.Lgs. 148/2015); its rate is 82% (L. 205/2017 art. 1 c. 137).

    Raises:
        InvalidInputError: When a flag is not a ``bool``.
    """

    union_agreement: bool
    cigs_employer: bool

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("union_agreement", "cigs_employer"):
            require_bool(
                getattr(self, name),
                f"CollectiveDismissal.{name}",
                feature="employment_facts",
            )
