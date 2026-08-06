#!/usr/bin/env python3
"""DECODE route 3. The frozen rule is in the manifest; this file executes it and nothing more.

PRIMARY is an EQUIVALENCE claim -> TOST against the frozen delta. Sigma is used ONLY for the
control (a difference claim) and for the mechanism test (rate != 0). Every branch verdict is a
conjunction with the apparatus gate (probe visibility at the zero point).
"""
import json, os, sys
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

JOB = "d9q2tk7v9q4s73bhnc8g"


def main():
    from ibm_multi_account import service_for_job
    man = json.load(open(os.path.join(RES, f"route3_manifest_{JOB}.json")))
    svc, acct = service_for_job(JOB)
    res = svc.job(JOB).result()
    pm = man["pubs_meta"]; probes = man["probes"]
    DELTA = man["delta_deg"]; VIS = man["vis_gate"]; TH = man["theta_target_deg"]

    # per-pub, per-probe expectation + SE
    def exps(i):
        c = res[i].data
        counts = getattr(c, list(vars(c).keys())[0]).get_counts() if False else c.c.get_counts()
        n = sum(counts.values())
        out = []
        for k in range(len(probes)):
            p1 = sum(v for b, v in counts.items()
                     if int(b.replace(" ", "")[len(probes) - 1 - k]) == 1) / n
            e = 1 - 2 * p1
            se = 2 * np.sqrt(max(p1 * (1 - p1), 1e-12) / n)
            out.append((e, se))
        return out

    data = {}
    for i, m in enumerate(pm):
        for k, (e, se) in enumerate(exps(i)):
            data[(m["kind"], m["n"], m["basis"], k)] = (e, se, m["dur_us"])

    def phase(kind, n, k):
        x, sx, dur = data[(kind, n, "X", k)]
        y, sy, _ = data[(kind, n, "Y", k)]
        v = np.hypot(x, y)
        th = np.degrees(np.arctan2(y, x))
        sth = np.degrees(np.hypot(x * sy, y * sx) / max(v ** 2, 1e-12))
        return th, sth, v, dur

    # ---- APPARATUS GATE (branch precondition, evaluated first) ----
    print(f"{'probe':>6} {'V(zero)':>8} {'gate':>6}")
    gate = {}
    for k, q in enumerate(probes):
        _, _, v, _ = phase("time", 0, k)
        gate[k] = v >= VIS
        print(f"q{q:>5} {v:>8.4f} {('PASS' if gate[k] else 'FAIL'):>6}")
    if not any(gate.values()):
        print("\nAPPARATUS GATE FAILED on every probe -> NO BRANCH MAY FIRE. Reporting only.")

    def unwrap(seq):
        out, off = [], 0.0
        for j, v in enumerate(seq):
            if j and (v + off) - out[-1] < -180:
                off += 360
            elif j and (v + off) - out[-1] > 180:
                off -= 360
            out.append(v + off)
        return np.array(out)

    rows, fits = [], {}
    for kind in ("time", "depth"):
        print(f"\n=== {kind.upper()} arm ===")
        print(f"{'probe':>6} " + " ".join(f"{'n=' + str(n):>10}" for n in man["ladder_n"]) +
              f" {'rate':>12} {'sigma':>7} {'ACTIVE':>7}")
        for k, q in enumerate(probes):
            ph = [phase(kind, n, k) for n in man["ladder_n"]]
            th = unwrap([p[0] for p in ph]); se = np.array([p[1] for p in ph])
            xs = np.array([p[3] for p in ph]) if kind == "time" else np.array(man["ladder_n"], float)
            th0 = th - th[0]
            w = 1 / np.maximum(se, 1e-6) ** 2
            slope = float(np.sum(w * xs * th0) / max(np.sum(w * xs * xs), 1e-12))
            sl_se = float(np.sqrt(1 / max(np.sum(w * xs * xs), 1e-12)))
            sig = abs(slope) / max(sl_se, 1e-12)
            unit = "deg/us" if kind == "time" else "deg/layer"
            fits[(kind, k)] = (slope, sl_se, xs, th0, se)
            print(f"q{q:>5} " + " ".join(f"{t:>10.2f}" for t in th0) +
                  f" {slope:>8.4f}{unit:<4} {sig:>7.1f} {str(sig >= 5):>7}")
            rows.append({"kind": kind, "probe": q, "rate": slope, "rate_se": sl_se,
                         "sigma": sig, "active": bool(sig >= 5), "unit": unit,
                         "phases": [float(t) for t in th0], "phase_se": [float(s) for s in se]})

    print(f"""
=== MECHANISM (frozen rule 2: ACTIVE iff rate != 0 at >=5 sigma) ===""")
    act_t = [r for r in rows if r["kind"] == "time" and r["active"]]
    act_d = [r for r in rows if r["kind"] == "depth" and r["active"]]
    print(f"  TIME arm active on {len(act_t)}/{len(probes)} probes | "
          f"DEPTH arm active on {len(act_d)}/{len(probes)} probes")
    mech = ("BOTH — consistent with a per-TIME rotation (gates carry duration too)"
            if act_t and act_d else
            "TIME ONLY — pure idle detuning; 'the universe rotates it while you wait' is LITERAL"
            if act_t else
            "DEPTH ONLY — a per-GATE phase; the wait does NOT do it, the gates do"
            if act_d else "NEITHER — no coherent accumulation resolved in this job")
    print(f"  -> {mech}")

    # ---- PRIMARY: TOST at the fit-selected rung ----
    print(f"""
=== PRIMARY (frozen rules 3-4: fit-selected rung, TOST vs delta={DELTA} deg) ===""")
    verdicts = []
    for kind in ("time", "depth"):
        for k, q in enumerate(probes):
            r = [x for x in rows if x["kind"] == kind and x["probe"] == q][0]
            if not r["active"]:
                continue
            slope, _, xs, th0, se = fits[(kind, k)]
            pred = np.abs(slope * xs - TH)               # rule 3: closest FITTED phase to target
            j = int(np.argmin(pred[1:]) + 1)
            ref_th, ref_se, ref_v, _ = phase("ref", 0, k)
            sel_abs = th0[j] + phase(kind, 0, k)[0]
            d = sel_abs - ref_th
            d = (d + 180) % 360 - 180
            sed = float(np.hypot(se[j], ref_se))
            t1 = (d + DELTA) / max(sed, 1e-9); t2 = (DELTA - d) / max(sed, 1e-9)
            p1 = 1 - stats.norm.cdf(-t1); p2 = 1 - stats.norm.cdf(-t2)
            p_tost = max(1 - stats.norm.cdf(t1), 1 - stats.norm.cdf(t2))
            equiv = (p_tost < 0.05)
            # control: most distant rung must DISAGREE (difference claim, sigma)
            jc = int(np.argmax(pred[1:]) + 1)
            dc = (th0[jc] + phase(kind, 0, k)[0]) - ref_th
            dc = (dc + 180) % 360 - 180
            sedc = float(np.hypot(se[jc], ref_se))
            ctrl_ok = (abs(dc) - DELTA) / max(sedc, 1e-9) >= 5
            fired = equiv and ctrl_ok and gate[k]
            verdicts.append({"kind": kind, "probe": q, "sel_n": man["ladder_n"][j],
                             "diff_deg": float(d), "se": sed, "p_tost": float(p_tost),
                             "equivalent": bool(equiv), "control_disagrees": bool(ctrl_ok),
                             "gate": bool(gate[k]), "FREE_GATE_CERTIFIED": bool(fired)})
            print(f"  {kind:>5} q{q:<4} rung n={man['ladder_n'][j]:<3} "
                  f"diff {d:>+7.2f} +/- {sed:>5.2f} deg  p_TOST {p_tost:.4f} "
                  f"equiv={equiv}  control_disagrees={ctrl_ok}  gate={gate[k]}  "
                  f"-> {'CERTIFIED' if fired else 'not certified'}")
            if not ctrl_ok:
                print(f"        NOTE: control did not disagree (|{dc:.1f}| deg) -> PRIMARY VOID by rule 5")

    n_cert = sum(1 for v in verdicts if v["FREE_GATE_CERTIFIED"])
    print(f"""
=== VERDICT ===
  free gate CERTIFIED on {n_cert} of {len(verdicts)} eligible (arm x probe) cells
  mechanism: {mech}""")
    out = os.path.join(RES, f"route3_decode_{JOB}.json")
    json.dump({"card": "route3_decode", "cycle": "C5018", "substrate": "claude-fable-5",
               "job": JOB, "delta_deg": DELTA, "vis_gate": VIS, "theta_target": TH,
               "mechanism": mech, "gate": {str(probes[k]): bool(v) for k, v in gate.items()},
               "rows": rows, "verdicts": verdicts, "n_certified": n_cert},
              open(out, "w"), indent=1)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
