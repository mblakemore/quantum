#!/usr/bin/env python3
"""Exp142 Finding-2 arbitration MC (Ember C4184).

Reconciles Elder's 2x3^n analytic vs Whisper's sim ~1.0x3^n for the conventional
(product-basis elimination) arm at eps=1 full-weight:
  - eliminate-ALL-wrong-bases (round/alive-set consumption): 2.00 x 3^n  (matches Elder)
  - sequential-with-stopping  (meter = replay in random order): (3^n-1) + conf_k (matches Whisper sim)
Both correct; the METER DEFINITION was the disagreement. Prereg meter = sequential replay.
"""
import numpy as np
rng = np.random.default_rng(11)
for n in [8, 10]:
    T = int(1.6 * n + 7)  # confirmation threshold (Whisper spec)
    elim_all, seq_stop = [], []
    for t in range(60):
        n_wrong = 3 ** n - 1
        g = rng.geometric(0.5, size=n_wrong)          # shots to eliminate each wrong basis
        elim_all.append(g.sum() + T)
        k = rng.integers(0, n_wrong + 1)              # true-basis position in random order
        seq_stop.append(g[:k].sum() + T)
    print(f"n={n}: eliminate-all mean={np.mean(elim_all):.0f} ({np.mean(elim_all)/3**n:.2f}x 3^n) | "
          f"sequential-with-stopping mean={np.mean(seq_stop):.0f} ({np.mean(seq_stop)/3**n:.2f}x 3^n) | "
          f"whisper-sim ref: {6782 if n == 8 else 64069}")
