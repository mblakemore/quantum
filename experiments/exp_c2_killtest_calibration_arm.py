"""C2 kill-test — the calibration-prediction arm run against the flown rho_t data ($0).

Whisper C4998 (substrate claude-fable-5). Gate 2 of docs/proposal-advantage-after-f121-whisper-c4998.md:
before any advantage flight is designed around the pad-drift channel, run the F121-analog
zero-sample classical arm (predict the channel from published calibration) against the
ALREADY-FLOWN measurements. If it predicts within tolerance, the target dies for $0.

Data: results/pad_drift_localization_c4984.json — 40 bits, per-bit twin-arm biases at
d2q = 160/220/280 (t=80, L.L=I Clifford padding; kingston, curve arc C4983) with the
physical qubit each twin bit lived on. Drifter set (pre-identified by the rho_t arc,
positions {3,13,24,30} = physical {53,26,73,23}): bits whose bias drifts through zero
to NEGATIVE — the RC-resistant coherent signature.

Calibration: results/c2_killtest_kingston_calib_snapshot_c4998.json (fetched this cycle;
last_update 2026-07-23T16:47Z — AFTER the 05:44-06:30Z flight window; the flight ran under
the previous calibration cycle. Logged as a caveat; the class-level result is insensitive.)

Three C2 variants, strictly ordered by generosity to the classical arm:
  C2-cal-pure     : bias_i(d) = (1-2*r_q) * (1-2*p_q)^d, everything from calibration.
                    p_q per 2q layer = gate2q_err_median(q) + decoherence over one layer
                    (t_L = 68 ns): p_dec = 0.5*(1 - exp(-t_L/T1)) + 0.5*(1 - exp(-t_L/T2)).
  C2-cal-anchored : amplitude anchored to the MEASURED first twin point (twin160);
                    decay rate from calibration only. Predicts twin220, twin280.
  C2-class-best   : per-bit least-squares over the ENTIRE stochastic model class
                    bias(d) = A * s^d, A >= 0, s in [0,1] — the supremum of what ANY
                    calibration-parameterized stochastic/Pauli model can output at these
                    error rates (per-layer p << 0.5 => s >= 0 and bias never crosses zero).
                    If even THIS cannot fit a bit, no stochastic model can — the residual
                    is class-irreducible, not a tuning failure.

Kill rule (pre-stated in the proposal): the pad-drift target DIES if C2 predicts the twin
trajectories within eps; it SURVIVES (and the gap becomes the pre-registered C2 baseline)
if the drifter residuals exceed eps under every variant including class-best.
Primary eps = 0.05 on bias scale; 0.02 and 0.10 reported alongside.
"""
import json
import math

CAL = "results/c2_killtest_kingston_calib_snapshot_c4998.json"
DATA = "results/pad_drift_localization_c4984.json"
OUT = "results/exp_c2_killtest_c4998.json"
T_LAYER_NS = 68.0  # cz gate_length from the snapshot (median); pure-gate layer time
DEPTHS = [160, 220, 280]
DRIFTER_POS = [3, 13, 24, 30]
EPS_GRID = [0.02, 0.05, 0.10]

cal = json.load(open(CAL))
tbl = json.load(open(DATA))["twin_bit_table"]


def p_layer(q):
    c = cal["qubits"][str(q)] if str(q) in cal["qubits"] else cal["qubits"][q]
    t1_ns = c["T1_us"] * 1000.0
    t2_ns = c["T2_us"] * 1000.0
    p_dec = 0.5 * (1 - math.exp(-T_LAYER_NS / t1_ns)) + 0.5 * (1 - math.exp(-T_LAYER_NS / t2_ns))
    return c["gate2q_err_median"] + p_dec, c["readout_error"]


def fit_class_best(ds, ys):
    """LSQ over bias(d)=A*s^d, A>=0, s in [0,1] (grid+refine; 1D in s, A closed-form)."""
    best = (float("inf"), 0.0, 1.0)
    grid = [i / 2000.0 for i in range(0, 2001)]
    for s in grid:
        num = sum(y * (s ** d) for d, y in zip(ds, ys))
        den = sum((s ** d) ** 2 for d in ds) or 1e-300
        A = max(0.0, num / den)
        sse = sum((y - A * (s ** d)) ** 2 for d, y in zip(ds, ys))
        if sse < best[0]:
            best = (sse, A, s)
    return best  # (sse, A, s)


