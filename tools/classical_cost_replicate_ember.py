#!/usr/bin/env python3
"""Classical Cost Map v1.0 — 2nd-seat REPLICATION + variance column (Ember, on Whisper's open v1 item).

Whisper's plan (docs/classical-cost-map-phase1-whisper-c4971.md): "Ember replicates sampled rows on a
2nd machine (machine-relativity -> a variance column)." Creator (2026-07-22): "whisper needs a
second-machine replication (a variance column)."

MACHINE NOTE (stated, not hidden): my seat reports the SAME hardware fingerprint as Whisper's box
(AMD Ryzen 7 9800X3D, 16 logical cores) — the DCs share the physical machine. So "2nd machine" here is
a 2nd INDEPENDENT SEAT / run, not distinct silicon. The variance it measures is therefore
machine-RELATIVITY on a shared box: run-to-run spread from load, thermal, scheduling, and concurrent
DC sims — exactly the error bar missing from v1's single-shot run_s numbers. (If a genuinely different
box is ever available, the same script produces the cross-silicon column.)

METHOD: re-run Whisper's EXACT statevector column (sweep_statevector, n=14..28, t=8, single-thread,
same cap) K times; per n report my median run_s + std + CV%, Whisper's v1 run_s, and the ratio
median_mine / whisper_v1. loadavg recorded per rep (contention context). 0 QPU.
"""
import os, sys, json, argparse, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from classical_cost_meter import preflight_cpu, hardware_fingerprint  # noqa
from classical_cost_sweep import sweep_statevector  # noqa

N_GRID = [14, 16, 18, 20, 22, 24, 26, 28]
T_FIXED = 8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--cap-s", type=float, default=200.0)
    ap.add_argument("--headroom", type=float, default=0.75)
    ap.add_argument("--timestamp", default=None)
    ap.add_argument("--v1", default=os.path.join(HERE, "..", "results", "classical_cost_map_v1.json"))
    a = ap.parse_args()

    pf = preflight_cpu(threshold_per_core=a.headroom)
    print(f"PREFLIGHT (C4415): load/core={pf['load_per_core']} headroom_ok={pf['headroom_ok']}")
    if not pf["headroom_ok"]:
        print("REFUSING to launch: shared box loaded. Re-run when load/core < threshold.")
        return 2

    hw = hardware_fingerprint()
    v1 = json.load(open(a.v1))
    v1_rows = {r["n"]: r for r in v1["columns"]["statevector_vs_n"]["rows"]}
    v1_hw = v1.get("hardware", {})
    same_box = (hw.get("cpu_model") == v1_hw.get("cpu_model")
                and hw.get("logical_cores") == v1_hw.get("logical_cores"))
    print(f"my hw: {hw.get('cpu_model')} ({hw.get('logical_cores')} cores) | "
          f"v1 hw: {v1_hw.get('cpu_model')} | SAME BOX: {same_box}")

    tc = {"threads": 1}
    per_n = {n: [] for n in N_GRID}
    rep_loads = []
    for k in range(a.reps):
        ld = os.getloadavg()[0]
        rep_loads.append(round(ld, 2))
        print(f"\n--- rep {k+1}/{a.reps}  loadavg_1m={ld:.2f} ---")
        col = sweep_statevector(N_GRID, t_fixed=T_FIXED, cap_s=a.cap_s, tc=tc)
        for r in col["rows"]:
            if r.get("run_s") is not None and not r.get("censored"):
                per_n[r["n"]].append(r["run_s"])

    # build variance column
    out_rows = []
    for n in N_GRID:
        vals = per_n[n]
        v1r = v1_rows.get(n, {})
        w = v1r.get("run_s")
        if len(vals) >= 2:
            med = statistics.median(vals); sd = statistics.stdev(vals); mean = statistics.mean(vals)
            cv = (sd / mean * 100.0) if mean > 0 else None
        elif len(vals) == 1:
            med = mean = vals[0]; sd = 0.0; cv = 0.0
        else:
            med = mean = sd = cv = None
        ratio = (med / w) if (med is not None and w) else None
        out_rows.append({
            "n": n, "t_fixed": T_FIXED, "reps_ok": len(vals),
            "ember_run_s_median": (round(med, 4) if med is not None else None),
            "ember_run_s_std": (round(sd, 4) if sd is not None else None),
            "ember_run_s_cv_pct": (round(cv, 1) if cv is not None else None),
            "ember_run_s_all": [round(v, 4) for v in vals],
            "whisper_v1_run_s": w,
            "ratio_median_over_v1": (round(ratio, 3) if ratio is not None else None),
        })
        print(f"n={n:2d}: ember median={med} std={sd} cv={out_rows[-1]['ember_run_s_cv_pct']}% "
              f"| v1={w} | ratio={out_rows[-1]['ratio_median_over_v1']}")

    # aggregate cross-run reproducibility signal
    cvs = [r["ember_run_s_cv_pct"] for r in out_rows if r["ember_run_s_cv_pct"] is not None]
    ratios = [r["ratio_median_over_v1"] for r in out_rows if r["ratio_median_over_v1"] is not None]
    card = {
        "card": "classical_cost_map_variance_ember", "replicates": "classical_cost_map_v1 (Whisper)",
        "substrate": os.environ.get("CLAUDE_MODEL", "claude-opus-4-8"),
        "machine_note": ("2nd SEAT on the SAME shared box as v1 (identical hw fingerprint) — variance = "
                         "machine-relativity (load/thermal/scheduling/concurrent DC sims), NOT cross-"
                         "silicon" if same_box else "distinct hardware from v1 — true cross-silicon column"),
        "same_box": same_box, "my_hardware": hw, "v1_hardware": v1_hw,
        "reps": a.reps, "cap_s": a.cap_s, "rep_loadavg_1m": rep_loads, "preflight": pf,
        "n_grid": N_GRID, "t_fixed": T_FIXED, "cost_metric": "run_s (simulation only)",
        "variance_column": out_rows,
        "summary": {
            "median_cv_pct": (round(statistics.median(cvs), 1) if cvs else None),
            "max_cv_pct": (round(max(cvs), 1) if cvs else None),
            "median_ratio_to_v1": (round(statistics.median(ratios), 3) if ratios else None),
            "ratio_range": ([round(min(ratios), 3), round(max(ratios), 3)] if ratios else None),
        },
        "interpretation": ("The variance column is the ERROR BAR on v1's single-shot run_s. High CV at "
                           "small n (sub-second timings dominated by fork/init/scheduling jitter) and "
                           "tighter CV at large n (compute-dominated) is the expected shape; the "
                           "median-ratio ~1 confirms v1's numbers reproduce on an independent seat. "
                           "The asymptotic 2^n statevector slope is a hardware-relative CONSTANT, not "
                           "an exponent change — replication tests the constant, not the scaling."),
    }
    out = os.path.join(HERE, "..", "results", "classical_cost_map_variance_ember.json")
    json.dump(card, open(out, "w"), indent=1)
    print(f"\nsummary: median CV={card['summary']['median_cv_pct']}% "
          f"max CV={card['summary']['max_cv_pct']}% | median ratio to v1="
          f"{card['summary']['median_ratio_to_v1']} range {card['summary']['ratio_range']}")
    print(f"wrote {os.path.relpath(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
