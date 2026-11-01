"""The overtime tables of the Alimentari, by sub-sector and category (Art. 31).

FLAI text of the CCNL 2023-2027, PDF pp. 87-90 (sha256
11792ad3df71999684bae85fea8aaf1e3d492d477043eecc78545b5f41db842c): the
day, weekday night and holiday overtime above 40 hours of each table,
the operai column apart from the impiegati one.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.working_time.models import WorkKind
from ccnl_engine.working_time.subsector.rules import with_subsector

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.working_time.models import OvertimeBand

_OPERAIO, _IMPIEGATO = WorkerCategory.OPERAIO, WorkerCategory.IMPIEGATO
_CCNL = load_ccnl("alimentari-federalimentare")


def _rates(subsector: str, category: WorkerCategory) -> dict[WorkKind, Decimal]:
    ccnl, unknown = with_subsector(_CCNL, subsector, category)
    assert not unknown
    assert ccnl.work_rules is not None
    supplements = ccnl.work_rules.time_supplements
    assert supplements is not None
    found: dict[WorkKind, Decimal] = {}
    for band in supplements.overtime_bands:
        value = band.rate.periods[-1].value
        assert value is not None
        for kind in band.applies_to_kinds:
            assert kind not in found, band.code
            found[kind] = value
    return found


@pytest.mark.parametrize(
    ("subsector", "category", "day", "night", "holiday"),
    [
        ("carni", _OPERAIO, "0.45", "0.50", "0.60"),
        ("carni", _IMPIEGATO, "0.45", "0.50", "0.60"),
        ("vini_liquori", _OPERAIO, "0.45", "0.50", "0.60"),
        ("vini_liquori", _IMPIEGATO, "0.45", "0.70", "0.90"),
        ("bevande_gassate", _OPERAIO, "0.45", "0.40", "0.45"),
        ("molitoria_pastificazione", _IMPIEGATO, "0.45", "0.65", "0.90"),
        ("conserve_ittiche", _OPERAIO, "0.45", "0.45", "0.50"),
        ("avicoli", _IMPIEGATO, "0.45", "0.65", "0.90"),
    ],
)
def test_the_rates_of_the_table_and_column(
    subsector: str, category: WorkerCategory, day: str, night: str, holiday: str
) -> None:
    """One rate a kind: rows 1, 6 (or the night overtime row) and 3."""
    assert _rates(subsector, category) == {
        WorkKind.WEEKDAY: Decimal(day),
        WorkKind.NIGHT: Decimal(night),
        WorkKind.HOLIDAY: Decimal(holiday),
    }


def test_a_dash_leaves_the_rate_to_the_caller() -> None:
    """Distillatori: no night overtime for the impiegati ('-')."""
    assert WorkKind.NIGHT not in _rates("distillatori", _IMPIEGATO)


def test_an_unstated_sub_sector_is_priced_with_the_first_table() -> None:
    """The bands of carni, the first table, are kept; the fact is missing."""
    ccnl, unknown = with_subsector(_CCNL, None, _OPERAIO)

    assert unknown
    assert ccnl.work_rules is not None
    assert ccnl.work_rules.time_supplements is not None
    bands = ccnl.work_rules.time_supplements.overtime_bands
    assert {b.code for b in bands} == {"OT_DIURNO", "OT_NOTTURNO", "OT_FESTIVO"}


def test_a_sub_sector_of_another_ccnl_is_refused() -> None:
    """Only the codes the bands name are accepted."""
    with pytest.raises(InvalidInputError, match=r"EmployerProfile\.subsector"):
        with_subsector(_CCNL, "tessile", _OPERAIO)


def test_a_ccnl_without_sub_sectors_is_unchanged() -> None:
    """Commercio names none: the CCNL comes back as it is."""
    commercio = load_ccnl("commercio-confcommercio")
    assert with_subsector(commercio, None, _IMPIEGATO) == (commercio, False)


def test_a_table_by_category_needs_the_category() -> None:
    """Vini-liquori pays operai and impiegati apart."""
    with pytest.raises(InvalidInputError, match=r"Employment\.category"):
        with_subsector(_CCNL, "vini_liquori", None)


def _with_bands(*bands: OvertimeBand) -> CCNL:
    rules = _CCNL.work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    supplements = rules.time_supplements.model_copy(update={"overtime_bands": bands})
    work = rules.model_copy(update={"time_supplements": supplements})
    return _CCNL.model_copy(update={"work_rules": work})


def _band(code: str, **update: object) -> OvertimeBand:
    rules = _CCNL.work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    (first, *_) = rules.time_supplements.overtime_bands
    return first.model_copy(update={"code": code, **update})


def test_bands_by_category_alone_need_no_sub_sector() -> None:
    """Categories without sub-sectors: the category decides, nothing missing."""
    ccnl = _with_bands(
        _band("OT_O", subsectors=(), categories=(_OPERAIO,)),
        _band("OT_I", subsectors=(), categories=(_IMPIEGATO,)),
    )
    kept, unknown = with_subsector(ccnl, None, _IMPIEGATO)

    assert not unknown
    assert kept.work_rules is not None
    assert kept.work_rules.time_supplements is not None
    assert [b.code for b in kept.work_rules.time_supplements.overtime_bands] == ["OT_I"]


def test_the_first_sub_sector_named_prices_an_unstated_one() -> None:
    """The first code of the first band, not a later one of the same band."""
    ccnl = _with_bands(
        _band("OT_A", subsectors=("alfa", "beta")),
        _band("OT_B", subsectors=("beta",), applies_to_kinds=(WorkKind.NIGHT,)),
    )
    kept, unknown = with_subsector(ccnl, None, _OPERAIO)

    assert unknown
    assert kept.work_rules is not None
    assert kept.work_rules.time_supplements is not None
    assert [b.code for b in kept.work_rules.time_supplements.overtime_bands] == ["OT_A"]


@pytest.mark.parametrize(
    ("subsector", "category", "field", "feature"),
    [
        ("tessile", _OPERAIO, "EmployerProfile.subsector", "employer_facts"),
        ("vini_liquori", None, "Employment.category", "overtime"),
    ],
)
def test_the_errors_name_their_field(
    subsector: str, category: WorkerCategory | None, field: str, feature: str
) -> None:
    """The input error points at the field to state."""
    with pytest.raises(InvalidInputError) as raised:
        with_subsector(_CCNL, subsector, category)

    assert (raised.value.field, raised.value.feature) == (field, feature)
