#!/usr/bin/env python3
"""Exp233 — THE HARD-REGIME CROSSOVER: does FT beat bare when the logical gate is EXPENSIVE? C4914.

Exp231 found the crossover (error-corrected beats bare, D~2, grows), but honestly flagged that its
advantage leaned on the [[4,2,2]] code making in-block CZ FREE (0 physical 2q). The real fault-
tolerance test is the HARD regime: use an EXPENSIVE logical gate and ask whether error detection
still wins against the encoding overhead. Here the entangling logical gate is in-block CNOT-bar =
SWAP(0,2) = 3 physical 2q gates (vs bare CNOT = 1). The logical arm now carries 3x the two-qubit
error per layer PLUS the encoding prep — the shield must overcome all of it by detection alone.

Same mirror-circuit method as 231 (exact identity at every depth, verified): layer = in-block
CNOT-bar(L1->L2) . Xbar1 ; forward D then inverse D ; barriers force execution. Measure Z, logical
postselects ZZZZ and decodes return-to-(0,0). If logical still overtakes bare, FT wins even in the
overhead-dominated regime — a strictly stronger result. If not, it honestly bounds the crossover to
the cheap-Clifford regime (which 231 established).

FROZEN GATES:
  G1_TREND: Delta(D) = F_logical - F_bare non-decreasing in D within error (FT trend).
  G2_HARD_CROSSOVER: Delta(D*) > 0 at some D* at >= 3 sigma -> FT beats bare EVEN with expensive
     logical gates (the strong FT result). Else: report NOT-REACHED with the trend (honest bound —
     the shield's detection did not overcome the 3x two-qubit overhead at these depths).
  Registered verdict = G1; G2 reported FOUND or NOT-REACHED honestly.
SCOPE: 2 logical qubits vs 2 physical qubits; expensive logical gate (SWAP-based in-block CNOT, 3
  physical 2q/layer) so the logical arm is overhead-dominated (2q ~ 6D vs bare 2D). This is the
  honest stress-test of the 231 crossover. Depth-check before submit; barriers prevent the mirror
  from compiling to identity (the 231 trap, already caught).
BUDGET CHECK (C4887): logical 2q ~ 6D, bare 2q ~ 2D. Predictions at freeze.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
DEPTHS = (1, 2, 4, 6, 8)


def bare_circuit(D):
    qc = QuantumCircuit(2, 2)
    for _ in range(D):
        qc.cx(0, 1); qc.x(0); qc.barrier()
    for _ in range(D):
        qc.x(0); qc.cx(0, 1); qc.barrier()
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


def _prep_00(qc): qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)


def _swap02(qc):
    # SWAP(0,2) as 3 explicit CX with barriers so the transpiler cannot virtualize it (real 2q cost)
    qc.cx(0, 2); qc.barrier(); qc.cx(2, 0); qc.barrier(); qc.cx(0, 2)


def _layer(qc, inv=False):
    if not inv:
        _swap02(qc)                   # in-block CNOT-bar(L1->L2), forced to 3 real physical 2q
        qc.x(0); qc.x(1)              # Xbar1 = X0X1
    else:
        qc.x(0); qc.x(1)
        _swap02(qc)


def logical_circuit(D):
    qc = QuantumCircuit(4, 4)
    _prep_00(qc); qc.barrier()
    for _ in range(D): _layer(qc, False); qc.barrier()
    for _ in range(D): _layer(qc, True); qc.barrier()
    for q in range(4): qc.measure(q, q)
    return qc


DEC = ((0, 2), (0, 1))


def _logical_fidelity(counts):
    acc = ok = tot = 0; (dA, dB) = DEC
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(4)]; tot += n
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) != 0: continue
        acc += n
        if (v[dA[0]] ^ v[dA[1]]) == 0 and (v[dB[0]] ^ v[dB[1]]) == 0: ok += n
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
    print("Exp233 selftest | THE HARD-REGIME CROSSOVER — expensive logical gate (SWAP-based CNOT)")
    for D in DEPTHS:
        fl, _, _ = _logical_fidelity(sim.run(logical_circuit(D), shots=20000).result().get_counts())
        fb, _ = _bare_fidelity(sim.run(bare_circuit(D), shots=20000).result().get_counts())
        assert fl > 0.98 and fb > 0.98, f"mirror must be identity at D={D}"
    print("  noiseless: both return to |00> at all depths (exact identities).")
    print("SELFTEST PASS: hard-regime mirror circuits are exact. On hardware, does the shield's "
          "detection overcome the 3x two-qubit overhead? Cleared to fly.")


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
    out = os.path.join(HERE, "..", "results", "exp233_hard_crossover_manifest.json")
    man = {"exp": 233, "slug": "ft_hard_regime", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "depths": list(DEPTHS), "order": [list(o) for o in order],
           "prereg": {"G1_trend": "Delta(D) non-decreasing in D",
                      "G2_hard_crossover": "Delta(D*)>0 at >=3 sigma -> FT beats bare with EXPENSIVE gates; else NOT-REACHED (honest bound)",
                      "registered_verdict": "G1; G2 reported FOUND or NOT-REACHED",
                      "scope": "hard-regime FT crossover; expensive logical gate (SWAP CNOT, 3 physical 2q/layer)"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp233_hard_crossover_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    depths = man["depths"]; raw = {}
    for idx, (k, D) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(k, D)] = getattr(r0.data, reg).get_counts()
    print(f"Exp233 THE HARD-REGIME CROSSOVER decode | job {man['job_id']}")
    print("  D | F_logical (accept) | F_bare | Delta")
    Fl = {}; Fb = {}; Del = {}; se = {}
    for D in depths:
        fl, acc, tot = _logical_fidelity(raw[("log", D)]); fb, tb = _bare_fidelity(raw[("bare", D)])
        Fl[D] = fl; Fb[D] = fb; Del[D] = fl - fb
        se[D] = float(np.sqrt(fl * (1 - fl) / max(1, acc) + fb * (1 - fb) / max(1, tb)))
        print(f"  {D:2d} | {fl:.3f} ({acc/tot:.2f})      | {fb:.3f} | {Del[D]:+.3f} ± {se[D]:.3f}")
    crossed = [D for D in depths if Del[D] > 0 and Del[D] / se[D] >= 3]
    trend_ok = all(Del[depths[i + 1]] >= Del[depths[i]] - 2 * se[depths[i]] for i in range(len(depths) - 1))
    print(f"\nG1 TREND: {'OK' if trend_ok else 'MIXED'}")
    if crossed:
        Dc = crossed[0]
        print(f"G2 HARD CROSSOVER: *** FOUND *** at D={Dc}: F_log={Fl[Dc]:.3f} > F_bare={Fb[Dc]:.3f} "
              f"(+{Del[Dc]:.3f} at {Del[Dc]/se[Dc]:.0f} sigma). FT beats bare EVEN with expensive logical gates.")
        verdict = "HARD-REGIME CROSSOVER FOUND — error detection overcomes 3x two-qubit overhead; FT wins in the hard regime"
    else:
        best = max(depths, key=lambda D: Del[D])
        print(f"G2 HARD CROSSOVER: NOT reached; best Delta={Del[best]:+.3f} at D={best}. Trend {[round(Del[D],3) for D in depths]}.")
        verdict = ("HARD-REGIME CROSSOVER NOT REACHED (honest) — with expensive (SWAP-based) logical gates the "
                   "encoding overhead was not overcome at these depths; the 231 crossover is bounded to the cheap-Clifford regime")
    print(f"VERDICT: {verdict}")
    json.dump({"job_id": man["job_id"], "F_logical": Fl, "F_bare": Fb, "Delta": Del,
               "crossover_depth": (crossed[0] if crossed else None)},
              open(os.path.join(HERE, "..", "results", "exp233_hard_crossover_decode.json"), "w"), indent=1)
    print("-> results/exp233_hard_crossover_decode.json")


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
