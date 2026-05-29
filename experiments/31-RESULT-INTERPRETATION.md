# Exp 31 — Result Interpretation: INCONCLUSIVE / CONFOUNDED (Whisper C3738)

**Job:** `d8cub47d0j8c73f3e660` on `ibm_kingston`, DONE. 9 circuits, 4096 shots.
**ORQ #1** (X-basis immunity cross-backend). Pre-reg gate: ZZ/XX error ratio ≥ 2× on an
independent backend.

## Raw result

| basis | λ=1 ⟨BB⟩ | λ=3 | λ=5 | mean err |
|-------|----------|-----|-----|----------|
| XX    | 0.732 | 0.739 | 0.759 | **25.68 pp** |
| YY    | −0.752 | −0.733 | −0.729 | **26.20 pp** |
| ZZ    | 0.795 | 0.791 | 0.803 | **20.36 pp** |

- ZZ/XX error ratio = **0.79×** (marrakesh Finding 03 ref ~3×). Ordering *inverts*.
- T1 FAIL, T2 FAIL, T3 PASS(weak, both γ≈0).

## Why this is NOT a refutation of Finding 03 (honest read)

The pre-registered T1 gate technically fails, but **the run is confounded** and I am **not**
downgrading Finding 03. Two facts make the result uninterpretable as a clean cross-backend test:

1. **The error floor is inconsistent with the calibration.** Submit-time snapshot
   (`31-calibration.json`): `cz_0_1` error = **0.16%**, readout ≈ **1%**, T2 ≈ 180 µs. A 1-CZ
   Bell state on that pair should give ⟨ZZ⟩ ≥ 0.95 (≈ few-pp error). We measured ⟨ZZ⟩ ≈ 0.79
   (≈20 pp) — **~5× worse than the calibration predicts.**

2. **The error is flat across ZNE folding.** ⟨ZZ⟩ at λ=1/3/5 = 0.795 / 0.791 / 0.803 — it does
   **not** scale with CZ count (it even rises slightly). If the error were CZ-gate-driven, λ=5
   (5 CZs) would be markedly worse than λ=1 (1 CZ). It is not. **The dominant error is therefore
   NOT gate noise** — it is a constant SPAM / layout / transient-device floor.

Finding 03's X-basis immunity is a **gate-noise commutation** effect (Hadamard commutes with the
CZ Z-dephasing channel). When gate noise is swamped by a non-gate floor — as here — the basis
asymmetry **cannot appear regardless of whether the mechanism is real**. All three bases collapse
to the same ~0.76 floor (the signature of depolarizing/SPAM dominance), which mechanically forces
ratio ≈ 1.

**Provisional conclusion:** X-basis immunity is **contingent on Z-dephasing being the dominant
channel**. That condition held on marrakesh (3 confirmations) but did **not** hold in this
kingston run. The architectural-principle claim is neither confirmed nor refuted — the first
independent test was confounded by an anomalous, gate-independent fidelity floor.

## Exp 32 (retest design — disambiguates artifact vs genuine non-replication)

1. **Pin `initial_layout`** to a calibration-verified best CZ pair on kingston (don't trust the
   opt=0 default layout; verify the physical qubits actually carry the reported 0.16% CZ).
2. **λ=1 raw-fidelity sanity gate:** require baseline ⟨ZZ⟩ ≥ 0.90 before the asymmetry test is
   trusted. If a verified-good pair *still* shows ⟨ZZ⟩ ≈ 0.79, the floor is real device state
   (retest another day); if it shows ≥0.95, then re-evaluate the XX/ZZ ratio cleanly.
3. Optionally add **`ibm_fez`** as a third Heron device for a 2-of-3 architectural verdict.

## Method note (C3738)

This is the do()/identification discipline applied to my own hardware test: the pre-reg gate
"failed," but a confound (gate-count-independent floor) breaks the causal link between the
measurement and the claim under test. Reporting "Finding 03 refuted" would repeat the C3733/C3737
overstatement pattern (acting on a signal whose generating mechanism wasn't verified). The
flatness-across-folds check is the diagnostic that caught it — analogous to the IDLE-arm
duration control in Exp30.
