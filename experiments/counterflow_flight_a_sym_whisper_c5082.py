#!/usr/bin/env python3
"""Counterflow Flight A — SYMMETRIZED instrument (Whisper C5082, board #195, THIRD fly).

Flights 1 & 2 saw the crossing (+0.18, +0.13, eps~0.75) but VOIDed on the equal-stream null arm:
fly 1 a readout asymmetry (fixed with per-qubit mitigation), fly 2 a deeper STRUCTURAL asymmetry —
the two exit qubits (hot-exit q2, cold-exit q3) have different advection/reset/gate histories, so with
equal streams the hot-exit qubit read 0.30 vs 0.225 (null crossing -0.074, > the |0.02| VOID line).

THE FIX — role-swap (A/B layout) averaging. Per-qubit exit bias: measured@qubit = physics + delta_q.
  Layout A: cold stream exits at q3, hot stream exits at q2  -> crossing_A = (c+d3) - (h+d2)
  Layout B (mirror): cold stream exits at q2, hot stream exits at q3 -> crossing_B = (c+d2) - (h+d3)
  average = [(c+d3-h-d2) + (c+d2-h-d3)] / 2 = c - h   -> the per-qubit bias (d2,d3) CANCELS EXACTLY,
  while the true crossing c-h survives. Same for co-flow and null (null averages to ~0). Per-qubit
  readout mitigation is also kept (cheap, orthogonal). This is a strictly stronger instrument than v2.

Routing unchanged: #151 spend gate (free instance only), backend PINNED ibm_fez. --dry-run uses Aer
(with an ASYMMETRIC per-qubit noise model, to prove the A/B average cancels a bias a single layout
shows); --submit only after a FRESH Creator GO citing this file's digest.
"""
import sys, os, json
import numpy as np
from qiskit import QuantumCircuit, transpile

P_HOT, P_COLD, TAU, N, T, SHOTS = 0.40, 0.05, 0.5, 3, 2, 10000
P_MEAN = (P_HOT + P_COLD) / 2.0
BACKEND_NAME = "ibm_fez"
def ryang(p): return 2 * np.arcsin(np.sqrt(p))
TH = np.arcsin(np.sqrt(TAU))
def _ps(qc, a, b): qc.rxx(TH, a, b); qc.ryy(TH, a, b)

# LAYOUTS: hot-stage qubits and cold-stage qubits (stage 0,1,2). Hot flows 0->2 (exit hot[2]);
# cold flows 2->0 (exit cold[0]). B is the mirror: the two EXIT qubits q2,q3 swap stream roles.
LAYOUTS = {
    "A": {"hot": [0, 1, 2], "cold": [3, 4, 5]},   # hot_exit=q2, cold_exit=q3
    "B": {"hot": [5, 4, 3], "cold": [2, 1, 0]},   # hot_exit=q3, cold_exit=q2  (roles swapped)
}

def build(arm, layout):
    L = LAYOUTS[layout]; H = list(L["hot"]); C = list(L["cold"])
    p_hot = P_MEAN if arm == "null" else P_HOT
    p_cold = P_MEAN if arm == "null" else P_COLD
    qc = QuantumCircuit(6, 2 + 6 * T)
    for q in H: qc.ry(ryang(p_hot), q)
    for q in C: qc.ry(ryang(p_cold), q)
    cb = 2
    for t in range(T):
        for k in range(N): _ps(qc, H[k], C[k])
        for q in H + C: qc.measure(q, cb); cb += 1          # dephase -> classical ladder
        if t < T - 1:
            qc.reset(H[2]); qc.swap(H[1], H[2]); qc.swap(H[0], H[1]); qc.reset(H[0]); qc.ry(ryang(p_hot), H[0])
            if arm == "coflow":
                qc.reset(C[2]); qc.swap(C[1], C[2]); qc.swap(C[0], C[1]); qc.reset(C[0]); qc.ry(ryang(p_cold), C[0])
            else:
                qc.reset(C[0]); qc.swap(C[1], C[0]); qc.swap(C[2], C[1]); qc.reset(C[2]); qc.ry(ryang(p_cold), C[2])
    qc.measure(C[0], 0)   # cold exit (q3 in A, q2 in B)
    qc.measure(H[2], 1)   # hot exit  (q2 in A, q3 in B)
    return qc

def build_cal(state):
    # calibrate the two physical exit qubits q2, q3 (used as exits in BOTH layouts)
    qc = QuantumCircuit(6, 2)
    if state == 1: qc.x(2); qc.x(3)
    qc.measure(3, 0)  # matches cold-exit position in layout A / hot-exit in B
    qc.measure(2, 1)
    return qc

