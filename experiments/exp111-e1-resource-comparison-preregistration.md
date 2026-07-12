# Exp111 — Is It Indefinite Causal Order, or Just Coherent Control? (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4593 (2026-07-12). Comms-path E1
(`docs/quantum-communication-paths-whisper-c4588.md`; theory tier C4589).
**Status**: FROZEN at commit. Grade on return, constants below, no analyst freedom.

## Question and stakes

The literature disputes whether the switch's communication advantage is an
indefinite-causal-order resource or merely coherent control (a superposition of PATHS through
the channels gets an advantage too — Abbott et al. 2020; photonic/NMR experiments exist; no
gate-model, co-batched, frozen-graded comparison exists on any platform per our C4588 search).
Theory tier (C4589, exact, implementation-fair — both arms use the identical Pauli-label Kraus
representation): switch transmits 0.0488 bits, paths 0.0123 bits, MI ratio 3.96; in
matched-filter effect-size units S_switch = 0.2500, S_paths = 0.1250, ratio 2.00.

**Either verdict is a finding**: paths ≈ switch → coherent control is the resource and our
ICO framing gets a measured caveat (confirmation-symmetry); switch ≫ paths → the ICO reading
strengthens with numbers. This also pre-empts the sharpest referee line against the
pearl-bridge paper and F86.

## Five arms, one job, one window (labels (a,b) ∈ Paulis², inputs b ∈ {0,1})

| Arm | Circuits | Shots each | Skeleton |
|---|---|---|---|
| switch | Exp106 build_circuit, 32 | 1500 | uniform 4-CZ (validated apparatus) |
| paths | c₀-σ_a, c₁-σ_b routing, 32 | 1500 | label-dependent 2–4 CZ (see fairness note) |
| sw_mix | switch w/ control prep pooled {|0⟩,|1⟩}, 64 | 750 | identical to switch, label-wise |
| paths_mix | paths w/ prep pooling, 64 | 750 | identical to paths, label-wise |
| null | definite order, 32 | 1500 | 0 CZ (control spectator) |
| sentinels | Exp105 DISC triplet ×3 (start/mid/end) | 2000 | Exp105 template |

**Fairness note (stated before data)**: exact cross-arm CZ matching is parity-blocked
(identity operands cost 2 CZ, others 1). Each arm's coherence is instead attributed via its
OWN label-wise skeleton-identical mixture control; the residual depth difference (paths
shallower) favors paths — i.e., it biases AGAINST the switch-wins headline, so G6 passing is
conservative.

## Frozen estimators

Pooled per arm per input over 16 labels (Exp106 analyze conventions; outcome order
(c+,t0),(c+,t1),(c−,t0),(c−,t1)). **Matched-filter statistics, filters frozen from the
noiseless tier** (`results/exp111_feasibility.json`):

Outcome vector order = counts-key order 'tc': **(t0 c+, t0 c−, t1 c+, t1 c−)**.
- S_switch = w_sw · (p̂₀ − p̂₁), w_sw = ½(+1,−1,−1,+1) — the C–T parity channel
  (order-symmetric pattern).
- S_paths  = w_pa · (p̂₀ − p̂₁), w_pa = ½(+1,−1,+1,−1) — the control-visibility channel.
  (The two arms carry information in DIFFERENT correlations — the tier-1 discovery that
  forced this estimator: Exp106's R̄ sees the switch at 0.5333 but the paths effect at only
  0.0185. R̄ and MI are reported for continuity, ungated. Pre-freeze catch logged: the first
  filter derivation used (c,t) outcome order while counts keys are (t,c) — caught because
  the circuit-tier S_paths read exactly 0 against theory 0.125; the parity filter's symmetry
  masked it for the switch. Filters above are in the counts order and reproduce theory
  exactly: S_sw = 0.25000, S_pa = 0.12500 noiseless.)
- Same filter applied to the arm's own mixture gives S_sw_mix, S_paths_mix.
- Null integrity via Exp106's unconditioned D observable.
- SEs: binomial propagation through the filter (per tier-1 formulas).

## Frozen gates (linter-verified pre-freeze; constants final)

- **G1 (sentinels)**: min DISC ≥ 1.60 over 3 replicates, else NO-TEST.
- **G2 (null integrity)**: |D_null| + 5·SE < 0.10, else NO-TEST.
- **G3 (mixture integrity)**: |S_sw_mix| + 5·SE < 0.04 AND |S_paths_mix| + 5·SE < 0.04,
  else NO-TEST (dephasing machinery broken → coherence attribution impossible). Linted:
  pass margins 0.017/0.013 at preview; broken-dephasing fails decisively (0.125–0.246 ≫ band).
- **G4 (switch WIN)**: S_switch − 5·SE > 0.10 (linted: pass 0.127 / fail 0.092).
- **G5 (paths WIN)**: S_paths − 5·SE > 0.05 (linted: pass 0.058 / fail 0.042).
- **G6 (headline, the resource question)**: S_switch − S_paths − 5·SE_diff > **0.02**
  (SE_diff = √(SE_sw² + SE_pa²)). PASS = "the switch strictly exceeds coherent path control
  at matched estimators, despite the depth confound favoring paths." (First draft used
  threshold ~0: VACUOUS-PASS — the equal-resources scenario lands AT the threshold and can
  never decisively fail; linter catch, same class as Exp109 G1. 0.02 sits > 2·SE_diff above
  equal-resources: fail margin 0.009, pass margin 0.071.)
- G4/G5/G6 grade independently (each can WIN/LOSS; G1–G3 failures = NO-TEST for all).

## Pre-filed expectations (FakeMarrakesh tier, `results/exp111_S_previews.json`)

S_switch preview 0.2463 (SE 0.0039), S_paths preview 0.1275 (SE 0.0039); mixtures consistent
with 0. Atlas shallow-class correction (+0.030 ln) → hardware expectation S_switch ∈
[0.225, 0.245], S_paths ∈ [0.115, 0.128], **S-ratio ∈ [1.7, 2.1]**.
**Prediction (pred-tracker convention)**: G4 WIN conf 0.90, G5 WIN conf 0.80, G6 PASS conf
0.85; S-ratio ∈ [1.6, 2.4] conf 0.60.

## Cost

228 payload pubs + 6 sentinels ≈ 250k shots ≈ 45–60 s QPU-class. Backend ibm_marrakesh,
pair via Exp105 `pick_pair` at submit; transpile: initial_layout=pair,
seed_transpiler=4593, optimization_level=1 (the frozen apparatus set, C4592 lesson);
label-wise CZ audit vs the FakeMarrakesh-tier histogram recorded in the feasibility JSON —
mismatch on any label = ABORT (free).

## Post-freeze amendment (C4593, pre-submission, compilation-level only)

The frozen text said optimization_level=3 (inherited from the 108-family); the free scan
showed level 3 CANCELS the barrier-fenced identity pads (switch histogram {4:14,2:12,0:6}
instead of uniform {4:32}). Level 1 — the level Exp106's validated skeleton was actually
built at — restores every expected skeleton exactly (switch {4:32}, sw_mix {4:64},
sentinels {4:6}, null {0:32}, paths {2:18,3:12,4:2}). No gate constants, filters, shots, or
analysis change. Honesty note: the FakeMarrakesh S previews were computed from opt-3
circuits (some pads cancelled → previews marginally optimistic on noise exposure); the
pre-filed expectation bands are informational (conf 0.60), the graded gates carry pass
margins (0.127/0.058/0.071) far exceeding the few-percent effect of ≤2 extra CZ.
