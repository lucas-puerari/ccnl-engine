"""The payable rules each capability of a run reads, for every contract kind."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.assurance.rule_source.services import run_rule_sources
from ccnl_engine.capability.rule.services import (
    LOADED,
    contract_rules,
    tax_rules,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.proration.services import FULL_MONTH
from ccnl_engine.employment.inputs import Apprentice, FixedTerm, Permanent
from ccnl_engine.period.repositories import (
    BundledKnowledgeRepository,
)
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance
from ccnl_engine.sector.loaders import load_year_rules
from ccnl_engine.variable_pay.loaders import load_variable_pay_rules

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.surtax.models import SurtaxRules

_YEAR = 2026
_CCNL = load_ccnl("metalmeccanico-federmeccanica.json")
_REPO = BundledKnowledgeRepository()


class _NoSurtax(BundledKnowledgeRepository):
    def load_surtax_rules(self, year: int) -> SurtaxRules | None:  # type: ignore[override]
        return None


def _ctx(
    *,
    contract: object = None,
    sector: TaxSector = TaxSector.INDUSTRIA,
    competence: date = date(_YEAR, 3, 1),
    repo: BundledKnowledgeRepository = _REPO,
    regione: str | None = None,
    comune: str | None = None,
) -> RunContext:
    level = _CCNL.level_by_code("C3")
    fake = SimpleNamespace(
        contract=SimpleNamespace(
            ccnl=_CCNL,
            level=level,
            tctx=SimpleNamespace(competence=competence),
            year_rules=load_year_rules(_YEAR, sector, 50),
        ),
        chain=SimpleNamespace(allowances=((a, None) for a in level.fixed_allowances)),
        request=SimpleNamespace(
            contract_type=contract or Permanent(),
            regione=regione,
            comune_belfiore=comune,
        ),
        accrual=None,
        settlements=(),
        proration=FULL_MONTH,
        var_pay_rules=load_variable_pay_rules(_YEAR),
        repo=repo,
        fiscal_year=_YEAR,
    )
    return cast("RunContext", fake)


def _names(rules: tuple[tuple[str, object], ...]) -> list[str]:
    return [name.split(":", 1)[1] for name, _ in rules]


def test_permanent_worker_reads_ordinary_rates() -> None:
    """A permanent worker reads the ordinary INPS block and its minimum base."""
    rules = contract_rules(_ctx())
    assert _names(rules["inps_employer"]) == [
        "inps",
        "domestic_contributions",
        "inps.minimum_base",
    ]
    assert rules["inps_employer"][1][1] is None
    assert isinstance(rules["inps_employer"][2][1], RuleProvenance)


def test_fixed_term_employer_reads_the_addizionale() -> None:
    """The fixed-term addizionale feeds the employer contributions only."""
    rules = contract_rules(_ctx(contract=FixedTerm()))
    assert _names(rules["inps_employer"])[-1] == "fixed_term_additional_rate"
    assert "fixed_term_additional_rate" not in _names(rules["inps_employee"])


def test_apprentice_reads_the_apprentice_rates() -> None:
    """An apprentice reads the apprentice block instead of the ordinary one."""
    rules = contract_rules(_ctx(contract=Apprentice(months_elapsed=3)))
    assert _names(rules["inps_employee"])[0] == "apprentice"


def test_domestic_sector_reads_the_flat_contributions() -> None:
    """A domestic sector has no ordinary rates nor minimum base, but flat rates."""
    (ordinary, domestic, minimum) = contract_rules(
        _ctx(sector=TaxSector.LAVORO_DOMESTICO)
    )["inps_employee"]
    assert ordinary[1] is None
    assert minimum[1] is None
    assert isinstance(domestic[1], RuleProvenance)


def test_salary_rules_before_the_series_start_are_empty() -> None:
    """No salary period is in force before the first tranche."""
    rules = contract_rules(_ctx(competence=date(1900, 1, 1)))
    assert all("base_salary" not in name for name in _names(rules["base_salary"]))


def test_salary_rules_name_the_period_in_force() -> None:
    """The base salary rule names the tranche of the competence date."""
    rules = contract_rules(_ctx())
    names = _names(rules["base_salary"])
    assert names[0].startswith("levels[C3].base_salary[")
    assert names[-1].startswith("additional_months[")


def test_regimes_report_their_source_status() -> None:
    """A substitute-tax regime reports the status of its cited source."""
    rules = tax_rules(_ctx())
    ((_, status),) = rules["rinnovo_substitute_tax"]
    assert status is ProvenanceStatus.DERIVED


def test_surtax_rules_follow_the_jurisdiction() -> None:
    """Regional and municipal rules name the table entry of the worker."""
    ctx = _ctx(regione="IT-45", comune="F257")
    ((regional, _),) = LOADED["addizionale_regionale"](ctx)
    ((municipal, record),) = LOADED["addizionale_comunale"](ctx)
    assert regional.endswith(":rates[Emilia-Romagna]")
    assert municipal.endswith(":rates[F257]")
    assert isinstance(record, RuleProvenance)


def test_surtax_rules_are_empty_without_tables() -> None:
    """A repository without surtax tables yields no surtax rule."""
    assert LOADED["addizionale_regionale"](_ctx(repo=_NoSurtax())) == ()


def test_only_executed_capabilities_are_reported() -> None:
    """Without decisions only the core stages report their rules."""
    capabilities = {
        source.capability for source in run_rule_sources(_ctx(), (), frozenset())
    }
    assert capabilities == {
        "base_salary",
        "inps_employee",
        "inps_employer",
        "tfr",
        "irpef",
    }


def _regime_ctx(sector: TaxSector) -> RunContext:
    """Build a run of the CCNL with its workers in the pubblici esercizi regime.

    Returns:
        The context of the run.
    """
    ctx = _ctx(sector=sector)
    assert _CCNL.work_rules is not None
    assert _CCNL.work_rules.sickness_rules is not None
    sickness = _CCNL.work_rules.sickness_rules.model_copy(
        update={"inps_regime": "pubblici_esercizi"}
    )
    work = _CCNL.work_rules.model_copy(update={"sickness_rules": sickness})
    ctx.contract.ccnl = _CCNL.model_copy(update={"work_rules": work})  # type: ignore[misc]
    return ctx


def test_a_regime_adds_its_supplement_to_the_employer_rules() -> None:
    """The terziario table holds the 0.77% of the pubblici esercizi."""
    rules = contract_rules(_regime_ctx(TaxSector.TERZIARIO))["inps_employer"]
    name, record = rules[-1]
    assert name.endswith(":inps.sick_pay_supplements[pubblici_esercizi]")
    assert isinstance(record, RuleProvenance)
    assert record.status is ProvenanceStatus.DERIVED


def test_a_regime_without_a_supplement_reads_no_record() -> None:
    """Industria holds none: the rule is named with no record."""
    rules = contract_rules(_regime_ctx(TaxSector.INDUSTRIA))["inps_employer"]
    name, record = rules[-1]
    assert name.endswith(":inps.sick_pay_supplements[pubblici_esercizi]")
    assert record is None


def test_no_regime_reads_no_supplement() -> None:
    """A CCNL that names no regime adds nothing to the employer rules."""
    names = _names(contract_rules(_ctx())["inps_employer"])
    assert not any("sick_pay_supplements" in name for name in names)
