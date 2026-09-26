# Architecture rules

The package is organised by capability (`payroll`, `contract`, `tax`,
`knowledge`, `provenance`, `diff`, `shared`) plus the `api` facade. Each
capability holds only the layers it needs:

| Layer | Holds |
|---|---|
| `application/` | use cases and orchestration |
| `service/` | calculators, resolvers, loaders and repositories |
| `domain/` | types, pure rules and invariants |

The rules below are enforced by `tests/architecture/`, which parses the
sources without importing them. Imports under `if TYPE_CHECKING:` are not
counted because they never run.

## Import direction

```text
api -> application -> service -> domain
       application -> domain
```

- `domain` imports only `domain`: its own, `shared.domain`, and another
  capability's domain only through a short allowlist in
  `tests/architecture/test_dependencies.py`, where each entry states its
  reason. An entry that no import uses any more fails the suite, so the list
  can only shrink.
- `service` never imports `application`.
- `api` imports `application` only; it never reaches loaders such as
  `knowledge.service` directly.
- Only the package root `ccnl_engine/__init__.py` imports `api`.
- The graph of `<capability>.<layer>` nodes has no cycle.
- Every module belongs to a layer. The package root, `ccnl_engine.version`
  and the `knowledge` data bundle outside `knowledge/service` are metadata
  and may be imported by any layer except `domain`.

## Domain purity

Domain modules perform no I/O: no `importlib.resources`, no `pathlib`, no
`open()`, no `json.load()` and no `.read_text()`, `.read_bytes()` or
`.open()` calls. Reading bundled data is a `service` concern.

## Source layout

- At most three directories under `ccnl_engine` before a source file:
  `ccnl_engine/<capability>/<layer>/<subfeature>/file.py`. `data/` resource
  directories are exempt.
- Every directory holding Python sources has an `__init__.py`.
- No layer directory exists without at least one module besides
  `__init__.py`.
- No production module exceeds 400 lines.
