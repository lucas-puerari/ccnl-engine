"""Test suite for ccnl_engine.

- ``unit/``: pure rules and value objects, no filesystem and no real bundle.
- ``integration/``: loaders, repositories, the real knowledge bundle and the
  wiring of several modules.
- ``acceptance/``: behaviour observed through the public ``PayrollEngine``.
- ``architecture/``: dependencies, structure, public exports and data quality.
- ``fixtures/``: data and helpers used by the categories above, never tests.
"""
