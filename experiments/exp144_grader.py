#!/usr/bin/env python3
"""Exp144 GRADER (freeze candidate — SHA256 recorded in prereg at freeze; no edits
post-freeze; post-flight bugs reported alongside results, never patched silently).

Vector shape per prereg v2 §5/§6 (Elder C6511):
  - 15 instances: n in {4,6,8} x k in {1..5}.
  - verify_commitment: RE-SERIALIZES terms/coeffs from the reveal record per the §6
    normative rules (terms lexicographic ascending; coeffs same index order, %+.2f)
    and checks sha256(salt || utf8("exp144|dynamics_fullweight_m3|{n}|{k}|{terms}|{coeffs}"))
    against the commitment record's SINGLE key "sha256" (FR-2: no bridge, no aliases).
  - Instance PASS (quantum): support set exact AND every signed coeff within TAU,
    AND budget conformity shots == 5*M_BELL[n].
  - Rung metric: MEDIAN ratio over K=5 (ratio_i = conv_meter_i / quantum_budget),
    reported with IQR. Rung WIN (n in {6,8}) = PASS on >= 4/5 AND median >= R_THRESHOLD.
  - THREE SCORED RUNGS (chair C4780): n=4 scored vs R(4) but NOT in the overall
    conjunction; n4 median outside the pre-registered TWO-SIDED band raises
    METER_MISCALIBRATION_FLAG. n=8 = predicted-ceiling rung: conv unresolved at
    CONV_CEILING -> ratio = LOWER BOUND (CEILING_RATIO). Pre-registered ratio
    bands + slope(6/4) band reported as a predictions scorecard.
  - Overall WIN = n6 WIN AND n8 WIN.
  - Verdict = JSON stdout (exit codes are NOT verdicts — Elder C6494).

Usage:
  python3 exp144_grader.py <commitments_dir> <answers_dir>
  python3 exp144_grader.py --selftest
Files:
  commitments_dir: commit_dynamics_fullweight_m3_n{N}_k{K}.json
                   reveal_dynamics_fullweight_m3_n{N}_k{K}.json
  answers_dir:     answers_n{N}_k{K}.json
    {"n":N,"instance":K,
     "quantum":{"terms":[...],"coeffs":[...],"shots_budget":int},
     "conventional":{"identified":bool,"terms":[...]|null,"coeffs":[...]|null,
                     "meter":float|null,"overage_submitted":int}}
"""
import hashlib
import json
import os
import statistics
import sys
import tempfile

ENSEMBLE = "dynamics_fullweight_m3"
NS = (4, 6, 8)
KS = (1, 2, 3, 4, 5)
TAU = 0.03

# ---- FROZEN CONSTANTS (freeze candidate v2, C6519 — MC v2, chair C4780/C4781) ----
M_BELL = {4: 1000, 6: 1000, 8: 1000}            # FROZEN C6508 (power calc B3)
R_THRESHOLD = {4: 2.0, 6: 1.5, 8: 10.0}          # 3 scored rungs (C4780 ruling 1)
CONV_CEILING = 1_000_000                          # per-instance conv cap (C4781 ruling 1)
CEILING_RATIO = CONV_CEILING / 5000               # = 200.0, LOWER-BOUND ratio semantics
RATIO_BANDS = {4: (7.4, 11.5), 6: (68.2, 98.5)}   # pre-registered (MC v2 C6519, eps=0.02)
SLOPE_64_BAND = (6.4, 12.1)                       # ratio(6)/ratio(4); asymptote 9
# n4 flag is TWO-SIDED (C4780 ruling 3): flown median outside RATIO_BANDS[4]
# in EITHER direction = METER_MISCALIBRATION_FLAG.
# n8 = PREDICTED-CEILING rung: conv expected NOT to resolve within CONV_CEILING;
# resolution within ceiling = cost model wrong (reported, not suppressed).
# ---------------------------------------------------------------------


