"""Comparison methods for counting extra-month accrual."""

from enum import StrEnum


class AccrualComparison(StrEnum):
    """How the accruing days of a month are compared with the threshold.

    Attributes:
        AT_LEAST: The month counts when its days reach the threshold
            ("pari o superiore a 15 giorni").
        MORE_THAN: The month counts when its days exceed the threshold
            ("frazione superiore a 15 giorni").
        WORKING_DAYS_26: No threshold: a month not worked in full accrues
            its accruing days from Monday to Saturday as twenty-sixths of a
            rateo, at most one (CCNL Turismo 2024, art. 160 c. 2: "i giorni
            lavorati - determinati in ventiseiesimi - [...] daranno diritto
            alla maturazione di un ugual numero di ventiseiesimi di un
            rateo mensile").
        DAYS_365: A whole month accrues a twelfth, a month served in part
            a 365th of the year for each day served (CCNL Sanità 2022-2024
            art. 60 c. 4: "per le frazioni di mese, in ragione di un
            trecentosessantacinquesimo per i giorni prestati nel mese").
        DAYS_360: As ``DAYS_365`` with a 360th for each day of a month
            served in part (CCNL Area I 21 April 2006 art. 63 c. 4).
        SERVICE_DAYS_365: Every day served accrues a 365th of the year,
            whole months too (CCNL Funzioni Locali 16 November 2022 art. 75
            c. 3: "in ragione di tanti 365esimi quanti sono i giorni di
            servizio prestato").
        CUMULATED_FRACTIONS: A whole month accrues a rateo; the days of the
            months served in part are summed, and each 30 days accrue a
            rateo, a remainder of 15 days or more one more (CCNL Pubblici
            Esercizi 8 February 2018 art. 183 c. 2: "le frazioni di mese
            saranno cumulate [...] un rateo mensile per ogni trenta giorni
            di calendario, nonché per la eventuale frazione residua pari o
            superiore a quindici giorni").
    """

    AT_LEAST = "at_least"
    MORE_THAN = "more_than"
    WORKING_DAYS_26 = "working_days_26"
    DAYS_365 = "days_365"
    DAYS_360 = "days_360"
    SERVICE_DAYS_365 = "service_days_365"
    CUMULATED_FRACTIONS = "cumulated_fractions"

    @property
    def by_days(self) -> bool:
        """Whether the rule accrues days rather than comparing a threshold."""
        return self not in {AccrualComparison.AT_LEAST, AccrualComparison.MORE_THAN}
