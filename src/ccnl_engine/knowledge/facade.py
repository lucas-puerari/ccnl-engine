"""ccnl_engine.knowledge — versioned dataset bundle (data only).

Passive JSON resources consumed by the capability loaders (contract, tax,
payroll), ordered as ``domain/dataset/year/scope.json`` and indexed by
``manifest.json``: every resource is listed there once, with its identity,
model, validity, ruleset and wheel name.  The JSON carries no Python logic,
so it can be upgraded or redistributed independently of the engine.  The
only code is :mod:`ccnl_engine.knowledge.loaders_manifest`, which reads the resources
through the manifest.

Datasets:
- ``contract/agreement/<slug>.json`` — one file per CCNL.
- ``taxation/annual/<year>/<sector>.json`` and ``taxation/<dataset>/<year>.json``
  — IRPEF, deductions, TFR, somma esente, variable pay, TFR revaluation.
- ``social_security/contribution/<year>/<sector>.json`` and
  ``social_security/sickness/rates.json`` — INPS rates and sick pay.
- ``surtax/regional|municipal/<year>.json`` — addizionali.
- ``capability/<year>/catalog.json``, ``limitation/engine.json``,
  ``policy/italy.json``.

Current data set version: :data:`__version__`.
"""

#: Knowledge base version. Bumped when the bundled datasets change (new year,
#: new CCNL, rate updates); independent of the library version.
__version__ = "2026.3"
