#!/usr/bin/env python3
"""Exp199 — THE SILENT ROTATION: coherent-error spectroscopy of the [[4,2,2]] shield. C4892.

Perturbation instrument #2 (after Exp198's dial): inject a GLOBAL coherent phase error
Rz(theta) on all 4 physical qubits of a [[4,2,2]] block holding |+bar +bar> (the realistic
calibration-error model — every qubit over-rotated by the same angle), sweep theta, read in
the X basis, and measure what the shield catches vs what sneaks through.

Exact code-space algebra (u=cos^2(theta/2), v=sin^2(theta/2)):
  COHERENT (amplitudes interfere):
    reject  R = 4uv(u-v)^2        -> ZERO at theta=pi/2 (w1 and w3 cancel exactly)
    silent  T = 12 u^2 v^2         (all six w2 errors are LOGICAL; amplitudes add)
    accept  A = 1 - R              -> returns to 1.0 at pi/2 (w4 = stabilizer adds BACK)
  TWIRLED (same per-qubit error probability p=v, incoherent via coin-CZ):
    reject  R = 4uv(u^2+v^2)/(u+v)... = 4u^3v+4uv^3;  silent T = 6 u^2 v^2;  A = 1-R
  => amplification T_coh/T_inc = 2 exactly at every dose, and THE BLIND SPOT at pi/2:
     coherent arm accepts 100% of shots while 75% carry silent logical corruption; the
     identical incoherent dose is rejected half the time. Acceptance NON-MONOTONIC
     (0.75 at pi/4 -> 1.0 at pi/2) — the smoking gun of coherence; incoherent falls
     monotonically. This is WHY real QEC underperforms Pauli-noise models, measured.

Twirl construction (198's entangle-to-decohere): per data qubit, coin Ry(2 asin(sin(th/2)))
then CZ(coin->data), coin measured and IGNORED in logicals (marginal = gauge). Within each
arm the gate burden is dose-independent (Rz is virtual; Ry cost is angle-independent);
cross-arm burden differs by 4 Ry + 4 CZ — bias INFLATES the twirled arm's silent rate,
pushing the measured amplification ratio DOWN: the >=1.5 threshold is conservative.

Z-NULL: |0bar 0bar> + max dose + Z readout — phase errors are invisible in the Z basis
(acceptance high, Zbar logicals intact): the damage is basis-specific, as physics requires.

BUDGET CHECK (C4887 rule): observables are rates with O(0.1-0.75) contrasts vs Exp189
baseline (acceptance 0.966, escape 0.02 at zero dose) — margins >> baseline noise. Feasible.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
DOSES = (0.0, 0.125, 0.25, 0.375, 0.5)       # theta / pi
ARMS = ("coh", "twl")                          # + znull at max dose


def circuit(arm, t):
    th = t * PI
    if arm == "znull":
        qc = QuantumCircuit(4, 4)
        qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)   # |0bar 0bar> = GHZ4
        qc.barrier()
        for q in range(4): qc.rz(th, q)
        qc.barrier()
        for q in range(4): qc.measure(q, q)               # Z readout
        return qc
    n = 4 if arm == "coh" else 8
    qc = QuantumCircuit(n, n)
    qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)       # GHZ4 = |0bar 0bar>
    for q in range(4): qc.h(q)                            # H^4 -> |+bar +bar>
    qc.barrier()
    if arm == "coh":
        for q in range(4): qc.rz(th, q)                   # the coherent global error
    else:
        a = 2 * np.arcsin(np.sin(th / 2))                 # coin: P(1) = sin^2(th/2)
        for q in range(4):
            qc.ry(a, 4 + q); qc.cz(4 + q, q)              # incoherent Z-channel, same p
    qc.barrier()
    for q in range(4): qc.h(q)                            # X-basis readout
    for q in range(n): qc.measure(q, q)
    return qc


def exact(t):
    u = np.cos(t * PI / 2) ** 2; v = np.sin(t * PI / 2) ** 2
    Rc = 4 * u * v * (u - v) ** 2; Tc = 12 * u ** 2 * v ** 2
    Ri = 4 * u ** 3 * v + 4 * u * v ** 3; Ti = 6 * u ** 2 * v ** 2
    return {"coh": {"A": 1 - Rc, "T": Tc, "L": Tc / (1 - Rc) if Rc < 1 else 0.0},
            "twl": {"A": 1 - Ri, "T": Ti, "L": Ti / (1 - Ri) if Ri < 1 else 0.0}}


def _stats(counts, arm):
    acc = rej = bad = 0; coin1 = 0; ncoinbits = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(len(b))]
        if arm == "twl":
            coin1 += n * sum(v[4:8]); ncoinbits += 4 * n
        par = v[0] ^ v[1] ^ v[2] ^ v[3]
        if par:
            rej += n; continue
        acc += n
        l1 = v[0] ^ v[1]; l2 = v[0] ^ v[2]                # Xbar1, Xbar2 (or Zbar for znull)
        if arm == "znull":
            l1 = v[0] ^ v[2]; l2 = v[0] ^ v[1]
        if l1 or l2: bad += n
    tot = acc + rej
    return {"A": acc / tot, "R": rej / tot, "L": bad / acc if acc else 0.0,
            "T": bad / tot, "n_acc": acc,
            "coin_p1": coin1 / ncoinbits if ncoinbits else None}


def analyze(get):
    r = {}
    for arm in ARMS:
        r[arm] = {t: _stats(get(arm, t), arm) for t in DOSES}
    r["znull"] = {0.5: _stats(get("znull", 0.5), "znull")}
    return r


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 100000; cache = {}
    def get(arm, t):
        k = (arm, t)
        if k not in cache: cache[k] = sim.run(circuit(arm, t), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    print("Exp199 selftest | exact blind spot at pi/2: coh A=1.00 L=0.75 R=0.00; twl A=0.50 L=0.75")
    for t in DOSES:
        e = exact(t)
        line = f"  t={t:5}: "
        for arm in ARMS:
            m = r[arm][t]
            line += (f"{arm} A={m['A']:.3f}/{e[arm]['A']:.3f} L={m['L']:.3f}/{e[arm]['L']:.3f}  ")
            assert abs(m["A"] - e[arm]["A"]) < 0.02 and abs(m["L"] - e[arm]["L"]) < 0.02, f"{arm}@{t}"
        print(line)
    zn = r["znull"][0.5]
    print(f"  znull(pi/2, Z basis): A={zn['A']:.3f} L={zn['L']:.3f} (phase errors invisible in Z)")
    assert zn["A"] > 0.98 and zn["L"] < 0.02, "znull must be clean"
    m = r["coh"]
    assert m[0.5]["A"] - m[0.25]["A"] > 0.15, "acceptance must RISE back toward the blind spot"
    tc, ti = m[0.5]["T"], r["twl"][0.5]["T"]
    print(f"  amplification at pi/2: T_coh/T_twl = {tc/ti:.3f} (exact 2.0)")
    assert abs(tc / ti - 2.0) < 0.15, "coherent amplification must be 2x"
    print("SELFTEST PASS: blind spot exact (accept-all yet 75% corrupted), twirled arm sees the "
          "same dose, amplification 2x, acceptance non-monotonic, Z-null clean. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for t in DOSES:
            circuits.append(transpile(circuit(arm, t), backend=backend, optimization_level=3))
            order.append([arm, t])
    circuits.append(transpile(circuit("znull", 0.5), backend=backend, optimization_level=3))
    order.append(["znull", 0.5])
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    man = {"exp": 199, "slug": "silent_rotation", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order,
           "exact": {str(t): exact(t) for t in DOSES},
           "prereg": {"anchors": "theta=0: A >= 0.90 and L <= 0.05, both arms",
                      "blind_spot": "coh @ pi/2: R <= 0.10 AND L >= 0.55 (exact 0 / 0.75)",
                      "twirl_sees": "twl @ pi/2: R >= 0.35 (exact 0.50) — same dose, caught",
                      "amplification": "T_coh/T_twl in [1.5, 2.6] at doses 1/4, 3/8, 1/2 "
                                       "(exact 2.0; twirl-arm burden biases DOWN — conservative)",
                      "nonmonotone": "A_coh(pi/2) - A_coh(pi/4) > 0 at >=3 sigma (the return "
                                     "to blindness; twirled acceptance must NOT rise)",
                      "znull": "Z-basis @ pi/2: A >= 0.90, L <= 0.05 (phase errors invisible in Z)",
                      "gauge": "twirl coin marginal P(1) = sin^2(theta/2) +- 0.05 per dose",
                      "budget_check": "rate contrasts 0.1-0.75 vs 189 baseline (A 0.966, esc 0.02)"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp199_silent_rotation_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots)")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp199_silent_rotation_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, (arm, t) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, float(t))] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, t: raw[(arm, float(t))])
    print(f"Exp199 THE SILENT ROTATION decode | job {man['job_id']}")
    for t in DOSES:
        e = man["exact"][str(t)]
        c, w = r["coh"][t], r["twl"][t]
        print(f"  t={t:5}: coh A={c['A']:.3f} L={c['L']:.3f} T={c['T']:.3f} (exA {e['coh']['A']:.2f} exL {e['coh']['L']:.2f}) | "
              f"twl A={w['A']:.3f} L={w['L']:.3f} T={w['T']:.3f} coinP1={w['coin_p1']:.3f}")
    zn = r["znull"][0.5]
    c0, w0 = r["coh"][0.0], r["twl"][0.0]
    cb, wb = r["coh"][0.5], r["twl"][0.5]
    a_ok = c0["A"] >= 0.90 and c0["L"] <= 0.05 and w0["A"] >= 0.90 and w0["L"] <= 0.05
    blind_ok = cb["R"] <= 0.10 and cb["L"] >= 0.55
    twirl_ok = wb["R"] >= 0.35
    ratios = {t: r["coh"][t]["T"] / r["twl"][t]["T"] if r["twl"][t]["T"] > 0 else None
              for t in (0.25, 0.375, 0.5)}
    amp_ok = all(v is not None and 1.5 <= v <= 2.6 for v in ratios.values())
    dA = cb["A"] - r["coh"][0.25]["A"]
    seA = np.sqrt(sum(r["coh"][t]["A"] * (1 - r["coh"][t]["A"]) / shots for t in (0.25, 0.5)))
    nm_ok = dA > 0 and dA / seA >= 3 and (wb["A"] - r["twl"][0.25]["A"]) < 2 * seA
    zn_ok = zn["A"] >= 0.90 and zn["L"] <= 0.05
    coin_ok = all(abs(r["twl"][t]["coin_p1"] - np.sin(t * PI / 2) ** 2) <= 0.05 for t in DOSES)
    print(f"\nANCHORS (t=0): coh A={c0['A']:.3f} L={c0['L']:.3f} | twl A={w0['A']:.3f} L={w0['L']:.3f} "
          f"{'OK' if a_ok else 'CHECK'}")
    print(f"THE BLIND SPOT (pi/2): shield rejects {cb['R']:.3f} of shots while {cb['L']:.3f} of "
          f"accepted are logically corrupted {'— BLIND AND WRONG, as coherence demands' if blind_ok else 'CHECK'}")
    print(f"TWIRLED CONTRAST: same dose incoherent -> rejected {wb['R']:.3f} "
          f"{'(the shield SEES stochastic errors)' if twirl_ok else 'CHECK'}")
    print(f"AMPLIFICATION T_coh/T_twl: " + ", ".join(f"{t}: {v:.2f}" for t, v in ratios.items())
          + f" (exact 2.0) {'OK' if amp_ok else 'CHECK'}")
    print(f"NON-MONOTONE: A_coh rises {dA:+.3f} ({dA/seA:.0f} sigma) from pi/4 to pi/2; "
          f"twirled rise {wb['A'] - r['twl'][0.25]['A']:+.3f} {'OK' if nm_ok else 'CHECK'}")
    print(f"Z-NULL: A={zn['A']:.3f} L={zn['L']:.3f} {'(invisible in Z, as physics requires)' if zn_ok else 'CHECK'}")
    print(f"COIN GAUGE: {'OK' if coin_ok else 'CHECK'}")
    ok = a_ok and blind_ok and twirl_ok and amp_ok and nm_ok and zn_ok and coin_ok
    print(f"VERDICT: {'THE SILENT ROTATION — the shield has a measured blind spot: a global coherent phase error at pi/2 passes 100% inspection while corrupting most of what passes, at 2x the stochastic rate — why QEC must fear calibration drift more than noise' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "results": {arm: {str(t): r[arm][t] for t in r[arm]} for arm in r},
               "ratios": {str(t): (float(v) if v else None) for t, v in ratios.items()},
               "anchors_ok": bool(a_ok), "blind_ok": bool(blind_ok), "twirl_ok": bool(twirl_ok),
               "amp_ok": bool(amp_ok), "nonmono_ok": bool(nm_ok), "znull_ok": bool(zn_ok),
               "coin_ok": bool(coin_ok), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp199_silent_rotation_decode.json"), "w"), indent=1)
    print("-> results/exp199_silent_rotation_decode.json")


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
