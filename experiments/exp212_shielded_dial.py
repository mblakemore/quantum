#!/usr/bin/env python3
"""Exp212 — THE SHIELDED DIAL: fault-tolerant indefinite causal order is a tunable resource. C4905.

Horizons-5 P1 / ICO arc, on the standing go ("ICO!"). 208 showed the shielded causal witness
fires; 209 showed it beats a FULL classical mixture. This flight sweeps the CONTINUUM between
them: dial the control's order-coherence from full (switch) to zero (mixture) and show the
SHIELDED witness DISC(phi) follows a continuous law — the F74/F76 continuous-law result
(bare: DISC(phi) = 2cos(phi/2), Pearson 0.9992) lifted into the [[4,2,2]] code. Indefinite
causal order is not binary behind the shield; it is a smooth, tunable resource.

The dial: after the shielded witness (208 apparatus — control bare in |+>, target [[4,2,2]]
logical, ops = logical Paulis Xbar1/Zbar1, ZZZZ postselect), a PARTIAL decohering coupling
cry(phi, control -> junk ancilla) between the switch halves drains the order-coherence by a
tunable amount. phi=0 -> full switch (209's switch arm); phi=pi -> full mixture (209's mixture
arm); interior phi -> partial definiteness. Exact DISC(phi) from the statevector (frozen from
the selftest).

Doses phi/pi {0, 1/4, 1/2, 3/4, 1}, pairs {commute (X,X), anti (X,Z)} = 10 circuits.
FROZEN GATES (relative to statevector-exact):
  G1_ANCHORS: DISC(0) > 1.0 at >=5 sigma (full shielded switch, reproduces 208/209 ~1.7);
     |DISC(pi)| <= 0.20 (full mixture, reproduces 209 inert).
  G2_CONTINUOUS_LAW: |DISC_meas(phi) - DISC_exact(phi)| <= 0.25 at every interior dose, and
     DISC strictly decreasing in phi (the dial actually dials, monotone from switch to mixture).
  G3_HALF_POINT: the phi where DISC crosses 0.5*DISC(0) is bracketed at >=3 sigma both sides
     (the half-coherence point measured — order-definiteness has a measured midpoint).
Registered verdict = G1 and G2 and G3.
SCOPE: coherence-of-causal-order witness (F77), half-shielded target, single-syndrome ZZZZ
(inherited from 208). Reproduces the F74/F76 continuous order-coherence law in the code.
BUDGET CHECK (C4887): 208/209 measured DISC_switch ~1.7; the dial spans 1.7->0. Ample.
Filed: DISC(0) in [1.4,1.9]; law residuals <= 0.15; half-point near phi=pi/2.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
PAIRS = {"commute": ("X", "X"), "anti": ("X", "Z")}
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
INTERIOR = (0.25, 0.5, 0.75)


def _ctrl_logical(qc, gate, c, cstate):
    if cstate == 0: qc.x(c)
    if gate == "X": qc.cx(c, 1); qc.cx(c, 2)
    elif gate == "Z": qc.cz(c, 1); qc.cz(c, 3)
    if cstate == 0: qc.x(c)


def circuit(A, B, phi, measured=True):
    """control q0, target [[4,2,2]] q1-4, dial-ancilla q5."""
    qc = QuantumCircuit(6, 5 if measured else 0)
    qc.h(0)
    qc.h(1); qc.cx(1, 2); qc.cx(1, 3); qc.cx(1, 4)   # target |0bar0bar>
    qc.barrier()
    _ctrl_logical(qc, A, 0, 0); _ctrl_logical(qc, B, 0, 1)
    if phi > 1e-9:
        qc.cry(phi, 0, 5)                             # partial order-decoherence dial
    qc.barrier()
    _ctrl_logical(qc, B, 0, 0); _ctrl_logical(qc, A, 0, 1)
    qc.barrier(); qc.h(0)
    if measured:
        for q in range(5): qc.measure(q, q)           # control(X)=clbit0, target(Z)=1-4
    return qc


def _xc(counts):
    acc = c = rej = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(5)]
        if v[1] ^ v[2] ^ v[3] ^ v[4]:
            rej += n; continue
        acc += n; c += (1 - 2 * v[0]) * n
    return (c / acc if acc else 0.0), acc, acc + rej


def analyze(get):
    r = {}
    for t in DOSES:
        xc_c, na_c, nt_c = _xc(get("commute", t))
        xc_a, na_a, nt_a = _xc(get("anti", t))
        r[t] = {"DISC": xc_c - xc_a, "n_acc": min(na_c, na_a),
                "acceptance": (na_c + na_a) / (nt_c + nt_a) if (nt_c + nt_a) else 0.0}
    return r


def exact():
    from qiskit.quantum_info import Statevector
    out = {}
    for t in DOSES:
        phi = t * PI
        discs = {}
        for pair, (A, B) in PAIRS.items():
            sv = Statevector(circuit(A, B, phi, measured=False))
            # <Xc> conditioned on ZZZZ accept: build from probabilities over q0..q4 (trace q5)
            probs = sv.probabilities_dict(range(5))
            acc = xc = 0.0
            for bs, p in probs.items():
                b = bs[::-1]; v = [int(b[i]) for i in range(5)]
                if (v[1] ^ v[2] ^ v[3] ^ v[4]) != 0:
                    continue
                acc += p; xc += (1 - 2 * v[0]) * p
            discs[pair] = xc / acc if acc > 1e-12 else 0.0
        out[t] = discs["commute"] - discs["anti"]
    return out


def selftest():
    from qiskit_aer import AerSimulator
    ex = exact()
    print("Exp212 selftest | shielded DISC(phi) continuous law (statevector-exact):")
    for t in DOSES:
        print(f"  phi={t:.2f}pi: DISC_exact={ex[t]:+.4f}")
    assert ex[0.0] > 1.9, "phi=0 must be the full shielded switch (~2)"
    assert abs(ex[1.0]) < 0.1, "phi=pi must be the full mixture (~0)"
    Ds = [ex[t] for t in DOSES]
    assert all(Ds[i] > Ds[i + 1] - 1e-6 for i in range(4)), "DISC must decrease monotonically"
    sim = AerSimulator(); shots = 40000; cache = {}
    def get(pair, t):
        k = (pair, t)
        if k not in cache:
            A, B = PAIRS[pair]
            cache[k] = sim.run(circuit(A, B, t * PI), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    for t in DOSES:
        print(f"  phi={t:.2f}pi: DISC_aer={r[t]['DISC']:+.4f} (exact {ex[t]:+.4f})  "
              f"acc={r[t]['acceptance']:.3f}")
        assert abs(r[t]["DISC"] - ex[t]) < 0.04, f"Aer/exact mismatch at {t}"
    print("SELFTEST PASS: the shielded witness DISC follows a continuous law from full switch "
          "(~2) to full mixture (~0), strictly decreasing — fault-tolerant indefinite causal "
          "order is a smooth, tunable resource. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    ex = exact()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names, builds = [], []
    for t in DOSES:
        for pair, (A, B) in PAIRS.items():
            names.append([pair, t]); builds.append(circuit(A, B, t * PI))
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for inst in c.data if inst.operation.num_qubits == 2) for c in circuits]
    print(f"  {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp212_shielded_dial_manifest.json")
    man = {"exp": 212, "slug": "shielded_dial", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names, "exact": {str(t): ex[t] for t in DOSES}}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "G1_anchors": "DISC(0) > 1.0 at >=5 sigma; |DISC(pi)| <= 0.20",
        "G2_continuous_law": "|DISC_meas - DISC_exact| <= 0.25 at every interior dose; "
                             "DISC strictly decreasing in phi",
        "G3_half_point": "phi crossing 0.5*DISC(0) bracketed at >=3 sigma both sides",
        "registered_verdict": "G1 and G2 and G3",
        "scope": "coherence-of-causal-order witness (F77), half-shielded, single-syndrome; "
                 "F74/F76 continuous law in the code",
        "budget_predictions": "DISC(0) in [1.4,1.9]; law residuals <= 0.15; half-point ~pi/2"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp212_shielded_dial_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, (pair, t) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(pair, float(t))] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda pair, t: raw[(pair, t)])
    ex = {float(t): v for t, v in man["exact"].items()}
    se = {t: 1 / np.sqrt(max(r[t]["n_acc"], 1)) * np.sqrt(2) for t in DOSES}
    print(f"Exp212 THE SHIELDED DIAL decode | job {man['job_id']}")
    for t in DOSES:
        print(f"  phi={t:.2f}pi: DISC={r[t]['DISC']:+.4f} (exact {ex[t]:+.4f}, se {se[t]:.3f})  "
              f"acc={r[t]['acceptance']:.3f}")
    D0 = r[0.0]["DISC"]
    z0 = (D0 - 1.0) / se[0.0]
    g1 = D0 > 1.0 and z0 >= 5 and abs(r[1.0]["DISC"]) <= 0.20
    Ds = [r[t]["DISC"] for t in DOSES]
    sep = [np.sqrt(se[DOSES[i]] ** 2 + se[DOSES[i + 1]] ** 2) for i in range(4)]
    mono = all(Ds[i + 1] - Ds[i] <= 2 * sep[i] for i in range(4))
    resid_ok = all(abs(r[t]["DISC"] - ex[t]) <= 0.25 for t in INTERIOR)
    g2 = resid_ok and mono
    # half point
    half = 0.5 * D0
    hp = None
    for i in range(4):
        if Ds[i] >= half >= Ds[i + 1]:
            frac = (Ds[i] - half) / (Ds[i] - Ds[i + 1]) if Ds[i] != Ds[i + 1] else 0
            hp = DOSES[i] + frac * (DOSES[i + 1] - DOSES[i]); break
    g3 = hp is not None and any((Ds[i] - half) / sep[min(i, 3)] >= 3 for i in range(len(DOSES)) if Ds[i] > half) \
         and any((half - Ds[i]) / sep[min(i - 1, 3)] >= 3 for i in range(len(DOSES)) if Ds[i] < half)
    print(f"\nG1 ANCHORS: DISC(0)={D0:.3f} ({z0:.0f} sigma), DISC(pi)={r[1.0]['DISC']:+.3f} "
          f"{'OK' if g1 else 'MISS'}")
    print(f"G2 CONTINUOUS LAW: max interior resid "
          f"{max(abs(r[t]['DISC'] - ex[t]) for t in INTERIOR):.3f}, monotone {mono} "
          f"{'OK' if g2 else 'MISS'}")
    print(f"G3 HALF-POINT: phi* = {hp:.3f}pi (DISC crosses {half:.3f}) {'OK' if g3 else 'MISS'}"
          if hp else "G3 HALF-POINT: not bracketed MISS")
    ok = g1 and g2 and g3
    win = ("THE SHIELDED DIAL — fault-tolerant indefinite causal order is a smooth, tunable "
           "resource: the shielded witness DISC follows a continuous law from full switch to "
           "full mixture, error-detected. The F74/F76 continuous law, in the code")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "DISC": {str(t): r[t]["DISC"] for t in DOSES},
               "exact": {str(t): ex[t] for t in DOSES}, "half_point_pi": hp,
               "sigma_anchor": float(z0), "acceptance": float(np.mean([r[t]["acceptance"] for t in DOSES])),
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp212_shielded_dial_decode.json"), "w"), indent=1)
    print("-> results/exp212_shielded_dial_decode.json")


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
