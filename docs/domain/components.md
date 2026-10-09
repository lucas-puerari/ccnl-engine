# CCNL Components

Every CCNL is built from a standard set of components. Understanding them is
essential for interpreting the library's input types and output fields.

## 1. Job levels (*livelli di inquadramento*)

Workers are classified into a hierarchy of levels (*livelli*), each corresponding to
a skill and responsibility band. Levels are typically grouped into categories:

| Category | Description |
|---|---|
| Operaio | Blue-collar worker |
| Impiegato | White-collar employee |
| Quadro | Middle management (not quite *dirigente*) |
| Dirigente | Senior executive |

Classification is determined at hire and may change through vertical progression.
Minimum salaries are non-decreasing across levels: a higher level always carries
a higher minimum than the one below it.

## 2. Base salary (*minimo tabellare*)

The base salary is the **statutory floor** for each level. It is set by the CCNL
and cannot be reduced by individual contract.

Because CCNLs are renewed in tranches, the minimum changes at scheduled dates.
The library models these as a time series: every call passes an `as_of` date and
the engine resolves the correct value.

*Example — Metalmeccanico C3 level (monthly, gross):*

| Effective date | Base salary (EUR/month) |
|---|---:|
| 2024-06-01 | 2,133 |
| 2025-01-01 | 2,172 |
| 2026-01-01 | 2,211 |

## 3. Historical allowances (*indennità storiche*)

Three frozen elements appear in many CCNLs:

| Allowance | Description | Value |
|---|---|---|
| Contingenza | Cost-of-living supplement, frozen Nov 1993 (L. 438/1992) | Level-specific |
| EDR | *Elemento Distinto della Retribuzione*, added in 1993 | €10.33/month |
| Terzo elemento | Sector-specific third element | Varies |

**Conglobamento vs. separated:** Many modern CCNLs *conglobate* (merge) contingenza
and EDR into the base salary figure, so the published minimum already includes them
and no separate rows appear. Others keep them as distinct allowance rows. The library
handles both: when allowances are listed separately, the engine sums them; when
conglobated, the base salary column already reflects the merged value.

## 4. Seniority increments (*scatti di anzianità*)

Workers accumulate a pay increment — *scatto di anzianità* — at regular intervals
of service. Key parameters:

- **Cadence**: how many months between increments (e.g. 24 months for Metalmeccanico,
  36 months for Commercio).
- **Amount**: a fixed EUR amount per level, defined in the CCNL.
- **Maximum**: the number of increments that can be accumulated (e.g. 5 for most).

Seniority is based on **company tenure**, not age. It is distinct from career
progression, which involves a change of level.

Some CCNLs use a tiered model: the cadence changes after a certain number of
increments (e.g. the first 4 increments every 24 months, then every 36 months).

## 5. Additional months and hourly divisor

### Additional months

All Italian workers receive a **thirteenth month** (*tredicesima*) paid in December.
Many CCNLs add a **fourteenth month** (*quattordicesima*), usually in June. The
engine accounts for both via the `parameters.additional_months` time series.

`additional_months` is an entitlement in equivalent months of pay, not a count
of payslips. Cooperative Sociali grants 13.5: a full tredicesima and half a
quattordicesima. The engine keeps three values apart:

| Concept | Type | Cooperative Sociali |
|---|---|---|
| Equivalent months of pay | `ExtraMonthEntitlement` | 13.5 |
| Payslips in the year | `PayrollRunCount` | 14 |
| IRPEF withholding slots | `WithholdingSchedule` | 14, the June quattordicesima carrying 0.5 |

The IRPEF projection and the year-end conguaglio run on the withholding
schedule. Each upcoming slot is projected at the pay its run kind carries
(a regular month, or the extra-month pay scaled by its fraction), and the last
slot settles the tax on the final taxable income. A value strictly between 12
and 13 (a partial tredicesima) is rejected.

