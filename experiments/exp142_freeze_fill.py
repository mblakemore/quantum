#!/usr/bin/env python3
"""Exp142 freeze-fill — Whisper C4746. Mechanical constant fill from Gate-2 v2
results into prereg text, grader, and flight kit; then SHA256 everything.

Run AFTER Gate-2 v2 (main + n=6 supplement) lands. Idempotent-safe: refuses to
run if any placeholder is already filled (freeze happens exactly once).
"""
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

def conf_k(n):
    return math.ceil(n * math.log2(3)) + 7

def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    main_res = json.load(open(os.path.join(HERE, "exp142_robust_decoder_results.json")))
    n6 = json.load(open(os.path.join(HERE, "exp142_gate2_n6_results.json")))
    per = {int(k): v for k, v in main_res["per_n"].items()}
    per[6] = n6

    if not all(per[n]["kill_gate_pass"] for n in (4, 6, 8, 10)):
        print("KILL-GATE NOT PASSED at all rungs — no freeze:",
              {n: per[n]["kill_gate_pass"] for n in (4, 6, 8, 10)})
        return 1

    m99i = {n: per[n]["m99_ideal"] for n in (4, 6, 8, 10)}
    bq = {n: 5 * m99i[n] for n in (4, 6, 8, 10)}
    rthr = {n: (3 ** n + conf_k(n)) / bq[n] for n in (4, 6, 8, 10)}
    ret = {n: per[n]["conventional_true_basis_parity_retention"] for n in (4, 6, 8, 10)}
    infl = {n: per[n]["m99_noisy"] / m99i[n] for n in (4, 6, 8, 10)}

    print("m99_ideal:", m99i)
    print("B_q      :", bq)
    print("R(n)     :", {n: round(rthr[n], 3) for n in rthr})
    print("retention:", {n: round(ret[n], 3) for n in ret})
    print("inflation:", {n: round(infl[n], 2) for n in infl})

    # ---- grader constants ----
    gpath = os.path.join(HERE, "exp142_grader.py")
    g = open(gpath).read()
    if "M99_IDEAL = {4: None" not in g:
        print("grader already frozen — aborting")
        return 1
    g = g.replace("M99_IDEAL = {4: None, 6: None, 8: None, 10: None}   # FREEZE-FILL",
                  f"M99_IDEAL = {{4: {m99i[4]}, 6: {m99i[6]}, 8: {m99i[8]}, 10: {m99i[10]}}}  # FROZEN C4746")
    g = g.replace("R_THRESHOLD = {4: None, 6: None, 8: None, 10: None} # FREEZE-FILL",
                  "R_THRESHOLD = {4: %.6f, 6: %.6f, 8: %.6f, 10: %.6f}  # FROZEN = (3^n+conf_k)/B_q exact"
                  % (rthr[4], rthr[6], rthr[8], rthr[10]))
    open(gpath, "w").write(g)

    # ---- flight kit BQ ----
    kpath = os.path.join(HERE, "exp142_flight_kit.py")
    k = open(kpath).read()
    if "BQ = {4: None" not in k:
        print("flight kit already frozen — aborting")
        return 1
    k = k.replace("BQ = {4: None, 6: None, 8: None, 10: None}",
                  f"BQ = {{4: {bq[4]}, 6: {bq[6]}, 8: {bq[8]}, 10: {bq[10]}}}  # FROZEN C4746")
    open(kpath, "w").write(k)

    # ---- prereg text ----
    ppath = os.path.join(HERE, "exp142-preregistration-DRAFT.md")
    p = open(ppath).read()
    subs = {
        "{GATE2_BUDGETS}": f"B_q = {{4: {bq[4]}, 6: {bq[6]}, 8: {bq[8]}, 10: {bq[10]}}} "
                           f"(m99_ideal = {{4: {m99i[4]}, 6: {m99i[6]}, 8: {m99i[8]}, 10: {m99i[10]}}}, "
                           f"Gate-2 v2 flight-layout sim)",
        "{GATE2_RET6}": f"{ret[6]:.3f}",
        "{GATE2_RET10}": f"{ret[10]:.3f}",
        "{GATE2_THRESHOLDS}": f"R(4) = {rthr[4]:.3f}, R(6) = {rthr[6]:.3f}, "
                              f"R(8) = {rthr[8]:.3f}, R(10) = {rthr[10]:.3f} "
                              f"(conf_k = {{4: {conf_k(4)}, 6: {conf_k(6)}, 8: {conf_k(8)}, 10: {conf_k(10)}}}); "
                              f"Gate-2 v2 noisy inflation previews: "
                              f"{infl[4]:.2f}x / {infl[6]:.2f}x / {infl[8]:.2f}x / {infl[10]:.2f}x at n=4/6/8/10",
    }
    for a, b in subs.items():
        if a not in p:
            print(f"placeholder {a} missing — aborting"); return 1
        p = p.replace(a, b)
    # v1 retention previews in section 4 -> v2
    p = p.replace("retention 0.978 (n=4), ", f"retention {ret[4]:.3f} (n=4), ")
    p = p.replace(", 0.948 (n=8), ", f", {ret[8]:.3f} (n=8), ")
    open(ppath, "w").write(p)

    # ---- hashes (kit + gate2 decoder-sim + grader + decode_meter), then prereg ----
    hashes = {
        "{KIT_HASH}": sha256(kpath),
        "{G2_HASH}": sha256(os.path.join(HERE, "exp142_robust_decoder_sim.py")),
        "{GRADER_HASH}": sha256(gpath),
    }
    p = open(ppath).read()
    for a, b in hashes.items():
        if a not in p:
            print(f"hash placeholder {a} missing — aborting"); return 1
        p = p.replace(a, b)
    dm_hash = sha256(os.path.join(HERE, "exp142_decode_meter.py"))
    p = p.replace("**Status**: DRAFT v1",
                  f"**Status**: FROZEN C4746 (decode_meter SHA256 {dm_hash})\n~~DRAFT v1~~")
    open(ppath, "w").write(p)

    print("\nFROZEN. Hashes:")
    for a, b in hashes.items():
        print(f"  {a[1:-1]}: {b}")
    print(f"  DECODE_METER: {dm_hash}")
    print("Next: git commit freeze -> Ember seals 4 P strings -> wave 1.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
