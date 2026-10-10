# Migration notes

Part of the [Architecture contract](architecture-contract.md). What the
structural migrations must change besides the moves themselves.

## Namespace package spike

A throwaway branch moved `src/ccnl_engine/diff/` to
`src/ccnl_engine/comparison/ruleset/` without any `__init__.py`, moved its
tests to mirror directories without `__init__.py`, and then removed every
`__init__.py` under `tests` and the markers of two data packages
(`knowledge/ccnl`, `knowledge/policies`). Findings:

| Tool | Result | What the migration must do |
|---|---|---|
| mypy (strict) | Passes while an ancestor still has an `__init__.py` (`ccnl_engine`, `tests`). Without the markers under `tests` it stops at `Duplicate module named "test_employment_facts"`. | Set `explicit_package_bases = true` and `mypy_path = ["src", "."]`; then all 816 files pass. |
| pytest | The default `prepend` import mode breaks: the root `conftest.py` cannot import `tests.*`, and the 25 test basenames used twice raise 31 `import file mismatch` errors. | Set `--import-mode=importlib` and `pythonpath = ["."]`; then 12660 tests pass. |
| coverage | `source = src/ccnl_engine` silently drops a module in a namespace directory that no test imports, so the 100% gate cannot see it. | Set `include_namespace_packages = true` under `[tool.coverage.report]`; the unimported module then reports 0%. |
| ruff | `INP001` (implicit namespace package) fires on every module of a directory without `__init__.py`; it is ignored only for `scripts`, `demo` and `docs` today. | Ignore `INP001` for `src` and `tests` in the same change. |
| architecture tests | `test_every_module_fits_a_layer` and `test_every_source_directory_is_a_package` fail. | Classify modules by role file (`tests/architecture/_imports.py`, `ROLE_LAYERS`); keep every source directory a package (markers below). |
| docs (found in the domain migration) | griffe, behind mkdocstrings, does not load a namespace directory inside a regular package (its loader skips it on purpose), so every `:::` directive of a moved module fails and the Docs build and the Pages deploy break. | Keep a docstring-only `__init__.py` marker in every source directory; the structure guardrail and the inventory accept only such markers under `src`. |
| `importlib.resources` | `files("ccnl_engine.knowledge.ccnl.data")` on a namespace package returns a `MultiplexedPath`; `iterdir()` and `joinpath()` work in the editable install and in the wheel (126 `.json.gz`). A namespace merges every portion on `sys.path`, so a stale copy would add files silently. | Resolve resources through the manifest and check the file list against it. |
| wheel | `uv build --wheel` packs the namespace directories (`packages = ["src/ccnl_engine"]`) and the build hook still injects the `.json.gz` files; `scripts/quality/smoke_test.py` passes in a clean virtual environment. | Update the build hook directory list and the `exclude` globs, which are path-keyed. |

## Path-keyed data

A move must update every place that names a path or a dotted module:

- **Loader package strings**: `importlib.resources.files("ccnl_engine.knowledge.<x>.data")`
  in `contract/service/discovery.py`, `contract/service/loaders.py`,
  `knowledge/service/capability_catalog_loader.py`,
  `knowledge/service/limitation_loader.py`,
  `payroll/service/policy_loader.py`, `tax/service/tax_resource_reader.py`,
  `tax/service/tax_optional_loaders.py`, `tax/service/surtax_loaders.py`
  and `tax/service/tax_annual_assembler.py`.
- **Baselines**: the keys of `scripts/provenance/baseline.json`
  (`ccnl/data/<slug>.json`, relative to `knowledge`) and of
  `scripts/structure/baseline.json` (repository paths).
- **Build and packaging**: the seven directory pairs of
  `scripts/distribution/build.py`, the wheel `exclude` globs and the sdist
  `include` of `pyproject.toml`.
- **Tool configuration in `pyproject.toml`**: the Ruff `TCH`
  per-file-ignores of model modules, the mutmut `source_paths` and test
  selection.
- **CI workflows**: the path filters of `capability-matrix.yml`,
  `contract-examples.yml` and `contracts-index.yml`, and the
  `tests/fixtures/reference_tables/*.json` globs of `ci.yml`.
- **Scripts**: the knowledge prefixes of `scripts/knowledge/diff.py`,
  the data paths of the documentation generators and of
  `scripts/knowledge/update.py`, and the reference case directory of
  `scripts/provenance/check.py`.
- **Tests that hardcode data paths**: under
  `tests/integration/ccnl_engine/contract/service/`,
  `tests/integration/ccnl_engine/knowledge/service/`,
  `tests/integration/ccnl_engine/tax/service/` and
  `tests/integration/scripts/knowledge/test_diff.py`; the reference
  case directory of `tests/architecture/_provenance.py`; the layer
  allowlists of `tests/architecture/test_dependencies.py` and
  `tests/architecture/_imports.py`.
- **Documentation**: the `--8<--` snippet includes of the agreement JSON in
  the generated pages under `docs/contracts`, the `docs/trust` tables
  generated from the bundle, the
  `:::` API directives of `docs/api/`, the module paths of
  `docs/engine/architecture.md`, `docs/engine/payroll-state.md`,
  `docs/rules/index.md`, the migration guides, `tests/README.md` and
  `CLAUDE.md`.
- **Mirror rules**: the mirror check of `tests/architecture/test_test_layout.py`
  and the categories it allows.

## Amendments

Where this contract departs from the original proposal:

- `payroll/state/` is added. Period state, tax cash state, YTD and credit
  accounts, carried obligations, opening balances and the state codec are
  one concept (see [Payroll state](payroll-state.md)) and fit no other
  subdomain.
- `tax/annual/` is added for the assembled ruleset of a year and the readers
  that build it, mirroring `knowledge/taxation/annual/`.
- `catalog.py` stays at the root as a public namespace.
- The scripts tree gains `provenance/labels.py`, `provenance/rules.py`
  (payable rules) and `provenance/fiscal.py`, which had no destination, and
  `structure/inventory*.{py,json}` for the inventory itself. The five
  documentation generators keep one file each instead of one
  `generate.py`.
- A test mirror directory may hold one dataset directory of non-Python
  resources; data never sits in a `fixtures` or `data` directory.
- Knowledge JSON is exempt from the source depth limit instead of `data/`
  directories.
- `demo/release` is gitignored build output; it is part of the contract but
  not of the file inventory.
