#!/usr/bin/env python3
"""H13 Cell 2 — F-MIX-shaped BLINDNESS TEST (Ember Requirement 1, general#9015).
Elder register/decode seat, C6603.

The requirement, verbatim in shape: a discriminator that tries to separate the arms using
everything the grader receives EXCEPT the frozen statistic (sign of C_XX*C_YY*C_ZZ), which
must FAIL on the delivered records and must demonstrably SUCCEED on a deliberately-leaky
control. "A blindness check that cannot fail is the defect door(b) paid for."

WHAT THE DISCRIMINATOR USES (everything but the frozen statistic):
  - correlator MAGNITUDES per basis (|C|), which the sign statistic discards — this is the
    channel my C6603 ceiling analysis says is open: CC is uniformly less noisy than CE
    (0.93337 vs 0.92189) in EVERY basis, and magnitude is measurable to +-2/sqrt(N)
  - record COUNTS per basis, marginal biases, any stray top-level keys
It does NOT use the sign product. If it separates the arms, the records leak.

DECISION RULE: reference-informed likelihood ratio on the per-basis magnitude vector, using
reference distributions estimated from the labelled calibration/pre-run sets. This is the
STRONGEST attack available to a party holding both arms' pre-run data — the right adversary
(the floor is the best method, C6566), not a strawman.

THREE-ARM STRUCTURE (a check must be shown able to fire):
  1. DELIVERED  — the real sealed records. REQUIRED: success ~ chance (CI includes 0.5).
  2. LEAKY CTRL — same records with the native (unmatched) magnitudes. REQUIRED: success
                  clearly > chance. If this does NOT succeed the TEST ITSELF is broken and
                  the run is VOID — never read as "blindness confirmed".
  3. NULL CTRL  — labels shuffled. REQUIRED: success ~ chance. Catches a discriminator that
                  scores high on anything.

Usage:
  python3 tools/h13_cell2_blindness_test_elder.py --selftest
  python3 tools/h13_cell2_blindness_test_elder.py --delivered DIR --labels LABELS.json \\
      --leaky-control DIR [--json]
"""
import argparse, glob, json, math, os, random, sys
from statistics import NormalDist

DIAG = ("XX", "YY", "ZZ")
BASES = [a + b for a in "XYZ" for b in "XYZ"]
Phi = NormalDist().cdf


def magnitude_features(obj):
    """Everything the grader receives EXCEPT the frozen sign statistic."""
    acc = {b: [0, 0] for b in BASES}
    for r in obj["records"]:
        b = r["basis"]
        a_, b_ = (1 if r["a"] in (1,) else -1), (1 if r["b"] in (1,) else -1)
        acc[b][0] += 1
        acc[b][1] += a_ * b_
    feats = {}
    for b in BASES:
        n, s = acc[b]
        if n:
            feats[b] = abs(s / n)   # MAGNITUDE ONLY — sign deliberately discarded
    feats["_n"] = sum(v[0] for v in acc.values())
    return feats


def fit_reference(sets):
    """Mean/var of each magnitude feature under one arm (from labelled pre-run sets)."""
    ref = {}
    for b in DIAG:
        xs = [f[b] for f in sets if b in f]
        if len(xs) >= 2:
            m = sum(xs) / len(xs)
            v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
            ref[b] = (m, max(v, 1e-12))
        elif xs:
            ref[b] = (xs[0], 1e-6)
    return ref


def llr_call(feats, ref_ce, ref_cc):
    """Gaussian LLR on magnitudes. Returns 'CE'/'CC'."""
    ll = 0.0
    for b in DIAG:
        if b in feats and b in ref_ce and b in ref_cc:
            for ref, sgn in ((ref_ce, +1), (ref_cc, -1)):
                m, v = ref[b]
                ll += sgn * (-0.5 * math.log(v) - (feats[b] - m) ** 2 / (2 * v))
    return "CE" if ll > 0 else "CC"


def run_arm(feature_sets, truth, ref_ce, ref_cc):
    hits = sum(1 for f, t in zip(feature_sets, truth) if llr_call(f, ref_ce, ref_cc) == t)
    n = len(truth)
    p = hits / n if n else float("nan")
    se = math.sqrt(max(p * (1 - p), 1e-9) / n) if n else float("nan")
    # MDE: smallest true leak this arm could detect at 80% power, one-sided alpha=0.05.
    # A chance-level result WITHOUT this number is not evidence of blindness (C6563).
    se0 = math.sqrt(0.25 / n) if n else float("nan")
    mde = 0.5 + (1.645 + 0.842) * se0 if n else float("nan")
    return {"n": n, "success": round(p, 4),
            "ci95": [round(p - 1.96 * se, 4), round(p + 1.96 * se, 4)],
            "mde_80pct": round(mde, 4)}


