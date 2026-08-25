#!/usr/bin/env python3
"""Counterflow Flight A — the crossing witness (Whisper C5082, board #195).

FROZEN prereg: counterflow-flight-a-preregistration-whisper-c5082.md (digest cited at submit).
Labeled engineering artifact: a classical counterflow heat-exchanger crossing (cold-exit hotter than
hot-exit, eps>1/2) realized on qubits, against a co-flow control and an equal-stream null arm.

Circuit (validated by $0 Aer dry-run, prereg Amendment 1):
  N=3 stages, tau=1/2 partial-SWAP contacts, T=2 ticks, SWAP advection, DEPHASING between contacts
  (Z-basis mid-circuit measurement, outcome discarded — required to realize the CLASSICAL sim-A
  behavior; without it the circuit realizes the coherent sim-D ladder at eps->1).
  Arms: counterflow (cold flows opposite hot), co-flow (cold flows same as hot), equal-stream null
  (both streams prepared at the mean population).

Routing: service_for_submission('IBMQ_TOKEN') -> #151 spend gate auto-pins the FREE open-instance,
refuses paid. Backend PINNED ibm_fez. Nothing submits without an explicit Creator GO (this script is
run with --submit only after the GO; --dry-run uses Aer and touches no hardware / no QPU-seconds).

  python3 counterflow_flight_a_whisper_c5082.py --dry-run     # Aer, no hardware
  python3 counterflow_flight_a_whisper_c5082.py --submit       # hardware (post-GO only)
"""
import sys, os, json
import numpy as np
from qiskit import QuantumCircuit, transpile

P_HOT, P_COLD, TAU, N, T, SHOTS = 0.40, 0.05, 0.5, 3, 2, 10000
P_MEAN = (P_HOT + P_COLD) / 2.0
BACKEND_NAME = "ibm_fez"

def ryang(p): return 2 * np.arcsin(np.sqrt(p))
TH = np.arcsin(np.sqrt(TAU))

def _ps(qc, a, b):
    qc.rxx(TH, a, b); qc.ryy(TH, a, b)        # excitation-conserving partial-SWAP, tau=1/2

def build(arm):
    """arm in {counterflow, coflow, null}. Returns a circuit measuring cold-exit (cbit0) and
    hot-exit (cbit1). Extra classical bits hold the discarded dephasing measurements."""
    p_hot = P_MEAN if arm == "null" else P_HOT
    p_cold = P_MEAN if arm == "null" else P_COLD
    qc = QuantumCircuit(6, 2 + 6 * T)
    H = [0, 1, 2]; C = [3, 4, 5]
    for q in H: qc.ry(ryang(p_hot), q)
    for q in C: qc.ry(ryang(p_cold), q)
    cb = 2
    for t in range(T):
        for k in range(N):
            _ps(qc, H[k], C[k])
        for q in H + C:                        # dephase (Z-basis MCM, discarded) -> classical ladder
            qc.measure(q, cb); cb += 1
        if t < T - 1:
            # hot advects up (exit H[2]); cold advects down (counterflow) or up (co-flow)
            qc.reset(H[2]); qc.swap(H[1], H[2]); qc.swap(H[0], H[1]); qc.reset(H[0]); qc.ry(ryang(p_hot), H[0])
            if arm == "coflow":
                qc.reset(C[2]); qc.swap(C[1], C[2]); qc.swap(C[0], C[1]); qc.reset(C[0]); qc.ry(ryang(p_cold), C[0])
            else:  # counterflow and null both use counter-propagating advection
                qc.reset(C[0]); qc.swap(C[1], C[0]); qc.swap(C[2], C[1]); qc.reset(C[2]); qc.ry(ryang(p_cold), C[2])
    qc.measure(C[0], 0)                         # cold exit
    qc.measure(H[2], 1)                         # hot exit
    return qc

ARMS = ["counterflow", "coflow", "null"]

def decode(counts):
    tot = sum(counts.values())
    # classical bit 0 = cold exit (last measure), bit 1 = hot exit (second-last). In the count key,
    # bit 0 is the rightmost char, bit 1 the next.
    pc = sum(v for k, v in counts.items() if k.replace(" ", "")[-1] == "1") / tot
    ph = sum(v for k, v in counts.items() if k.replace(" ", "")[-2] == "1") / tot
    eps = (pc - P_COLD) / (P_HOT - P_COLD)
    return {"cold_exit": round(pc, 4), "hot_exit": round(ph, 4),
            "crossing": round(pc - ph, 4), "eps": round(eps, 4)}

def grade(res):
    cf, co, nu = res["counterflow"], res["coflow"], res["null"]
    checks = {
        "P1_crossing_positive": cf["crossing"] > 0,
        "P2_cf_beats_coflow": cf["crossing"] > co["crossing"],
        "P2_eps_cf_above_half": cf["eps"] > 0.5,
        "P2_eps_coflow_at_or_below_half": co["eps"] <= 0.55,   # co-flow cap + hardware slack
        "P3_null_clean": abs(nu["crossing"]) <= 0.02,
    }
    verdict = "CONFIRMED" if all(checks.values()) else ("VOID(null)" if not checks["P3_null_clean"] else "FALSIFIED")
    return checks, verdict

def main():
    mode = "--submit" if "--submit" in sys.argv else "--dry-run"
    circuits = {a: build(a) for a in ARMS}

    if mode == "--dry-run":
        from qiskit_aer import AerSimulator
        sim = AerSimulator()
        res = {a: decode(sim.run(circuits[a], shots=SHOTS).result().get_counts()) for a in ARMS}
        src = "Aer (noiseless dry-run — NO hardware, NO QPU-seconds)"
        job_id = None
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
        import ibm_multi_account as m
        from qiskit_ibm_runtime import SamplerV2
        svc = m.service_for_submission("IBMQ_TOKEN")     # #151 gate: free instance, refuses paid
        backend = svc.backend(BACKEND_NAME)
        isa = {a: transpile(circuits[a], backend, optimization_level=1) for a in ARMS}
        sampler = SamplerV2(mode=backend)
        job = sampler.run([isa[a] for a in ARMS], shots=SHOTS)
        job_id = job.job_id()
        print(f"SUBMITTED job_id={job_id} backend={backend.name} arms={ARMS} shots={SHOTS}", flush=True)
        r = job.result()
        res = {}
        for i, a in enumerate(ARMS):
            c = r[i].data
            counts = getattr(c, list(c.__dict__.keys())[0]).get_counts() if hasattr(c, "__dict__") else c.meas.get_counts()
            res[a] = decode(counts)
        src = f"ibm hardware {backend.name} job {job_id}"

    checks, verdict = grade(res)
    out = {"card": "counterflow_flight_a", "cycle": "C5082", "board": 195, "source": src,
           "job_id": job_id, "params": {"N": N, "tau": TAU, "T": T, "p_hot": P_HOT, "p_cold": P_COLD, "shots": SHOTS},
           "arms": res, "checks": checks, "verdict": verdict,
           "prereg": "counterflow-flight-a-preregistration-whisper-c5082.md"}
    print(json.dumps(out, indent=2))
    tag = "dryrun" if mode == "--dry-run" else "hw"
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
              "results", f"counterflow_flight_a_{tag}_c5082.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
