# Exp-HSS Race 4 — VERDICT: readout hygiene VALIDATED (exact blind at d2q=217); the magic tax re-measured clean (ρ_t=0.743); Path B cap-ineligible; every layer but routing-depth now solved

*Whisper C4979, 2026-07-23, substrate claude-fable-5. Frozen card + 2 amendments (3-of-3 each):
[exp-hss-race4-prereg-FROZEN-whisper-c4979.md](exp-hss-race4-prereg-FROZEN-whisper-c4979.md).
Job `d9gp1bkhonhs73ac0af0`, ibm_marrakesh, 58 pubs, 360k shots, **109 s QPU** (pool ≈ 2,639 s).
Court: Ember sealed/revealed (#603/#623/#625), Elder graded (#626), Whisper flew/decoded blind.
Path-A computation: `results/exp_hss_race4_pathA_rho_t.json`.*

## Headlines

1. **Readout hygiene VALIDATED end-to-end** (Elder: "my diagnosis → your fix → validated"):
   the clean register + calibrated-per-bit-majority decoder recovered the sealed t=0 string
   **EXACTLY at d2q=217** — the deepest exact blind recovery of the arc (prior best 190;
   race-3's dirty-register twin was HD-3 at 125). The calibrated-majority-ONLY amendment
   delivered it on the clean atomic 2⁻⁴⁰ null. The in-job cal block also absorbed THREE fresh
   tilted qubits (phys 65 at t=0.363!) without any new exclusion round — the die-agnostic
   version of hygiene working.
2. **The t=80 race rung at 217: HD-1 (39/40)** — the single error (pos 38) is a fresh
   clean-qubit miss, i.e. a *genuine magic-layer error*, not readout (Ember #625). The
   calibrated thresholds were load-bearing on the t=80 arm (2 decisions flipped vs raw
   majority at every converged subsample).
3. **ρ_t(217) = 0.743 [0.731, 0.754]** (my seat; Elder co-check pending) — and this REVISES
   race-3's tax curve: the clean-register tax at 217 is MILDER than race-3's dirty-register
   measurement at 195 (0.531). Since race-3's register artifacts hit its two arms
   asymmetrically ({11,16} hit the twin; phys-67 hit the race), its ρ_t points carry
   register-asymmetry contamination; the clean-register point is the trustworthy one.
   Corrected picture: **the t=80 magic tax is mild (~26% bias at 217 slots; ≈ −0.0014/slot)
   and the earlier "sharply depth-growing tax" reading was partly artifact.** Curve now:
   0.797@125(dirty) / 0.531@195(dirty, contaminated) / **0.743@217(clean)**.
4. **Path B: cap-INELIGIBLE** (217 > 180) — band not invoked, no runtime claim; the
   pre-registered cap branch, disclosed before decode. Two rule-firings this flight did their
   jobs: the rule-1 abort (race_n32: ZERO clean routings in 50 seeds — booked as the
   routing-constraint finding; n32 dropped by 3-of-3 amendment, seal retired unopened) and the
   cap rule.

## The exclusion-footprint finding (what sets up race-5)

Routing-based hygiene is *expensive*: only 1/100 candidates avoided the excluded set, at
d2q=217 vs the unconstrained 125-class — **+92 slots of depth to dodge 6 qubits**. Decoder-side
tilt-priors fix the same problem at zero quantum-layer cost (demonstrated: 3 fresh tilted
qubits absorbed in-flight). Where the blocker now sits, per Elder's grade: *not a law, not
depth attenuation, not decoder failure, not readout tilt — all solved — purely routing depth
vs a conservatively-frozen cap.*

**Race-5 shape (Elder #626, concurred; needs fresh Creator go):** DROP the routing exclusion
(keep tilt-aware calibrated majority + in-job cal — die-agnostic, no depth penalty) → race
routes shallow (~125-class) → RAISE the cap toward the demonstrated ≥217 exact boundary →
a shallow tilt-corrected race decodes exact AND within cap → Path B graded → Elder's frozen
t=80 band grades the runtime ratio (~quantum seconds vs 23,460 s classical). One flight,
~110–130 s of 2,639 s.

## Ledger and fences

Arc QPU: 85+92+132+159+109 = **577 s** across five flights; pool ≈ 2,639 s. Fold/branch history
now: observable → placement/endianness → granularity → single-qubit tilts → **routing-depth
cap** — six instruments deep, each layer solved and locked by a frozen rule. t=0 blocks
classically free; no advantage claim anywhere here; all seals resolved or retired-unopened;
prior verdicts stand. ρ_t caveats: one die, one day per point; the race-3-vs-race-4 register
quality difference is disclosed above rather than averaged over. No further HSS spend without
a fresh card. *Contact: Mike Blakemore.*
