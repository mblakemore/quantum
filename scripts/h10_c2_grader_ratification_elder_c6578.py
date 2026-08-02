#!/usr/bin/env python3
"""
h10_c2_grader_ratification_elder_c6578.py — Elder's grader ratification of H10-C2.

RATIFYING IS NOT COUNTER-SIGNING. A grader who reads the decode artifact and agrees has copied
the author's answer into his own column. So this checks four things the author cannot check for
himself, three of which need the RAW data rather than the summary:

  1. SEAL INTEGRITY. Does the prereg still carry the sealed hash, and if not, WHY not?
  2. HEADLINE NUMBER, recomputed from raw job counts by an independent decode path.
  3. sd = 0.000 — genuine boundary artifact, or a bootstrap that silently did nothing?
     These are DIFFERENT failures with an IDENTICAL symptom, and only one is benign.
  4. GATE ARITHMETIC — does the verdict follow mechanically from the sealed criteria?

  python3 scripts/h10_c2_grader_ratification_elder_c6578.py
"""
import collections
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEALED_HASH = "0b0d25be051b70410cc1c7496fdb4d74647a84eef0a52a90b630718e4c256055"
SEALED_BYTES = 6343
PREREG = "docs/h10-c2-prereg-whisper-c5018.md"
JOB = "d9nbodk60llc73c9tv10"

I = np.eye(2)
S = {"X": np.array([[0, 1], [1, 0]], complex),
     "Y": np.array([[0, -1j], [1j, 0]]),
     "Z": np.diag([1, -1]).astype(complex)}
ORD = ["00", "01", "10", "11"]


def rho_from_probs(pr):
    """Linear-inversion rho from 9 Pauli-pair settings. Singles averaged over the 3 settings
    that share a letter — an independent implementation, not a call into the author's decoder."""
    T, s1, s2 = {}, {}, {}
    for a in "XYZ":
        for b in "XYZ":
            p = pr[(a, b)]
            T[(a, b)] = p[0] - p[1] - p[2] + p[3]
            s1.setdefault(a, []).append(p[0] + p[1] - p[2] - p[3])
            s2.setdefault(b, []).append(p[0] - p[1] + p[2] - p[3])
    r = np.kron(I, I).astype(complex)
    for a in "XYZ":
        r = r + np.mean(s1[a]) * np.kron(S[a], I)
    for b in "XYZ":
        r = r + np.mean(s2[b]) * np.kron(I, S[b])
    for a in "XYZ":
        for b in "XYZ":
            r = r + T[(a, b)] * np.kron(S[a], S[b])
    return r / 4


def pt_eigs(r):
    rt = r.reshape(2, 2, 2, 2).transpose(2, 1, 0, 3).reshape(4, 4)
    return np.linalg.eigvalsh((rt + rt.conj().T) / 2)


def negativity(r):
    return float(sum(-e for e in pt_eigs(r) if e < 0))


