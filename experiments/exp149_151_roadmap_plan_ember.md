# Roadmap: building on the GF(2) hidden-structure machine (Ember, C4195) — REVISED

## Unifying thesis
Simon (145), Even-Mansour (146), QEC syndrome decoding (147), Hamiltonian learning (142/144) are
**one machine**: a GF(2) parity/detection engine. Three composable moves:
1. **Make the reader smarter** (Exp149) — engineer the reps↔depth tradeoff + test/defend the
   coherent inversion.
2. **Climb toward the descendants** (Exp150) — add the QFT (the Shor kernel, toy size).
3. **Predict survival before flying** (Move 3, a tool) — gates Move 2 (NOT Move 1, see gap G1).

Built on (measured tonight): reader robustness = optimal detection of a shrinking bias, wall =
statistical-power threshold movable with reps (148); confident-wrong failure is copy-channel-
specific, not generic depth, and there the blind self-check *endorses* the wrong answer (148b/C4837);
E_CX≈1.06%, idle-blindness, calibration under-reports ~8×.

---

## REVISIT — gaps found (advisor pass) and how they change the plan
- **G1 — the predictor is blind to the inversion, by construction.** It's a depolarizing/independent
  model `(1-E_CX)^n_cx …`; it predicts the bias decaying *toward* 0.5 (graceful) and has **no term
  that yields p_true < 0.5**. So it CANNOT predict the copy-channel inversion. Green from it means
  "won't drown from generic decay," NOT "won't lie from a coherent inversion." **Scope it to
  generic-decay reachability; do NOT lean on it for Exp149.** Back-test = predict 148b's GENERIC arm
  (should match) and confirm it does NOT claim the copy arm. Division of labor: predictor bounds
  generic reach; twirling (149) handles coherent failure; neither alone is a full safety gate.
- **G2 — Exp150 r-choice.** r∈{2,4} at t=3 are powers of 2, so `x mod r` = low bits → near-degenerate,
  barely exercises the QFT, and "recovered r == planted" would hide a weak test. The genuine QFT test
  is r ∤ 2^t (real Shor regime; recovery is *approximate* via continued fractions). Pick deliberately
  and state the regime.
- **G3 — Exp150 self-verification is NOT Simon's.** Orthogonality doesn't transfer. The blind intrinsic
  check for period-finding is `f(x) == f(x + r_hat) (mod N)` for sampled x. Specify it explicitly.
- **G4 — Exp149 twirl is a MECHANISM test, not just a defense.** 148b showed the inversion is
  location-specific but did NOT establish it's coherent. Pauli twirling converts coherent→stochastic
  at matched infidelity, so twirl-kills-inversion IS the evidence it was coherent (the c4183_001
  control 148b deferred). Reframe + pre-register that way.
- **G5 — vacuous-twirl trap (c4195_002).** A twirl of identity Paulis is logically correct and a no-op
  — it passes a noiseless-truth gate while doing nothing. Needs a NON-vacuous twirl gate: assert the
  inserted Paulis vary per rep AND actually twirl the channel.
- **G6 — QFT-correctness is bug-prone** (qubit ordering, controlled-phase angles, terminal bit-reversal).
  The noiseless gate must recover planted r EXACTLY as an explicit QFT check.

## PRE-DEV TEMPLATE (every experiment fills this BEFORE building)
```
- Hypothesis:               the claim, falsifiably.
- Pre-registered prediction + confidence (written to disk BEFORE decode).
- Self-verification:        the blind intrinsic truth-check (ground-truth held by submitter).
- Pre-flight gates:         noiseless-truth (non-vacuous), matched-noise, correctness-specific.
- Survival gate:            predictor call (SCOPED to generic decay) — where applicable.
- Falsifier:                what result kills the hypothesis.
- Honest label, BOTH ways:  the sentence we ship if it holds AND if it fails.
- KILL-CRITERION:           which gate failure means DO NOT FLY, and what we report instead.
- Budget (QPU-s) + dependencies + confound notes.
```

---

## Move 3 — survival PREDICTOR (tool; build & run FIRST)
- **Hypothesis:** measured-noise depolarizing model predicts *generic-decay* recovery vs (2q, reps).
- **Prediction (0.7):** it matches 148b's GENERIC arm within ~1 rung; it does NOT reproduce the copy
  inversion (G1 — a feature, scoping proof).
