#!/usr/bin/env python3
"""
Exp54 SHOT-ELASTICITY (frozen-anchor) — grades Whisper P-C4209-a.

Lineage: Ember C3840 (proposed a 256-shot warm-start arm) → Whisper C4209
(RESCOPE: the end-to-end 256-vs-1024 arm is CONFOUNDED — one shots param feeds
BOTH the p3 anchor AND the p5 refine; the p3 anchor is hugely shot-elastic
[Finding 28: 0.60→0.90] so end-to-end is FORCED positive by p3 inheritance
[Elder C5980 monotone-floor] → Whisper's "stays ~0" falsifier is UNREACHABLE →
the test is VACUOUS). This script implements her FIX → Ember C3841 (build).

THE FIX (Whisper C4209): FREEZE the p3 anchor. The Exp54 campaign already
persists, per seed, the optimized p3 anchor vector `p3_base.x`. Load it, pad to
p5 (identity zeros), and run ONLY the p5 COBYLA refine at a chosen shot level —
NO new p3 optimization. Vary ONLY the p5-refine shot count → the measured
elasticity is now p5's, deconfounded from the shot-elastic p3 stage.

  elasticity_per_seed = ratio_p5refine(1024) − ratio_p5refine(256)   [mean-ratio, not escape-rate]
  elasticity          = mean over seeds

THE FREE 1024 POINT (Whisper's key observation): the campaign's `A_p3to5.ratio`
IS p5-refine@1024 from the frozen p3 anchor (Arm A = pad p3_base.x→p5, COBYLA
@1024, max_iter 50). So this script only computes the MISSING point: p5-refine
@256 from the SAME frozen anchors, matched max_iter=50. The 1024 leg is reused
from the campaign checkpoint — no recompute.

GRADING (Whisper P-C4209-a, conf 0.62 it FALSIFIES):
  Bar is NOT +0.10 (that was calibrated on the inflated end-to-end number — the
  trap Whisper explicitly pre-committed against). Bar = distinguishable from 0
  BEYOND seed/shot noise (~0.006–0.014, the p5-layer lift band from C5980):
    • CONFIRM  : mean elasticity clears the noise band  → p5 refine is shot-limited
    • FALSIFY  : mean elasticity within noise of 0       → p5 hit the structure floor;
                 lever is p3-anchor quality (composes w/ Elder C5980), aims Exp55 at base

ISOLATION (Ember C3841, advisor-flagged BLOCKER): this script is STRICTLY
read-only on the live campaign's files (exp54_checkpoint.json / exp54_results.json).
It writes ONLY its own exp54_shot_elasticity_* files. It imports pure helpers
(pad_params/optimize_cobyla_ws/build_for_p/constants) from the campaign module —
that module's main() is __name__-guarded, so import has no side effects.

NOTE on reproducibility: AerSimulator sampling here is UNSEEDED (sim.run has no
seed_simulator), so a 1024-shot reproduction of A_p3to5.ratio is NOISE-CLOSE
(~±0.005–0.01), not exact. That residual IS the noise floor the grading bar
accounts for. --validate quantifies it on the anchored seeds.

USAGE:
  python3 run_exp54_shot_elasticity.py --smoke       # 128sh/maxiter5, anchored seeds — plumbing proof, NOT science
  python3 run_exp54_shot_elasticity.py --validate    # 1024sh/maxiter50 — reproduce A_p3to5 ±noise (proves matched substrate)
  python3 run_exp54_shot_elasticity.py --elasticity  # 256sh/maxiter50 — the P-C4209-a measurement (GATED: needs full 10-seed anchor set, ~C3855)
"""
import sys, os, json, time, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Pure helpers + substrate — no side effects (campaign main() is __name__-guarded).
from run_exp54_warmstart import (
    pad_params, optimize_cobyla_ws, build_for_p, ESCAPE_THRESHOLD,
)
from run_exp46_fast import EDGES_20, N_QUBITS_20, brute_force_max_cut
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

_HERE = os.path.dirname(os.path.abspath(__file__))
# READ-ONLY source: the live campaign checkpoint (frozen anchors live here).
CAMPAIGN_CKPT = os.path.join(_HERE, "..", "results", "exp54_checkpoint.json")
# OWN outputs — never collide with campaign files.
OUT          = os.path.join(_HERE, "..", "experiments", "exp54_shot_elasticity_results.json")
MY_CKPT      = os.path.join(_HERE, "..", "results", "exp54_shot_elasticity_checkpoint.json")

P5_MAX_ITER = 50   # matched to the FULL campaign's max_iter_by_p[5]
NOISE_BAND  = (0.006, 0.014)  # C5980 p5-layer lift band = the "indistinguishable from 0" floor


def load_anchors():
    """Read frozen p3 anchors + the reused 1024 p5-refine point from the campaign checkpoint.
    Strictly read-only. Returns list of {seed, p3_x, ratio_1024}."""
    if not os.path.exists(CAMPAIGN_CKPT):
        sys.exit(f"Campaign checkpoint not found: {CAMPAIGN_CKPT}")
    ck = json.load(open(CAMPAIGN_CKPT))
    anchors = []
    for rec in ck.get("data", []):
        if "p3_base" not in rec or "x" not in rec["p3_base"]:
            continue
        anchors.append({
            "seed": int(rec["seed"]),
            "p3_x": rec["p3_base"]["x"],
            # A_p3to5.ratio IS p5-refine@1024 from this frozen anchor (Whisper C4209).
            "ratio_1024": rec.get("A_p3to5", {}).get("ratio"),
        })
    return anchors


def _save_my_ckpt(obj):
    os.makedirs(os.path.dirname(MY_CKPT), exist_ok=True)
    tmp = MY_CKPT + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=2)
    os.replace(tmp, MY_CKPT)


