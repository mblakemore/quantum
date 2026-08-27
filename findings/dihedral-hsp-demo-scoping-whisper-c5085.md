# Dihedral-HSP hardware demo — $0 scoping (Whisper C5085)

Creator asked: could our quantum-learning rails support a non-abelian (dihedral) HSP testbed, and what could it honestly claim? $0 pass, no QPU spend.

## What HSP piece this is
Dihedral HSP over D_N ≡ the HIDDEN SHIFT problem (find s∈Z_N). After the abelian Fourier step each oracle
sample is a COSET (phase) state |ψ_k⟩ = (|0⟩ + ω^{ks}|1⟩)/√2, ω=e^{2πi/N}, k KNOWN, s HIDDEN. Kuperberg's
SIEVE combines pairs of these (CNOT + herald) to manufacture states with useful k (e.g. k=N/2, which reads
a bit of s), in 2^O(√log N) — subexponential, NOT polynomial.

## What I built and verified ($0, Aer)
Minimal N=8 demo: prepare |ψ_1⟩,|ψ_3⟩ (hidden s), CNOT, herald target=0 → control=|ψ_4⟩=|0⟩+(-1)^s|1⟩,
X-read = s mod 2. RESULT: all 8 hidden shifts recover s mod 2 correctly, ~50% herald-keep (as the
combination predicts). Cost per sieve step: 2 qubits, 1 CX, depth 5. The sieve used only known k + the
coset states, never s — it genuinely LEARNS the shift.

## Full-demo scope (still $0 → then a small fly)
- N=8 all 3 bits: recurse the sieve to k=2,k=1 (a few more steps, still tiny).
- N=16/32 to show the sieve SCALING (more phase states + rounds; Kuperberg needs ~2^√n states).
- from_backend noise validation: the sensitive parts are (a) PHASE precision of the ω^{ks} rotation —
  fine for small N (coarse phases ~π), degrades as N grows and phases get fine; (b) the herald MCM (cheap,
  same primitive as the counterflow dephasing); (c) multiplicative shot-loss (~50%/combination bounds N).
- Hardware fly if it survives sim: SMALL — a phase state is 1 qubit, a sieve step 2 qubits + 1 CX + 1 MCM;
  width bounded by reset-reuse. Estimate ~10–20 QPU-s, like the counterflow flights.

## What it CAN honestly claim
A LABELED ENGINEERING DEMONSTRATION (Flight-A frame): the dihedral-HSP procedure — coset-state prep +
Kuperberg sieve — realized on IBM hardware, recovering the hidden shift for small N, graded by hardware
survival. The NON-ABELIAN coset counterpart to F113's abelian 2D-HLF coset solver. A capability result.

## What it CANNOT claim (the fences — and F121 is why)
- NOT a quantum advantage. Small-N brute force is classically trivial (N=8: instant). ZERO advantage claim
  possible — which is GOOD: it removes the attack surface AND the planted-structure-leak trap that RETIRED
  F121 (our own hidden-shift "advantage" fell to a 41-query classical solve). No advantage claimed → all
  attack_preflight advantage classes N/A, exactly like Flight A.
- NOT progress on the OPEN problem. Kuperberg is subexponential; a small instance says NOTHING about hard
  scaling, and NOTHING about breaking lattice crypto. It is the KNOWN algorithm on a TINY instance.
- The honesty IS the point: we demonstrate the machinery runs on qubits; we do not pretend to have solved
  non-abelian HSP.

## Recommendation
Feasible, cheap, clean. Worth a $0-first build (full N=8 + N=16 + from_backend) as a labeled capability
demo on our existing rails (coset prep, MCM/herald, sealed-blind adjudication, attack-preflight). Fly only
if the sim survives noise, and fence it from the first line: engineering demonstration, no advantage, no
scaling/crypto implication. The value is a clean non-abelian-HSP instrument in the portfolio — not a claim.

---
## BUILD RESULTS ($0, C5085 — Creator "go ahead with the $0-first build") — GO for a small fly

Script: `experiments/dihedral_hsp_demo_whisper_c5085.py`. Full recovery (all bits, using the
RECOVERED lower bits for each phase correction = error-propagating, the honest metric).

- **IDEAL SIM**: N=8 full-string **8/8 exact**, N=16 **16/16 exact** (per-bit 100%).
- **NOISY — EXACT `ibm_fez` noise model** (`NoiseModel.from_backend`, verified non-empty:
  cz/sx/measure/reset errors): N=8 **8/8 exact**, N=16 **16/16 exact** (per-bit 100%).
- **Cost**: per-bit circuit = **1 two-qubit gate, depth 6** for BOTH N=8 and N=16 (small-N sieve
  is ONE combination round regardless of N). A full shift = n such circuits (n=3 for N=8, 4 for N=16).
- **The noise IS biting, verified**: fine-phase worst cases (N=16, high bits) the majority vote
  drops 1.0000 (ideal) → **0.959–0.974** (noisy) — real degradation, but ~0.46 clear of the 0.5
  threshold, so recovery is exact. Herald-keep ~50%/round as the combination predicts.

### Why it survives — stated honestly (this is the fence, not a boast)
Robustness comes from TWO things, neither of which is "beating deep noise":
1. **Shallow circuit** — small N needs 1 sieve round (1 CX). No feed-forward even needed: read the
   herald + the bit both terminally, post-select the herald in classical post-processing.
2. **Majority-vote observable** — each bit is a vote over 20k shots (the F120 shot-axis redundancy).
This is EXACTLY why small N is flyable and large N is not: larger N needs more sieve rounds (deeper +
multiplicative ~50%/round herald loss + finer phases), which is where it would break. The demo does
not claim otherwise.

### GO / NO-GO on a small fly: **GO (small, fenced)**
- FOR: machinery recovers s exactly on N=8 AND N=16 under the EXACT device noise model; circuits are
  tiny (1 CX, depth 6/bit); free open-instance `ibm_fez` (#151 gate), ~10-20 QPU-s. Hardware is the
  campaign's truth standard — a noise MODEL missed the localized q142 high-population error in the
  coflow caveat, so a real fly is the honest confirmation a model can't give.
- SCOPE (unchanged): labeled ENGINEERING demonstration — the non-abelian coset counterpart to F113's
  abelian 2D-HLF solver. NO advantage (small-N brute force is trivial → all attack_preflight advantage
  classes N/A, like Flight A). NO scaling / NO crypto claim. Graded solely by hardware recovery of s.
- NEXT STEP if you say fly: freeze a pre-registration + run attack_preflight + submit ONE job to
  `ibm_fez` under a Creator GO citing the frozen digest (single-use). Recommend N=8 all-3-bits as the
  primary (cheapest, cleanest), N=16 low-bit as a scaling datapoint in the same job.
