#!/usr/bin/env python3
"""H13 Cells 3+5 — DECODE + GRADE against the FROZEN preregs (commit e7ca10d).

Read-only: fetches completed jobs, computes the frozen quantities, grades each gate,
writes append-only run-scoped results JSON. No submission paths anywhere.

Usage: python3 scripts/h13_cells35_grade_c5048.py <cell3_jobid> <cell5_jobid>
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.pop("QISKIT_IBM_INSTANCE", None)
from ibm_multi_account import _load_env_files, service_for_job

_load_env_files()

I2 = np.eye(2, dtype=complex)
PAULI = {
    "I": I2,
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
BASES = ["X", "Y", "Z"]
B_BOOT = 1000
RNG = np.random.default_rng(5048)


def counts_of(pub_result):
    data = pub_result.data
    creg = getattr(data, "c")
    return creg.get_counts()


def corr_and_singles(counts):
    n = sum(counts.values())
    e_ab = e_a = e_b = 0.0
    for k, v in counts.items():
        c1, c0 = int(k[0]), int(k[1])   # keys '<c1><c0>'
        e_ab += v * (-1) ** (c0 + c1)
        e_a += v * (-1) ** c0
        e_b += v * (-1) ** c1
    return e_ab / n, e_a / n, e_b / n


def resample(counts):
    keys = list(counts)
    n = sum(counts.values())
    p = np.array([counts[k] for k in keys], dtype=float) / n
    draw = RNG.multinomial(n, p)
    return dict(zip(keys, draw))


def build_R(cmat, s1, s2):
    """cmat[(i,j)] two-time correlators; s1[i], s2[j] singles."""
    R = np.zeros((4, 4), dtype=complex)
    labels = ["I", "X", "Y", "Z"]
    for i in labels:
        for j in labels:
            if i == "I" and j == "I":
                c = 1.0
            elif i == "I":
                c = s2[j]
            elif j == "I":
                c = s1[i]
            else:
                c = cmat[(i, j)]
            R += c * np.kron(PAULI[i], PAULI[j]) / 4
    return R


def grade_cell3(jid):
    man = json.load(open(f"/droid/repos/quantum/results/h13_cell3_manifest_{jid}.json"))
    svc, acct = service_for_job(jid)
    res = svc.job(jid).result()
    counts = [counts_of(res[k]) for k in range(len(man["labels"]))]

    def quantities(counts_list):
        # temporal: pool the two preps per (i,j)
        cmat_t, s1_t, s2_t = {}, {p: [] for p in "XYZ"}, {p: [] for p in "XYZ"}
        for bi in BASES:
            for bj in BASES:
                vals, e1s, e2s = [], [], []
                for k, lab in enumerate(man["labels"]):
                    if lab["arm"] == "temporal" and lab["i"] == bi and lab["j"] == bj:
                        c, a, b = corr_and_singles(counts_list[k])
                        vals.append(c); e1s.append(a); e2s.append(b)
                cmat_t[(bi, bj)] = float(np.mean(vals))
                s1_t[bi].append(float(np.mean(e1s)))
                s2_t[bj].append(float(np.mean(e2s)))
        s1_t = {k: float(np.mean(v)) for k, v in s1_t.items()}
        s2_t = {k: float(np.mean(v)) for k, v in s2_t.items()}
        cmat_s, s1_s, s2_s = {}, {p: [] for p in "XYZ"}, {p: [] for p in "XYZ"}
        for bi in BASES:
            for bj in BASES:
                for k, lab in enumerate(man["labels"]):
                    if lab["arm"] == "spatial" and lab["i"] == bi and lab["j"] == bj:
                        c, a, b = corr_and_singles(counts_list[k])
                        cmat_s[(bi, bj)] = c
                        s1_s[bi].append(a); s2_s[bj].append(b)
        s1_s = {k: float(np.mean(v)) for k, v in s1_s.items()}
        s2_s = {k: float(np.mean(v)) for k, v in s2_s.items()}
        Rt = build_R(cmat_t, s1_t, s2_t)
        Rs = build_R(cmat_s, s1_s, s2_s)
        return (float(np.linalg.eigvalsh(Rt)[0]), float(np.linalg.eigvalsh(Rs)[0]),
                cmat_t, s1_t, s2_t, cmat_s)

    me_t, me_s, cmat_t, s1_t, s2_t, cmat_s = quantities(counts)
    boots_t, boots_s = [], []
    for _ in range(B_BOOT):
        rc = [resample(c) for c in counts]
        bt, bs2, *_ = quantities(rc)
        boots_t.append(bt); boots_s.append(bs2)
    se_t, se_s = float(np.std(boots_t)), float(np.std(boots_s))

    offdiag = {f"{i}{j}": round(cmat_t[(i, j)], 5) for i in BASES for j in BASES if i != j}
    singles = {**{f"{k}(t1)": round(v, 5) for k, v in s1_t.items()},
               **{f"{k}(t2)": round(v, 5) for k, v in s2_t.items()}}
    g1 = (me_t < 0) and (abs(me_t) / se_t >= 5) and (-0.50 <= me_t <= -0.30)
    g2 = me_s >= -2 * se_s
    g3 = all(abs(v) <= 0.10 for v in offdiag.values())
    g4 = all(abs(v) <= 0.06 for v in singles.values())
    no_test = any(abs(v) > 0.10 for v in singles.values())
    verdict = ("NO-TEST" if no_test else
               "PASS" if (g1 and g2 and g3 and g4) else
               "UNDERPOWERED" if (me_t < 0 and abs(me_t) / se_t >= 2 and g2 and g3 and g4)
               else "FAIL")
    out = {
        "cell": "H13-Cell3-PDM", "job_id": jid, "account": acct,
        "min_eig_temporal": round(me_t, 5), "se_boot": round(se_t, 6),
        "sigmas_below_PSD": round(abs(me_t) / se_t, 1) if me_t < 0 else None,
        "min_eig_spatial": round(me_s, 5), "se_spatial": round(se_s, 6),
        "c_diag_temporal": [round(cmat_t[(b, b)], 5) for b in BASES],
        "c_diag_spatial": [round(cmat_s[(b, b)], 5) for b in BASES],
        "offdiag_temporal": offdiag, "singles_temporal": singles,
        "gates": {"G1_headline": g1, "G2_control": g2, "G3_structure": g3, "G4_apparatus": g4},
        "verdict": verdict,
    }
    path = f"/droid/repos/quantum/results/h13_cell3_grade_{jid}.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    return out


def grade_cell5(jid):
    man = json.load(open(f"/droid/repos/quantum/results/h13_cell5_manifest_{jid}.json"))
    svc, acct = service_for_job(jid)
    res = svc.job(jid).result()

    def p_of(counts, key):
        n = sum(counts.values())
        return counts.get(key, 0) / n, n

    vals = {}
    for k, lab in enumerate(man["labels"]):
        counts = counts_of(res[k])
        # c1 = a, c0 = b -> key '<a><b>'
        p11, n = p_of(counts, "11")
        p00, _ = p_of(counts, "00")
        vals[(lab["arm"], lab["A"], lab["B"])] = {"p11": p11, "p00": p00, "n": n}

    def W_of(arm):
        q = vals[(arm, "A1", "B1")]["p11"]
        z1 = vals[(arm, "A2", "B1")]["p11"]
        z2 = vals[(arm, "A1", "B2")]["p11"]
        z3 = vals[(arm, "A2", "B2")]["p00"]
        ses = []
        for p, key in [(q, ("A1", "B1")), (z1, ("A2", "B1")), (z2, ("A1", "B2")), (z3, ("A2", "B2"))]:
            n = vals[(arm, *key)]["n"]
            ses.append(np.sqrt(p * (1 - p) / n))
        W = q - z1 - z2 - z3
        seW = float(np.sqrt(sum(s ** 2 for s in ses)))
        return W, seW, q, (z1, z2, z3)

    W, seW, q, zeros = W_of("hardy")
    Wn, seWn, qn, zn = W_of("null")
    g1 = (W / seW >= 5) and (0.02 <= W <= 0.09)
    g2 = all(z <= 0.03 for z in zeros)
    g3 = 0.05 <= q <= 0.12
    diff_sig = (W - Wn) / float(np.sqrt(seW ** 2 + seWn ** 2))
    g4 = (Wn < 0) and (diff_sig >= 5)
    no_test = any(z > 0.05 for z in zeros)
    verdict = ("NO-TEST" if no_test else
               "PASS" if (g1 and g2 and g3 and g4) else
               "UNDERPOWERED" if (W > 0 and W / seW >= 2 and g2 and g4) else "FAIL")
    out = {
        "cell": "H13-Cell5-Hardy", "job_id": jid, "account": acct,
        "W": round(W, 5), "se_W": round(seW, 5), "W_sigmas": round(W / seW, 1),
        "q": round(q, 5), "zeros": [round(z, 5) for z in zeros],
        "W_null": round(Wn, 5), "se_W_null": round(seWn, 5),
        "W_minus_Wnull_sigmas": round(diff_sig, 1),
        "gates": {"G1_headline": g1, "G2_zeros": g2, "G3_fraction": g3, "G4_null": g4},
        "verdict": verdict,
    }
    path = f"/droid/repos/quantum/results/h13_cell5_grade_{jid}.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    return out


if __name__ == "__main__":
    j3, j5 = sys.argv[1], sys.argv[2]
    r3 = grade_cell3(j3)
    print(json.dumps(r3, indent=2))
    r5 = grade_cell5(j5)
    print(json.dumps(r5, indent=2))
