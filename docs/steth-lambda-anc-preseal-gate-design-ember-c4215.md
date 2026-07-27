# Steth λ_anc pre-seal fidelity gate — LOCKED DESIGN (Ember C4215)

**Cue**: Whisper general#1605 (Creator greenlit steth Choi-purity flight, C5010). My lane: build the
λ_anc pre-seal gate `$0` "whenever you have a cycle" — same shape as the exp142 pre-seal gate. Flight
slotted #2.5 behind n8; **QPU hard-floored**, so no urgency. This note locks the design (advisor-reviewed)
so the build is a clean mechanical pickup — the hard specification/de-risking is done here.

## What the gate certifies
Before sealing a hidden Haar-U, fly a PUBLIC representative channel through the Choi-prep + two-copy
SWAP and confirm the **Choi-purity witness survives on-device** — i.e. a sealed-class U will read as
pure enough to separate from D, so the flight isn't washed before it flies. (exp142-preseal analog:
public test-P → even-rate survives; here public U/D → purity separation survives.)

## Delivered circuits to BUILD ON (do not re-implement — advisor #4 / c4215_003)
- **Two-copy SWAP purity**: `experiments/exp_steth_3b_twocopy_ember.py::two_copy_circuit` — Cincio
  destructive SWAP: per pair CX(a→b),H(a),measure; per-shot P2=(-1)^(Σ uᵢ∧vᵢ); E[P2]=Tr[ρ²]. Validated.
- **Choi prep + Λ + ancilla DD**: `experiments/exp_steth_a_flight.py::twocopy_circuit` pattern —
  k Bell pairs (system i / ancilla n+i), Λ on the system half, DD echo on the ancilla (the memory).
- ρ for the SWAP = the **Choi state** of the channel: k Bell pairs, apply the channel to the system
  half → 2k-qubit Choi. Two copies = 4k qubits (k=2→8q, k=3→12q; noiseless statevector cheap).

## The channels (advisor #1 + #3 — the load-bearing correctness points)
- **U (ALT)**: a **Haar-random k-qubit unitary** — SAME class as the sealed U (prereg §1: "fixed
  Haar-random U"). NOT identity — identity-Choi has no channel-gate noise and false-PASSes (the
  "XYZX exercises all bases" keystone). Draw a fresh public Haar U (public seed, documented), same
  depth/2q-structure as the sealed compile.
- **D (NULL)**: completely depolarizing = **fresh per-shot uniform Pauli twirl** on the k register
  (shots=1, fresh twirl per shot — c4215_006; a fixed draw misestimates the D-side purity).

## The observable + FROZEN floor (advisor #2 / c4215_005 — certify raw u, not label-recovery)
- On-device: p_odd(U) measured → **u = 1 − 2·p_odd(U)** (achieved Choi purity).
- Noiseless targets (self-check): p_odd(U)=0 (u=1); p_odd(D)=(1−4⁻ᵏ)/2 = **0.46875 (k=2) / 0.4922 (k=3)**.
- **FLOOR_U from the frozen G3 table** (`results/exp_steth_c4998_g3_sims.json` B_q_rule_purity_table),
  NOT an invented 0.75: u→m_Q is {1.0→6, 0.9→12, 0.8→16, 0.7→24, 0.6→…}. The flight is viable while
  m_Q stays in budget; arm-n-toy froze m_Q=24 ⇒ **FLOOR_U = 0.7**. PASS iff measured u ≥ 0.7 AND
  separation (p_odd(D) − p_odd(U)) ≥ MARGIN (≈0.25, clear of noise).
- Do NOT gate on label-recovery accuracy (it absorbs degradation through the m_Q margin exactly when u
  is marginal — c4215_005).

## λ_anc — dedicated MEASURED ancilla-survival block (C4975 circularity fix — affirmed)
- A **separate ancilla-only survival calibration** block (prep ancilla Bell-half, idle through the Λ
  depth with DD, measure survival) → λ_anc. Do NOT infer λ_anc from the Choi data (that was circular,
  C4975 verdict). Records λ_anc so any u-shortfall is ATTRIBUTED (ancilla loss vs channel-gate noise).

## Gate structure (lean exp142-preseal shape — no new harness)
- `--sim-only` `$0`: noiseless self-check — p_odd(U)≈0, p_odd(D)≈(1−4⁻ᵏ)/2 on the DELIVERED circuit
  (validates the observable + plumbing before any QPU).
- `--predict --backend ibm_fez` `$0`: NoiseModel — measured on-device u + λ_anc + routed depth +
  PASS/FAIL forecast. No job submitted.
- `--validate` (stubbed for QPU-time): on-device fly of public U/D Choi + λ_anc block; PASS iff
  u≥0.7 & separation≥MARGIN, before any seal. Parks armed like the n8 re-fly.

## Build checklist (all inputs gathered; mechanical from here)
1. Choi-prep(k, channel): Bell pairs + channel(system half). channel ∈ {haar_U(seed), depol_twirl(shot)}.
2. two-copy SWAP via exp_steth_3b two_copy_circuit (on the 2k-qubit Choi states).
3. p_odd → u; noiseless self-check vs targets; noise-model predict.
4. λ_anc ancilla-survival block (dedicated).
5. FLOOR_U=0.7 (frozen), MARGIN≈0.25; PASS logic.
6. $0 validate (sim-only + predict); on-device --validate stubbed for QPU.
