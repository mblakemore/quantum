#!/usr/bin/env python3
"""DECODE the kingston ladder — branches (a)-(d) frozen in the manifest before submission.

CORRECTION VALIDITY, in the combined form adopted from Ember #5148:
  PRIMARY (free, binary, no threshold): a block is INVALID if its corrected purity leaves
    [0,1] or its corrected distribution carries negative mass. Rejecting a computation whose
    output is mathematically impossible is not outcome-selection.
  SECONDARY (reported, not gating): a correction is SUSPECT if its magnitude exceeds
    cond x readout_error. On its own this PASSES fez q71 — that gap is why PRIMARY exists.

The readout bar (precondition 5) already ran at BUILD time and cost blocks. The validity
check runs at DECODE time and costs nothing. Which one does the work is reported, not assumed.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

JOB = "d9ptuqa42q2c73b8f610"


def joint_bins(counts, idx, shots):
    v = np.zeros(16)
    for bstr, n in counts.items():
        b = bstr.replace(" ", ""); w = len(b)
        g = lambda p: int(b[w - 1 - p])
        v[(g(idx[0]) << 3) | (g(idx[1]) << 2) | (g(idx[2]) << 1) | g(idx[3])] += n
    return v / shots


def u_from_bins(p):
    odd = 0.0
    for k in range(16):
        b = [(k >> 3) & 1, (k >> 2) & 1, (k >> 1) & 1, k & 1]
        if ((b[0] & b[1]) ^ (b[2] & b[3])):
            odd += p[k]
    return 1.0 - 2.0 * odd


def main():
    from ibm_multi_account import service_for_job
    man = json.load(open(os.path.join(RES, f"armn_kingston_manifest_{JOB}.json")))
    svc, acct = service_for_job(JOB)
    res = svc.job(JOB).result()
    pm = man["pubs_meta"]
    cnt = lambda i: res[i].data.meas.get_counts()

    w = len(next(iter(cnt(0))).replace(" ", ""))

    def perq(counts, tgt, shots):
        e = np.zeros(w)
        for b, n in counts.items():
            b = b.replace(" ", "")
            for p in range(w):
                if int(b[w - 1 - p]) != tgt:
                    e[p] += n
        return e / shots

    e0 = perq(cnt(0), 0, pm[0]["shots"])
    e1 = perq(cnt(1), 1, pm[1]["shots"])

    rows = []
    for i, m in enumerate(pm):
        if "q" not in m:
            continue
        pl = m["plan"]; idx = (pl["anc1"], pl["anc2"], pl["s1"], m["q"])
        p = joint_bins(cnt(i), idx, m["shots"])
        u_raw = u_from_bins(p)
        J = None
        for pos in idx:
            A = np.array([[1 - e0[pos], e1[pos]], [e0[pos], 1 - e1[pos]]])
            J = A if J is None else np.kron(J, A)
        cond = float(np.linalg.cond(J))
        pc = np.linalg.solve(J, p)
        u = float(u_from_bins(pc))
        neg = float(pc[pc < 0].sum())
        worst_ro = float(max(e0[x] for x in idx) if max(e0[x] for x in idx) > max(e1[x] for x in idx)
                         else max(e1[x] for x in idx))
        # PRIMARY: physical range. binary, no threshold.
        valid = (0.0 <= u <= 1.0) and (neg > -1e-9)
        # SECONDARY: magnitude vs condition-number ceiling. reported, not gating.
        suspect = abs(u - u_raw) > cond * worst_ro
        rows.append({"q": m["q"], "config": m["config"], "u_raw": round(float(u_raw), 5),
                     "u": round(u, 5), "delta": round(u - float(u_raw), 5),
                     "cond": round(cond, 3), "neg_mass": round(neg, 6),
                     "worst_readout": round(worst_ro, 4),
                     "VALID": valid, "suspect": bool(suspect)})

    print(f"{'q':>4} {'config':<11} {'u_raw':>8} {'u':>8} {'delta':>8} {'cond':>6} "
          f"{'negmass':>9} {'VALID':>6} {'susp':>5}")
    for r in sorted(rows, key=lambda r: (r["config"], r["q"])):
        print(f"{r['q']:>4} {r['config']:<11} {r['u_raw']:>8.5f} {r['u']:>8.5f} "
              f"{r['delta']:>+8.5f} {r['cond']:>6.3f} {r['neg_mass']:>9.6f} "
              f"{str(r['VALID']):>6} {str(r['suspect']):>5}")

    w2 = [r for r in rows if r["config"] == "shallow_2"]
    valid2 = [r for r in w2 if r["VALID"]]
    invalid2 = [r for r in w2 if not r["VALID"]]
    u_valid = np.array([r["u"] for r in valid2])

    print(f"""
