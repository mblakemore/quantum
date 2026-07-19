#!/usr/bin/env python3
"""Exp182 — THE SCALING LAW: n=3 distributed Bernstein-Vazirani. C4870.
Upgrades Exp181's single per-gate ratio into a dose-response: 8 hidden strings spanning
w = 0..3 teleported oracle gates. Constant per-gate cost r (P ~ P0 * r^w) => a LAW with an
extrapolation license (r^10). Zero-feedforward architecture throughout (X-corr = global phase
on the |-> ancilla; Z-corr = decode XOR); algebra is n-independent, selftest reproves at n=3.

Layout: data q0-q2, ancilla q3, e-bits (q4,q5) (q6,q7) (q8,q9).
clbits: c0-c2 = m1-m3 (q0-q2), c3-c5 = z1-z3 (q5,q7,q9), c6-c8 = e1 discards, c9 = ancilla.
Arms: local (8 strings) | dist (8) | noresource (weight reps 000,001,011,111).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

N = 3
STRINGS = [format(k, "03b") for k in range(8)]          # 's3s2s1'
NR_REPS = ("000", "001", "011", "111")
EBIT = {1: (4, 5), 2: (6, 7), 3: (8, 9)}


def _bits(s):
    return {i: int(s[N - i]) for i in (1, 2, 3)}


def bv_circuit(arm, s):
    qc = QuantumCircuit(10, 10)
    bits = _bits(s)
    for q in range(N): qc.h(q)                          # Alice data |+>
    qc.x(3); qc.h(3)                                    # Bob ancilla |->
    if arm == "dist":
        for i in (1, 2, 3):
            e1, e2 = EBIT[i]
            qc.h(e1); qc.cx(e1, e2)                     # pre-shared e-bits (all 3, uniform)
    qc.barrier()
    for i in (1, 2, 3):                                 # oracle: CNOT(a_i -> anc) if s_i = 1
        if not bits[i]:
            continue
        a = i - 1
        if arm == "local":
            qc.cx(a, 3)
        else:
            e1, e2 = EBIT[i]
            qc.cx(a, e1)                                # Alice half (e1 measured later; x discarded)
            qc.cx(e2, 3)                                # Bob half
            qc.h(e2)                                    # e2 Z-measure -> z_i -> decode XOR
    qc.barrier()
    for q in range(N): qc.h(q)                          # BV final Hadamards
    qc.barrier()                                        # ONE merged measurement layer
    for q in range(N): qc.measure(q, q)                 # m_i -> c0..c2
    for i in (1, 2, 3): qc.measure(EBIT[i][1], 2 + i)   # z_i -> c3..c5
    for i in (1, 2, 3): qc.measure(EBIT[i][0], 5 + i)   # e1 discards -> c6..c8
    qc.measure(3, 9)                                    # ancilla discard
    return qc


def decode_shot(bstr, arm, s):
    b = bstr.replace(" ", "")
    bits = _bits(s)
    m = [int(b[-1]), int(b[-2]), int(b[-3])]            # m1, m2, m3
    z = [int(b[-4]), int(b[-5]), int(b[-6])]            # z1, z2, z3
    if arm != "local":
        for i in (1, 2, 3):
            if bits[i]:
                m[i - 1] ^= z[i - 1]
    return f"{m[2]}{m[1]}{m[0]}"                        # 's3s2s1'


def analyze(get, shots, arms_strings):
    out = {}
    for arm, strs in arms_strings.items():
        per = {}
        for s in strs:
            tallies = {}
            for bstr, n in get(arm, s).items():
                d = decode_shot(bstr, arm, s)
                tallies[d] = tallies.get(d, 0) + n
            per[s] = {"P": float(tallies.get(s, 0) / shots),
                      "modal": max(tallies, key=tallies.get)}
            per[s]["modal_ok"] = per[s]["modal"] == s
        out[arm] = per
    return out


def weight_means(per):
    Pw = {}
    for w in range(4):
        vals = [per[s]["P"] for s in per if s.count("1") == w]
        if vals: Pw[w] = float(np.mean(vals))
    return Pw


def scaling(Pw, shots, n_per_w):
    """Successive ratios + pooled log-linear r-hat (weights by string count)."""
    se_P = lambda p, k: np.sqrt(max(p * (1 - p), 1e-9) / (shots * k))
    ratios, sig = {}, {}
    for w in (1, 2, 3):
        r = Pw[w] / Pw[w - 1]
        se_r = r * np.sqrt((se_P(Pw[w], n_per_w[w]) / Pw[w]) ** 2 +
                           (se_P(Pw[w - 1], n_per_w[w - 1]) / Pw[w - 1]) ** 2)
        ratios[w] = (float(r), float(se_r))
    ws = np.array([0, 1, 2, 3], dtype=float)
    logP = np.array([np.log(Pw[w]) for w in range(4)])
    wts = np.array([n_per_w[w] for w in range(4)], dtype=float)
    A = np.vstack([np.ones_like(ws), ws]).T
    W = np.diag(wts)
    coef = np.linalg.solve(A.T @ W @ A, A.T @ W @ logP)
    r_hat = float(np.exp(coef[1]))
    rs = [ratios[w][0] for w in (1, 2, 3)]
    ses = [ratios[w][1] for w in (1, 2, 3)]
    consistent = all(abs(rs[i] - rs[j]) <= 2 * np.sqrt(ses[i] ** 2 + ses[j] ** 2)
                     for i in range(3) for j in range(i + 1, 3))
    return {"ratios": {w: {"r": ratios[w][0], "se": ratios[w][1]} for w in ratios},
            "r_hat": r_hat, "r_hat_pow10": float(r_hat ** 10), "consistent_2sigma": bool(consistent)}


ARMS_STRINGS = {"local": STRINGS, "dist": STRINGS, "noresource": list(NR_REPS)}
N_PER_W = {0: 1, 1: 3, 2: 3, 3: 1}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, s):
        if (arm, s) not in cache:
            cache[(arm, s)] = sim.run(bv_circuit(arm, s), shots=shots).result().get_counts()
        return cache[(arm, s)]
    r = analyze(get, shots, ARMS_STRINGS)
    print("Exp182 selftest (noiseless Aer)")
    for arm, strs in ARMS_STRINGS.items():
        row = "  ".join(f"{s}:{r[arm][s]['P']:.3f}" for s in strs)
        print(f"  {arm:>10}: {row}")
    for arm in ("local", "dist"):
        for s in STRINGS:
            assert r[arm][s]["P"] > 0.999, f"{arm}/{s} must be exact (n=3 deferral algebra)"
    floors = {"000": 1.0, "001": 0.5, "011": 0.25, "111": 0.125}
    for s, f in floors.items():
        assert abs(r["noresource"][s]["P"] - f) < 0.03, f"noresource {s} must sit at {f}"
    print("SELFTEST PASS: n=3 deferral algebra exact (all 8 programs, 0-3 teleported gates); "
          "falsifier floors at 1/2^w. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm, strs in ARMS_STRINGS.items():
        for s in strs:
            circuits.append(transpile(bv_circuit(arm, s), backend=backend, optimization_level=3))
            order.append([arm, s])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 182, "slug": "dist_bv3", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"primary": "dist > noresource >=3 sigma per weight class; modal 8/8",
                           "scaling": "successive ratios r1,r2,r3 consistent within 2 sigma => constant-cost "
                                      "law; r_hat band 0.93-0.99; report r_hat^10",
                           "bands": "local 0.85-0.99 all; dist P0 0.90-0.99, P1 0.84-0.97, P2 0.78-0.95, "
                                    "P3 0.72-0.93; noresource w1 0.42-0.56, w2 0.19-0.31, w3 0.09-0.17",
                           "failure_mode_named": "monotone ratio degradation > 2 sigma => resource-scale "
                                                 "interaction (routing congestion / e-bit prep crosstalk)"}}
    out = os.path.join(HERE, "..", "results", "exp182_dist_bv3_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp182_dist_bv3_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, s: raw[(arm, s)], shots, ARMS_STRINGS)
    Pw = weight_means(r["dist"]); sc = scaling(Pw, shots, N_PER_W)
    se_P = lambda p, k: np.sqrt(max(p * (1 - p), 1e-9) / (shots * k))
    print(f"Exp182 SCALING LAW decode | job {man['job_id']} | backend {man['backend']}")
    for arm, strs in ARMS_STRINGS.items():
        row = "  ".join(f"{s}:{r[arm][s]['P']:.3f}{'*' if not r[arm][s]['modal_ok'] else ''}" for s in strs)
        print(f"  {arm:>10}: {row}")
    print(f"\nDIST BY WEIGHT: " + "  ".join(f"w={w}: {Pw[w]:.3f}" for w in range(4)))
    print(f"PER-GATE RATIOS: " + "  ".join(
        f"r{w}={sc['ratios'][w]['r']:.3f}±{sc['ratios'][w]['se']:.3f}" for w in (1, 2, 3)))
    print(f"POOLED r-hat = {sc['r_hat']:.3f} -> extrapolation r^10 = {sc['r_hat_pow10']:.2f}")
    print(f"CONSTANT-COST LAW: {'CONSISTENT (all ratios within 2 sigma)' if sc['consistent_2sigma'] else 'VIOLATED — ratio drift (see named failure modes)'}")
    nrw = {s.count("1"): r["noresource"][s]["P"] for s in NR_REPS}
    sigs = {}
    for w in (1, 2, 3):
        d, n_ = Pw[w], nrw[w]
        sigs[w] = (d - n_) / np.sqrt(se_P(d, N_PER_W[w]) ** 2 + se_P(n_, 1) ** 2)
    modal8 = all(r["dist"][s]["modal_ok"] for s in STRINGS)
    print(f"VS FALSIFIER: " + "  ".join(f"w={w}: +{sigs[w]:.0f}σ" for w in (1, 2, 3)) +
          f" | modal {'8/8' if modal8 else 'FAILED'}")
    ok = all(sigs[w] >= 3 for w in sigs) and modal8
    print(f"PRIMARY: {'HELD' if ok else 'NOT HELD'} | scaling: "
          f"{'LAW (constant per-gate cost ' + format(sc['r_hat'], '.3f') + ')' if sc['consistent_2sigma'] else 'drift — resource-scale interaction'}")
    out = {"job_id": man["job_id"], "results": r, "P_by_weight": Pw, "scaling": sc,
           "sigmas_vs_floor": {w: float(v) for w, v in sigs.items()},
           "modal_8of8": bool(modal8), "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp182_dist_bv3_decode.json"), "w"), indent=1)
    print("-> results/exp182_dist_bv3_decode.json")


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
