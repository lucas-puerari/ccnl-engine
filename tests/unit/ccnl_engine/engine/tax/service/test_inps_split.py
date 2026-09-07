"""Data-integrity tests for the tax/INPS file split.

Each ``<year>-<sector>.json`` pair in ``knowledge/tax/data`` and
``knowledge/inps/data`` must merge back into exactly the payload the engine's
``YearRulesRaw`` schema expects, so the split is lossless with respect to the
pre-split tax files.
"""

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.tax.domain.rules import YearRulesRaw
from ccnl_engine.engine.tax.service.loaders import (
    load_year_rules,
    read_inps_rules_raw,
    read_tax_rules_raw,
)

_TAX_ONLY = {
    "irpef_brackets",
    "work_deduction_breakpoints",
    "fixed_term_additional_rate",
    "tfr",
    "trattamento_integrativo",
    "notes",
}
_CONTRIB_KEYS = {"inps", "apprentice", "domestic_contributions"}
_SHARED = {"year", "sector"}


class TestTaxInpsSplit:
    """The tax/INPS split must be lossless across every bundled sector."""

    def test_all_sectors_have_data_pair(self) -> None:
        """Every TaxSector has a 2026 tax + inps data file."""
        for sector in TaxSector:
            read_tax_rules_raw(2026, sector)
            read_inps_rules_raw(2026, sector)

    def test_tax_files_have_no_contribution_keys(self) -> None:
        """Tax files carry only IRPEF/TFR keys, never the contribution block."""
        for sector in TaxSector:
            tax = read_tax_rules_raw(2026, sector)
            assert not _CONTRIB_KEYS & set(tax), sector

    def test_inps_files_have_no_tax_keys(self) -> None:
        """INPS files carry only the contribution block, never IRPEF/TFR."""
        for sector in TaxSector:
            inps = read_inps_rules_raw(2026, sector)
            assert not _TAX_ONLY & set(inps), sector

    def test_only_shared_keys_overlap(self) -> None:
        """Tax and INPS files share only year/sector."""
        for sector in TaxSector:
            tax = read_tax_rules_raw(2026, sector)
            inps = read_inps_rules_raw(2026, sector)
            assert set(tax) & set(inps) == _SHARED, sector

    def test_standard_sector_merged_validates(self) -> None:
        """Standard sectors merge into a valid YearRulesRaw with inps+apprentice."""
        for sector in TaxSector:
            if sector is TaxSector.LAVORO_DOMESTICO:
                continue
            inps = read_inps_rules_raw(2026, sector)
            assert {"inps", "apprentice"} <= set(inps), sector
            raw = YearRulesRaw.model_validate({
                **read_tax_rules_raw(2026, sector),
                **inps,
            })
            assert raw.sector is sector
            assert raw.inps is not None
            assert raw.apprentice is not None

    def test_domestic_sector_merged_validates(self) -> None:
        """Lavoro domestico merges with only domestic_contributions."""
        sector = TaxSector.LAVORO_DOMESTICO
        inps = read_inps_rules_raw(2026, sector)
        assert set(inps) == _SHARED | {"domestic_contributions"}
        raw = YearRulesRaw.model_validate({**read_tax_rules_raw(2026, sector), **inps})
        assert raw.inps is None
        assert raw.apprentice is None
        assert raw.domestic_contributions is not None

    def test_load_year_rules_all_sectors(self) -> None:
        """load_year_rules resolves every sector end-to-end."""
        for sector in TaxSector:
            yr = load_year_rules(2026, sector, num_employees=50)
            assert yr.year == 2026
