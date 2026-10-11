"""Import direction between layers and capabilities of ``ccnl_engine``.

Layers import downwards only: ``api -> application -> service -> domain``,
and ``application`` may also import ``domain`` directly.  ``domain`` imports
only ``domain``, performs no I/O and reaches another capability's domain
only through :data:`DOMAIN_COUPLING`.  Only the package root imports ``api``,
and the capability layers form no import cycle.

Concepts import their own tier or a lower one (norms, computation,
orchestration); the roots of the layout by source are skipped until they
empty (:mod:`tests.integration.scripts.structure.support`).

Each rule is checked on the real sources and on a synthetic violation, so a
rule that silently stops detecting anything fails too.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.integration.scripts.structure.support import (
    legacy_coupling_violations,
    legacy_layer_graph,
    stale_legacy_coupling,
    stale_legacy_roots,
    stale_tier_entries,
    tier_violations,
    unknown_concepts,
)
from tests.integration.scripts.structure.support_imports import (
    Location,
    cycles,
    domain_coupling_violations,
    domain_io_violations,
    layer_graph,
    layer_violations,
    locate,
    parse_sources,
    read_package,
    runtime_imports,
    stale_allowlist_entries,
    unclassified,
)

if TYPE_CHECKING:
    from tests.integration.scripts.structure.support_imports import Module

_SRC = Path(str(importlib.resources.files("ccnl_engine"))).parent

#: Imports of another capability's domain from a domain layer, keyed by
#: ``(importing capability, imported module or package)``.  Each entry states
#: why the value type belongs to its owner and not to ``shared``.  Entries may
#: only be removed; an entry that no import uses fails the suite.
DOMAIN_COUPLING: dict[tuple[str, str], str] = {}


#: Imports of a higher tier, keyed by ``(importing concept, imported module
#: or package)``, each with the reason it cannot move yet.  Entries may only
#: be removed; an entry that no import uses fails the suite.
TIER_ALLOWLIST: dict[tuple[str, str], str] = {
    (
        "contribution",
        "ccnl_engine.capability.rule.services",
    ): (
        "INPS decisions cite the payable rules of the run, which the rule "
        "lookup of the capability report builds from every computation concept."
    ),
    (
        "seniority",
        "ccnl_engine.capability.rule.services",
    ): (
        "The seniority decision cites the payable rules of the run, which the "
        "rule lookup of the capability report builds."
    ),
}


@pytest.fixture(scope="module")
def package() -> dict[str, Module]:
    """Return the parsed ``ccnl_engine`` sources.

    Returns:
        The modules keyed by dotted name.
    """
    return read_package(_SRC)


def _modules(**sources: str) -> dict[str, Module]:
    """Parse synthetic sources keyed by dotted module name.

    A name ending in ``__init__`` is a package.

    Returns:
        The parsed modules keyed by dotted name.
    """
    return parse_sources({
        name.replace(".", "/") + ".py": source for name, source in sources.items()
    })


# ---------------------------------------------------------------------------
# Real sources
# ---------------------------------------------------------------------------


def test_every_module_fits_a_layer(package: dict[str, Module]) -> None:
    """Every module and every imported module maps to a known layer."""
    assert unclassified(package) == []


def test_layers_import_downwards(package: dict[str, Module]) -> None:
    """Runtime imports follow api -> application -> service -> domain."""
    assert layer_violations(package) == []


def test_domain_imports_other_domains_only_through_allowlist(
    package: dict[str, Module],
) -> None:
    """A legacy domain reaches another legacy domain only when allowlisted."""
    assert legacy_coupling_violations(package, DOMAIN_COUPLING) == []


def test_domain_coupling_allowlist_has_no_stale_entry(
    package: dict[str, Module],
) -> None:
    """Every allowlist entry is still used, so the list can only shrink."""
    assert stale_legacy_coupling(package, DOMAIN_COUPLING) == []


def test_domain_performs_no_io(package: dict[str, Module]) -> None:
    """Domain modules neither read files nor load bundled resources."""
    assert domain_io_violations(package) == []


def test_layers_form_no_cycle(package: dict[str, Module]) -> None:
    """The ``<capability>.<layer>`` import graph of the legacy roots is acyclic."""
    assert cycles(legacy_layer_graph(package)) == []


def test_analysis_sees_the_package(package: dict[str, Module]) -> None:
    """The analysis reads real modules and real imports, not an empty tree."""
    assert "ccnl_engine.api" in package
    targets = {imp.target for imp in runtime_imports(package)}
    assert "ccnl_engine.payroll.period.services" in targets


# ---------------------------------------------------------------------------
# Synthetic violations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("importer", "target"),
    [
        ("ccnl_engine.payroll.domain.x", "ccnl_engine.payroll.service.y"),
        ("ccnl_engine.payroll.domain.x", "ccnl_engine.payroll.application.y"),
        ("ccnl_engine.payroll.service.x", "ccnl_engine.payroll.application.y"),
        ("ccnl_engine.tax.service.x", "ccnl_engine.api"),
        ("ccnl_engine.payroll.application.x", "ccnl_engine.api"),
        ("ccnl_engine.api", "ccnl_engine.knowledge.loaders"),
        ("ccnl_engine.api", "ccnl_engine.payroll.domain.y"),
        ("ccnl_engine.payroll.domain.x", "ccnl_engine.knowledge"),
        ("ccnl_engine.payroll.__init__", "ccnl_engine.payroll.domain.y"),
    ],
)
def test_upward_import_is_rejected(importer: str, target: str) -> None:
    """An import against the layer direction is reported."""
    modules = _modules(**{importer: f"import {target}\n"})
    assert len(layer_violations(modules)) == 1


def test_downward_imports_are_accepted() -> None:
    """Imports along the layer direction are not reported."""
    modules = _modules(**{
        "ccnl_engine.__init__": "from ccnl_engine.api import Engine\n",
        "ccnl_engine.api": (
            "from ccnl_engine.payroll.application import run\n"
            "from ccnl_engine.knowledge import __version__\n"
        ),
        "ccnl_engine.payroll.application.run": (
            "from ccnl_engine.payroll.service import calc\n"
            "from ccnl_engine.payroll.domain import model\n"
        ),
        "ccnl_engine.payroll.service.calc": (
            "from ccnl_engine.knowledge.service import bundled\nfrom . import other\n"
        ),
        "ccnl_engine.payroll.service.other": "",
        "ccnl_engine.payroll.domain.model": (
            "from ccnl_engine.shared.domain import errors\n"
        ),
    })
    assert layer_violations(modules) == []
    assert unclassified(modules) == []


def test_type_checking_import_is_ignored_but_else_branch_counts() -> None:
    """Imports under TYPE_CHECKING do not run; its ``else`` branch does."""
    modules = _modules(**{
        "ccnl_engine.payroll.domain.x": (
            "import typing\n"
            "if typing.TYPE_CHECKING:\n"
            "    from ccnl_engine.payroll.service import a\n"
            "else:\n"
            "    from ccnl_engine.payroll.service import b\n"
        ),
    })
    expected = "ccnl_engine/payroll/domain/x.py:5 -> ccnl_engine.payroll.service"
    assert layer_violations(modules) == [f"{expected} (domain -> service)"]


def test_relative_and_lazy_imports_are_resolved() -> None:
    """Relative imports are made absolute and function-level imports count."""
    modules = _modules(**{
        "ccnl_engine.payroll.domain.__init__": "from ..service import calc\n",
        "ccnl_engine.payroll.domain.x": (
            "def f() -> None:\n    from ...tax.service import y\n"
        ),
        "ccnl_engine.payroll.service.calc": "",
    })
    package_import = "ccnl_engine/payroll/domain/__init__.py:1"
    lazy_import = "ccnl_engine/payroll/domain/x.py:2"
    assert layer_violations(modules) == [
        f"{package_import} -> ccnl_engine.payroll.service.calc (domain -> service)",
        f"{lazy_import} -> ccnl_engine.tax.service (domain -> service)",
    ]


@pytest.mark.parametrize(
    "name",
    ["ccnl_engine.payroll.misc", "ccnl_engine.payroll.misc.x"],
)
def test_module_outside_layers_is_unclassified(name: str) -> None:
    """A module outside any layer is reported, as is an import of it."""
    modules = _modules(**{
        name: "",
        "ccnl_engine.payroll.domain.x": f"import {name}\n",
    })
    assert len(unclassified(modules)) == 2
    assert layer_violations(modules) == []


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("ccnl_engine", Location("", "root")),
        ("ccnl_engine.inputs", Location("", "root")),
        ("ccnl_engine.catalog", Location("", "root")),
        ("ccnl_engine.version", Location("", "metadata")),
        ("ccnl_engine.api", Location("api", "api")),
        ("ccnl_engine.knowledge", Location("knowledge", "metadata")),
        ("ccnl_engine.knowledge.ccnl", Location("knowledge", "metadata")),
        ("ccnl_engine.knowledge.service.x", Location("knowledge", "service")),
        ("ccnl_engine.tax", Location("tax", "package")),
        ("ccnl_engine.tax.domain.a.b", Location("tax", "domain")),
    ],
)
def test_locate(name: str, expected: Location) -> None:
    """Module names map to their capability and layer."""
    assert locate(name) == expected


def test_foreign_domain_import_needs_allowlist_entry() -> None:
    """A domain importing another capability's domain must be allowlisted."""
    modules = _modules(**{
        "ccnl_engine.payroll.domain.x": (
            "from ccnl_engine.tax.domain.regime import Regime\n"
            "from ccnl_engine.errors import Error\n"
        ),
    })
    assert domain_coupling_violations(modules, {}) == [
        "ccnl_engine/payroll/domain/x.py:1 -> ccnl_engine.tax.domain.regime"
    ]
    allowlist = {("payroll", "ccnl_engine.tax.domain"): "reason"}
    assert domain_coupling_violations(modules, allowlist) == []
    wrong_owner = {("contract", "ccnl_engine.tax.domain"): "reason"}
    assert len(domain_coupling_violations(modules, wrong_owner)) == 1


