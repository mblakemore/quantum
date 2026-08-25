#!/usr/bin/env python3
"""$0 TRANSPILE-PROOF validation of the population-swap symmetric instrument (Whisper C5082, board #195).

NOT a flight script — a $0 validator. Builds NO --submit path. Its whole job is to answer, on the
TRANSPILED circuit (the gap that sank the terminal-swap v5: a pre-measure SWAP got virtualized), whether
a population-swap exit exchange cleans the null.

DESIGN (transpile-proof by construction): two versions per arm, SAME physical qubits, SAME layout, NO
terminal swap and NO relayout. Version B swaps which STREAM's populations sit on which chain and reads
the cold PARCEL wherever it exits:
  A: H-chain=hot pop (exit H2), C-chain=cold pop (exit C0)  -> bit0<-C0 (cold), bit1<-H2 (hot)
  B: H-chain=cold pop (exit H2), C-chain=hot pop (exit C0)  -> bit0<-H2 (cold), bit1<-C0 (hot)
  average -> cold - hot ; per-exit-qubit bias d{C0,H2} cancels. The A/B difference is in the ry PREP
  angles + the classical BIT assignment, both real gates/wiring the transpiler cannot virtualize.

VALIDATION (all on the transpiled circuit, opt_level=3 + initial_layout, exactly as a fly would):
  - PHYS confound: inject amp-damping + readout on ONE PHYSICAL exit qubit; the single-version (A only)
    null must be biased and the A/B average must clean it. This is the test v5's logical dry-run skipped.
  - from_backend: real ibm_fez noise snapshot + real routing.
Prints where each version's exits physically land (proof the two versions measure the same phys qubits
into SWAPPED bits — the cancellation's precondition) and the direct-vs-avg nulls.
"""
import sys, os, json
import numpy as np
from qiskit import QuantumCircuit, transpile

P_HOT, P_COLD, TAU, N, T, SHOTS = 0.40, 0.05, 0.5, 3, 2, 8000
P_MEAN = (P_HOT + P_COLD) / 2.0
BACKEND_NAME = "ibm_fez"
QUIET_LAYOUT = [123, 136, 143, 142, 141, 144]   # [H0,H1,H2,C0,C1,C2]
def ryang(p): return 2 * np.arcsin(np.sqrt(p))
TH = np.arcsin(np.sqrt(TAU))
def _ps(qc, a, b): qc.rxx(TH, a, b); qc.ryy(TH, a, b)

def build(arm, ver):
    """ver 'A' or 'B'. B swaps the stream populations between H/C chains and swaps the exit->bit wiring."""
    if arm == "null":
        pH = pC = P_MEAN
    elif ver == "A":
        pH, pC = P_HOT, P_COLD
    else:                       # ver B: populations swapped between chains
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
    # cold PARCEL exits: ver A on C-chain (C0), ver B on H-chain (H2). Read cold->bit0, hot->bit1.
    if ver == "A":
        qc.measure(C[0], 0); qc.measure(H[2], 1)   # cold=C0, hot=H2
    else:
        qc.measure(H[2], 0); qc.measure(C[0], 1)   # cold=H2, hot=C0
    return qc

ARMS = ["counterflow", "coflow", "null"]

def build_cal(state, ver):
    # calibrate the two physical exit qubits (C0=3, H2=2) in the SAME bit wiring as this version
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

