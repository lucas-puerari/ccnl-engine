# /goal — Obiettivo multi-sessione: aggiungi N nuovi CCNL al repo

Questo progetto usa un sistema di goal basato su git history, non sulla valutazione LLM del `/goal` built-in.

Un Stop hook project-local conta i commit `feat(...): add CCNL ...` su main dopo ogni turno.
Il goal è raggiunto quando ne esistono abbastanza in più rispetto al baseline.
Lo stato persiste in `.claude/GOAL.md` (locale, non committato) — funziona tra sessioni diverse.

---

## Imposta un nuovo goal

Se l'utente ha specificato quanti contratti aggiungere (es. `/goal 5`):

1. Conta il baseline attuale (fonte di verità: file JSON dei contratti):
   ```bash
   ls src/ccnl_engine/contracts/data/*.json | grep -v '__init__' | wc -l
   ```

2. Crea `.claude/GOAL.md`:
   ```markdown
   ---
   status: active
   baseline: <numero contato al punto 1>
   target: <N richiesto dall'utente>
   created: <data ISO>
   ---

   Aggiungi <N> nuovi CCNL al repo seguendo il processo in `.claude/commands/new-contract.md`.

   Ogni contratto deve:
   - Essere mergiato su main tramite PR
   - Avere un commit con formato: `feat(<slug>): add CCNL <nome> (<codice>) payroll engine`
   - Comparire in `git log main --oneline`

   Procedi in ordine, un contratto alla volta. Scegli quelli con il maggior numero di lavoratori coperti non ancora presenti nel repo.
   ```

3. Inizia subito a lavorare seguendo `/new-contract`.

---

## Mostra stato (nessun argomento)

Leggi `.claude/GOAL.md` e mostra:
- `status`, `baseline`, `target`
- Conteggio corrente: `git log main --oneline | grep -c "feat(.*): add CCNL"`
- Quanti aggiunti e quanti mancano

---

## Cancella goal (`/goal clear`)

Aggiorna `status: cancelled` in `.claude/GOAL.md`.

---

## Vincoli

- Non creare un commit esplicito "goal done" — il completamento è rilevato automaticamente dallo Stop hook contando i feat commit.
- Non dichiarare il goal completato finché `git log main` non mostra i commit attesi.
- Usa sempre `/new-contract` per aggiungere ogni singolo CCNL.
