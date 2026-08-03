#!/usr/bin/env python3
"""CELL 11 decode/fit/grade (Whisper C5018). Modes:
  --fita <jobA_id>   decode Job A, fit (axis, rate) of banked-epoch1 -> now per drifter,
                     write cell11_jobA_fit_c5018.json (carries Job A's cal_epoch for the
                     same-cal gate in --jobb).
  --grade <jobA_id> <jobB_id>   final grading per the FROZEN rule (see flight script header):
                     per gated drifter (73,26,23) per depth:
                       eligible    : uncomp |dtheta(now vs epoch1)| > 3 sigma
                       DAMPED      : eligible AND comp |dtheta(vs epoch1)| < 3 sigma
                       NOT-DAMPED  : eligible AND comp |dtheta| >= 3 sigma
                       UNDERPOWERED: not eligible
                     q53 reported-not-gated. Margins carried on every row.
Bloch extraction identical to the census decoder (same-job cal, readout-corrected)."""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
QROOT = os.path.join(HERE, "..")
RES = os.path.join(QROOT, "results")
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(QROOT, "scripts"))

BANKED_EP1 = "d9kq85jhdfks73ck12gg"
CENSUS = os.path.join(RES, "exp_drift_purity_probe_census_d9kq85jhdfks73ck12gg_d9l4ncrjf64c739j1q8g.json")
GATED = [73, 26, 23]


def epoch1_bloch():
    rep = json.load(open(CENSUS))
    ep = rep["per_epoch"][BANKED_EP1]
    return {int(q): {r["depth"]: (np.array(r["bloch"], float), r["sigma_r"]) for r in d["rows"]}
            for q, d in ep.items()}


def decode(job_id, man):
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(job_id)
    job = svc.job(job_id)
    res = job.result()
    meta = man["pubs_meta"]
    drifters = man["drifters_active"]
    nphys = 156  # kingston; only drifter marginals are read

    def counts_of(i):
        return res[i].data.meas.get_counts()

    def marg(counts, q):
        tot = sum(counts.values()); s = 0
        for bs, c in counts.items():
            if bs.replace(" ", "")[::-1][q] == "1":
                s += c
        return s / tot, tot

    c0 = counts_of(0); c1 = counts_of(1)
    e0 = {q: marg(c0, q)[0] for q in drifters}
    e1 = {q: 1.0 - marg(c1, q)[0] for q in drifters}
    out = {}
    for i, m in enumerate(meta):
        if m["block"] in ("cal0", "cal1"):
            continue
        D, B, arm = m["depth"], m["basis"], m.get("arm", "uncomp")
        cts = counts_of(i)
        for q in drifters:
            p1, tot = marg(cts, q)
            den = 1 - e0[q] - e1[q]
            if abs(den) < 1e-6:
                continue
            p1c = min(max((p1 - e0[q]) / den, 0.0), 1.0)
            z = 1 - 2 * p1c
            sig = 2 * np.sqrt(p1 * (1 - p1) / tot) / abs(den)
            out.setdefault(q, {}).setdefault(arm, {}).setdefault(D, {})[B] = (z, sig)
    return out


def vecs(byB):
    v = np.array([byB[k][0] for k in "XYZ"])
    s = np.array([byB[k][1] for k in "XYZ"])
    return v, s


def dtheta(v1, s1, v2, s2):
    r1, r2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if r1 < 1e-6 or r2 < 1e-6:
        return None
    ang = float(np.degrees(np.arccos(np.clip(np.dot(v1, v2) / (r1 * r2), -1, 1))))
    sig = float(np.degrees(max(np.max(s1), np.max(s2)) / min(r1, r2)))
    return ang, sig


def do_fita(jid):
    man = json.load(open(os.path.join(RES, f"cell11_jobA_manifest_{jid}.json")))
    now = decode(jid, man)
    ep1 = epoch1_bloch()
    sys.path.insert(0, HERE)
    from exp_cell11_inertial_dampener_whisper_c5018 import fit_axis_rate
    fits = {}
    for q in sorted(set(now) & set(ep1)):
        v_now = {D: vecs(b)[0] for D, b in now[q]["uncomp"].items() if all(k in b for k in "XYZ")}
        v_ep1 = {D: ep1[q][D][0] for D in ep1[q]}
        f = fit_axis_rate(v_ep1, v_now)
        fits[str(q)] = f
        print(f"q{q}: axis {f['axis']} rate {f['rate_deg_per_layer']} deg/layer rms {f['rms_resid']}")
    out = {"fits": fits, "cal_epoch": man["cal_epoch"], "jobA": jid}
    json.dump(out, open(os.path.join(RES, "cell11_jobA_fit_c5018.json"), "w"), indent=1)
    print("-> cell11_jobA_fit_c5018.json (feeds --jobb; same-cal gate armed)")


def do_grade(ja, jb):
    manB = json.load(open(os.path.join(RES, f"cell11_jobB_manifest_{jb}.json")))
    B = decode(jb, manB)
    ep1 = epoch1_bloch()
    report = {"card": "cell11_GRADE", "cycle": "C5018", "substrate": "claude-fable-5",
              "jobA": ja, "jobB": jb, "rows": {}, "tally": {}}
    tally = {"DAMPED": 0, "NOT-DAMPED": 0, "UNDERPOWERED": 0}
    for q in sorted(B):
        rows = []
        for D in sorted(B[q].get("uncomp", {})):
            bu = B[q]["uncomp"].get(D, {}); bc = B[q].get("comp", {}).get(D, {})
            if not (all(k in bu for k in "XYZ") and all(k in bc for k in "XYZ") and D in ep1.get(q, {})):
                continue
            vu, su = vecs(bu); vc, sc = vecs(bc)
            v1 = ep1[q][D][0]; s1 = np.array([ep1[q][D][1]] * 3)
            du = dtheta(v1, s1, vu, su); dc = dtheta(v1, s1, vc, sc)
            if du is None or dc is None:
                continue
            eligible = du[0] > 3 * du[1]
            if not eligible:
                verdict = "UNDERPOWERED"
            elif dc[0] < 3 * dc[1]:
                verdict = "DAMPED"
            else:
                verdict = "NOT-DAMPED"
            rows.append({"depth": D, "uncomp_dtheta": round(du[0], 2), "sigma_u": round(du[1], 2),
                         "comp_dtheta": round(dc[0], 2), "sigma_c": round(dc[1], 2),
                         "verdict": verdict, "gated": q in GATED})
            if q in GATED:
                tally[verdict] += 1
        report["rows"][str(q)] = rows
        for r in rows:
            g = "GATED" if r["gated"] else "reported"
            print(f"q{q} d{r['depth']} [{g}]: uncomp {r['uncomp_dtheta']}±{r['sigma_u']}° "
                  f"-> comp {r['comp_dtheta']}±{r['sigma_c']}°  {r['verdict']}")
    report["tally"] = tally
    out = os.path.join(RES, f"cell11_grade_{jb}.json")
    json.dump(report, open(out, "w"), indent=1)
    print(json.dumps(tally), f"-> {out}")


if __name__ == "__main__":
    if "--fita" in sys.argv:
        do_fita(sys.argv[sys.argv.index("--fita") + 1])
    elif "--grade" in sys.argv:
        i = sys.argv.index("--grade")
        do_grade(sys.argv[i + 1], sys.argv[i + 2])
    else:
        print("modes: --fita <jobA> | --grade <jobA> <jobB>")
