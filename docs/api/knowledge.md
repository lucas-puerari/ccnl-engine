# Knowledge base

The versioned dataset bundle consumed by the loaders. Every file here is pure
JSON data plus version metadata — the knowledge base carries no Python logic,
so it can be updated or redistributed independently of the engine.

`ccnl_engine.bundle_version` identifies the bundled data set: its release
series and a digest of the manifest (e.g. `"2026.3+5d69b5708cfb"`). The
manifest records the content hash of every resource, so two bundles that
differ in any file never share a version. It is independent of the library
version in `pyproject.toml`.

## Layout

The resources are ordered as `domain/dataset/year/scope.json` under
`src/ccnl_engine/knowledge/`, and `knowledge/manifest.json` indexes each one
once: identity (`dataset_id`), path, dataset, year and scope, model, schema
version, validity (or the reason it has none), ruleset id, version and hash,
owner and the name of its compressed copy in the wheel.
Every resource has a content hash. Engine-maintained registries that have no
enclosing ruleset identity, and legacy resource formats that have no explicit
schema version, carry an explanatory note in place of the absent metadata.

| Dataset | Contents |
|---|---|
| `agreement/<slug>.json` | One file per CCNL (e.g. `metalmeccanico-federmeccanica.json`) |
| `sector/<year>/<sector>.json` | IRPEF brackets, work-income deductions, TFR, trattamento integrativo |
| `family/<year>.json`, `tax_credit/somma_esente/<year>.json`, `variable_pay/<year>.json`, `severance/revaluation/<year>.json` | Family deductions, somma esente, variable pay, TFR revaluation |
| `contribution/<year>/<sector>.json` | INPS rates and apprenticeship, or the domestic flat rates |
| `sickness/indemnity/rates.json` | INPS sick-pay indemnity |
| `surtax/regional/<year>.json`, `surtax/municipal/<year>.json` | Addizionale regionale e comunale |
| `capability/registry/<year>.json`, `limitation/engine.json`, `pay_item/italy.json` | Capability catalog, engine limitations, policy ruleset |

`scripts/knowledge/manifest/build.py` rebuilds the manifest from the files;
`--check` fails in CI when it drifts.

## Version

::: ccnl_engine.bundle_version

## Reading data

The loaders of each concept and the readers of `ccnl_engine.bundle` read
these resources through the manifest (`ccnl_engine.bundle.loaders`): a path the manifest does not list
is never read.  A wheel carries each resource compressed under the same path
with `.gz`.  The loaders validate the JSON against the engine's pydantic
schemas.
Neither the engine nor the loaders recompute or store data themselves.
