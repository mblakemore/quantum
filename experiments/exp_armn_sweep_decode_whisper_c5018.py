#!/usr/bin/env python3
"""DECODE the matched delay sweep. Branches frozen in the manifests before submission.

EVERY BRANCH CARRIES THE APPARATUS GATE (u >= 0.700 in-job at the D in question). No claim is
carried from a D where the chip's own witness fails its gate — the C5018 kingston lesson,
compiled in rather than remembered.

Correction validity, combined form (Ember #5148):
  PRIMARY  (free, binary)   invalid if u leaves [0,1] or the corrected distribution has
                            negative mass. Rejecting an impossible output is not selection.
  SECONDARY (reported)      suspect if |correction| > cond x readout_error. Alone this passes
                            fez q71, which is exactly why PRIMARY exists.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

JOBS = {"ibm_kingston": "d9pu5s97s9kc73auhnu0", "ibm_fez": "d9pu5sh7s9kc73auhnug"}
GATE = 0.700


def u_from_bins(p):
    odd = 0.0
    for k in range(16):
        b = [(k >> 3) & 1, (k >> 2) & 1, (k >> 1) & 1, k & 1]
        if ((b[0] & b[1]) ^ (b[2] & b[3])):
            odd += p[k]
    return 1.0 - 2.0 * odd


def decode(bname, jid):
    from ibm_multi_account import service_for_job
    man = json.load(open(os.path.join(RES, f"armn_sweep_manifest_{jid}.json")))
    svc, acct = service_for_job(jid)
    res = svc.job(jid).result()
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

    e0 = perq(cnt(0), 0, pm[0]["shots"]); e1 = perq(cnt(1), 1, pm[1]["shots"])
    rows = []
    for i, m in enumerate(pm):
        if "q" not in m:
            continue
        pl = m["plan"]; idx = (pl["anc1"], pl["anc2"], pl["s1"], m["q"])
        v = np.zeros(16)
        for bstr, n in cnt(i).items():
            b = bstr.replace(" ", "")
            g = lambda p: int(b[w - 1 - p])
            v[(g(idx[0]) << 3) | (g(idx[1]) << 2) | (g(idx[2]) << 1) | g(idx[3])] += n
        p = v / m["shots"]
        u_raw = u_from_bins(p)
        J = None
        for pos in idx:
            A = np.array([[1 - e0[pos], e1[pos]], [e0[pos], 1 - e1[pos]]])
            J = A if J is None else np.kron(J, A)
        cond = float(np.linalg.cond(J)); pc = np.linalg.solve(J, p)
        u = float(u_from_bins(pc)); neg = float(pc[pc < 0].sum())
        ro = float(max(max(e0[x], e1[x]) for x in idx))
        rows.append({"q": m["q"], "D": m["D"], "D_us": m["D_us"], "u_raw": round(float(u_raw), 5),
                     "u": round(u, 5), "cond": round(cond, 3), "neg_mass": round(neg, 6),
                     "worst_readout": round(ro, 4),
                     "VALID": (0.0 <= u <= 1.0) and (neg > -1e-9),
                     "suspect": bool(abs(u - float(u_raw)) > cond * ro)})
    return man, rows


def main():
    out = {}
    for bname, jid in JOBS.items():
        man, rows = decode(bname, jid)
        out[bname] = {"job": jid, "rows": rows, "manifest_branches": man.get("branches")}
        Ds = sorted({r["D"] for r in rows})
        print(f"\n{'='*70}\n{bname}   job {jid}\n{'='*70}")
        print(f"{'D(dt)':>7} {'D(us)':>7} {'n':>3} {'mean u':>8} {'sd':>7} {'GATE':>6}   per-block")
        prof = {}
        for D in Ds:
            v = [r for r in rows if r["D"] == D and r["VALID"]]
            us = np.array([r["u"] for r in v])
            prof[D] = us
            gate = "PASS" if us.mean() >= GATE else "fail"
            det = " ".join(f"q{r['q']}:{r['u']:.3f}" for r in sorted(v, key=lambda x: x["q"]))
            print(f"{D:>7} {v[0]['D_us']:>7.2f} {len(us):>3} {us.mean():>8.4f} "
                  f"{us.std(ddof=1) if len(us)>1 else 0:>7.4f} {gate:>6}   {det}")
        inv = [(r["q"], r["D"]) for r in rows if not r["VALID"]]
        if inv:
            print(f"  INVALID (range check): {inv}")

        clearing = [D for D in Ds if prof[D].mean() >= GATE]
        largest = max(clearing) if clearing else None
        lbl = f"{largest} dt ({largest*4e-3:.2f} us)" if largest is not None else "NONE"
        print(f"\n  LARGEST D CLEARING u>={GATE}: {lbl}")
        if bname == "ibm_kingston":
            br = ("(a) FIXED with useful drift exposure" if largest and largest >= 824 else
                  "(b) FIXED at reduced exposure — price the signal cost" if largest else
                  "(c) NOT the idle — shallow_0 is what needs explaining")
            print(f"  FROZEN BRANCH FIRED: {br}")
        out[bname]["profile"] = {int(D): [round(float(x), 5) for x in prof[D]] for D in Ds}
        out[bname]["largest_clearing_D"] = largest

    # --- SECONDARY: the anomaly, now at MATCHED D ---
    K, F = out["ibm_kingston"]["profile"], out["ibm_fez"]["profile"]
    print(f"\n{'='*70}\nSECONDARY — kingston vs fez at MATCHED D (identical grid, dt=4.0ns both)\n{'='*70}")
    print(f"{'D(dt)':>7} {'kingston':>9} {'fez':>9} {'k loss':>8} {'f loss':>8} {'ratio':>7}  gate-ok?")
    u0k, u0f = np.mean(K[0]), np.mean(F[0])
    for D in sorted(set(K) & set(F)):
        if D == 0:
            continue
        mk, mf = np.mean(K[D]), np.mean(F[D])
        lk, lf = u0k - mk, u0f - mf
        ok = "both" if (mk >= GATE and mf >= GATE) else ("fez only" if mf >= GATE else "neither")
        print(f"{D:>7} {mk:>9.4f} {mf:>9.4f} {lk:>8.4f} {lf:>8.4f} "
              f"{lk/lf if lf > 1e-6 else float('nan'):>7.2f}  {ok}")
    print("  NOTE: ratios from a D where a chip's witness fails its own gate are REPORTED, "
          "NOT CARRIED — the apparatus gate binds the claim, not just the branch.")

    # --- functional form ---
    print(f"\n{'='*70}\nFUNCTIONAL FORM (does loss go linear or multiplicative in D?)\n{'='*70}")
    for bname, prof in (("kingston", K), ("fez", F)):
        Ds = [D for D in sorted(prof) if D > 0]
        u0 = np.mean(prof[0])
        lin = [np.mean(prof[D]) for D in Ds]
        print(f"  {bname}: u0={u0:.4f}")
        for D in Ds:
            m = np.mean(prof[D])
            print(f"    D={D:>5}  u={m:.4f}   loss={u0-m:.4f}   loss/D={1000*(u0-m)/D:.4f} per 1000dt"
                  f"   ln(u/u0)/D={1000*np.log(max(m,1e-6)/u0)/D:+.4f} per 1000dt")
        print("    LINEAR if loss/D is constant; MULTIPLICATIVE if ln(u/u0)/D is constant.")

    # --- tertiary: the coincidence, with D as covariate ---
    kr = out["ibm_kingston"]["rows"]
    print(f"\n{'='*70}\nTERTIARY — the q21/q47 coincidence with D as covariate\n{'='*70}")
    print(f"{'q':>4} " + " ".join(f"{D:>8}" for D in sorted(set(r['D'] for r in kr))))
    for q in sorted(set(r["q"] for r in kr)):
        cells = []
        for D in sorted(set(r["D"] for r in kr)):
            m = [r for r in kr if r["q"] == q and r["D"] == D and r["VALID"]]
            cells.append(f"{m[0]['u']:>8.4f}" if m else f"{'INVALID':>8}")
        mark = "  <-- HIGH pair" if q in (21, 47) else ""
        print(f"{q:>4} " + " ".join(cells) + mark)
    print("  HIGH at every D = block property | only at long D = D-dependent | "
          "tracks others = the original split was noise.")

    path = os.path.join(RES, "armn_sweep_decode_c5018.json")
    json.dump({"card": "armn_sweep_decode", "cycle": "C5018", "substrate": "claude-fable-5",
               "gate": GATE, "chips": out}, open(path, "w"), indent=1)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
