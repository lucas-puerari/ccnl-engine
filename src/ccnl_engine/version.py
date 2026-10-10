"""Version of the ccnl-engine library.

This mirrors the ``project.version`` in ``pyproject.toml`` and is kept in sync
manually.  It is distinct from the *knowledge base* version exposed at
``ccnl_engine.bundle_version``: the library version changes when the
engine code changes, while the knowledge version changes when the bundled
datasets change.  A payroll result records the knowledge version in
``bundle_version``; a persisted state records both, and is read back only by
the same engine and knowledge, so a chain of runs is never continued under
other code or rules.
"""

#: Library (engine) version.
__version__ = "0.6.0"
