"""Registry of the defaults of the public input fields.

Every field with a default in the public input types (the request and plan
types of :mod:`ccnl_engine`, the facts of :mod:`ccnl_engine.inputs` and the
events of :mod:`ccnl_engine.events`) is classified in
:data:`~ccnl_engine.payroll.domain.input_defaults.registry\
.INPUT_DEFAULTS`, keyed ``"Type.field"``: either its default is the
fact, or it stands for a fact the caller has not stated (see
:mod:`~ccnl_engine.payroll.domain.input_defaults.model`).  An architecture
test fails on a defaulted public field without a classification.
"""
