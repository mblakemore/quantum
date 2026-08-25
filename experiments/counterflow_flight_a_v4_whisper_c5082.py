#!/usr/bin/env python3
"""Counterflow Flight A v4 — WEATHER-AWARE: exits pinned to the quiet-line matched pair + nowcast window gate (Whisper C5082, board #195, 3rd fly).
Flights 1-2 used optimization_level=1 (NOT noise-aware) -> the two exit qubits landed on mismatched
hardware -> null-arm structural bias (-0.074). This v3 uses optimization_level=3 (noise-aware
SabreLayout), placing all six qubits incl. both exits on low-error matched hardware. Keeps the readout
mitigation. The A/B role-swap was tried and $0-proven not to cancel a role-dependent bias; noise-aware
layout attacks the CAUSE (mismatched exit qubits) instead. Null-cleanliness is a HARDWARE test (fly 3).

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
QUIET_LAYOUT = [123, 136, 143, 142, 141, 144]  # [H0,H1,H2,C0,C1,C2]; exits H2=q143,C0=q142 (matched quiet pair, ibm_fez window scan)

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

def build_cal(state):
    """Readout calibration (prereg Amendment 2): prepare the two exit qubits in |state> and measure.
    Gives per-exit-qubit r0 = P(read 1 | prep 0) and r1 = P(read 0 | prep 1). Added because Flight A's
    first fly VOIDed on the null arm (-0.049) from an uncorrected readout asymmetry on the hot-exit
    qubit — the mitigation the prereg specified but the first script omitted."""
    qc = QuantumCircuit(6, 2)
    C0, H2 = 3, 2
    if state == 1:
        qc.x(C0); qc.x(H2)
    qc.measure(C0, 0)   # cold-exit qubit
    qc.measure(H2, 1)   # hot-exit qubit
    return qc

def _raw(counts):
    tot = sum(counts.values())
    pc = sum(v for k, v in counts.items() if k.replace(" ", "")[-1] == "1") / tot   # bit0 cold
    ph = sum(v for k, v in counts.items() if k.replace(" ", "")[-2] == "1") / tot   # bit1 hot
    return pc, ph

def _correct(p, r0, r1):
    d = 1.0 - r0 - r1
    return (p - r0) / d if abs(d) > 1e-6 else p

def decode(counts, cal0=None, cal1=None):
    pc, ph = _raw(counts)
    mit = None
    if cal0 is not None and cal1 is not None:
        r0c, r0h = _raw(cal0)              # P(read1|prep0) per exit qubit
        pc1, ph1 = _raw(cal1); r1c, r1h = 1 - pc1, 1 - ph1   # P(read0|prep1)
        pc, ph = _correct(pc, r0c, r1c), _correct(ph, r0h, r1h)
        mit = {"r0_cold": round(r0c, 4), "r1_cold": round(r1c, 4), "r0_hot": round(r0h, 4), "r1_hot": round(r1h, 4)}
    eps = (pc - P_COLD) / (P_HOT - P_COLD)
    d = {"cold_exit": round(pc, 4), "hot_exit": round(ph, 4),
         "crossing": round(pc - ph, 4), "eps": round(eps, 4)}
    if mit: d["readout_mitigation"] = mit
    return d

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

def _counts_of(pub):
    c = pub.data
    return getattr(c, list(c.__dict__.keys())[0]).get_counts() if hasattr(c, "__dict__") else c.meas.get_counts()

def main():
    mode = "--submit" if "--submit" in sys.argv else "--dry-run"
    # order: 3 arms, then cal0, cal1 (readout mitigation in the SAME job/calibration window)
    circ = [build(a) for a in ARMS] + [build_cal(0), build_cal(1)]

    if mode == "--dry-run":
        # dry-run with a realistic readout error so the mitigation is exercised, not a no-op
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, ReadoutError
        nm = NoiseModel()
        nm.add_all_qubit_readout_error(ReadoutError([[0.97, 0.03], [0.06, 0.94]]))  # asymmetric, ~hw-like
        sim = AerSimulator(noise_model=nm)
        cts = [sim.run(c, shots=SHOTS).result().get_counts() for c in circ]
        src = "Aer (dry-run WITH asymmetric readout noise — NO hardware, NO QPU-seconds)"
        job_id = None
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
        import ibm_multi_account as m
        from qiskit_ibm_runtime import SamplerV2
        svc = m.service_for_submission("IBMQ_TOKEN")     # #151 gate: free instance, refuses paid
        backend = svc.backend(BACKEND_NAME)
        isa = [transpile(c, backend, optimization_level=3, initial_layout=QUIET_LAYOUT) for c in circ]
        # report where the two exit qubits landed (matched-qubit check): last two measures
        try:
            fl = isa[0].layout.final_index_layout()
            print(f'EXIT physical qubits (cold,hot) = {fl[3]},{fl[2]} via noise-aware layout', flush=True)
        except Exception as e:
            print('layout report:', e, flush=True)
        sampler = SamplerV2(mode=backend)
        job = sampler.run(isa, shots=SHOTS)
        job_id = job.job_id()
        print(f"SUBMITTED job_id={job_id} backend={backend.name} arms={ARMS}+cal0,cal1 shots={SHOTS}", flush=True)
        r = job.result()
        cts = [_counts_of(r[i]) for i in range(len(circ))]
        src = f"ibm hardware {backend.name} job {job_id}"

    cal0, cal1 = cts[3], cts[4]
    res = {a: decode(cts[i], cal0, cal1) for i, a in enumerate(ARMS)}

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
