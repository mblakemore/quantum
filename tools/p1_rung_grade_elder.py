#!/usr/bin/env python3
"""p1_rung_grade_elder.py — grade ONE P1 ladder rung exactly as declared on board#400 (Elder, C6655).

    commit  --manifest M                     decode the science outcomes BLIND -> decisions file + commitment sha256
                                             (publish the hash BEFORE the sealer unseals; refuses if bits not persisted)
    grade   --manifest M --revealed-P P --record R   after unseal: eps_size (k cal blocks), eps_del, r, interval, verdict
    selftest                                 regression: reproduce the i1 n=16 record's tr2/SE EXACTLY from its raw file

RULES (declared pre-data on #400 and the registration, quantum@c787440/5f38d13):
  PRIMARY  r(n) = eps_del/eps_size per rung, eps = sqrt(max(tr2,0))/3 (runner:1027-1030), k-split interval,
           falsifier r < 0.8.  SECONDARY (across-rung residual) is NOT computed here — it needs >=3 graded rungs
           and is reported with its identification numbers by a separate step.
  REFUSALS: raw artifacts absent or sha256 != manifest -> REFUSE (#353: a job id is a pointer to someone else's
           retention policy); no decisions file -> REFUSE (cannot prove decode preceded unseal); revealed P weight
           != manifest sealed_weight -> REFUSE (verify_weight, Ember's rule); permutation test failing -> REFUSE.
  EPOCH:   the weather job, its eps_eff, halt count and submit epoch are carried from the record beside r(n);
           reported, never corrected.
"""
import argparse, hashlib, importlib.util, json, math, os, random, sys, datetime
QROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _decoder():
    spec = importlib.util.spec_from_file_location("dd", os.path.join(QROOT, "tools/doorb_decoder_elder.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.init(); return m
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def tr2_and_se(dd, P, raws, n):
    shots = [dd.outcome_to_bells(r, n) for r in raws]
    vals = [dd.shot_value(P, s) for s in shots]
    N = len(vals); m = sum(vals) / N
    se = math.sqrt(max(1.0 - m * m, 0.0) / N)          # vals in {-1,+1}: var = 1 - m^2
    return m, se, N
def eps_of(tr2): return math.sqrt(max(tr2, 0.0)) / 3.0
def permutation_ok(dd, P, raws, n, seed=6655):
    m0, _, _ = tr2_and_se(dd, P, raws, n); perm = raws[:]; random.Random(seed).shuffle(perm)
    m1, _, _ = tr2_and_se(dd, P, perm, n); return m0 == m1
def refuse(msg): print(f"REFUSE: {msg}"); sys.exit(2)
def load_manifest(path):
    man = json.load(open(path)); base = path[:-5] if path.endswith(".json") else path
    arts = man.get("raw_artifacts")
    if not arts: refuse("manifest carries no raw_artifacts — bits NOT persisted (#353); run the runner's --collect first")
    for p, h in arts.items():
        if not os.path.exists(p): refuse(f"raw artifact missing on disk: {p}")
        if sha(p) != h: refuse(f"raw artifact sha256 mismatch vs manifest: {p}")
    sci = [p for p in arts if p.endswith("_science_outcomes.json")]
    cal = sorted([p for p in arts if "_cal_block" in p])
    if len(sci) != 1: refuse(f"expected exactly one science_outcomes artifact, found {len(sci)}")
    return man, base, sci[0], cal
def cmd_commit(a):
    dd = _decoder(); man, base, sci, cal = load_manifest(a.manifest)
    out = base + "_decisions_elder.json"
    if os.path.exists(out) and not a.force: refuse(f"decisions already exist: {out} (re-decoding after a commitment is not allowed)")
    rc = dd.decode(sci, out)
    h = sha(out); print(json.dumps({"decisions": out, "commitment_sha256": h, "science_sha256": sha(sci),
                                    "note": "POST THIS HASH BEFORE UNSEAL; the grader refuses without the file"})); return rc
def cmd_grade(a):
    dd = _decoder(); man, base, sci, cal = load_manifest(a.manifest); n = int(man["n"])
    dec = base + "_decisions_elder.json"
    if not os.path.exists(dec): refuse("no decisions file — decode commitment must precede unseal; run `commit` first")
    P = a.revealed_P.strip().upper()
    if len(P) != n or any(c not in "IXYZ" for c in P): refuse(f"revealed P must be {n} chars over IXYZ")
    w = sum(1 for c in P if c != "I"); w_sealed = man.get("sealed_weight")
    if w_sealed is not None and int(w_sealed) != w: refuse(f"verify_weight: revealed weight {w} != sealed_weight {w_sealed}")
    S = json.load(open(sci)); assert int(S["n"]) == n
    if not permutation_ok(dd, P, S["shots"], n): refuse("permutation test FAILED on science shots — decode is order-dependent")
    tr2, se_tr2, N = tr2_and_se(dd, P, S["shots"], n)
    if tr2 <= 0: refuse(f"science tr2 = {tr2:+.5f} <= 0 — eps_del undefined; NOT a pass, a dead measurement")
    eps_del = eps_of(tr2); se_del = se_tr2 / (6.0 * math.sqrt(tr2))
    blocks = []
    for cp in cal:
        C = json.load(open(cp)); Pc = C["P"]
        if sum(1 for c in Pc if c != "I") != w: refuse(f"cal block {cp}: weight {sum(1 for c in Pc if c!='I')} != revealed weight {w} (matched-weight cal broken)")
        if not permutation_ok(dd, Pc, C["shots"], n): refuse(f"permutation test FAILED on cal block {cp}")
        m, se, Nb = tr2_and_se(dd, Pc, C["shots"], n)
        blocks.append({"file": os.path.basename(cp), "P_cal": Pc, "N": Nb, "tr2": m, "se_tr2": se,
                       "eps": eps_of(m) if m > 0 else None, "se_eps_shot": (se / (6 * math.sqrt(m))) if m > 0 else None})
    live = [b for b in blocks if b["eps"] is not None]
    if len(live) < 2: refuse(f"fewer than 2 cal blocks with tr2 > 0 ({len(live)}) — eps_size interval undefined")
    k = len(live); eps_size = sum(b["eps"] for b in live) / k
    sd = math.sqrt(sum((b["eps"] - eps_size) ** 2 for b in live) / (k - 1)); se_size = sd / math.sqrt(k)
    r = eps_del / eps_size; se_r = r * math.hypot(se_del / eps_del, se_size / eps_size)
    z08 = (r - 0.8) / se_r; z1 = (r - 1.0) / se_r
    verdict = "WALL (r<0.8)" if r < 0.8 else "DELIVERS at this rung (r>=0.8)"
    row = {"n": n, "sealed_w": w, "revealed_P": P, "science_N": N, "tr2_science": tr2, "se_tr2": se_tr2,
           "eps_del": eps_del, "se_del": se_del, "cal_blocks": blocks, "k_live": k, "eps_size": eps_size, "se_size_ksplit": se_size,
           "r": r, "se_r": se_r, "interval_95": [r - 1.96 * se_r, r + 1.96 * se_r], "z_vs_0.8": z08, "z_vs_1.0": z1,
           "verdict": verdict, "decisions_sha256": sha(dec), "science_sha256": sha(sci), "graded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "rule": "board#400 pre-data declaration; PRIMARY per-rung r<0.8; epoch reported beside, never corrected"}
    print(f"RUNG n={n} w={w}: eps_del {eps_del:.5f}±{se_del:.5f} | eps_size {eps_size:.5f}±{se_size:.5f} (k={k}) | "
          f"r = {r:.4f} ± {se_r:.4f}  95% [{row['interval_95'][0]:.4f}, {row['interval_95'][1]:.4f}]  z(0.8)={z08:+.1f}  z(1.0)={z1:+.1f}  -> {verdict}")
    if a.record:
        R = json.load(open(a.record)); tgt = None
        for rg in R["rungs"]:
            if int(rg["n"]) == n: tgt = rg
        if tgt is None: R["rungs"].append({"n": n}); tgt = R["rungs"][-1]
        tgt.update({"r": r, "se_r": se_r, "eps_size": eps_size, "eps_del": eps_del, "interval": row["interval_95"], "verdict": verdict, "grade": row})
        json.dump(R, open(a.record, "w"), indent=1); print(f"record updated: {a.record}")
    if a.json: print(json.dumps(row, indent=1))
    return 0
def cmd_selftest(a):
    dd = _decoder(); raw = os.path.join(QROOT, "results/doorb_dist_i1_raw_science_n16_elder.json")
    G = json.load(open(os.path.join(QROOT, "results/doorb_dist_i1_grade_n16_elder.json")))
    S = json.load(open(raw)); n = int(S["n"]); P = G["planted_P"]
    tr2, se, N = tr2_and_se(dd, P, S["shots"], n)
    ok_tr2 = (tr2 == G["estimate_tr2"]); ok_se = abs(se - G["se"]) < 5e-7; ok_abs = abs(math.sqrt(tr2) - G["abs_tr"]) < 5e-6
    ok_perm = permutation_ok(dd, P, S["shots"], n)
    print(f"i1 regression: tr2 {tr2!r} vs record {G['estimate_tr2']!r} -> {'EXACT' if ok_tr2 else 'MISMATCH'}; se {se:.6f} vs {G['se']} -> {ok_se}; |tr| {math.sqrt(tr2):.5f} vs {G['abs_tr']} -> {ok_abs}; permutation invariant -> {ok_perm}")
    print(f"eps_del(i1) = {eps_of(tr2):.5f}  (sqrt(tr2)/3; N={N})")
    return 0 if (ok_tr2 and ok_se and ok_abs and ok_perm) else 1
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("commit"); c.add_argument("--manifest", required=True); c.add_argument("--force", action="store_true")
    g = sub.add_parser("grade"); g.add_argument("--manifest", required=True); g.add_argument("--revealed-P", required=True); g.add_argument("--record"); g.add_argument("--json", action="store_true")
    sub.add_parser("selftest")
    a = ap.parse_args(); sys.exit({"commit": cmd_commit, "grade": cmd_grade, "selftest": cmd_selftest}[a.cmd](a))
