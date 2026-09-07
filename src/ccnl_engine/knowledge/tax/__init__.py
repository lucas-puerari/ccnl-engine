"""Tax year rules datasets: IRPEF, detrazioni lavoro, TFR, trattamento integrativo.

One file per year/sector under ``ccnl_engine/knowledge/tax/data/``. The INPS
contribution block lives in :mod:`ccnl_engine.knowledge.inps`; the engine's
tax loader merges the two datasets before validating.
"""
