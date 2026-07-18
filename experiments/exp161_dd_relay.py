#!/usr/bin/env python3
"""Exp161 — DD ON THE RELAY RECEIVER: the condition-first test, properly triggered.
C4850. Exp160 measured the disease in-job (~0.17 superposition gap on the two-window relay);
Exp158's null was a no-disease condition. This is the same DD question asked where the gap IS.

ARMS (one job, matched): nodd (re-establishes the gap THIS job), dd (CPMG-2 XX pairs on the end
receiver q4 in BOTH feedforward windows + on the idling Bell-half q3 in window 1; frame-neutral),
bracket (inversion placement, mechanism control — must track nodd).

DECODE PRE-CONDITION: in-job gap = meanZ(nodd) - meanXY(nodd) must exceed 0.10, else the
condition is absent and any null is declared UNINFORMATIVE (condition-first, C4847).
ESTIMATOR (pre-chosen): Delta = mean over X±,Y± of [F_dd - F_nodd]; binomial SE;
resolvable iff Delta > 2*SE AND Delta > 0.01. Bracket gate: |Delta_bracket| < max(2SE, 0.01).

Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp154_teleportation import STATES, _apply

SUPERPOS = ("X+", "X-", "Y+", "Y-")
ARMS = ("nodd", "dd", "bracket")


def relay_circuit(prep, verify, arm):
    """Exp160 chain with the two idle windows instrumented. dd: X pairs SUBDIVIDE each window
    (q4 both windows, q3 window 1). bracket: X pairs ENCLOSE each window (inversion, no refocus).
    Single-qubit barriers stop XX cancellation on the wire."""
    qc = QuantumCircuit(5, 5)
    _apply(qc, prep, 0)
    qc.h(1); qc.cx(1, 2)
    qc.h(3); qc.cx(3, 4)
    qc.barrier()
    qc.cx(0, 1); qc.h(0)                              # --- window 1: measure q0,q1 + correct q2
    if arm == "bracket":
        qc.x(3); qc.x(4); qc.barrier(3, 4)
    qc.measure(0, 0)
    if arm == "dd":
        qc.x(3); qc.x(4); qc.barrier(3, 4)
    qc.measure(1, 1)
    if arm in ("dd", "bracket"):
        qc.x(3); qc.x(4); qc.barrier(3, 4)
    with qc.if_test((qc.clbits[1], 1)): qc.x(2)
    with qc.if_test((qc.clbits[0], 1)): qc.z(2)
    qc.barrier()
    qc.cx(2, 3); qc.h(2)                              # --- window 2: measure q2,q3 + correct q4
    if arm == "bracket":
        qc.x(4); qc.barrier(4)
    qc.measure(2, 2)
    if arm == "dd":
        qc.x(4); qc.barrier(4)
    qc.measure(3, 3)
    if arm in ("dd", "bracket"):
        qc.x(4); qc.barrier(4)
    with qc.if_test((qc.clbits[3], 1)): qc.x(4)
    with qc.if_test((qc.clbits[2], 1)): qc.z(4)
    qc.barrier()
    _apply(qc, verify, 4)
    qc.measure(4, 4)
    return qc


def _fid(counts, shots):
    return sum(c for b, c in counts.items() if b.replace(" ", "")[0] == "0") / shots


def selftest():
    """Noiseless: all arms F=1 all states (XX pairs frame-neutral in both windows, including on
    the Bell-pair half q3 — the flipped pair is restored before it is consumed)."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 4000
    print("Exp161 selftest (noiseless Aer)")
    for arm in ARMS:
        fids = {n: _fid(sim.run(relay_circuit(s["prep"], s["verify"], arm), shots=shots)
                        .result().get_counts(), shots) for n, s in STATES.items()}
        print(f"  {arm:>8}: " + " ".join(f"{n}={f:.2f}" for n, f in fids.items()))
        assert all(f > 0.99 for f in fids.values()), f"{arm} breaks the relay algebra"
    print("SELFTEST PASS: all arms algebra-neutral; effect is hardware-only. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for name, s in STATES.items():
            circuits.append(transpile(relay_circuit(s["prep"], s["verify"], arm),
                                      backend=backend, optimization_level=1))
            order.append([name, arm])
    def n1q(tqc):
        return sum(1 for i in tqc.data if len(i.qubits) == 1 and i.operation.name in ("x", "sx", "rz"))
    counts = {}
    for tqc, (name, arm) in zip(circuits, order):
        counts.setdefault(name, {})[arm] = n1q(tqc)
    ok = all(c["dd"] > c["nodd"] and c["bracket"] > c["nodd"] for c in counts.values())
    if not ok:
        print("ABORT: DD pulses cancelled in transpile:", counts["Z+"]); sys.exit(1)
    print(f"transpile-survival PASS (Z+ 1q-ops: {counts['Z+']})")
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 161, "slug": "dd_relay", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"precondition": "in-job gap meanZ-meanXY (nodd) > 0.10 else null UNINFORMATIVE",
                           "estimator": "Delta = mean X/Y of F_dd - F_nodd; binomial SE",
                           "resolvable": "Delta > 2*SE AND Delta > 0.01",
                           "mechanism": "|Delta_bracket| < max(2*SE, 0.01)",
                           "prediction": "gap 0.10-0.22; Delta 0.005-0.08; P(resolvable) 0.55"}}
    out = os.path.join(HERE, "..", "results", "exp161_dd_relay_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp161_dd_relay_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    F = {a: {} for a in ARMS}
    for idx, (name, arm) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        F[arm][name] = _fid(getattr(r.data, reg).get_counts(), shots)
    print(f"Exp161 DD-on-relay decode | job {man['job_id']} | backend {man['backend']}")
    print(f"{'state':>6} {'F(nodd)':>9} {'F(dd)':>9} {'F(bracket)':>11}")
    for n in STATES:
        print(f"{n:>6} {F['nodd'][n]:>9.3f} {F['dd'][n]:>9.3f} {F['bracket'][n]:>11.3f}")
    mz = np.mean([F["nodd"][s] for s in ("Z+", "Z-")])
    mxy = np.mean([F["nodd"][s] for s in SUPERPOS])
    gap = float(mz - mxy)
    d = float(np.mean([F["dd"][s] - F["nodd"][s] for s in SUPERPOS]))
    db = float(np.mean([F["bracket"][s] - F["nodd"][s] for s in SUPERPOS]))
    se = float(np.sqrt(sum(F["dd"][s]*(1-F["dd"][s]) + F["nodd"][s]*(1-F["nodd"][s])
                           for s in SUPERPOS) / shots) / 4)
    dz = float(np.mean([F["dd"][s] - F["nodd"][s] for s in ("Z+", "Z-")]))
    cond = gap > 0.10
    resolvable = d > 2 * se and d > 0.01
    mech = abs(db) < max(2 * se, 0.01)
    print(f"\nPRE-CONDITION: in-job gap = {gap:.3f} ({'PRESENT' if cond else 'ABSENT -> any null UNINFORMATIVE'})")
    print(f"PRIMARY  Delta_dd = {d:+.4f} ± {se:.4f} (z={d/se:+.1f}) | recovery {100*d/max(gap,1e-9):.0f}% of gap")
    print(f"MECH     Delta_bracket = {db:+.4f} ({'tracks nodd' if mech else 'DOES NOT track nodd'}) | Delta_Z(dd) = {dz:+.4f}")
    if cond and resolvable:
        v = "DD RECOVERS THE RELAY — condition-first test positive; the idle-window dephasing is echo-refocusable at two-window scale"
    elif cond:
        v = "NULL WITH THE DISEASE PRESENT — the relay's idle dephasing is NOT resolvably echo-refocusable (informative null; noise is fast or measurement-induced)"
    else:
        v = "UNINFORMATIVE — condition absent this job"
    print(f"VERDICT: {v}")
    out = {"job_id": man["job_id"], "fidelities": F, "gap_nodd": gap, "delta_dd": d, "se": se,
           "delta_bracket": db, "delta_z": dz, "condition_present": bool(cond),
           "resolvable": bool(resolvable), "mechanism_ok": bool(mech)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp161_dd_relay_decode.json"), "w"), indent=1)
    print("-> results/exp161_dd_relay_decode.json")


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
