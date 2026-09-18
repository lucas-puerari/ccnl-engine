"""Loader for pre-built payroll knowledge bundles."""

from __future__ import annotations

from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle, make_bundle
from ccnl_engine.engine.surtax.service.loaders import load_surtax_rules
from ccnl_engine.engine.tax.service.loaders import load_year_rules


def load_payroll_bundle(
    ccnl_id: str,
    year: int,
    *,
    num_employees: int,
    load_surtax: bool = False,
) -> PayrollBundle:
    """Load a frozen payroll knowledge bundle for a given CCNL and tax year.

    Loads the CCNL, tax/INPS and (when ``load_surtax`` is ``True``) surtax
    rules for the given year and wraps them in an immutable
    :class:`~ccnl_engine.engine.payroll.domain.bundle.PayrollBundle` with a
    deterministic content hash.

    The individual loaders are cached, so repeated calls with the same
    arguments are cheap.  The returned bundle can be passed to
    :func:`~ccnl_engine.engine.payroll.service.orchestrator.compute` to skip
    rule loading inside the computation loop.

    Args:
        ccnl_id: Filename of the CCNL JSON bundled under
            ``ccnl_engine/knowledge/ccnl/data/``
            (e.g. ``"metalmeccanico-federmeccanica.json"``).
        year: Tax year for which to load rules.
        num_employees: Employer headcount; selects the INPS contribution tier.
        load_surtax: When ``True``, loads regional/municipal surtax rates for
            ``year``.  Set to ``True`` whenever any scenario in the run
            provides a jurisdiction.

    Returns:
        An immutable :class:`~ccnl_engine.engine.payroll.domain.bundle\
.PayrollBundle` with ``bundle_hash`` reflecting the exact data files loaded.
    """
    ccnl = load_ccnl(ccnl_id)
    rules = load_year_rules(year, ccnl.meta.tax_sector, num_employees)
    surtax = load_surtax_rules(year) if load_surtax else None
    return make_bundle(ccnl, rules, surtax)
