"""General causes of the end of an employment and NASpI exception cases."""

from enum import StrEnum


class TerminationCause(StrEnum):
    """How an employment ends.

    Attributes:
        DISMISSAL: The employer dismisses the worker (licenziamento).
        RESIGNATION: The worker resigns (dimissioni).
        DEATH: The worker dies.
        MUTUAL_AGREEMENT: The parties agree to end it (risoluzione
            consensuale).
    """

    DISMISSAL = "dismissal"
    RESIGNATION = "resignation"
    DEATH = "death"
    MUTUAL_AGREEMENT = "mutual_agreement"


_JUST_CAUSE = frozenset({TerminationCause.DISMISSAL, TerminationCause.RESIGNATION})


class NaspiCase(StrEnum):
    """The case of an end of employment that changes the NASpI contribution.

    Attributes:
        ORDINARY: None of the cases below.
        PROTECTED_MATERNITY: A resignation in the protected period of
            maternity (INPS circ. 44/2013 par. 1): owes it.
        CONCILIATION: A mutual agreement before the labour office (art. 7
            L. 604/1966): owes it.
        TRANSFER: A mutual agreement on a transfer more than 50 km from home
            or 80 minutes away by public transport: owes it.
        CONTRACTOR_CHANGE: A dismissal on a change of contractor followed by
            hiring under a social clause (L. 92/2012 art. 2 c. 34 lett. a):
            owes none.
        SITE_CLOSURE: A dismissal in construction on the end of the works
            and closure of the site (c. 34 lett. b): owes none.
    """

    ORDINARY = "ordinary"
    PROTECTED_MATERNITY = "protected_maternity"
    CONCILIATION = "conciliation"
    TRANSFER = "transfer"
    CONTRACTOR_CHANGE = "contractor_change"
    SITE_CLOSURE = "site_closure"


_CASE_CAUSE = {
    NaspiCase.PROTECTED_MATERNITY: TerminationCause.RESIGNATION,
    NaspiCase.CONCILIATION: TerminationCause.MUTUAL_AGREEMENT,
    NaspiCase.TRANSFER: TerminationCause.MUTUAL_AGREEMENT,
    NaspiCase.CONTRACTOR_CHANGE: TerminationCause.DISMISSAL,
    NaspiCase.SITE_CLOSURE: TerminationCause.DISMISSAL,
}
