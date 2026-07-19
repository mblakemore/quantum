#!/usr/bin/env python3
"""Exp195c — BEAM THE POWER, differential primary: Hotta QET as a pure information effect. C4887.

Exp195b's absolute primary died to the hardware noise budget (11% contrast damping vs a 5.7%
budget): E_B ~ lambda*ideal, and no fez circuit with feed-forward clears lambda>0.943. The
noise-robust observable is the DIFFERENTIAL between two gate-for-gate identical circuits that
differ only in WHICH classical bit drives Bob's kick:

  qet arm:        Alice measures X_A -> c0; coin measured -> c2; kick conditioned on **c0**
  coinfrozen arm: Alice measures X_A -> c0; coin measured -> c2; kick conditioned on **c2**

Both arms freeze A early (no frozen-vs-quantum-A asymmetry — the 195b post-hoc confound is
eliminated by construction, not modeled) and share every gate, measurement, and feed-forward
window; heating cancels in the difference to first order. Exact statevector:
dE_qet = -0.1028, dE_coinfrozen = +0.0973 (dephasing does not change the symmetric cost),
information gap = -0.2001. Under the lambda~0.89 damping measured in 195b, expected observed
gap ~ -0.16 to -0.20; SE_diff at 16000 shots = 0.020 -> ~8-10 sigma.

PRE-REGISTERED PRIMARY: E_B(qet) - E_B(coinfrozen) <= -0.10 at >=5 sigma, band [-0.30, -0.10].
FALSIFIERS: dE(coinfrozen) > 0 and dE(nomeasure) > 0, band [+0.02, +0.50] (hardware heating
pushes up; the physics claim rides on the differential, the falsifiers are sign sanity).
SECONDARY (labeled, not verdict-gating): absolute dE(qet) — expected positive on this fabric.

Usage: --selftest | --submit | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
H_, K_ = 1.0, 1.5
BTHETA = 0.17
GPREP = 3.7851  # exact ground prep Ry angle (fidelity 1.000000)

# ---------- exact numeric derivation (numpy-only; the selftest target) ----------
def derive():
    I2 = np.eye(2); Z = np.diag([1., -1.]); X = np.array([[0., 1.], [1., 0.]])
    op = lambda a, b: np.kron(b, a)
    Hfull = H_ * op(Z, I2) + H_ * op(I2, Z) + K_ * op(X, X)
    w, v = np.linalg.eigh(Hfull); g = v[:, 0]
    HB = H_ * op(I2, Z) + K_ * op(X, X)
    base = float(np.real(g @ HB @ g))
    Ry = lambda t: np.array([[np.cos(t/2), -np.sin(t/2)], [np.sin(t/2), np.cos(t/2)]])
    branches = []
    for P in (op((I2 + X) / 2, I2), op((I2 - X) / 2, I2)):   # X_A = +1, -1
        psi = P @ g; p = float(np.real(psi @ psi)); branches.append((p, psi / np.sqrt(p)))
    dqet = 0.0
    for (p, psi), sgn in zip(branches, (+1, -1)):            # sign correlated with X_A
        phi = op(I2, Ry(sgn * 2 * BTHETA)) @ psi
        dqet += p * float(np.real(phi.conj() @ HB @ phi))
    dqet -= base
    dcoin = 0.0
    for p, psi in branches:                                   # sign from an uncorrelated coin
        for sgn in (+1, -1):
            phi = op(I2, Ry(sgn * 2 * BTHETA)) @ psi
            dcoin += 0.5 * p * float(np.real(phi.conj() @ HB @ phi))
    dcoin -= base
    phi = op(I2, Ry(+2 * BTHETA)) @ g                         # fixed kick, no measurements
    dfix = float(np.real(phi.conj() @ HB @ phi)) - base
    return {"ground_E": float(w[0]), "baseline_EB": base, "dE_qet": dqet,
            "dE_coinfrozen": dcoin, "dE_nomeasure": dfix, "gap": dqet - dcoin}

# ---------- circuits ----------
def _ground(qc):
    qc.ry(GPREP, 0); qc.cx(0, 1)

def circuit(name):
    term = name.split("_")[-1]     # XX or ZB
    arm = name.rsplit("_", 1)[0]   # qet / coinfrozen / nomeasure
    qc = QuantumCircuit(3, 3)      # q0=A, q1=B, q2=coin | c0=X_A bit s, c1=B readout, c2=coin
    _ground(qc)
    qc.barrier()
    if arm in ("qet", "coinfrozen"):
        qc.h(0); qc.measure(0, 0)  # Alice measures X_A -> s (frozen; used in XX reconstruction)
        qc.h(2); qc.measure(2, 2)  # coin measured in BOTH arms (gate-identical)
        drive = 0 if arm == "qet" else 2   # the ONLY difference between the two arms
        with qc.if_test((qc.clbits[drive], 0)): qc.ry(+2 * BTHETA, 1)
        with qc.if_test((qc.clbits[drive], 1)): qc.ry(-2 * BTHETA, 1)
    else:  # nomeasure: fixed kick
        qc.ry(+2 * BTHETA, 1)
    qc.barrier()
    if term == "XX":
        if arm == "nomeasure":
            qc.h(0); qc.measure(0, 0)      # A read terminally (untouched until now)
        qc.h(1)                             # X_B; frozen arms already hold s in c0
    qc.measure(1, 1)
    return qc

TERMS = ("XX", "ZB")
ARMSET = ("qet", "coinfrozen", "nomeasure")

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
    print(f"Exp195c selftest | exact: baseline {d['baseline_EB']:.4f}, dE_qet {d['dE_qet']:+.4f}, "
          f"dE_coinfrozen {d['dE_coinfrozen']:+.4f}, dE_nomeasure {d['dE_nomeasure']:+.4f}, "
          f"GAP {d['gap']:+.4f}")
    assert abs(d["dE_qet"] - (-0.1028)) < 1e-3 and abs(d["gap"] - (-0.2001)) < 1e-3, "derivation drift"
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 200000; cache = {}
    def get(name):
        if name not in cache:
            cache[name] = sim.run(circuit(name), shots=shots).result().get_counts()
        return cache[name]
    r = analyze(get); base = d["baseline_EB"]
    for arm in ARMSET:
        print(f"  {arm:>10}: <Z_B>={r[arm]['ZB']:+.4f} <X_A X_B>={r[arm]['XX']:+.4f} "
              f"E_B={r[arm]['E_B']:+.4f}  Delta={r[arm]['E_B']-base:+.4f}")
    gap = r["qet"]["E_B"] - r["coinfrozen"]["E_B"]
    print(f"  circuit GAP (qet - coinfrozen) = {gap:+.4f} (exact {d['gap']:+.4f})")
    assert abs((r["qet"]["E_B"] - base) - d["dE_qet"]) < 0.01, "qet arm off exact"
    assert abs((r["coinfrozen"]["E_B"] - base) - d["dE_coinfrozen"]) < 0.015, "coinfrozen off exact"
    assert abs((r["nomeasure"]["E_B"] - base) - d["dE_nomeasure"]) < 0.015, "nomeasure off exact"
    assert abs(gap - d["gap"]) < 0.02, "gap off exact"
    print("SELFTEST PASS: gate-identical arms reproduce the exact -0.2001 information gap; "
          "both no-information arms PAY. Cleared to fly.")

def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    d = derive()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = [f"{arm}_{t}" for arm in ARMSET for t in TERMS]
    circuits = [transpile(circuit(n), backend=backend, optimization_level=3) for n in names]
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    man = {"exp": "195c", "slug": "energy_teleport", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names, "baseline_EB": d["baseline_EB"],
           "h": H_, "k": K_, "theta": BTHETA, "exact": d,
           "prereg": {"primary": "E_B(qet) - E_B(coinfrozen) <= -0.10 at >=5 sigma; band "
                                 "[-0.30, -0.10] (exact -0.2001; lambda~0.89 -> ~-0.18)",
                      "falsifiers": "dE(coinfrozen) > 0 and dE(nomeasure) > 0, band [+0.02, +0.50]",
                      "secondary_labeled": "absolute dE(qet) reported, not verdict-gating"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp195c_energy_teleport_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) | gap target {d['gap']:+.4f}")

def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp195c_energy_teleport_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; regs = list(r0.data.keys())
        if len(regs) != 1: raise RuntimeError(f"unexpected multi-register result for {name}: {regs}")
        raw[name] = getattr(r0.data, regs[0]).get_counts()
    r = analyze(lambda n: raw[n]); base = man["baseline_EB"]; shots = man["shots"]
    seE = np.sqrt((H_**2 + K_**2) / shots); se_gap = np.sqrt(2) * seE
    gap = r["qet"]["E_B"] - r["coinfrozen"]["E_B"]; z = -gap / se_gap
    d_qet, d_coin, d_fix = (r[a]["E_B"] - base for a in ARMSET)
    print(f"Exp195c decode | job {man['job_id']} | baseline {base:.4f} | exact gap {man['exact']['gap']:+.4f}")
    for arm in ARMSET:
        print(f"  {arm:>10}: <Z_B>={r[arm]['ZB']:+.3f} <X_A X_B>={r[arm]['XX']:+.3f}  "
              f"E_B={r[arm]['E_B']:+.4f}  Delta={r[arm]['E_B']-base:+.4f}")
    p_ok = -0.30 <= gap <= -0.10 and z >= 5
    f_ok = (0.02 <= d_coin <= 0.50) and (0.02 <= d_fix <= 0.50)
    print(f"\nPRIMARY: GAP(qet - coinfrozen) = {gap:+.4f} ({z:.0f} sigma; SE {se_gap:.4f}) — "
          f"identical circuits, only the bit differs")
    print(f"FALSIFIERS: coinfrozen {d_coin:+.4f} | nomeasure {d_fix:+.4f} (both must pay)")
    print(f"SECONDARY (labeled): absolute dE(qet) = {d_qet:+.4f} (noise-heated; not verdict-gating)")
    ok = p_ok and f_ok
    print(f"VERDICT: {'INFORMATION MOVES ENERGY — the informed bit extracts what the coin bit cannot, in gate-identical circuits' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": r, "baseline": base, "gap": float(gap),
               "sigma": float(z), "delta_qet": float(d_qet), "delta_coinfrozen": float(d_coin),
               "delta_nomeasure": float(d_fix), "primary_ok": bool(p_ok),
               "falsifier_ok": bool(f_ok), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp195c_energy_teleport_decode.json"), "w"), indent=1)
    print("-> results/exp195c_energy_teleport_decode.json")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=16000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
