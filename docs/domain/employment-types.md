# Employment types

Italian labor law recognises three categories of subordinate employment that differ
in their legal duration, INPS contribution rules, and salary computation. Each maps
to a concrete type in `ccnl_engine.inputs` passed as `Employment.contract_type`.
The field has no default: the contract type selects the NASpI surcharge and the
art. 13 TUIR deduction minimum, so it is always stated.

See [CCNL Components](components.md#8-fixed-term-tempo-determinato) for the
legal background on fixed-term and
[Apprenticeship](components.md#6-apprenticeship-apprendistato-professionalizzante)
for how the apprendistato professionalizzante contract works under Italian law.

## Permanent (*tempo indeterminato*)

The standard open-ended employment contract under Art. 2094 c.c. No duration
limit; full INPS rates apply. This is the baseline from which all other types
deviate.

```python
--8<-- "docs/examples/period/example.py"
```

## Fixed-term (*tempo determinato*)

Governed by D.Lgs. 81/2015. Duration is capped (36 months, with acausale
extensions). Gross and net pay are unchanged relative to a permanent worker at
the same level; the employer owes the NASpI surcharge on the INPS side, as a
disincentive to systematic precarious use.

### NASpI surcharge

L. 92/2012 art. 2 (Normattiva, text in force on 7 October 2026):

- **c. 28**: a contribution of 1.4% of the INPS base, charged to the
  employer on every non-permanent employment, "aumentato di 0,5 punti
  percentuali in occasione di ciascun rinnovo del contratto a tempo
  determinato, anche in regime di somministrazione" (period added by D.L.
  87/2018 art. 3 c. 2). Each renewal adds 0.5 points to the rate of the
  previous contract: 1.4%, 1.9%, 2.4%, 2.9% (INPS circ. 121/2019 par. 2.3).
  A prorogation is not a renewal, and renewals signed before 14 July 2018
  are not counted (same circular, par. 2.2 and 2.3). The increase does not
  apply to domestic work.
- **c. 29**: not charged for workers hired to replace absent workers (lett.
  a), for the seasonal activities of DPR 1525/1963 and of the Bolzano CCNLs
  of lett. b-bis (lett. b), for apprentices (lett. c), for the public
  administrations of art. 1 c. 2 D.Lgs. 165/2001 (lett. d) and for the
  services of at most three days in tourism and public establishments of
  D.Lgs. 81/2015 art. 29 c. 2 lett. b (lett. d-bis).
- **c. 3**: the whole article does not apply to the operai agricoli a tempo
  determinato o indeterminato.
- D.L. 87/2018 art. 1 c. 3: research and teaching contracts of private
  universities and research bodies keep the 1.4% but not the renewal
  increase.

`FixedTerm` carries the two facts of the contract:

| Field | Meaning | `None` |
|---|---|---|
| `renewals` | Renewals with the same employer counted from 14 July 2018, this contract being the last | Unknown: a run that owes the increase has a `missing_fact renewals` blocker |
| `naspi_exclusion` | `NaspiExclusion.NONE`, `REPLACEMENT`, `SEASONAL`, `PUBLIC_ADMINISTRATION`, `SHORT_SERVICE` or `RESEARCH` (1.4% without the increase) | Unknown: a run whose sector charges the surcharge has a `missing_fact naspi_exclusion` blocker |

Apprentices are not an exclusion of `FixedTerm`: an apprenticeship is an
`Apprentice` contract, which never pays the surcharge. The operai agricoli
are not either: the agricoltura ruleset exempts the category `operaio`, so a
level that leaves the category open has a `missing_fact category` blocker.
While a fact is missing, the amounts charge the surcharge as for a contract
with no exclusion and no renewal, and the `inps_employer` decision has no
amount. The decision records `naspi_surcharge` (`charged`, `excluded`,
`exempt_category`), `naspi_surcharge_rate` and `naspi_renewals`.

Not modelled: the refund of the surcharge on a conversion to a permanent
contract or a permanent hire within six months (c. 30), and the reading of
the seasonal exclusion for activities that only a CCNL calls seasonal (INPS
messages 269/2025 and 483/2025): the caller states the exclusion.

```python
--8<-- "docs/examples/fixed_term/example.py"
```

## Apprenticeship (*apprendistato*)

The *apprendistato professionalizzante* (Art. 44 D.Lgs. 81/2015) is a
dual-purpose contract: the employer trains the worker toward a target
qualification (*qualifica*) while benefiting from reduced INPS rates and a
below-minimum starting salary. Duration and pay progression are set by the CCNL,
not by statute.

The `Apprentice` type covers both salary tracks used by Italian CCNLs:

- **Percentage track**: pay = % of destination level minimum, stepped by elapsed
  months. Used by most industrial CCNLs (Metalmeccanico, Chimica, Edilizia).
- **Under-classification track**: the apprentice is placed at a lower level for each
  phase. Used by most tertiary CCNLs (Commercio, Turismo).

The engine picks the track of the destination level. When the CCNL has several
tracks for that level (the longer profiles of Commercio Art. 68 Tabella B, of
Edilizia or of FIPE), `Apprentice.track` names the one of the worker's profile;
without it the run raises an input error.

```python
--8<-- "docs/examples/apprenticeship/example.py"
```

## Part time (*tempo parziale*)

Part time is not a contract type: any of the three above can be part time
(Art. 4-12 D.Lgs. 81/2015). The contract states the reduced hours and how
they are spread over the week, the month and the year (art. 5 c. 2), and the
worker is paid in proportion to the work done (art. 7 c. 1).

- **Horizontal** (*orizzontale*): fewer hours every working day. State
  `Employment.weekly_hours` below `full_time_weekly_hours`, as a `Decimal`
  with up to two places (`WeeklyHours(Decimal("37.5"))`): every month pays
  `weekly_hours / full_time_weekly_hours` of the full-time pay.
- **Vertical** (*verticale*): full days on some days of the week, or some
  months of the year. State `Employment.work_pattern`, a `WorkPattern`: the
  hours of the seven days of the week (Monday first, summing to
  `weekly_hours`) and/or the `months` worked.
- **Mixed** (*misto*): both, e.g. 8 hours Monday to Wednesday from January
  to June.

A month outside `WorkPattern.months` pays no monthly pay, has no INPS
minimum (the hourly minimum of art. 11 c. 1 has no hour to count) and
accrues no tredicesima or quattordicesima rateo; a month worked pays the
weekly-hours ratio. The weekday hours are validated against
`weekly_hours`, which alone sets the ratio. See
[Pay components](../engine/pay-components.md#part-time) for what the
engine does and does not model.

**API reference:** [`Permanent`](../api/inputs.md), [`FixedTerm`](../api/inputs.md),
[`Apprentice`](../api/inputs.md), [`WeeklyHours`](../api/inputs.md),
[`WorkPattern`](../api/inputs.md)

---

[Engine: Pay components →](../engine/pay-components.md)
