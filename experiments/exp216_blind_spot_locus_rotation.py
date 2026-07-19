#!/usr/bin/env python3
"""Exp216 — THE ROTATING BLIND SPOT: the [[4,2,2]] transfer function is basis-relative. C4905.

Horizons-5 P5 flight 2, on the standing go ("fly the next one!"). Exp211 measured the shield's
coherent-error transfer function for the X-basis logical readout and found the RULE: blind spots
are the error axes ORTHOGONAL to the logical readout basis (X-readout -> Y,Z blind, X
transparent). The sharp prediction: the blind-spot locus ROTATES with the readout basis. This
flight confirms it by measuring BOTH bases in one experiment:
  X-readout (prep |+bar>): blind = Y,Z ; transparent = X   (reproduces 211)
  Z-readout (prep |0bar>): blind = X,Y ; transparent = Z   (the rotated locus — the prediction)

If the blind axis for each readout is exactly the plane orthogonal to it, the transfer function
is fully determined by (error axis) . (readout basis): blind iff perpendicular. The shield's
coherent-error response is then a single geometric rule, and the code is a complete self-
characterizing spectrometer.

Apparatus (211): prep the logical eigenstate of the readout basis, apply global R_axis(theta)^4,
read out. A = acceptance (parity check in the readout basis); L = logical corruption (readout-
basis logical Pauli flipped, union over L1,L2); P_silent = A*L.
Arms: readout {X,Z} x error axis {X,Y,Z} x dose theta/pi {0,1/4,1/2,3/4,1} = 30 circuits.

FROZEN GATES (statevector-exact):
  G1_211_REPRODUCE: X-readout, Z-axis, pi/2 -> A>=0.85 & L>=0.60 (the 211 blind spot).
  G2_ROTATED_LOCUS: Z-readout, X-axis, pi/2 -> A>=0.85 & L>=0.60 (the ROTATED blind spot -
     the X-axis, transparent for X-readout, is now a blind spot for Z-readout).
  G3_TRANSPARENT_FLIP: P_silent(X-axis, X-readout, pi/2) <= 0.15 AND P_silent(Z-axis, Z-readout,
     pi/2) <= 0.15 (each readout is transparent to its OWN axis).
  G4_RULE: for every (readout, axis, interior dose), |A-A_exact|<=0.12 and |L-L_exact|<=0.12
     (the full 2x3 transfer function matches the blind-iff-perpendicular rule).
Registered verdict = G1-G4.
SCOPE: [[4,2,2]] coherent-error transfer function, X- and Z-basis logical readouts, global-
rotation error family. Completes 211: the blind-spot locus is basis-relative (blind iff error
axis orthogonal to readout basis). Textbook code + 211 priors; contribution is the rotating-
locus confirmation.
BUDGET CHECK (C4887): shallow (3 2q each, like 211). Filed: both blind spots A>=0.88/L>=0.65;
own-axis P_silent < 0.10.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
READOUTS = ("X", "Z")
AXES = ("X", "Y", "Z")
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
INTERIOR = (0.25, 0.5, 0.75)


def circuit(readout, axis, t, measured=True):
    th = t * PI
    qc = QuantumCircuit(4, 4 if measured else 0)
    qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)   # |0bar0bar>
    if readout == "X":
        for q in range(4): qc.h(q)                    # -> |+bar+bar> (X-eigenstate)
    qc.barrier()
    for q in range(4):
        if axis == "X": qc.rx(th, q)
        elif axis == "Y": qc.ry(th, q)
        elif axis == "Z": qc.rz(th, q)
    qc.barrier()
    if readout == "X":
        for q in range(4): qc.h(q)                    # X-basis readout
    if measured:
        for q in range(4): qc.measure(q, q)
    return qc


def _stats(counts):
    acc = rej = corr = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(4)]
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) != 0:          # parity check (XXXX or ZZZZ via readout)
            rej += n; continue
        acc += n
        # logical Pauli of the readout basis: L1 = v0^v1, L2 = v0^v2 (same index map for X and Z
        # readout — the physical bits already carry the readout-basis outcome). Union flip.
        corr += n * (1 if ((v[0] ^ v[1]) or (v[0] ^ v[2])) else 0)
    tot = acc + rej
    return {"A": acc / tot if tot else 0.0, "L": corr / acc if acc else 0.0, "n_acc": acc, "n": tot}


def analyze(get):
    r = {(ro, ax, t): _stats(get(ro, ax, t)) for ro in READOUTS for ax in AXES for t in DOSES}
    for k in r:
        r[k]["P_silent"] = r[k]["A"] * r[k]["L"]
    return r


def exact():
    from qiskit.quantum_info import Statevector
    out = {}
    for ro in READOUTS:
        for ax in AXES:
            for t in DOSES:
                sv = Statevector(circuit(ro, ax, t, measured=False))
                probs = sv.probabilities_dict(range(4))
                acc = corr = 0.0
                for bs, p in probs.items():
                    b = bs[::-1]; v = [int(b[i]) for i in range(4)]
                    if (v[0] ^ v[1] ^ v[2] ^ v[3]) != 0:
                        continue
                    acc += p
                    corr += p * (1 if ((v[0] ^ v[1]) or (v[0] ^ v[2])) else 0)
                A = acc; L = corr / acc if acc > 1e-12 else 0.0
                out[(ro, ax, t)] = {"A": A, "L": L, "P_silent": A * L}
    return out


def selftest():
    from qiskit_aer import AerSimulator
    ex = exact()
    print("Exp216 selftest | transfer function (statevector-exact): blind iff error axis _|_ readout")
    for ro in READOUTS:
        row = "  " + ro + "-readout P_silent@pi/2:  " + "  ".join(
            f"{ax}:{ex[(ro, ax, 0.5)]['P_silent']:.3f}" for ax in AXES)
        print(row)
    # X-readout: X transparent, Y/Z blind. Z-readout: Z transparent, X/Y blind.
    assert ex[("X", "Z", 0.5)]["A"] >= 0.85 and ex[("X", "Z", 0.5)]["L"] >= 0.60, "211 blind spot"
    assert ex[("Z", "X", 0.5)]["A"] >= 0.85 and ex[("Z", "X", 0.5)]["L"] >= 0.60, "rotated blind spot"
    assert ex[("X", "X", 0.5)]["P_silent"] <= 0.10, "X-readout transparent to X"
    assert ex[("Z", "Z", 0.5)]["P_silent"] <= 0.10, "Z-readout transparent to Z"
    sim = AerSimulator(); shots = 40000
    def get(ro, ax, t): return sim.run(circuit(ro, ax, t), shots=shots).result().get_counts()
    r = analyze(get)
    for ro in READOUTS:
        for ax in AXES:
            for t in DOSES:
                assert abs(r[(ro, ax, t)]["A"] - ex[(ro, ax, t)]["A"]) < 0.02
    print("SELFTEST PASS: the blind-spot locus ROTATES with the readout basis — X-readout blind "
          "to Y,Z; Z-readout blind to X,Y; each transparent to its own axis. blind iff error _|_ "
          "readout, confirmed on both bases. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    ex = exact()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = [[ro, ax, t] for ro in READOUTS for ax in AXES for t in DOSES]
    circuits = [transpile(circuit(ro, ax, t), backend=backend, optimization_level=3, seed_transpiler=0)
                for ro, ax, t in names]
    n2s = [sum(1 for inst in c.data if inst.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp216_locus_rotation_manifest.json")
    man = {"exp": 216, "slug": "blind_spot_locus_rotation", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names,
           "exact": {f"{ro}_{ax}_{t}": ex[(ro, ax, t)] for ro in READOUTS for ax in AXES for t in DOSES}}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "G1_211_reproduce": "X-readout Z-axis pi/2: A>=0.85 & L>=0.60",
        "G2_rotated_locus": "Z-readout X-axis pi/2: A>=0.85 & L>=0.60 (rotated blind spot)",
        "G3_transparent_flip": "P_silent(X-readout,X-axis) & P_silent(Z-readout,Z-axis) <= 0.15",
        "G4_rule": "|A-A_ex|<=0.12 & |L-L_ex|<=0.12 every (readout,axis,interior dose)",
        "registered_verdict": "G1-G4",
        "budget_predictions": "both blind spots A>=0.88/L>=0.65; own-axis P_silent<0.10"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp216_locus_rotation_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (ro, ax, t) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(ro, ax, float(t))] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda ro, ax, t: raw[(ro, ax, t)])
    ex = {(ro, ax, t): man["exact"][f"{ro}_{ax}_{t}"] for ro in READOUTS for ax in AXES for t in DOSES}
    print(f"Exp216 THE ROTATING BLIND SPOT decode | job {man['job_id']}")
    for ro in READOUTS:
        print(f"  {ro}-readout P_silent@pi/2:  " + "  ".join(
            f"{ax}:{r[(ro, ax, 0.5)]['P_silent']:.3f}" for ax in AXES))
    g1 = r[("X", "Z", 0.5)]["A"] >= 0.85 and r[("X", "Z", 0.5)]["L"] >= 0.60
    g2 = r[("Z", "X", 0.5)]["A"] >= 0.85 and r[("Z", "X", 0.5)]["L"] >= 0.60
    g3 = r[("X", "X", 0.5)]["P_silent"] <= 0.15 and r[("Z", "Z", 0.5)]["P_silent"] <= 0.15
    g4 = all(abs(r[(ro, ax, t)]["A"] - ex[(ro, ax, t)]["A"]) <= 0.12
             and abs(r[(ro, ax, t)]["L"] - ex[(ro, ax, t)]["L"]) <= 0.12
             for ro in READOUTS for ax in AXES for t in INTERIOR)
    print(f"\nG1 211 BLIND SPOT (X-readout, Z-axis): A={r[('X','Z',0.5)]['A']:.3f} "
          f"L={r[('X','Z',0.5)]['L']:.3f} {'OK' if g1 else 'MISS'}")
    print(f"G2 ROTATED BLIND SPOT (Z-readout, X-axis): A={r[('Z','X',0.5)]['A']:.3f} "
          f"L={r[('Z','X',0.5)]['L']:.3f} {'OK' if g2 else 'MISS'}")
    print(f"G3 TRANSPARENT-FLIP: X/X P_s={r[('X','X',0.5)]['P_silent']:.3f}, "
          f"Z/Z P_s={r[('Z','Z',0.5)]['P_silent']:.3f} {'OK' if g3 else 'MISS'}")
    print(f"G4 RULE (full 2x3 transfer function): max |dA| "
          f"{max(abs(r[(ro,ax,t)]['A']-ex[(ro,ax,t)]['A']) for ro in READOUTS for ax in AXES for t in INTERIOR):.3f}, "
          f"max |dL| {max(abs(r[(ro,ax,t)]['L']-ex[(ro,ax,t)]['L']) for ro in READOUTS for ax in AXES for t in INTERIOR):.3f} "
          f"{'OK' if g4 else 'MISS'}")
    ok = g1 and g2 and g3 and g4
    win = ("THE ROTATING BLIND SPOT — the [[4,2,2]] coherent-error transfer function is a single "
           "geometric rule: a code is blind exactly to the error axes ORTHOGONAL to its logical "
           "readout basis, and the blind-spot locus rotates with the basis (X-readout blind to "
           "Y,Z; Z-readout blind to X,Y). The self-characterizing spectrometer, complete")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "map": {f"{ro}_{ax}_{t}": r[(ro, ax, t)] for ro in READOUTS for ax in AXES for t in DOSES},
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "g4": bool(g4), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp216_locus_rotation_decode.json"), "w"), indent=1)
    print("-> results/exp216_locus_rotation_decode.json")


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
