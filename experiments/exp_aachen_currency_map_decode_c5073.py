#!/usr/bin/env python3
"""Aachen currency-map decode (Whisper C5073) — frozen rules from a013389 docstring.
Estimator math carried verbatim from the GEAR-1 and GEAR-3 decodes (one code path per axis)."""
import json, os, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
MAN = json.load(open(os.path.join(QROOT, "results", "exp_aachen_currency_map_c5073_manifest.json")))
JOB = MAN["job_id"]
EDGES = [tuple(e) for e in MAN["edges"]]
DEPTHS = MAN["depths_2k"]


def main():
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(JOB, account_hint="IBMQ_TOKEN")
    res = svc.job(JOB).result()
    idx = {m["block"]: i for i, m in enumerate(MAN["pubs_meta"])}
    n2q = {m["block"].replace("switch_", ""): m.get("cz_count") for m in MAN["pubs_meta"] if "switch" in m["block"]}

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
        return max(-1, min(1, 1 - 2 * ((p1 - p01) / vis))), n

    ramsey = lambda i: EDGES[i][0] if i % 2 == 0 else EDGES[i][1]

    # --- A-PHASE-FIELD (GEAR-1 estimator, usable-depth rule vis>=0.2) ---
    field_edges = 0; edge_rows = []
    for i in range(len(EDGES)):
        q = ramsey(i)
        rows = {}
        for ctrl in (False, True):
            base = math.atan2(*[expval(f"rider_2k0_c{int(ctrl)}_{b}", q)[0] for b in ("Y", "X")])
            seq, prev = [], 0.0
            for twok in DEPTHS[1:]:
                x, nx = expval(f"rider_2k{twok}_c{int(ctrl)}_X", q)
                y, ny = expval(f"rider_2k{twok}_c{int(ctrl)}_Y", q)
                vis = math.hypot(x, y)
                d = math.atan2(y, x) - base
                while d - prev > math.pi: d -= 2 * math.pi
                while d - prev < -math.pi: d += 2 * math.pi
                prev = d
                seq.append((twok, d, vis, 1.0 / (max(vis, 0.05) * math.sqrt(min(nx, ny)))))
            rows[ctrl] = seq
        usable = [t for (t, _, v, _) in rows[True] if v >= 0.2 and
                  any(tt == t and vv >= 0.2 for (tt, _, vv, _) in rows[False])]
        if len(usable) < 2:
            edge_rows.append({"edge": list(EDGES[i]), "status": "VIS-DEAD"}); continue
        def fit(seq):
            ks = np.array([t for (t, d, v, s) in seq if t in usable], float)
            ph = np.array([d for (t, d, v, s) in seq if t in usable], float)
            se = np.array([s for (t, d, v, s) in seq if t in usable], float)
            w = 1 / se**2
            slope = float(np.sum(w * ks * ph) / np.sum(w * ks * ks))
            return slope, float(1 / math.sqrt(np.sum(w * ks * ks)))
        s0, se0 = fit(rows[False]); s1, se1 = fit(rows[True])
        cond, sec = s1 - s0, math.hypot(se0, se1)
        resolved = abs(cond) > 3 * sec
        if resolved: field_edges += 1
        edge_rows.append({"edge": list(EDGES[i]), "cond_mrad": round(1000*cond, 3),
                          "se_mrad": round(1000*sec, 3), "resolved": resolved})
    a_field = "FIELD-PRESENT" if field_edges >= 4 else "FIELD-BELOW-RESOLUTION"

    # --- A-PHASE-STAB: repeats vs early twins ---
    zs = []
    for basis in ("X", "Y"):
        for i in range(len(EDGES)):
            q = ramsey(i)
            e, ne = expval(f"rider_2k16_c1_{basis}", q)
            l, nl = expval(f"rider_2k16_c1_{basis}_repeat", q)
            se = 2 * math.sqrt(1/ne + 1/nl) / 2
            zs.append(abs(l - e) / se)
    worst = max(zs)
    a_stab = ("TURBULENT-REPLICATES" if worst > 10 else
              "STABLE-DIFFERS" if worst <= 3 else f"INTERMEDIATE({worst:.1f})")

    # --- A-NONDIAG: GEAR-3 rule verbatim ---
    def xc(tag):
        cc = counts(tag); n = sum(cc.values())
        return (cc.get("0", 0) - cc.get("1", 0)) / n
    vf, vs, vp = xc("switch_floor"), xc("switch_science"), xc("switch_polarity")
    se_d = math.sqrt(2) / math.sqrt(8000)
    gate = vp <= -0.5 and vf >= 0.3
    if gate:
        vfn = math.copysign(abs(vf) ** (n2q["science"] / n2q["floor"]), vf)
        deficit = vfn - vs; zn = deficit / se_d
        a_nd = "NONDIAG-PRESENT" if deficit > 3 * se_d else "NONDIAG-ABSENT-AT-RESOLUTION"
    else:
        vfn = deficit = zn = None; a_nd = "NO-TEST(gate)"

    # --- A-POP: paired sentinels ---
    def eps(tag):
        cc = counts(tag); n = sum(cc.values())
        return sum(v for k, v in cc.items() if k.replace(" ", "") in ("01", "10")) / n, n
    e_e, n_e = eps("sentinel_early"); e_l, n_l = eps("sentinel_late")
    se_p = math.sqrt(e_e*(1-e_e)/n_e + e_l*(1-e_l)/n_l)
    zp = (e_l - e_e) / max(se_p, 1e-9)
    a_pop = "QUIET" if abs(zp) <= 3 else "POPULATION-MOTION"

    rep = {"card": "exp_aachen_currency_map_decode", "cycle": "C5073", "job": JOB,
           "account": acct, "cal_epoch": MAN["cal_epoch"],
           "A_PHASE_FIELD": {"verdict": a_field, "resolved_edges": field_edges, "edges": edge_rows},
           "A_PHASE_STAB": {"verdict": a_stab, "worst_z": worst},
           "A_NONDIAG": {"verdict": a_nd, "V_floor": vf, "V_science": vs, "V_polarity": vp,
                          "V_floor_norm": vfn, "deficit": deficit, "z": zn},
           "A_POP": {"verdict": a_pop, "eps_early": e_e, "eps_late": e_l, "z": zp}}
    out = os.path.join(QROOT, "results", "exp_aachen_currency_map_decoded_c5073.json")
    json.dump(rep, open(out, "w"), indent=1)
    print(f"A-PHASE-FIELD: {a_field} ({field_edges} edges resolved)")
    print(f"A-PHASE-STAB:  {a_stab} (worst repeat z {worst:.1f})")
    print(f"A-NONDIAG:     {a_nd}" + (f" (floor {vf:+.3f} norm {vfn:+.3f} science {vs:+.3f} deficit {deficit:+.4f} z {zn:+.1f})" if gate else f" (floor {vf:+.3f} polarity {vp:+.3f})"))
    print(f"A-POP:         {a_pop} (eps {e_e:.4f} -> {e_l:.4f}, z {zp:+.2f})")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