These counts are for a full year. With an employment period, only the runs of
months the employment overlaps exist, and an extra month has a run only when
its payment month is one of them. The withholding schedule follows the
payments actually made in the tax year. Each extra month pays one twelfth per qualifying month of its
window (at least 15 accruing days), and the ratei of an extra month not paid
before the termination are paid on the last regular run.

### Hourly divisor (*divisore orario*)

The hourly divisor converts a monthly salary into an hourly rate. It is derived from
the standard weekly hours defined in the CCNL (see `parameters.hourly_divisor` in the
contract's JSON file). Each CCNL defines its own value; never copy one contract's
divisor into another.

## 6. Apprenticeship (*apprendistato professionalizzante*)

The *apprendistato professionalizzante* (D.lgs. 81/2015, Art. 41–47) is a fixed-term
training contract that allows reduced labour costs. Key features:

- Duration: up to 36 months (can extend to 60 in some sectors).
- Employer can terminate without notice at the end of the period.
- Reduced INPS employer contributions (often ~10% for employers with < 9 employees).

Two distinct salary models exist:

### Percentage track (*percentuale*)

The apprentice's pay is expressed as a percentage of the destination level's
minimum, increasing at preset thresholds.

*Example — Metalmeccanico:*

| Phase | Months elapsed | % of destination level |
|---|---:|---:|
| 1 | 0–11 | 70% |
| 2 | 12–23 | 80% |
| 3 | 24+ | 90% |

Used in: Metalmeccanico, Chimica, Edilizia, and most industrial CCNLs.

**What the percentage reduces.** The percentage applies to the base salary
(*minimo tabellare*), to the seniority and to each fixed allowance whose
`apprenticeship_pct_relevant` flag is `true`. An allowance with the flag
`false` is paid at its full contractual value. The flag defaults to `true`,
so an allowance is reduced unless the contract data exempts it.

Many CCNLs list the elements the percentage applies to, and whatever is not
listed is paid in full. *Example: Trasporto Aereo, Gestori Aeroportuali*,
Art. G14 c. 16 applies the percentage to "minimi tabellari in vigore,
indennità di contingenza"; the EDR (Art. G22) is not listed and is paid in
full to apprentices.

| Level 4, 36-month track, month 0 (75%) | Full value | Apprentice |
|---|---:|---:|
| Minimo tabellare | 1307.47 | 980.60 |
| Indennità di contingenza | 522.19 | 391.64 |
| EDR (`apprenticeship_pct_relevant: false`) | 41.85 | 41.85 |
| **Gross** | 1871.51 | **1414.09** |

Each component is rounded to the cent after the percentage. The run records
an `apprenticeship_scaling` decision with the percentage, the scaled
components (`base_salary`, `seniority` when due, allowance codes) and the
unscaled allowance codes. Part-time scaling, when it applies, follows the
apprenticeship percentage.

Bundled CCNLs that exempt allowances: Trasporto Aereo (EDR), Energia e
Petrolio (EDR IPCA, indennità di funzione), Igiene Ambientale Utilitalia
(EDR, indennità integrativa). Vetro Meccanizzato flags its TER but models no
apprenticeship track, so the flag has no effect there.

### Under-classification track (*sottoinquadramento*)

The apprentice is formally assigned to a level two steps below the destination,
then moves up at scheduled months.

*Example — Commercio:*

| Phase | Months elapsed | Effective level |
|---|---:|---|
| 1 | 0–11 | Destination − 2 |
| 2 | 12–23 | Destination − 1 |
| 3 | 24+ | Destination |

Used in: Commercio, Turismo, and most tertiary-sector CCNLs.

## 7. Part-time

Part-time contracts scale base pay, seniority, and most allowances proportionally
to the agreed ratio of full-time hours. Individual frozen elements (*ad personam*
amounts agreed outside the CCNL table) are not scaled.

## 8. Fixed-term (*tempo determinato*)

Remuneration is identical to a permanent contract. The only difference is an
additional **NASpI *addizionale*** charged to the employer on the INPS base:
1.40%, plus 0.50% for each renewal of the contract (Art. 2, c. 28, L.
92/2012). It is not due for replacement, seasonal, apprenticeship and public
administration contracts (c. 29) nor for the operai agricoli (c. 3); see
[Employment types](employment-types.md#fixed-term-tempo-determinato).

## 9. Social contributions (INPS)

### Percentage-based (all sectors except domestic work)

Both employee and employer contribute a percentage of gross salary, up to an annual
ceiling (*massimale IVS*). Rates vary by sector, employer size, and contract type.
The `tax/data/` files bundled with the library carry the precise rates for each year
and sector.

Public employees contribute to the fund of INPS Gestione Dipendenti Pubblici their
CCNL names (`meta.public_pension_fund`): CTPS for the State (8.80% employee, 24.20%
employer), CPDEL for the enti locali and the health service, CPS for its doctors and
veterinarians (8.85% and 23.80%).

They also finance the end-of-service fund of the Gestione on 80% of the pay: ENPAS
for the State (the tredicesima left out), INADEL for the others (the tredicesima
included). State the regime in `Employment.public_end_of_service`:

- `tfs`: the worker pays 2.50%, the administration 7.10% (ENPAS) or 3.60% (INADEL);
  no TFR accrues;
- `tfr_inps`: the administration pays 9.60% or 6.10% and the gross is reduced by the
  2.50% the worker no longer pays, a negative earning `public_tfr_reduction` outside
  the INPS and TFR bases (DPCM 20 dicembre 1999 art. 1 c. 3), so net, taxable and the
  cost of the administration equal those of the TFS; INPS accrues the TFR
  notionally, the run posts none. A fixed term or a member of Perseo Sirio or Espero
  is on the TFR: `tfs` raises `InvalidInputError`;
- `tfr_employer`: enti pubblici non economici and enti di ricerca accrue the TFR
  themselves and pay the Gestione nothing.

Left `None`, the run leaves these contributions out with the issue
`public_end_of_service_unknown`.

Every public employee also pays the credit contribution of the Gestione: 0.35% of the
pension base (L. 662/1996 art. 1 c. 242), the component `credit_employee`. The
employees of an ente di diritto pubblico other than the State, the Province and the
Comuni also pay the Assicurazione Sociale Vita, ex ENPDEP (INPS circ. 104/2014):
0.027% of the worker and 0.093% of the employer on the pension base. State it in
`EmployerProfile.public_life_insurance`; the CCNL of the State school and of the
forze di polizia fix it as not owed, the others leave the run incomplete with the
issue `public_life_insurance_unknown` until it is stated. The permanent teachers of
the scuola dell'infanzia and primaria (`CCNLParameters.enam_levels`) pay the ENAM:
1% of 80% of the stipendio (L. 93/1957 art. 3), the component `enam_employee`; the
stipendio leaves out the IIS conglobata, which the bundle does not give apart, so the
run has the open limitation `enam_base`.

### Flat hourly rate (domestic work)

Domestic workers (*lavoro domestico*) use a different system: INPS publishes tables
of fixed per-hour contributions by wage bracket. No percentage of gross applies.

### Contribution base

The INPS base is the gross pay of the run with the events that enter it; a fixed
allowance is never taken out of it, so the contract data rejects
`contribution_relevant = false`. The TFR base leaves out the allowances flagged
`tfr_relevant = false` (art. 2120 c. 2 c.c.: "salvo diversa previsione dei contratti
collettivi"), and so do the bases built on it: the pension funds on the TFR base and
the end-of-service base of a public employee.

## 10. IRPEF and surcharges

### IRPEF

Italian personal income tax is progressive, computed on *reddito imponibile* (taxable
income = gross − INPS employee contributions). Rates and brackets are set by law
annually; values for each year are in the bundled `tax/data/` files.

Workers earning from employment receive a **work income deduction** (*detrazione da
lavoro dipendente*, Art. 13 TUIR): a credit that decreases as income rises and
reaches zero around €50,000.

Workers with taxable income between €8,500 and €28,000 receive the **trattamento
integrativo** (Art. 1 D.L. 3/2020): €1,200/year, paid on the payslip by the
employer as withholding agent (art. 1 c. 3) and offset against the taxes it pays
over.

### Addizionale regionale

A regional surcharge on taxable income, with rates set by each region. Rates are
in the bundled `surtax/data/regionale/` files.

### Addizionale comunale

A municipal surcharge on taxable income, identified by the municipality's *codice
catastale*. Rates are in the bundled `surtax/data/comunale/` files.

### Domestic work exception

A household employer is not a *sostituto d'imposta*: it is not among the
withholding agents of art. 23 c. 1 DPR 600/1973 (art. 33 c. 1 D.Lgs. 33/2025
from 2027). Its payslips withhold no IRPEF and no surcharges, and pay no
trattamento integrativo, somma esente or ulteriore detrazione, since those are
recognized by the withholding agent (D.L. 3/2020 art. 1 c. 3; L. 207/2024
art. 1 c. 7). The worker declares the income and pays the tax directly. See
[Engine: Domestic work](../engine/domestic-work.md).

## 11. TFR (*Trattamento di Fine Rapporto*)

The severance fund accrues annually at 1/13.5 of the TFR-relevant remuneration
(Art. 2120 c.c.). The TFR base is gross pay minus elements flagged
`tfr_relevant = false` in the contract data.

L. 297/1982 art. 3 cc. 15-16 raised the employer IVS rate by 0.50% of the
INPS taxable pay and has the employer deduct that contribution from the TFR
quota of the same period, or from the TFR paid to a pension fund. The 0.50%
is already inside the employer IVS rate (23.81% in industria), so
the employer cost counts it once: the INPS contributions include it and the
TFR accrued is net of it. The deduction is charged on the IVS base of the
run, events outside the TFR base included, and never exceeds the quota.
The bundle applies the deduction in industria, terziario, artigianato,
credito and edilizia. It does not apply it, and the quota accrues whole, in
public administration (not insured with the FPLD), in domestic work (named
by c. 15, but paid by flat hourly contributions with no percentage IVS base)
and in agricoltura (the composition of its employer rate is not sourced).
For apprentices the 0.50% is not due (INPS circ. 70/2007, note 5): the
quota accrues whole.

The TFR not destined to a pension fund goes to the Fondo Tesoreria INPS
(L. 296/2006 art. 1 cc. 755-756) when the employer is obliged: at least 50
employees on the yearly average of 2006, or of the year the activity
started (DM 30 gennaio 2007 art. 1 c. 6); from 2026 also an employer that
reaches the threshold later, on the average of the year before, with at
least 60 employees in 2026 and 2027 (c. 756 as in force from 12 August
2026). Some workers are excluded (DM art. 1 c. 8), and so are domestic
employers and the public administrations. The Fondo takes the quota net of
the 0.50%. The headcount of the run is not the test: the caller states the
outcome as `Employment.tfr_treasury_fund`.

The fund, excluding the quota accrued in the year, is revalued at 31
December by 1.5% plus 75% of the yearly increase of the ISTAT FOI index
without tobacco (art. 2120 c. 4 c.c.; L. 81/1992 art. 4 c. 1); the
revaluation bears a 17% substitute tax charged to the fund (D.Lgs.
47/2000 art. 11 cc. 3-4, paid by the employer: acconto by 16 December,
saldo by 16 February). See [Pay components: TFR](../engine/pay-components.md#tfr).

## 12. Second-level bargaining (*contrattazione di secondo livello*)

Company or territorial agreements may supplement the national CCNL with additional
allowances: productivity bonuses, shift premiums, welfare. Each supplementary element
can be independently configured for INPS, TFR, and apprenticeship scaling.

The 5% preferential tax rate on *premi di risultato* (Art. 1 c. 182 L. 208/2015) is
**not** computed by the engine.

---

→ [Guide: How to use the library](../domain/employment-types.md)  
→ [Contracts: all 85 supported CCNLs](../contracts/index.md)
