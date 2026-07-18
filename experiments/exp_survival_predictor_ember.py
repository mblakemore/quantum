#!/usr/bin/env python3
"""Measured-noise SURVIVAL PREDICTOR v2 (Ember, C4199) — per-qubit baseline, protection term REMOVED.

WHAT CHANGED FROM v1 (and why): v1 used a single hard-coded E_CX=0.0106 borrowed from the Exp148b
READER qubits and applied it to every circuit. On the Exp151b DTC chain (qubits 123,124,125,136,142,143)
that borrowed rate was ~5x too high — the DTC ran on good qubits (measured mean CZ 0.00217). So v1's
"generic" prediction under-shot the DTC amplitude by up to 0.27, and a two-term fit read that gap as a
spurious "structured-protection factor" of ~2.9x (beta 0.0077/gate, E_eff 0.0030). THE PROTECTION WAS
AN ARTIFACT. Using the CORRECT per-qubit baseline, a clean two-parameter fit gives:

    A_hw/A_ideal = B * (1 - E_eff)^n2q      B=0.934 (SPAM/front-end),  E_eff = 0.00214 / 2q
    measured CZ on those exact qubits       = 0.00217 / 2q
    E_eff / measured                        = 0.99   -> observable decays AT the bare gate-error rate
    protection vs correct baseline          = 1.00x  -> NONE.

The Exp151b/​C4196 "interactions protect the observable ~2.9x over generic" claim was a
baseline-mismatch confound (good qubits vs a borrowed worse-qubit rate). Corrected here. (Exp151b's
PRIMARY result — disorder adds no DIFFERENTIAL protection over interactions, a DTC/MATCH ratio on the
SAME qubits — is untouched; baseline cancels in a ratio. Only the "vs generic" secondary claim falls.)

THE FIX (load-bearing, advisor C4199): E_CX is now a REQUIRED per-qubit input. Match the baseline to
the qubits the circuit actually ran on — the same match-the-axis discipline as C4196 (duration) and
C4198 (estimator). `measured_cz(job_id)` pulls it straight from backend properties.

SCOPE that REMAINS (gap G1, genuine): this predicts a generic-DEPOLARIZING decay of a POSITIVE-signal
observable toward its floor. It has NO term that yields a coherent SIGN INVERSION, so it structurally
cannot predict the copy-channel confident-wrong inversion (Exp148 copy arm 0.10-0.34; Exp149b showed
it is not even purely coherent). A green light = "won't drown from decay on these qubits" — NOT "won't
lie from a coherent inversion." That diagnosis is echo/leakage territory, not this gate's.

  python3 exp_survival_predictor_ember.py --backtest
  python3 exp_survival_predictor_ember.py --measured-cz --job d9di5mkjeosc73fhkf6g
  python3 exp_survival_predictor_ember.py --predict --n2q 42 --nmeas 4 --ecx 0.0022 --reps 256
"""
import argparse, math

E_RO = 0.02
SPAM_B = 0.934          # front-end (prep+readout) offset, fitted on the 151b DTC arm; ~1 for low-SPAM readers


def p_true_pred(n2q, n_meas, e_cx):
    """Predicted positive-observable survival under generic depolarizing decay on the ACTUAL qubits.
    e_cx is REQUIRED and MUST be the mean 2q error of the qubits the circuit ran on (not a global
    constant). Passing a borrowed rate is the v1 bug that invented a phantom protection factor."""
    if e_cx is None:
        raise ValueError("e_cx is required — pass the per-qubit mean CZ error (measured_cz(job)).")
    return 0.5 + 0.5 * (1 - e_cx) ** n2q * (1 - E_RO) ** n_meas


def amplitude_pred(n2q, e_cx, a_ideal=1.0, spam=SPAM_B):
    """Predicted hardware amplitude of a coherent observable (e.g. DTC subharmonic): SPAM x ideal x
    per-qubit decay. NO protection term — the observable decays at the qubits' gate-error rate."""
    return spam * a_ideal * (1 - e_cx) ** n2q


def reps_to_recover(n2q, n_meas, n_secret_bits, e_cx, alpha=0.05):
    from statistics import NormalDist
    p = p_true_pred(n2q, n_meas, e_cx)
    delta = p - 0.5
    if delta <= 0:
        return math.inf
    C = 2 ** n_secret_bits - 2
    z = NormalDist().inv_cdf(1 - alpha / max(C, 1))
    return (z * math.sqrt(2 * 0.25) / delta) ** 2


