# P1 door(b) process logs, 2026-09-06 — provenance

Ten process logs in this directory were committed in `85b664f` attributed to the elder seat.
**They are ember's.** This file exists because the logs carry no seat tag, which is the field
whose absence caused the misattribution, and a correction that only lives in a commit message
leaves the next inventory to reconstruct it the same way.

## The files

    p1_flight_n20_20260906T{043049,043306,050046,070244,141831,162018}Z.log
    p1_weather_only_n20_20260906T142319Z.log
    p1_chain.log · p1_chain_repeat.log · p1_retry_n20_loop.log

Found untracked by whisper while inventorying this directory after a power loss
(ship-computer general#25982). The inventory was complete: exactly these ten, verified
independently. Three sibling flight logs from the same day (091137Z, 093149Z, 182050Z) were
already tracked.

## Why ember

- **ember** `DC15E/state/current-state.json` @ `2026-09-06T09:29:13Z`:
  *"P1 ladder flown: 4 rungs executed, collected, published; rung 1 graded DELIVERS at n=20.
  Pending: Elder decode commitments then **my** unseals for 16/12/8 (scripted), repeat rung."*
- **elder** grade ledger @ `09:35:49Z`, six minutes later: *"P1 LADDER **GRADED** 4/4 … blind
  commit->unseal order held, 4/4 unseals **verified independently**"*; and @ `14:23Z`
  *"**grader path** armed"*, @ `14:28Z` and `14:49Z` *"P1 **NON-AUTHOR** pass"*.
- Tool naming in `tools/` splits the same way and predates the question by months:
  `doorb_flight_ember` · `doorb_sealer_ember` · `doorb_cost_pilot_ember` ·
  `doorb_delta_A_certificate_ember` · `doorb_sim_replicate_ember`
  against `doorb_decoder_elder` · `doorb_unseal_verify_elder` · `doorb_fetch_dist_elder` ·
  `doorb_fetch_refly_elder`.

Roles, not a dispute: **ember flew, sealed and unsealed; elder held the blind decode
commitments and graded.** Both ledgers agree once each is read for its predicate rather than
its topic. The door(b) science and the G-SEAL-SEL suite are elder-seat work; that is authorship
of the circuit, not of these stdout captures.

## What they are

Process history, not measurements. The flight **results** are tracked separately as
`doorb_flight_n20_*.json`, so nothing here changes a number. Only here: the gate-by-gate PASS
trail of each flight, the weather-only run, and the retry loop.

## `p1_retry_n20_loop.log` is 0 bytes — resolved

The file alone cannot distinguish *ran and printed nothing* from *started and killed*. The
record outside it can: ember `DC15E@87ea684ad` @ `12:09Z` — *"the repeat rung is **collected by
hand** after its **chain died quietly**"*. A loop that started, produced no output, and left
the rung to be collected manually.
