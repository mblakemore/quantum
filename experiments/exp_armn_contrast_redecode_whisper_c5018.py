#!/usr/bin/env python3
"""RE-DECODE the contrast job: is q71 physical, or did the readout correction create it?

WHY ($0, and it gates a QPU spend):
The arm-N closure ("~22-28x infeasible on this hardware") rests on ONE measured quantity —
the candidate-to-candidate purity spread, pooled sd 0.0378 from the contrast flight. A
leverage check on that flight shows the entire excess is q71:

    drifters   q23 0.75132  q25 0.75685  q51 0.75469  q71 0.86437   <- +0.110 above the others
    pooled sd  all 9 candidates 0.03777  |  without q71 0.01222   (3.1x smaller)

and TWO INDEPENDENT fez jobs agree on ~0.012 when q71 is absent:
    ladder shallow_2 pooled within-group sd  0.01197  (6 candidates, q71 not among them)
    contrast pooled sd excluding q71         0.01222  (8 candidates)

Consequence: at sd 0.012 the closing number is ~20 blocks needed vs 9 available = ~2x
infeasible — a DESIGN problem. At sd 0.038 it is ~200 vs 9 = ~22x — a WALL. **One qubit
decides which of those two statements is true**, so it must be diagnosed before more spend.

HYPOTHESIS UNDER TEST (the commensurate-correction rule from earlier this cycle, applied to
my own headline): a readout correction is a matrix INVERSION, and its condition number sets
how much it amplifies noise. If q71's block carried a worse/more ill-conditioned cal, the
inversion could OVERSHOOT and inflate purity. The stored rule is "a correction whose effect
exceeds the magnitude of the error being corrected is a bug until proven otherwise" — this
run applies it to the number that closed the arm.

WHAT THIS IS NOT: it is NOT a re-grade of the contrast. The frozen readout fired
(CI includes zero -> BOUNDED, not measured) and that verdict stands untouched. q71 is not
excluded from anything. This diagnoses the ERROR TERM feeding a FEASIBILITY claim, which is
a different object from the effect estimate, and the distinction is stated here rather than
assumed.

PRE-STATED DISPOSITION (written before running):
  (A) raw q71 also ~+0.11 high, correction small     -> q71 is PHYSICAL. The heavy-tailed
      spread is real, closure at ~22x STANDS, kingston would be confirmatory not decisive.
  (B) raw q71 in line, correction supplies the excess -> ARTIFACT. Generic spread ~0.012,
      closure WITHDRAWN, arm-N is ~2x infeasible = a design problem, and kingston becomes
      the right independent check of the generic spread.
  (C) ambiguous (partial)                            -> report as ambiguous, do not round
      toward either story; kingston decides.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

JOB = "d9pt5ja42q2c73b8e7sg"
MANIFEST = os.path.join(RES, f"armn_contrast_manifest_{JOB}.json")


def bits_of(arr, nbits):
    """counts dict -> array of shots x nbits (little-endian qubit index)."""
    return arr


def pair_purity(counts, idx, nshots):
    """u = 1 - 2 P(odd), singlet flag per pair = AND of its two bits.
    idx = (a1, a2, s1, q) physical indices into the measured register."""
    a1, a2, s1, q = idx
    odd = 0
    for bstr, n in counts.items():
        b = bstr.replace(" ", "")
        # qiskit bitstrings are printed MSB-first over the full register
        w = len(b)
        g = lambda p: int(b[w - 1 - p])
        f1 = g(a1) & g(a2)
        f2 = g(s1) & g(q)
        if (f1 ^ f2):
            odd += n
    p_odd = odd / nshots
    return 1.0 - 2.0 * p_odd, p_odd


def joint_bins(counts, idx, nshots):
    """16-bin joint distribution over (a1,a2,s1,q)."""
    v = np.zeros(16)
    for bstr, n in counts.items():
        b = bstr.replace(" ", ""); w = len(b)
        g = lambda p: int(b[w - 1 - p])
        k = (g(idx[0]) << 3) | (g(idx[1]) << 2) | (g(idx[2]) << 1) | g(idx[3])
        v[k] += n
    return v / nshots


def u_from_bins(p):
    """Same estimator as above, expressed on the 16-bin vector."""
    odd = 0.0
    for k in range(16):
        b = [(k >> 3) & 1, (k >> 2) & 1, (k >> 1) & 1, k & 1]
        if ((b[0] & b[1]) ^ (b[2] & b[3])):
            odd += p[k]
    return 1.0 - 2.0 * odd


def main():
    from ibm_multi_account import service_for_job
    man = json.load(open(MANIFEST))
    svc, acct = service_for_job(JOB)
    print(f"[read] job {JOB} via account {acct}")
    job = svc.job(JOB)
    res = job.result()
    pm = man["pubs_meta"]

    # --- calibration: cal0 (prep all-0), cal1 (prep all-1) -> per-qubit e0, e1
    def marg(pub_i, shots):
        return res[pub_i].data.meas.get_counts()

    cal0 = marg(0, pm[0]["shots"]); cal1 = marg(1, pm[1]["shots"])

    def per_qubit_err(counts, target_bit, nshots):
        """P(read != prep) per physical qubit position."""
        w = len(next(iter(counts)).replace(" ", ""))
        err = np.zeros(w)
        for bstr, n in counts.items():
            b = bstr.replace(" ", "")
            for p in range(w):
                if int(b[w - 1 - p]) != target_bit:
                    err[p] += n
        return err / nshots

    e0 = per_qubit_err(cal0, 0, pm[0]["shots"])   # P(read 1 | prep 0)
    e1 = per_qubit_err(cal1, 1, pm[1]["shots"])   # P(read 0 | prep 1)

    rows = []
    for i, meta in enumerate(pm):
        if not meta["block"].startswith("WIT_"):
            continue
        q = meta["q"]; pl = meta["plan"]
        idx = (pl["anc1"], pl["anc2"], pl["s1"], q)
        counts = marg(i, meta["shots"])
        p = joint_bins(counts, idx, meta["shots"])
        u_raw = u_from_bins(p)

        # full 4-qubit joint inversion (kron of per-qubit inverse confusion matrices)
        mats = []
        for pos in idx:
            a, b_ = e0[pos], e1[pos]
            A = np.array([[1 - a, b_], [a, 1 - b_]])
            mats.append(A)
        J = mats[0]
        for M2 in mats[1:]:
            J = np.kron(J, M2)
        cond = np.linalg.cond(J)
        p_corr = np.linalg.solve(J, p)
        u_corr = u_from_bins(p_corr)

        neg = float(p_corr[p_corr < 0].sum())     # negative mass = inversion overshoot
        rows.append({
            "q": q, "role": meta["role"], "u_raw": round(float(u_raw), 5),
            "u_corr": round(float(u_corr), 5), "delta": round(float(u_corr - u_raw), 5),
            "readout_err": [round(float(e0[p_]), 4) for p_ in idx],
            "readout_err_1": [round(float(e1[p_]), 4) for p_ in idx],
            "cond": round(float(cond), 3), "neg_mass": round(neg, 5),
        })

    print(f"\n{'q':>4} {'role':<8} {'u_raw':>8} {'u_corr':>8} {'delta':>8} {'cond':>7} {'negmass':>8}")
    for r in sorted(rows, key=lambda r: r["q"]):
        print(f"{r['q']:>4} {r['role']:<8} {r['u_raw']:>8.5f} {r['u_corr']:>8.5f} "
              f"{r['delta']:>+8.5f} {r['cond']:>7.3f} {r['neg_mass']:>8.5f}")

    def pooled(vals_d, vals_q):
        d, qq = np.array(vals_d), np.array(vals_q)
        return float(np.sqrt(((len(d) - 1) * d.var(ddof=1) + (len(qq) - 1) * qq.var(ddof=1))
                             / (len(d) + len(qq) - 2)))

    for key in ("u_raw", "u_corr"):
        dv = [r[key] for r in rows if r["role"] == "drifter"]
        qv = [r[key] for r in rows if r["role"] == "quiet"]
        dv71 = [r[key] for r in rows if r["role"] == "drifter" and r["q"] != 71]
        print(f"\n{key}:  pooled sd all-9 {pooled(dv, qv):.5f}   without q71 {pooled(dv71, qv):.5f}"
              f"   contrast {np.mean(dv) - np.mean(qv):+.5f}")

    out = os.path.join(RES, f"armn_contrast_redecode_{JOB}.json")
    json.dump({"card": "armn_contrast_redecode", "cycle": "C5018",
               "substrate": "claude-fable-5", "job": JOB, "account": acct,
               "purpose": "diagnose whether q71 is physical or a readout-correction artifact",
               "not_a_regrade": ("The frozen contrast verdict (CI includes zero -> BOUNDED) "
                                 "stands untouched. This diagnoses the ERROR TERM feeding a "
                                 "FEASIBILITY claim, not the effect estimate."),
               "rows": rows}, open(out, "w"), indent=1)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
