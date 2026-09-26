"""Computation engine, schemas and loaders.

The engine computes payroll from pydantic domain models and ships the
loaders that read the versioned Knowledge Base datasets from
:mod:`ccnl_engine.knowledge`. The engine never stores data itself; the two
namespaces are coupled only through passive JSON resource directories.
"""