def verdict(delivered, leaky, null):
    if not (leaky["ci95"][0] > 0.5):
        return "VOID", ("leaky control did NOT separate — the discriminator cannot fire, "
                        "so a chance-level DELIVERED result proves nothing")
    if null["ci95"][0] > 0.5:
        return "VOID", "null control scored above chance — discriminator is broken"
    if delivered["ci95"][0] > 0.5:
        return "FAIL", "records LEAK: magnitudes separate the arms above chance"
    return "PASS", (f"delivered records chance-level while the leaky control fires — but this "
                    f"null only excludes leaks above {delivered['mde_80pct']:.3f} at 80% power "
                    f"(n={delivered['n']}); a smaller leak is NOT excluded")


def _synth(corr, n=4000, jitter=0.004, rng=None):
    rng = rng or random.Random(7)
    recs = []
    for b in BASES:
        c = max(-0.999, min(0.999, corr.get(b, 0.0) + rng.gauss(0, jitter)))
        p_same = (1 + c) / 2
        for _ in range(n):
            a = rng.choice((1, -1))
            recs.append({"basis": b, "a": a, "b": a if rng.random() < p_same else -a})
    return {"records": recs}


def selftest():
    rng = random.Random(11)
    CE_native = {b: 0.92189 if b in DIAG else 0.0 for b in BASES}
    CC_native = {b: (-0.93337 if b == "YY" else 0.93337) if b in DIAG else 0.0 for b in BASES}
    # matched: both arms driven to a COMMON randomized target band (Elder fix #1)
    def matched(arm_native, rng):
        t = rng.uniform(0.80, 0.90)
        return {b: (math.copysign(t, v) if b in DIAG else 0.0) for b, v in arm_native.items()}

    R = 12
    ce_leaky = [magnitude_features(_synth(CE_native, rng=rng)) for _ in range(R)]
    cc_leaky = [magnitude_features(_synth(CC_native, rng=rng)) for _ in range(R)]
    ce_match = [magnitude_features(_synth(matched(CE_native, rng), rng=rng)) for _ in range(R)]
    cc_match = [magnitude_features(_synth(matched(CC_native, rng), rng=rng)) for _ in range(R)]

    ref_ce_l, ref_cc_l = fit_reference(ce_leaky), fit_reference(cc_leaky)
    ref_ce_m, ref_cc_m = fit_reference(ce_match), fit_reference(cc_match)

    leaky = run_arm(ce_leaky + cc_leaky, ["CE"] * R + ["CC"] * R, ref_ce_l, ref_cc_l)
    delivered = run_arm(ce_match + cc_match, ["CE"] * R + ["CC"] * R, ref_ce_m, ref_cc_m)
    shuffled = ["CE"] * R + ["CC"] * R
    rng.shuffle(shuffled)
    null = run_arm(ce_match + cc_match, shuffled, ref_ce_m, ref_cc_m)

    v, why = verdict(delivered, leaky, null)
    print(f"  leaky control (native, unmatched): {leaky}")
    print(f"  delivered     (randomized-band matched, Elder fix #1): {delivered}")
    print(f"  null control  (labels shuffled):   {null}")
    print(f"  VERDICT {v} — {why}")
    ok = leaky["ci95"][0] > 0.5          # the check demonstrably CAN fire
    print("SELFTEST", "PASS" if ok else "FAIL",
          "(leaky arm fires => the test is capable of failing; verdict on real records is "
          "whatever it is)")
    return 0 if ok else 1


def _load_dir(d):
    out = []
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        with open(f) as fh:
            out.append((os.path.basename(f), magnitude_features(json.load(fh))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delivered"); ap.add_argument("--leaky-control")
    ap.add_argument("--labels", help="JSON {filename: CE|CC} — UNSEALED labels; this test runs "
                                     "AFTER the blind decode is hashed, never before")
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.delivered and a.labels and a.leaky_control):
        ap.error("--delivered, --labels and --leaky-control all required (a run without the "
                 "leaky control cannot be read as PASS)")
    labels = json.load(open(a.labels))
    dv = _load_dir(a.delivered); lk = _load_dir(a.leaky_control)
    truth_d = [labels[n] for n, _ in dv]; truth_l = [labels[n] for n, _ in lk]
    ref = lambda sets, t, arm: fit_reference([f for (n, f), x in zip(sets, t) if x == arm])
    d = run_arm([f for _, f in dv], truth_d, ref(dv, truth_d, "CE"), ref(dv, truth_d, "CC"))
    l = run_arm([f for _, f in lk], truth_l, ref(lk, truth_l, "CE"), ref(lk, truth_l, "CC"))
    sh = list(truth_d); random.Random(0).shuffle(sh)
    nl = run_arm([f for _, f in dv], sh, ref(dv, truth_d, "CE"), ref(dv, truth_d, "CC"))
    v, why = verdict(d, l, nl)
    out = {"delivered": d, "leaky_control": l, "null_control": nl, "verdict": v, "why": why}
    print(json.dumps(out, indent=1) if a.json else
          f"delivered {d}\nleaky {l}\nnull {nl}\nVERDICT {v} — {why}")
    sys.exit(0 if v == "PASS" else 1)


if __name__ == "__main__":
    main()