=== WHICH CHECK DID THE WORK ===
  build-time readout bar (COSTLY): {man['n_qualify']} of 156 blocks qualified; 13 qubits failed
  decode-time range check (FREE) : {len(invalid2)} of {len(w2)} flown blocks INVALID {[r['q'] for r in invalid2]}
  suspect by cond-ceiling only   : {[r['q'] for r in w2 if r['suspect'] and r['VALID']]}""")

    if len(u_valid) > 1:
        sd = float(u_valid.std(ddof=1)); n_q = man["n_qualify"]
        n_need = (3 * sd * 2 / 0.016) ** 2
        print(f"""
=== PRIMARY ESTIMAND ===
  candidate-to-candidate sd on shallow_2, VALID blocks only:  {sd:.5f}   (n={len(u_valid)})
  mean u {u_valid.mean():.5f}   range [{u_valid.min():.4f}, {u_valid.max():.4f}]
  fez comparison:  ladder 0.01197  |  contrast q72-free 0.00676  |  contrast as-flown 0.03777

=== FEASIBILITY, re-derived on kingston ===
  blocks needed for 3sd on a 0.016 contrast: {n_need:.0f}
  blocks available (N_qualify, NO drifter exclusion — an UPPER bound): {n_q}
  ratio: {n_need / n_q:.2f}x""")
        b = ("(a) FEASIBLE — re-pre-register arm-N" if sd <= 0.015 and n_q >= 12 else
             "(b) block count binds — design-search problem" if sd <= 0.015 else
             "(c) heavy tail is REAL — re-file the closure on THIS evidence" if sd >= 0.030 else
             "(d) between — report the interval, no story")
        print(f"\n  FROZEN BRANCH FIRED: {b}")

    lad = {}
    for cfg in ("shallow_0", "shallow_1", "shallow_2"):
        v = [r["u"] for r in rows if r["config"] == cfg and r["VALID"]]
        if v:
            lad[cfg] = float(np.mean(v))
    if len(lad) == 3:
        common = set(r["q"] for r in rows if r["config"] == "shallow_0")
        print(f"""
=== SECONDARY: does idle-dominance generalise off fez? ===
  shallow_0 (gates+readout, no channel) {lad['shallow_0']:.4f}
  shallow_1 (+1 idle)                   {lad['shallow_1']:.4f}   idle 1 costs {lad['shallow_0']-lad['shallow_1']:.4f}
  shallow_2 (+2 idles = witness)        {lad['shallow_2']:.4f}   idle 2 costs {lad['shallow_1']-lad['shallow_2']:.4f}
  gates+readout cost {1-lad['shallow_0']:.4f} across 9 CZ
  ratio idle:gates = {(lad['shallow_0']-lad['shallow_2'])/(1-lad['shallow_0']):.2f}:1   (fez measured ~3:1)
  NOTE: shallow_2 mean here is over the LADDER SUBSET only where configs overlap ({sorted(common)}).""")

    out = os.path.join(RES, f"armn_kingston_decode_{JOB}.json")
    json.dump({"card": "armn_kingston_decode", "cycle": "C5018", "substrate": "claude-fable-5",
               "job": JOB, "account": acct, "n_qualify": man["n_qualify"],
               "rows": rows, "ladder_means": lad,
               "sd_valid": float(u_valid.std(ddof=1)) if len(u_valid) > 1 else None,
               "n_valid": len(u_valid), "n_invalid": len(invalid2)},
              open(out, "w"), indent=1)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
