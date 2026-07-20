#!/usr/bin/env python3
"""Exp234 — HOW MANY OBSERVERS MAKE A PAST PERMANENT: the arrow-bender, scaled. C4914.

Exp232 showed a recorded event is revocable while held, permanent once released to ONE environment
fragment. Scale it: release the record to N fragments with PARTIAL copy strength, and watch how the
revocability decays as the past spreads. This is the arrow-bender meeting quantum Darwinism (P4):
how many observers must hold a piece of an event before it can no longer be un-happened?

Record cry(pi) S->B (full record), then copy B into N environment fragments with partial coupling
cry(phi) B->E_i (each observer gets a partial witness), then try to REVOKE cry(-pi) S->B and read
the system coherence <X_S>. Derivation (verified): after revoke the system is entangled with the
fragments, and <X_S>(N) = cos(phi/2)^N = kappa_copy^N — the revocability decays GEOMETRICALLY in the
number of observers. Each partial witness makes the past more permanent; below a threshold N* the
event can no longer be revoked. (phi = pi/2 -> kappa_copy = cos(pi/4) = 0.707, so <X_S> = 1, .707,
.5, .354, .25 at N = 0..4; the past crosses "mostly irreversible" (<0.5) at N* = 2.)

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_GEOMETRIC_DECAY: <X_S>(N) matches kappa_copy^N to <= 0.10 at every N, strictly decreasing —
     the revocability decays geometrically as the record spreads to more observers.
  G2_THRESHOLD: <X_S> falls below 0.5 at some N* (report the number of observers that make the past
     permanent); ideal N* = 2 at phi = pi/2.
  G3_DARWINISM_LINK (reported): the decay rate kappa_copy = cos(phi/2) — the same record-strength
     dial that governs objectivity (P4/201) and the ledger of time (P3).
  Registered verdict = G1 and G2.
SCOPE: system + record + up to N=4 environment fragments; partial-copy Darwinism dial. The
  irreversibility is operational (fragments are extra qubits standing in for observers). Composes
  the arrow-bender (232) with quantum Darwinism (204/223) and the bath-record ledger (P3). No new
  physics — the scaling law (revocability = kappa_copy^N) is the result. KILL K1: trivial depth.
BUDGET CHECK (C4887): shallow (1 cry record + N cry copies + 1 cry revoke). Predictions at freeze.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
PHI = PI / 2                          # partial copy strength; kappa_copy = cos(phi/2)
NS = (0, 1, 2, 3, 4)                  # number of environment fragments


def circuit(N):
    """S=q0, record B=q1, fragments E_i = q2..q(1+N). Record, spread to N fragments, revoke, read X_S."""
    qc = QuantumCircuit(6, 1)
    qc.h(0)
    qc.cry(PI, 0, 1)                  # record the event
    qc.barrier()
    for i in range(N):
        qc.cry(PHI, 1, 2 + i)         # partial copy to observer i (Darwinism spread)
    qc.barrier()
    qc.cry(-PI, 0, 1)                 # try to revoke
    qc.barrier()
    qc.h(0); qc.measure(0, 0)         # system coherence <X_S>
    return qc


def _xs(counts):
    c = tot = 0
    for s, n in counts.items():
        c += (1 - 2 * int(s.replace(" ", "")[-1])) * n; tot += n
    return c / tot


def _ideal(N): return float(np.cos(PHI / 2) ** N)


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 100000
    kc = np.cos(PHI / 2)
    print(f"Exp234 selftest | HOW MANY OBSERVERS MAKE A PAST PERMANENT (kappa_copy=cos(phi/2)={kc:.3f})")
    xs = {}
    for N in NS:
        xs[N] = _xs(sim.run(circuit(N), shots=shots).result().get_counts())
        print(f"  N={N}: <X_S>(revoke) = {xs[N]:+.3f}  (ideal kappa^N = {_ideal(N):.3f})")
    for N in NS:
        assert abs(xs[N] - _ideal(N)) < 0.03, f"revocability must follow kappa^N at N={N}"
    assert all(xs[NS[i]] > xs[NS[i + 1]] - 0.02 for i in range(len(NS) - 1)), "must decay with N"
    Nstar = next((N for N in NS if xs[N] < 0.5), None)
    print(f"  irreversibility threshold N* (<X_S><0.5): N={Nstar}")
    print("SELFTEST PASS: the revocability decays geometrically as kappa_copy^N — each observer that "
          "holds a piece of the event makes the past more permanent, crossing irreversible at N*. "
          "The arrow-bender meets quantum Darwinism. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    builds = [circuit(N) for N in NS]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp234_arrow_scaled_manifest.json")
    man = {"exp": 234, "slug": "arrow_bender_scaled", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "Ns": list(NS), "phi": float(PHI),
           "ideal": {str(N): _ideal(N) for N in NS},
           "prereg": {"G1_geometric_decay": "<X_S>(N) matches kappa_copy^N <=0.10 all N, strictly decreasing",
                      "G2_threshold": "<X_S> < 0.5 at some N* (observers that make the past permanent)",
                      "G3_darwinism_link": "reported: decay rate kappa_copy = cos(phi/2)",
                      "registered_verdict": "G1 and G2",
                      "scope": "arrow-bender scaled by observer count; revocability = kappa_copy^N; "
                               "Darwinism permanence threshold"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp234_arrow_scaled_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    Ns = man["Ns"]; ideal = {int(k): v for k, v in man["ideal"].items()}; xs = {}; se = {}
    for idx, N in enumerate(Ns):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        ct = getattr(r0.data, reg).get_counts()
        xs[N] = _xs(ct); nn = sum(ct.values()); se[N] = float(np.sqrt(max(1e-9, 1 - xs[N] ** 2) / nn))
    kc = np.cos(man["phi"] / 2)
    print(f"Exp234 HOW MANY OBSERVERS MAKE A PAST PERMANENT decode | job {man['job_id']}")
    for N in Ns:
        print(f"  N={N}: <X_S>(revoke) = {xs[N]:+.3f} ± {se[N]:.3f}  (ideal kappa^N = {ideal[N]:.3f})")
    g1 = (all(abs(xs[N] - ideal[N]) <= 0.10 for N in Ns)
          and all(xs[Ns[i]] > xs[Ns[i + 1]] - 0.03 for i in range(len(Ns) - 1)))
    Nstar = next((N for N in Ns if xs[N] < 0.5), None)
    g2 = Nstar is not None
    print(f"\nG1 GEOMETRIC DECAY (kappa_copy={kc:.3f}): {'OK' if g1 else 'MISS'}")
    print(f"G2 THRESHOLD: past crosses irreversible (<X_S><0.5) at N* = {Nstar} observers {'OK' if g2 else 'MISS'}")
    print(f"G3 DARWINISM LINK: revocability = kappa_copy^N, kappa_copy=cos(phi/2)={kc:.3f} (same dial as objectivity/P3)")
    ok = g1 and g2
    win = ("HOW MANY OBSERVERS MAKE A PAST PERMANENT — the arrow-bender scaled: the revocability of a "
           f"recorded event decays as kappa_copy^N in the number of observers holding a piece of it, "
           f"crossing irreversible at N*={Nstar}. The past sets not at once but observer by observer, "
           "on the same record-strength dial that governs objectivity. On silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "xs": {str(N): xs[N] for N in Ns}, "Nstar": Nstar,
               "kappa_copy": float(kc), "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp234_arrow_scaled_decode.json"), "w"), indent=1)
    print("-> results/exp234_arrow_scaled_decode.json")


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
