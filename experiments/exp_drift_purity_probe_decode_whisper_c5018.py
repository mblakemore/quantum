#!/usr/bin/env python3
"""DRIFT PURITY PROBE — decode + the clock-or-coin census (Whisper C5018, H11 Tier-0 №4).

DEBT CLEARED: the C5010 probe flew TWICE on ibm_kingston (jobs d9kq85jhdfks73ck12gg,
d9l4ncrjf64c739j1q8g) and was never decoded — the flight script shipped with no decode path
(the flown-but-ungraded class: QPU spent, results unread; today's write-lands-where-nothing-
reads shape, in flight form). Retrieval of completed jobs is $0 — no pool seconds consumed.

PER-EPOCH RULE (pre-registered at C5010 in the manifest, frozen, applied verbatim):
  per drifter, per depth: <X>,<Y>,<Z> readout-corrected -> r = |(<X>,<Y>,<Z>)|,
  purity = (1+r^2)/2; classify REVIVAL (coherent — phase spread cannot revive) vs
  MONOTONE-DECAY (ambiguous: Markovian decoherence vs inhomogeneous coherent dephasing).

CROSS-EPOCH RULE (pre-registered HERE, committed BEFORE first retrieval of either job —
the data has never been looked at, so the freeze is honest):
  On drifters ACTIVE IN BOTH epochs (the set is epoch-volatile, C5002), at each depth where
  both epochs have all 3 bases:
    dtheta  = angle between the two epochs' Bloch vectors (their direction change)
    dr      = |r_epoch2 - r_epoch1| (their length change)
    sigma_* = shot-noise propagated; a quantity is RESOLVED iff its value > 3*sigma.
  CLOCK-CONSISTENT: dtheta resolved (>3 sigma) AND dr NOT resolved — the drift moved the
    phase and kept the length: a coherent trajectory between epochs (a clock ticks).
  COIN-CONSISTENT: dr resolved AND negative (length collapsed) regardless of dtheta — the
    epoch change destroyed coherence (a coin flips).
  UNDERPOWERED: neither resolved. MIXED: both resolved (rotation AND shrinkage) — reported
    as its own outcome, not forced into either bin.
  Census verdict = per-drifter tally; NO aggregate claim if drifter verdicts disagree —
  disagreement IS the finding (drift is not one mechanism).

VERDICTS ARE THREE-STATE+; margins carried (value, sigma, ratio) on every row.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
QROOT = os.path.join(HERE, "..")
RES = os.path.join(QROOT, "results")

JOBS = ["d9kq85jhdfks73ck12gg", "d9l4ncrjf64c739j1q8g"]  # epoch order by id-time (kq < l4)


def marginals(counts, nbits, qubits):
    """Per-qubit P(1) marginals from a counts dict keyed by bitstrings (qiskit bit order)."""
    tot = sum(counts.values())
    p1 = {}
    for q in qubits:
        s = 0
        for bs, c in counts.items():
            if bs.replace(" ", "")[::-1][q] == "1":
                s += c
        p1[q] = s / tot
    return p1, tot


def corrected_expz(p1, e0, e1):
    """Invert the per-qubit 2x2 readout matrix: raw P(1) -> corrected <Z>.
    e0 = P(read 1 | prep 0), e1 = P(read 0 | prep 1)."""
    denom = 1.0 - e0 - e1
    if abs(denom) < 1e-6:
        return None
    p1c = (p1 - e0) / denom
    p1c = min(max(p1c, 0.0), 1.0)
    return 1.0 - 2.0 * p1c


def decode_job(job_id, man):
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from ibm_multi_account import service_for_job
    svc, job = service_for_job(job_id, "IBMQ_ALT")
    res = job.result()
    meta = man["pubs_meta"]
    drifters = man["drifters_active"]
    depths = man["depths"]
    nphys = max(man["register"]) + 1

    def counts_of(i):
        return getattr(res[i].data, list(res[i].data.__dict__)[0] if hasattr(res[i].data, "__dict__") else "meas").get_counts() \
            if False else res[i].data.meas.get_counts()

    # readout cal from the SAME job (floor doctrine: same-job context)
    c0, _ = marginals(counts_of(0), nphys, drifters)
    c1, _ = marginals(counts_of(1), nphys, drifters)
    e0 = {q: c0[q] for q in drifters}            # P(1|0)
    e1 = {q: 1.0 - c1[q] for q in drifters}      # P(0|1)

    out = {}
    for i, m in enumerate(meta):
        if m["block"] in ("cal0", "cal1"):
            continue
        D, B = m["depth"], m["basis"]
        p1, tot = marginals(counts_of(i), nphys, drifters)
        for q in drifters:
            z = corrected_expz(p1[q], e0[q], e1[q])
            if z is None:
                continue
            sig = 2.0 * np.sqrt(p1[q] * (1 - p1[q]) / tot) / abs(1 - e0[q] - e1[q])
            out.setdefault(q, {}).setdefault(D, {})[B] = (z, sig)
    return out, {"e0": e0, "e1": e1}


def main():
    mans = {}
    for j in JOBS:
        with open(os.path.join(RES, f"exp_drift_purity_probe_manifest_{j}.json")) as f:
            mans[j] = json.load(f)
    epochs = {}
    for j in JOBS:
        print(f"[retrieve] {j} (ibm_kingston, $0 API retrieval)")
        epochs[j], cal = decode_job(j, mans[j])
        print(f"  readout e0/e1 medians: {np.median(list(cal['e0'].values())):.4f}/{np.median(list(cal['e1'].values())):.4f}")

    report = {"card": "exp_drift_purity_probe_DECODE+CENSUS", "cycle": "C5018",
              "substrate": "claude-fable-5", "jobs": JOBS,
              "per_epoch": {}, "cross_epoch": {}}

    # PER-EPOCH (C5010 frozen rule)
    for j in JOBS:
        ep = {}
        for q, byd in sorted(epochs[j].items()):
            rows = []
            for D in sorted(byd):
                b = byd[D]
                if not all(k in b for k in "XYZ"):
                    continue
                v = np.array([b["X"][0], b["Y"][0], b["Z"][0]])
                sv = np.array([b["X"][1], b["Y"][1], b["Z"][1]])
                r = float(np.linalg.norm(v))
                sr = float(np.sqrt(np.sum((v / max(r, 1e-9) * sv) ** 2)))
                rows.append({"depth": D, "bloch": [round(x, 4) for x in v],
                             "r": round(r, 4), "sigma_r": round(sr, 4),
                             "purity": round((1 + r * r) / 2, 4)})
            # revival: any later-depth r exceeding an earlier local minimum by >3 sigma
            verdict = "MONOTONE-DECAY(ambiguous)"
            rs = [row["r"] for row in rows]; ss = [row["sigma_r"] for row in rows]
            for a in range(len(rs)):
                for b2 in range(a + 1, len(rs)):
                    if rs[b2] - rs[a] > 3 * np.hypot(ss[a], ss[b2]):
                        verdict = f"REVIVAL(coherent) d{rows[a]['depth']}->d{rows[b2]['depth']} " \
                                  f"(+{rs[b2]-rs[a]:.4f}, {(rs[b2]-rs[a])/np.hypot(ss[a],ss[b2]):.1f} sigma)"
            ep[q] = {"rows": rows, "verdict": verdict}
        report["per_epoch"][j] = ep

    # CROSS-EPOCH census (rule frozen in this header)
    j1, j2 = JOBS
    both = sorted(set(epochs[j1]) & set(epochs[j2]))
    tally = {"CLOCK": 0, "COIN": 0, "UNDERPOWERED": 0, "MIXED": 0}
    for q in both:
        rows = []
        for D in sorted(set(epochs[j1][q]) & set(epochs[j2][q])):
            b1, b2 = epochs[j1][q][D], epochs[j2][q][D]
            if not (all(k in b1 for k in "XYZ") and all(k in b2 for k in "XYZ")):
                continue
            v1 = np.array([b1[k][0] for k in "XYZ"]); s1 = np.array([b1[k][1] for k in "XYZ"])
            v2 = np.array([b2[k][0] for k in "XYZ"]); s2 = np.array([b2[k][1] for k in "XYZ"])
            r1, r2 = np.linalg.norm(v1), np.linalg.norm(v2)
            if r1 < 1e-6 or r2 < 1e-6:
                continue
            cosang = float(np.clip(np.dot(v1, v2) / (r1 * r2), -1, 1))
            dtheta = float(np.degrees(np.arccos(cosang)))
            # angle noise: worst-case component noise projected across the smaller r
            sang = float(np.degrees(max(np.max(s1), np.max(s2)) / min(r1, r2)))
            dr = float(r2 - r1)
            sdr = float(np.hypot(np.sqrt(np.sum((v1 / r1 * s1) ** 2)), np.sqrt(np.sum((v2 / r2 * s2) ** 2))))
            rows.append({"depth": D, "dtheta_deg": round(dtheta, 2), "sigma_theta": round(sang, 2),
                         "dr": round(dr, 4), "sigma_dr": round(sdr, 4)})
        ang_res = [r for r in rows if r["dtheta_deg"] > 3 * r["sigma_theta"]]
        len_res = [r for r in rows if abs(r["dr"]) > 3 * r["sigma_dr"] and r["dr"] < 0]
        if ang_res and not len_res:
            v = "CLOCK"
        elif len_res and not ang_res:
            v = "COIN"
        elif ang_res and len_res:
            v = "MIXED"
        else:
            v = "UNDERPOWERED"
        tally[v] += 1
        report["cross_epoch"][q] = {"rows": rows, "verdict": v}
    report["census_tally"] = tally
    report["census_note"] = ("verdicts per drifter; disagreement across drifters is a finding, "
                             "not averaged away")

    out = os.path.join(RES, f"exp_drift_purity_probe_census_{j1}_{j2}.json")
    json.dump(report, open(out, "w"), indent=1)
    print(json.dumps({k: report[k] for k in ("census_tally",)}, indent=1))
    for j in JOBS:
        for q, d in report["per_epoch"][j].items():
            print(f"  epoch {j[:6]} q{q}: {d['verdict']}")
    for q, d in report["cross_epoch"].items():
        print(f"  census q{q}: {d['verdict']}  " + " ".join(
            f"d{r['depth']}:dθ{r['dtheta_deg']}±{r['sigma_theta']}° dr{r['dr']}±{r['sigma_dr']}" for r in d["rows"]))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
