# Examples

Runnable scripts covering every major feature of the engine.
Each file in `docs/examples/` is executed in CI via `tests/acceptance/public_api/test_docs_examples.py`:
if an API change breaks an example, the build fails.

## Trust — Why this number?

The most important question a payroll engine must answer is not "what is the
net salary?" but "why is it that number?" This example walks through all three
verifiability layers: provenance, versioning, and the capability report.

```python
--8<-- "docs/examples/11_why_this_number.py"
```

## Basics

### Quickstart

Minimal call: build a `PeriodInput` and pass it to `PayrollEngine.calculate_period()`.

```python
--8<-- "docs/examples/01_quickstart.py"
```

### Reading the result

`PayrollEngine.calculate_period()` returns a `PeriodResult` for one run: its status, period
gross, net and employer cost, the INPS contribution breakdown, the IRPEF
computation and the pay items.

```python
--8<-- "docs/examples/02_payroll_fields.py"
```

## Contract types

### Fixed-term (tempo determinato)

`FixedTerm(renewals=..., naspi_exclusion=...)` adds the NASpI surcharge to the employer's INPS contribution: 1.4%, plus 0.5% per renewal, unless an exclusion of L. 92/2012 art. 2 c. 29 applies; gross and net are unchanged. Left unknown, either fact blocks the run.

```python
--8<-- "docs/examples/03_fixed_term.py"
```

### Apprenticeship (apprendistato)

Percentage track: the apprentice's pay is a % of the destination level, increasing with `months_elapsed`.

```python
--8<-- "docs/examples/06_apprentice.py"
```

## Pay components

### Family deductions

A `FamilyComposition` with dependants raises the Art. 12 TUIR deductions and the net pay. The deductions read the reddito complessivo of the year: state the income beyond this employment with `CurrentYearTaxFacts` (zero included), or the result is not payable. See [Family deductions](engine/fiscal.md#family-deductions-art-12-tuir).

```python
--8<-- "docs/examples/04_part_time.py"
```

### Seniority increments (scatti di anzianità)

Pass the recognised seniority as `Employment.seniority`, a `SeniorityFact` dated and sourced; unknown seniority is a missing fact, not zero. The category selects category-specific increments.

```python
--8<-- "docs/examples/05_seniority.py"
```

### Pension fund (previdenza complementare)

Declare the enrolment in the CCNL fund as `Employment.pension_fund`; without it no fund contribution is posted. See [Pension funds](engine/pay-components.md#pension-funds-previdenza-complementare).

```python
--8<-- "docs/examples/13_pension_fund.py"
```

### Year-to-date chaining

Pass the `closing_state` of one run as the `opening_state` of the next, so progressive IRPEF and the year-to-date totals carry forward.

```python
--8<-- "docs/examples/09_negotiated_ral.py"
```

### Second-level bargaining (contrattazione di secondo livello)

Territorial or company allowances on top of the CCNL minimums, with per-item contribution/TFR/apprenticeship control.

```python
--8<-- "docs/examples/08_second_level.py"
```

## Fiscal

### Regional and municipal surcharges (addizionali)

Pass `regione` (ISO 3166-2:IT region code, e.g. `IT-45`) and `comune_belfiore` (Belfiore code, e.g. `F257`) to include addizionale regionale and comunale. The surtax of a year is determined by its conguaglio and withheld the next year by installments, so a run withholds the surtax an earlier conguaglio determined: import it with `OpeningBalances.surtax_obligations`. Check `result.assurance.calculation` and `result.decisions`: an unknown table, or a `regione` or `comune_belfiore` left `None` (decision `residence_unknown`), makes the calculation `incomplete` and the result not payable.

```python
--8<-- "docs/examples/07_addizionali.py"
```

### December paid in January (tax year and conguaglio)

A tax year holds the payments made in it (TUIR art. 51 c. 1): December paid
by 12 January is still income of its year, paid later it opens the next one.
`calculate_tax_year` computes the payments of one tax year and settles the
conguaglio on the last; `calculate_competence_year` computes the runs of one
competence year across the tax years that pay them.

```python
--8<-- "docs/examples/14_tax_year.py"
```

### Domestic work (lavoro domestico)

Flat per-hour INPS contributions; the employer does not withhold IRPEF. `weekly_hours` is required.

```python
--8<-- "docs/examples/10_domestic.py"
```
