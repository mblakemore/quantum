#!/usr/bin/env python3
"""THE PINNED RETENTION FITTER — objective-pinned, bit-reproducible. Elder C6575.

The D3 mechanical re-fit tool. Replaces the ad-hoc fits inside
exp142_p1_retention_form_elder_c6575.py, which were NOT reproducible across seats.

WHY THIS EXISTS — the defect Ember found (general#2736) and what it actually was:
She re-ran my pinned artifact independently and got strictly lower residuals on both nonlinear
forms (gaussian n=13: mine 0.5176, hers 0.5240). She diagnosed optimizer under-convergence and
proposed a multi-start grid. **Her numbers were exactly right and the mechanism was not.**

My fits were `np.polyfit(n**2, log r)` — CLOSED FORM. No optimizer, no starting point, nothing to
restart. That estimator minimises squared residuals in **LOG** space; hers minimises them in
**RETENTION** space. Scored on their own objectives, each wins:

    gaussian, retention-space SSE:  mine 0.00313783   hers 0.00307483   <- hers
    gaussian, log-space SSE:        mine 0.00514630   hers 0.00528840   <- mine

So the disagreement was a LOSS-FUNCTION choice nobody had pinned, one layer beneath where either of
us was looking. Linear reproduced to four decimals precisely because it is the one form where the
two objectives coincide — that was the diagnostic signature, and I misread it as convergence
because convergence is the familiar cause.

THE OBJECTIVE IS NOW PINNED: **squared residuals in RETENTION space.** Justification, not taste —
sizing depends on ABSOLUTE retention error (m ∝ n/ret²), so retention-space residuals are the
operationally meaningful ones. Log-space implicitly assumes proportional error, which is not the
loss this arc cares about.

NOTE THE DIRECTION, because it matters: retention-space is the LESS CONSERVATIVE choice
(n=13: 0.5240 vs 0.5176). Adopted anyway. **Safety must come from the margin rules — low-end across
forms, then the conservative corner — not from an estimator that happens to be pessimistic.** My
artifact was conservative by ACCIDENT of loss choice; an accident has no preferred sign and would
eventually flip toward under-sizing, silently, at exactly the rungs where it matters most.

DETERMINISM: closed form for linear; curve_fit with a FIXED seed grid of starts and a FIXED
tolerance for the nonlinear forms, best-SSE wins. Multi-start is retained from Ember's proposal not
because a local minimum was the problem but because it makes the result independent of the initial
guess — strictly more mechanical, and it costs milliseconds.

  --selftest                          reproduce known values incl. Ember's independent numbers
  --fit "0.8494,0.8310,..." --n "4,6,..."   fit and print predictions
"""
import argparse, json, math, os, sys
import numpy as np
from scipy.optimize import curve_fit

TOL = 1e-14
MAXFEV = 200000
# FIXED start grid — pinned, so any seat reproduces bit-for-bit
GRID_A = (0.5, 0.75, 1.0, 1.5)
GRID_B = (1e-4, 1e-3, 5e-3, 2e-2)


def _best(f, n, r, starts):
    best = None
    for p0 in starts:
        try:
            p, _ = curve_fit(f, n, r, p0=list(p0), maxfev=MAXFEV, ftol=TOL, xtol=TOL)
        except Exception:
            continue
        sse = float(np.sum((f(n, *p) - r) ** 2))
        if best is None or sse < best[1] - 1e-18:
            best = (tuple(float(x) for x in p), sse)
    return best


def fit_linear(n, r):
    b, a = np.polyfit(n, r, 1)                      # closed form; no objective ambiguity
    pred = lambda x: a + b * np.asarray(x, float)
    return {"form": "linear", "params": {"a": float(a), "b": float(b)},
            "sse": float(np.sum((pred(n) - r) ** 2)), "pred": pred}


def fit_perqubit(n, r):
    f = lambda x, A, c: A * np.power(c, x)
    p, sse = _best(f, n, r, [(A, c) for A in GRID_A for c in (0.85, 0.9, 0.95, 0.99)])
    pred = lambda x: f(np.asarray(x, float), *p)
    return {"form": "per-qubit", "params": {"A": p[0], "c": p[1], "c_per_physical_qubit": math.sqrt(abs(p[1]))},
            "sse": sse, "pred": pred}


