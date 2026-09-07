"""Fail-hard source_hash verification across the knowledge-base loaders.

Every loader must raise ``ValueError`` when a bundled data file's recorded
``ruleset.source_hash`` does not match the hash recomputed over the payload
(a file edited without updating its provenance block). Files without a
``ruleset`` block — or with a malformed one — must still load untouched.
"""

import copy
import importlib
import importlib.resources
import json
from typing import Any, cast

import pytest

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.contract.service import loaders as contract_loaders
from ccnl_engine.engine.contract.service.loaders import (
    _verify_ruleset_hash as _verify_contract_hash,
)
from ccnl_engine.engine.contract.service.loaders import (
    load_ccnl as load_ccnl_from_bundle,
)
from ccnl_engine.engine.surtax.service import loaders as surtax_loaders
from ccnl_engine.engine.tax.service import loaders as tax_loaders
from tests.helpers import make_ccnl_dict

LOADER_PATHS = (
    "ccnl_engine.engine.contract.service.loaders",
    "ccnl_engine.engine.tax.service.loaders",
    "ccnl_engine.engine.surtax.service.loaders",
)


def _load_bundled_text(pkg_name: str, filename: str) -> str:
    pkg = importlib.resources.files(pkg_name)
    return pkg.joinpath(filename).read_text(encoding="utf-8")


