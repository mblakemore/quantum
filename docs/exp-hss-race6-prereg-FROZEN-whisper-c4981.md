# Exp-HSS Race 6 — PRE-REGISTRATION **FROZEN** (2026-07-23) — three fences

**FREEZE RECORD**: Creator go (general#655, "Go 6"). Ember 2 seals quantum@7e23d35 (#657:
rung0_n40 71b8378d…, race_n40 e3839fc5…; GREEN on all three fences + seal-preservation
mechanics stated: reveal on ladder-exact, retire unopened on ladder-fail). Elder ACK #658
(faithful implementation; register unification called "the deepest fix in the card" — makes
the pre-gate certify the race register AND ρ_t a genuine clean point; RESIDUAL RISK NAMED:
8-qubit exclusion may push min-d2q past cap 200 → cap-miss = live pre-registered branch (b),
a device-limitation finding not a design flaw). This commit is the freeze.**

**POST-FREEZE AMENDMENT (3-of-3, pre-submission)**: the rule-1 abort FIRED on marrakesh —
ZERO clean n40 routings in 100 seeds with the 8-qubit targeted exclusion (device-limitation
finding, stronger than the #658 named cap-miss risk). Amendment (Ember #661 GREEN, Elder #662
CONCUR): **fly the same frozen card on the best-queue alternate die (kingston) with
EXCLUDED = {}** — sound and not a race-5 regression because race-6 HAS the clean-ladder
pre-gate + seal preservation (race-5's mistake was grading a dirty register WITHOUT one); on
an unmapped die the pre-gate IS the empirical register-quality filter, at zero seal cost.
Ember's seals carry over UNCHANGED (same card, same commitments, still blind; no re-seal).
Die-change grading reminder (Ember): the quantum wall is re-measured on the die actually
flown; Elder's classical band is die-independent. No other change.**

*Whisper C4981, 2026-07-23, substrate claude-fable-5. Creator directive (general#655): "Go 6."
Design court-converged in the race-5 record (Ember #649/#651, Elder #652). Court: same 3-of-3.
Freeze = commit with DRAFT removed after Ember's 2 fresh seals + Elder ACK.*

## The three fences (each individually evidence-backed by races 4–5)

1. **MINIMAL-TARGETED EXCLUSION (frozen)**: EXCLUDED = {67, 113, 114, 115, 119, 133, 134, 135}
   — the qubits calibration fundamentally cannot fix: near-stuck (113), circuit-level-bad
   (114, 115 — the race-5 discovery: fail at depth, NO readout signature), and the
   measured-bad set. Tilted-but-correctable qubits (68, 73, 78, 4, 69-class) stay IN — the cal
   block handles them (race-4-validated) and depth stays low (Elder #652 refinement). Clean
   filter applies to ALL blocks; rule-1 abort if any block has zero clean candidates.
2. **CAL BLOCK + CALIBRATED MAJORITY (unchanged, race-4-validated)**: whole-chip all-0/all-1
   cal; graded statistic = calibrated per-bit majority (t_i = (p01_i+1−p10_i)/2, atomic 2⁻⁴⁰
   null, Chase/soft diagnostics only, no rescue).
3. **CLEAN-LADDER PRE-GATE (Ember #651, Elder-adopted #652 — the race-5 lesson)**: the grade
   fires ONLY if BOTH ladder rungs (t=0, classically free) decode s EXACTLY at stage-1.
   **Abort-not-grade**: if the ladder is not exact, the race rung is NEVER decoded and its
   seal is RETIRED UNOPENED — a dirty register cannot consume a graded seal. This is the only
   guard that catches circuit-level-bad qubits (proven: it caught {113,114,115,119} at HD-4).

## Register unification (the race-5 structural fix)

Race-5's ladder/twin/race rode THREE different registers, making the guards guard the wrong
qubits. Race-6 unifies: the twin's t=0 source is transpiled with **initial_layout = the race's
FINAL routed layout**, candidates filtered clean, and the chosen candidate must have final-
layout overlap ≥ 30/40 with the race's final register (overlap reported in the manifest;
abort if unmet). **The LADDER = m ∈ {0,1} folds of that same twin source** — so ladder, twin,
and (approximately) race certify the SAME physical qubits, and the pre-gate actually guards
the register the race reads out on.

## The job (~58 pubs, 360k shots ≈ 105–115 s of ~2,531 s pool)

| Block | Structure | Shots |
|---|---|---|
| READOUT-CAL | all-0 + all-1, measure_all | 20k |
| LADDER | m ∈ {0,1} of the twin source (race-register), 4 twirls × 5k | 40k |
| TWIN n=40 | twin source padded to d2q_race exactly, 16 twirls × 6,250 | 100k |
| RACE n=40 | t=80, 32 twirls × 6,250 | 200k |

Race transpile: clean best-of-100 (min d2q among EXCLUDED-avoiding candidates). **Cap 200**
(unchanged; demonstrated boundary ≥217). Marrakesh default (standing rule). Seals: Ember, 2
fresh strings (rung0_n40 for ladder+twin, race_n40), hardened 0-indexed format.

## Frozen decision rules

1. **CAP**: advantage-eligible iff clean best-of-100 d2q ≤ 200. Rule-1 abort if no clean
   candidate.
2. **PRE-GATE (stage-1, adjudicated first)**: both ladder rungs exact ⇒ proceed; else ABORT —
   race seal retired unopened, deliverable = the register-quality card for this routing.
3. **GATE**: twin decodes EXACTLY (calibrated majority, full 100k).
4. **WIN (unchanged)**: exact ŝ==s on race_n40 + re-measured quantum wall (smallest
   exactly-decoding subsample of {2,4,8,16,32} pubs; cal block excluded per-circuit, Elder
   #605) ≤ 1/10 of Elder's frozen t=80 band lower edge at EVERY edge (binding 181.8 s).
   Supersedable-by-design printed.
5. **Path A**: ρ_t(d2q_race) with 1k-pub bootstrap — candidate second CLEAN point if the
   pre-gate passes (the #630 requirement).
6. **Named failure modes**: (a) pre-gate abort (register card deliverable, seal preserved-
   retired); (b) cap miss (Path A only); (c) twin fold (Path B ungraded); (d) genuine
   magic-layer bit on the race (race-4 pos-38 class ⇒ MISS booked, attribution via cal +
   ladder being clean); (e) stuck/circuit-bad qubit evading all three fences ⇒ MISS with the
   full localization playbook. No rescue anywhere.

## Fences

As the race-5 card (best-known-simulator race, not a theorem; t=0 free; prior verdicts stand;
prior reveals resolved/retired; WIN stated with its fences: one instance family, one die,
Elder's C6563 edge-robust band, joules one-sided). QPU after ≈ 2,415–2,425 s; no further HSS
spend without a fresh card. *Contact: Mike Blakemore.*
