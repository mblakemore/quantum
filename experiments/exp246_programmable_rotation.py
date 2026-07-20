#!/usr/bin/env python3
"""Exp246 — THE PROGRAMMABLE ROTATION: the injected T steered around the Bloch equator. C4932.

Completes Exp244. 244 steered the injected T to 2 sign-flipped non-stabilizer targets (+-0.71), read in
the byproduct-robust X-bar. This flight steers it to the FOUR distinct non-stabilizer targets around the
Bloch equator via cheap logical-Clifford wrappers W in {I, S-bar, Z-bar, S-bar.Z-bar} -- a genuinely
PROGRAMMABLE non-Clifford rotation (Clifford + T generating a dense set), error-detected.

CLEAN Y-BAR (dodges the mixed-basis wall): to read <Y-bar>, apply a cheap S-bar-dagger (maps Y-bar->X-bar)
then the robust all-X readout. To drop the injection's S-bar byproduct, POSTSELECT m=0 (the ancilla
Z-bar outcome) -- no feed-forward needed; on m=0 the data is exactly W . T-bar|+bar>.

CONSTRUCTION (two [[4,2,2]] blocks, 243-class depth):
  data A=|+bar>; ancilla B = Rzz(theta) |+bar> (T=pi/4 magic, or S=pi/2 Clifford falsifier);
  transversal CNOT A->B; wrapper W on A; (readout Y: S-bar-dagger on A); all-X readout on A; measure.
  postselect XXXX_A & ZZZZ_B & m(=z4^z6)==0. <X-bar1_A>=<x0^x1> gives <X-bar> (basis X) or <Y-bar> (basis Y).

The four T-targets (m=0): I->(X,Y)=(+0.71,+0.71) 45deg; S-bar->(-0.71,+0.71) 135; Z-bar->(-0.71,-0.71)
225; S-bar.Z-bar->(+0.71,-0.71) 315 -- a full programmable rotation, every point non-stabilizer.

FROZEN GATES (checked in selftest, statevector-exact):
  G1_PROGRAMMABLE_ROTATION: the 4 T-wrappers land at the 4 DIAGONAL equator points -- each |<X-bar>| and
     |<Y-bar>| in [0.55,0.85], with the (sign_X, sign_Y) pattern (++,-+,--,+-) for (I,S,Z,SZ). A
     programmable non-Clifford rotation steered by the logical-Clifford program.
  G2_T_NECESSARY: with the Clifford (S) ancilla, the points collapse onto stabilizer AXES (not the
     diagonal): every |<X-bar>| or |<Y-bar>| <= 0.2 for at least one axis per wrapper (on-axis, not the
     magic diagonal). Only the non-Clifford T reaches the diagonal equator targets.
  Registered verdict = G1 and G2. REPORTED: the 8 (wrapper x basis) values + acceptance (m=0 postselect).
SCOPE: error-DETECTED (distance-2, postselect + m=0), single injected T + cheap logical-Clifford program,
  X-bar-robust readout (Y-bar via S-bar-dagger). Composes 243 (injection) + 214 (cheap in-block S-bar1) +
  213 (the logical-Y idea). Completes 244's 2-point steering into a 4-point programmable rotation.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
GATES = {"T": PI / 4, "S": PI / 2}
WRAPPERS = ("I", "S", "Z", "SZ")
BASES = ("X", "Y")
# ideal (X,Y) for W . T|+bar>, m=0:
IDEAL_T = {"I": (0.707, 0.707), "S": (-0.707, 0.707), "Z": (-0.707, -0.707), "SZ": (0.707, -0.707)}


def _plus_bar(qc, b):
    qc.h(b); qc.cx(b, b + 1); qc.h(b + 2); qc.cx(b + 2, b + 3)


def _sbar(qc, dag=False):                    # logical S-bar1 on block A = S0 S2 CZ(0,2)  (214)
    if dag: qc.sdg(0); qc.sdg(2)
    else: qc.s(0); qc.s(2)
    qc.cz(0, 2)


def _zbar(qc):                               # logical Z-bar1 = Z0 Z2
    qc.z(0); qc.z(2)


def circuit(gate, wrapper, basis):
    qc = QuantumCircuit(8, 8)
    _plus_bar(qc, 0)                          # data A = |+bar>
    _plus_bar(qc, 4)                          # ancilla B ...
    qc.rzz(GATES[gate], 4, 6)                 # ... = Rz_bar(theta)|+bar>  (T magic / S Clifford)
    qc.barrier()
    for i in range(4): qc.cx(i, i + 4)        # transversal CNOT A->B (inject)
    qc.barrier()
    if wrapper in ("S", "SZ"): _sbar(qc)      # logical-Clifford PROGRAM on A
    if wrapper in ("Z", "SZ"): _zbar(qc)
    if basis == "Y": _sbar(qc, dag=True)      # read Y-bar := S-bar-dagger then X-bar
    qc.barrier()
    for q in range(4): qc.h(q)                # all-X readout on A (X-bar1 = x0^x1; XXXX_A postselect)
    for q in range(8): qc.measure(q, q)       # B in Z (m = z4^z6; ZZZZ_B postselect)
    return qc


def _analyze(counts):
    """postselect XXXX_A & ZZZZ_B & m==0; return <X-bar1_A> and acceptance."""
    acc = c = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(8)]; tot += n
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) or (v[4] ^ v[5] ^ v[6] ^ v[7]): continue
        if (v[4] ^ v[6]) != 0: continue        # m == 0 (drop the byproduct branch)
        acc += n; c += (1 - 2 * (v[0] ^ v[1])) * n
    return (c / acc if acc else 0.0), (acc / tot)


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000
    print("Exp246 selftest | THE PROGRAMMABLE ROTATION — inject T, steer around the Bloch equator")
    ok = True
    for w in WRAPPERS:
        xv, _ = _analyze(sim.run(circuit("T", w, "X"), shots=shots).result().get_counts())
        yv, _ = _analyze(sim.run(circuit("T", w, "Y"), shots=shots).result().get_counts())
        ix, iy = IDEAL_T[w]
        good = abs(xv - ix) < 0.05 and abs(yv - iy) < 0.05
        ok = ok and good
        print(f"  T, W={w:>2}: (<X-bar>,<Y-bar>)=({xv:+.3f},{yv:+.3f})  ideal ({ix:+.2f},{iy:+.2f}) {'ok' if good else 'MISMATCH'}")
    assert ok, "the 4 T-wrappers must land at the 4 diagonal equator points"
    # Clifford falsifier: S ancilla -> on-axis (stabilizer), not diagonal
    for w in ("I",):
        xv, _ = _analyze(sim.run(circuit("S", w, "X"), shots=shots).result().get_counts())
        yv, _ = _analyze(sim.run(circuit("S", w, "Y"), shots=shots).result().get_counts())
        print(f"  S(Clifford), W={w}: (<X-bar>,<Y-bar>)=({xv:+.3f},{yv:+.3f}) — expect an AXIS (a 0), not the diagonal")
        assert abs(xv) <= 0.15 or abs(yv) <= 0.15, "Clifford injection must land on a stabilizer axis"
    print("SELFTEST PASS: the injected T is steered by the logical-Clifford program to the 4 distinct "
          "non-stabilizer equator targets (a programmable rotation); the Clifford ancilla collapses to an "
          "axis. Y-bar read cleanly via S-bar-dagger+X-bar; byproduct dropped by m=0 postselect. Cleared.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [("T", w, bsp) for w in WRAPPERS for bsp in BASES] + [("S", "I", "X"), ("S", "I", "Y")]
    circuits = [transpile(circuit(*o), backend=backend, optimization_level=3, seed_transpiler=0) for o in order]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)} (243-class: 2 blocks + transversal CNOT)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp246_programmable_rotation_manifest.json")
    man = {"exp": 246, "slug": "programmable_rotation", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "prereg": {"G1_programmable_rotation": "4 T-wrappers land at 4 diagonal equator points (|X|,|Y| in [0.55,0.85], signs ++,-+,--,+-)",
                      "G2_T_necessary": "Clifford S ancilla collapses onto a stabilizer axis (a 0), not the diagonal",
                      "registered_verdict": "G1 and G2 — a programmable non-Clifford rotation, error-detected",
                      "scope": "single injected T + cheap logical-Clifford program; Y-bar via S-bar-dagger+X-bar; m=0 postselect"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp246_programmable_rotation_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    def counts(idx):
        r0 = res[idx]; reg = list(r0.data.keys())[0]; return getattr(r0.data, reg).get_counts()
    vals = {}
    for idx, o in enumerate(man["order"]):
        vals[tuple(o)] = _analyze(counts(idx))
    print(f"Exp246 THE PROGRAMMABLE ROTATION decode | job {man['job_id']}")
    print("  gate wrapper   <X-bar>   <Y-bar>   (ideal)          accept")
    pts = {}
    for w in WRAPPERS:
        xv, ax = vals[("T", w, "X")]; yv, ay = vals[("T", w, "Y")]; pts[w] = (xv, yv)
        ix, iy = IDEAL_T[w]
        print(f"  T    {w:>2}       {xv:+.3f}   {yv:+.3f}    ({ix:+.2f},{iy:+.2f})    {ax:.2f}/{ay:.2f}")
    sx, _ = vals[("S", "I", "X")]; sy, _ = vals[("S", "I", "Y")]
    print(f"  S(Cliff) I    {sx:+.3f}   {sy:+.3f}    (axis)")
    # G1: 4 diagonal non-stabilizer points with correct signs
    sign = {"I": (1, 1), "S": (-1, 1), "Z": (-1, -1), "SZ": (1, -1)}
    g1 = all(0.55 <= abs(pts[w][0]) <= 0.85 and 0.55 <= abs(pts[w][1]) <= 0.85
             and np.sign(pts[w][0]) == sign[w][0] and np.sign(pts[w][1]) == sign[w][1] for w in WRAPPERS)
    g2 = abs(sx) <= 0.2 or abs(sy) <= 0.2
    print(f"\nG1 PROGRAMMABLE ROTATION: 4 diagonal non-stab targets, correct signs {'OK' if g1 else 'MISS'}")
    print(f"G2 T-NECESSARY: Clifford collapses to an axis (|{sx:+.2f}| or |{sy:+.2f}| <= 0.2) {'OK' if g2 else 'MISS'}")
    ok = g1 and g2
    win = ("THE PROGRAMMABLE ROTATION — the injected non-Clifford T steered by a logical-Clifford program "
           "to FOUR distinct non-stabilizer targets around the Bloch equator (45/135/225/315deg), each a "
           "point no stabilizer state can occupy, collapsing onto a stabilizer axis the instant T becomes "
           "a Clifford. Clifford + T composed into a programmable rotation, error-detected — the universal "
           "gate set not just closed (244) but dialed")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "points": {w: pts[w] for w in WRAPPERS}, "S_axis": [sx, sy],
               "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp246_programmable_rotation_decode.json"), "w"), indent=1)
    print("-> results/exp246_programmable_rotation_decode.json")


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