def serialize_vector(terms, coeffs):
    """§6 NORMATIVE serialization. Terms sorted lexicographic ascending; coeffs
    follow the SAME permutation; coeffs formatted %+.2f. Returns (terms_csv, coeffs_csv)."""
    if len(terms) != len(coeffs):
        raise ValueError("terms/coeffs length mismatch")
    order = sorted(range(len(terms)), key=lambda i: terms[i])
    t_sorted = [terms[i] for i in order]
    c_sorted = [coeffs[i] for i in order]
    return ",".join(t_sorted), ",".join(f"{c:+.2f}" for c in c_sorted)


def preimage_string(n, k, terms, coeffs):
    t_csv, c_csv = serialize_vector(terms, coeffs)
    return f"exp144|{ENSEMBLE}|{n}|{k}|{t_csv}|{c_csv}"


def verify_commitment(commit_path, reveal_path):
    """Returns (ok, terms_sorted, coeffs_sorted). Single key 'sha256' (FR-2)."""
    with open(commit_path) as f:
        c = json.load(f)
    with open(reveal_path) as f:
        r = json.load(f)
    pre = bytes.fromhex(r["salt_hex"]) + \
        preimage_string(int(r["n"]), int(r["instance"]), r["terms"], r["coeffs"]).encode()
    digest = hashlib.sha256(pre).hexdigest()
    ok = (digest == c["sha256"]) \
        and (c.get("ensemble") == r.get("ensemble") == ENSEMBLE) \
        and (int(c["n"]) == int(r["n"])) \
        and (int(c["instance"]) == int(r["instance"]))
    order = sorted(range(len(r["terms"])), key=lambda i: r["terms"][i])
    return ok, [r["terms"][i] for i in order], [float(r["coeffs"][i]) for i in order]


def verify_convseed(commit_path, reveal_path):
    """F2b conv-order commitment (chair C4776 option (a)): per-rung seed.
    preimage = salt || utf8("exp144|convseed|{n}|{seed_decimal}"). Single key
    'sha256'. Returns (ok, seed)."""
    with open(commit_path) as f:
        c = json.load(f)
    with open(reveal_path) as f:
        r = json.load(f)
    pre = bytes.fromhex(r["salt_hex"]) + \
        f"exp144|convseed|{int(r['n'])}|{int(r['seed'])}".encode()
    ok = (hashlib.sha256(pre).hexdigest() == c["sha256"]) \
        and (int(c["n"]) == int(r["n"]))
    return ok, int(r["seed"])


def grade_instance(n, true_terms, true_coeffs, ans):
    """Returns (quantum_pass: bool, ratio: float|None, notes: str)."""
    q, c = ans["quantum"], ans["conventional"]
    truth = dict(zip(true_terms, true_coeffs))
    q_map = dict(zip(q["terms"], [float(x) for x in q["coeffs"]]))
    support_ok = set(q_map) == set(truth)
    coeff_ok = support_ok and all(abs(q_map[t] - truth[t]) <= TAU for t in truth)
    budget_ok = int(q["shots_budget"]) == 5 * M_BELL[n]
    qpass = support_ok and coeff_ok and budget_ok
    notes = []
    if not support_ok: notes.append("quantum support wrong")
    elif not coeff_ok: notes.append("quantum coeff outside tau")
    if not budget_ok: notes.append(
        f"budget {q['shots_budget']} != frozen {5 * M_BELL[n]} (conformity)")
    ratio = None
    if c.get("ceiling_hit"):
        ratio = CEILING_RATIO                     # LOWER BOUND (C4781 semantics)
        notes.append(f"conv unresolved at ceiling — ratio is LOWER BOUND >= {CEILING_RATIO}")
    elif c.get("identified") and c.get("terms") is not None:
        c_map = dict(zip(c["terms"], [float(x) for x in c["coeffs"]]))
        c_ok = set(c_map) == set(truth) and all(
            abs(c_map[t] - truth[t]) <= TAU for t in truth)
        if c_ok:
            ratio = float(c["meter"]) / (5 * M_BELL[n])
        else:
            notes.append("conventional misidentified (instance NULL for ratio)")
    else:
        notes.append("conventional failed to identify (instance NULL for ratio)")
    return qpass, ratio, "; ".join(notes) if notes else "clean"


