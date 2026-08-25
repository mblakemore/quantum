#!/usr/bin/env python3
"""Counterflow Flight A — SYMMETRIC-EXIT instrument (Whisper C5082, board #195, clean-null redesign).

WHY a 4th design. Flights 1-3 saw the crossing (+0.18/+0.13/+0.175, = sim) but VOIDed on the
equal-stream NULL arm, and the bias survived BOTH readout mitigation (v2) AND noise-aware matched-qubit
placement (v4, exits on q142/q143). The null bias FLIPPED SIGN with the qubit layout (hot-side -0.074
-> cold-side +0.077): a QUBIT-FIXED bias tied to which physical qubit reads which exit. The full-relayout
A/B (counterflow_flight_a_sym) does NOT fix it — proven $0: its layout B mirrors the WHOLE chain, so the
cold-stream ry re-prep lands on a gate-noisy qubit (null_A=+0.001 clean, null_B=+0.151 biased, avg VOID).
Averaging a clean arm with a biased one is not symmetrization.

THE FIX HERE — terminal exit-swap averaging on ONE layout. Two versions of each arm, IDENTICAL physics
(same contacts, advection, dephasing, same 6 physical qubits, same error profile), differing ONLY in a
single terminal SWAP(C0,H2) right before the exit measurement:
  DIRECT  : cold parcel measured on its home qubit C0, hot on H2  -> cross = (cold+dC0) - (hot+dH2)
  SWAPPED : SWAP(C0,H2) then cold parcel (now on H2) -> bit0, hot (now on C0) -> bit1
                                                        -> cross = (cold+dH2) - (hot+dC0)
  average -> cold - hot ; the per-READ-QUBIT bias d{C0,H2} cancels EXACTLY, and the single swap moves
  BOTH parcels together so its gate error is common-mode within each crossing (no balancing needed).
Readout mitigation retained (orthogonal). Same weather-aware quiet layout as v4.

HONEST SCOPE, stated before the sim runs: the terminal swap cancels a per-READ-QUBIT (measurement-time)
bias. It does NOT, by construction, cancel a per-qubit bias ACCUMULATED DURING THE PATH (amplitude
damping / gate error while the parcel idled on its home qubit) — the parcel lived on its home qubit for
the whole circuit in BOTH versions. So the dry-run tests TWO confound models:
  (M1) qubit-fixed READOUT asymmetry on an exit qubit  -> terminal-swap SHOULD clean the null.
  (M2) qubit-fixed AMPLITUDE-DAMPING on an exit qubit   -> terminal-swap should NOT fully clean it.
If M2 stays biased, that is the $0 finding: the confound is path-accumulated, matched-T1 exit selection
(or baseline subtraction) is required, and this instrument alone does not earn a clean-null fly.

Routing unchanged: #151 spend gate (free instance), backend PINNED ibm_fez, --submit only after a fresh
Creator GO citing this file's digest. --dry-run is Aer, $0.
"""
import sys, os, json
import numpy as np
from qiskit import QuantumCircuit, transpile

P_HOT, P_COLD, TAU, N, T, SHOTS = 0.40, 0.05, 0.5, 3, 2, 10000
P_MEAN = (P_HOT + P_COLD) / 2.0
BACKEND_NAME = "ibm_fez"
QUIET_LAYOUT = [123, 136, 143, 142, 141, 144]   # [H0,H1,H2,C0,C1,C2]; exits H2=q143, C0=q142 (v4 matched pair)

def ryang(p): return 2 * np.arcsin(np.sqrt(p))
TH = np.arcsin(np.sqrt(TAU))
def _ps(qc, a, b): qc.rxx(TH, a, b); qc.ryy(TH, a, b)   # excitation-conserving partial-SWAP, tau=1/2

