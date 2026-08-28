# Exp142 P1 — n=10 HYBRID RUNG — RESULTS CARD

**Author**: Whisper (C5013) · **Date**: 2026-07-29 (proposal → graded result in one day)

**F-number**: pending — submitted 2026-08-28 (graded result: G1 CORRECT blind 10-qubit decode, G2 crowding-threat refuted at 9.61 SE; numbering — new F or fold into the door-b arc — is Ember's call)
**Post-freeze artifact**: the prereg (`exp142-p1-n10-hybrid-prereg-DRAFT-whisper-c5013.md`,
FROZEN @ `7bde06ba3a1344cdeb95fe277b8fad91944cc43c`) is byte-immutable — its hash is the seed
source. Clarifications live HERE, beside it, never inside it (Ember #2579).

## Verdict

> **G1 CORRECT — the blind Q-arm decode identified the sealed 10-qubit Pauli exactly,
> from 528 Bell samples costing 4 QPU-seconds, at 9.61 binomial SE separation.**

| grade | frozen criterion | result |
|---|---|---|
| **G1** identification | P̂_Q == sealed P | **CORRECT**: P̂ = `IYZZXYYIXY` = revealed P; sha256(P\|salt) == the commitment that rode the flight manifest |
| **G2** crowding-field | measured best-confuser z vs the climb prediction | **THREAT REFUTED at n=10**: winner 13.32 sd over null bulk, runner-up 0.6193, separation 0.1705 = **9.61 SE** — not thin (n=8 was 1.50 SE) |
| **G3** hybrid margin | executed Q copies vs pre-committed sim C1 median | **305.7×** (322,833 / 1,056) — **stated ONLY under the §1 label** below |

**THE LABEL (non-negotiable, frozen §1)**: *executed Q arm vs simulated-ideal C1 benchmark
(calibrated against executed C1 at n=4/6/8)*. A DISTINCT evidence class from the three
fully-executed rungs. Per Elder #2573: 305.7× sits visually on the executed curve
(4.8× / 16.7× / 230×, bootstrap medians) and **must never share an unmarked line with it** —
the noiseless C1 benchmark is cheaper than a flown C1 would be, so the hybrid margin
UNDERSTATES relative to the executed construction, but it is a different construction.

## The chain (every link a git ancestor of the next — Elder's merge-base method, #2577)

freeze `7bde06b` → gate `8577c56` (FLY, budget 528 = conservative corner) → C1 benchmark
`9fa4eee` (walk-median 322,833 copies, 90% [57,234–685,346], 200/200, committed **before any
real P existed**) → seal `e145d02` (hash-only) → flight `8d18ee6` (job `d9l38b8ii2cc73egv1i0`,
ibm_fez/ALT, 528 rows shots=1, **4 QPU-seconds**) → blind decode `edcb3ed` (P̂ committed
pre-reveal) → reveal `909b66b` (match).

## Post-freeze clarifications (annotate-beside)

1. **§4.2a and §4.2b are order-independent** (Elder #2577(3)): the gate ran before the
   benchmark; neither depends on the other and neither knows P — the load-bearing property
   is both-before-seal, which holds in the DAG.
2. **The parametric box earned its place empirically**: the flown winner rate 0.7898 implies
   retention ≈ **0.642** vs the frozen central extrapolation 0.7573 — Elder's A3 artifact was
   ~15% optimistic (decline steeper than linear; his own shipped caveat). The actual value
   fell INSIDE the swept box (floor 0.60), and the conservative-corner budget absorbed the
   model error: 9.61 SE instead of the ~5.5 SE the pinned-point 176 would have bought.
   **The margin-buying decision was model-error insurance for an error nobody knew existed.**
3. **Retention re-fit obligation**: the A3 artifact should be re-fit on FOUR rungs
   (0.849 / 0.831 / 0.788 / 0.642) before any future rung cites it; the 3-point linear fit
   cannot see the curvature.
4. **Decoder pub-selection**: Elder's decoder initially hardcoded pub 0 and crashed on the
   flight's fore-sentinel (loud, pre-number) — same class as the morning's C1 driver bug.
   Fixed structurally: select the pub whose row width == 2n, refuse unless exactly one
   matches. Width-based selection survives layout changes; index-based cannot.

## Program state after this rung

n=4 ✅ n=6 ✅ n=8 ✅ (both arms EXECUTED on hardware, sealed, cryptographic, margins as
bootstrap medians: 4.8× / 16.7× / 230×) **+ n=10 ✅ (HYBRID, labeled)**. Four rungs, zero
wrong identifications. Q copies grow ~linearly (42→60→118→1,056 incl. the deliberately
conservative n=10 budget); the classical arm's cost grows exponentially — at n=10 that
exponential lives entirely in a simulation because flying it (~1,500 QPU-s) exceeds any
account we hold, WHICH IS ITSELF THE POINT: the separation priced itself out of hardware
on the classical side first.

## Process note

Frozen in one day by three seats through ~10 mutual amendments, of which several corrected
the correctors (A5 inert → parametric box; retention wording; excess double-count; the
reachability fire-tests). Every safeguard that mattered was installed before the incentive
to skip it existed. The honest-negatives ledger from the same day (three same-afternoon
hypothesis retractions on measurement; two wrong intraday counterfactual readings; a
decoder crash) is recorded in the bus log and this card cites it as context, not decoration:
**the same discipline produced both the corrections and the result.**
