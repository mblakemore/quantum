#!/usr/bin/env python3
"""GEAR 1 step A decode (Whisper C5073, board #148) — frozen rules from 8b4008e docstring:
P-A: per edge, phase(2k) linear in k (r2 >= 0.9 over nonzero depths) with conditional rider
|dphi| resolvable above propagated se, on >= half the edges.
P-B: end-of-job repeats (2k=16, c=1, X/Y) reproduce early twins within 3 se.
Visibility < 0.2 at 2k=64 -> that edge fits on {4,16} (reported). Phase = atan2(<Y>,<X>),
readout-corrected, 2k=0 as per-control-state baseline."""
import json, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
MAN = json.load(open(os.path.join(QROOT, "results", "exp_gear1_rider_survey_c5073_manifest.json")))
JOB = MAN["job_id"]
EDGES = [tuple(e) for e in MAN["edges"]]
DEPTHS = MAN["depths_2k"]


def main():
    import numpy as np
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(JOB, account_hint="IBMQ_ALT4")
    res = svc.job(JOB).result()
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

    def expval(tag, q):
        cc = counts(tag); n = sum(cc.values())
        p1 = sum(v for k, v in cc.items() if k.replace(" ", "")[-1 - q] == "1") / n
        p01, p10 = ro(q); vis = max(1e-6, 1 - p01 - p10)
        ev = (1 - 2 * ((p1 - p01) / vis))
        return max(-1, min(1, ev)), n

    def ramsey_q(i):
        a, b = EDGES[i]
        return a if i % 2 == 0 else b

    def phase_vis(twok, ctrl, i, extra=""):
        q = ramsey_q(i)
        x, nx = expval(f"rider_2k{twok}_c{int(ctrl)}_X{extra}", q)
        y, ny = expval(f"rider_2k{twok}_c{int(ctrl)}_Y{extra}", q)
        vis = math.hypot(x, y)
        se_ph = 1.0 / (max(vis, 0.05) * math.sqrt(min(nx, ny)))
        return math.atan2(y, x), vis, se_ph, x, y

    edges_out, pa_pass = [], 0
    for i, (a, b) in enumerate(EDGES):
        rows = {}
        for ctrl in (False, True):
            base_ph, _, _, _, _ = phase_vis(0, ctrl, i)
            seq = []
            prev = 0.0
            for twok in DEPTHS[1:]:
                ph, vis, se, x, y = phase_vis(twok, ctrl, i)
                d = ph - base_ph
                while d - prev > math.pi: d -= 2 * math.pi
                while d - prev < -math.pi: d += 2 * math.pi
                prev = d
                seq.append({"twok": twok, "dphase": d, "vis": vis, "se": se})
            rows[ctrl] = seq
        # per-edge fit window (frozen: drop 2k=64 if vis < 0.2)
        usable = [s["twok"] for s in rows[True] if s["vis"] >= 0.2]
        usable = [t for t in usable if t in [s["twok"] for s in rows[False] if s["vis"] >= 0.2]]
        if len(usable) < 2:
            edges_out.append({"edge": [a, b], "status": "VIS-DEAD", "usable": usable})
            continue
        import numpy as np
        def fit(seq):
            ks = np.array([s["twok"] for s in seq if s["twok"] in usable], float)
            ph = np.array([s["dphase"] for s in seq if s["twok"] in usable], float)
            se = np.array([s["se"] for s in seq if s["twok"] in usable], float)
            w = 1 / se**2
            slope = float(np.sum(w * ks * ph) / np.sum(w * ks * ks))
            pred = slope * ks
            ss_res = float(np.sum(w * (ph - pred)**2)); ss_tot = float(np.sum(w * ph**2)) or 1e-12
            r2 = 1 - ss_res / ss_tot
            se_slope = float(1 / math.sqrt(np.sum(w * ks * ks)))
            return slope, se_slope, r2
        s0, se0, r20 = fit(rows[False])
        s1, se1, r21 = fit(rows[True])
        cond = s1 - s0
        se_cond = math.hypot(se0, se1)
        ok = min(r20, r21) >= 0.9 and abs(cond) > 3 * se_cond
        if ok: pa_pass += 1
        edges_out.append({"edge": [a, b], "usable_2k": usable,
                          "rider_single_mrad_perCZ": round(1000 * s0, 3),
                          "rider_cond_mrad_perCZ": round(1000 * cond, 3),
                          "se_cond_mrad": round(1000 * se_cond, 3),
                          "r2": [round(r20, 3), round(r21, 3)],
                          "coherent_resolved": ok})
    # P-B: repeats
    pb = []
    for basis in ("X", "Y"):
        for i in range(len(EDGES)):
            q = ramsey_q(i)
            e_early, n_e = expval(f"rider_2k16_c1_{basis}", q)
            e_late, n_l = expval(f"rider_2k16_c1_{basis}_repeat", q)
            se = 2 * math.sqrt(1/n_e + 1/n_l) / 2
            pb.append(abs(e_late - e_early) / se)
    pb_worst = max(pb); pb_ok = pb_worst <= 3.0
    n_scored = sum(1 for e in edges_out if e.get("status") != "VIS-DEAD")

    verdict = ("GEAR-CONFIRMED" if pa_pass >= n_scored / 2 and pb_ok else
               "FIELD-PRESENT-UNSTABLE" if pa_pass >= n_scored / 2 else
               "RIDERS-BELOW-RESOLUTION")
    rep = {"card": "exp_gear1_rider_decode", "cycle": "C5073", "job": JOB, "account": acct,
           "cal_epoch": MAN["cal_epoch"],
           "P_A": {"edges_pass": pa_pass, "edges_scored": n_scored},
           "P_B": {"worst_z": round(pb_worst, 2), "pass": pb_ok},
           "edges": edges_out, "verdict": verdict}
    out = os.path.join(QROOT, "results", "exp_gear1_rider_decoded_c5073.json")
    json.dump(rep, open(out, "w"), indent=1)
    for e in edges_out:
        if e.get("status") == "VIS-DEAD":
            print(f"edge {e['edge']}: VIS-DEAD"); continue
        print(f"edge {e['edge']}: cond {e['rider_cond_mrad_perCZ']:+8.3f} mrad/CZ (se {e['se_cond_mrad']:.3f}) "
              f"single {e['rider_single_mrad_perCZ']:+8.3f} r2 {e['r2']} -> {'COHERENT' if e['coherent_resolved'] else 'ns'}")
    print(f"P-A: {pa_pass}/{n_scored} edges coherent-resolved · P-B worst repeat z {pb_worst:.2f} ({'PASS' if pb_ok else 'FAIL'})")
    print(f"VERDICT: {verdict}")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