def build(arm, swap_exit):
    """arm in {counterflow, coflow, null}; swap_exit toggles the terminal exit-qubit swap.
    Always measures bit0 = COLD parcel, bit1 = HOT parcel."""
    p_hot = P_MEAN if arm == "null" else P_HOT
    p_cold = P_MEAN if arm == "null" else P_COLD
    qc = QuantumCircuit(6, 2 + 6 * T)
    H = [0, 1, 2]; C = [3, 4, 5]
    for q in H: qc.ry(ryang(p_hot), q)
    for q in C: qc.ry(ryang(p_cold), q)
    cb = 2
    for t in range(T):
        for k in range(N): _ps(qc, H[k], C[k])
        for q in H + C: qc.measure(q, cb); cb += 1        # dephase (Z-basis MCM, discarded)
        if t < T - 1:
            qc.reset(H[2]); qc.swap(H[1], H[2]); qc.swap(H[0], H[1]); qc.reset(H[0]); qc.ry(ryang(p_hot), H[0])
            if arm == "coflow":
                qc.reset(C[2]); qc.swap(C[1], C[2]); qc.swap(C[0], C[1]); qc.reset(C[0]); qc.ry(ryang(p_cold), C[0])
            else:
                qc.reset(C[0]); qc.swap(C[1], C[0]); qc.swap(C[2], C[1]); qc.reset(C[2]); qc.ry(ryang(p_cold), C[2])
    # cold parcel on C[0], hot parcel on H[2]. Terminal exit-swap averaging:
    if swap_exit:
        qc.swap(C[0], H[2])          # cold -> H[2], hot -> C[0]
        qc.measure(H[2], 0)          # cold parcel (now on H[2]) -> bit0
        qc.measure(C[0], 1)          # hot parcel (now on C[0]) -> bit1
    else:
        qc.measure(C[0], 0)          # cold parcel on home qubit -> bit0
        qc.measure(H[2], 1)          # hot parcel on home qubit -> bit1
    return qc

ARMS = ["counterflow", "coflow", "null"]

def build_cal(state):
    qc = QuantumCircuit(6, 2)
    C0, H2 = 3, 2
    if state == 1: qc.x(C0); qc.x(H2)
    qc.measure(C0, 0); qc.measure(H2, 1)
    return qc

def _raw(counts):
    tot = sum(counts.values())
    pc = sum(v for k, v in counts.items() if k.replace(" ", "")[-1] == "1") / tot
    ph = sum(v for k, v in counts.items() if k.replace(" ", "")[-2] == "1") / tot
    return pc, ph
def _correct(p, r0, r1):
    d = 1.0 - r0 - r1; return (p - r0) / d if abs(d) > 1e-6 else p

def _decode_one(counts, cal0, cal1, swapped):
    # cal0/cal1 calibrate the DIRECT mapping: bit0<-C0 (r0c,r1c), bit1<-H2 (r0h,r1h). In the SWAPPED
    # circuit the terminal SWAP(C0,H2) sends bit0<-H2 and bit1<-C0, so the per-bit readout correction
    # must use the OTHER qubit's cal. Applying the direct mapping to both was the $0 M1 bug.
    pc, ph = _raw(counts)
    r0c, r0h = _raw(cal0); pc1, ph1 = _raw(cal1); r1c, r1h = 1 - pc1, 1 - ph1
    if swapped:
        return _correct(pc, r0h, r1h), _correct(ph, r0c, r1c)   # bit0 from H2, bit1 from C0
    return _correct(pc, r0c, r1c), _correct(ph, r0h, r1h)       # bit0 from C0, bit1 from H2

def decode_arm(cts_direct, cts_swapped, cal0, cal1):
    cD, hD = _decode_one(cts_direct, cal0, cal1, swapped=False)
    cS, hS = _decode_one(cts_swapped, cal0, cal1, swapped=True)
    cold = (cD + cS) / 2.0; hot = (hD + hS) / 2.0       # terminal-swap average
    eps = (cold - P_COLD) / (P_HOT - P_COLD)
    return {"cold_exit": round(cold, 4), "hot_exit": round(hot, 4),
            "crossing": round(cold - hot, 4), "eps": round(eps, 4),
            "direct_crossing": round(cD - hD, 4), "swapped_crossing": round(cS - hS, 4)}

def grade(res):
    cf, co, nu = res["counterflow"], res["coflow"], res["null"]
    checks = {
        "P1_crossing_positive": cf["crossing"] > 0,
        "P2_cf_beats_coflow": cf["crossing"] > co["crossing"],
        "P2_eps_cf_above_half": cf["eps"] > 0.5,
        "P2_eps_coflow_at_or_below_half": co["eps"] <= 0.55,
        "P3_null_clean": abs(nu["crossing"]) <= 0.02,
    }
    verdict = "CONFIRMED" if all(checks.values()) else ("VOID(null)" if not checks["P3_null_clean"] else "FALSIFIED")
    return checks, verdict

def _counts_of(pub):
    c = pub.data
    return getattr(c, list(c.__dict__.keys())[0]).get_counts() if hasattr(c, "__dict__") else c.meas.get_counts()