ARMS = ["counterflow", "coflow", "null"]

def _raw(counts):
    tot = sum(counts.values())
    pc = sum(v for k, v in counts.items() if k.replace(" ", "")[-1] == "1") / tot
    ph = sum(v for k, v in counts.items() if k.replace(" ", "")[-2] == "1") / tot
    return pc, ph
def _correct(p, r0, r1):
    d = 1 - r0 - r1; return (p - r0) / d if abs(d) > 1e-6 else p

def decode_layout(counts, cal0, cal1):
    pc, ph = _raw(counts)
    r0c, r0h = _raw(cal0); pc1, ph1 = _raw(cal1); r1c, r1h = 1 - pc1, 1 - ph1
    return _correct(pc, r0c, r1c), _correct(ph, r0h, r1h)   # (cold_exit, hot_exit), readout-mitigated

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
    # 6 physics circuits (3 arms x 2 layouts) + 2 cal
    order = [(a, L) for a in ARMS for L in ("A", "B")]
    circ = [build(a, L) for (a, L) in order] + [build_cal(0), build_cal(1)]

    if mode == "--dry-run":
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error
        nm = NoiseModel()
        # ASYMMETRIC per-qubit error: q2 much worse than q3 (reproduces the structural bias class),
        # so a SINGLE layout is biased and the A/B average must cancel it.
        nm.add_readout_error(ReadoutError([[0.90, 0.10], [0.04, 0.96]]), [2])
        nm.add_readout_error(ReadoutError([[0.99, 0.01], [0.02, 0.98]]), [3])
        nm.add_quantum_error(depolarizing_error(0.03, 1), ['ry'], [2])   # q2 extra 1q error
        sim = AerSimulator(noise_model=nm)
        cts = [sim.run(c, shots=SHOTS).result().get_counts() for c in circ]
        src = "Aer (dry-run WITH asymmetric per-qubit noise q2>>q3 — NO hardware)"
        job_id = None
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
        import ibm_multi_account as m
        from qiskit_ibm_runtime import SamplerV2
        svc = m.service_for_submission("IBMQ_TOKEN")
        backend = svc.backend(BACKEND_NAME)
        isa = [transpile(c, backend, optimization_level=1) for c in circ]
        job = SamplerV2(mode=backend).run(isa, shots=SHOTS)
        job_id = job.job_id()
        print(f"SUBMITTED job_id={job_id} backend={backend.name} circuits={len(circ)} shots={SHOTS}", flush=True)
        r = job.result(); cts = [_counts_of(r[i]) for i in range(len(circ))]
        src = f"ibm hardware {backend.name} job {job_id}"

    cal0, cal1 = cts[-2], cts[-1]
    # per arm: decode layout A and B, then AVERAGE (cancels per-qubit exit bias)
    res = {}; single = {}
    for i, (a, L) in enumerate(order):
        c_exit, h_exit = decode_layout(cts[i], cal0, cal1)
        single.setdefault(a, {})[L] = {"cold_exit": round(c_exit, 4), "hot_exit": round(h_exit, 4),
                                       "crossing": round(c_exit - h_exit, 4)}
    for a in ARMS:
        A, B = single[a]["A"], single[a]["B"]
        cx = (A["crossing"] + B["crossing"]) / 2
        # cold-exit physics averaged across the two exit qubits:
        cold = (A["cold_exit"] + B["cold_exit"]) / 2
        eps = (cold - P_COLD) / (P_HOT - P_COLD)
        res[a] = {"crossing": round(cx, 4), "eps": round(eps, 4),
                  "layout_A_crossing": A["crossing"], "layout_B_crossing": B["crossing"]}
    checks, verdict = grade(res)
    out = {"card": "counterflow_flight_a_symmetrized", "cycle": "C5082", "board": 195, "source": src,
           "job_id": job_id, "params": {"N": N, "tau": TAU, "T": T, "p_hot": P_HOT, "p_cold": P_COLD, "shots": SHOTS},
           "arms": res, "single_layout": single, "checks": checks, "verdict": verdict,
           "prereg": "counterflow-flight-a-preregistration-whisper-c5082.md"}
    print(json.dumps(out, indent=2))
    tag = "dryrun" if mode == "--dry-run" else "hw"
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
              "results", f"counterflow_flight_a_sym_{tag}_c5082.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