def survives(n2q, n_meas, n_secret_bits, rep_budget, e_cx):
    need = reps_to_recover(n2q, n_meas, n_secret_bits, e_cx)
    return {"e_cx_used": e_cx,
            "p_true_pred": round(p_true_pred(n2q, n_meas, e_cx), 3),
            "reps_needed": None if need == math.inf else round(need, 1),
            "rep_budget": rep_budget,
            "survives": need != math.inf and need <= rep_budget,
            "SCOPE": "generic decay on THESE qubits — blind to coherent inversion (G1)"}


def measured_cz(job_id, backend_name="ibm_fez"):
    """Pull the mean CZ error on the physical qubits a job actually used — the correct baseline."""
    import os, sys, numpy as np
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); job = svc.job(job_id)
    pubs = job.inputs.get("pubs")
    edges = set()
    for pub in pubs:
        qc = pub[0]
        for inst in qc.data:
            if inst.operation.num_qubits == 2:
                edges.add(tuple(sorted(qc.find_bit(b).index for b in inst.qubits)))
    p = svc.backend(backend_name).properties()
    errs = [par.value for (a, b) in edges for g in p.gates
            if g.gate in ("cz", "ecr") and sorted(g.qubits) == sorted([a, b])
            for par in g.parameters if par.name == "gate_error"]
    return {"job": job_id, "n_edges": len(edges), "mean_cz": float(np.mean(errs)),
            "median_cz": float(np.median(errs)), "qubits": sorted({q for e in edges for q in e})}


def backtest():
    """Back-test the DTC amplitude (Exp151b, job d9di5mkjeosc73fhkf6g) three ways: the borrowed-baseline
    v1 model, the corrected per-qubit baseline, and the 2-param (SPAM+E_eff) fit."""
    A_hw = [0.996, 0.885, 0.867, 0.809, 0.767, 0.703, 0.662, 0.595, 0.569, 0.511, 0.457, 0.412, 0.349]
    A_id = [1.0, 1.0, 0.960, 0.951, 0.883, 0.869, 0.794, 0.777, 0.710, 0.681, 0.583, 0.570, 0.468]
    BORROWED, MEAS = 0.0106, 0.00217
    print("BACK-TEST: DTC subharmonic amplitude vs 3 baselines (Exp151b, qubits 123,124,125,136,142,143):")
    print(f"  {'t':>2} {'n2q':>4} {'A_hw':>6} {'borrow':>7} {'per-qb':>7} {'2-par':>7}")
    me = {"borrow": 0.0, "perqb": 0.0, "twopar": 0.0}
    for t, (ahw, aid) in enumerate(zip(A_hw, A_id)):
        n2q = 10 * t
        bor = aid * (1 - BORROWED) ** n2q
        per = aid * (1 - MEAS) ** n2q
        two = SPAM_B * aid * (1 - 0.00214) ** n2q
        for k, v in (("borrow", bor), ("perqb", per), ("twopar", two)):
            me[k] = max(me[k], abs(v - ahw))
        print(f"  {t:>2} {n2q:>4} {ahw:>6.3f} {bor:>7.3f} {per:>7.3f} {two:>7.3f}")
    print(f"\n  max|err|  borrowed(v1)={me['borrow']:.3f}   per-qubit={me['perqb']:.3f}   2-param={me['twopar']:.3f}")
    print(f"  E_eff(fit)=0.00214 vs measured CZ 0.00217 = 0.99x -> observable decays AT the gate-error rate.")
    print(f"  PROTECTION vs correct baseline = 1.00x (NONE). v1's 2.9x was baseline mismatch, now removed.")
    ok = me["perqb"] < 0.12
    print(f"  -> corrected model {'VALIDATED' if ok else 'FAILS'} (per-qubit baseline, no protection term).")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backtest", action="store_true")
    ap.add_argument("--measured-cz", action="store_true"); ap.add_argument("--job")
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--n2q", type=int, default=42); ap.add_argument("--nmeas", type=int, default=4)
    ap.add_argument("--nbits", type=int, default=4); ap.add_argument("--reps", type=int, default=256)
    ap.add_argument("--ecx", type=float, default=None)
    a = ap.parse_args()
    if a.backtest:
        return 0 if backtest() else 1
    if a.measured_cz:
        import json; print(json.dumps(measured_cz(a.job), indent=1)); return 0
    if a.predict:
        import json
        if a.ecx is None:
            print("ERROR: --ecx required (per-qubit mean CZ; get it via --measured-cz --job <id>)"); return 1
        print(json.dumps(survives(a.n2q, a.nmeas, a.nbits, a.reps, a.ecx), indent=1)); return 0
    ap.print_help(); return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
