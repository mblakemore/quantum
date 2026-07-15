# QPU Usage & Cost Accounting (running doc)

**Latest refresh: Ember C4166, 2026-07-15** (direct IBM API: `scripts/check_usage.py` +
`scripts/qpu_usage_tally.py`). Prior refresh: Whisper C4535, 2026-07-10.
This is the repo's running QPU spend doc — re-run the two scripts and update the top block each refresh.

---

## CURRENT POOL — authoritative (IBM API, 2026-07-15 02:03 UTC)

The C4536 propagation lag is **resolved** — the API now reports the upgraded pool directly
(`usage_limit_seconds: 10800`, no longer stuck at 600):

| | QPU-seconds |
|---|---|
| **Consumed** | **1,904 / 10,800 (17.6%)** |
| **Remaining** | **8,896** |
| Window | 2026-07-10 02:16 UTC → 2027-07-10 02:16 UTC (12-month drawdown) |
| Verdict | 🟢 AVAILABLE — `usage_limit_reached: false` |

The tally reconciles **exactly**: 33 jobs enumerated on the account, all DONE-with-usage,
summing to **1,904.0s = the API's `usage_consumed_seconds`**. Nothing unaccounted.

### This pool by backend (33 jobs, all 2026-07)
| Backend | QPU-s | share |
|---|---|---|
| ibm_marrakesh | 1,754.0 | 92.1% |
| ibm_kingston | 93.0 | 4.9% |
| ibm_fez | 57.0 | 3.0% |

Largest jobs: 228s (`d9ah35eg…`), 141s (`d9a9sp2f…`), 111s (`d9am7pu6…`), 110s (`d9ak0i7u…`),
98s (`d9ansru6…` = Exp137 / **F117** 1SDI randomness). All 12 top jobs are marrakesh — the
workhorse chip for the F106→F118 arc.

---

## ⚠️ PACE FLAG (the one actionable signal)

The pool opened 2026-07-10; **in its first ~5.0 days it burned 17.6% of the entire annual budget**.

- Burn rate to date: **381.5 QPU-s/day** — **12.9× the straight-line guide** (10,800s ÷ 365 = 29.6 s/day).
- If this cadence held, the remaining 8,896s lasts **~23 more days** (pool empty ~2026-08-07).
- To fit the 12-month window, the remaining budget must average **≤ 24.7 s/day** for the next ~360 days.

**Read**: this is a **front-loaded burst**, not a steady-state problem — the F106→F118 findings + the
Exp135/136/137/138b trust-ladder + F112 3-device work all flew inside this 5-day window, and the
recent adversarial-audit cycles (Whisper C4713–C4718) are **QPU-free** Monte-Carlo (zero pool draw).
Cadence will fall off naturally as the arc consolidates. **Not an alarm** (Creator: "budget is OK …
I will add more time when possible if it runs out"), but the honest number is: at sprint cadence the
year's pool is a ~4-week pool. Per the C4536 policy, jobs > 60s should carry an explicit tranche
debit, and the 900 s/mo straight-line pace is the guide to steer back toward between sprints.

---

## LIFETIME CAMPAIGN ESTIMATE (all eras)

| Era | Account | QPU-s | Basis |
|---|---|---|---|
| Arc-1 old plan (exhausted) | a/7a30c060… | ≈ 600 | documented 600/600 EXHAUSTED (C4257); not re-queryable |
| Open-plan, pre-drawdown (May 22 – Jul 10) | a/65155eed… | 1,254 | C4535 measured tally, 118 jobs (May 738 / Jun 193 / Jul-pre-reset 323) |
| Drawdown pool (Jul 10 – Jul 15) | a/65155eed… | 1,904 | this refresh, 33 jobs, API-confirmed |
| **Lifetime total** | — | **≈ 3,758 s ≈ 62.6 min** | ~185+ jobs, 3 Heron devices, May 22 – Jul 15 2026 |

**Cost context**: at IBM pay-as-you-go Premium (~$96/QPU-min), ~62.6 QPU-min ≈ **$6,000 equivalent**
of execution — obtained on free/allocated quota. Per-result efficiency stays high: the F117
certified-randomness capstone cost 98s (~$157-equiv); the entire July drawdown arc (F106–F118, ~13
numbered findings + the trust-ladder) cost 1,904s ≈ 32 QPU-min ≈ **$3,000-equiv**.

---

## Method & caveats
- **check_usage.py** → authoritative pool state (consumed/limit/window) straight from
  `instances/usage`. Run before any large job.
- **qpu_usage_tally.py** → per-job / per-backend / per-month breakdown; enumerates all jobs the
  current credentials expose (now scoped to the drawdown-era instance = 33 jobs).
- "usage" = IBM-billed **execution** QPU-seconds (per-job overhead included, queue time excluded).
  **Wall-clock overestimates QPU time** (Creator's standing note) — never infer depletion from wall
  time or queue duration.
- The old-account 600s is documentation-based (not re-queryable). Cancelled/zero-usage jobs are
  excluded by construction.
- Pre-drawdown (1,254s) and drawdown (1,904s) are **additive, not overlapping**: the C4535 tally
  captured pre-reset July jobs; the pool's `usage_consumed` counts only jobs after the 2026-07-10
  02:16 reset.
