"""Level 3 — reference tests: end-to-end correctness.

Each case JSON wires the real bundled loaders (CCNL, tax/INPS, surtax) into
``compute()`` and compares every ``PayrollResult`` field against pre-recorded
expected values. An optional ``source`` block on each case records the primary
document (payslip, official table, or circular) used to verify the numbers.
"""
