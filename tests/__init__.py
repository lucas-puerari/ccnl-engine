"""Three-level test suite for ccnl_engine.

Level 1 — ``unit/``: code correctness. Algorithms, validators, and
  serialisation tested in isolation with synthetic CCNL objects. 100% branch
  coverage enforced on every run.

Level 2 — ``data/``: domain correctness. Salary table values, seniority
  increments, and apprenticeship percentages verified directly against the
  bundled CCNL knowledge JSON files. No tax computation involved.

Level 3 — ``reference/``: end-to-end correctness. Full ``compute()`` runs on
  real CCNL + tax/INPS data compared field-by-field against pre-recorded
  expected payroll results. An optional ``source`` field on each case records
  the primary document used for verification.
"""
