#!/usr/bin/env python3
"""
Exp63: k-adaptive escalation — does escalating k only on a BAD first anchor draw capture
the best-of-k warm-start lift (Finding 36/37) at materially lower expected cost?
Elder C6115 (pre-reg + replay-grade, same cycle).

Pre-registration: experiments/exp63-kadaptive-escalation-preregistration.md
                  DC1.5 state/experiments/c6115-exp63-kadaptive-escalation.json

WHY A REPLAY, NOT A NEW RUN (EVI / measurement-inversion, C6044)
  The adaptive policy is a pure SELECTION rule over anchor draws that ALREADY EXIST in the
  Exp61 (EDGES_20, seeds 42-49) and Exp62 (fresh instances rand101/202/303) results JSONs.
  Per cell we have r_p3_anchors (k pilot recalls), lift_single (warm from anchor 0), and
  lift_best (warm from argmax-of-k). The policy outcome is computed EXACTLY with zero new
  compute. Re-drawing the same anchors via ~11h of FakeMarrakesh sim would be re-measuring a
  known quantity.

POLICY pi_tau (per cell):
  a0 = r_p3_anchors[0]
  if a0 >= tau:  adaptive_lift = lift_single ; k_used = 1
  else:          adaptive_lift = lift_best   ; k_used = k     (escalate -> full-k best)

DESIGN (OOS, disjoint):
  TRAIN = Exp61 EDGES_20 seeds 42-49 (N=8) -> set tau* = median(r_p3_single on train).
  TEST  = Exp62 fresh instances rand101/202/303 (N=9) -> grade capture + cost at tau*.
  (Exp62 EDGES_20_ref seeds 42-44 duplicate Exp61 42-44 -> excluded from test.)

GRADED (by the letter, C5923):
  H1 (PRIMARY): capture >= 0.80 AND mean k_used < 3 on TEST.
  H2 (cost):    mean k_used + % saving (reported).
  H3 (mechanism / non-tautology): capture_adaptive > f (escalation fraction). Random escalation
                of fraction f has expected capture = f; beating it proves a0 selects rescue-cells.

USAGE
  python3 run_exp63_kadaptive_escalation.py --selftest   # policy invariants (no data needed beyond files)
  python3 run_exp63_kadaptive_escalation.py --run         # the graded replay
"""
import sys, os, json, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
E61 = os.path.join(HERE, "..", "experiments", "exp61_results.json")
E62 = os.path.join(HERE, "..", "experiments", "exp62_results.json")
RESULTS = os.path.join(HERE, "..", "experiments", "exp63_results.json")

CAPTURE_BAR = 0.80   # H1 pre-committed
K_FIXED = 3          # fixed-k baseline cost


def load_cells():
    e61 = json.load(open(E61))
    e62 = json.load(open(E62))
    train = [r for r in e61["data"]]                       # EDGES_20 seeds 42-49
    test = [r for r in e62["data"] if r["instance"] != "EDGES_20_ref"]  # fresh instances only
    # sanity: all k=3
    assert all(r["k"] == K_FIXED for r in train + test), "expected k=3 throughout"
    return train, test


def policy_outcome(cell, tau, k):
    """Return (adaptive_lift, k_used) for one cell under threshold tau."""
    a0 = cell["r_p3_anchors"][0]
    if a0 >= tau:
        return cell["lift_single"], 1
    return cell["lift_best"], k


def evaluate(cells, tau, k):
    lift_single = np.array([c["lift_single"] for c in cells], float)
    lift_best = np.array([c["lift_best"] for c in cells], float)
    adaptive = np.array([policy_outcome(c, tau, k)[0] for c in cells], float)
    k_used = np.array([policy_outcome(c, tau, k)[1] for c in cells], float)
    D_fixed = float(lift_best.mean() - lift_single.mean())
    D_adapt = float(adaptive.mean() - lift_single.mean())
    f = float(np.mean([1.0 if c["r_p3_anchors"][0] < tau else 0.0 for c in cells]))
    capture = (D_adapt / D_fixed) if abs(D_fixed) > 1e-9 else None
    return {
        "n": len(cells),
        "D_fixed": D_fixed,
        "D_adaptive": D_adapt,
        "capture": capture,
        "mean_k_used": float(k_used.mean()),
        "escalate_frac": f,
        "mean_lift_single": float(lift_single.mean()),
        "mean_lift_best": float(lift_best.mean()),
        "mean_adaptive_lift": float(adaptive.mean()),
    }


def frontier(cells, k):
    """capture vs cost across a tau sweep (honest context, not graded)."""
    a0s = sorted(set(c["r_p3_anchors"][0] for c in cells))
    # tau candidates: just below/above each distinct a0, plus +/-inf
    taus = [-np.inf] + [a + 1e-6 for a in a0s] + [np.inf]
    rows = []
    for tau in taus:
        ev = evaluate(cells, tau, k)
        rows.append({"tau": (None if not np.isfinite(tau) else round(tau, 5)),
                     "tau_kind": ("-inf" if tau == -np.inf else "+inf" if tau == np.inf else "finite"),
                     "capture": ev["capture"], "mean_k_used": ev["mean_k_used"],
                     "escalate_frac": ev["escalate_frac"]})
    return rows


