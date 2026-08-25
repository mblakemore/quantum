#!/usr/bin/env python3
"""Counterflow Flight A — POPULATION-SWAP symmetric instrument (Whisper C5082, board #195, clean-null fly).

The transpile-proof clean-null instrument. v5 (terminal exit-swap) VOIDed because the transpiler
VIRTUALIZED the pre-measurement SWAP -> both versions read the SAME physical qubits, no exchange, no
cancellation. THIS design forces the exit exchange through the STATE PREPARATION (ry angles) + the
classical BIT WIRING, neither of which a transpiler can virtualize:
  A: hot-pop on H-chain (exit H2), cold-pop on C-chain (exit C0)  -> bit0<-C0 (cold), bit1<-H2 (hot)
  B: cold-pop on H-chain (exit H2), hot-pop on C-chain (exit C0)  -> bit0<-H2 (cold), bit1<-C0 (hot)
  average -> cold - hot ; per-exit-qubit bias cancels. Verified transpile-proof: ver A reads bit0<-phys
  q142, ver B reads bit0<-phys q144 (DIFFERENT physical qubits — the precondition v5 lacked).

$0 VALIDATION ON THE TRANSPILED CIRCUIT (counterflow_flight_a_popswap_validate, quantum@7bc91b8):
  A/B average cleans localized physical confounds — q142: A-only null +0.051 -> avg -0.006; q144:
  A-only -0.054 -> avg +0.001; from_backend (real ibm_fez noise + routing): null +0.004 CONFIRMED,
  crossing +0.169. Robust to WHICH exit qubit is bad (the weather-robustness v5 lacked).

FROZEN prereg: counterflow-flight-a-preregistration-whisper-c5082.md Amendment 6. Claim/params/
falsifiers UNCHANGED. Routing: #151 spend gate (free instance), backend PINNED ibm_fez. --submit only
after a FRESH Creator GO citing this file's digest (the v5 GO was consumed by the VOIDed v5).
"""
import sys, os, json
import numpy as np
from qiskit import QuantumCircuit, transpile

P_HOT, P_COLD, TAU, N, T, SHOTS = 0.40, 0.05, 0.5, 3, 2, 10000
P_MEAN = (P_HOT + P_COLD) / 2.0
BACKEND_NAME = "ibm_fez"
QUIET_LAYOUT = [123, 136, 143, 142, 141, 144]   # [H0,H1,H2,C0,C1,C2]
def ryang(p): return 2 * np.arcsin(np.sqrt(p))
TH = np.arcsin(np.sqrt(TAU))
def _ps(qc, a, b): qc.rxx(TH, a, b); qc.ryy(TH, a, b)

def build(arm, ver):
    if arm == "null":
        pH = pC = P_MEAN
    elif ver == "A":
        pH, pC = P_HOT, P_COLD
    else:
        pH, pC = P_COLD, P_HOT
    qc = QuantumCircuit(6, 2 + 6 * T)
    H = [0, 1, 2]; C = [3, 4, 5]
    for q in H: qc.ry(ryang(pH), q)
    for q in C: qc.ry(ryang(pC), q)
    cb = 2
    for t in range(T):
        for k in range(N): _ps(qc, H[k], C[k])
        for q in H + C: qc.measure(q, cb); cb += 1
        if t < T - 1:
            qc.reset(H[2]); qc.swap(H[1], H[2]); qc.swap(H[0], H[1]); qc.reset(H[0]); qc.ry(ryang(pH), H[0])
            if arm == "coflow":
                qc.reset(C[2]); qc.swap(C[1], C[2]); qc.swap(C[0], C[1]); qc.reset(C[0]); qc.ry(ryang(pC), C[0])
            else:
                qc.reset(C[0]); qc.swap(C[1], C[0]); qc.swap(C[2], C[1]); qc.reset(C[2]); qc.ry(ryang(pC), C[2])
    if ver == "A":
        qc.measure(C[0], 0); qc.measure(H[2], 1)
    else:
        qc.measure(H[2], 0); qc.measure(C[0], 1)
    return qc

ARMS = ["counterflow", "coflow", "null"]

def build_cal(state, ver):
    qc = QuantumCircuit(6, 2)
    C0, H2 = 3, 2
    if state == 1: qc.x(C0); qc.x(H2)
    if ver == "A":
        qc.measure(C0, 0); qc.measure(H2, 1)
    else:
        qc.measure(H2, 0); qc.measure(C0, 1)
    return qc

