# Knowledge base

The versioned dataset bundle consumed by the loaders. Every file here is pure
JSON data plus version metadata — the knowledge base carries no Python logic,
so it can be updated or redistributed independently of the engine.

`ccnl_engine.knowledge.__version__` identifies the bundled data set (e.g.
`"2026.1"`). It is independent of the library version in `pyproject.toml`.

## Layout

| Package | Contents |
|---|---|
| `ccnl_engine.knowledge.ccnl` | One JSON file per CCNL contract under `data/` (e.g. `metalmeccanico-federmeccanica.json`) |
| `ccnl_engine.knowledge.tax` | IRPEF brackets, work-income deductions, TFR, trattamento integrativo — `data/<year>-<sector>.json` |
| `ccnl_engine.knowledge.inps` | INPS aliquote + apprendistato, or domestic-foret growth — `data/<year>-<sector>.json` |
| `ccnl_engine.knowledge.surtax` | Addizionale regionale e comunale — `data/regionale-<year>.json`, `data/comunale-<year>.json` |

## Version

::: ccnl_engine.knowledge.version.__version__

## Reading data

Loaders in `ccnl_engine.engine` read these resources through
`importlib.resources` and validate them against the engine's pydantic schemas.
Neither the engine nor the loaders recompute or store data themselves.