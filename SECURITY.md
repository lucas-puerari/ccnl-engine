# Security policy

ccnl-engine computes payroll from the data it is given: it runs no
server, stores nothing and opens no network connection. A vulnerability is
most likely in how it reads input or the bundled data (a crash, a
resource exhaustion, an amount an attacker can steer) or in the release
chain.

## Reporting

Report a vulnerability privately through GitHub: the **Security** tab of the
repository, **Report a vulnerability**. Do not open a public issue for it.
Include the version (`ccnl_engine.engine_version`), the input that triggers
it and what you observed.

## What to expect

The project has one maintainer and offers no service level (see the
[versioning and support policy](https://lucas-puerari.github.io/ccnl-engine/docs/trust/data-operations/#versioning-and-support)).
Reports are read and fixed on a best-effort basis; a fix ships as a patch
release with a changelog entry, and the report is credited unless you ask
otherwise.

## Releases

Releases are published to PyPI by GitHub Actions with Trusted Publishing,
with a build attestation, from a tag on `main` that passed every quality
gate. Each GitHub release attaches the wheel, the sdist and `pylock.toml`,
the exact runtime dependencies with their hashes (PEP 751).