def run_on_sim(sim, backend):
    """Transpile every circuit with the SAME opt_level/layout a fly uses, run on sim, decode A/B average."""
    order = [(a, v) for a in ARMS for v in ("A", "B")]
    circ = [build(a, v) for (a, v) in order] + [build_cal(0, "A"), build_cal(1, "A"), build_cal(0, "B"), build_cal(1, "B")]
    isa = [transpile(c, backend, optimization_level=3, initial_layout=QUIET_LAYOUT) for c in circ]
    cts = [sim.run(c, shots=SHOTS).result().get_counts() for c in isa]
    calA0, calA1, calB0, calB1 = cts[-4], cts[-3], cts[-2], cts[-1]
    res, single = {}, {}
    for a in ARMS:
        iA = order.index((a, "A")); iB = order.index((a, "B"))
        cA, hA = _decode(cts[iA], calA0, calA1)
        cB, hB = _decode(cts[iB], calB0, calB1)
        cold = (cA + cB) / 2; hot = (hA + hB) / 2
        res[a] = {"cold_exit": round(cold, 4), "hot_exit": round(hot, 4), "crossing": round(cold - hot, 4),
                  "eps": round((cold - P_COLD) / (P_HOT - P_COLD), 4),
                  "verA_crossing": round(cA - hA, 4), "verB_crossing": round(cB - hB, 4)}
        single[a] = {"A_only_crossing": round(cA - hA, 4)}
    checks, verdict = grade(res)
    return res, single, checks, verdict, isa, order

def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
    import ibm_multi_account as m
    svc = m.service_for_submission("IBMQ_TOKEN")
    backend = svc.backend(BACKEND_NAME)
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, ReadoutError, amplitude_damping_error

    # where do the exits physically land in A vs B? (precondition: same phys qubits, swapped bits)
    for v in ("A", "B"):
        isa = transpile(build("null", v), backend, optimization_level=3, initial_layout=QUIET_LAYOUT)
        fin = {}
        for instr in isa.data:
            if instr.operation.name == "measure":
                cb = isa.find_bit(instr.clbits[0]).index
                if cb in (0, 1): fin[cb] = isa.find_bit(instr.qubits[0]).index
        print(f"ver {v}: bit0<-phys q{fin.get(0)} (cold)  bit1<-phys q{fin.get(1)} (hot)")

    out = {"card": "counterflow_flight_a_popswap_VALIDATE", "cycle": "C5082", "board": 195, "tests": {}}

    # PHYS confound: amp-damp + readout localized on a PHYSICAL exit qubit (transpiled circuit)
    for physq in (142, 144):
        nm = NoiseModel()
        nm.add_quantum_error(amplitude_damping_error(0.10), ['id', 'ry', 'rz', 'sx', 'x'], [physq])
        nm.add_readout_error(ReadoutError([[0.90, 0.10], [0.05, 0.95]]), [physq])
        sim = AerSimulator(noise_model=nm)
        res, single, checks, verdict, _, _ = run_on_sim(sim, backend)
        out["tests"][f"PHYS_confound_q{physq}"] = {"verdict": verdict, "arms": res, "single_A_only": single, "checks": checks}
        print(f"\n=== PHYS confound on q{physq} (transpiled): {verdict} ===")
        for a, vv in res.items():
            print(f"  {a:12s} avg_cross={vv['crossing']:+.4f} eps={vv['eps']:.3f}  [A={vv['verA_crossing']:+.4f} B={vv['verB_crossing']:+.4f}]  (A-only={single[a]['A_only_crossing']:+.4f})")

    # from_backend: real noise + real routing
    simfb = AerSimulator.from_backend(backend)
    res, single, checks, verdict, _, _ = run_on_sim(simfb, backend)
    out["tests"]["from_backend"] = {"verdict": verdict, "arms": res, "single_A_only": single, "checks": checks}
    print(f"\n=== from_backend (real noise+routing): {verdict} ===")
    for a, vv in res.items():
        print(f"  {a:12s} avg_cross={vv['crossing']:+.4f} eps={vv['eps']:.3f}  [A={vv['verA_crossing']:+.4f} B={vv['verB_crossing']:+.4f}]  (A-only={single[a]['A_only_crossing']:+.4f})")

    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
              "results", "counterflow_flight_a_popswap_validate_c5082.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nsaved results/counterflow_flight_a_popswap_validate_c5082.json")

if __name__ == "__main__":
    main()
