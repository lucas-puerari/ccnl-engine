"""Every bundled payable fiscal block reaches its loaded model with a record."""

from __future__ import annotations

import pytest

from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.tax.annual.loaders import load_year_rules
from ccnl_engine.tax.annual.loaders_optional import (
    load_family_deduction_rules,
    load_variable_pay_rules,
)
from ccnl_engine.tax.surtax.loaders import load_surtax_rules

_YEAR = 2026


@pytest.mark.parametrize("sector", list(TaxSector))
@pytest.mark.parametrize("headcount", [5, 100])
def test_year_rules_carry_every_block_record(sector: TaxSector, headcount: int) -> None:
    """Tax and INPS blocks keep their record once the tiers are resolved."""
    rules = load_year_rules(_YEAR, sector, headcount)
    records = [
        rules.irpef_brackets_provenance,
        rules.fixed_term_additional_rate_provenance,
        rules.work_deduction.provenance,
        rules.tfr.provenance,
    ]
    records.extend(
        block.provenance
        for block in (
            rules.trattamento_integrativo,
            rules.ulteriore_detrazione,
            rules.somma_esente,
            rules.sterilizzazione_detrazioni,
            rules.inps,
            rules.apprentice,
            rules.domestic_contributions,
        )
        if block is not None
    )
    assert all(record is not None for record in records)


def test_surtax_tables_carry_their_record() -> None:
    """Both surtax tables carry a table-level record."""
    surtax = load_surtax_rules(_YEAR)
    assert surtax.regional_provenance is not None
    assert surtax.municipal_provenance is not None


def test_family_and_variable_pay_blocks_carry_their_record() -> None:
    """Loaders built field by field keep the record of each block."""
    family = load_family_deduction_rules(_YEAR)
    variable = load_variable_pay_rules(_YEAR)
    assert family.spouse.provenance is not None
    assert family.children.provenance is not None
    assert family.other_dependents.provenance is not None
    assert variable.fringe_benefit.provenance is not None
    assert variable.pdr.provenance is not None