def test_unused_allowlist_entry_is_stale() -> None:
    """An allowlist entry that no import uses is reported."""
    modules = _modules(**{
        "ccnl_engine.payroll.domain.x": "import ccnl_engine.tax.domain.a\n",
    })
    allowlist = {
        ("payroll", "ccnl_engine.tax.domain.a"): "used",
        ("payroll", "ccnl_engine.tax.domain.ab"): "prefix of nothing",
    }
    assert stale_allowlist_entries(modules, allowlist) == [
        ("payroll", "ccnl_engine.tax.domain.ab")
    ]


@pytest.mark.parametrize(
    "source",
    [
        "import importlib.resources\n",
        "from importlib import resources\n",
        "from importlib.resources import files\n",
        "import pathlib\n",
        "from pathlib import Path\n",
        "open('x')\n",
        "import json\njson.load(f)\n",
        "p.read_text()\n",
        "p.read_bytes()\n",
        "p.open()\n",
    ],
)
def test_domain_io_is_rejected(source: str) -> None:
    """Domain modules may not read files or bundled resources."""
    modules = _modules(**{"ccnl_engine.tax.domain.x": source})
    assert len(domain_io_violations(modules)) == 1


def test_io_outside_domain_and_pure_json_are_accepted() -> None:
    """Services may read files; ``json.dumps`` in domain is not I/O."""
    modules = _modules(**{
        "ccnl_engine.tax.service.x": "from pathlib import Path\nopen('x')\n",
        "ccnl_engine.tax.domain.y": (
            "import json\n"
            "from typing import TYPE_CHECKING\n"
            "if TYPE_CHECKING:\n"
            "    from pathlib import Path\n"
            "json.dumps({})\n"
            "json.loads('{}')\n"
            "Obligation.open(1)\n"
            "f()\n"
            "from . import z\n"
        ),
        "ccnl_engine.tax.domain.z": "",
    })
    assert domain_io_violations(modules) == []


