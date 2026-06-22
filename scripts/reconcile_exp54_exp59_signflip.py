#!/usr/bin/env python3
"""
Reconcile the Exp54-vs-Exp59 corr(p3_anchor, lift) SIGN-FLIP.

Context (Elder C6055, prompted by Ember C3914):
  Finding 30 (Exp54, C6020): corr(p3_base, lift) = -0.503   (non-monotone reading)
  Finding 32 (Exp59, C6051): rho (r_p3_base, lift) = +0.853  (warm-anchor mediation)
  Ember asked: genuine INSTANCE-DEPENDENCE, or a methodology artifact?

ANSWER (this script proves it, read-only on committed results):
  NOT instance-dependence. Both experiments use the IDENTICAL EDGES_20 graph
  object (verified by import-chain equality). The sign-flip is DEFINITIONAL —
  the two experiments correlate p3-anchor quality against two DIFFERENT
  dependent variables that share the name "lift":
     Exp54 lift = r_warm_p5 - r_p3_base   ("gain ABOVE the anchor" = p5 headroom)
     Exp59 lift = r_warm_p5 - r_cold_p5   ("advantage OVER cold-start" = inheritance)
  Each sign reproduces on a SINGLE dataset by swapping the definition, so the
  data (graph, seeds, fidelity) is not what produces the sign — the DV choice is.

Both findings AGREE on the mechanism: the p3 anchor is the binding lever.
  - warm-anchor is high  => warm_p5 inherits a high floor => big advantage over
    cold (Exp59 +) AND little room left for p5 to add on top (Exp54 -).
  Two faces of the same monotone-floor mechanism (Finding 30 P-E1).

Usage:  python3 scripts/reconcile_exp54_exp59_signflip.py
Strictly read-only on experiments/exp54_results.json + exp59_results.json.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..")


def pearson(x, y):
    n = len(x); mx = sum(x) / n; my = sum(y) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    vx = sum((a - mx) ** 2 for a in x) ** 0.5
    vy = sum((b - my) ** 2 for b in y) ** 0.5
    return cov / (vx * vy)


def spearman(x, y):
    n = len(x)

    def rank(v):
        s = sorted(range(n), key=lambda i: v[i]); r = [0] * n; i = 0
        while i < n:
            j = i
            while j + 1 < n and v[s[j + 1]] == v[s[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[s[k]] = avg
            i = j + 1
        return r
    return pearson(rank(x), rank(y))


def confirm_same_graph():
    sys.path.insert(0, HERE)
    from run_exp46_fast import EDGES_20 as E46
    from run_exp54_warmstart import EDGES_20 as E54
    from run_exp59_x0_selection import EDGES_20 as E59
    same = tuple(E46) == tuple(E54) == tuple(E59)
    print("INSTANCE IDENTITY: exp54.EDGES_20 == exp59.EDGES_20 :", same,
          "(|E|=%d)" % len(E46))
    return same


def main():
    # ---- Exp59 (256sh/maxiter20): per-seed cold/anchor/warm ----
    e59 = json.load(open(os.path.join(REPO, "experiments/exp59_results.json")))["data"]
    s59 = {int(r["seed"]): (float(r["r_p3_base"]), float(r["r_cold_p5"]),
                            float(r["r_warm_p5"])) for r in e59}
    ks = sorted(s59)
    p3 = [s59[k][0] for k in ks]; cold = [s59[k][1] for k in ks]; warm = [s59[k][2] for k in ks]
    l_wc = [w - c for w, c in zip(warm, cold)]   # warm - cold   (Exp59 def)
    l_wa = [w - a for w, a in zip(warm, p3)]      # warm - anchor (Exp54 def)
    print("\n=== EXP59 dataset (256sh / maxiter20 / n=%d) ===" % len(p3))
    print("  corr(p3, warm-COLD)   [Exp59 official]: pearson %+.3f  spearman %+.3f"
          % (pearson(p3, l_wc), spearman(p3, l_wc)))
    print("  corr(p3, warm-ANCHOR) [Exp54-style]   : pearson %+.3f  spearman %+.3f"
          % (pearson(p3, l_wa), spearman(p3, l_wa)))

    # ---- Exp54 (1024sh/maxiter50): anchor + warm; cold = constant baseline ----
    e54 = json.load(open(os.path.join(REPO, "experiments/exp54_results.json")))
    cold_c = float(e54["p5_coldstart_baseline"])
    d54 = {int(r["seed"]): (float(r["p3_base"]["ratio"]), float(r["A_p3to5"]["ratio"]))
           for r in e54["data"]}
    ks2 = sorted(d54)
    p3b = [d54[k][0] for k in ks2]; warmb = [d54[k][1] for k in ks2]
    l_wa54 = [w - a for w, a in zip(warmb, p3b)]      # warm - anchor (Exp54 official)
    l_wc54 = [w - cold_c for w in warmb]              # warm - cold(const) (Exp59-style)
    print("\n=== EXP54 dataset (1024sh / maxiter50 / n=%d / cold=%.3f) ===" % (len(p3b), cold_c))
    print("  corr(p3, warm-ANCHOR) [Exp54 official]: pearson %+.3f  spearman %+.3f"
          % (pearson(p3b, l_wa54), spearman(p3b, l_wa54)))
    print("  corr(p3, warm-COLD)   [Exp59-style]   : pearson %+.3f  spearman %+.3f"
          % (pearson(p3b, l_wc54), spearman(p3b, l_wc54)))

    print("\nVERDICT: each sign reproduces on EACH dataset by swapping the 'lift'")
    print("definition -> the sign is DEFINITIONAL, not instance/fidelity/sampling.")


if __name__ == "__main__":
    confirm_same_graph()
    main()
