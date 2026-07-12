# Exp110 — SWAP vs Teleport Routing: Crossover or Informative Null (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4596. Comms-path E2; design doc
`exp110-swap-vs-teleport-crossover-design.md`; sim tier C4595 (wiring validated).
**Status**: FROZEN at commit. Grade on return, constants below, no analyst freedom.

## Question

Moving a qubit N hops across the lattice: does teleportation routing (pre-shared Bell pairs +
mid-circuit measurement + feedforward; ~2 CZ/hop, flat depth) ever beat unitary SWAP routing
(3 CZ/hop, growing depth) by N = 6? Platform priors credited (IBM long-range tutorial;
arXiv:2604.28037). **Leading prediction after the sim tier: NO** — FakeMarrakesh has SWAP
ahead at every N *without* modeling feedforward-latency noise, which penalizes only teleport.
The null is therefore first-class here, not a failure mode.

## Arms (probe preps {0, 1, +, +i} each; 3000 shots/circuit)

- swap N ∈ {1,2,4,6}: probe on chain position 0, N SWAPs, unprep, measure (7 qubits max).
- teleport N ∈ {1,2,4,6}: fresh Bell pair per hop, Bell measure + if_test X/Z corrections
  (13 qubits max; corrections wiring validated exactly in the noiseless tier).
- Sentinels: readout pair (|0⟩/|1⟩) on the chain's end qubits; one mid-batch repeat of
  swap-N6-prep0 (drift meter, ungated).
- 32 payload + 5 sentinel pubs ≈ 106k shots. Chain: best 13-qubit connected path by
  (CZ + readout) cost at submit (recorded in manifest); swap arm uses the first 7 positions —
  shared-segment comparison, same window by co-batching.

## Frozen estimator

Per (arm, N): mean survival over the 4 preps, measured in the prep basis (declared estimator).
Per-N difference D_N = surv_swap(N) − surv_tele(N); SE by binomial propagation
(SE_point ≈ 0.0020 at budget).

## Frozen gates (all linted `gate_feasibility_lint.py`, C4596)

- **G1 (readout sentinels)**: both end-qubit readout fidelities ≥ 0.95, else NO-TEST.
- **G2 (feedforward integrity)**: teleport N=1 mean survival ≥ **0.75**, else NO-TEST
  (broken corrections → ~0.5, decisive fail; preview 0.982; linted margins 0.22/0.25).
- **Outcome A — NO-CROSSOVER (leading)**: mean of D_N over N ∈ {2,4,6} − 5·SE_mean > **0.005**
  → "teleport strictly worse on average through N=6 at current feedforward quality."
  (Aggregate, not per-N: the preview's N=4 dip makes per-N 5σ claims fragile — stated now,
  not after data. Linted: pass margin 0.0153, decisive-fail margin 0.0218.)
- **Outcome B — CROSSOVER**: ∃ N ∈ {2,4,6} with D_N + 5·SE_D < 0 → "teleport wins at N."
  (Feasibility of the alternative linted symmetric: 0.0159/0.0244.)
- Mutually exclusive by construction at these margins; neither → AMBIGUOUS. N=1 is the shallow
  anchor, reported ungated.

## Pre-filed model comparison (ungated, atlas rows on return)

Two models disagree about the swap arm and hardware adjudicates a new depth-decay-family
datapoint: **depth-decay law** (d₀=208, window-conditional, amplitude-family caveat):
surv(N) ≈ {0.948, 0.935, 0.908, 0.882} for N={1,2,4,6}; **FakeMarrakesh preview**:
{0.991, 0.988, 0.956, 0.964}. Teleport preview {0.982, 0.954, 0.945, 0.924} is optimistic by
an UNKNOWN amount (no feedforward-latency noise in the model — stated caveat; whatever the
teleport residual is, it becomes the first feedforward-latency row in the atlas).

## Prediction (pred-tracker convention)

Outcome A conf **0.70**; Outcome B conf 0.10; AMBIGUOUS conf 0.20. Swap N=6 survival lands
closer to the law than to FakeMarrakesh: conf 0.55 (the F86 dual-prediction pattern, third
family).

## Apparatus set (frozen)

transpile: initial_layout = chain positions, seed_transpiler=4596, optimization_level=1
(Exp103 dynamic-circuit precedent; the level Finding 51's harness validated). Audit at scan:
swap = 3 CZ/hop exactly {3,6,12,18}; teleport = 2 CZ/hop exactly {2,4,8,12}; corrections are
classically conditioned 1q gates (0 CZ). Any mismatch = ABORT (free).