def selftest():
    train, test = load_cells()
    k = K_FIXED
    ok = True
    # policy: a0 >= tau -> use single (don't escalate); a0 < tau -> escalate.
    # tau=-inf  -> no cell has a0<-inf -> NEVER escalate -> capture 0, cost 1.
    # tau=+inf  -> every cell a0<+inf  -> ALWAYS escalate -> capture 1, cost k.
    for name, cells in (("train", train), ("test", test)):
        ev_neg = evaluate(cells, -np.inf, k)   # never escalate
        ev_pos = evaluate(cells, np.inf, k)    # always escalate
        c1 = abs(ev_neg["D_adaptive"]) < 1e-9          # never escalate -> D_adapt 0
        c2 = abs(ev_neg["mean_k_used"] - 1.0) < 1e-9   # cost 1
        c3 = (ev_pos["capture"] is None) or abs(ev_pos["capture"] - 1.0) < 1e-9  # always -> capture 1
        c4 = abs(ev_pos["mean_k_used"] - k) < 1e-9     # cost k
        passed = c1 and c2 and c3 and c4
        ok = ok and passed
        print(f"  [{name}] tau=-inf D_adapt={ev_neg['D_adaptive']:+.4f} cost={ev_neg['mean_k_used']:.3f} | "
              f"tau=+inf capture={ev_pos['capture']} cost={ev_pos['mean_k_used']:.3f} "
              f"-> {'PASS' if passed else 'FAIL'}")
    print(f"SELFTEST: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    if not args.run:
        print("Specify --run | --selftest. Refusing to guess.")
        sys.exit(2)

    train, test = load_cells()
    k = K_FIXED

    # --- pre-committed tau* = median first-anchor recall on TRAIN ---
    train_a0 = np.array([c["r_p3_single"] for c in train], float)
    tau_star = float(np.median(train_a0))

    print("=" * 72)
    print("Exp63 k-adaptive escalation — graded replay (NO new compute)")
    print("=" * 72)
    print(f"TRAIN = EDGES_20 Exp61 seeds {[c['seed'] for c in train]} (N={len(train)})")
    print(f"TEST  = Exp62 fresh instances {sorted(set(c['instance'] for c in test))} (N={len(test)})")
    print(f"tau* = median(r_p3_single | train) = {tau_star:.5f}")
    print(f"  train first-anchor recalls: {[round(float(x),4) for x in sorted(train_a0)]}")
    print("-" * 72)

    train_ev = evaluate(train, tau_star, k)
    test_ev = evaluate(test, tau_star, k)

    for name, ev in (("TRAIN (in-sample)", train_ev), ("TEST (OOS)", test_ev)):
        cap = "n/a (D_fixed~0)" if ev["capture"] is None else f"{ev['capture']:+.3f}"
        print(f"\n  [{name}] N={ev['n']}")
        print(f"    mean lift_single={ev['mean_lift_single']:+.4f}  "
              f"mean lift_best(fixed-k)={ev['mean_lift_best']:+.4f}  "
              f"D_fixed={ev['D_fixed']:+.4f}")
        print(f"    mean adaptive_lift={ev['mean_adaptive_lift']:+.4f}  "
              f"D_adaptive={ev['D_adaptive']:+.4f}")
        print(f"    capture={cap}  escalate_frac f={ev['escalate_frac']:.3f}  "
              f"mean k_used={ev['mean_k_used']:.3f} (fixed={k})")

    # ---- grade on TEST ----
    cap = test_ev["capture"]
    f = test_ev["escalate_frac"]
    cost = test_ev["mean_k_used"]
    saving = (1.0 - cost / k)

    near_zero_dfixed = abs(test_ev["D_fixed"]) < 0.005
    h1 = (cap is not None) and (cap >= CAPTURE_BAR) and (cost < k) and (not near_zero_dfixed)
    h3 = (cap is not None) and (cap > f) and (not near_zero_dfixed)

    print("\n" + "=" * 72)
    print("VERDICTS (graded by the letter on TEST, C5923)")
    print("=" * 72)
    if near_zero_dfixed:
        print(f"  [!] TEST D_fixed={test_ev['D_fixed']:+.4f} is near-zero -> capture ratio "
              f"UNSTABLE. NULL-consistent; do NOT manufacture a capture %. (C6051/C5958)")
    print(f"  H1 (capture>={CAPTURE_BAR:.2f} AND k_used<{k}): "
          f"capture={cap if cap is None else round(cap,3)} cost={cost:.3f} "
          f"-> {'SUPPORTED' if h1 else 'REFUTED/NULL'}")
    print(f"  H2 (cost): mean k_used={cost:.3f} of {k} -> {saving*100:.1f}% compute saving "
          f"(escalated {f*100:.0f}% of cells)")
    print(f"  H3 (capture > escalate_frac f={f:.3f}, beats cost-matched random): "
          f"{'SUPPORTED' if h3 else 'REFUTED/NULL'} "
          f"(adaptive captures {cap if cap is None else round(cap,3)} vs random {f:.3f})")

    out = {
        "experiment": "Exp63", "title": "k-adaptive escalation of best-of-k warm-start anchor selection",
        "author": "Elder", "cycle": "C6115", "compute": "NONE (replay over Exp61+Exp62)",
        "k_fixed": k, "capture_bar": CAPTURE_BAR, "tau_star": tau_star,
        "tau_rule": "median(r_p3_single | train)",
        "train": {"source": "exp61_results.json EDGES_20 seeds 42-49", **train_ev},
        "test": {"source": "exp62_results.json fresh instances rand101/202/303", **test_ev},
        "test_compute_saving_frac": saving,
        "verdicts": {
            "H1_supported": bool(h1), "H3_supported": bool(h3),
            "test_D_fixed_near_zero": bool(near_zero_dfixed),
        },
        "frontier_train": frontier(train, k),
        "frontier_test": frontier(test, k),
    }
    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"\n  Wrote {RESULTS}")


if __name__ == "__main__":
    main()
