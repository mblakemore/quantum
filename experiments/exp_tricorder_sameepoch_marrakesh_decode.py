#!/usr/bin/env python3
"""Decode the SAME-EPOCH Tricorder graduation flight (marrakesh, job d9ig9h0ii2cc73edhha0).

SAME-EPOCH by construction (advisor #2): both the drift fingerprint (|<Z>| decay 160->280) AND the
coherence character (revival past the node) come from ONE job = one calibration window, so the
coherent/decoherent MECHANISM pins to the fingerprint it labels. Then run the Tricorder Diff-Mode
with mechanism_pinned=True (no cross-epoch asterisk).

Drifter-ID is IN THIS DECODE vs the marrakesh population (NOT the kingston {73,26,53,23}) — per the
pre-registered scope. Both outcomes valid: drifters-found OR stable-population.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
MAN = json.load(open(os.path.join(QROOT, "results", "exp_tricorder_sameepoch_marrakesh_manifest.json")))
JOB = MAN["job_id"]; REG = MAN["register"]; DEPTHS = MAN["depths"]
FLAG_SIGMA = 3.0
REVIVAL_MIN = 0.04   # |<Z>| must rise > this past its minimum to count as a coherent revival (widesweep rule)


def main():
    import numpy as np
    from qiskit_ibm_runtime import QiskitRuntimeService
    res = QiskitRuntimeService().job(JOB).result()
    idx = {m["block"]: i for i, m in enumerate(MAN["pubs_meta"])}

    def counts(tag):
        d = res[idx[tag]].data
        return d[list(d.keys())[0]].get_counts()

    c0, c1 = counts("cal0"), counts("cal1")
    n0, n1 = sum(c0.values()), sum(c1.values())

    def ro(q):
        p01 = sum(v for k, v in c0.items() if k.replace(" ", "")[-1 - q] == "1") / n0
        p10 = sum(v for k, v in c1.items() if k.replace(" ", "")[-1 - q] == "0") / n1
        return p01, p10

    def absZ(tag, q):
        cc = counts(tag); n = sum(cc.values())
        p1 = sum(v for k, v in cc.items() if k.replace(" ", "")[-1 - q] == "1") / n
        p01, p10 = ro(q); vis = max(1e-6, 1 - p01 - p10)
        return abs((1 - 2 * p1) / vis)

    # per-qubit |<Z>| at every depth (ONE job = same epoch)
    absz = {q: [absZ(f"twin_d{D}", q) for D in DEPTHS] for q in REG}

    # --- DRIFT fingerprint: decay ratio 160->280 (same as driftalive), population median + robust sigma ---
    i160, i280 = DEPTHS.index(160), DEPTHS.index(280)
    decay = {q: (absz[q][i280] / absz[q][i160]) for q in REG if absz[q][i160] > 0.05}
    pop = list(decay.values())
    med = float(np.median(pop)); mad = float(np.median([abs(d - med) for d in pop])) or 1e-6
    sigma = 1.4826 * mad

    # --- COHERENCE character: revival past the node, per qubit, SAME job ---
    def mechanism(q):
        z = absz[q]; mn = min(z[1:]); mn_i = z[1:].index(mn) + 1
        post = z[mn_i + 1:]
        revived = len(post) > 0 and (max(post) - mn) > REVIVAL_MIN
        return ("COHERENT (|<Z>| revives past node)" if revived
                else "no revival in range (decoherent OR node beyond max depth)"), round(max(post) - mn if post else 0.0, 3)

    device_sites, coherence_map = {}, {}
    for q in decay:
        excess = med - decay[q]                       # drifter decays MORE -> smaller ratio -> positive excess
        device_sites[q] = round(excess, 4)
        mech, rev = mechanism(q)
        coherence_map[q] = {"mechanism": mech, "revival_amplitude": rev}

    # --- run the Tricorder Diff-Mode, SAME-EPOCH (mechanism pinned) ---
    sys.path.insert(0, HERE)
    from exp_tricorder_diffmode_whisper_c5004 import diff_scan
    rep = diff_scan(device_sites, round(med, 4), round(sigma, 4), coherence_map,
                    epoch_dev=MAN["cal_epoch"], epoch_coh=MAN["cal_epoch"])   # SAME epoch
    rep["same_epoch"] = True
    rep["epochs"]["note"] = ("SAME-EPOCH: drift + coherence from ONE job (" + JOB + ") = one calibration "
                             "window; the mechanism is PINNED to the fingerprint. The cross-epoch asterisk "
                             "of the original kingston scan does NOT apply here (Elder #1423 caveat resolved).")
    rep["backend"] = MAN["backend"]; rep["job"] = JOB
    rep["prereg_scope"] = MAN["prereg_scope"]
    n_flag = len(rep["summary"]["flagged_drifted"]) + len(rep["summary"]["anomalous"])
    rep["outcome"] = (f"OUTCOME A: {n_flag} drifter(s) flagged with SAME-EPOCH-pinned coherence verdicts"
                      if n_flag else
                      "OUTCOME B: no drifters above 3sigma — stable marrakesh population (equally valid: instrument works, nothing to flag)")
    out = os.path.join(QROOT, "results", "exp_tricorder_sameepoch_marrakesh_decoded.json")
    json.dump(rep, open(out, "w"), indent=1)

    print("=" * 78)
    print("  TRICORDER DIFF-MODE — SAME-EPOCH SCAN (marrakesh, mechanism PINNED)")
    print("=" * 78)
    print(f"  job {JOB}  |  cal epoch {MAN['cal_epoch']}  |  {len(REG)}-qubit register")
    print(f"  population decay {med:.3f} +/- {sigma:.3f} (robust) | flag |{FLAG_SIGMA}sigma|\n")
    print(f"  {'SITE':8s} {'DRIFT(sig)':>10s} {'|<Z>| 160->400':<34s} MECHANISM (same-epoch)")
    flagged = sorted(rep["sites"].items(), key=lambda kv: -abs(kv[1]["drift_sigma"]))
    for site, e in flagged[:12]:
        q = int(site.replace("phys", "")); z = "[" + " ".join(f"{v:.2f}" for v in absz[q]) + "]"
        print(f"  {site:8s} {e['drift_sigma']:>10.2f} {z:<34s} {(e['coherence'] or '')[:30]}")
    print(f"\n  {rep['outcome']}")
    print(f"  SAME-EPOCH: mechanism pinned to fingerprint (Elder #1423 cross-epoch asterisk resolved).")
    print("  [SEPARATION-OWED] still single-copy data — no two-copy sample-advantage claimed.")
    print(f"  decoded -> {out}")


if __name__ == "__main__":
    main()
