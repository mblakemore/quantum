# Exp110 — SWAP-vs-Teleport Crossover Law (DESIGN, pre-prereg)

**Author**: Whisper (DC15W), C4590. Comms-path E2. **Status: DESIGN** — sim tier and freeze
next; nothing here is frozen yet.

## Question

Moving a qubit state N hops across the heavy-hex lattice: at what hop count does
teleportation-based routing (pre-shared entanglement + mid-circuit measurement +
feedforward; depth ~constant per hop in 2q gates, classical wire does the work) beat unitary
SWAP routing (3 CZ per hop, depth grows linearly)? Platform priors credited (IBM long-range
entanglement tutorial; arXiv:2604.28037 dynamic teleportation on ibm_fez) — the DEMO is
worthless; the **crossover hop count N\*** under stated window/placement conditions is the
open number, and it feeds `design_optimum.py` as a routing rule.

## Arms (per N ∈ {1, 2, 4, 6} hops, same chain of qubits, co-batched)

- **SWAP arm**: prepare probe states on q0, SWAP N hops down the chain, measure fidelity
  proxy (state tomography-lite: prepare {|0⟩,|1⟩,|+⟩,|+i⟩}, measure appropriate basis —
  average fidelity estimator from 4 preps).
- **Teleport arm**: same probe preps; entangle-and-measure teleport at each hop
  (dynamic circuits, `if_else` corrections per Finding 51 machinery).
- **Null/reference**: N=0 prepare-measure on q0 (readout floor) + the chain's per-pair CZ
  sentinel.

## Pre-filed predictions (to freeze with numbers at prereg)

- SWAP arm: depth-decay law with d(N)=3N CZ → fidelity ratio ≈ 0.962·exp(−3N/d₀), d₀ from
  the live sentinel ledger at freeze time. This arm doubles as a NEW depth-decay datapoint
  family (routing observable class — the atlas doesn't cover it).
- Teleport arm: per-hop cost ≈ constant (1 Bell prep + 1 Bell meas + feedforward latency
  ≈ 2 CZ + measurement-classical-latency noise per hop). Key uncertainty: mid-circuit
  measurement + feedforward error per hop on Heron (literature: this is the dominant term —
  2604.28037's subject). The sim tier CANNOT preview feedforward latency noise faithfully
  (FakeMarrakesh limitation, to be stated); the prereg must gate on relative comparison, not
  absolute teleport fidelity.
- Crossover: if per-hop teleport cost < 3-CZ-equivalent decay, N\* is small (≤4); the
  interesting NULL is "no crossover by N=6" (teleport worse everywhere at current
  feedforward quality) — both outcomes are findings, and the gate structure must make both
  gradeable (linter check on both directions).

## Design constraints carried in

- Chain selection: quiet-qubit picker over a connected path (F57–F70 machinery), recorded.
- Window: same-depth-class sentinel co-batched (F85 rule); the SWAP N=6 arm is 18 CZ = the
  deep probe.
- Dynamic-circuit support on marrakesh runtime confirmed by Exp102/103 (Finding 51) —
  reuse that harness's if_else conventions.
- Feasibility tiers: noiseless + FakeMarrakesh for the SWAP arm; teleport arm noiseless +
  best-effort Fake (feedforward noise caveat stated); ALL gates through
  `gate_feasibility_lint.py` pre-freeze.

## Cost estimate

4 preps × 4 Ns × 2 arms × ~3k shots + sentinels ≈ 100k shots, tens of seconds QPU-class.
Submit after Exp108b and Exp109 grade (max two jobs in flight — queue hygiene).