- **Self-verification:** back-test against already-graded 148b data (generic arm), not new flight.
- **Gates:** reproduces Simon 145 survival + Exp144 detector death (already known-answer).
- **Falsifier:** if it can't match the generic arm, the model is wrong and gates nothing.
- **Honest label:** holds → "bounds generic reach, blind to coherent inversion (use with twirl)."
  fails → "no trustworthy survival gate; fly conservatively."
- **KILL:** if back-test fails, do NOT use it to gate 150; fly 150 at the smallest t only.
- **Budget:** 0 QPU (analysis). **Gates Move 2, not Move 1.**

## Move 1 — Exp149: adaptive reader + twirl mechanism-test/defense
- **Hypothesis:** (a) adaptive/SPRT sampling reaches greater depth at equal TOTAL budget than fixed
  reps; (b) Pauli-twirling the oracle REMOVES the copy-channel inversion — which both confirms the
  inversion was coherent (G4) and provides the defense.
- **Prediction (0.65):** twirled does NOT invert (p_true>0.5, recovers) where untwirled inverts;
  adaptive buys ≥1 depth rung at fixed budget. (Low conf: quantum, and twirl efficacy on THIS
  hardware is unmeasured.)
- **Self-verification:** planted s (Simon kit), s_hat==planted AND orthogonality.
- **Pre-flight gates:** noiseless-truth (twirled & untwirled both recover s); matched-noise
  (twirled≈untwirled 2q at each depth); **NON-VACUOUS twirl gate (G5):** assert inserted Paulis
  differ across reps AND that twirled≠untwirled as circuits while ideal-equivalent.
- **Survival gate:** N/A per G1 (predictor can't see this); rely on the twirl gate instead.
- **Falsifier:** twirled ALSO inverts → not purely coherent; adaptive ≤ fixed → no sampling gain.
- **Honest label:** holds → "the inversion is coherent and twirling defends it; smart sampling
  extends reach." fails → "inversion not purely coherent / twirl insufficient on this hardware."
- **KILL:** if the non-vacuous twirl gate fails (twirl is a no-op), DO NOT FLY — report the twirl
  construction bug. If noiseless-truth fails, DO NOT FLY.
- **Budget:** ~8 QPU-s. Adaptive analysis is free (post-processing on 148 + 149 streams).

## Move 2 — Exp150: QFT period-finding over Z_{2^t} (Shor kernel, toy)
- **Hypothesis:** QFT-based period-finding recovers a hidden period r on kingston at small t.
- **Prediction (predictor-set):** recover r at the largest t the (scoped) predictor says survives;
  fail beyond it. Two regimes flown, LABELED (G2): r | 2^t (exact peaks, weak QFT test) AND
  r ∤ 2^t (approximate, continued fractions — the real Shor regime).
- **Self-verification (G3):** planted r; blind check `f(x)==f(x+r_hat) mod 2^t` on sampled x, plus
  recovered-r == planted at zero noise.
- **Pre-flight gates:** **QFT-correctness / noiseless-truth (G6):** recover planted r EXACTLY at
  zero noise (catches qubit-order/phase/bit-reversal bugs); matched transpile; survival-gate for t.
- **Falsifier:** fails to recover r at a t the predictor said survives → either QFT bug (should have
  been caught noiseless) or predictor over-optimistic (log it).
- **Honest label + FENCE (same breath as any headline):** holds → "the Shor KERNEL — QFT
  period-finding — runs on real hardware at t=N; **NOT factoring RSA** (needs modular exponentiation,
  fault tolerance, t of hundreds)." fails → "QFT depth (~t²) drowns past t=N on current noise."
- **KILL:** if noiseless-truth (QFT-correctness) does not pass EXACTLY, DO NOT FLY — ship this plan
  entry with the failing gate named, not a broken circuit (that is compliance with "fly them," not
  failure).
- **Budget:** ~5–10 QPU-s, t-dependent.

---

## Execution order (unchanged, right)
1. Build + back-test + run predictor (Move 3) → survival table (gates Move 2).
2. Fly Exp149 (most ready, builds on 148; twirl gate is the go/no-go).
3. Fly Exp150 at reachable t (QFT-correctness gate is the go/no-go).
Each: pre-registered before decode, self-verifying, honest label both ways, KILL-criterion honored.
**"Fly them" = fly each whose gates pass; for any that fails a gate, report it designed-and-gated
with the failing gate named. That is compliance, not failure.**
