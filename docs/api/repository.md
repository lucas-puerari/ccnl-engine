# ccnl_engine.repository

The knowledge port of the engine. A `PayrollEngine` reads every CCNL, tax
year, surtax table, capability catalog and limitation through a
`KnowledgeRepository`; `BundledKnowledgeRepository` is the one the package
ships. To add a CCNL variant or a year the bundle does not hold, pass a
repository of your own, typically one that wraps the bundled repository and
overrides the loaders it changes:

```python
from ccnl_engine import PayrollEngine
from ccnl_engine.repository import BundledKnowledgeRepository, YearRules


class WithMyYear(BundledKnowledgeRepository):
    def load_year_rules(self, year, sector, num_employees) -> YearRules:
        return super().load_year_rules(year, sector, num_employees)


engine = PayrollEngine(repository=WithMyYear())
```

Below the facade every service receives the repository it is given: none
falls back to the bundled data, so a run never mixes two sources. The
models the port returns are frozen; build a variant with
`model_copy(update=...)`.

::: ccnl_engine.repository.KnowledgeRepository

::: ccnl_engine.repository.BundledKnowledgeRepository

::: ccnl_engine.repository.PolicyResolver

::: ccnl_engine.repository.bundled_policies

::: ccnl_engine.repository.CCNL

::: ccnl_engine.repository.YearRules

::: ccnl_engine.repository.SurtaxRules

::: ccnl_engine.repository.VariablePayRules

::: ccnl_engine.repository.FamilyDeductionRules

::: ccnl_engine.repository.InpsSickPayRates

::: ccnl_engine.repository.InsuredAbsenceRates
