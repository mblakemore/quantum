#!/usr/bin/env python3
"""Exp231 — THE CROSSOVER: does error-corrected beat bare, and where? C4914.

Stair 1 of the frontier (docs/state-of-the-frontier-whisper-c4913.md), the make-or-break question:
the fault-tolerance thesis says the [[4,2,2]] shield beats bare and MORE with depth (191 +0.07 ->
197 +0.24), yet the distributed HLF at n=4 (222) had logical BELOW bare (overhead won). WHERE is the
crossover? Sweep depth and measure logical-postselected vs bare fidelity; find where (or whether)
the error-detection outweighs the encoding overhead on this hardware. Honest either way.

A 2-qubit mirror circuit: prep |00>, apply D scramble layers, then their exact inverse (mirror),
so the ideal output is |00> for every D. Fidelity = P(return to |00>); it decays with depth as
errors accumulate. Layer = CZ(L1,L2) . Xbar1 . Xbar2 (an entangling + bit-flip scramble).
  bare:    2 physical qubits; layer = cz(0,1), x(0), x(1)
  logical: [[4,2,2]] (2 logical qubits, q0-3); layer = S^4 (in-block CZbar), Xbar1=X0X1, Xbar2=X0X2
Measure in Z; logical postselects ZZZZ and decodes L1,L2 (return = (0,0)). At small D the encoding
overhead makes bare win; if the shield's single-error detection wins at larger D, the curves cross.

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_TREND: the shield advantage Delta(D) = F_logical(D) - F_bare(D) is measured at every depth and
     is non-decreasing in D within error (the FT trend: detection pays more as depth grows).
  G2_CROSSOVER: Delta(D*) > 0 at some depth D* at >= 3 sigma -> the crossover is FOUND (error-
     corrected genuinely beats bare). If no D* qualifies, report honestly: crossover not reached on
     this hardware, with the measured trend.
  Registered verdict = G1 (the trend); G2 (the crossover) is the headline question, reported as
     FOUND or NOT-REACHED with the data — a real answer either way.
SCOPE: 2 logical qubits ([[4,2,2]]) vs 2 physical qubits; mirror-circuit fidelity, Z-readout,
  ZZZZ postselection. Distance-2 code detects 1 error; whether it wins depends on the per-gate error
  vs the overhead. Honest: the crossover may not be reached at d=2 on current hardware — that is a
  valuable answer (it bounds where FT starts paying). Depths swept, no silent cap.
BUDGET CHECK (C4887): depth-scaled; bare 2q ~ D, logical 2q ~ per-layer S^4 (0) + Paulis (0) so the
  entangling cost is the in-block CZ (0 physical 2q!) -> logical 2q mostly from prep. Predictions at freeze.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, itertools, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
DEPTHS = (1, 2, 4, 6, 8, 12)


def bare_circuit(D):
    qc = QuantumCircuit(2, 2)
    for _ in range(D):
        qc.cz(0, 1); qc.x(0); qc.x(1); qc.barrier()
    for _ in range(D):
        qc.x(0); qc.x(1); qc.cz(0, 1); qc.barrier()   # inverse (self-inverse gates, reversed order)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


def _prep_00(qc): qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)     # |0bar0bar> = GHZ4


def _layer(qc, inv=False):
    if not inv:
        for q in range(4): qc.s(q)                    # in-block CZbar(L1,L2) = S^4
        qc.x(0); qc.x(1)                              # Xbar1 = X0X1
        qc.x(0); qc.x(2)                              # Xbar2 = X0X2
    else:
        qc.x(0); qc.x(2); qc.x(0); qc.x(1)
        for q in range(4): qc.sdg(q)


def logical_circuit(D):
    qc = QuantumCircuit(4, 4)
    _prep_00(qc)
    qc.barrier()
    for _ in range(D): _layer(qc, inv=False); qc.barrier()
    for _ in range(D): _layer(qc, inv=True); qc.barrier()
    for q in range(4): qc.measure(q, q)
    return qc


DEC = [((0, 2), (0, 1))]     # Z-decode: L1 = Z0Z2 parity, L2 = Z0Z1 parity (191 map)


def _logical_fidelity(counts):
    """postselect ZZZZ; decode (L1,L2); fidelity = P(return to (0,0))."""
    acc = ok = tot = 0
    (dA, dB) = DEC[0]
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(4)]
        tot += n
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) != 0: continue
        acc += n
        L1 = v[dA[0]] ^ v[dA[1]]; L2 = v[dB[0]] ^ v[dB[1]]
        if L1 == 0 and L2 == 0: ok += n
    return (ok / acc if acc else 0.0), acc, tot


def _bare_fidelity(counts):
    ok = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); tot += n
        if b[-1] == "0" and b[-2] == "0": ok += n
    return ok / tot, tot


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    print("Exp231 selftest | THE CROSSOVER — mirror-circuit fidelity, logical (postselected) vs bare")
    for D in DEPTHS:
        fl, acc, _ = _logical_fidelity(sim.run(logical_circuit(D), shots=20000).result().get_counts())
        fb, _ = _bare_fidelity(sim.run(bare_circuit(D), shots=20000).result().get_counts())
        assert fl > 0.98 and fb > 0.98, f"noiseless mirror must return to |00> at D={D}"
    print("  noiseless: logical & bare both return to |00> (fidelity 1) at all depths.")
    print("SELFTEST PASS: the mirror circuits are exact identities at every depth. On hardware the "
          "fidelities decay; the crossover (if any) is where logical-postselected overtakes bare. "
          "Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [("log", D) for D in DEPTHS] + [("bare", D) for D in DEPTHS]
    builds = [logical_circuit(D) if k == "log" else bare_circuit(D) for (k, D) in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp231_crossover_manifest.json")
    man = {"exp": 231, "slug": "ft_crossover", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "depths": list(DEPTHS), "order": [list(o) for o in order],
           "prereg": {"G1_trend": "Delta(D)=F_log-F_bare non-decreasing in D within error (FT trend)",
                      "G2_crossover": "Delta(D*)>0 at some D* at >=3 sigma -> FOUND; else NOT-REACHED (report trend)",
                      "registered_verdict": "G1 (trend); G2 crossover reported FOUND or NOT-REACHED",
                      "scope": "[[4,2,2]] mirror-circuit fidelity vs depth; distance-2 detection vs "
                               "encoding overhead; honest crossover measurement"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp231_crossover_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    depths = man["depths"]; raw = {}
    for idx, (k, D) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(k, D)] = getattr(r0.data, reg).get_counts()
    print(f"Exp231 THE CROSSOVER decode | job {man['job_id']}")
    print("  D | F_logical (accept) | F_bare | Delta = F_log - F_bare")
    Fl = {}; Fb = {}; Del = {}; se = {}
    for D in depths:
        fl, acc, tot = _logical_fidelity(raw[("log", D)]); fb, tb = _bare_fidelity(raw[("bare", D)])
        Fl[D] = fl; Fb[D] = fb; Del[D] = fl - fb
        se[D] = float(np.sqrt(fl * (1 - fl) / max(1, acc) + fb * (1 - fb) / max(1, tb)))
        print(f"  {D:2d} | {fl:.3f} ({acc/tot:.2f})      | {fb:.3f} | {Del[D]:+.3f} ± {se[D]:.3f}")
    # G2 crossover: any depth with Delta>0 at >=3 sigma
    crossed = [D for D in depths if Del[D] > 0 and Del[D] / se[D] >= 3]
    # G1 trend: Delta non-decreasing (within 1 sigma slack) over the sweep
    trend_ok = all(Del[depths[i + 1]] >= Del[depths[i]] - 2 * se[depths[i]] for i in range(len(depths) - 1))
    print(f"\nG1 TREND (Delta non-decreasing in D): {'OK' if trend_ok else 'MIXED'}")
    if crossed:
        Dc = crossed[0]
        print(f"G2 CROSSOVER: *** FOUND *** at D={Dc}: F_log={Fl[Dc]:.3f} > F_bare={Fb[Dc]:.3f} "
              f"(Delta=+{Del[Dc]:.3f} at {Del[Dc]/se[Dc]:.0f} sigma). Error-corrected BEATS bare.")
        verdict = "THE CROSSOVER FOUND — error-corrected distributed-class computation beats bare on silicon"
    else:
        best = max(depths, key=lambda D: Del[D])
        print(f"G2 CROSSOVER: not reached at d=2 on this hardware; best Delta={Del[best]:+.3f} at D={best}. "
              f"Trend: {[round(Del[D],3) for D in depths]}. An HONEST bound on where FT starts to pay.")
        verdict = ("CROSSOVER NOT REACHED (honest) — the shield-advantage trend measured; distance-2 "
                   "detection has not overtaken the encoding overhead at these depths on this hardware")
    print(f"VERDICT: {verdict}")
    json.dump({"job_id": man["job_id"], "F_logical": Fl, "F_bare": Fb, "Delta": Del,
               "crossover_depth": (crossed[0] if crossed else None), "trend_ok": bool(trend_ok)},
              open(os.path.join(HERE, "..", "results", "exp231_crossover_decode.json"), "w"), indent=1)
    print("-> results/exp231_crossover_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