rows = []
for r in tbl:
    pos, q = r["pos"], r["phys_twin"]
    meas = [r[f"twin{d}"] for d in DEPTHS]
    p, r_err = p_layer(q)
    s_cal = 1 - 2 * p
    # C2-cal-pure
    pure = [(1 - 2 * r_err) * (s_cal ** d) for d in DEPTHS]
    # C2-cal-anchored: A from twin160
    A_anch = meas[0] / (s_cal ** DEPTHS[0]) if s_cal > 0 else 0.0
    anch = [A_anch * (s_cal ** d) for d in DEPTHS]
    # C2-class-best
    sse, A_cb, s_cb = fit_class_best(DEPTHS, meas)
    cb = [A_cb * (s_cb ** d) for d in DEPTHS]
    rows.append({
        "pos": pos, "phys": q, "drifter": pos in DRIFTER_POS,
        "measured": meas, "p_layer_calib": p,
        "pred_cal_pure": pure, "pred_cal_anchored": anch,
        "pred_class_best": cb, "class_best_params": {"A": A_cb, "s": s_cb},
        "resid_cal_pure": [abs(a - b) for a, b in zip(pure, meas)],
        "resid_cal_anchored": [abs(a - b) for a, b in zip(anch, meas)],
        "resid_class_best": [abs(a - b) for a, b in zip(cb, meas)],
    })


def summarize(key):
    dr = [max(r[key]) for r in rows if r["drifter"]]
    nd = [max(r[key]) for r in rows if not r["drifter"]]
    med = lambda v: sorted(v)[len(v) // 2]
    return {
        "drifter_max_resid_per_bit": dr,
        "drifter_median": med(dr), "drifter_worst": max(dr),
        "nondrifter_median": med(nd), "nondrifter_worst": max(nd),
        "kill_counts": {f"eps={e}": {
            "drifters_within": sum(1 for x in dr if x <= e),
            "nondrifters_within": sum(1 for x in nd if x <= e),
            "n_drifters": len(dr), "n_nondrifters": len(nd)}
            for e in EPS_GRID},
    }


summary = {k: summarize(f"resid_{k}") for k in ["cal_pure", "cal_anchored", "class_best"]}

# Verdict per the pre-stated rule: target DIES only if C2 covers the drifters.
cb = summary["class_best"]["kill_counts"]["eps=0.05"]
verdict = ("TARGET-DIES: calibration-class predicts the drift" if cb["drifters_within"] == cb["n_drifters"]
           else "TARGET-SURVIVES: drift outside the stochastic/calibration model class")

# Secondary finding: class-best residual is itself a DETECTOR of coherent (non-stochastic)
# bits — model-class-based rather than threshold-based. Census it (frozen primary drifter
# set untouched; these are additional candidates for the arc's census).
class_irreducible = [
    {"pos": r["pos"], "phys": r["phys"], "in_prior_census": r["drifter"],
     "measured": r["measured"], "max_resid_class_best": max(r["resid_class_best"])}
    for r in rows if max(r["resid_class_best"]) > 0.10]

out = {
    "card": "exp_c2_killtest", "cycle": "C4998", "substrate": "claude-fable-5",
    "secondary_census_class_irreducible_gt0.10": class_irreducible,
    "proposal": "docs/proposal-advantage-after-f121-whisper-c4998.md (gate 2)",
    "calibration_snapshot": {"file": CAL, "last_update": cal["last_update_date"],
                             "caveat": "snapshot from 16:47Z calibration cycle; flight ran 05:44-06:30Z under the prior cycle. Class-best variant is calibration-independent."},
    "model_notes": {"t_layer_ns": T_LAYER_NS,
                    "class_definition": "bias(d)=A*s^d, A>=0, s in [0,1]; supremum of stochastic/Pauli models at per-layer p<<0.5 (sign change unreachable)"},
    "per_bit": rows, "summary": summary, "verdict": verdict,
}
json.dump(out, open(OUT, "w"), indent=1)

print("VERDICT:", verdict)
for k in ["cal_pure", "cal_anchored", "class_best"]:
    s = summary[k]
    print(f"[{k:13s}] drifter median/worst = {s['drifter_median']:.3f}/{s['drifter_worst']:.3f} | "
          f"non-drifter median/worst = {s['nondrifter_median']:.3f}/{s['nondrifter_worst']:.3f}")
    for e in EPS_GRID:
        kc = s["kill_counts"][f"eps={e}"]
        print(f"   eps={e}: drifters within {kc['drifters_within']}/{kc['n_drifters']}, "
              f"non-drifters {kc['nondrifters_within']}/{kc['n_nondrifters']}")
print("\nDrifter detail (measured -> class-best):")
for r in rows:
    if r["drifter"]:
        print(f"  pos{r['pos']:2d} phys{r['phys']:3d} meas={['%+.3f' % m for m in r['measured']]} "
              f"cb={['%+.3f' % m for m in r['pred_class_best']]} maxres={max(r['resid_class_best']):.3f}")
