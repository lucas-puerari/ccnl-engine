# Regional and municipal surcharges

The engine computes *addizionale regionale* and *addizionale comunale* only
for the jurisdictions the request names:

- `regione`: the ISO 3166-2:IT subdivision code of the region, `IT-` and
  two digits, for example `IT-45` for Emilia-Romagna or `IT-25` for
  Lombardia (source: [ISO Online Browsing Platform](https://www.iso.org/obp/ui/#iso:code:3166:IT)).
  The regional surtax is set separately by the autonomous provinces, so use
  `IT-BZ` (Bolzano) or `IT-TN` (Trento); `IT-32` (Trentino-Alto Adige) is
  rejected.  The codes are listed in [`REGION_CODES`](../api/models.md#fiscal).
- `comune_belfiore`: the *codice catastale* (Belfiore code) of the
  municipality, one upper-case letter and three digits, for example `F257`
  for Modena.

A malformed code (`ER`, `Lombardia`, `IT45`, `f257`) is rejected with
`InvalidInputError`.  A well-formed code without a row in the tax year table
is not an input error: see the decisions below.  A code left `None` is an
unknown residence, not a residence without surtax: when the employer is a
withholding agent the run has a `requirement_unresolved` blocker on the
surtax it cannot decide (see
[Fail-closed payability](../trust/confidence.md#fail-closed-payability)).

```python
--8<-- "docs/examples/07_addizionali.py"
```

## When the surtax is withheld

The surtax of tax year N is **determined by the conguaglio of N** and
**withheld on the payslips of N+1**:

| Component | Determined by | Withheld | Codice tributo | Source |
|---|---|---|---|---|
| Regional surtax of N | conguaglio of N | up to 11 installments, January to November of N+1 | 3802 | D.Lgs. 446/1997 art. 50 c. 4 |
| Municipal saldo of N | conguaglio of N: municipal surtax of N less the acconto withheld in N | up to 11 installments, January to November of N+1 | 3848 | D.Lgs. 360/1998 art. 1 c. 5 |
| Municipal acconto of N+1 | conguaglio of N: 30% of the municipal surtax on the income of N, rate and threshold of N | up to 9 installments, March to November of N+1 | 3847 | D.Lgs. 360/1998 art. 1 cc. 4-5 |

Art. 50 c. 4 reads "trattenuto in un numero massimo di undici rate, a
partire dal periodo di paga successivo a quello in cui le stesse sono
effettuate e non oltre quello relativamente al quale le ritenute sono
versate nel mese di dicembre"; art. 1 c. 5 applies the same words to the
municipal saldo and sets the acconto "in un numero massimo di nove rate
mensili, effettuate a partire dal mese di marzo". The withholding remitted
in December is the one of the November pay period, so the engine, whose
conguaglio is the last payslip of the year, withholds:

- one installment on each **regular** payslip of the window, the maximum
  number of equal installments rounded to the cent, the last one taking
  the residual; the November payslip takes whatever is left;
- nothing on the extra-month payslips (tredicesima, quattordicesima), the
  December payslip or an adjustment run;
- on the **last run of the employment**, every residual at once ("in caso
  di cessazione del rapporto l'importo è trattenuto in unica soluzione",
  art. 50 c. 4; "l'addizionale residua dovuta è prelevata in unica
  soluzione", art. 1 c. 5). That run is also the conguaglio of its year:
  the regional surtax and the municipal saldo of the year are withheld on
  it, and no acconto of the next year is determined (CU 2026 instructions,
  point 29 "non dovrà essere compilato" at the cessazione).

When the acconto withheld in the year exceeds the municipal surtax due, the
conguaglio gives the excess back on a `SURTAX_REFUNDS` line (CU 2026
instructions, point 26: the acconto "effettivamente trattenuto, al netto,
quindi, di quanto eventualmente restituito"). The CU text covers the
cessazione; the engine applies the same refund at the ordinary conguaglio,
where the saldo "determinato all'atto delle operazioni di conguaglio"
(art. 1 c. 5) is negative.

A termination run after the last withholding slot is a second conguaglio
of the year: it determines the surtax of the year again on the final
income, drops what the first conguaglio deferred, and withholds the
difference from what an earlier conguaglio of the year already withheld.

A debt keeps the region or municipality of the year that determined it:
the installments of N+1 do not read the `regione` and `comune_belfiore` of
the N+1 runs.

### First year computed by the engine

The engine withholds in year N only the surtax an earlier conguaglio
determined. For an employment it computes from January 2026 the 2025
saldi and the 2026 acconto come from the conguaglio of 2025, run by the
previous provider or by the employer before the engine: import them with
`OpeningBalances.surtax_obligations` and `municipal_advance_withheld`.
Without them **no surtax is withheld in 2026** and the whole 2026 surtax
is deferred to 2027. The law still requires the 2025 amounts to be
withheld in 2026 by the employer that certified them.

For a worker hired during N with no earlier employment at the same
employer, no acconto of N is withheld (the acconto is determined by the
conguaglio of the year before), the conguaglio of N determines the whole
municipal surtax as saldo, and the acconto of N+1 is computed on the income
this employer paid in N.

## Surtax decisions

Each jurisdiction named in the request records a `CalculationDecision` in
`result.decisions`, with capability `addizionale_regionale` or
`addizionale_comunale`. On the conguaglio its `amount` is the annual surtax
of the tax year on the annual taxable income; on any other run the surtax
is not determined. Its `inputs` hold the code, the table row name, the tax
year and the taxable income, and its `rule` and `rule_version` the bundled
ruleset.

| `reason_code` | Status | Amount | Meaning |
|---|---|---|---|
| `determined_at_conguaglio` | `final` | 0 | A run before the conguaglio: the table exists, nothing of the year is determined yet. |
| `table_applied` | `final` | computed | The bundled row of the tax year was applied: brackets, and for a regional row its whole-income rate and income-only deductions. |
| `dependent_provisions_not_applied` | `provisional` | computed | The regional row has provisions for dependents or disability that are not applied, and the request declares a child or a disabled dependent; issue `regional_surtax_dependent_provisions_not_applied` quotes them. |
| `prior_year_rates_applied` | `provisional` | computed | The municipal row holds the rates of an earlier year (`inputs["rates_year"]`): no delibera of the tax year was published when the table was built; issue `municipal_surtax_prior_year_rates`. |
| `specific_exemptions_not_applied` | `provisional` | computed | The municipal row exempts only a category of income (for example lavoro dipendente up to a limit); issue `municipal_surtax_specific_exemptions_not_applied` quotes the exemptions. |
| `below_exemption_threshold` | `final` | 0 | The regional or municipal exemption threshold covers the taxable income. |
| `no_irpef_due` | `final` | 0 | Net IRPEF (gross less the deductions) of the year is zero, so no surtax is due. |
| `table_unknown` | `incomplete` | `None` | The code is well formed but the tax year table has no row for it. |

A `table_unknown` decision comes with a `CalculationIssue` coded
`regional_surtax_unknown` or `municipal_surtax_unknown`, on every run, not
only on the conguaglio. Nothing is determined for that surtax and the
period result, hence the year result, is `incomplete`: **it must not be
paid as is**. Without `regione` and `comune_belfiore` no surtax decision is
taken and nothing is determined; the installments carried in are withheld
all the same.

The conguaglio and each installment record one more decision per
component, with the same capability and `inputs["component"]`
(`regional_balance`, `municipal_balance` or `municipal_advance`),
`inputs["reference_year"]` and `inputs["jurisdiction"]`:

| `reason_code` | Amount | Meaning |
|---|---|---|
| `deferred_to_installments` | deferred | The conguaglio opened the obligation; `inputs["installments_total"]`, and `inputs["advance_withheld"]` for the saldo. |
| `withheld_at_termination` | withheld | The last run of the employment withheld the surtax of its year at once. |
| `surtax_refunded` | negative | The surtax withheld in the year (usually the acconto) exceeded what is due; the difference is refunded. |
| `installment_posted`, `last_installment_posted` | withheld | An installment of a carried obligation; `inputs["installment_number"]`, `installments_total`, `residual_before`. |
| `settled_at_termination` | withheld | The residual of a carried obligation, on the last run of the employment. |

The surtax is due only when the IRPEF net of its deductions is due
(D.Lgs. 446/1997 art. 50 c. 2 for the regional, D.Lgs. 360/1998 art. 1 c. 4
for the municipal): a worker whose deductions absorb the whole gross IRPEF
owes neither.

### Foreign tax credit

Both articles take the IRPEF net of the deductions **and of the credit for
taxes paid abroad**: art. 50 c. 2 D.Lgs. 446/1997 names the "crediti di cui
agli articoli 14 e 15" of the TUIR in its former numbering (art. 15 is now
art. 165), art. 1 c. 4 D.Lgs. 360/1998 the "credito di cui all'articolo 165".
See [Foreign tax credit at the conguaglio](fiscal.md#foreign-tax-credit-at-the-conguaglio):
when the credit brings the net IRPEF to zero, both surtax decisions are
`no_irpef_due`.

### Regional rates of 2026

`regionale-2026.json` is taken from the MEF Dipartimento delle Finanze
pages of the addizionale regionale, one per region or autonomous province
(`addregirpef.php?reg=NN&anno=2026`, retrieved on 27 September 2026). Each
row records the URL of its page, the MEF publication date and a
`derived` provenance; no row has been checked by a named reviewer yet.
Where MEF lists two delibere for 2026 (Molise, Puglia) the later one, which
raises the rates under art. 1 c. 174 L. 311/2004, is bundled.

The provisions that depend on income only are computed:

| Row | Provision |
|---|---|
| Valle d'Aosta | Exempt up to 15,000 euro, then 1.23% on the whole income. |
| Trento | A 30,000 euro deduction for income up to 30,000 euro, stored as an exemption threshold. |
| Friuli-Venezia Giulia | 0.70% on the whole income up to 15,000 euro, otherwise 1.23% on the whole income. |
| Lazio | 1.73% on the whole income up to 28,000 euro; a 60 euro detrazione above 28,000 and up to 30,000 euro. |
| Umbria | 1.23% on the whole income up to 28,000 euro; a 150 euro detrazione above 28,000 and up to 50,000 euro. |
| Bolzano | A 430.50 euro detrazione up to 90,000 euro, and up to 125 euro above 50,000 euro (125 x (income - 50,000) / 25,000). |

Regional deductions never create a credit: the surtax is floored at zero.
Income limits are checked on the IRPEF taxable income of the employment,
also where the regional law refers to *reddito complessivo* (Valle
d'Aosta) or adds income taxed separately (Bolzano).

Provisions for dependents or disability are **not** computed: per-child
detrazioni (Bolzano, Campania, Piemonte, Puglia, Sardegna, Trento) and
reduced rates for a disabled taxpayer or family member (Marche, Veneto).
The row states them in `dependent_provisions`. When the request declares a
child or a disabled dependent in `family_composition`, the regional
decision is `provisional` with the issue
`regional_surtax_dependent_provisions_not_applied`; the surtax withheld
may be too high. The engine has no input for the disability of the worker,
so the Veneto rate for a disabled taxpayer without dependents is not
flagged.

### Municipal rates of the tax year

The acconto of N+1 uses the rate and threshold "nella misura vigente
nell'anno precedente" (art. 1 c. 4), which at the conguaglio of N are those
of N; the saldo of N uses them too. `comunale-2026.json` is generated by
`scripts/data/build_comunale_surtax.py` from the MEF *elenco generale*
CSV of 2026 and of 2025, downloaded on 27 September 2026 (their sha256 is in
the file notes). A municipality that published a 2026 delibera has its 2026
rates (`final`). One that has not yet (`0*` in the list, 4,558 of 7,897 at
download, Milano, Roma and Torino included) keeps its 2025 rates, which
stay in force without a new delibera (art. 1 c. 169 L. 296/2006): the row
has `rates_year: 2025` and an `assumed` record, and its decision is
`provisional` with the issue `municipal_surtax_prior_year_rates` until the
table is rebuilt from a later list. A delibera can still be published until
20 December 2026. Municipalities without a surtax have a zero rate row.

Exemptions for a category of income only (`FLAG_NUOVA` 5 and 6 of the
list, for example lavoro dipendente up to 12,000 euro) are kept as text in
`specific_exemptions` and not computed; a row with them is `provisional`
with the issue `municipal_surtax_specific_exemptions_not_applied`. To
refresh the table, download both lists and run the script as its docstring
shows; a row it cannot read stops the build.
