"""Load every resource of the knowledge manifest through its typed loader.

Each dataset has its own tests; this one walks the manifest once and reads
every resource the way the engine does, so a file that no longer validates
against its model, or a dataset added without a loader, fails here.  The
ruleset hash of each file is checked by the loaders on the way.
"""

from __future__ import annotations

import json
from operator import itemgetter
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.capability.loaders import load_capability_catalog
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.family.loaders import load_family_deduction_rules
from ccnl_engine.limitation.loaders import load_engine_limitations
from ccnl_engine.pay_item.loaders import load_policy_resolver
from ccnl_engine.sector.loaders import load_year_rules
from ccnl_engine.severance.loaders import load_tfr_revaluation_rules
from ccnl_engine.sickness.indemnity.loaders import load_sick_pay_rates
from ccnl_engine.surtax.loaders import load_surtax_rules
from ccnl_engine.tax_credit.somma_esente.loaders import load_somma_esente_rules
from ccnl_engine.variable_pay.loaders import load_variable_pay_rules
from scripts.provenance.rules import KNOWLEDGE_DIR

if TYPE_CHECKING:
    from collections.abc import Callable

_RESOURCES: list[dict[str, Any]] = json.loads(
    (KNOWLEDGE_DIR / "manifest.json").read_text(encoding="utf-8")
)["resources"]
#: Headcount of the load: every INPS tier list resolves at any size.
_HEADCOUNT = 10


def _year_rules(resource: dict[str, Any]) -> object:
    return load_year_rules(resource["year"], TaxSector(resource["scope"]), _HEADCOUNT)


_LOADERS: dict[str, Callable[[dict[str, Any]], object]] = {
    "agreement": lambda r: load_ccnl(f"{r['scope']}.json"),
    "capability/registry": lambda r: load_capability_catalog(r["year"]),
    "contribution": _year_rules,
    "family": lambda r: load_family_deduction_rules(r["year"]),
    "limitation": lambda _: load_engine_limitations(),
    "pay_item": lambda _: load_policy_resolver(),
    "sector": _year_rules,
    "severance/revaluation": lambda r: load_tfr_revaluation_rules(r["year"]),
    "sickness/indemnity": lambda _: load_sick_pay_rates(),
    "surtax/municipal": lambda r: load_surtax_rules(r["year"]),
    "surtax/regional": lambda r: load_surtax_rules(r["year"]),
    "tax_credit/somma_esente": lambda r: load_somma_esente_rules(r["year"]),
    "variable_pay": lambda r: load_variable_pay_rules(r["year"]),
}


def test_every_dataset_has_a_loader() -> None:
    """A dataset added to the manifest must be added here with its loader."""
    assert {r["dataset"] for r in _RESOURCES} == set(_LOADERS)


@pytest.mark.parametrize("resource", _RESOURCES, ids=itemgetter("path"))
def test_every_resource_loads_through_its_loader(resource: dict[str, Any]) -> None:
    """The typed loader of the dataset reads and validates the resource."""
    assert _LOADERS[resource["dataset"]](resource) is not None