def grade_rung(n, inst_results):
    passes = sum(1 for p, _, _ in inst_results if p)
    ratios = [r for _, r, _ in inst_results if r is not None]
    med = statistics.median(ratios) if ratios else None
    iqr = None
    if len(ratios) >= 4:
        qs = statistics.quantiles(ratios, n=4)
        iqr = qs[2] - qs[0]
    if med is None:
        return "NULL", "no valid conventional ratios", passes, med, iqr
    if passes < 4:
        return "LOSS", f"quantum PASS {passes}/5 < 4", passes, med, iqr
    band_note = ""
    if n == 4 and n in RATIO_BANDS:
        lo, hi = RATIO_BANDS[4]
        if not (lo <= med <= hi):
            band_note = (f"; TWO-SIDED BAND FLAG: median {med:.2f} outside "
                         f"[{lo}, {hi}] — METER_MISCALIBRATION_FLAG, investigate "
                         f"before trusting n6/n8 (C4780 ruling 3)")
    if med >= R_THRESHOLD[n]:
        return ("WIN", f"median ratio {med:.2f} >= {R_THRESHOLD[n]} (IQR {iqr})"
                + band_note, passes, med, iqr)
    return ("LOSS", f"median ratio {med:.2f} < {R_THRESHOLD[n]} with PASS {passes}/5"
            + band_note, passes, med, iqr)


def main(commits_dir, answers_dir):
    rungs = {}
    convseeds = {}
    for n in NS:
        cs_c = os.path.join(commits_dir, f"commit_convseed_n{n}.json")
        cs_r = os.path.join(commits_dir, f"reveal_convseed_n{n}.json")
        if not (os.path.exists(cs_c) and os.path.exists(cs_r)):
            convseeds[n] = ("MISSING", None)
        else:
            ok, seed = verify_convseed(cs_c, cs_r)
            convseeds[n] = ("OK" if ok else "INVALID", seed if ok else None)
    for n in NS:
        inst = []
        for k in KS:
            base = f"{ENSEMBLE}_n{n}_k{k}.json"
            ok, tt, tc = verify_commitment(
                os.path.join(commits_dir, "commit_" + base),
                os.path.join(commits_dir, "reveal_" + base))
            if not ok:
                rungs[n] = ("INVALID", f"commitment mismatch n{n}k{k} — protocol breach",
                            0, None, None)
                break
            with open(os.path.join(answers_dir, f"answers_n{n}_k{k}.json")) as f:
                ans = json.load(f)
            inst.append(grade_instance(n, tt, tc, ans))
        else:
            rungs[n] = grade_rung(n, inst)
    # convseed breach: an unverifiable conv order invalidates that rung's METER
    for n, (st, _) in convseeds.items():
        if st != "OK" and n in rungs and rungs[n][0] not in ("INVALID",):
            v, r, p, m, i = rungs[n]
            rungs[n] = ("INVALID", f"convseed {st} — conv order unverifiable "
                        f"(F2b breach); prior verdict was {v}: {r}", p, m, i)
    wins = [n for n, (v, *_ ) in rungs.items() if v == "WIN"]
    overall = "WIN" if (6 in wins and 8 in wins) else "NOT-WIN"
    n4_med = rungs.get(4, (None, None, None, None, None))[3]
    flag = (n4_med is not None and not
            (RATIO_BANDS[4][0] <= n4_med <= RATIO_BANDS[4][1]))
    n6_med = rungs.get(6, (None, None, None, None, None))[3]
    scorecard = {
        "n4_median_in_band": None if n4_med is None else
            bool(RATIO_BANDS[4][0] <= n4_med <= RATIO_BANDS[4][1]),
        "n6_median_in_band": None if n6_med is None else
            bool(RATIO_BANDS[6][0] <= n6_med <= RATIO_BANDS[6][1]),
        "slope_6over4": None if (n4_med in (None, 0) or n6_med is None) else
            round(n6_med / n4_med, 2),
        "slope_6over4_in_band": None if (n4_med in (None, 0) or n6_med is None)
            else bool(SLOPE_64_BAND[0] <= n6_med / n4_med <= SLOPE_64_BAND[1]),
        "n8_ceiling_prediction_held": None}
    out = {"per_n": {str(n): {"verdict": v, "reason": r, "quantum_pass": p,
                              "median_ratio": m, "iqr": i}
                     for n, (v, r, p, m, i) in rungs.items()},
           "overall": overall,
           "convseeds": {str(n): st for n, (st, _) in convseeds.items()},
           "meter_miscalibration_flag": flag,
           "constants": {"M_BELL": M_BELL, "R_THRESHOLD": R_THRESHOLD, "TAU": TAU,
                         "CONV_CEILING": CONV_CEILING,
                         "RATIO_BANDS": {str(k): v for k, v in RATIO_BANDS.items()},
                         "SLOPE_64_BAND": SLOPE_64_BAND},
           "predictions_scorecard": scorecard}
    print(json.dumps(out, indent=2))
    return 0


