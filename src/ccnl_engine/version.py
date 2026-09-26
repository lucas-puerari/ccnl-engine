"""Version of the ccnl-engine library.

This mirrors the ``project.version`` in ``pyproject.toml`` and is kept in sync
manually.  It is distinct from the *knowledge base* version exposed at
``ccnl_engine.knowledge.__version__``: the library version changes when the
engine code changes, while the knowledge version changes when the bundled
datasets change.  A payroll result
records both so a result can be reproduced against the exact engine + data
combination that produced it.
"""

#: Library (engine) version.
__version__ = "0.5.1"
