"""CCNL data files of the bundle: load, list, search and resolve the contracts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING, Any, NewType

from ccnl_engine.agreement.facade import CCNL
from ccnl_engine.agreement.validity.models import (
    ValidityWindow,
    model_window,
)
from ccnl_engine.bundle.loaders import read_resource, resources
from ccnl_engine.bundle.validators import (
    verify_provenance_labels,
    verify_ruleset_hash,
)
from ccnl_engine.errors import UnknownCcnlError
from ccnl_engine.surtax.jurisdiction.types import REGION_CODES
from ccnl_engine.surtax.loaders import load_surtax_rules
from ccnl_engine.validators import require_str

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.provenance.ruleset.models import RulesetReadiness
    from ccnl_engine.provenance.source.models import SourceDocument


#: Dataset of the CCNL files in the knowledge manifest.
AGREEMENTS = "agreement"

#: Shape of a CCNL slug: lower-case letters, digits and hyphens.
SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")


@cache
def load_ccnl(ccnl_id: str) -> CCNL:
    """Load and validate the CCNL with slug *ccnl_id* from the package bundle.

    The returned :class:`CCNL` instance is shared across all callers in the
    same process (the result is cached after the first load).  All models in
    the CCNL hierarchy are frozen (``model_config frozen=True``), list fields
    use immutable tuples and dict fields are wrapped in
    ``types.MappingProxyType``, making the entire object graph transitively
    read-only.  Callers must not attempt to modify the returned object.

    Args:
        ccnl_id: Slug of a bundled CCNL
            (e.g. ``"metalmeccanico-federmeccanica"``).

    Returns:
        The validated, immutable CCNL instance.

    Raises:
        UnknownCcnlError: When *ccnl_id* is not a slug the bundle holds.
    """
    require_str(ccnl_id, "ccnl_id", feature="catalog")
    if not SLUG.fullmatch(ccnl_id):
        raise UnknownCcnlError(ccnl_id)
    filename = f"{ccnl_id}.json"
    try:
        raw = read_resource(f"{AGREEMENTS}/{filename}")
    except FileNotFoundError:
        raise UnknownCcnlError(ccnl_id) from None
    payload = json.loads(raw)
    _verify_payload(payload, filename)
    return CCNL.model_validate(payload)


def _verify_payload(payload: dict[str, Any], filename: str) -> None:
    """Verify the ``ruleset.source_hash`` and the provenance labels.

    Delegates to :func:`~ccnl_engine.bundle.validators.verify_ruleset_hash` and
    :func:`~ccnl_engine.bundle.validators.verify_provenance_labels`.
    """
    verify_ruleset_hash(payload, filename)
    verify_provenance_labels(payload, filename)


CcnlId = NewType("CcnlId", str)


@dataclass(frozen=True, slots=True)
class ContractSummary:
    """Summary of one bundled CCNL: who it is and how far it is cleared.

    Attributes:
        ccnl_id: Human-readable slug
            (e.g. ``"metalmeccanico-federmeccanica"``).
        name: Full display name
            (e.g. ``"CCNL Metalmeccanico Federmeccanica"``).
        cnel_code: Official CNEL classification code (e.g. ``"E042"``).
        readiness: Readiness tier of the CCNL ruleset; only ``production``
            is payable in ``operational`` mode.
        validity: Dates on which every rule of the CCNL has a value in the
            bundle (pay tables, parameters, work rules), both ends included.
            A run inside it never raises
            :class:`~ccnl_engine.errors.MissingRuleError`; a
            run outside it raises that error when it reads a rule not in
            force on its date, and a competence year skips the runs before
            the base salary of the level starts.  ``None`` when no date
            covers every rule.
        withholding_agent: Whether the employer of the CCNL withholds
            IRPEF as sostituto d'imposta (``False`` for domestic work).
        sources: The documents the CCNL file cites, in its order.
    """

    ccnl_id: CcnlId
    name: str
    cnel_code: str
    readiness: RulesetReadiness
    validity: ValidityWindow | None
    withholding_agent: bool = True
    sources: tuple[SourceDocument, ...] = ()


@dataclass(frozen=True, slots=True)
class LevelSummary:
    """One level of a bundled CCNL, as ``Employment.level_code`` names it.

    Attributes:
        code: The level code (e.g. ``"C3"``).
        description: Label of the level in the CCNL data.
        category: Worker category the level is restricted to, ``None``
            when the level admits any.
        apprenticeship_tracks: Names of the apprenticeship tracks that lead
            to the level, the ``Apprentice.track`` a run may state.
    """

    code: str
    description: str
    category: WorkerCategory | None
    apprenticeship_tracks: tuple[str, ...] = ()


def contract_summary(ccnl: CCNL) -> ContractSummary:
    """Return the summary of *ccnl*: identity, readiness and validity.

    Args:
        ccnl: A validated CCNL, from the bundle or another repository.

    Returns:
        The :class:`ContractSummary` of *ccnl*.
    """
    meta = ccnl.meta
    return ContractSummary(
        ccnl_id=CcnlId(meta.ccnl_id),
        name=meta.name,
        cnel_code=meta.cnel_code,
        readiness=ccnl.verification.readiness,
        validity=model_window(ccnl),
        withholding_agent=meta.withholding_agent,
        sources=tuple(meta.sources),
    )


@cache
def _load_all() -> tuple[ContractSummary, ...]:
    """Load the summary of every bundled CCNL file (result is cached).

    Returns:
        Tuple of :class:`ContractSummary` sorted by ccnl_id.
    """
    items = (
        contract_summary(load_ccnl(resource.name.removesuffix(".json")))
        for resource in resources(AGREEMENTS)
    )
    return tuple(sorted(items, key=lambda item: item.ccnl_id))


def list_contracts() -> tuple[ContractSummary, ...]:
    """Return every bundled CCNL contract, sorted by ccnl_id.

    Returns:
        Tuple of :class:`ContractSummary` for every bundled CCNL.
    """
    return _load_all()


def resolve_contract(
    contracts: Iterable[ContractSummary], ccnl_id: str
) -> ContractSummary:
    """Resolve a CCNL among *contracts* by slug or CNEL code.

    Args:
        contracts: The contracts to search, e.g. those of a repository.
        ccnl_id: A slug (e.g. ``"metalmeccanico-federmeccanica"``) or CNEL
            code (e.g. ``"E042"``).

    Returns:
        The matching :class:`ContractSummary`.

    Raises:
        UnknownCcnlError: When no CCNL matches *ccnl_id*, with up to five
            similar identifiers attached as suggestions, or when *ccnl_id*
            is a CNEL code shared by several CCNLs, with their slugs as
            suggestions: a shared code does not name one contract.
    """
    require_str(ccnl_id, "ccnl_id", feature="catalog")
    candidates = tuple(contracts)
    for info in candidates:
        if ccnl_id == info.ccnl_id:
            return info
    coded = tuple(info for info in candidates if ccnl_id == info.cnel_code)
    if len(coded) == 1:
        return coded[0]
    if coded:
        raise UnknownCcnlError(ccnl_id, tuple(info.ccnl_id for info in coded))
    query = ccnl_id.lower()
    suggestions = tuple(
        info.ccnl_id
        for info in candidates
        if query in info.ccnl_id.lower() or query in info.name.lower()
    )[:5]
    raise UnknownCcnlError(ccnl_id, suggestions)


def get_ccnl(ccnl_id: str) -> ContractSummary:
    """Resolve a bundled CCNL by slug or CNEL code.

    See :func:`resolve_contract`.

    Args:
        ccnl_id: A slug (e.g. ``"metalmeccanico-federmeccanica"``) or CNEL
            code (e.g. ``"E042"``).

    Returns:
        The matching :class:`ContractSummary`.
    """
    return resolve_contract(_load_all(), ccnl_id)


def search_ccnls(query: str) -> tuple[ContractSummary, ...]:
    """Return all CCNLs whose name or slug contains *query*.

    The comparison is case-insensitive.

    Args:
        query: Substring to match against :attr:`ContractSummary.ccnl_id` and
            :attr:`ContractSummary.name`.

    Returns:
        A tuple of matching :class:`ContractSummary`, in slug order.
    """
    require_str(query, "query", feature="catalog")
    q = query.lower()
    return tuple(
        info
        for info in _load_all()
        if q in info.ccnl_id.lower() or q in info.name.lower()
    )


@dataclass(frozen=True, slots=True)
class Jurisdiction:
    """A region or a comune a run can name, as the surtax tables hold it.

    Attributes:
        code: The code a run states: ``PeriodFacts.regione`` (``IT-25``) or
            ``PeriodFacts.comune_belfiore`` (``F205``).
        name: Its name.
    """

    code: str
    name: str


def regions(year: int) -> tuple[Jurisdiction, ...]:
    """Return the regions with a regional surtax table for ``year``.

    Returns:
        One per region, ordered by name.
    """
    tables = load_surtax_rules(year).regionale
    found = (Jurisdiction(c, n) for c, n in REGION_CODES.items() if n in tables)
    return tuple(sorted(found, key=lambda j: j.name))


def municipalities(year: int) -> tuple[Jurisdiction, ...]:
    """Return the comuni with a municipal surtax rate for ``year``.

    Returns:
        One per comune, ordered by name.
    """
    rows = load_surtax_rules(year).comunale.items()
    found = (Jurisdiction(code, row.nome) for code, row in rows)
    return tuple(sorted(found, key=lambda j: j.name))
