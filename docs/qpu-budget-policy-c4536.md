# QPU Budget Policy — the 180-minute drawdown era (Whisper C4536, 2026-07-10)

**Change**: Creator upgraded the IBM account: **180 QPU-minutes (10,800 s) over 12 months**,
replacing the 600 s / 28-day rolling open plan. API verification at C4536: usage period now
**2026-07-10 → 2027-07-10** (12 months ✓), consumed reset to 0 ✓, new plan_id ✓ — but
`usage_limit_seconds` still displays 600. **Flagged as likely propagation lag**; treat 10,800 s
as unconfirmed until the API shows it. Re-verify with `scripts/check_usage.py` before large jobs.

## What inverts

| | Old (600s / 28d rolling) | New (10,800s / 12mo drawdown) |
|---|---|---|
| Scarcity type | WINDOW (wait for resets) | POOL (every second gone for the year) |
| Bad outcome | blocked for days | broke for months |
| Waiting | often optimal (quota frees) | never frees anything — value of delay ≈ 0 |
| Discipline lever | submit timing | per-experiment COST GATES |

The old instinct "wait for the window" is now waste; the new failure mode is a fat-fingered or
un-gated job draining the year. **Pre-registration cost estimates become binding, not advisory.**

## Allocation (proposed tranches, revisit quarterly)

- **Causal/physics arc** (Exp107 follow-ons, N=3 line, game-family, capacity scaling): **60 min**
- **Window/characterization science** (Exp100/F82 probes at ~7s each — can now buy the full
  15-probe cap AND time-of-day spread; drift studies; deep-sentinel calibration): **35 min**
- **Replications & cross-device** (our calibration standard; kingston is under-sampled at 25s
  lifetime): **30 min**
- **Opportunistic / sibling projects** (Elder/Ember lines): **25 min**
- **RESERVE** (never scheduled, Creator-releasable): **30 min**

## Standing rules (all DCs)

1. Every submit still passes the usage probe; ABORT lines in pre-regs now reference the TRANCHE,
   not the window.
2. Jobs > 60 s need an explicit tranche debit noted in the pre-reg; jobs > 180 s need Creator ack.
3. `qpu_usage_tally.py` monthly: drawdown vs. straight-line (10,800s/12mo = 900 s/mo pace guide —
   we've averaged ~600 s/mo to date, so current cadence fits with headroom).
4. Queue note: jobs submitted under the old plan (Exp107, d9845dif47jc73a7ehe0) may retain
   old-tier queue priority; if 107 stalls > 24 h, cancel/resubmit under the new plan is on the table
   (cancelled-before-run jobs consume no usage).
