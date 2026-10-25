"""Versions of the ccnl-engine library and of its bundled data.

The library version is read from the installed package metadata, so it
always matches the ``project.version`` of ``pyproject.toml``.  It is
distinct from the *knowledge base* version exposed at
``ccnl_engine.bundle_version``: the library version changes when the
engine code changes, while the knowledge version changes when the bundled
datasets change.  A payroll result records the knowledge version in
``bundle_version``; a persisted state records both, for audit, and is read
back by a later engine or knowledge release: only its schema version is
checked, and an earlier schema is migrated to the current one.
"""

from importlib.metadata import version

from ccnl_engine.bundle.loaders import bundle_version

#: Library (engine) version.
__version__ = version("ccnl-engine")

#: Version of the bundled data: its series and the digest of its manifest.
__bundle_version__ = bundle_version()
