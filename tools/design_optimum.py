#!/usr/bin/env python3
"""Interior-optimum design calculator (Whisper C4564; licensed by the depth-decay
law surviving its Exp108 out-of-sample test, C4561).

Given a theory gain curve g(N) and a transpiled depth curve d(N) (CZ count),
predict the practical optimum N* = argmax g(N) * a * exp(-d(N)/d0), with
(a, d0) from the law fit and a window-quality knob.

Law (C4560, capacity-family amplitude observables, ibm_marrakesh):
    a = 0.962, d0 = 208 CZ  (window-conditional; Exp108's mediocre window
    delivered ratio 0.774 vs the law's 0.866 at 22 CZ)
Atlas note (C4564): the noise model UNDER-predicts the haircut by a depth-growing,
observable-family-dependent factor — use THIS law (hardware-anchored), not
FakeMarrakesh, for depth > ~20 CZ amplitude predictions, and rescale by a
same-depth sentinel when one is available.

Usage:
    from design_optimum import predict_ratio, optimum
    optimum(g=lambda N: capacity(N), d=lambda N: cz_cost(N), N_range=range(2, 7))

CLI demo reproduces the F85 inversion:  python3 tools/design_optimum.py
"""
import numpy as np

A_FIT = 0.962
D0_FIT = 208.0        # CZ, ibm_marrakesh, average-window


def predict_ratio(depth_cz, a=A_FIT, d0=D0_FIT, window=1.0):
    """Predicted measured/ideal ratio at a 2q depth. window: 1.0 = average
    (law fit); scale by (sentinel_hw / sentinel_expected) when a same-depth
    retention sentinel is available (Exp108: 0.856/0.9575 -> window ~0.89)."""
    return a * np.exp(-depth_cz / d0) * window


def optimum(g, d, N_range, **kw):
    """Return (N*, table). g(N)=ideal gain, d(N)=2q depth."""
    table = []
    for N in N_range:
        ratio = predict_ratio(d(N), **kw)
        table.append((N, g(N), d(N), ratio, g(N) * ratio))
    best = max(table, key=lambda r: r[-1])
    return best[0], table


if __name__ == "__main__":
    # Demo: the capacity-activation family (reproduces the F85 inversion).
    # Ideal Rbar grows with N; depth explodes (C4531 audit: 4 / 110 / ~341 CZ).
    g = {2: 8 / 15, 3: 0.6730}
    d = {2: 4, 3: 110}
    print("Capacity family (measured anchors in [brackets]):")
    for N in (2, 3):
        pred = g[N] * predict_ratio(d[N])
        meas = {2: 0.5034, 3: 0.3817}[N]
        print(f"  N={N}: ideal {g[N]:.4f} @ {d[N]:>3d} CZ -> predicted {pred:.4f} [measured {meas:.4f}]")
    # hypothetical N=4 full-cyclic at the C4531 6-order cost scale
    print(f"  N=6 full-order @ 341 CZ -> predicted ratio {predict_ratio(341):.3f} "
          f"(theory gain would need to be {1/predict_ratio(341):.1f}x N=2's to break even -> "
          f"confirms 'not this generation')")
    nstar, _ = optimum(lambda N: g[N], lambda N: d[N], (2, 3))
    print(f"  N* = {nstar} (the F85 conclusion, now computable pre-submission)")
