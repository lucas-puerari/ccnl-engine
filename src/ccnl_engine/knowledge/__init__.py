"""ccnl_engine.knowledge — versioned dataset bundle (data only).

Passive JSON resources consumed by the engine's loaders
(:mod:`ccnl_engine.engine`). The knowledge base carries no Python logic: every
file here is data plus version metadata, so it can be upgraded or redistributed
independently of the engine.

Sub-packages:
- ``ccnl_engine.knowledge.ccnl`` — one JSON file per CCNL contract.
- ``ccnl_engine.knowledge.tax`` — IRPEF / detrazioni / TFR / trattamento integrativo.
- ``ccnl_engine.knowledge.inps`` — INPS aliquote, apprendistato, lavoro domestico.
- ``ccnl_engine.knowledge.surtax`` — addizionale regionale e comunale.

Current data set version: :data:`__version__`.
"""

#: Knowledge base version. Bumped when the bundled datasets change (new year,
#: new CCNL, rate updates); independent of the library version.
__version__ = "2026.2"