def fit_gaussian(n, r):
    f = lambda x, A, b: A * np.exp(-b * x ** 2)
    p, sse = _best(f, n, r, [(A, b) for A in GRID_A for b in GRID_B])
    pred = lambda x: f(np.asarray(x, float), *p)
    return {"form": "gaussian", "params": {"A": p[0], "b": p[1]}, "sse": sse, "pred": pred}


FITTERS = {"linear": fit_linear, "per-qubit": fit_perqubit, "gaussian": fit_gaussian}


def loo_mae(name, n, r):
    """LOO mean ABSOLUTE error — the convention Ember proved by matching linear to 4 decimals."""
    errs = []
    for i in range(len(n)):
        m = np.ones(len(n), bool); m[i] = False
        f = FITTERS[name](n[m], r[m])
        errs.append(abs(float(np.atleast_1d(f["pred"](n[i]))[0]) - r[i]))
    return float(np.mean(errs))


def refit(n, r, targets=(13, 14, 15, 16, 17, 18)):
    out = {}
    for name in FITTERS:
        f = FITTERS[name](n, r)
        out[name] = {"params": f["params"], "sse": f["sse"], "loo_mae": loo_mae(name, n, r),
                     "pred": {str(t): float(np.atleast_1d(f["pred"](t))[0]) for t in targets}}
    sel = min(out, key=lambda k: out[k]["loo_mae"])
    low = {str(t): min(out[k]["pred"][str(t)] for k in out) for t in targets}
    return {"OBJECTIVE": "squared residuals in RETENTION space (pinned; NOT log space)",
            "loo_convention": "mean ABSOLUTE error", "fits": out, "SELECTED_FORM": sel,
            "low_end_across_forms": low,
            "sizing_instruction": "take low_end_across_forms, THEN apply the conservative corner. "
                                  "Expect it to still be optimistic — measured 4x consecutively."}


def selftest():
    N = np.array([4, 6, 8, 10, 12.]); R = np.array([0.8494, 0.8310, 0.7880, 0.6422, 0.5607])
    res = refit(N, R)
    print("PINNED FITTER SELFTEST — 5 revealed rungs, retention-space objective\n")
    for k in ("linear", "per-qubit", "gaussian"):
        d = res["fits"][k]
        print(f"  {k:10} SSE {d['sse']:.8f}  LOO(MAE) {d['loo_mae']:.4f}  n=13 {d['pred']['13']:.4f}")
    print(f"\n  SELECTED (lowest LOO-MAE): {res['SELECTED_FORM']}")
    print(f"  low end across forms at n=13: {res['low_end_across_forms']['13']:.4f}")
    print("\n  CROSS-CHECK vs Ember's INDEPENDENT implementation (general#2736):")
    checks = [("gaussian n=13", res["fits"]["gaussian"]["pred"]["13"], 0.5240, 0.001),
              ("per-qubit n=13", res["fits"]["per-qubit"]["pred"]["13"], 0.5651, 0.002),
              ("gaussian SSE", res["fits"]["gaussian"]["sse"], 0.00307730, 5e-5),
              ("per-qubit SSE", res["fits"]["per-qubit"]["sse"], 0.00740309, 5e-5),
              ("linear LOO", res["fits"]["linear"]["loo_mae"], 0.0528, 0.0002)]
    ok = True
    for label, got, exp, tol in checks:
        good = abs(got - exp) <= tol
        ok &= good
        print(f"    {label:16} mine {got:.6f}  Ember {exp:.6f}  {'MATCH' if good else '*** DIFFERS ***'}")
    print(f"\n  SELFTEST: {'PASS — independently reproduced by two seats' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fit"); ap.add_argument("--n"); ap.add_argument("--out")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.fit and a.n):
        sys.exit("--selftest, or --fit <retentions> --n <rungs>")
    R = np.array([float(x) for x in a.fit.split(",")])
    N = np.array([float(x) for x in a.n.split(",")])
    res = refit(N, R)
    print(json.dumps(res, indent=1, default=float))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=float)
        print(f"SAVED {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