def test_layer_cycle_is_detected() -> None:
    """Two services importing each other form a reported cycle."""
    modules = _modules(**{
        "ccnl_engine.contract.service.a": "import ccnl_engine.knowledge.service.b\n",
        "ccnl_engine.knowledge.service.b": "import ccnl_engine.contract.service.a\n",
        "ccnl_engine.contract.service.c": "import ccnl_engine.contract.service.a\n",
        "ccnl_engine.contract.domain.d": "import ccnl_engine.version\n",
    })
    assert cycles(layer_graph(modules)) == [["contract.service", "knowledge.service"]]


def test_acyclic_graph_has_no_cycle() -> None:
    """A diamond is not a cycle."""
    graph = {"a": {"b", "c"}, "b": {"d"}, "c": {"d"}, "d": set()}
    assert cycles(graph) == []


# ---------------------------------------------------------------------------
# Concept tiers
# ---------------------------------------------------------------------------


def test_every_root_has_a_tier_or_is_legacy(package: dict[str, Module]) -> None:
    """A new root of the package needs a tier before it holds modules."""
    assert unknown_concepts(package) == []


def test_legacy_roots_only_shrink(package: dict[str, Module]) -> None:
    """A legacy root that no module uses must leave the list."""
    assert stale_legacy_roots(package) == []


