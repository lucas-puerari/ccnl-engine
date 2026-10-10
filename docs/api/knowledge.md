# Knowledge base

The versioned dataset bundle consumed by the loaders. Every file here is pure
JSON data plus version metadata — the knowledge base carries no Python logic,
so it can be updated or redistributed independently of the engine.

`ccnl_engine.bundle_version` identifies the bundled data set (e.g.
`"2026.3"`). It is independent of the library version in `pyproject.toml`.

## Layout

The resources are ordered as `domain/dataset/year/scope.json` under
`src/ccnl_engine/knowledge/`, and `knowledge/manifest.json` indexes each one
once: identity (`dataset_id`), path, dataset, year and scope, model, schema
version, validity (or the reason it has none), ruleset id, version and hash,
owner and the name of its compressed copy in the wheel.

| Dataset | Contents |
|---|---|
| `contract/agreement/<slug>.json` | One file per CCNL (e.g. `metalmeccanico-federmeccanica.json`) |
| `taxation/annual/<year>/<sector>.json` | IRPEF brackets, work-income deductions, TFR, trattamento integrativo |
| `taxation/family/<year>.json`, `exemption/<year>.json`, `variable_pay/<year>.json`, `severance/<year>.json` | Family deductions, somma esente, variable pay, TFR revaluation |
| `social_security/contribution/<year>/<sector>.json` | INPS rates and apprenticeship, or the domestic flat rates |
| `social_security/sickness/rates.json` | INPS sick-pay indemnity |
| `surtax/regional/<year>.json`, `surtax/municipal/<year>.json` | Addizionale regionale e comunale |
| `capability/<year>/catalog.json`, `limitation/engine.json`, `policy/italy.json` | Capability catalog, engine limitations, policy ruleset |

`scripts/data/build_manifest.py` rebuilds the manifest from the files;
`--check` fails in CI when it drifts.

## Version

::: ccnl_engine.bundle_version

## Reading data

Loaders in `ccnl_engine.contract.service`, `ccnl_engine.tax.service` and
`ccnl_engine.knowledge.service` read these resources through the manifest
(`ccnl_engine.knowledge.loaders_manifest`): a path the manifest does not list
is never read.  A wheel carries each resource compressed under the same path
with `.gz`.  The loaders validate the JSON against the engine's pydantic
schemas.
Neither the engine nor the loaders recompute or store data themselves.