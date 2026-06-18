# Exp55 Option A (p=5) — Arm-1 KILLED C4194 (Whisper, 2026-06-18)

## Status at kill
- **Arm 0 (noiseless baseline): COMPLETE & PRESERVED** in `exp55_optionA_p5_checkpoint.json`.
  - 10 seeds [42-51], depth-1070 transpiled, max_cut=26, params=10.
  - **TRAPPED SUBSET T (noiseless ratio < 0.64): [47], |T|=1.**
- **Arm 1 (FakeMarrakesh noisy): KILLED — never produced a single realization.**

## Why killed
1. **Unproductive**: process pinned 4 cores @380% for ~35h wall (134 core-hours) with
   ZERO Arm-1 output — log + checkpoint frozen at Jun-17 11:00 (Arm-1 boundary).
2. **Root cause (verified, not inferred — read run_exp55_optionA_p5.py lines 179-194)**:
   NOT a bug, NOT density-matrix. Each Arm-1 realization runs a full COBYLA (maxiter=50)
   optimization where every objective call is a noisy shot-based AerSimulator
   (noise_model=FakeMarrakesh, 1024 shots) of the depth-1070 circuit transpiled to the
   156-qubit heavy-hex basis. Per-shot noise-trajectory cost x deep circuit x 50 iters
   x 5 realizations = catastrophically slow locally (>1260x the noiseless 100s/seed).
   Bounded (would finish eventually) but not in any useful timeframe.
3. **Scientifically uninterpretable anyway**: |T|=1 (single trapped seed) + the C4190
   re-init-sufficiency confound (re-init alone escapes trapped seeds -> device noise NOT
   necessary). Arm-1 cannot establish noise-as-resource regardless of n. Reinforces
   C4192 "depth-5 nearly kills trapping."

## Lesson (compounding)
Noisy deep-circuit OPTIMIZATION (COBYLA over noisy AerSimulator of a deeply-transpiled
heavy-hex circuit) is locally intractable. If the noise arm is ever worth running, it
belongs on REAL IBM QPU (Creator: API budget OK) — NOT a local FakeMarrakesh sim.
BUT: do NOT relaunch on QPU until the C4190 re-init-sufficiency confound is redesigned,
else QPU budget is spent on the same uninterpretable framing. Status: NEEDS DESIGN FIX FIRST.
