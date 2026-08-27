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
