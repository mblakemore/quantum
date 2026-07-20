#!/usr/bin/env python3
"""Exp244 — THE UNIVERSAL GATE SET, CLOSED: a programmable Clifford+T logical operation. C4924.

Horizons-6 P1 (the-living-ship doc). Every error-corrected COMPUTATION in the campaign was Clifford
(206/214 logical HLF — S-vertices are still Clifford; Gottesman-Knill simulable). Exp243 supplied the
missing non-Clifford ingredient (an injected T) but as a single bare gate. This flight COMPOSES the two:
the injected T is STEERED by a surrounding logical-Clifford PROGRAM to distinct non-stabilizer targets,
error-detected — the universal gate set (Clifford + T) closed behind the [[4,2,2]] shield, and shown to
be PROGRAMMABLE.

HONEST FRAMING (advisor C4924): a single T on a few qubits is trivially classically simulable by brute
force; non-simulability is asymptotic. So the claim is the MECHANISM — "the universal gate set is closed:
a programmable Clifford+T logical operation, error-detected" — NOT "we ran something intractable." This
is the universal-gate-set demonstration, not a supremacy stunt.

CONSTRUCTION (243's injection + a cheap Clifford program; two [[4,2,2]] blocks, X-bar readout robust):
  data A = C_in|+bar>  (C_in = I -> |+bar> ; Z-bar -> |-bar>, cheap Pauli program on the input)
  ancilla B = G|+bar>  (G = T via Rzz(pi/4) [magic] ; or S via Rzz(pi/2) [Clifford falsifier])
  transversal CNOT A->B ; measure B in Z-bar ; read A in X-bar ; postselect XXXX_A & ZZZZ_B.
  Result: A = (injected G) . C_in|+bar>, read <X-bar>. The injected T's non-stabilizer output is
  STEERED by the Clifford program C_in to a chosen sign.
WHY X-BAR STAYS ROBUST: the injection byproduct is an S-bar (Y-bar plane); a Z-TYPE program (Paulis)
  keeps <X-bar> byproduct-insensitive (both m-branches equal), so no frame/feed-forward is needed. An
  S-bar wrapper would rotate the magic into the byproduct-sensitive Y-bar plane (needs 213's frame) —
  named as the richer next step, not flown here.

FROZEN GATES (checked in selftest, statevector-exact; postselect XXXX_A & ZZZZ_B):
  G1_UNIVERSAL_PROGRAMMABLE: both T-outputs are non-stabilizer AND programmed to distinct targets —
     |<X-bar>(T,I)| and |<X-bar>(T,Zbar)| both in [0.55,0.85], and <X-bar>(T,I) - <X-bar>(T,Zbar) >= 1.1
     (the Clifford program steers the injected T from +0.707 to -0.707).
  G2_T_NECESSARY: replacing T with a Clifford (S) collapses BOTH outputs onto stabilizer points
     (|<X-bar>(S,*)| <= 0.2), AND without the gadget CNOT nothing reaches the data (no-cnot >= 0.9).
     Only the non-Clifford T reaches the programmed non-stabilizer targets.
  Registered verdict = G1 and G2. REPORTED: the 2x2 (gate x program) table + no-cnot control + accept.
SCOPE: error-DETECTED (distance-2, postselect), single injected T + a Z-type Clifford program, X-bar-
  robust (no frame). The full programmable ROTATION (S-bar wrappers -> 4 equator targets, needs 213's
  Y-bar frame + feed-forward) and error-CORRECTED universality (distance-3) are the depth/next steps,
  named not flown. Composes 243 (injection) + 214 (cheap in-block Cliffords) + [[4,2,2]] shield.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
GATES = {"T": PI / 4, "S": PI / 2}          # injected ancilla gate: T = magic, S = Clifford falsifier
PROGRAMS = ("I", "Zbar")                     # cheap Clifford program on the data input


def _prep_plus_bar(qc, base):
    qc.h(base); qc.cx(base, base + 1); qc.h(base + 2); qc.cx(base + 2, base + 3)   # |+bar> on L1


def circuit(gate, program, gadget=True):
    qc = QuantumCircuit(8, 8)
    _prep_plus_bar(qc, 0)                     # data A = |+bar>
    if program == "Zbar":                     # cheap Pauli program: Z-bar1 = Z0 Z2 -> |-bar>
        qc.z(0); qc.z(2)
    _prep_plus_bar(qc, 4)                     # ancilla B = |+bar> ...
    qc.rzz(GATES[gate], 4, 6)                 # ... then G = Rz_bar(theta): T (magic) or S (Clifford)
    qc.barrier()
    if gadget:
        for i in range(4): qc.cx(i, i + 4)    # transversal logical CNOT A->B (the injection)
    qc.barrier()
    for q in range(4): qc.h(q)                # A read in X (X-bar_A = x0^x1; XXXX_A postselect)
    for q in range(8): qc.measure(q, q)       # B read in Z (Z-bar_B = z4^z6 = m; ZZZZ_B postselect)
    return qc


def _analyze(counts):
    acc = 0; c = 0; tot = 0; cm = {0: 0.0, 1: 0.0}; nm = {0: 0, 1: 0}
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(8)]; tot += n
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) or (v[4] ^ v[5] ^ v[6] ^ v[7]): continue
        acc += n; xbar = 1 - 2 * (v[0] ^ v[1]); c += xbar * n
        m = v[4] ^ v[6]; cm[m] += xbar * n; nm[m] += n
    return {"xbar": (c / acc if acc else 0.0), "acceptance": acc / tot,
            "xbar_m0": (cm[0] / nm[0] if nm[0] else 0.0), "xbar_m1": (cm[1] / nm[1] if nm[1] else 0.0)}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000
    print("Exp244 selftest | THE UNIVERSAL GATE SET — programmable Clifford+T logical operation")
    tab = {}
    for g in GATES:
        for p in PROGRAMS:
            tab[(g, p)] = _analyze(sim.run(circuit(g, p), shots=shots).result().get_counts())
            r = tab[(g, p)]
            print(f"    inject {g} on program {p:>4}: <X-bar_A>={r['xbar']:+.3f} | m0 {r['xbar_m0']:+.3f} "
                  f"m1 {r['xbar_m1']:+.3f} | acc {r['acceptance']:.2f}")
            assert abs(r["xbar_m0"] - r["xbar_m1"]) < 0.05, "Z-type program must keep X-bar byproduct-robust"
    nocx = _analyze(sim.run(circuit("T", "I", gadget=False), shots=shots).result().get_counts())
    print(f"    NO-CNOT control (T,I): <X-bar_A>={nocx['xbar']:+.3f} (~+1, no injection)")
    tI, tZ = tab[("T", "I")]["xbar"], tab[("T", "Zbar")]["xbar"]
    sI, sZ = tab[("S", "I")]["xbar"], tab[("S", "Zbar")]["xbar"]
    assert 0.55 <= tI <= 0.85 and -0.85 <= tZ <= -0.55, "T must give non-stabilizer +-0.707 steered by program"
    assert abs(sI) <= 0.15 and abs(sZ) <= 0.15, "Clifford S injection must collapse to a stabilizer point"
    assert nocx["xbar"] >= 0.9, "no injection without the gadget"
    print("SELFTEST PASS: the injected T lands at a non-stabilizer +-0.707 STEERED by the Clifford program "
          "(I->+0.707, Z-bar->-0.707); replacing T with the Clifford S collapses both to 0; nothing reaches "
          "the data without the gadget. The universal gate set is closed and programmable. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [("g", g, p) for g in GATES for p in PROGRAMS] + [("nocx", "T", "I")]
    def build(o):
        return circuit(o[1], o[2], gadget=(o[0] == "g"))
    circuits = [transpile(build(o), backend=backend, optimization_level=3, seed_transpiler=0) for o in order]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)} (243-class: two blocks + transversal CNOT)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp244_universal_gate_manifest.json")
    man = {"exp": 244, "slug": "universal_gate", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "prereg": {"G1_universal_programmable": "|<X-bar>(T,I)|,|<X-bar>(T,Zbar)| in [0.55,0.85] and "
                                                   "<X-bar>(T,I)-<X-bar>(T,Zbar) >= 1.1 (T steered to distinct non-stab targets)",
                      "G2_T_necessary": "|<X-bar>(S,*)| <= 0.2 (Clifford collapses to stabilizer) AND no-cnot >= 0.9",
                      "registered_verdict": "G1 and G2 — universal gate set closed + programmable, error-detected (NOT supremacy)",
                      "scope": "single injected T + Z-type Clifford program, X-bar-robust; full rotation (Y-bar frame) "
                               "+ error-corrected universality (distance-3) named not flown"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp244_universal_gate_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    def counts(idx):
        r0 = res[idx]; reg = list(r0.data.keys())[0]; return getattr(r0.data, reg).get_counts()
    rows = {}
    for idx, o in enumerate(man["order"]):
        rows[tuple(o)] = _analyze(counts(idx))
    print(f"Exp244 THE UNIVERSAL GATE SET decode | job {man['job_id']}")
    print("  inject / program     <X-bar_A>   m0 / m1        acceptance")
    for o in man["order"]:
        r = rows[tuple(o)]
        tag = f"{o[1]} on {o[2]}" if o[0] == "g" else "NO-CNOT (T,I)"
        print(f"  {tag:>16}   {r['xbar']:+.3f}    {r['xbar_m0']:+.3f}/{r['xbar_m1']:+.3f}   {r['acceptance']:.3f}")
    tI = rows[("g", "T", "I")]["xbar"]; tZ = rows[("g", "T", "Zbar")]["xbar"]
    sI = rows[("g", "S", "I")]["xbar"]; sZ = rows[("g", "S", "Zbar")]["xbar"]
    nocx = rows[("nocx", "T", "I")]["xbar"]
    steer = tI - tZ
    g1 = (0.55 <= abs(tI) <= 0.85) and (0.55 <= abs(tZ) <= 0.85) and (steer >= 1.1)
    g2 = abs(sI) <= 0.2 and abs(sZ) <= 0.2 and nocx >= 0.9
    print(f"\n  T targets: (I) {tI:+.3f}  (Z-bar) {tZ:+.3f}  -> steer {steer:+.3f} | Clifford S: {sI:+.3f}/{sZ:+.3f} | no-cnot {nocx:+.3f}")
    print(f"G1 UNIVERSAL+PROGRAMMABLE: T non-stab & steered by {steer:+.3f} >= 1.1 {'OK' if g1 else 'MISS'}")
    print(f"G2 T-NECESSARY: Clifford collapses to stab (|{sI:+.2f}|,|{sZ:+.2f}|<=0.2) & no-cnot {nocx:+.2f}>=0.9 {'OK' if g2 else 'MISS'}")
    ok = g1 and g2
    win = ("THE UNIVERSAL GATE SET, CLOSED — a programmable Clifford+T logical operation, error-detected: "
           "the injected non-Clifford T is STEERED by the surrounding logical-Clifford program to distinct "
           "non-stabilizer targets (+0.707 <-> -0.707) that NO stabilizer circuit can reach, and that "
           "collapse to stabilizer points the instant T is replaced by a Clifford. Clifford + T, composed "
           "and protected — the mechanism of universal quantum computation, on silicon behind the shield")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "T_I": tI, "T_Zbar": tZ, "S_I": sI, "S_Zbar": sZ,
               "no_cnot": nocx, "steer": steer, "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp244_universal_gate_decode.json"), "w"), indent=1)
    print("-> results/exp244_universal_gate_decode.json")


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
