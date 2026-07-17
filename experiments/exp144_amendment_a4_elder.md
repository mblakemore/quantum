# Exp144 AMENDMENT A4 — conv budget disclosure (Elder, chair-directed C4801)

Amends the frozen prereg (`exp144-preregistration-DRAFT.md`, sha 4d75d190…) §9
BUDGET line. Recorded out loud per freeze discipline — the prereg body is NOT
silently edited; the amendment is disclosed with its measured basis BEFORE the
spend, exactly as A1/A2 were.

## The change

§9 pre-registered conventional-arm budget: **~405 QPU-s → ~535 QPU-s.**

## Basis (all measured / 2-of-2 verified, none assumed)

1. **Fitted cost model, 2-of-2:** `2.64 QPU-s/job (fixed) + 282 µs/shot (marginal)`
   — Elder and Whisper independent fits on the two flown conv waves converge
   number-for-number. (Supersedes the pre-flight ~18k-shots/QPU-s guess, which
   was a single-point extrapolation; the measured per-job fixed cost dominates
   at the small shot counts stage-1 SPRT waves actually use.)
2. **Quota verified 2-of-2:** independent API queries (Whisper C4799, Ember)
   agree — allocation 10,800 QPU-s, consumed 3,188, **7,612 remaining**, window
   2026-07-10 → 2027-07-10. The +130 QPU-s raise = **1.7 % of remaining** — well
   inside headroom.
3. **Creator authorization (verbatim):** "fly when ready" → option (A) authorized;
   **n=6 completes fully.**
4. **Disclosed BEFORE the spend** (this record precedes n=4 wave-3 / n=6 waves).

## Why an amendment and not a drift

The pre-registration discipline holds precisely because a measured budget
overrun is AMENDED OUT LOUD, with its cause and authorization, rather than
quietly absorbed. The ~405 figure was a pre-flight model; the real per-job cost
is measured; the honest number of record is ~535. The n=6 go/no-go had real
headroom against the (corrected) year-window quota, so option (A) stands.

## Sequence unblocked by this + the wave-2 2-of-2 (C4800 R1)

n=4 wave-3 (co-batched on the converged alive lists) → n=4 stage-2 + signs →
n=6 stage-1 waves → n=6 stage-2 + signs → REVEAL grades everything (both
primaries as-flown, both secondaries, scorecard, n=8 unmetered-honest). No
decision points remain except divergence stops.
