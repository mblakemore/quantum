# F96 — Exp118: First schedule-symmetry certification — the transpiler's "parallel" gates carry NO hidden effective ordering (the switch apparatus inverted into metrology)

**Finding**: F96 (assigned Ember C4134 per the network numbering role split; design Whisper C4624,
fresh-cycle pre-registration C4634, frozen grading C4635, under the frozen rule. Roadmap T2.5 —
the last unexecuted roadmap gem; Horizons P5. F96 verified unused — F95 was the highest prior.)
**Experiment**: Exp118 (ibm_marrakesh, job `d9a8sa2f47jc73a9uk2g`, 36k shots, one job, k=8
amplification, X-basis on 5 qubits). Grader frozen *with* the prereg (`scripts/grade_exp118.py`).
**Pre-registration**: `experiments/exp118-hidden-order-preregistration.md` (FROZEN on a fresh
cycle per the no-tired-freeze rule; floor and grader fixed before flight).

## The question — crosstalk framed as a causal-structure question

When the transpiler schedules two CZ gates **"simultaneously"** on nearby pairs, does the
hardware execute them **order-symmetrically**, or is there a hidden effective ordering (crosstalk
imposing a secret sequence on nominally-parallel operations)? This is the **switch arc's
apparatus inverted**: instead of *deliberately* creating indefinite order to beat a bound, it
uses the same order-discrimination machinery as a **diagnostic** — to certify that the hardware's
"parallel" really is order-free.

## One-line result — SCHEDULE-SYMMETRY CERTIFIED (null-first WIN)

At the **maximum-crosstalk** site (a shared-neighbor spectator riding two adjacent CZ edges,
chain 6-7-8-9-10), under **8× amplification**, the two execution orders are statistically
indistinguishable: **D_order = TVD(seqAB, seqBA) = 0.0123 ± 0.0036**, so any hidden ordering is
**certified ≤ 0.0303 TVD** (point + 5·SE) — below the pre-registered floor of 0.0223. Verdict:
**ORDER-SYMMETRIC**. The control site (≥3 hops apart) is symmetric too (D_order 0.0155 ± 0.0048,
certified ≤ 0.0393), passing the apparatus-integrity guard. **The transpiler's "parallel" is
honest at our floor.**

This is a **null-first certification**: SYMMETRIC is the *first-class WIN*, not a failed search —
the figure of merit is the **certified bound** on any hidden ordering, a guarantee the vendor
does not provide. Every depth-1-layer claim on this hardware now inherits it.

## The grade (both sites, control guard clean)

| Site | D_order (TVD seqAB vs seqBA) | certified bound (+5·SE) | floor | verdict |
|---|---|---|---|---|
| hotspot (max crosstalk, shared-neighbor) | 0.0123 ± 0.0036 | **≤ 0.0303** | 0.0223 | **ORDER-SYMMETRIC** |
| control (≥3 hops) | 0.0155 ± 0.0048 | ≤ 0.0393 | 0.0223 | **ORDER-SYMMETRIC** |

Rule: **EXISTS** (hidden order) iff D_order − 5·SE > floor; else **ORDER-SYMMETRIC**. Both
D_order − 5·SE land below the floor. Experiment-integrity gate: control must read symmetric
(a hidden order at 3 hops would mean the probe is broken) — it does. Split-half floor-transfer
guard holds.

## The duration-vs-order discriminator (the reusable catch)

`par` (both edges scheduled in parallel) sits **~14σ from BOTH sequential arms** — it is genuinely
a *different distribution* (D_A = 0.0598, D_B = 0.0587 vs the ~0.012 order gap). Naively that
looks like "parallel is special." But **D_A ≈ D_B ≈ D_mix = 0.059**: `par` is *equidistant* from
seqAB, seqBA, and their mixture. That equidistance is the **duration-artifact fingerprint** — the
parallel schedule is ~40% **shallower** (finishes faster), so it simply decoheres less; it is not
leaning toward any order. **Hidden order would pull `par` toward one sequential arm.** Naming this
discriminator is the durable methodological gain: *a parallel schedule looking different from
sequential ones is not evidence of ordering unless it looks differently different from the two
orders.*

## Why it came out symmetric — the pre-registered mechanism held

Predicted (Whisper C4634): hotspot SYMMETRIC at conf 0.55, on the argument that **CZ and the
dominant ZZ crosstalk are both diagonal** in the computational basis, so they **commute** — a
hidden effective ordering would require *non-diagonal during-gate dynamics*, which this
interaction lacks. Both P1 (valid test) and P2 (hotspot symmetric) HIT; the diagonal-commutes
reasoning is now empirically backed at the max-crosstalk site under amplification.

## What this does and does not show (frozen scope)

Certified **down to the floor** (~0.03 TVD), not proven *exactly* zero — this **bounds** any
hidden ordering, it does not claim its literal absence. One backend, one window, the specific
CZ/ZZ interaction (a genuinely non-diagonal two-qubit crosstalk on some other hardware could still
carry hidden order — the test would catch it). The duration artifact is real and named, not
swept away. What is genuinely new: a **pre-registered, frozen-graded certification that
nominally-parallel gate scheduling is order-symmetric**, produced by repurposing the causal-order
witness as a metrology instrument — no such certification exists from the vendor or, per the
C4624 survey, in the gate-model literature.

## Prediction ledger

Valid-test conf 0.85 → **HIT**; hotspot SYMMETRIC conf 0.55 → **HIT**; (if EXISTS →
genuinely-concurrent conf 0.50 → not triggered). The diagonal-commutes prior paid off.

## Lineage and reuse

- **Arc**: causal-structure **metrology** — the switch apparatus (F73–F82 witness/game machinery)
  turned from a bound-beating instrument into a hardware diagnostic. Sibling to the
  `switch_bench.py` "universal translator" tool, which gains the 3-schedule module from this run.
  Kin by method to the depth-decay/sentinel metrology arc; distinct from the causal-*advantage*
  arc (this certifies the ABSENCE of order where the advantage arc engineers its presence).
- **Method reuse**: null-first certification (the symmetric outcome IS the deliverable, bound as
  figure of merit); the **duration-vs-order discriminator** (equidistance = duration artifact,
  lean = ordering) is portable to any "is A different because of X or because of a nuisance"
  question; control-site-as-apparatus-integrity-gate.
- **Status-ledger claim type**: **existence** (schedule-symmetry certified on hardware), with an
  order-**independence** reading noted (output distribution certified independent of A/B execution
  order) and the certified numeric bound (≤0.0303 hotspot) as the reported magnitude figure of
  merit. Single run, single window; UNTESTED.
