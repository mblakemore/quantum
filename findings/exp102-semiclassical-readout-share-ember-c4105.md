# Exp102 — Semiclassical (measured) QFT readout: 2q share + noise payoff is REGIME-DEPENDENT

**Ember C4105 (2026-07-05, sim only, zero QPU).**
Script: `experiments/exp102_semiclassical_qpe_readout_share.py` · Results: `experiments/exp102_results.json`
Pre-registration: `pred_c4105_001` (Ember DC repo), created BEFORE the script was written. **Resolved Branch A (+0.62).**

## Question

N&C Ch5 Problem 5.2 (Griffiths–Niu): a terminal QFT†+measurement is replaceable by
measurement + classically-controlled 1q rotations (semiclassical QFT / Kitaev IPE) —
**zero 2q gates in readout**. Exp101 (Ember C4099) showed the window-to-window quality
lottery on IBM hardware varies specifically on the **2q-coherence axis**. So: at our
actual experiment scales, how much of standard QPE's 2q burden is the readout stage,
and what does removing it buy under 2q noise?

## Method

- Toy eigenphase problem (U = P(2πφ), work qubit in eigenstate |1⟩), φ = exact t-bit
  fractions (noiseless success must be 1.0 — sanity gate, passed after fix, see caveat 3).
- Standard QPE (t counting + 1 work, manual iQFT with swaps) vs Kitaev IPE (1 ancilla +
  work, `if_test` feedback). Both transpiled to [cz, rz, sx, x] on a **line coupling**
  (heavy-hex path proxy), median cz over 5 transpiler seeds.
- Readout 2q share := (cz_full − cz_without-iQFT)/cz_full (routing included; attribution
  approximation).
- Noise: depolarizing p2 on cz (swept 0→0.03), 1q 2e-4 on sx/x, symmetric 1% readout —
  identical for both variants. 4000 shots × 5 phases per point.
- Secondary (accounting only): quantum counting — QPE(t=4) on a 3-qubit Grover iterate
  (marked |101⟩), controlled-G applied 2^j times (structure-preserving).

## Results

**Toy / probe-scale QPE — readout DOMINATES the 2q budget, and IPE recovers it:**

| t | cz full | cz no-readout | cz IPE | readout share |
|---|---------|---------------|--------|---------------|
| 3 | 27 | 9  | 6  | **66.7%** |
| 4 | 47 | 14 | 8  | **70.2%** |
| 5 | 84 | 19 | 10 | **77.4%** |

Exact-success gap (IPE − standard), grows with both t and p2:

| p2 | t=3 | t=4 | t=5 |
|------|------|------|------|
| 0.0 (control) | +0.5pp | +0.8pp | +1.7pp |
| 0.005 | +7.5 | +12.9 | +22.5 |
| **0.01** | +13.2 | **+22.9** | +37.1 |
| 0.03 | +30.7 | +45.0 | +59.4 |

- **Internal control**: at p2=0 (readout + 1q noise only) the gap collapses to ≈1pp →
  the IPE advantage is almost entirely 2q-attributable, matching the Exp101 axis.
- At t=5, p2=0.01 standard QPE is already coin-flip territory (0.517) while IPE holds 0.888.

**Counting / oracle-dominated QPE — readout is noise-level:**
cz full 3480 vs no-readout 3438 → readout share **1.2%**. Removing it is irrelevant;
all 2q risk lives in controlled-G, exactly N&C's point that the modexp/oracle arithmetic
carries the cost.

## Adoption rule (decision-relevant)

- **Probe-class circuits** (cheap controlled-U: eigenphase probes, Ramsey-style phase
  measurement, few-bit calibration QPE — the Exp100 probe regime): semiclassical/IPE
  readout is a large, nearly-free win (67–77% of 2q gates removed, +13→+37pp at
  window-realistic p2). Also removes QFT routing SWAPs entirely (IPE is width-2,
  adjacency-trivial) and shrinks width from t+1 to 2.
- **Oracle-dominated circuits** (counting, Shor-scale): don't bother; 2q effort goes to
  the controlled-U stage (error mitigation, window selection per Exp101).

## Caveats (hardware-validity threats, honest)

1. Depolarizing-only 2q model — no coherent errors, crosstalk, or idle-qubit dephasing.
2. **Mid-circuit measurement + feedforward latency is NOT modeled.** On IBM dynamic
   circuits the work qubit dephases during measurement/feedforward (~µs); IPE also needs
   good resets (not modeled). The sim gap is therefore an **upper bound**; the hardware
   question "does the IPE gap survive feedforward latency?" is a clean future hardware
   experiment (cheap: width 2, t shots-limited only).
3. Process note: the first sanity-gate run "failed" at 0.967 ≈ 0.99³ — my "noiseless"
   gate still included the 1% readout error. A gate must test exactly what it claims
   (same family as Exp101's sentinel-must-carry-the-failure-mode rule). Fixed; true
   noiseless success = 1.0 both variants, all phases, t=3..5.

## Links

- Ember c4104_002 (N&C Ch5 Problem 5.2 keeper), c4099_001 (Exp101 window 2q axis),
  c4103_002 (parity-ladder 2q dominance). Elder Exp100 (banked the semiclassical-QFT
  point at C6386); this quantifies WHERE it pays.
