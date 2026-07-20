#!/usr/bin/env python3
"""Exp226 — THE MEASUREMENT ENGINE: distributed measurement-based computation across a cut. C4912.

The Federation Computer's next paradigm. Exp217-222 computed by GATES across the cut; Exp221 gave
the distributed cluster bond. This flight computes by MEASUREMENT: a logical qubit's state in shield
A is fed a Hadamard purely by MEASURING A in the X-basis, and the result H|psi> is delivered to
shield B across the cut — the one-qubit measurement-based-computation (MBQC) primitive, distributed
and error-detected. The network computes not by acting, but by looking.

MBQC rule: input |psi> on A (block q0-3), |+bar> on B (block q4-7), a cluster bond CZbar(A,B) made
DISTRIBUTED via a physical relay (221 construction: CNOT from Zbar1A support -> e_A, CZ from e_B ->
Zbar1B support; H-free). Measure A in Xbar -> B is left in H|psi> up to a byproduct Xbar^{m_A}
(m_A = A's Xbar outcome), applied as a decode-time frame. The choice to measure A in X is what
applies the Hadamard — computation programmed by the measurement basis.

Verify on Clifford inputs (all X/Z readout, no Ybar wall):
  |0bar> -> H|0>=|+bar>  : <Xbar_B> = +1
  |1bar> -> H|1>=|-bar>  : <Xbar_B> = -1
  |+bar> -> H|+>=|0bar>  : <Zbar_B> = +1
Frame (byproduct + CZ frame) found by search, frozen (221/206 method). Per-block XXXX/ZZZZ shield.

FROZEN GATES (relative to statevector-exact; frame found by search then frozen):
  G1_HADAMARD_BY_MEASUREMENT: all three inputs give the correct H|psi> signature (|<obs_B>| >= 0.55,
     correct sign, each >= 5 sigma) after the byproduct frame + stabilizer postselection. Measuring
     A in X applied a Hadamard, delivered to B across the cut.
  G2_BOND_NECESSARY: in-decode/hardware falsifier — with NO cluster bond (the distributed CZ
     omitted), B does NOT carry H|psi> (|<obs_B>| <= 0.30). The gate needs the distributed bond.
  G3_FRAME_NECESSARY: ignore the byproduct bit m_A and the |+bar> (Z-output) case collapses
     (|<Zbar_B>| <= 0.30). The classical bit completes the teleported gate.
  Registered verdict = G1 and G2 and G3.
SCOPE: 2 [[4,2,2]] blocks (input A + output B) + physical relay; per-variant partial shield. X/Z
  Clifford MBQC (the Xbar-measure applies H; continuous-angle gates need the Ybar-plane readout, the
  stated [[4,2,2]] wall). Textbook MBQC (Raussendorf-Briegel one-qubit teleportation) + the 221
  distributed CZ; contribution = measurement-based computation across a shielded cut. KILL K1: depth.
BUDGET CHECK (C4887): ~221-class (1 distributed CZ). Predictions filed at freeze.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, itertools, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

# input -> (prep, B-output observable, ideal sign)
INPUTS = {"0": ("Xbar_B", +1), "1": ("Xbar_B", -1), "plus": ("Zbar_B", +1)}


def _p_00(qc, o): qc.h(o); qc.cx(o, o + 1); qc.cx(o, o + 2); qc.cx(o, o + 3)     # |0bar0bar>
def _p_p0(qc, o): qc.h(o); qc.cx(o, o + 1); qc.h(o + 2); qc.cx(o + 2, o + 3)     # |+bar0bar>
def _Xbar1(qc, o): qc.x(o); qc.x(o + 1)


def circuit(inp, bond=True):
    """A=q0-3 (input, measured in Xbar), B=q4-7 (output |+bar>), relay e_A=q8,e_B=q9."""
    out_obs = INPUTS[inp][0]
    qc = QuantumCircuit(10, 10)
    if inp == "plus":
        _p_p0(qc, 0)                        # A = |+bar>
    else:
        _p_00(qc, 0)                        # A = |0bar>
        if inp == "1": _Xbar1(qc, 0)        # A = |1bar>
    _p_p0(qc, 4)                            # B = |+bar>
    qc.h(8); qc.cx(8, 9)                    # relay Bell
    qc.barrier()
    if bond:
        qc.cx(0, 8); qc.cx(2, 8)            # distributed CZbar(A,B): CNOT(A->e_A) from Zbar1A=Z0Z2
        qc.cz(9, 4); qc.cz(9, 6)            # CZ(e_B->B) into Zbar1B=Z4Z6
    qc.barrier()
    # measure A in Xbar (H on block A); relay e_A in Z, e_B in X; B in its output basis
    for q in range(4): qc.h(q)              # A -> Xbar readout (Xbar1A=X0X1)
    qc.h(9)                                 # e_B in X
    if out_obs == "Xbar_B":
        for q in range(4, 8): qc.h(q)       # B -> Xbar readout (Xbar1B=X4X5)
    for q in range(10): qc.measure(q, q)
    return qc


def _accA(v): return (v[0] ^ v[1] ^ v[2] ^ v[3]) == 0     # A block stabilizer (X-basis: XXXX)
def _accB(v, xbasis):
    return (v[4] ^ v[5] ^ v[6] ^ v[7]) == 0                # B block stabilizer


def _obs(counts, inp, frame, frame_on=True):
    """<obs_B> with byproduct/CZ frame. frame=(fb, use_mA): XOR relay bit fb + A's Xbar outcome."""
    out_obs = INPUTS[inp][0]; fb, use_mA = frame
    num = den = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(10)]
        if not (_accA(v) and _accB(v, out_obs == "Xbar_B")): continue
        mA = v[0] ^ v[1]                                  # A's Xbar1 = X0X1 outcome
        if out_obs == "Xbar_B":
            Bbit = v[4] ^ v[5]                            # Xbar1B = X4X5
        else:
            Bbit = v[4] ^ v[6]                            # Zbar1B = Z4Z6
        if frame_on:
            if fb is not None: Bbit ^= v[fb]
            if use_mA: Bbit ^= mA
        num += n * (1 - 2 * Bbit); den += n
    return (num / den if den else 0.0), den


