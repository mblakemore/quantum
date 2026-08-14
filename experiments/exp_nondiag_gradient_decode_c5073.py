#!/usr/bin/env python3
"""Non-diag gradient decode (Whisper C5073): per-rung P-G3 verdicts + the 3-point
grind-vs-score curve (banked best cell + two band rungs). Registered readings:
MONOTONE-GRADED / NON-GRADED / ALL-CLEAN. Usage: --backend ibm_marrakesh|ibm_aachen"""
import argparse, json, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--backend", required=True)
    a = ap.parse_args()
    short = a.backend.replace("ibm_", "")
    MAN = json.load(open(os.path.join(QROOT, "results", f"exp_nondiag_gradient_{short}_c5073_manifest.json")))
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(MAN["job_id"], account_hint=MAN["account"])
    res = svc.job(MAN["job_id"]).result()
    idx = {m["block"]: i for i, m in enumerate(MAN["pubs_meta"])}
    se_d = math.sqrt(2) / math.sqrt(MAN["shots"])

    def xc(tag):
        d = res[idx[tag]].data
        c = d[list(d.keys())[0]].get_counts()
        return (c.get("0", 0) - c.get("1", 0)) / sum(c.values())

    best = json.load(open(os.path.join(QROOT, "results", MAN["best_cell_banked"]["decoded"])))
    curve = [{"score": MAN["best_cell_banked"]["score"], "deficit": best["deficit"],
              "z": best["z"], "verdict": best["verdict"], "rung": "best(banked)"}]
    for r in MAN["rungs"]:
        f = f"f{r['frac']:.2f}"
        vf, vs, vp = xc(f + "_floor"), xc(f + "_science"), xc(f + "_polarity")
        n2f = next(m["cz_count"] for m in MAN["pubs_meta"] if m["block"] == f + "_floor")
        n2s = next(m["cz_count"] for m in MAN["pubs_meta"] if m["block"] == f + "_science")
        gate = vp <= -0.5 and vf >= 0.3
        if gate:
            vfn = math.copysign(abs(vf) ** (n2s / n2f), vf)
            deficit = vfn - vs; z = deficit / se_d
            verdict = "NONDIAG-PRESENT" if deficit > 3 * se_d else "NONDIAG-ABSENT"
        else:
            vfn = deficit = z = None
            verdict = f"RUNG-DEAD(floor {vf:+.3f}, guard-model err {r['vpred']:.2f} predicted)"
        curve.append({"score": r["score"], "path": r["path"], "vpred": r["vpred"],
                      "V_floor": vf, "V_science": vs, "V_polarity": vp,
                      "deficit": deficit, "z": z, "verdict": verdict, "rung": f})
        print(f"{f}: floor {vf:+.3f} science {vs:+.3f} pol {vp:+.3f} -> {verdict}" +
              (f" (deficit {deficit:+.4f} z {z:+.1f})" if gate else ""))
    live = [c for c in curve if c.get("deficit") is not None]
    grinds = [c for c in live if c["verdict"].startswith("NONDIAG-PRESENT")]
    if len(live) >= 3 and grinds:
        mono = all(live[i]["deficit"] <= live[i+1]["deficit"] + 2*se_d for i in range(len(live)-1))
        reading = "MONOTONE-GRADED" if mono else "NON-GRADED (discrete-defect class)"
    elif not grinds:
        reading = f"ALL-CLEAN (threshold > {max(c['score'] for c in live):.4f} on live rungs)"
    else:
        reading = "PARTIAL (dead rungs limit the curve)"
    print(f"CURVE ({short}):", [(round(c['score'],4), None if c['deficit'] is None else round(c['deficit'],4)) for c in curve])
    print("READING:", reading)
    out = os.path.join(QROOT, "results", f"exp_nondiag_gradient_{short}_decoded_c5073.json")
    json.dump({"card": "exp_nondiag_gradient_decode", "cycle": "C5073", "backend": a.backend,
               "job": MAN["job_id"], "account": acct, "cal_epoch": MAN["cal_epoch"],
               "curve": curve, "reading": reading}, open(out, "w"), indent=1)
    print("->", out)


if __name__ == "__main__":
    main()
