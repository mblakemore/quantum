#!/usr/bin/env python3
"""Exp248 — THE CLOAKING DEVICE (H7-P2): QEC-as-privacy, certified on silicon.

CLAIM: every single physical qubit of a [[4,2,2]]-encoded logical state carries ~zero information
about the logical bit (Holevo chi_single < 0.01 bit), while the logical readout stays high-fidelity —
and the cloak measurably BREAKS at two-qubit probes (the d=2 edge: the Z0Z2 pair carries logical Z).

States (one logical qubit probed; the other logical + gauge pinned by construction):
  S1 |0L> = GHZ4 = (|0000>+|1111>)/sqrt2          chain encode: h(0) cx(0,1) cx(1,2) cx(2,3)
  S2 |1L> = X̄1 S1 = (|1100>+|0011>)/sqrt2        S1 then x(0) x(1)    [X̄1 = X0X1]
  S3 |+L> = Bell+(0,1) ⊗ Bell+(2,3)
  S4 |-L> = Bell-(0,1) ⊗ Bell-(2,3)
Logical readout: Z̄1 = Z0Z2 (S1:+1, S2:-1 in Z pubs); X̄1 = X0X1 (S3:+1, S4:-1 in X pubs).
Stabilizer postselection per basis: Z-pubs on ZZZZ=+1, X-pubs on XXXX=+1, Y-pubs on YYYY=+1.
Pubs: 4 states x 3 bases (all qubits measured in the same basis -> every single AND pair marginal from
the same counts) + 2 readout-mitigation cals (|0000>,|1111>) = 14 pubs x 8000 shots. STATIC. ~3 CZ max.
Substrate claude-fable-5, Whisper C4952. Pre-reg frozen separately before submission."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from qiskit import QuantumCircuit

SHOTS = 8000
STATES = ("S1_0L", "S2_1L", "S3_pL", "S4_mL")
BASES = ("Z", "X", "Y")

def prep(state):
    qc = QuantumCircuit(4, 4)
    if state == "S1_0L":
        qc.h(0); qc.cx(0, 1); qc.cx(1, 2); qc.cx(2, 3)
    elif state == "S2_1L":
        qc.h(0); qc.cx(0, 1); qc.cx(1, 2); qc.cx(2, 3); qc.x(0); qc.x(1)
    elif state == "S3_pL":
        qc.h(0); qc.cx(0, 1); qc.h(2); qc.cx(2, 3)
    elif state == "S4_mL":
        qc.h(0); qc.cx(0, 1); qc.z(0); qc.h(2); qc.cx(2, 3); qc.z(2)
    return qc

def pub(state, basis):
    qc = prep(state)
    qc.barrier()
    for q in range(4):
        if basis == "X": qc.h(q)
        elif basis == "Y": qc.sdg(q); qc.h(q)
        qc.measure(q, q)
    return qc

def build():
    pubs = [(f"{s}_{b}", pub(s, b), SHOTS) for s in STATES for b in BASES]
    for lab, bits in (("cal0", "0000"), ("cal1", "1111")):
        qc = QuantumCircuit(4, 4)
        if lab == "cal1":
            for q in range(4): qc.x(q)
        for q in range(4): qc.measure(q, q)
        pubs.append((lab, qc, SHOTS))
    return pubs

# ---------------- grading (frozen with the builder) ----------------

def _postselect(counts, basis):
    """Keep shots with the basis-compatible stabilizer = +1 (even parity of the 4 outcome bits)."""
    kept = {}
    for k, v in counts.items():
        if k.count("1") % 2 == 0:
            kept[k] = v
    return kept

def _marginals(counts):
    """Per-qubit <sigma> and per-pair <sigma sigma> from 4-bit counts (qiskit key: q3q2q1q0)."""
    n = sum(counts.values())
    s = np.zeros(4); ss = np.zeros((4, 4))
    for k, v in counts.items():
        bits = [1 - 2 * int(k[3 - q]) for q in range(4)]   # 0->+1, 1->-1
        for q in range(4):
            s[q] += v * bits[q]
            for r in range(q + 1, 4):
                ss[q, r] += v * bits[q] * bits[r]
    return s / n, ss / n, n

def _entropy(rho):
    ev = np.clip(np.linalg.eigvalsh(rho), 1e-12, 1)
    ev = ev / ev.sum()
    return float(-(ev * np.log2(ev)).sum())

def _rho(x, y, z):
    r = np.sqrt(x * x + y * y + z * z)
    if r > 1: x, y, z = x / r, y / r, z / r    # clip to Bloch ball
    return 0.5 * np.array([[1 + z, x - 1j * y], [x + 1j * y, 1 - z]])

def grade(counts_by_label, out):
    # readout mitigation: per-qubit p(read 1|prep 0), p(read 0|prep 1)
    m0, _, n0 = _marginals(counts_by_label["cal0"]); m1, _, n1 = _marginals(counts_by_label["cal1"])
    eps0 = (1 - m0) / 2   # P(read 1 | 0)
    eps1 = (1 + m1) / 2   # P(read 0 | 1)
    def mitigate(v, q):   # invert symmetric-ish readout on an expectation value
        a = 1 - eps0[q] - eps1[q]
        return float(np.clip(v / a if a > 0.1 else v, -1, 1))
    # single-qubit tomograms per state (postselected per basis), raw + mitigated
    chi_single_raw, chi_single_mit = [], []
    tomo = {}
    for q in range(4):
        rhos_raw, rhos_mit = [], []
        for s in STATES:
            comp = {}
            for b in BASES:
                kept = _postselect(counts_by_label[f"{s}_{b}"], b)
                m, _, _ = _marginals(kept)
                comp[b] = m[q]
            rhos_raw.append(_rho(comp["X"], comp["Y"], comp["Z"]))
            rhos_mit.append(_rho(mitigate(comp["X"], q), mitigate(comp["Y"], q), mitigate(comp["Z"], q)))
            tomo[f"q{q}_{s}"] = {b: round(float(comp[b]), 4) for b in BASES}
        for rhos, acc in ((rhos_raw, chi_single_raw), (rhos_mit, chi_single_mit)):
            avg = sum(rhos) / 4
            acc.append(_entropy(avg) - float(np.mean([_entropy(r) for r in rhos])))
    # pair leak: classical MI of pair outcomes about the logical bit, per basis-matched pair
    # (d=2 edge: Z-basis pair (0,2) distinguishes S1/S2 via Z0Z2; X-basis pair (0,1) distinguishes S3/S4)
    def pair_mi(sA, sB, basis, qa, qb):
        dists = []
        for s in (sA, sB):
            kept = _postselect(counts_by_label[f"{s}_{basis}"], basis)
            d = np.zeros(4); n = 0
            for k, v in kept.items():
                idx = 2 * int(k[3 - qa]) + int(k[3 - qb]); d[idx] += v; n += v
            dists.append(d / n)
        p = 0.5 * (dists[0] + dists[1])
        mi = 0.0
        for i in range(4):
            for j, d in enumerate(dists):
                if d[i] > 0:
                    mi += 0.5 * d[i] * np.log2(d[i] / p[i])
        return float(mi)
    pair_edge = {"Z02_S1S2": pair_mi("S1_0L", "S2_1L", "Z", 0, 2),
                 "X01_S3S4": pair_mi("S3_pL", "S4_mL", "X", 0, 1)}
    # logical readout fidelity (postselected)
    def logi(s, basis, qa, qb, want):
        kept = _postselect(counts_by_label[f"{s}_{basis}"], basis)
        _, ss, n = _marginals(kept)
        return float((1 + want * ss[qa, qb]) / 2), n
    F = {"S1_Zbar": logi("S1_0L", "Z", 0, 2, +1), "S2_Zbar": logi("S2_1L", "Z", 0, 2, -1),
         "S3_Xbar": logi("S3_pL", "X", 0, 1, +1), "S4_Xbar": logi("S4_mL", "X", 0, 1, -1)}
    acc = {f"{s}_{b}": round(sum(_postselect(counts_by_label[f'{s}_{b}'], b).values()) /
                             sum(counts_by_label[f"{s}_{b}"].values()), 3) for s in STATES for b in BASES}
    chi_max_mit = max(chi_single_mit); chi_max_raw = max(chi_single_raw)
    Fmin = min(v[0] for v in F.values())
    edge_min = min(pair_edge.values())
    # FROZEN rule: PASS-CLOAK if chi_max_mit < 0.01 and Fmin > 0.9 ; PASS-EDGE if edge_min > 5*chi_max_mit
    cloak = chi_max_mit < 0.01 and Fmin > 0.9
    edge = edge_min > 5 * max(chi_max_mit, 1e-4)
    verdict = ("PASS-CLOAK+EDGE" if cloak and edge else
               "PASS-CLOAK" if cloak else "CLOAK-LEAK" if Fmin > 0.9 else "READOUT-FAIL")
    out.update({"chi_single_mit_bits": [round(c, 5) for c in chi_single_mit],
                "chi_single_raw_bits": [round(c, 5) for c in chi_single_raw],
                "chi_max_mit": round(chi_max_mit, 5), "chi_max_raw": round(chi_max_raw, 5),
                "pair_edge_bits": {k: round(v, 4) for k, v in pair_edge.items()},
                "F_logical": {k: round(v[0], 4) for k, v in F.items()}, "F_min": round(Fmin, 4),
                "acceptance": acc, "readout_eps": [round(float(e), 4) for e in (eps0 + eps1) / 2],
                "tomo": tomo, "verdict": verdict})
    print(f"  chi_single (mitigated, bits): {[round(c,5) for c in chi_single_mit]}  max={chi_max_mit:.5f} (<0.01)")
    print(f"  pair edge (bits): {pair_edge}  (rule: min > 5*chi_max)")
    print(f"  F_logical: { {k: round(v[0],4) for k,v in F.items()} }  min={Fmin:.4f} (>0.9)")
    print(f"  VERDICT: {verdict}")
    return verdict

def selftest():
    from qiskit.quantum_info import Statevector, partial_trace
    # per-qubit reduced states identical (=I/2) across the 4 states; logical readouts exact
    for q in range(4):
        rhos = [partial_trace(Statevector.from_instruction(prep(s)), [i for i in range(4) if i != q]).data
                for s in STATES]
        for r in rhos:
            assert np.allclose(r, np.eye(2) / 2, atol=1e-9), (q, r)
    counts = {}
    for s in STATES:
        for b in BASES:
            qc = pub(s, b)
            sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
            counts[f"{s}_{b}"] = {k: int(round(v * SHOTS)) for k, v in sv.probabilities_dict().items() if v > 1e-9}
    counts["cal0"] = {"0000": SHOTS}; counts["cal1"] = {"1111": SHOTS}
    out = {}
    v = grade(counts, out)
    assert out["chi_max_raw"] < 1e-6 and out["F_min"] > 0.9999 and v == "PASS-CLOAK+EDGE", (v, out["chi_max_raw"], out["F_min"])
    assert min(out["pair_edge_bits"].values()) > 0.9, out["pair_edge_bits"]  # ideal pair probes carry ~1 bit
    print("SELFTEST PASS: per-qubit reductions = I/2 for all 4 logical states (chi=0), logical readouts exact,")
    print("pair probes carry ~1 bit (the d=2 edge). The cloak claim is well-posed; hardware decides the leak.")

def submit(backend_name):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(); backend = svc.backend(backend_name)
    pubs = build()
    circs = [transpile(qc, backend, optimization_level=3, seed_transpiler=11) for _, qc, _ in pubs]
    n2 = [sum(1 for i in c.data if len(i.qubits) == 2) for c in circs]
    assert max(n2) <= 6, n2   # chain encodes: <=3 abstract, allow routing slack
    print(f"DEPTH CHECK: {len(circs)} pubs, transpiled 2q {min(n2)}-{max(n2)}")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(c,) for c in circs], shots=SHOTS)
    man = {"job_id": job.job_id(), "backend": backend_name, "labels": [l for l, _, _ in pubs]}
    json.dump(man, open(os.path.join(QROOT, "results", "exp248_cloak_manifest.json"), "w"), indent=1)
    print("handle persisted:", man["job_id"])
    res = job.result()
    counts = {lab: res[i].data.c.get_counts() if hasattr(res[i].data, "c") else
              {k: v for k, v in res[i].data.meas.get_counts().items()} for i, (lab, _, _) in enumerate(pubs)}
    out = {"job_id": man["job_id"], "backend": backend_name, "substrate": "claude-fable-5"}
    grade(counts, out)
    json.dump({"card": out, "counts": counts},
              open(os.path.join(QROOT, "results", "exp248_cloak_result.json"), "w"), indent=1, default=float)
    print("card -> results/exp248_cloak_result.json")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--submit":
        submit(sys.argv[2] if len(sys.argv) > 2 else "ibm_fez")
    else:
        selftest()
