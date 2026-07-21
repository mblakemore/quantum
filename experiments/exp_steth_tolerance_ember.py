#!/usr/bin/env python3
"""Exp-STETH annex §3 — coherent-SPAM TOLERANCE CURVE (Ember, 0 QPU) for the flight gate.

Whisper's scout (quantum@9d9d68a, results/exp_steth_scout.json) = GO, but tested SPAM-separability at
a SINGLE coherent angle (0.1 rad) and fenced it explicitly:
  "coh_angle=0.1 rad is a chosen pessimistic non-Pauli SPAM; a real coherent fraction must be MEASURED
   on the target region before a flight"  +  flight_gate: "measured coherent-SPAM fraction on the
   target region required before any pre-reg".

A measured fraction is only a gate if there is a THRESHOLD to compare it against. This maps it:
sweep the coherent-SPAM angle theta and the ref-vs-channel DRIFT ratio, and find theta* where the
self-cert bias crosses eps=0.02. The flight is SPAM-safe iff the measured coherent SPAM on the target
region is below theta* (and the drift below the mapped tolerance). That is the concrete pass/fail the
gate needs.

INDEPENDENCE / faithfulness: reuse Whisper's EXACT model (import choi_eigenvalue) so this is
apples-to-apples with her GO point — the contribution is the THRESHOLD she did not map, not a
re-derivation. Adversarial extension: the drift multiplier is varied (she fixed 1.5x), since drift
(SPAM differing between reference and channel runs) is the ratio-cancellation breaker.

Substrate stamped at runtime. No QPU (exact density-matrix, n=1 Choi).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from exp_hss_generator import t_count  # noqa (keeps import graph honest; unused)
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Operator, Pauli
import exp_steth_scout as steth

LAM_TRUE = 0.80
EPS = 0.02


def bias_at(kind, angle, drift_mult=1.5):
    """Bias |ratio - lam_true| at a given coherent angle. For 'drift', temporarily set the model's
    measurement-vs-prep multiplier (Whisper hardcoded 1.5); we vary it to map drift sensitivity."""
    if kind == "drift" and drift_mult != 1.5:
        # replicate choi_eigenvalue's drift branch with an arbitrary multiplier
        return _bias_drift_custom(angle, drift_mult)
    raw, ref, ratio = steth.choi_eigenvalue(LAM_TRUE, kind, angle)
    return abs(ratio - LAM_TRUE)


def _bias_drift_custom(angle, mult):
    def run(apply_channel):
        qc = QuantumCircuit(2)
        steth._bell_prep(qc, 0, 1, over_rot=angle)
        dm = DensityMatrix(qc)
        if apply_channel:
            dm = steth._dephase(dm, 0, LAM_TRUE)
        qmc = QuantumCircuit(2); qmc.ry(angle * mult, 0); qmc.ry(angle * mult, 1)
        dm = dm.evolve(Operator(qmc))
        return float(np.real(dm.expectation_value(Pauli("XX"))))
    raw, ref = run(True), run(False)
    ratio = raw / ref if abs(ref) > 1e-9 else float("nan")
    return abs(ratio - LAM_TRUE)


def find_threshold(kind, drift_mult=1.5, hi=1.2):
    """Smallest angle where bias crosses EPS (bisection; bias is monotone in angle here)."""
    lo, b_lo = 0.0, bias_at(kind, 0.0, drift_mult)
    if b_lo > EPS:
        return 0.0
    b_hi = bias_at(kind, hi, drift_mult)
    if b_hi < EPS:
        return None  # never breaks within range
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if bias_at(kind, mid, drift_mult) < EPS:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    try:
        subst = json.load(open(os.path.join(os.path.dirname(__file__), "..", "..", "DC15E",
                          "state", "current-state.json"))).get("substrate", "claude-opus-4-8")
    except Exception:
        subst = "claude-opus-4-8"

    print("=" * 82)
    print(f"Exp-STETH coherent-SPAM TOLERANCE CURVE (Ember 2-of-2 gate input) — eps={EPS}, "
          f"lam_true={LAM_TRUE}")
    print(f"substrate={subst}; model reused from exp_steth_scout (Whisper quantum@9d9d68a)")
    print("=" * 82)

    angles = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    print(f"{'theta(rad)':>10} {'theta(deg)':>10} {'bias_coherent':>14} {'bias_drift1.5x':>15} "
          f"{'coh_ok':>7} {'drift_ok':>9}")
    rows = []
    for a in angles:
        bc = bias_at("coherent", a)
        bd = bias_at("drift", a)
        rows.append({"theta_rad": a, "theta_deg": round(np.degrees(a), 1),
                     "bias_coherent": round(bc, 5), "bias_drift_1p5x": round(bd, 5),
                     "coherent_ok": bc <= EPS, "drift_ok": bd <= EPS})
        print(f"{a:>10.3f} {np.degrees(a):>10.1f} {bc:>14.5f} {bd:>15.5f} "
              f"{str(bc<=EPS):>7} {str(bd<=EPS):>9}")

    th_coh = find_threshold("coherent")
    th_drift = find_threshold("drift", 1.5)
    # drift-multiplier sensitivity at the scout's 0.1 rad
    drift_sweep = []
    for m in [1.0, 1.25, 1.5, 2.0, 3.0]:
        b = bias_at("drift", 0.10, m)
        drift_sweep.append({"drift_mult": m, "bias_at_0.1rad": round(b, 5), "ok": b <= EPS})

    print("-" * 82)
    def deg(x): return f"{np.degrees(x):.1f} deg" if x is not None else "no break <=1.2 rad"
    print(f"THRESHOLD theta* (bias crosses eps={EPS}):")
    print(f"  coherent (self-ref, same strength ref+channel): theta* = "
          f"{th_coh:.3f} rad ({deg(th_coh)})" if th_coh else "  coherent: no break")
    print(f"  drift    (measure = 1.5x prep, ref!=channel):    theta* = "
          f"{th_drift:.3f} rad ({deg(th_drift)})" if th_drift else "  drift: no break")
    print(f"\ndrift-multiplier sensitivity at 0.1 rad prep:")
    for d in drift_sweep:
        print(f"  measure/prep={d['drift_mult']}x: bias={d['bias_at_0.1rad']} ok={d['ok']}")

    scout_val = 0.10
    headroom_coh = (th_coh / scout_val) if th_coh else None
    print("-" * 82)
    print(f"GATE READOUT for the flight: measured coherent SPAM on the target region must be")
    print(f"  < {th_coh:.3f} rad ({deg(th_coh)}) for the self-cert bias to stay within eps={EPS}.")
    print(f"  Scout assumed 0.10 rad -> headroom {headroom_coh:.1f}x to the wall (self-ref)." )
    print(f"  DRIFT is the tighter risk: if SPAM differs ref-vs-channel by >=1.5x, wall drops to "
          f"{th_drift:.3f} rad ({deg(th_drift)}).")
    print(f"  => flight-safe REQUIRES co-batching ref+channel (no drift window) AND measured coherent "
          f"SPAM below the drift-case wall.")

    out = {
        "card": "exp_steth_tolerance_ember", "role": "annex §3 coherent-SPAM tolerance (flight-gate input)",
        "substrate": subst, "model_source": "exp_steth_scout (Whisper quantum@9d9d68a), reused verbatim",
        "eps": EPS, "lam_true": LAM_TRUE, "sweep": rows,
        "threshold_theta_star_rad": {"coherent_selfref": th_coh, "drift_1p5x": th_drift},
        "threshold_theta_star_deg": {"coherent_selfref": (round(np.degrees(th_coh),1) if th_coh else None),
                                     "drift_1p5x": (round(np.degrees(th_drift),1) if th_drift else None)},
        "drift_multiplier_sensitivity_at_0p1rad": drift_sweep,
        "scout_assumed_rad": scout_val, "headroom_coherent_x": (round(headroom_coh,1) if headroom_coh else None),
        "gate_readout": ("Flight-safe iff measured coherent SPAM on target region < drift-case theta* "
                         "AND ref+channel co-batched to suppress drift. The scout's 0.1-rad assumption "
                         "sits with headroom to the self-ref wall but the DRIFT wall is the binding one."),
    }
    outp = os.path.join(os.path.dirname(__file__), "..", "results", "exp_steth_tolerance_ember.json")
    json.dump(out, open(outp, "w"), indent=1)
    print(f"\nwrote {os.path.relpath(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
