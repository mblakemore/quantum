#!/usr/bin/env python3
"""grade_exp125b.py — grade Exp125b (coherent-record erasure frontier, H4 companion) under the FROZEN
prereg. 2-qubit tomography -> physical rho -> S(B|A) with two-sided bootstrap SE + MC debias; record
k_BT; frontier vs coherent (0.028) / classical (0.092) taxes. Writes results/exp125b_grade.json."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = {"I": I2, "X": SX, "Y": SY, "Z": SZ}
LN2 = math.log(2)
BOOT_B = 400
RNG = np.random.default_rng(4664)


def counts_vec(counts):
    """4-vector over (a,b) index=2a+b; a=qubitA(c0), b=qubitB(c1). Qiskit key 'b1b0'."""
    v = np.zeros(4)
    for key, c in counts.items():
        bits = key.replace(" ", "")
        b1, b0 = int(bits[-2]), int(bits[-1])   # b0=c0=A, b1=c1=B
        v[2 * b0 + b1] += c
    return v


def vN(rho):
    w = np.linalg.eigvalsh(rho)
    w = np.clip(w.real, 0, None)
    w = w / w.sum()
    return float(-sum(x * math.log2(x) for x in w if x > 1e-12))


def rho_from_counts(tomo_pv, Minv):
    """tomo_pv: dict (ba,bb)->prob4. Returns physical rho_AB (4x4)."""
    corr = {}
    single_a = {b: [] for b in "XYZ"}
    single_b = {b: [] for b in "XYZ"}
    for (ba, bb), pv in tomo_pv.items():
        p = Minv @ pv
        p = np.clip(p, 0, None)
        p = p / p.sum()
        # index=2a+b ; sign (-1)^a for A, (-1)^b for B
        s = p.reshape(2, 2)               # s[a,b]
        sa = np.array([1, -1])
        AB = sa[:, None] * sa[None, :]
        corr[(ba, bb)] = float((AB * s).sum())
        single_a[ba].append(float((sa[:, None] * s).sum()))
        single_b[bb].append(float((sa[None, :] * s).sum()))
    c = {("I", "I"): 1.0}
    for b in "XYZ":
        c[(b, "I")] = float(np.mean(single_a[b]))
        c[("I", b)] = float(np.mean(single_b[b]))
    for k, v in corr.items():
        c[k] = v
    rho = np.zeros((4, 4), dtype=complex)
    for (i, j), cij in c.items():
        rho += cij * np.kron(PAULI[i], PAULI[j])
    rho = rho / 4.0
    # physical projection
    w, V = np.linalg.eigh((rho + rho.conj().T) / 2)
    w = np.clip(w.real, 0, None)
    w = w / w.sum()
    return (V * w) @ V.conj().T


def s_cond(rho):
    """S(B|A) = S(AB) - S(A). index=2a+b, A=first."""
    rhoA = np.zeros((2, 2), dtype=complex)
    for a in range(2):
        for ap in range(2):
            rhoA[a, ap] = sum(rho[2 * a + b, 2 * ap + b] for b in range(2))
    return vN(rho) - vN(rhoA)


def floor_of(p):
    if p <= 0:
        return 0.0
    if p >= 0.5:
        return float("inf")
    return LN2 / math.log((1 - p) / p)   # floor_classical = k_BT*ln2, k_BT=1/ln((1-p)/p) [E units]


def main():
    man = json.load(open(os.path.join(HERE, "..", "results", "exp125b_jobids.json")))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    metas = man["metas"]
    raw = {}
    for i, m in enumerate(metas):
        d = res[i].data
        counts = list(d.__dict__.values())[0].get_counts() if not hasattr(d, "c") \
            else d.c.get_counts()
        raw[m["label"]] = counts_vec(counts)

    # confusion matrix M: column = true state (2*sa+sb), from cal pubs
    M = np.zeros((4, 4))
    for sa in (0, 1):
        for sb in (0, 1):
            col = raw[f"cal_{sa}{sb}"]
            M[:, 2 * sa + sb] = col / col.sum()
    Minv = np.linalg.pinv(M)

    tomo_counts = {}
    for ba in "XYZ":
        for bb in "XYZ":
            tomo_counts[(ba, bb)] = raw[f"tomo_{ba}{bb}"]

    def pipeline(tc):
        pv = {k: v / v.sum() for k, v in tc.items()}
        return s_cond(rho_from_counts(pv, Minv))

    s_point = pipeline(tomo_counts)
    boots = []
    for _ in range(BOOT_B):
        tc = {}
        for k, v in tomo_counts.items():
            N = int(v.sum())
            tc[k] = RNG.multinomial(N, v / N).astype(float)
        boots.append(pipeline(tc))
    boots = np.array(boots)
    se_s = float(boots.std(ddof=1))
    bias = float(boots.mean() - s_point)          # finite-sample bias estimate
    s_deb = s_point - bias                          # debiased (bias makes S too low)

    # k_BT of record qubit (phys 4 = index B); m00_B = P(B=1 | prep 00)
    rec_q = man["pair"][1]
    a_max = man["a_max"][str(rec_q)] if str(rec_q) in man["a_max"] else man["a_max"][rec_q]
    c00 = raw["cal_00"]
    m00_B = (c00[1] + c00[3]) / c00.sum()           # b=1 states: (a,b)=(0,1)->idx1,(1,1)->idx3
    se_m = math.sqrt(m00_B * (1 - m00_B) / c00.sum())
    p_lo = max(0.0, m00_B - a_max)
    floor_lo = floor_of(p_lo)                        # conservative (small) floor
    floor_hi = floor_of(m00_B)

    absS_lo = max(0.0, abs(s_deb) - 5 * se_s)        # conservative small |S|
    absS_hi = abs(s_deb) + 5 * se_s
    bonus_lo = absS_lo * floor_lo                    # conservative lower bound on bonus
    bonus_hi = absS_hi * floor_hi                    # generous upper bound

    tax_c, tax_k = man["tax_coherent_E"], man["tax_classical_E"]

    def frontier(tax):
        if bonus_lo > tax:
            return "ACCESSIBLE"
        if bonus_hi < tax:
            return "INACCESSIBLE"
        return "STRADDLE"

    g_ent = "PASS" if (s_deb + 5 * se_s) < 0 else "FAIL"  # conservative entanglement cert
    out = {
        "experiment": "exp125b-coherent-record-erasure-frontier", "cycle": "C4664-whisper",
        "job_id": man["job_id"], "pair": man["pair"], "record_qubit": rec_q,
        "bound_graded": man["bound_graded"],
        "S(B|A)_point": round(s_point, 4), "S(B|A)_debiased": round(s_deb, 4),
        "SE_boot": round(se_s, 4), "finite_sample_bias": round(bias, 4),
        "G_ent(S(B|A)+5SE<0)": g_ent,
        "record_p_eq_bracket": [round(p_lo, 5), round(m00_B, 5)], "a_max": a_max,
        "floor_classical_E_bracket": [round(floor_lo, 4), round(floor_hi, 4)],
        "bonus_E_bracket": [round(bonus_lo, 4), round(bonus_hi, 4)],
        "tax_coherent": tax_c, "tax_classical": tax_k,
        "frontier_vs_coherent": frontier(tax_c),
        "frontier_vs_classical": frontier(tax_k),
        "bias_note": "finite-sample vN entropy biased low -> |S| high -> bonus high -> favors ACCESSIBLE; a coherent-ACCESSIBLE verdict is the one to distrust",
    }
    outp = os.path.join(HERE, "..", "results", "exp125b_grade.json")
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
