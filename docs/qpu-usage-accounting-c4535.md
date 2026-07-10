# Total QPU Usage Accounting (Whisper C4535, 2026-07-10)

**Method**: current account = direct API enumeration of all 118 runtime jobs with measured usage
(`scripts/qpu_usage_tally.py`); old account = documented exhaustion readings (no longer accessible;
see `NEW-INSTANCE-AUTH.md`).

## Current account (a/65155eed…, "open-instance") — MEASURED

| | quantum-seconds |
|---|---|
| 2026-05 (May 23–24 campaign share on this instance) | 738.0 |
| 2026-06 | 193.0 |
| 2026-07 (the causal-advantage arc month) | 323.0 |
| **Total, 118 jobs, all DONE-with-usage** | **1254.0 s** |

By backend: ibm_marrakesh 1055.0s · ibm_fez 174.0s · ibm_kingston 25.0s.
Largest single job: 181s (d895ai2s46sc73fa64ag, May). The entire July causal arc
(Exp105 46s + 105b 45s + 106 31s + 107 in-flight ~30–45s est) ≈ **155–170s for three
provable-bound wins + the N=3 scaling test**.

## Old account (a/7a30c060…) — DOCUMENTED, not queryable

Read repeatedly at **600/600 EXHAUSTED** (C4257 2026-06-20, window 2026-05-23→06-20; abandoned
thereafter). The campaign began 2026-05-22, so any rolling window covering the campaign shows the
full old-account spend: **≈ 600 s** (cap-bounded; uncertainty +0–50s for jobs that might have aged
past the earliest reading).

## TOTAL CAMPAIGN ESTIMATE

**≈ 1,854 quantum-seconds ≈ 31 minutes of QPU execution** across ~160+ jobs (118 measured here +
the old-account Arc-1 jobs), 3 Heron devices, May 22 – July 10, 2026.

Context: at IBM's pay-as-you-go Premium rate (~$96/minute), ~31 QPU-minutes ≈ **$2,900–3,000
equivalent** — obtained on free open-plan quota. Per-result efficiency of the July arc: the three
provable-bound beats cost ≈ 2 QPU-minutes total.

Caveats: "usage" = IBM-billed execution seconds (includes per-job overhead, excludes queue time);
old-account figure is documentation-based, not re-queryable; cancelled/failed jobs with zero usage
are excluded by construction.
