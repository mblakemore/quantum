#!/usr/bin/env python3
"""Cross-block CAL BLOCK decode — fold gate + adaptive-N + drift-alive scout.

Whisper C4999 (substrate claude-fable-5). Job d9hansogk0ls73f2ns90 (ibm_kingston).
Frozen rules (card + addendum + Elder #865):
  - lambda_hold,witness = readout-corrected X-basis Ramsey coherence THROUGH the pad, per hold
    candidate. FOLD GATE: best candidate per required site < 0.6 -> MAIN BLOCK FOLDS
    (null-validity: an H-suppressed witness cannot interpret a null).
  - Adaptive-N: Delta_pred = Delta_design * lambda_hold_best (witness component held through pad
    run 2); N/class from the frozen power formula, ceil to [5500,8000]; >8000 -> FOLD.
  - Drift-alive scout (epoch re-scout): drifter-site Bell fidelity deficit vs the null site after
    envelope accounting — scout-grade indicator, not a graded claim.
"""
import json, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
QROOT = os.path.join(HERE, "..")
JOB = "d9hansogk0ls73f2ns90"
MAN = json.load(open(os.path.join(QROOT, "results", "exp_crossblock_cal_manifest.json")))
CAL_QUBITS = MAN["cal_qubits"]           # [74, 79, 22, 44, 6, 8]
PAIRS = [tuple(p[:2]) for p in MAN["bell_pairs"]]  # [(73,74),(23,22),(45,44),(7,6)]
DELTA_DESIGN = 0.052
SE_COEF = 0.446*0.554 + 0.25*0.388*0.612 + 0.25*0.400*0.600  # variance coefficient per class-N


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(JOB)
    res = job.result()
    blocks = {m["block"]: i for i, m in enumerate(MAN["pubs_meta"])}

    def counts(tag):
        return res[blocks[tag]].data[list(res[blocks[tag]].data.keys())[0]].get_counts()

    # readout correction factors per physical qubit (from whole-chip cal blocks)
    c0, c1 = counts("cal_all0"), counts("cal_all1")
    n0 = sum(c0.values()); n1 = sum(c1.values())
    def ro_err(q):
        # bit position: measure_all -> bit index == qubit index from the right
        p01 = sum(v for k, v in c0.items() if k.replace(" ", "")[-1 - q] == "1") / n0
        p10 = sum(v for k, v in c1.items() if k.replace(" ", "")[-1 - q] == "0") / n1
        return p01, p10

    out = {"card": "exp_crossblock_cal_decode", "cycle": "C4999", "substrate": "claude-fable-5",
           "job": JOB, "hold_candidates": {}, "bell_sites": {}}

    # Ramsey: clbit ci corresponds to CAL_QUBITS[ci]
    for tag in ("ramsey_pad", "ramsey_idle"):
        cc = counts(tag); n = sum(cc.values())
        for ci, q in enumerate(CAL_QUBITS):
            p0 = sum(v for k, v in cc.items() if k.replace(" ", "")[-1 - ci] == "0") / n
            lam_raw = 2 * p0 - 1
            p01, p10 = ro_err(q)
            vis = max(1e-6, 1 - p01 - p10)         # readout visibility correction
            lam = lam_raw / vis
            d = out["hold_candidates"].setdefault(q, {})
            d[tag] = {"p0": round(p0, 4), "lambda_raw": round(lam_raw, 4),
                      "lambda_corrected": round(lam, 4)}
    for q, d in out["hold_candidates"].items():
        pad, idle = d["ramsey_pad"]["lambda_corrected"], d["ramsey_idle"]["lambda_corrected"]
        d["crosstalk_ratio_pad_over_idle"] = round(pad / idle, 3) if idle > 0.05 else None

    # Bell sites: clbits (2i, 2i+1) = (probe, anc); Bell fidelity proxy = P(00)
    for tag in ("bell_pad", "bell_idle"):
        cc = counts(tag); n = sum(cc.values())
        for i, (probe, anc) in enumerate(PAIRS):
            s = 0
            for k, v in cc.items():
                kk = k.replace(" ", "")
                if kk[-1 - 2 * i] == "0" and kk[-1 - (2 * i + 1)] == "0":
                    s += v
            out["bell_sites"].setdefault(f"{probe}-{anc}", {})[tag] = round(s / n, 4)

    # FOLD GATE + adaptive-N
    site_holds = {73: [74, 79], 23: [22], 45: [44], 7: [6, 8]}
    gate = {}
    for site, cands in site_holds.items():
        best_q, best = None, -1
        for q in cands:
            lam = out["hold_candidates"][q]["ramsey_pad"]["lambda_corrected"]
            if lam > best:
                best, best_q = lam, q
        gate[site] = {"best_hold": best_q, "lambda_hold_witness": round(best, 4),
                      "pass_0.6": bool(best >= 0.6)}
    all_pass = all(g["pass_0.6"] for g in gate.values())
    out["fold_gate"] = {"per_site": gate, "ALL_PASS": all_pass}

    lam_min = min(g["lambda_hold_witness"] for g in gate.values())
    delta_pred = DELTA_DESIGN * lam_min
    from statistics import NormalDist
    nd = NormalDist()
    n_needed = None
    for N in range(5500, 8001, 100):
        se = math.sqrt(SE_COEF / N)
        if 1 - nd.cdf(5 - delta_pred / se) >= 0.90:
            n_needed = N
            break
    out["adaptive_N"] = {"lambda_hold_min": round(lam_min, 4),
                         "delta_pred": round(delta_pred, 4),
                         "N_per_class": n_needed,
                         "verdict": ("FOLD (>8000 needed)" if (all_pass and n_needed is None)
                                     else "FOLD (lambda_hold gate)" if not all_pass
                                     else f"GO at N/class={n_needed}")}

    # drift-alive scout: drifter Bell-pad fidelity vs null site (envelope-heterogeneity caveat)
    f7 = out["bell_sites"]["7-6"]["bell_pad"]
    out["drift_alive_scout"] = {
        f"{p}-{a}": {"bell_pad": out["bell_sites"][f"{p}-{a}"]["bell_pad"],
                     "deficit_vs_null_site": round(f7 - out["bell_sites"][f"{p}-{a}"]["bell_pad"], 4)}
        for p, a in PAIRS if p != 7}
    out["drift_alive_scout"]["caveat"] = ("scout-grade: per-site envelope heterogeneity not yet "
                                          "normalized; graded drift evidence comes from the main block")

    path = os.path.join(QROOT, "results", "exp_crossblock_cal_decoded.json")
    json.dump(out, open(path, "w"), indent=1)
    print(json.dumps(out["fold_gate"], indent=1))
    print(json.dumps(out["adaptive_N"], indent=1))
    print(json.dumps(out["drift_alive_scout"], indent=1))
    print(f"metrics: usage={job.usage()}s")
    print(f"saved {path}")


if __name__ == "__main__":
    main()
