#!/usr/bin/env python3
"""P1 C1-epoch measured readout q from the FLOWN cal0/cal1 jobs — Elder C6575.

The ALT manifest's readout_cal_spec makes this the AUTHORITATIVE q for the C1 arm:
  cal0 = prep|0>, measure -> P(read 1) = p01     cal1 = prep|1>, measure -> P(read 0) = p10
per qubit on conv_layout (that order), 4096 shots each. backend props are a cross-check only.

WHY IT MATTERS: identification is q-robust (the n6 gate lands IYXZXY across a 50x q range), but the
METER is not — C1 copies-to-identify and therefore the C1/Q margin are billed through p0_of's
weight-dependent p_flip(w,q). The margin spans the Q epoch (2026-07-25) and this C1 epoch
(2026-07-29), so the epoch gap is stated, not hidden.

Bit convention `[::-1]` identical to the scaffold / Q arm / covering driver.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from run_exp66_qpu_partb import _get_ibm_service

MAN = os.path.join(HERE, "..", "results", "exp142_p1_n8_c1_refly_manifest_ALT.json")


def bits_of(job):
    res = job.result()[0]
    reg = list(res.data.keys())[0] if hasattr(res.data, "keys") else "c"
    return [[int(x) for x in s.replace(" ", "")[::-1]] for s in getattr(res.data, reg).get_bitstrings()]


def main():
    man = json.load(open(MAN))
    layout = man["conv_layout"]
    svc = _get_ibm_service()
    cal = man["readout_cal_jobs"]
    print(f"cal0={cal['cal0']} cal1={cal['cal1']}  conv_layout={layout}", flush=True)
    b0, b1 = bits_of(svc.job(cal["cal0"])), bits_of(svc.job(cal["cal1"]))
    print(f"  cal0 {len(b0)} shots, cal1 {len(b1)} shots (manifest cal_shots={man['cal_shots']})")
    n = len(layout)
    per, props = {}, man.get("q_backend_props_per_qubit", {})
    for i, qb in enumerate(layout):
        p01 = sum(r[i] for r in b0) / len(b0)            # prep|0> read 1
        p10 = sum(1 - r[i] for r in b1) / len(b1)        # prep|1> read 0
        q = (p01 + p10) / 2.0
        pr = props.get(str(qb), {}).get("q")
        per[qb] = {"p01": p01, "p10": p10, "q": q, "backend_props_q": pr}
        print(f"  q{qb:>4}: p01={p01:.5f} p10={p10:.5f}  q={q:.5f}   props_q={pr:.5f}"
              f"  ratio={q/pr:.2f}x" if pr else f"  q{qb:>4}: q={q:.5f}")
    qmean = sum(v["q"] for v in per.values()) / n
    pmean = (sum(v["backend_props_q"] for v in per.values() if v["backend_props_q"]) / n) if props else None
    print(f"\n  MEASURED C1-epoch mean q = {qmean:.6f}"
          + (f"   (backend-props mean {pmean:.6f}, ratio {qmean/pmean:.2f}x)" if pmean else ""))
    out = os.path.join(HERE, "..", "results", "exp142_p1_c1_epoch_q_elder_c6575.json")
    json.dump({"source": "FLOWN cal0/cal1, ALT manifest", "conv_layout": layout,
               "per_qubit": {str(k): v for k, v in per.items()},
               "q_mean_measured": qmean, "q_mean_backend_props": pmean,
               "cal_shots": man["cal_shots"], "epoch": "C1 (2026-07-29)",
               "note": "authoritative q for the C1 meter/margin per manifest readout_cal_spec"},
              open(out, "w"), indent=1)
    print(f"SAVED {out}")


if __name__ == "__main__":
    main()
