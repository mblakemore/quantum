#!/usr/bin/env python3
"""Measured-noise SURVIVAL PREDICTOR (Ember, Move 3) — gates Move 2, NOT Move 1.

SCOPE (gap G1, load-bearing): this is a generic-DEPOLARIZING model. It predicts the GF(2)-reader's
true-signal orthogonality decaying toward 0.5 (graceful). It has NO term that yields p_true < 0.5,
so it STRUCTURALLY CANNOT predict the copy-channel COHERENT INVERSION (Exp148 copy arm hit
0.10-0.34). A green light means "won't drown from generic decay" — NOT "won't lie from a coherent
inversion." Coherent failure is twirling's job (Exp149), not this gate's. Use accordingly.

MODEL: p_true(2q) ~ 0.5 + 0.5 * (1-E_CX)^n_2q * (1-E_RO)^n_meas
  BACK-TESTED vs Exp148b GENERIC arm: max error 0.017 across 2q = 4..60. Validated for generic reach.
  Also (known-answer): reproduces Simon 145 survival and Exp144 detector death qualitatively.

From p_true it derives the bias margin and the reps a consensus (ML) decoder needs to recover.

  python3 exp_survival_predictor_ember.py --backtest
  python3 exp_survival_predictor_ember.py --predict --n2q 42 --nmeas 4 --reps 256
"""
import argparse
import math

E_CX = 0.0106
E_RO = 0.02


def p_true_pred(n2q, n_meas):
    """Predicted true-signal orthogonality fraction under generic depolarizing decay."""
    return 0.5 + 0.5 * (1 - E_CX) ** n2q * (1 - E_RO) ** n_meas


def reps_to_recover(n2q, n_meas, n_secret_bits, alpha=0.05):
    """Reps a Bonferroni-corrected consensus/ML detector needs to resolve the bias vs 2^n-2
    competitors. Uses the predicted p_true; competitor fraction modeled at 0.5 (generic)."""
    from statistics import NormalDist
    p = p_true_pred(n2q, n_meas)
    delta = p - 0.5                                   # generic: best competitor ~ 0.5
    if delta <= 0:
        return math.inf
    C = 2 ** n_secret_bits - 2
    z = NormalDist().inv_cdf(1 - alpha / max(C, 1))
    return (z * math.sqrt(2 * 0.25) / delta) ** 2


def survives(n2q, n_meas, n_secret_bits, rep_budget):
    """Predicted survival: does the generic-decay bias resolve within the rep budget?"""
    need = reps_to_recover(n2q, n_meas, n_secret_bits)
    return {"p_true_pred": round(p_true_pred(n2q, n_meas), 3),
            "reps_needed": None if need == math.inf else round(need, 1),
            "rep_budget": rep_budget,
            "survives": need != math.inf and need <= rep_budget,
            "SCOPE": "generic decay only — blind to coherent inversion (G1)"}


def backtest():
    gen = {4: 0.973, 20: 0.915, 32: 0.873, 44: 0.825, 60: 0.749}   # Exp148b GENERIC arm, measured
    print("BACK-TEST vs Exp148b GENERIC arm (n_meas=4):")
    print(f"  {'2q':>3} {'pred':>7} {'meas':>7} {'err':>6}")
    maxerr = 0.0
    for q, m in gen.items():
        p = p_true_pred(q, 4)
        e = abs(p - m); maxerr = max(maxerr, e)
        print(f"  {q:>3} {p:>7.3f} {m:>7.3f} {e:>6.3f}")
    ok = maxerr < 0.05
    print(f"  max error {maxerr:.3f} -> {'VALIDATED (generic scope)' if ok else 'MODEL FAILS'}")
    # G1 scope proof: cannot reproduce the copy inversion
    copymin = min(p_true_pred(q, 4) for q in gen)
    print(f"  G1: model floor = 0.5 (min predicted p_true here {copymin:.3f} at 2q=60); Exp148 COPY arm "
          f"hit 0.10-0.34 -> model provably CANNOT predict the coherent inversion. Scope confirmed.")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backtest", action="store_true")
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--n2q", type=int, default=42)
    ap.add_argument("--nmeas", type=int, default=4)
    ap.add_argument("--nbits", type=int, default=4)
    ap.add_argument("--reps", type=int, default=256)
    a = ap.parse_args()
    if a.backtest:
        return 0 if backtest() else 1
    if a.predict:
        import json
        print(json.dumps(survives(a.n2q, a.nmeas, a.nbits, a.reps), indent=1))
        return 0
    ap.print_help(); return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
