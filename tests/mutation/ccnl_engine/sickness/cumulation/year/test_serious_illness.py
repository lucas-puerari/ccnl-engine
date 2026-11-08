"""Diagnosis-specific comporto and paid days in the signed CCNLs."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.counting.rules import with_window_counting
from ccnl_engine.sickness.cumulation.rules import SicknessWorker
from ccnl_engine.sickness.cumulation.year.rules import YearTreatment
from ccnl_engine.sickness.integration.models import SicknessRules
from ccnl_engine.sickness.models import SeriousIllnessKind, SicknessEpisode


def _rules(ccnl_id: str, *, window: bool = False) -> SicknessRules:
    ccnl = load_ccnl(ccnl_id)
    if window:
        ccnl = with_window_counting(ccnl, True)
    assert ccnl.work_rules is not None
    assert ccnl.work_rules.sickness_rules is not None
    return ccnl.work_rules.sickness_rules


def _day(
    rules: SicknessRules,
    episode: SicknessEpisode,
    index: int,
    earlier: tuple[SicknessEpisode, ...] = (),
) -> tuple[bool, Decimal]:
    day = episode.started_on + timedelta(days=index - 1)
    year = YearTreatment(
        rules,
        episode,
        earlier,
        SicknessWorker(),
        lambda i: next(
            (b.integration_rate for b in rules.day_bands if b.holds(i)),
            rules.full_pay_integration_rate,
        ),
    )
    treatment = year.day(index, day)
    return treatment.beyond_comporto, treatment.rate


def test_studi_serious_month_nine_vs_ordinary() -> None:
    """At €10/day, day 241 pays €7 serious versus €0 ordinary (past 180)."""
    rules = _rules("studi-professionali-confprofessioni")
    start = date(2026, 1, 1)
    end = start + timedelta(days=270)
    ordinary = SicknessEpisode("ordinary", start, end)
    serious = SicknessEpisode("documented-illness", start, end, serious_illness=True)
    assert _day(rules, ordinary, 241) == (True, Decimal(1))
    assert _day(rules, serious, 241) == (False, Decimal("0.7"))
    assert Decimal(10) * _day(rules, serious, 241)[1] == Decimal(7)
    assert _day(rules, serious, 270) == (False, Decimal("0.7"))
    assert _day(rules, serious, 271)[0]


def test_abi_oncological_vs_ordinary_and_other_qualifying_diagnoses() -> None:
    """At €10/day, day 181 pays €10 for oncology versus €0 ordinary."""
    rules = _rules("bancari-abi")
    start = date(2026, 1, 1)
    end = start + timedelta(days=360)
    ordinary = SicknessEpisode("ordinary", start, end)
    oncology = SicknessEpisode(
        "oncology", start, end, serious_illness_kind=SeriousIllnessKind.ONCOLOGICAL
    )
    assert _day(rules, ordinary, 181)[0]
    assert _day(rules, oncology, 181) == (False, Decimal(1))
    assert Decimal(10) * _day(rules, oncology, 181)[1] == Decimal(10)
    assert _day(rules, oncology, 360)[0] is False
    assert _day(rules, oncology, 361)[0] is True
    for kind in (
        SeriousIllnessKind.TUBERCULOSIS_CARE,
        SeriousIllnessKind.AIDS,
        SeriousIllnessKind.SEVERE_DISABILITY,
    ):
        case = SicknessEpisode(kind, start, end, serious_illness_kind=kind)
        assert _day(rules, case, 360)[0] is False
        assert _day(rules, case, 361)[0] is True
    # A generic flag alone does not certify an ABI c. 4 diagnosis.
    assert _day(
        rules, SicknessEpisode("generic", start, end, serious_illness=True), 181
    )[0]


def test_abi_seniority_bands_respect_floors_caps_and_half_month() -> None:
    """15 months x 1.5 = 22.5 months = 675 days; 22 x 2 caps at 36."""
    rules = _rules("bancari-abi")
    assert [
        (b.comporto_days, b.serious_comporto_days, b.oncological_comporto_days)
        for b in rules.comporto_bands
    ] == [
        (180, 360, 360),
        (240, 360, 480),
        (360, 540, 720),
        (450, 675, 900),
        (540, 810, 1080),
        (660, 900, 1080),
    ]


def test_abi_alternative_window_keeps_diagnosis_specific_limits() -> None:
    """In the 48-month variant, 240 ordinary days versus 480 oncological."""
    rules = _rules("bancari-abi", window=True)
    start = date(2026, 1, 1)
    end = start + timedelta(days=480)
    ordinary = SicknessEpisode("ordinary", start, end)
    oncology = SicknessEpisode(
        "oncology", start, end, serious_illness_kind=SeriousIllnessKind.ONCOLOGICAL
    )
    assert _day(rules, ordinary, 241)[0]
    assert _day(rules, oncology, 241) == (False, Decimal(1))
    assert _day(rules, oncology, 481)[0]
    assert [
        (b.comporto_days, b.serious_comporto_days, b.oncological_comporto_days)
        for b in rules.comporto_bands
    ] == [
        (240, 360, 480),
        (300, 450, 600),
        (420, 630, 840),
        (540, 810, 1080),
        (660, 900, 1080),
        (720, 900, 1080),
    ]


def test_qualifying_treatment_days_do_not_consume_comporto() -> None:
    """At €10/day, day 181 still pays €10 after one excluded dialysis day."""
    for ccnl_id in ("bancari-abi", "studi-professionali-confprofessioni"):
        rules = _rules(ccnl_id)
        start = date(2026, 1, 1)
        end = start + timedelta(days=181)
        episode = SicknessEpisode(
            "treated", start, end, excluded_comporto_days=(start,)
        )
        assert _day(rules, episode, 181)[0] is False
        assert _day(rules, episode, 182)[0] is True
        prior = SicknessEpisode("prior", start, start, excluded_comporto_days=(start,))
        later = SicknessEpisode("later", start + timedelta(days=10), end)
        if rules.comporto_windows:
            year = YearTreatment(
                rules, later, (prior,), SicknessWorker(), lambda _: Decimal(1)
            )
            assert year.window_days(year.window, later.started_on) == 1  # type: ignore[arg-type]


def test_excluded_days_in_a_relapse_chain_are_not_counted_twice() -> None:
    """The 181st calendar day still pays €10 with one excluded earlier day."""
    rules = _rules("bancari-abi")
    start = date(2026, 1, 1)
    prior = SicknessEpisode(
        "prior", start, start + timedelta(days=179), excluded_comporto_days=(start,)
    )
    current = SicknessEpisode(
        "relapse",
        start + timedelta(days=180),
        start + timedelta(days=181),
        relapse_of="prior",
    )
    worker = SicknessWorker()
    year = YearTreatment(rules, current, (prior,), worker, lambda _: Decimal(1))
    assert not year.day(181, current.started_on).beyond_comporto
    assert year.day(182, current.ended_on).beyond_comporto
    # A caller cannot count an unrecorded relapse as a recorded history.
    unknown = SicknessEpisode(
        "unrecorded", current.started_on, current.ended_on, relapse_of="missing"
    )
    missing = YearTreatment(rules, unknown, (prior,), worker, lambda _: Decimal(1))
    assert missing.day(181, unknown.started_on).beyond_comporto
    shortened = SicknessEpisode(
        "truncated",
        start,
        start + timedelta(days=3),
        excluded_comporto_days=(start, start + timedelta(days=3)),
    ).through(start + timedelta(days=1))
    assert shortened.excluded_comporto_days == (start,)


def test_invalid_diagnosis_and_excluded_dates_are_rejected() -> None:
    """An unverified diagnosis or out-of-episode date cannot extend the job."""
    start = date(2026, 1, 1)
    with pytest.raises(InvalidInputError, match="serious_illness_kind"):
        SicknessEpisode(
            "invalid",
            start,
            start,
            serious_illness_kind="serious",  # type: ignore[arg-type]
        )
    with pytest.raises(InvalidInputError, match="excluded_comporto_days"):
        SicknessEpisode(
            "invalid", start, start, excluded_comporto_days=(start + timedelta(days=1),)
        )
    with pytest.raises(InvalidInputError, match="duplicate day"):
        SicknessEpisode(
            "duplicate", start, start, excluded_comporto_days=(start, start)
        )


def test_an_abi_diagnosis_does_not_extend_the_studi_comporto() -> None:
    """Studi art. 120 lists its own illnesses, not those of ABI.

    A tuberculosis-care kind alone leaves day 181 past the 180 days.
    """
    rules = _rules("studi-professionali-confprofessioni")
    start = date(2026, 1, 1)
    end = start + timedelta(days=200)
    abi_only = SicknessEpisode(
        "tbc", start, end, serious_illness_kind=SeriousIllnessKind.TUBERCULOSIS_CARE
    )
    assert _day(rules, abi_only, 181)[0]


def test_new_serious_episode_in_month_nine_pays_its_waiting_days_at_70() -> None:
    """A new serious episode in month nine pays its carenza day at 70%.

    After a 240-day serious illness the next day is in month nine (70%), not
    at the carenza 100%.
    """
    rules = _rules("studi-professionali-confprofessioni")
    first = SicknessEpisode(
        "first",
        date(2026, 1, 1),
        date(2026, 1, 1) + timedelta(days=239),
        serious_illness=True,
    )
    again = date(2026, 8, 30)
    second = SicknessEpisode("second", again, again, serious_illness=True)
    year = YearTreatment(
        rules,
        second,
        (first,),
        SicknessWorker(),
        lambda i: next(
            (b.integration_rate for b in rules.day_bands if b.holds(i)),
            rules.full_pay_integration_rate,
        ),
    )
    treatment = year.day(1, again)
    assert (treatment.beyond_comporto, treatment.rate, treatment.carenza_rate) == (
        False,
        Decimal("0.7"),
        Decimal("0.7"),
    )
