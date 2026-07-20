#!/usr/bin/env python3
"""Exp223 — THE BIRTH OF THE CLASSICAL WORLD: quantum Darwinism as an objectivity dial. C4911.

Horizons-5 P4. Exp204's exponent law measured how many observers make a fact; Exp198's dial set
how strongly a fact is copied. Compose them into an instrument for the emergence of classical
reality — and a physics-enforced privacy control.

A system S = |+bar-pointer> is broadcast into N environment fragments by partial-copy couplings
cry(theta, S->E_i) (the 198/200b record dial). Measuring everything in the pointer (Z) basis, the
accessible information a fragment group holds about S is the classical mutual information
I(S : E_f). Three measured faces of the classical world's birth:

  THE PLATEAU (Darwinism): at full copy (theta=pi) I(S:E_f) ~ 1 bit = H(S) for EVERY fragment
    f >= 1 — the fact is redundantly recorded, N independent observers each hold the whole thing.
    Objectivity = the redundancy plateau.
  THE DIAL (selective objectivity / privacy): a single fragment's info I(S:E_1) rises monotonically
    with the copy strength theta, from ~0 (private — no observer can learn the fact) to ~1
    (objective — every observer learns it). The objectivity of a fact is a dialable quantity.
  THE RISE (consensus): at partial copy (theta=pi/2) I(S:E_f) grows with the number of fragments f
    — objectivity accumulates as more observers hold a piece.

Exact ideal: S=|+>, each fragment independent with P(E_i=1|S=1)=sin^2(theta/2), P(E_i=1|S=0)=0;
joint P(S,E_1..E_N)=0.5 * prod P(E_i|S). Classical MI computed from that (ideal) and from the
Z-basis counts (measured). N=5 fragments, doses theta/pi in {0,1/4,1/2,3/4,1}. Shallow (N cry), all
Z-basis (H-free readout).

FROZEN GATES (relative to the exact classical ideal; checked in selftest):
  G1_PLATEAU: at theta=pi, I(S:E_f) >= 0.80 for every f=1..N AND the plateau is flat (max-min over
     f <= 0.15) — the redundancy plateau (objectivity: every fragment holds the whole fact).
  G2_DIAL: I(S:E_1) is monotone increasing in theta and matches the exact ideal to <= 0.12 at each
     dose; I(theta=0) <= 0.06 (private) and I(theta=pi) >= 0.80 (objective) — the selective-
     objectivity / privacy dial.
  G3_RISE: at theta=pi/2, I(S:E_N) - I(S:E_1) >= 0.15 and I(S:E_f) non-decreasing in f — objectivity
     accumulates with observers.
  Registered verdict = G1 and G2 and G3.
SCOPE: single system + N=5 single-qubit fragments (width-cheap); the accessible/pointer information
  (classical MI in the pointer basis) is the Darwinism objectivity quantity for a decohered pointer
  (quantum MI = classical MI in the pointer basis here). Textbook quantum Darwinism (Zurek;
  Ollivier-Poulin-Zurek) + the campaign's 198/204 dial; contribution = objectivity as a dialed,
  measured quantity + the private/objective control. n finite (F98 hull at N=5), not asymptotic.
BUDGET CHECK (C4887): shallow (5 cry). Filed: I(S:E_1) at pi/2 ~ 0.31; plateau ~1.0 at full copy.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
N = 5                                   # environment fragments
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)


def circuit(t):
    """system q0 = |+>, broadcast into N fragments q1..qN by cry(theta). Measure all in Z."""
    qc = QuantumCircuit(1 + N, 1 + N)
    qc.h(0)                             # system pointer superposition
    for i in range(1, N + 1):
        qc.cry(t * PI, 0, i)            # partial copy of the pointer into fragment i
    qc.barrier()
    for q in range(1 + N): qc.measure(q, q)
    return qc


def _mi_from_joint(joint):
    """classical mutual information I(S:E) in bits from a dict {(s, e_tuple): prob}."""
    ps = {}; pe = {}
    for (s, e), p in joint.items():
        ps[s] = ps.get(s, 0) + p; pe[e] = pe.get(e, 0) + p
    mi = 0.0
    for (s, e), p in joint.items():
        if p > 0 and ps[s] > 0 and pe[e] > 0:
            mi += p * np.log2(p / (ps[s] * pe[e]))
    return float(max(0.0, mi))


def _mi_of_f(counts, k):
    """I(S : first-k fragments) from Z-basis counts. bit index: q0=S, q1..qN=fragments."""
    tot = sum(counts.values()); joint = {}
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(1 + N)]
        S = v[0]; E = tuple(v[1:1 + k])
        joint[(S, E)] = joint.get((S, E), 0) + n / tot
    return _mi_from_joint(joint)


def _ideal_mi(t, k):
    """exact classical MI I(S:E_f) for k fragments at strength t (each frag independent)."""
    q = np.sin(t * PI / 2) ** 2         # P(E_i=1 | S=1); P(E_i=1|S=0)=0
    joint = {}
    for S in (0, 1):
        # each fragment: given S, E_i ~ Bernoulli(q if S==1 else 0)
        for mask in range(2 ** k):
            E = tuple((mask >> j) & 1 for j in range(k))
            p_e = 1.0
            for bit in E:
                pi_ = (q if S == 1 else 0.0)
                p_e *= (pi_ if bit == 1 else (1 - pi_))
            joint[(S, E)] = joint.get((S, E), 0) + 0.5 * p_e
    return _mi_from_joint(joint)


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 200000
    print(f"Exp223 selftest | THE BIRTH OF THE CLASSICAL WORLD — objectivity dial (N={N} fragments)")
    res = {}
    for t in DOSES:
        ct = sim.run(circuit(t), shots=shots).result().get_counts()
        mis = [_mi_of_f(ct, k) for k in range(1, N + 1)]
        res[t] = mis
        ideal1 = _ideal_mi(t, 1)
        print(f"  th={t:.2f}pi: I(S:E_f) f=1..{N} = {[round(m,3) for m in mis]}  (ideal I1={ideal1:.3f})")
    # G1 plateau at full copy
    plateau = res[1.0]
    print(f"  PLATEAU @full copy: min={min(plateau):.3f} spread={max(plateau)-min(plateau):.3f}")
    assert min(plateau) > 0.80 and (max(plateau) - min(plateau)) < 0.15, "redundancy plateau"
    # G2 dial: I(S:E_1) monotone + matches ideal
    dial = [res[t][0] for t in DOSES]
    for i, t in enumerate(DOSES):
        assert abs(dial[i] - _ideal_mi(t, 1)) < 0.05, f"dial vs ideal {t}"
    assert dial[0] < 0.06 and dial[-1] > 0.80, "dial private->objective endpoints"
    assert all(dial[i] <= dial[i + 1] + 0.02 for i in range(len(dial) - 1)), "dial monotone"
    # G3 rise at half copy
    rise = res[0.5]
    assert rise[-1] - rise[0] > 0.15 and all(rise[i] <= rise[i + 1] + 0.02 for i in range(N - 1)), "consensus rise"
    print(f"  DIAL I(S:E_1) vs theta: {[round(d,3) for d in dial]}  (private->objective)")
    print(f"  RISE @half copy: I(S:E_1)={rise[0]:.3f} -> I(S:E_{N})={rise[-1]:.3f}")
    print("SELFTEST PASS: objectivity emerges as a redundancy plateau, dials from private to public "
          "with copy strength, and accumulates with observers. The classical world, measured. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    builds = [circuit(t) for t in DOSES]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp223_objectivity_dial_manifest.json")
    man = {"exp": 223, "slug": "objectivity_dial", "backend": backend_name, "shots": shots, "N": N,
           "job_id": job.job_id(), "doses": list(DOSES),
           "ideal": {str(t): [_ideal_mi(t, k) for k in range(1, N + 1)] for t in DOSES},
           "prereg": {"G1_plateau": "theta=pi: I(S:E_f)>=0.80 all f, spread<=0.15 (redundancy plateau)",
                      "G2_dial": "I(S:E_1) monotone, matches ideal <=0.12; th=0 <=0.06 (private), th=pi >=0.80 (objective)",
                      "G3_rise": "theta=pi/2: I(S:E_N)-I(S:E_1)>=0.15, non-decreasing in f",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "system + N=5 fragments; pointer-basis accessible info = Darwinism "
                               "objectivity; selective-objectivity/privacy dial on the 198/204 apparatus"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp223_objectivity_dial_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    doses = man["doses"]; raw = {}
    for idx, t in enumerate(doses):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[t] = getattr(r0.data, reg).get_counts()
    ideal = {float(t): v for t, v in man["ideal"].items()}
    print(f"Exp223 THE BIRTH OF THE CLASSICAL WORLD decode | job {man['job_id']}")
    mi = {}
    for t in doses:
        mi[t] = [_mi_of_f(raw[t], k) for k in range(1, N + 1)]
        print(f"  th={t:.2f}pi: I(S:E_f) = {[round(m,3) for m in mi[t]]}  (ideal I1={ideal[t][0]:.3f})")
    plateau = mi[1.0]
    dial = [mi[t][0] for t in doses]
    rise = mi[0.5]
    g1 = min(plateau) >= 0.80 and (max(plateau) - min(plateau)) <= 0.15
    g2 = (all(abs(dial[i] - ideal[doses[i]][0]) <= 0.12 for i in range(len(doses)))
          and dial[0] <= 0.06 and dial[-1] >= 0.80
          and all(dial[i] <= dial[i + 1] + 0.03 for i in range(len(dial) - 1)))
    g3 = (rise[-1] - rise[0]) >= 0.15 and all(rise[i] <= rise[i + 1] + 0.03 for i in range(N - 1))
    print(f"\nG1 PLATEAU (full copy): I(S:E_f) min {min(plateau):.3f}, spread {max(plateau)-min(plateau):.3f} {'OK' if g1 else 'MISS'}")
    print(f"G2 DIAL (private->objective): I(S:E_1) {[round(d,3) for d in dial]}; ends {dial[0]:.3f}/{dial[-1]:.3f} {'OK' if g2 else 'MISS'}")
    print(f"G3 RISE (consensus @half): I1={rise[0]:.3f} -> I{N}={rise[-1]:.3f} (+{rise[-1]-rise[0]:.3f}) {'OK' if g3 else 'MISS'}")
    ok = g1 and g2 and g3
    win = ("THE BIRTH OF THE CLASSICAL WORLD — objectivity measured as a dial: a fact becomes a "
           "redundancy plateau (every observer holds the whole of it), its objectivity tunes from "
           "PRIVATE to PUBLIC with copy strength, and it sharpens as more observers agree. Quantum "
           "Darwinism turned into an objectivity/privacy instrument, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "mi": {str(t): mi[t] for t in doses},
               "plateau": plateau, "dial": dial, "rise": rise,
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp223_objectivity_dial_decode.json"), "w"), indent=1)
    print("-> results/exp223_objectivity_dial_decode.json")


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
