#!/usr/bin/env python3
"""Exp170 — Floquet SPT edge pi-mode on IBM hardware: "a clock that only ticks at the ends"
(Creator directive 2026-07-18: fly the exotic-phases wing; Whisper on the network wing / Exp163+).

THE PHASE. A driven spin chain can host a symmetry-protected topological (SPT) edge mode with NO
counterpart in the bulk: under a near-pi Ising drive, the BOUNDARY spin locks to a rigid period-2
(pi-quasienergy) response while the BULK, lacking localization, thermalizes and decays. Order that
lives only at the edge, protected by the Ising Z2 symmetry (P = prod X_i). This is NOT the discrete
time crystal (Exp151): the DTC's whole BULK period-doubles rigidly; here the bulk DECAYS and only the
topological edge mode survives. DTC and 1D-SPT are duality partners — the distinctness rests ENTIRELY
on the bulk being trivial, so the bulk-decay is a load-bearing, verified condition, not an assumption.

DRIVE (open chain, N=8): U_F = [prod_i RZZ(2J)] . [prod_i RX(pi(1-eps))],  eps=0.15, J=1.3. From |0..0>
measure per-site A_j(n) = (-1)^n <Z_j(nT)>. Noiseless (verified in --selftest):
  * EDGE (site 0, N-1): A ~ 0.94, RIGID through n=10 (the protected pi-mode).
  * BULK (mid sites):   A decays 1.0 -> ~0.33 by n~8 (trivial, no bulk order).

THE MATCHED CONTROL (is the edge just "fewer neighbors"?). A finite chain's edge spins have one bond
vs the bulk's two, so they dephase slower even with NO topology. The discriminator: add a longitudinal
Z-field (RZ(2h), h=0.5) that BREAKS the Ising Z2. If the persistence is the symmetry-protected pi-mode
it DIES (verified: edge 0.94 -> 0.54, contrast +0.61 -> ~0); if it were a trivial boundary effect it
would survive. Symmetry-break is the axis-matched control (same circuit + one field term).

THE NUMBERS (both baseline-robust CONTRASTS, not absolutes — the C4199 lesson: contrasts cancel the
per-qubit decay a borrowed absolute baseline would mismatch):
  (1) EDGE-BULK contrast in the SPT arm:  <|A_edge|> - <|A_bulk|>  > 0   (the SPT signature)
  (2) SYMMETRY protection: <|A_edge|>_SPT - <|A_edge|>_broken       > 0   (protection is the symmetry)

FENCE (headline): finite chain (N=8), finite coherence — a hardware SIGNATURE of the Floquet-SPT edge
mode, not a thermodynamic-limit proof. Both arms decohere; the claims are RELATIVE (edge vs bulk; SPT
vs symmetry-broken). Uniform J, single drive realization.

Usage:
  python3 exp170_floquet_spt_edge_ember.py --selftest
  python3 exp170_floquet_spt_edge_ember.py --submit [--backend ibm_fez --tmax 10 --shots 4000]
  python3 exp170_floquet_spt_edge_ember.py --decode --manifest ../results/exp170_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

N = 8
EPS = 0.15                 # near-pi flip: theta = pi(1-eps)  (gives the pi edge mode)
J = 1.3                    # uniform Ising coupling (SPT regime; bulk trivial, no disorder)
H_BREAK = 0.5              # symmetry-breaking Z-field for the control (kills the pi-mode)
EDGE_SITES = [0, N - 1]
BULK_SITES = [3, 4]
LATE = None                # set per tmax in metrics


def floquet_spt_circuit(t_periods, h_break=0.0, measure=True):
    theta = np.pi * (1 - EPS)
    qc = QuantumCircuit(N, N if measure else 0)
    for _ in range(t_periods):
        for q in range(N):
            qc.rx(theta, q)                    # imperfect global pi-pulse
        for i in range(N - 1):
            qc.rzz(2 * J, i, i + 1)            # uniform Ising
        if h_break:
            for i in range(N):
                qc.rz(2 * h_break, i)          # symmetry-breaking longitudinal field (control only)
    if measure:
        qc.measure(range(N), range(N))
    return qc


def _z_exact(t, h_break):
    from qiskit.quantum_info import Statevector, SparsePauliOp
    sv = Statevector(floquet_spt_circuit(t, h_break, measure=False))
    out = []
    for i in range(N):
        lbl = ["I"] * N; lbl[N - 1 - i] = "Z"
        out.append(float(np.real(sv.expectation_value(SparsePauliOp("".join(lbl))))))
    return np.array(out)


def _z_counts(counts, shots):
    z = np.zeros(N)
    for bit, c in counts.items():
        b = bit.replace(" ", "")[::-1]
        for i in range(N):
            z[i] += (1 if b[i] == "0" else -1) * c
    return z / shots


def _amp_persite(zt):
    """A_j(n) = (-1)^n <Z_j(n)>, per site."""
    return np.array([((-1) ** t) * zt[t] for t in range(zt.shape[0])])


def _edge_bulk(A, tmax):
    late = range(max(1, tmax - 3), tmax + 1)
    edge = float(np.mean([abs(A[t, s]) for t in late for s in EDGE_SITES]))
    bulk = float(np.mean([abs(A[t, s]) for t in late for s in BULK_SITES]))
    return edge, bulk


def selftest():
    """Noiseless truth-gate — the THREE conditions that make this an SPT and not a DTC or a boundary
    artifact (advisor C4200): (1) edge persists, (2) BULK DECAYS (load-bearing: trivial bulk = not a
    DTC), (3) symmetry-break kills the edge mode (protection is the Z2 symmetry, not fewer neighbors).
    Every assertion can fail."""
    Tm = 10
    A_spt = _amp_persite(np.array([_z_exact(t, 0.0) for t in range(Tm + 1)]))
    A_brk = _amp_persite(np.array([_z_exact(t, H_BREAK) for t in range(Tm + 1)]))
    e_s, b_s = _edge_bulk(A_spt, Tm)
    e_b, b_b = _edge_bulk(A_brk, Tm)
    print(f"Exp170 selftest (noiseless) | N={N} eps={EPS} J={J} h_break={H_BREAK} tmax={Tm}")
    print(f"{'t':>3} {'A_edge0':>8} {'A_edgeN':>8} {'A_bulk3':>8} {'A_bulk4':>8}")
    for t in range(Tm + 1):
        print(f"{t:>3} {A_spt[t,0]:>8.3f} {A_spt[t,N-1]:>8.3f} {A_spt[t,3]:>8.3f} {A_spt[t,4]:>8.3f}")
    print(f"\nSPT arm    : edge_late={e_s:.3f}  bulk_late={b_s:.3f}  edge-bulk contrast={e_s-b_s:+.3f}")
    print(f"broken arm : edge_late={e_b:.3f}  bulk_late={b_b:.3f}  edge-bulk contrast={e_b-b_b:+.3f}")
    print(f"symmetry protection: edge_SPT - edge_broken = {e_s-e_b:+.3f}")
    assert e_s > 0.70, "edge pi-mode must persist in the SPT arm"
    assert b_s < 0.50, "BULK must decay (trivial bulk) — else this is a DTC, not an SPT (load-bearing)"
    assert e_s - b_s > 0.25, "edge-bulk contrast (the SPT signature) too weak"
    assert e_s - e_b > 0.25, "symmetry-break must kill the edge mode (protection is the Z2 symmetry)"
    print("\nSELFTEST PASS: edge persists, bulk decays (not a DTC), symmetry-break destroys the edge "
          "mode (not a boundary artifact). All three SPT conditions hold; the test can fail.")


def submit(backend_name, tmax, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order, meta = [], [], []
    for arm, hb in (("spt", 0.0), ("broken", H_BREAK)):
        for t in range(tmax + 1):
            tqc = transpile(floquet_spt_circuit(t, hb, measure=True), backend=backend, optimization_level=3)
            circuits.append(tqc); order.append([arm, t])
            meta.append({"arm": arm, "t": t, "depth": tqc.depth(), "n2q": tqc.num_nonlocal_gates()})
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 170, "backend": backend_name, "tmax": tmax, "shots": shots, "N": N,
                "eps": EPS, "J": J, "h_break": H_BREAK, "edge_sites": EDGE_SITES, "bulk_sites": BULK_SITES,
                "job_id": job.job_id(), "order": order, "meta": meta,
                "prereg": {"confidence": 0.55,
                           "gate": "edge-bulk contrast (SPT) > 0.15 AND edge_SPT - edge_broken > 0.15",
                           "note": "both are baseline-robust CONTRASTS (C4199): global decay cancels"},
                "note": "Floquet SPT edge pi-mode: spt(h=0) vs symmetry-broken(h=0.5) control; per-site "
                        "A_j=(-1)^n<Z_j>; edge persists + bulk decays + symmetry-break kills = SPT signature"}
    out = os.path.join(HERE, "..", "results", "exp170_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    deep = max(meta, key=lambda m: m["n2q"])
    print(f"submitted {job.job_id()} ({len(circuits)} circuits = 2 arms x t=0..{tmax}, {shots} shots) -> {out}")
    print(f"  deepest: {deep['arm']} t={deep['t']} depth={deep['depth']} 2q={deep['n2q']}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    tmax = man["tmax"]; shots = man["shots"]
    arms = {"spt": {}, "broken": {}}
    for idx, (arm, t) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        arms[arm][t] = _z_counts(getattr(r.data, reg).get_counts(), shots)
    A_spt = _amp_persite(np.array([arms["spt"][t] for t in range(tmax + 1)]))
    A_brk = _amp_persite(np.array([arms["broken"][t] for t in range(tmax + 1)]))
    e_s, b_s = _edge_bulk(A_spt, tmax)
    e_b, b_b = _edge_bulk(A_brk, tmax)
    spt_contrast = e_s - b_s
    protection = e_s - e_b
    print(f"Exp170 decode | job {man['job_id']} | backend {man['backend']} | N={man['N']} tmax={tmax}")
    print(f"{'t':>3} {'edge0':>7} {'edgeN':>7} {'bulk3':>7} {'bulk4':>7}  | broken edge0/edgeN")
    for t in range(tmax + 1):
        print(f"{t:>3} {A_spt[t,0]:>7.3f} {A_spt[t,N-1]:>7.3f} {A_spt[t,3]:>7.3f} {A_spt[t,4]:>7.3f}  | "
              f"{A_brk[t,0]:>6.3f} {A_brk[t,N-1]:>6.3f}")
    print(f"\nSPT arm    : edge_late={e_s:.3f} bulk_late={b_s:.3f}  EDGE-BULK CONTRAST={spt_contrast:+.3f}")
    print(f"broken arm : edge_late={e_b:.3f} bulk_late={b_b:.3f}  edge-bulk={e_b-b_b:+.3f}")
    print(f"SYMMETRY PROTECTION: edge_SPT - edge_broken = {protection:+.3f}")
    gate = spt_contrast > 0.15 and protection > 0.15
    print(f"\nPRE-REG GATE (edge-bulk>0.15 AND protection>0.15): {'HELD' if gate else 'FALSIFIED'}")
    if not gate:
        print("  -> honest null: the SPT edge signature did not survive the depth on hardware, OR the "
              "edge persistence is not symmetry-protected at this noise level.")
    out = {"job_id": man["job_id"], "backend": man["backend"], "N": man["N"], "tmax": tmax,
           "edge_spt": e_s, "bulk_spt": b_s, "spt_edge_bulk_contrast": spt_contrast,
           "edge_broken": e_b, "symmetry_protection": protection, "prereg_gate_held": bool(gate),
           "A_spt": A_spt.tolist(), "A_broken": A_brk.tolist()}
    fn = os.path.join(HERE, "..", "results", "exp170_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--tmax", type=int, default=10)
    ap.add_argument("--shots", type=int, default=4000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.tmax, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp170_manifest.json"))
    else: ap.print_help()