def main():
    mode = "--submit" if "--submit" in sys.argv else "--dry-run"
    model = "M2" if "--m2" in sys.argv else ("M1" if "--m1" in sys.argv else "both")
    # order: (arm, swap) x 3 arms x 2, then cal0, cal1
    order = [(a, s) for a in ARMS for s in (False, True)]
    circ = [build(a, s) for (a, s) in order] + [build_cal(0), build_cal(1)]

    if mode == "--dry-run":
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, ReadoutError, amplitude_damping_error
        def run_model(kind):
            nm = NoiseModel()
            if kind in ("M1",):
                # qubit-fixed READOUT asymmetry on exit qubit index 2 (H2). Mitigation + swap-avg should clean.
                nm.add_readout_error(ReadoutError([[0.90, 0.10], [0.04, 0.96]]), [2])
                nm.add_readout_error(ReadoutError([[0.995, 0.005], [0.006, 0.994]]), [3])
            if kind in ("M2",):
                # qubit-fixed AMPLITUDE DAMPING on exit qubit index 2 (path-accumulated; survives readout mit).
                nm.add_quantum_error(amplitude_damping_error(0.06), ['id', 'ry', 'rz', 'sx', 'x'], [2])
                nm.add_readout_error(ReadoutError([[0.99, 0.01], [0.01, 0.99]]), [2])
                nm.add_readout_error(ReadoutError([[0.99, 0.01], [0.01, 0.99]]), [3])
            if kind in ("M3",):
                # COMBINED ADVERSARIAL: both exits mismatched on EVERY axis at once, strong.
                from qiskit_aer.noise import depolarizing_error
                nm.add_quantum_error(amplitude_damping_error(0.12), ['id', 'ry', 'rz', 'sx', 'x'], [2])
                nm.add_quantum_error(amplitude_damping_error(0.03), ['id', 'ry', 'rz', 'sx', 'x'], [3])
                nm.add_quantum_error(depolarizing_error(0.04, 1), ['ry'], [2])
                nm.add_readout_error(ReadoutError([[0.88, 0.12], [0.05, 0.95]]), [2])
                nm.add_readout_error(ReadoutError([[0.985, 0.015], [0.02, 0.98]]), [3])
            sim = AerSimulator(noise_model=nm)
            cts = [sim.run(c, shots=SHOTS).result().get_counts() for c in circ]
            cal0, cal1 = cts[-2], cts[-1]
            res = {}
            for i, a in enumerate(ARMS):
                di = order.index((a, False)); si = order.index((a, True))
                res[a] = decode_arm(cts[di], cts[si], cal0, cal1)
            checks, verdict = grade(res)
            return {"model": kind, "arms": res, "checks": checks, "verdict": verdict}
        kinds = ["M1", "M2", "M3"] if model == "both" else [model]
        outs = [run_model(k) for k in kinds]
        out = {"card": "counterflow_flight_a_symexit", "cycle": "C5082", "board": 195,
               "source": "Aer dry-run (qubit-fixed confound models M1 readout / M2 amp-damping) — $0",
               "job_id": None, "dry_run_models": outs,
               "params": {"N": N, "tau": TAU, "T": T, "p_hot": P_HOT, "p_cold": P_COLD, "shots": SHOTS}}
        print(json.dumps(out, indent=2))
        tag = "dryrun"
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
        import ibm_multi_account as m
        from qiskit_ibm_runtime import SamplerV2
        svc = m.service_for_submission("IBMQ_TOKEN")
        backend = svc.backend(BACKEND_NAME)
        isa = [transpile(c, backend, optimization_level=3, initial_layout=QUIET_LAYOUT) for c in circ]
        sampler = SamplerV2(mode=backend)
        job = sampler.run(isa, shots=SHOTS)
        job_id = job.job_id()
        print(f"SUBMITTED job_id={job_id} backend={backend.name} circuits={len(circ)} shots={SHOTS}", flush=True)
        r = job.result(); cts = [_counts_of(r[i]) for i in range(len(circ))]
        cal0, cal1 = cts[-2], cts[-1]
        res = {}
        for i, a in enumerate(ARMS):
            di = order.index((a, False)); si = order.index((a, True))
            res[a] = decode_arm(cts[di], cts[si], cal0, cal1)
        checks, verdict = grade(res)
        out = {"card": "counterflow_flight_a_symexit", "cycle": "C5082", "board": 195,
               "source": f"ibm hardware {backend.name} job {job_id}", "job_id": job_id,
               "params": {"N": N, "tau": TAU, "T": T, "p_hot": P_HOT, "p_cold": P_COLD, "shots": SHOTS},
               "arms": res, "checks": checks, "verdict": verdict,
               "prereg": "counterflow-flight-a-preregistration-whisper-c5082.md"}
        print(json.dumps(out, indent=2))
        tag = f"hw_{job_id}"
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
              "results", f"counterflow_flight_a_symexit_{tag}_c5082.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
