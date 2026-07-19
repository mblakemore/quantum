#!/usr/bin/env python3
"""Exp195b — BEAM THE POWER (clean readout): Hotta quantum energy teleportation. C4887.

H = h(Z_A+Z_B) + k X_A X_B (h=1, k=1.5), exact entangled ground |g> (E=-2.5; Bob-local share
E_B = h<Z_B>+k<X_A X_B> = -1.7). Alice measures X_A (the coupling basis) -> bit s, sent to Bob
by a classical channel (real feed-forward, if_test); Bob applies Ry(+2*theta) if X_A=+1 (s=0),
Ry(-2*theta) if X_A=-1 (s=1), theta=0.17 (numeric optimum). Bob's local energy drops by
Delta E_B = -0.1028: energy extracted from the A-B correlations, none in transit.

Fixes over exp195 (selftest-gated at C4886):
  1. LOCC bit and energy readout SEPARATED: Alice's X_A measurement writes c0 exactly once and
     freezes X_A = 1-2s; <X_A X_B> is reconstructed as <(1-2s)*x_B> with X_B read from q1 (H
     then measure -> c1). q0 is never touched again in the qet arm.
  2. Conditioning sign matched to the numeric derivation: s=0 -> Ry(+2t) (the old s=0 -> Ry(-2t)
     gives Delta E_B = +0.297, energy PAID — exactly what the selftest refused to pass).
  3. noLOCC falsifier no longer re-entangles A after Bob's kick (old reset+reprep cx scrambled B).
  4. Falsifier prediction corrected by exact numerics: no-information arms give Delta E_B =
     +0.0973 (POSITIVE — a local kick without the bit costs energy, ground-state passivity),
     not ~0 as the old prereg assumed. Discriminator: information -0.103 vs no-information
     +0.097, a 0.200 gap.

Selftest: embedded exact statevector derivation (numpy only) must give -0.1028; Aer circuit
must reproduce it within 0.01 (and both falsifier arms within 0.015 of +0.0973) before flight.
Usage: --selftest | --submit | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
H_, K_ = 1.0, 1.5
BTHETA = 0.17   # Bob conditional angle (numeric optimum; see derive())
GPREP = 3.7851  # Ry angle on q0 for exact ground prep (fidelity 1.000000, re-verified C4887)

# ---------- exact numeric derivation (independent of qiskit; the selftest target) ----------
def derive():
    I2 = np.eye(2); Z = np.diag([1., -1.]); X = np.array([[0., 1.], [1., 0.]])
    op = lambda a, b: np.kron(b, a)                     # a on q0 (Alice), b on q1 (Bob)
    Hfull = H_ * op(Z, I2) + H_ * op(I2, Z) + K_ * op(X, X)
    w, v = np.linalg.eigh(Hfull); g = v[:, 0]
    HB = H_ * op(I2, Z) + K_ * op(X, X)                 # Bob-local share (his Z + the coupling)
    base = float(np.real(g.conj() @ HB @ g))
    Ry = lambda t: np.array([[np.cos(t/2), -np.sin(t/2)], [np.sin(t/2), np.cos(t/2)]])
    Pp, Pm = op((I2 + X) / 2, I2), op((I2 - X) / 2, I2) # X_A = +1 / -1 projectors
    dqet = 0.0
    for P, sgn in ((Pp, +1), (Pm, -1)):                 # X_A=+1 -> +2t, X_A=-1 -> -2t
        psi = P @ g; p = float(np.real(psi.conj() @ psi)); psi /= np.sqrt(p)
        phi = op(I2, Ry(sgn * 2 * BTHETA)) @ psi
        dqet += p * float(np.real(phi.conj() @ HB @ phi))
    dqet -= base
    phi = op(I2, Ry(+2 * BTHETA)) @ g                   # fixed kick, no bit
    dctl_p = float(np.real(phi.conj() @ HB @ phi)) - base
    phi = op(I2, Ry(-2 * BTHETA)) @ g
    dctl_m = float(np.real(phi.conj() @ HB @ phi)) - base
    return {"ground_E": float(w[0]), "baseline_EB": base, "dE_qet": dqet,
            "dE_nomeasure": dctl_p, "dE_noLOCC": (dctl_p + dctl_m) / 2}

# ---------- circuits ----------
def _ground(qc):
    qc.ry(GPREP, 0); qc.cx(0, 1)   # exact ground of h(ZA+ZB)+k XA XB

def circuit(name):
    term = name.split("_")[-1]     # XX or ZB
    arm = name.rsplit("_", 1)[0]   # qet / noLOCC / nomeasure
    qc = QuantumCircuit(3, 3)      # q0=A, q1=B, q2=coin | c0=LOCC/X_A, c1=B readout, c2=coin
    _ground(qc)
    qc.barrier()
    if arm == "qet":
        qc.h(0); qc.measure(0, 0)  # Alice measures X_A -> s in c0 (written once, never reused)
        with qc.if_test((qc.clbits[0], 0)): qc.ry(+2 * BTHETA, 1)   # X_A=+1
        with qc.if_test((qc.clbits[0], 1)): qc.ry(-2 * BTHETA, 1)   # X_A=-1
    elif arm == "noLOCC":
        qc.h(2); qc.measure(2, 2)  # uncorrelated coin drives the same feed-forward
        with qc.if_test((qc.clbits[2], 0)): qc.ry(+2 * BTHETA, 1)
        with qc.if_test((qc.clbits[2], 1)): qc.ry(-2 * BTHETA, 1)
    else:  # nomeasure: fixed kick, no bit at all
        qc.ry(+2 * BTHETA, 1)
    qc.barrier()
    if term == "XX":
        if arm != "qet":
            qc.h(0); qc.measure(0, 0)   # controls: X_A read terminally (A untouched until now)
        qc.h(1)                          # X_B; qet arm's X_A is frozen in c0 already
    qc.measure(1, 1)
    return qc

TERMS = ("XX", "ZB")
ARMSET = ("qet", "noLOCC", "nomeasure")

def analyze(get):
    r = {}
    for arm in ARMSET:
        zb = xx = 0.0
        for term in TERMS:
            c = get(f"{arm}_{term}"); acc = tot = 0
            for s, n in c.items():
                b = s.replace(" ", "")
                if term == "ZB":
                    acc += (1 - 2 * int(b[-2])) * n                           # <Z_B> from c1
                else:
                    acc += (1 - 2 * int(b[-1])) * (1 - 2 * int(b[-2])) * n    # (1-2s)*x_B
                tot += n
            if term == "ZB": zb = acc / tot
            else: xx = acc / tot
        r[arm] = {"ZB": float(zb), "XX": float(xx), "E_B": float(H_ * zb + K_ * xx)}
    return r

def selftest():
    d = derive()
    print(f"Exp195b selftest | exact: ground {d['ground_E']:.4f}, baseline E_B {d['baseline_EB']:.4f}, "
          f"dE_qet {d['dE_qet']:+.4f}, dE_noLOCC {d['dE_noLOCC']:+.4f}, dE_nomeasure {d['dE_nomeasure']:+.4f}")
    assert abs(d["dE_qet"] - (-0.1028)) < 1e-3, "numeric derivation drifted from verified -0.1028"
    assert d["dE_noLOCC"] > 0.05 and d["dE_nomeasure"] > 0.05, "controls must PAY energy (passivity)"
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 200000; cache = {}
    def get(name):
        if name not in cache:
            cache[name] = sim.run(circuit(name), shots=shots).result().get_counts()
        return cache[name]
    r = analyze(get); base = d["baseline_EB"]
    for arm in ARMSET:
        print(f"  {arm:>9}: <Z_B>={r[arm]['ZB']:+.4f} <X_A X_B>={r[arm]['XX']:+.4f} "
              f"E_B={r[arm]['E_B']:+.4f}  Delta={r[arm]['E_B']-base:+.4f}")
    dqet = r["qet"]["E_B"] - base
    assert abs(dqet - d["dE_qet"]) < 0.01, f"circuit must reproduce exact dE_qet, got {dqet:+.4f}"
    assert abs((r["noLOCC"]["E_B"] - base) - d["dE_noLOCC"]) < 0.015, "noLOCC arm off exact"
    assert abs((r["nomeasure"]["E_B"] - base) - d["dE_nomeasure"]) < 0.015, "nomeasure arm off exact"
    print(f"SELFTEST PASS: circuit reproduces the exact derivation — qet extracts {dqet:+.4f} "
          f"(target {d['dE_qet']:+.4f}); both no-information arms PAY ~+0.097. Cleared to fly.")

def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    d = derive()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = [f"{arm}_{t}" for arm in ARMSET for t in TERMS]
    circuits = [transpile(circuit(n), backend=backend, optimization_level=3) for n in names]
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    man = {"exp": "195b", "slug": "energy_teleport", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names, "baseline_EB": d["baseline_EB"],
           "h": H_, "k": K_, "theta": BTHETA, "exact": d,
           "prereg": {"primary": "Delta E_B(qet) < 0 at >=5 sigma; band [-0.15, -0.05] (exact -0.1028)",
                      "falsifiers": "Delta E_B(noLOCC) and Delta E_B(nomeasure) both POSITIVE, "
                                    "band [+0.03, +0.17] (exact +0.0973) — no-information arms pay"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp195b_energy_teleport_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits) | baseline {d['baseline_EB']:.4f}")

def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp195b_energy_teleport_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]
        counts = {}
        for reg in r0.data.keys():                       # merge registers into one bitstring view
            c = getattr(r0.data, reg).get_counts()
            if not counts: counts = c
            else:
                # multiple registers: rebuild joint counts via bit concatenation is backend-dependent;
                # transpiled circuit keeps a single 3-bit creg, so this branch should not trigger
                raise RuntimeError(f"unexpected multi-register result for {name}: {list(r0.data.keys())}")
        raw[name] = counts
    r = analyze(lambda n: raw[n]); base = man["baseline_EB"]; shots = man["shots"]
    seE = np.sqrt((H_**2 + K_**2) / shots)               # conservative per-arm SE on E_B
    dqet = r["qet"]["E_B"] - base; z = -dqet / seE
    print(f"Exp195b BEAM THE POWER decode | job {man['job_id']} | baseline E_B {base:.4f} | "
          f"exact targets: qet {man['exact']['dE_qet']:+.4f}, controls +0.0973")
    for arm in ARMSET:
        print(f"  {arm:>9}: <Z_B>={r[arm]['ZB']:+.3f} <X_A X_B>={r[arm]['XX']:+.3f}  "
              f"E_B={r[arm]['E_B']:+.4f}  Delta={r[arm]['E_B']-base:+.4f}")
    d_no, d_fix = r["noLOCC"]["E_B"] - base, r["nomeasure"]["E_B"] - base
    p_ok = -0.15 <= dqet <= -0.05 and z >= 5
    f_ok = (0.03 <= d_no <= 0.17) and (0.03 <= d_fix <= 0.17)
    print(f"\nPRIMARY: Delta E_B(qet) = {dqet:+.4f} ({z:.0f} sigma below zero) — with Alice's bit, "
          f"Bob's lab loses energy it did not contain")
    print(f"FALSIFIERS: noLOCC {d_no:+.4f} | nomeasure {d_fix:+.4f} (both must be POSITIVE ~ +0.097 "
          f"— the same kick without the information costs energy)")
    ok = p_ok and f_ok
    print(f"VERDICT: {'ENERGY TELEPORTED — extracted from correlations via a classical bit, none in transit; the uninformed kick pays' if ok else 'NOT HELD (accounting above; scope/caveats stand)'}")
    json.dump({"job_id": man["job_id"], "results": r, "baseline": base, "delta_EB": float(dqet),
               "sigma": float(z), "delta_noLOCC": float(d_no), "delta_nomeasure": float(d_fix),
               "primary_ok": bool(p_ok), "falsifier_ok": bool(f_ok), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp195b_energy_teleport_decode.json"), "w"), indent=1)
    print("-> results/exp195b_energy_teleport_decode.json")

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