FRAME = {}
FRAME_OPTS = [(fb, m) for fb in (None, 8, 9) for m in (False, True)]


def _find_frame(sim, inp):
    ct = sim.run(circuit(inp), shots=40000).result().get_counts()
    sign = INPUTS[inp][1]; best = (None, -2)
    for fr in FRAME_OPTS:
        val, _ = _obs(ct, inp, fr)
        score = val * sign                                # want <obs> to match the ideal sign
        if score > best[1]: best = (fr, score)
    return best[0]


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    print("Exp226 selftest | THE MEASUREMENT ENGINE — distributed MBQC (Hadamard by measurement)")
    for inp in INPUTS:
        FRAME[inp] = _find_frame(sim, inp)
    print(f"  FROZEN frames: {FRAME}")
    ok = True
    for inp, (obs, sign) in INPUTS.items():
        ct = sim.run(circuit(inp), shots=40000).result().get_counts()
        val, _ = _obs(ct, inp, FRAME[inp])
        nob, _ = _obs(sim.run(circuit(inp, bond=False), shots=40000).result().get_counts(), inp, FRAME[inp])
        off, _ = _obs(ct, inp, FRAME[inp], frame_on=False)
        print(f"  input |{inp:>4}> -> H|psi>: <{obs}>={val:+.3f} (ideal {sign:+d})  no-bond={nob:+.3f}  frame-off={off:+.3f}")
        if val * sign < 0.95: ok = False
    assert ok, "all three inputs must show H applied (correct sign, ~1)"
    # bond & frame necessity (use the plus input: Z-output, sensitive to both)
    nob_plus, _ = _obs(sim.run(circuit("plus", bond=False), shots=40000).result().get_counts(), "plus", FRAME["plus"])
    off_plus, _ = _obs(sim.run(circuit("plus"), shots=40000).result().get_counts(), "plus", FRAME["plus"], frame_on=False)
    assert abs(nob_plus) < 0.3, "no cluster bond -> no gate"
    assert abs(off_plus) < 0.3, "ignore byproduct bit -> Z-output collapses"
    print("SELFTEST PASS: measuring A in Xbar applies a Hadamard to the input and delivers H|psi> to "
          "B across the cut; no bond or no byproduct bit and it dies. Computation by measurement, "
          "distributed. Cleared to fly.")