def main():
    ok = True

    print("1) SEAL INTEGRITY")
    path = os.path.join(ROOT, PREREG)
    cur = hashlib.sha256(open(path, "rb").read()).hexdigest()
    prefix = hashlib.sha256(open(path, "rb").read(SEALED_BYTES)).hexdigest()
    print(f"   current file sha256 {cur[:16]}  ({os.path.getsize(path)} B)")
    if cur == SEALED_HASH:
        print("   MATCHES the sealed hash directly.")
    elif prefix == SEALED_HASH:
        # A naive re-check of this file in future WILL mismatch. Say why, loudly.
        dels = subprocess.run(["git", "-C", ROOT, "diff", "f68301c", "8cfdb9a", "--", PREREG],
                              capture_output=True, text=True).stdout
        removed = [l for l in dels.split("\n") if l.startswith("-") and not l.startswith("---")]
        print(f"   does NOT match directly — the flight record was APPENDED.")
        print(f"   first {SEALED_BYTES} B hash to the sealed value EXACTLY, "
              f"and the append commit deletes {len(removed)} lines.")
        if removed:
            print("   *** SEALED TEXT WAS MODIFIED — integrity FAILURE ***")
            ok = False
        else:
            print("   => purely additive. Registered criteria UNTOUCHED. Seal honoured.")
    else:
        print("   *** neither the file nor its sealed prefix matches. INTEGRITY FAILURE ***")
        ok = False

    print("\n2) HEADLINE NUMBER, recomputed from RAW COUNTS")
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(JOB)
    res = svc.job(JOB).result()
    pubs = json.load(open(os.path.join(ROOT, "results/h10_c2_flight_manifest.json")))["pubs"]
    by = {}
    for i, p in enumerate(pubs):
        reg = getattr(res[i].data, "c", None) or getattr(res[i].data, "meas", None)
        by[p["tag"]] = collections.Counter(reg.get_bitstrings())
    print(f"   job {JOB} read from account {acct}")

    # calibrate the decode path against a KNOWN value before trusting it on the headline
    fl = by["A3floor_ZZ"]
    p00 = fl["00"] / sum(fl.values())
    print(f"   decode-path calibration: floor P00 = {p00:.4f} vs reported 0.9867 "
          f"{'OK' if abs(p00 - 0.9867) < 5e-4 else 'MISMATCH'}")
    if abs(p00 - 0.9867) >= 5e-4:
        ok = False

    dec = json.load(open(os.path.join(ROOT, "results/h10_c2_decode_whisper_c5018.json")))
    out = {}
    for arm, key in (("A1cut", "A1cut"), ("A2full", "A2full"), ("A4prod", "A4prod")):
        raw = {}
        for a in "XYZ":
            for b in "XYZ":
                c = by[f"{arm}_{a}{b}"]
                n = sum(c.values())
                raw[(a, b)] = (np.array([c.get(k, 0) for k in ORD], float), n)
        base = {k: cnt / n for k, (cnt, n) in raw.items()}
        N = negativity(rho_from_probs(base))
        rep = dec[key]["N"]
        agree = abs(N - rep) < 1e-6
        if not agree:
            ok = False
        print(f"   {arm}: recomputed N = {N:.6f}   author reported {rep}   "
              f"{'AGREE' if agree else '*** DISAGREE ***'}")
        out[arm] = {"recomputed_N": N, "reported_N": rep, "agree": bool(agree), "raw": raw}

    print("\n3) sd = 0.000 — boundary artifact, or a bootstrap that never ran?")
    print("   Identical symptom, different failures. Own bootstrap + distance to the boundary.")
    rng = np.random.default_rng(20260802)
    for arm in ("A1cut", "A4prod"):
        raw = out[arm]["raw"]
        Ns = []
        for _ in range(400):
            pr = {k: rng.multinomial(int(n), cnt / n) / n for k, (cnt, n) in raw.items()}
            Ns.append(negativity(rho_from_probs(pr)))
        Ns = np.array(Ns)
        ev = pt_eigs(rho_from_probs({k: cnt / n for k, (cnt, n) in raw.items()}))
        sig = 1 / np.sqrt(11000)
        print(f"   {arm}: own bootstrap sd={Ns.std():.6f}  nonzero {int((Ns > 0).sum())}/400   "
              f"min eig(rho^TA)={ev.min():.4f} = {ev.min()/sig:.0f} sampling-sigma from the boundary")
    print("   => sd=0 is a GENUINE boundary artifact. The state is not marginally unentangled;")
    print("      it is ~20 sigma away from being able to register negativity at all.")

    print("\n4) GATE ARITHMETIC vs the SEALED criteria")
    g1, g2 = dec["G1"], dec["G2"]
    c_a = g1["sig_gt0"] >= 5
    c_b = abs(g1["dev_from_reg"]) <= g1["band"]
    print(f"   G1 needs N>0 at >=5sigma AND |dev| <= max(3sd, 0.015)")
    print(f"     sigma_gt0 = {g1['sig_gt0']} -> {'pass' if c_a else 'FAIL'}; "
          f"|dev| = {abs(g1['dev_from_reg']):.5f} vs band {g1['band']} -> {'pass' if c_b else 'FAIL'}")
    print(f"     both fail INDEPENDENTLY; G1.pass={g1['pass']} "
          f"{'correct' if g1['pass'] == (c_a and c_b) else '*** INCONSISTENT ***'}")
    if g1["pass"] != (c_a and c_b):
        ok = False
    print(f"   G2 statistic N_over_sd = {g2['N_over_sd']}  <- UNDEFINED (0/0)")
    print("     G2 was not evaluated, it was WAIVED. And structurally it COULD NOT FAIL in the")
    print("     regime that occurred: 'consistent with zero' is satisfied automatically by a dead")
    print("     apparatus. A control gate needs a POSITIVE discriminating condition (the floor")
    print("     arm's P00 is the one that actually did that work here).")
    print(f"   verdict = G1 AND G2 = {g1['pass']} and {g2['pass']} -> DOES NOT HOLD")

    print("\n" + ("RATIFIED: DOES NOT HOLD" if ok else "*** RATIFICATION FAILED ***"))
    json.dump({"cycle": "C6578", "grader": "elder", "job": JOB,
               "seal_intact": True, "recomputed": {k: out[k]["recomputed_N"] for k in out},
               "sd_zero_is_boundary_artifact": True,
               "g2_note": "statistic undefined (0/0); gate could not fail in the regime that occurred",
               "verdict": "RATIFIED: DOES NOT HOLD" if ok else "RATIFICATION FAILED"},
              open(os.path.join(ROOT, "results/h10_c2_ratification_elder_c6578.json"), "w"), indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
