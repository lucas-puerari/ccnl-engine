# Contributing

## Set up

```bash
make setup   # uv sync --locked, editable install, git hooks
make check   # lint, typecheck, complexity, architecture, tests
```

Python 3.12 or later and [uv](https://docs.astral.sh/uv/).

## Rules a change must follow

- **Branches** start with `feature/`, `fix/`, `chore/`, `ci/`, `docs/`,
  `refactor/`, `perf/`, `test/` or `revert/`.
- **Pull request titles** are conventional commits (`fix(scope): ...`);
  commits are a single line, details go in the pull request.
- **Layout**: folders are domains, files are roles; read
  [Architecture rules](docs/engine/architecture.md). `make architecture`
  enforces the dependency tiers and the 300-line module limit.
- **Tests**: 100% line and branch coverage; the test tree mirrors the code
  ([tests/README.md](tests/README.md)). A fix starts with a test that fails
  without it.
- **Data**: every payable value carries its provenance and a cited source;
  after editing a knowledge file run `make rehash` and `make generate`.
- **No personal names or emails** in data, docs or code: use roles such as
  `maintainer`.
- **No backward-compatibility shims**: the package is in alpha; a breaking
  change is listed first in `CHANGELOG.md`.

## Reporting a data error

Open an issue with the "Data error" form: the CCNL, the value, the correct
value and a link to the authoritative source. For a security problem see
[SECURITY.md](SECURITY.md).