def selftest():
    """Round-trip + grading logic on synthetic records. No secrets, no shots."""
    import secrets as pysecrets
    ok_all = True
    with tempfile.TemporaryDirectory() as td:
        cdir, adir = os.path.join(td, "c"), os.path.join(td, "a")
        os.makedirs(cdir); os.makedirs(adir)
        truth = {}
        for n in NS:                       # convseed records (F2b)
            seed = int.from_bytes(pysecrets.token_bytes(8), "big")
            salt = pysecrets.token_bytes(16)
            pre = salt + f"exp144|convseed|{n}|{seed}".encode()
            json.dump({"schema": "exp144-convseed-commit-v1", "n": n,
                       "sha256": hashlib.sha256(pre).hexdigest()},
                      open(os.path.join(cdir, f"commit_convseed_n{n}.json"), "w"))
            json.dump({"schema": "exp144-convseed-reveal-v1", "n": n,
                       "salt_hex": salt.hex(), "seed": seed},
                      open(os.path.join(cdir, f"reveal_convseed_n{n}.json"), "w"))
        for n in NS:
            for k in KS:
                terms = sorted(["X" * n, "X" * (n - 2) + "YY", "X" * (n - 2) + "ZZ"])
                coeffs = [0.15, -0.20, 0.25]
                salt = pysecrets.token_bytes(16)
                pre = salt + preimage_string(n, k, terms, coeffs).encode()
                base = f"{ENSEMBLE}_n{n}_k{k}.json"
                json.dump({"schema": "exp144-commit-v1", "ensemble": ENSEMBLE, "n": n,
                           "instance": k, "sha256": hashlib.sha256(pre).hexdigest()},
                          open(os.path.join(cdir, "commit_" + base), "w"))
                # reveal with terms/coeffs deliberately PERMUTED (grader must re-sort)
                json.dump({"schema": "exp144-reveal-v1", "salt_hex": salt.hex(),
                           "ensemble": ENSEMBLE, "n": n, "instance": k,
                           "terms": terms[::-1], "coeffs": coeffs[::-1]},
                          open(os.path.join(cdir, "reveal_" + base), "w"))
                truth[(n, k)] = (terms, coeffs)
        # T1: verify_commitment round-trip incl. permuted reveal
        for (n, k), (terms, coeffs) in truth.items():
            base = f"{ENSEMBLE}_n{n}_k{k}.json"
            ok, tt, tc = verify_commitment(os.path.join(cdir, "commit_" + base),
                                           os.path.join(cdir, "reveal_" + base))
            ok_all &= ok and tt == terms and tc == coeffs
        print(f"T1 verify_commitment 15/15 incl. permuted reveals: {'PASS' if ok_all else 'FAIL'}")
        # T2: tampered coeff sign must FAIL
        base = f"{ENSEMBLE}_n4_k1.json"
        r = json.load(open(os.path.join(cdir, "reveal_" + base)))
        r["coeffs"][0] = -r["coeffs"][0]
        json.dump(r, open(os.path.join(cdir, "reveal_" + base), "w"))
        bad, _, _ = verify_commitment(os.path.join(cdir, "commit_" + base),
                                      os.path.join(cdir, "reveal_" + base))
        print(f"T2 tampered sign rejected: {'PASS' if not bad else 'FAIL'}")
        ok_all &= not bad
        r["coeffs"][0] = -r["coeffs"][0]   # restore
        json.dump(r, open(os.path.join(cdir, "reveal_" + base), "w"))
        # T3: grading logic — quantum correct everywhere; conv meters set so
        # n4 ratio ~0.36 (CONTROL), n6 ~2.6 (WIN), n8 ~25 (WIN) -> overall WIN
        meters = {4: 55000, 6: 400000, 8: None}   # n8 = ceiling_hit
        for (n, k), (terms, coeffs) in truth.items():
            json.dump({"n": n, "instance": k,
                       "quantum": {"terms": terms, "coeffs": coeffs,
                                   "shots_budget": 5 * M_BELL[n]},
                       "conventional": ({"identified": False, "ceiling_hit": True,
                                         "terms": None, "coeffs": None,
                                         "meter": 1000000, "overage_submitted": 0}
                                        if meters[n] is None else
                                        {"identified": True, "terms": terms,
                                         "coeffs": coeffs, "meter": meters[n] + 100 * k,
                                         "overage_submitted": 0})},
                      open(os.path.join(adir, f"answers_n{n}_k{k}.json"), "w"))
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(cdir, adir)
        v = json.loads(buf.getvalue())
        t3 = (v["overall"] == "WIN" and v["per_n"]["4"]["verdict"] == "WIN"
              and v["per_n"]["6"]["verdict"] == "WIN" and v["per_n"]["8"]["verdict"] == "WIN"
              and not v["meter_miscalibration_flag"]
              and v["predictions_scorecard"]["n4_median_in_band"]
              and v["predictions_scorecard"]["n6_median_in_band"]
              and v["predictions_scorecard"]["slope_6over4_in_band"])
        print(f"T3 grading (3 rungs WIN, bands+slope in-band, no flag): {'PASS' if t3 else 'FAIL'}")
        ok_all &= t3
        # T4: budget nonconformity -> instance fails -> rung LOSS
        a = json.load(open(os.path.join(adir, "answers_n6_k1.json")))
        a["quantum"]["shots_budget"] = 4999
        json.dump(a, open(os.path.join(adir, "answers_n6_k1.json"), "w"))
        a2 = json.load(open(os.path.join(adir, "answers_n6_k2.json")))
        a2["quantum"]["shots_budget"] = 4999
        json.dump(a2, open(os.path.join(adir, "answers_n6_k2.json"), "w"))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(cdir, adir)
        v = json.loads(buf.getvalue())
        t4 = v["per_n"]["6"]["verdict"] == "LOSS" and v["overall"] == "NOT-WIN"
        print(f"T4 budget nonconformity x2 -> n6 LOSS, overall NOT-WIN: {'PASS' if t4 else 'FAIL'}")
        ok_all &= t4
        # T5: convseed tamper -> rung INVALID (conv order unverifiable = F2b breach)
        rpath = os.path.join(cdir, "reveal_convseed_n8.json")
        rc = json.load(open(rpath))
        rc["seed"] = rc["seed"] ^ 1
        json.dump(rc, open(rpath, "w"))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(cdir, adir)
        v = json.loads(buf.getvalue())
        t5 = (v["convseeds"]["8"] == "INVALID"
              and v["per_n"]["8"]["verdict"] == "INVALID"
              and v["overall"] == "NOT-WIN")
        print(f"T5 convseed tamper -> n8 INVALID, overall NOT-WIN: {'PASS' if t5 else 'FAIL'}")
        ok_all &= t5
    print("SELFTEST:", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    sys.exit(main(sys.argv[1], sys.argv[2]))