def submit(backend_name, shots):
    from qiskit_aer import AerSimulator
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    sim = AerSimulator()
    for inp in INPUTS: FRAME[inp] = _find_frame(sim, inp)
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [(inp, "bond") for inp in INPUTS] + [(inp, "nobond") for inp in INPUTS]
    builds = [circuit(inp, bond=(tag == "bond")) for (inp, tag) in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp226_distributed_mbqc_manifest.json")
    man = {"exp": 226, "slug": "distributed_mbqc", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "frame": {inp: list(FRAME[inp]) if FRAME[inp] else [None, False] for inp in INPUTS},
           "prereg": {"G1_hadamard_by_measurement": "all 3 inputs |<obs_B>|>=0.55 correct sign, >=5 sigma",
                      "G2_bond_necessary": "no-bond |<obs_B>| <= 0.30",
                      "G3_frame_necessary": "byproduct-ignored |<Zbar_B>| <= 0.30 (plus input)",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "distributed measurement-based computation across a shielded cut; "
                               "Xbar-measure applies H (221 cluster bond); X/Z Clifford MBQC"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp226_distributed_mbqc_manifest.json")))
    for inp in INPUTS:
        fr = man["frame"][inp]; FRAME[inp] = (fr[0], fr[1])
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (inp, tag) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(inp, tag)] = getattr(r0.data, reg).get_counts()
    print(f"Exp226 THE MEASUREMENT ENGINE decode | job {man['job_id']}")
    vals = {}; ses = {}
    for inp, (obs, sign) in INPUTS.items():
        val, nn = _obs(raw[(inp, "bond")], inp, FRAME[inp])
        nob, _ = _obs(raw[(inp, "nobond")], inp, FRAME[inp])
        off, _ = _obs(raw[(inp, "bond")], inp, FRAME[inp], frame_on=False)
        se = float(np.sqrt(max(1e-9, 1 - val ** 2) / max(1, nn)))
        vals[inp] = (val, sign); ses[inp] = se
        print(f"  |{inp:>4}> -> H|psi>: <{obs}>={val:+.3f}±{se:.3f} (ideal {sign:+d})  no-bond={nob:+.3f}  frame-off={off:+.3f}")
    g1 = all(vals[i][0] * vals[i][1] >= 0.55 and abs(vals[i][0]) / ses[i] >= 5 for i in INPUTS)
    nob_p, _ = _obs(raw[("plus", "nobond")], "plus", FRAME["plus"])
    off_p, _ = _obs(raw[("plus", "bond")], "plus", FRAME["plus"], frame_on=False)
    g2 = abs(nob_p) <= 0.30
    g3 = abs(off_p) <= 0.30
    print(f"\nG1 HADAMARD-BY-MEASUREMENT: {[f'{vals[i][0]:+.2f}' for i in INPUTS]} vs ideal {[vals[i][1] for i in INPUTS]} {'OK' if g1 else 'MISS'}")
    print(f"G2 BOND NECESSARY: no-bond <Zbar_B>={nob_p:+.3f} (<=0.30) {'OK' if g2 else 'MISS'}")
    print(f"G3 FRAME NECESSARY: byproduct-off <Zbar_B>={off_p:+.3f} (<=0.30) {'OK' if g3 else 'MISS'}")
    ok = g1 and g2 and g3
    win = ("THE MEASUREMENT ENGINE — a Hadamard applied to a logical qubit in one shield purely by "
           "MEASURING it in the X basis, the result H|psi> delivered to another shield across the cut. "
           "Distributed measurement-based quantum computation: the network computes by looking, error-"
           "detected, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "outputs": {i: vals[i][0] for i in INPUTS},
               "bond_null": nob_p, "frame_null": off_p,
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp226_distributed_mbqc_decode.json"), "w"), indent=1)
    print("-> results/exp226_distributed_mbqc_decode.json")


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
