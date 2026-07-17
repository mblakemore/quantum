#!/usr/bin/env python3
"""Exp144 FINGERPRINT-GATED LAYOUT (Ember) — freeze sequence step 4, prereg §8.

RULE (frozen, quoted): "Exclude any candidate Bell-pair whose raw-idle error > 2x cohort
median at the 5us arm." Arm selection was made from TRANSPILED DURATION (Elder C6512:
circuits ~4.5/6.3/8.0us at n=4/6/8, so the 1us and 5us fingerprint arms bracket the real
exposure -> gate on 5us, conservative). Both Exp143 outliers (q2-q3, q148-q149) must fall
out at this arm — that is the check that the rule reproduces the finding it came from.

WHY THIS GATE EXISTS AT ALL: the calibration-gated picker keys on gate+readout error and
is BLIND to raw-idle dephasing. Exp143 found pairs that look calibration-perfect (T2
110-284us, "healthy") yet lose 66-96% at a 5us idle. Kingston's own picker selected them
FOR that apparent health. ~5 QPU-s of fingerprint buys exclusion of pairs no amount of
calibration reading would flag.

I do NOT re-derive the arm or the threshold — both are frozen. This applies them.

  python3 exp144_layout_gate_ember.py
"""
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FP = os.path.join(HERE, "..", "results", "exp143_fingerprint.json")

ARM = "D5"          # frozen: 5us arm (C6512, from transpiled duration)
MULT = 2.0          # frozen: > 2x cohort median -> excluded
KNOWN_OUTLIERS = [(2, 3), (148, 149)]   # Exp143's named pairs; must be excluded by the rule


def main():
    with open(FP) as f:
        d = json.load(f)

    pairs = [tuple(p) for p in d["manifest"]["physical_pairs"]]
    errs = d["results"][ARM]["p_err_per_pair"]
    if len(pairs) != len(errs):
        print(f"REFUSING: {len(pairs)} pairs vs {len(errs)} error values — shape mismatch")
        return 2

    med = statistics.median(errs)
    cut = MULT * med
    print(f"=== §8 fingerprint gate — arm {ARM} (5us), backend {d['manifest']['backend']} ===")
    print(f"cohort median idle error: {med:.4f}  ->  exclusion cut: >{cut:.4f} (2x median)")
    print()

    keep, drop = [], []
    for p, e in sorted(zip(pairs, errs), key=lambda x: x[1]):
        (drop if e > cut else keep).append((p, e))

    for p, e in drop:
        print(f"  EXCLUDE  q{p[0]}-q{p[1]:<4} idle {e*100:6.2f}%   ({e/med:.1f}x median)")
    print(f"  ---- {len(keep)} pairs pass ----")
    for p, e in keep[:6]:
        print(f"  keep     q{p[0]}-q{p[1]:<4} idle {e*100:6.2f}%")
    if len(keep) > 6:
        print(f"  ... and {len(keep)-6} more")

    # The rule must reproduce the finding that motivated it. If Exp143's named outliers
    # survive this cut, either the threshold or the arm is wrong — do not fly on it.
    print("\n=== does the frozen rule reproduce Exp143's named outliers? ===")
    dropped = {p for p, _ in drop}
    ok = True
    for o in KNOWN_OUTLIERS:
        hit = o in dropped or o[::-1] in dropped
        ok &= hit
        print(f"  q{o[0]}-q{o[1]}: {'EXCLUDED ✅' if hit else 'SURVIVED ❌ — rule does not reproduce its own finding'}")

    # Capacity: n=8 needs 8 Bell pairs (+ conv layout). If the gate leaves too few, the
    # flight cannot proceed on this fingerprint and that is a real blocker, not a nuisance.
    need = 8
    print(f"\n=== capacity: n=8 needs {need} pairs, gate leaves {len(keep)} ===")
    enough = len(keep) >= need
    print(f"  {'SUFFICIENT ✅' if enough else 'INSUFFICIENT ❌ — cannot fly n=8 on this fingerprint'}")

    out = os.path.join(HERE, "..", "results", "exp144_layout_gated_ember.json")
    with open(out, "w") as f:
        json.dump({"_meta": "Exp144 §8 fingerprint-gated layout (Ember). Arm D5 (5us, frozen "
                            "C6512 from transpiled duration); exclude >2x cohort median.",
                   "source_fingerprint": "results/exp143_fingerprint.json",
                   "arm": ARM, "cohort_median": med, "cut": cut,
                   "excluded": [{"pair": list(p), "idle_err": e} for p, e in drop],
                   "eligible": [{"pair": list(p), "idle_err": e} for p, e in keep]}, f, indent=1)
    print(f"\nwrote {out}")

    good = ok and enough
    print(f"\nLAYOUT GATE: {'PASS' if good else 'FAIL'}")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