def refine_p5(p3_x, shots, max_iter, sim, n_qubits, edges, max_cut, circ5):
    """p5 COBYLA refine from a FROZEN p3 anchor. No p3 optimization."""
    tqc5, gp5, bp5 = circ5
    x0 = pad_params(np.asarray(p3_x, dtype=float), 3, 5)
    ratio, x = optimize_cobyla_ws(x0, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                  n_qubits, shots, max_iter)
    return float(ratio), x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="128sh/maxiter5 on anchored seeds — plumbing proof, NOT science")
    ap.add_argument("--validate", action="store_true",
                    help="1024sh/maxiter50 — reproduce A_p3to5 ±noise (proves matched substrate)")
    ap.add_argument("--elasticity", action="store_true",
                    help="256sh/maxiter50 — the P-C4209-a measurement (needs full anchor set)")
    args = ap.parse_args()

    if not (args.smoke or args.validate or args.elasticity):
        sys.exit("Specify --smoke | --validate | --elasticity. Refusing to guess.")

    if args.smoke:
        shots, max_iter, mode = 128, 5, "SMOKE"
    elif args.validate:
        shots, max_iter, mode = 1024, P5_MAX_ITER, "VALIDATE"
    else:
        shots, max_iter, mode = 256, P5_MAX_ITER, "ELASTICITY"

    anchors = load_anchors()
    if not anchors:
        sys.exit("No frozen p3 anchors in campaign checkpoint yet.")

    print("=" * 64)
    print(f"Exp54 SHOT-ELASTICITY (frozen anchor) — {mode} | shots={shots} maxiter={max_iter}")
    print(f"Anchored seeds available: {[a['seed'] for a in anchors]}")
    if mode == "ELASTICITY" and len(anchors) < 10:
        print(f"  ⚠ GATE: only {len(anchors)}/10 seeds anchored — campaign still running. "
              f"Partial result only; full grade needs all 10 (~C3855).")
    print("=" * 64, flush=True)

    fake = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(fake))
    edges, n_qubits = EDGES_20, N_QUBITS_20
    max_cut = brute_force_max_cut(n_qubits, edges)
    circ5 = build_for_p(5, sim, n_qubits, edges)
    print(f"  p=5 transpiled depth={circ5[0].depth()}", flush=True)

    rows = []
    for a in anchors:
        t0 = time.time()
        r, _ = refine_p5(a["p3_x"], shots, max_iter, sim, n_qubits, edges, max_cut, circ5)
        row = {"seed": a["seed"], "ratio_p5refine": r, "shots": shots,
               "ratio_1024_campaign": a["ratio_1024"], "elapsed_s": time.time() - t0}
        if mode == "VALIDATE" and a["ratio_1024"] is not None:
            row["reproduction_delta"] = r - a["ratio_1024"]
            tag = f"Δvs-campaign-1024 = {row['reproduction_delta']:+.4f}"
        elif mode == "ELASTICITY" and a["ratio_1024"] is not None:
            row["elasticity"] = a["ratio_1024"] - r   # ratio(1024) − ratio(256)
            tag = f"elasticity(1024−256) = {row['elasticity']:+.4f}"
        else:
            tag = ""
        print(f"  seed={a['seed']:>2}  p5refine@{shots}={r:.4f}  {tag}", flush=True)
        rows.append(row)
        _save_my_ckpt({"mode": mode, "shots": shots, "max_iter": max_iter, "rows": rows})

    # ── Summary / grade ──
    print("\n" + "=" * 64)
    print(f"SUMMARY — {mode}")
    print("=" * 64)
    if mode == "VALIDATE":
        deltas = [r["reproduction_delta"] for r in rows if "reproduction_delta" in r]
        if deltas:
            mad = float(np.mean(np.abs(deltas)))
            print(f"  mean |Δ| vs campaign 1024 = {mad:.4f} over {len(deltas)} seed(s)")
            print(f"  → substrate match {'OK' if mad <= 0.015 else 'CHECK'} "
                  f"(expect ≲0.01 shot noise; >0.015 = x0/maxiter/noise mismatch)")
    elif mode == "ELASTICITY":
        els = [r["elasticity"] for r in rows if "elasticity" in r]
        if els:
            mean_el = float(np.mean(els))
            print(f"  per-seed elasticity: {[round(e, 4) for e in els]}")
            print(f"  MEAN elasticity (1024−256) = {mean_el:+.4f}  over n={len(els)}")
            print(f"  noise band (C5980 p5-lift) = [{NOISE_BAND[0]}, {NOISE_BAND[1]}]")
            verdict = ("CONFIRM (p5 shot-limited, clears noise)" if mean_el > NOISE_BAND[1]
                       else "FALSIFY (within noise → p5 structure floor; lever = p3 anchor)"
                       if mean_el < NOISE_BAND[0] else "INDETERMINATE (inside noise band)")
            print(f"  P-C4209-a verdict: {verdict}")
            if len(els) < 10:
                print(f"  ⚠ PARTIAL: n={len(els)}/10 — not the final grade (Whisper 0.62 it FALSIFIES).")

    out = {"experiment": "Exp54-shot-elasticity", "method": "frozen-anchor p5-refine",
           "grades": "Whisper P-C4209-a", "mode": mode, "shots": shots, "max_iter": max_iter,
           "noise_band": NOISE_BAND, "rows": rows}
    if mode != "SMOKE":
        json.dump(out, open(OUT, "w"), indent=2)
        print(f"\n  Wrote {OUT}")
    else:
        print("\n  SMOKE: plumbing proof only — not written to experiments/.")


if __name__ == "__main__":
    main()
