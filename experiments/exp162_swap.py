#!/usr/bin/env python3
"""Exp162 — ENTANGLEMENT SWAPPING: entangle two qubits that never interacted.
C4851. The true repeater primitive (network wing: hop 154, chain 160, swap 162).

Bell(A,B1) + Bell(B2,C); Bell-measure (B1,B2) with real feedforward corrections on C ->
A and C are projected into |Phi+> though no gate ever connected them. Certified by the
ENTANGLEMENT WITNESS: F(A-C, Phi+) = (1 + <ZZ> + <XX> - <YY>)/4 > 1/2 — no separable state
can exceed 1/2 overlap with a maximally entangled state.

ARMS (within one job, x 3 settings ZZ/XX/YY): swap | direct (Bell(A,C) prepared directly,
same-job swap cost) | nocorr (skip feedforward -> random Bell mixture, F ~ 0.25) |
nomeas (skip the Bell measurement -> A,C never entangled, F ~ 0.25).

Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ARMS = ("swap", "direct", "nocorr", "nomeas")
SETTINGS = ("ZZ", "XX", "YY")
WITNESS = 0.5


def swap_circuit(arm, setting):
    """A=q0, B1=q1, B2=q2, C=q3. Measure q0,q3 parity in the given basis (c2,c3)."""
    qc = QuantumCircuit(4, 4)
    if arm == "direct":
        qc.h(0); qc.cx(0, 3)
    else:
        qc.h(0); qc.cx(0, 1)          # Bell(A,B1)
        qc.h(2); qc.cx(2, 3)          # Bell(B2,C)
        qc.barrier()
        if arm != "nomeas":
            qc.cx(1, 2); qc.h(1)      # Bell measurement on the middles
            qc.measure(1, 0); qc.measure(2, 1)
            if arm != "nocorr":
                with qc.if_test((qc.clbits[1], 1)): qc.x(3)
                with qc.if_test((qc.clbits[0], 1)): qc.z(3)
    qc.barrier()
    for q in (0, 3):
        if setting == "XX":
            qc.h(q)
        elif setting == "YY":
            qc.sdg(q); qc.h(q)
    qc.measure(0, 2); qc.measure(3, 3)
    return qc


def _parity(counts, shots):
    """<P0 P3> from clbits c2,c3 (string 'c3c2c1c0': c3 leftmost)."""
    acc = 0
    for b, c in counts.items():
        b = b.replace(" ", "")
        s = (1 if b[0] == "0" else -1) * (1 if b[1] == "0" else -1)
        acc += s * c
    return acc / shots


def fidelity(par):
    """F(Phi+) = (1 + ZZ + XX - YY)/4."""
    return (1 + par["ZZ"] + par["XX"] - par["YY"]) / 4


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    print("Exp162 selftest (noiseless Aer)")
    for arm in ARMS:
        par = {s: _parity(sim.run(swap_circuit(arm, s), shots=shots).result().get_counts(), shots)
               for s in SETTINGS}
        F = fidelity(par)
        print(f"  {arm:>7}: ZZ={par['ZZ']:+.2f} XX={par['XX']:+.2f} YY={par['YY']:+.2f} -> F={F:.3f}")
        if arm in ("swap", "direct"):
            assert F > 0.99, f"{arm} must give perfect Phi+"
        else:
            assert abs(F - 0.25) < 0.04, f"{arm} control must sit at 0.25"
    print("SELFTEST PASS: swap projects A-C into Phi+ exactly; both falsifiers collapse to 0.25. "
          "Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for s in SETTINGS:
            circuits.append(transpile(swap_circuit(arm, s), backend=backend, optimization_level=3))
            order.append([arm, s])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 162, "slug": "swap", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "witness": WITNESS,
                "prereg": {"primary": "F_swap > 1/2 (separable bound) at >5 sigma",
                           "controls": "nocorr and nomeas F in [0.18, 0.35]",
                           "prediction": "F_swap 0.80-0.92; F_direct 0.90-0.97; controls 0.22-0.28"}}
    out = os.path.join(HERE, "..", "results", "exp162_swap_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp162_swap_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    par = {a: {} for a in ARMS}
    for idx, (arm, s) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        par[arm][s] = _parity(getattr(r.data, reg).get_counts(), shots)
    F = {a: fidelity(par[a]) for a in ARMS}
    se = 0.75 / np.sqrt(shots)   # conservative: 3 parities each var<=1/shots, /4
    print(f"Exp162 SWAP decode | job {man['job_id']} | backend {man['backend']} | witness {WITNESS}")
    for a in ARMS:
        p = par[a]
        print(f"  {a:>7}: ZZ={p['ZZ']:+.3f} XX={p['XX']:+.3f} YY={p['YY']:+.3f} -> F = {F[a]:.3f}")
    nsig = (F["swap"] - WITNESS) / se
    ok = F["swap"] > WITNESS and nsig > 5 and 0.18 < F["nocorr"] < 0.35 and 0.18 < F["nomeas"] < 0.35
    print(f"\nWITNESS: F_swap = {F['swap']:.3f} vs 1/2 separable bound -> {nsig:.0f} sigma")
    print(f"SWAP COST (same job): F_direct - F_swap = {F['direct'] - F['swap']:+.3f}")
    print(f"FALSIFIERS: nocorr {F['nocorr']:.3f} | nomeas {F['nomeas']:.3f} (both must sit near 0.25)")
    print(f"VERDICT: {'SWAP WORKS — two qubits that never interacted are certified entangled' if ok else 'FAILED a gate (honest accounting above)'}")
    out = {"job_id": man["job_id"], "parities": par, "fidelities": {a: float(F[a]) for a in ARMS},
           "witness_sigma": float(nsig), "swap_cost": float(F["direct"] - F["swap"]),
           "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp162_swap_decode.json"), "w"), indent=1)
    print("-> results/exp162_swap_decode.json")


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