def test_concepts_import_their_tier_or_lower(package: dict[str, Module]) -> None:
    """No runtime import reaches a higher tier unless allowlisted."""
    assert tier_violations(package, TIER_ALLOWLIST) == []


def test_tier_allowlist_has_no_stale_entry(package: dict[str, Module]) -> None:
    """Every tier allowlist entry is still used, so the list only shrinks."""
    assert stale_tier_entries(package, TIER_ALLOWLIST) == []


def test_upward_tier_import_is_reported_and_allowlistable() -> None:
    """Computation importing orchestration is reported until allowlisted."""
    modules = _modules(**{
        "ccnl_engine.sickness.services": (
            "from ccnl_engine.period.services import shared\n"
            "from ccnl_engine.provenance.source import models\n"
            "from ccnl_engine.sickness.day import rules\n"
            "from ccnl_engine.payroll.period import services\n"
        ),
        "ccnl_engine.period.services": "from ccnl_engine.sickness import services\n",
        "ccnl_engine.contribution.rules": "import ccnl_engine\n",
    })
    assert tier_violations(modules, {}) == [
        (
            "ccnl_engine/sickness/services.py:1 -> ccnl_engine.period.services "
            "(sickness computation -> period orchestration)"
        )
    ]
    allowlist = {("sickness", "ccnl_engine.period"): "shared helpers move down"}
    assert tier_violations(modules, allowlist) == []
    assert stale_tier_entries(modules, allowlist) == []
    unused = {("sickness", "ccnl_engine.year"): "nothing imports it"}
    assert stale_tier_entries(modules, unused) == [("sickness", "ccnl_engine.year")]


def test_roots_without_tier_and_stale_legacy_are_reported() -> None:
    """An unknown root is reported; a legacy root without modules is stale."""
    modules = _modules(**{
        "ccnl_engine.__init__": "",
        "ccnl_engine.misc.models": "",
        "ccnl_engine.payroll.misc.models": "",
    })
    assert unknown_concepts(modules) == ["misc"]
    assert stale_legacy_roots(modules) == ["tax"]
