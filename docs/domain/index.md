# What is a CCNL?

A **CCNL** (*Contratto Collettivo Nazionale di Lavoro* — National Collective Labor
Agreement) is the legal instrument that governs the employment relationship for a
category of Italian workers. It fixes minimum wages, seniority rules, working hours,
leave entitlements, and dozens of other conditions for an entire economic sector,
binding on all employers who belong — or are functionally comparable — to the
signatory employers' association.

## Constitutional basis

Art. 39 of the Italian Constitution guarantees freedom of association for workers
and employers, and grants registered unions the power to conclude collective agreements
with *erga omnes* effect. In practice, registration is never used and Italian law does
not formally extend CCNL coverage to all workers in a sector. However, courts
systematically apply the minimum wage and core terms of the sector's leading CCNL to
any worker performing that type of work, regardless of the employer's formal
affiliation. The result is *de facto* universality.

## Who signs a CCNL

Every CCNL is the product of bargaining between two sides:

- **Employers' association** (*associazione datoriale*): for example Federmeccanica
  (engineering), Confcommercio (trade and services), ARAN (public sector).
- **Union federations** (*federazioni sindacali*): typically CGIL, CISL, and UIL
  affiliates for the relevant sector (e.g. FIOM-CGIL, FIM-CISL, UILM-UIL for metals).

## CNEL registration

The National Council for Economics and Labour (CNEL) maintains the official archive
of Italian collective agreements. Each deposited CCNL receives a unique alphanumeric
code (e.g. `H011` for the trade and services agreement, `C011` for metals). These
codes are used throughout this library to identify contracts unambiguously.

!!! note
    A small number of instruments that regulate employment conditions are not CNEL-
    registered CCNLs: the *Forze di Polizia ad ordinamento civile* are governed by
    Presidential Decree (DPR 53/2025), not a negotiated agreement.

## Application scope

Each CCNL defines its field of application (*campo di applicazione*): the economic
activities and job functions it covers. An employer whose primary activity falls
within the scope is expected to apply the agreement to all employees performing
covered work.

## Lifecycle

A CCNL typically covers a **three-year period** (*triennio contrattuale*). After
expiry it enters *vacanza contrattuale* — a state of lapse — during which workers
retain the last agreed conditions but no new increases apply. Renewal is triggered
by inflation indicators (typically IPCA, the harmonised Italian consumer price index
net of energy) and by economic conditions in the sector. Salary increases are almost
always split into tranches, each taking effect on a specific date.

## Hierarchy of sources

Italian labor law recognises a layered system:

1. **CCNL nazionale** — the baseline, which sets the floor.
2. **Accordo integrativo territoriale** — a provincial or regional supplement,
   typically used in sectors like construction or agriculture.
3. **Contratto aziendale** — a company-level agreement, which may improve on the
   national CCNL but not worsen it (the *favor prestatoris* principle).

The ccnl-engine models the national CCNL layer (1) and company-level supplements
(3) via [`Employer.second_level_allowances`](../guide/second-level.md).
Territorial supplements (2) are not modelled.

## Next: CCNL components

[CCNL Components →](components.md) explains every building block in detail:
levels, base salary, seniority increments, apprenticeship tracks, INPS contributions,
IRPEF, TFR, and more.