def _raw(counts):
    tot = sum(counts.values())
    pc = sum(v for k, v in counts.items() if k.replace(" ", "")[-1] == "1") / tot
    ph = sum(v for k, v in counts.items() if k.replace(" ", "")[-2] == "1") / tot
    return pc, ph
def _correct(p, r0, r1):
    d = 1.0 - r0 - r1; return (p - r0) / d if abs(d) > 1e-6 else p
def _decode(counts, cal0, cal1):
    pc, ph = _raw(counts)
    r0c, r0h = _raw(cal0); pc1, ph1 = _raw(cal1); r1c, r1h = 1 - pc1, 1 - ph1
    return _correct(pc, r0c, r1c), _correct(ph, r0h, r1h)

def grade(res):
    cf, co, nu = res["counterflow"], res["coflow"], res["null"]
    checks = {"P1_crossing_positive": cf["crossing"] > 0, "P2_cf_beats_coflow": cf["crossing"] > co["crossing"],
              "P2_eps_cf_above_half": cf["eps"] > 0.5, "P2_eps_coflow_at_or_below_half": co["eps"] <= 0.55,
              "P3_null_clean": abs(nu["crossing"]) <= 0.02}
    verdict = "CONFIRMED" if all(checks.values()) else ("VOID(null)" if not checks["P3_null_clean"] else "FALSIFIED")
    return checks, verdict

def _counts_of(pub):
    c = pub.data
    return getattr(c, list(c.__dict__.keys())[0]).get_counts() if hasattr(c, "__dict__") else c.meas.get_counts()

ORDER = [(a, v) for a in ARMS for v in ("A", "B")]
def decode_all(cts):
    calA0, calA1, calB0, calB1 = cts[-4], cts[-3], cts[-2], cts[-1]
    res = {}
    for a in ARMS:
        iA = ORDER.index((a, "A")); iB = ORDER.index((a, "B"))
        cA, hA = _decode(cts[iA], calA0, calA1)
        cB, hB = _decode(cts[iB], calB0, calB1)
        cold = (cA + cB) / 2; hot = (hA + hB) / 2
        res[a] = {"cold_exit": round(cold, 4), "hot_exit": round(hot, 4), "crossing": round(cold - hot, 4),
                  "eps": round((cold - P_COLD) / (P_HOT - P_COLD), 4),
                  "verA_crossing": round(cA - hA, 4), "verB_crossing": round(cB - hB, 4)}
    return res

def main():
    mode = "--submit" if "--submit" in sys.argv else "--dry-run"
    circ = [build(a, v) for (a, v) in ORDER] + [build_cal(0, "A"), build_cal(1, "A"), build_cal(0, "B"), build_cal(1, "B")]

    if mode == "--dry-run":
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
        import ibm_multi_account as m
        svc = m.service_for_submission("IBMQ_TOKEN"); backend = svc.backend(BACKEND_NAME)
        from qiskit_aer import AerSimulator
        sim = AerSimulator.from_backend(backend)
        isa = [transpile(c, backend, optimization_level=3, initial_layout=QUIET_LAYOUT) for c in circ]
        cts = [sim.run(c, shots=SHOTS).result().get_counts() for c in isa]
        src = "Aer from_backend(ibm_fez) — $0 dry-run (real noise snapshot + real routing)"
        job_id = None
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
        import ibm_multi_account as m
        from qiskit_ibm_runtime import SamplerV2
        svc = m.service_for_submission("IBMQ_TOKEN")
        backend = svc.backend(BACKEND_NAME)
        isa = [transpile(c, backend, optimization_level=3, initial_layout=QUIET_LAYOUT) for c in circ]
        job = SamplerV2(mode=backend).run(isa, shots=SHOTS)
        job_id = job.job_id()
        print(f"SUBMITTED job_id={job_id} backend={backend.name} circuits={len(circ)} shots={SHOTS}", flush=True)
        r = job.result(); cts = [_counts_of(r[i]) for i in range(len(circ))]
        src = f"ibm hardware {backend.name} job {job_id}"

    res = decode_all(cts)
    checks, verdict = grade(res)
    out = {"card": "counterflow_flight_a_popswap", "cycle": "C5082", "board": 195, "source": src, "job_id": job_id,
           "params": {"N": N, "tau": TAU, "T": T, "p_hot": P_HOT, "p_cold": P_COLD, "shots": SHOTS},
           "arms": res, "checks": checks, "verdict": verdict,
           "prereg": "counterflow-flight-a-preregistration-whisper-c5082.md"}
    print(json.dumps(out, indent=2))
    tag = "dryrun" if mode == "--dry-run" else f"hw_{job_id}"
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
              "results", f"counterflow_flight_a_popswap_{tag}_c5082.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