def _tamper(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-copied payload with a hidden data modification.

    Returns:
        A copy of *payload* with the first level's base salary rewritten.
    """
    tampered = copy.deepcopy(payload)
    tampered["levels"][0]["base_salary"]["periods"][0]["value"] = "999.99"
    return tampered


class TestContractLoaderIntegrity:
    """load_ccnl rejects stale source_hash, passes valid/missing blocks."""

    def _repatch(self, monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
        monkeypatch.setattr(
            contract_loaders,
            "read_bundled",
            lambda pkg, filename: raw,
        )

    def test_tampered_payload_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A data change without a ruleset update must raise ValueError."""
        raw = _load_bundled_text(
            "ccnl_engine.knowledge.ccnl.data", "commercio-confcommercio.json"
        )
        tampered = _tamper(json.loads(raw))
        self._repatch(monkeypatch, json.dumps(tampered))

        with pytest.raises(ValueError, match="source_hash mismatch"):
            load_ccnl_from_bundle("commercio-confcommercio.json")

    def test_missing_ruleset_still_loads(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A legacy file without any ruleset block must load unchanged."""
        payload = make_ccnl_dict()
        payload.pop("ruleset", None)
        assert "ruleset" not in payload
        self._repatch(monkeypatch, json.dumps(payload))

        ccnl = load_ccnl_from_bundle("whatever.json")
        assert ccnl.meta.ccnl_id == "test"
        assert ccnl.ruleset is None

    def test_valid_file_loads(self) -> None:
        """The real bundled file (hash intact) still validates."""
        ccnl = load_ccnl_from_bundle("commercio-confcommercio.json")
        assert ccnl.ruleset is not None
        assert ccnl.ruleset.id == "ccnl/commercio-confcommercio"
        assert ccnl.ruleset.version == "2026.1"


class TestVerifyRulesetHash:
    """Direct branch coverage of _verify_ruleset_hash in each loader."""

    @pytest.mark.parametrize("module_path", LOADER_PATHS)
    def test_no_ruleset_is_skipped(self, module_path: str) -> None:
        """A payload without a ruleset block is never verified."""
        loader = importlib.import_module(module_path)
        verify = loader._verify_ruleset_hash
        if "contract" in module_path:
            verify({"levels": []})  # single-arg signature
        else:
            verify({"levels": []}, "file.json")

    @pytest.mark.parametrize("module_path", LOADER_PATHS)
    def test_malformed_source_hash_is_skipped(self, module_path: str) -> None:
        """A non-string source_hash is ignored (no hash comparison)."""
        loader = importlib.import_module(module_path)
        verify = loader._verify_ruleset_hash
        payload = {"a": 1, "ruleset": {"source_hash": 123}}
        if "contract" in module_path:
            verify(payload)
        else:
            verify(payload, "file.json")

    def test_contract_mismatch_raises(self) -> None:
        """Contract loader raises on a stale hash with a stable message."""
        payload = {"a": 2, "ruleset": {"source_hash": "0" * 64}}
        with pytest.raises(ValueError, match="source_hash mismatch"):
            _verify_contract_hash(payload)

    def test_tax_mismatch_raises_with_filename(self) -> None:
        """Tax loader includes the filename in the mismatch error."""
        payload = {"a": 2, "ruleset": {"source_hash": "0" * 64}}
        with pytest.raises(ValueError, match=r"in 2026-terziario\.json"):
            tax_loaders._verify_ruleset_hash(payload, "2026-terziario.json")

    def test_surtax_mismatch_raises_with_filename(self) -> None:
        """Surtax loader includes the filename in the mismatch error."""
        payload = {"a": 2, "ruleset": {"source_hash": "0" * 64}}
        with pytest.raises(ValueError, match=r"in regionale-2026\.json"):
            surtax_loaders._verify_ruleset_hash(payload, "regionale-2026.json")


class TestTaxLoaderIntegrity:
    """load_year_rules propagates ruleset blocks and rejects tampering."""

    def _raw(self, kind: str, sector: str) -> dict[str, Any]:
        pkg = f"ccnl_engine.knowledge.{kind}.data"
        return cast(
            "dict[str, Any]",
            json.loads(_load_bundled_text(pkg, f"2026-{sector}.json")),
        )

    def test_tax_and_inps_rulesets_propagated(self) -> None:
        """Both ruleset blocks surface on the merged YearRules."""
        rules = tax_loaders.load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert rules.ruleset is not None
        assert rules.ruleset.id == "tax/2026/terziario"
        assert rules.inps_ruleset is not None
        assert rules.inps_ruleset.id == "inps/2026/terziario"

    def test_tampered_tax_raw_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A tampered tax file must raise ValueError from load_year_rules."""
        raw = self._raw("tax", "terziario")
        tampered = json.loads(json.dumps(raw))
        tampered["irpef_brackets"][0]["rate"] = "0.90"
        monkeypatch.setattr(
            tax_loaders, "read_bundled", lambda pkg, f: json.dumps(tampered)
        )

        with pytest.raises(ValueError, match="source_hash mismatch in 2026"):
            tax_loaders.load_year_rules(2026, TaxSector.TERZIARIO, 50)

    def test_missing_ruleset_produces_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Legacy tax/INPS files without a ruleset yield None identities."""
        raw = self._raw("tax", "terziario")
        raw.pop("ruleset", None)
        inps_raw = self._raw("inps", "terziario")
        inps_raw.pop("ruleset", None)

        def fake_read(pkg: object, f: str) -> str:
            if "tax" in str(pkg):
                return json.dumps(raw)
            return json.dumps(inps_raw)

        monkeypatch.setattr(tax_loaders, "read_bundled", fake_read)

        rules = tax_loaders.load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert rules.ruleset is None
        assert rules.inps_ruleset is None


class TestSurtaxLoaderIntegrity:
    """load_surtax_rules rejects tampering and maps the regionale identity."""

    def test_ruleset_propagated(self) -> None:
        """SurtaxRules.ruleset reflects the regionale file identity."""
        rules = surtax_loaders.load_surtax_rules(2026)
        assert rules.ruleset is not None
        assert rules.ruleset.id == "surtax/2026/regionale"

    def test_tampered_comunale_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Tampered comunale file must raise ValueError."""
        pkg = "ccnl_engine.knowledge.surtax.data"
        reg = json.loads(_load_bundled_text(pkg, "regionale-2026.json"))
        com = json.loads(_load_bundled_text(pkg, "comunale-2026.json"))
        com["rates"]["A083"]["brackets"][0]["rate"] = "0.50"

        def fake_read(pkg_: object, f: str) -> str:
            if "comunale" in f:
                return json.dumps(com)
            return json.dumps(reg)

        monkeypatch.setattr(surtax_loaders, "read_bundled", fake_read)
        with pytest.raises(ValueError, match="source_hash mismatch"):
            surtax_loaders.load_surtax_rules(2026)
