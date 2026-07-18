#!/usr/bin/env python3
"""Exp160 — TELEPORT RELAY: the second hop. q0 -> (Bell1) -> q2 -> (Bell2) -> q4.
Creator directive C4849. Second piece of the quantum-network wing (Exp154 = single hop).

THE AHA. A network is not a link — it is links COMPOSED. The state crosses two Bell pairs
through two mid-circuit Bell measurements and two real feedforward corrections in sequence;
the receiver of hop 1 becomes the sender of hop 2. Verified end-to-end against the known input.
The 2/3 measure-and-prepare bound applies to the WHOLE channel (any classical relay is also
bounded), so beating it end-to-end certifies genuine quantum relay.

FOUR ARMS, within one job (C4847 non-stationarity: the single-hop baseline flies in the SAME
job, so the per-hop cost is drift-free):
  chain      — full two-hop relay (primary)
  single     — Exp154 single hop, same job (per-hop cost = F_single - F_chain)
  noent2     — hop-2 Bell pair never created; hop 1 intact. The RELAY resource is load-bearing:
               superpositions must collapse to ~1/2 (hop-1 falsifiers established in Exp154).
  nocorr2    — hop-2 corrections skipped; hop 1 intact. The RELAY feedforward is load-bearing:
               all six states must collapse to ~1/2.

PRE-REG: primary = chain avg F > 2/3. Prediction (2x-wide band): 0.855-0.92 (point ~0.878 from
composing today's same-day 0.936 single-hop via process-fidelity square); per-hop cost 0.02-0.09;
noent2 superpositions 0.46-0.54; nocorr2 avg 0.46-0.54.

FENCE (headline): two hops on one die with zero storage time — a relay PRIMITIVE (sequential
teleportation), not a repeater (no entanglement swapping, no purification, no quantum memory).

Usage:
  python3 exp160_relay.py --selftest
  python3 exp160_relay.py --submit [--backend ibm_fez --shots 4096]
  python3 exp160_relay.py --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp154_teleportation import STATES, CLASSICAL_BOUND, _apply

SUPERPOS = ("X+", "X-", "Y+", "Y-")
ARMS = ("chain", "single", "noent2", "nocorr2")


def relay_circuit(prep, verify, arm):
    """Two-hop teleport chain with real feedforward. Arms vary ONLY hop 2 (or truncate to one hop).
    Qubits: 0 source | 1,2 Bell-1 | 3,4 Bell-2. Classical: c0..c3 Bell bits, c4 verify."""
    if arm == "single":
        qc = QuantumCircuit(3, 3)
        _apply(qc, prep, 0)
        qc.h(1); qc.cx(1, 2)
        qc.barrier()
        qc.cx(0, 1); qc.h(0)
        qc.measure(0, 0); qc.measure(1, 1)
        with qc.if_test((qc.clbits[1], 1)): qc.x(2)
        with qc.if_test((qc.clbits[0], 1)): qc.z(2)
        qc.barrier()
        _apply(qc, verify, 2)
        qc.measure(2, 2)
        return qc
    qc = QuantumCircuit(5, 5)
    _apply(qc, prep, 0)
    qc.h(1); qc.cx(1, 2)                          # Bell pair 1 (hop 1 resource)
    if arm != "noent2":
        qc.h(3); qc.cx(3, 4)                      # Bell pair 2 (hop 2 resource)
    qc.barrier()
    qc.cx(0, 1); qc.h(0)                          # hop 1: Bell measure (q0,q1)
    qc.measure(0, 0); qc.measure(1, 1)
    with qc.if_test((qc.clbits[1], 1)): qc.x(2)   # hop 1 corrections (always applied)
    with qc.if_test((qc.clbits[0], 1)): qc.z(2)
    qc.barrier()
    qc.cx(2, 3); qc.h(2)                          # hop 2: Bell measure (q2,q3)
    qc.measure(2, 2); qc.measure(3, 3)
    if arm != "nocorr2":
        with qc.if_test((qc.clbits[3], 1)): qc.x(4)
        with qc.if_test((qc.clbits[2], 1)): qc.z(4)
    qc.barrier()
    _apply(qc, verify, 4)
    qc.measure(4, 4)
    return qc


def _fid(counts, shots, nclbits):
    """F = P(verify bit == 0); verify bit is the highest clbit (leftmost char)."""
    return sum(c for b, c in counts.items() if b.replace(" ", "")[0] == "0") / shots


def selftest():
    """P3 TRUTH-GATE (noiseless Aer): chain and single give F=1 for all six states; noent2
    collapses the superpositions; nocorr2 collapses everything. The test can fail: a broken
    hop-2 correction table or mis-wired clbits shows up immediately."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 4000
    print("Exp160 selftest (noiseless Aer)")
    F = {a: {} for a in ARMS}
    for arm in ARMS:
        for name, s in STATES.items():
            qc = relay_circuit(s["prep"], s["verify"], arm)
            F[arm][name] = _fid(sim.run(qc, shots=shots).result().get_counts(), shots, qc.num_clbits)
        print(f"  {arm:>8}: " + " ".join(f"{n}={f:.2f}" for n, f in F[arm].items()))
    assert all(f > 0.99 for f in F["chain"].values()), "chain must teleport perfectly noiseless"
    assert all(f > 0.99 for f in F["single"].values()), "single hop must be perfect noiseless"
    assert all(abs(F["noent2"][s] - 0.5) < 0.05 for s in SUPERPOS), "noent2 must collapse superpositions"
    assert abs(np.mean(list(F["nocorr2"].values())) - 0.5) < 0.05, "nocorr2 must collapse to chance"
    print("SELFTEST PASS: relay exact, hop-2 resource and feedforward each load-bearing. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for name, s in STATES.items():
            qc = relay_circuit(s["prep"], s["verify"], arm)
            circuits.append(transpile(qc, backend=backend, optimization_level=3))
            order.append([name, arm])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 160, "slug": "relay", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "classical_bound": CLASSICAL_BOUND,
                "prereg": {"primary": "chain avg F > 2/3 (end-to-end classical relay bound)",
                           "prediction": "chain 0.855-0.92 (point 0.878); per-hop cost 0.02-0.09; "
                                         "noent2 superpos 0.46-0.54; nocorr2 avg 0.46-0.54",
                           "within_job": "single-hop baseline same job (drift-free per-hop cost)"},
                "note": "two-hop teleport relay, 4 arms x 6 states; hop-2 falsifiers; "
                        "relay primitive fence (no swapping/purification/memory)"}
    out = os.path.join(HERE, "..", "results", "exp160_relay_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits = 4 arms x 6 states, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp160_relay_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    F = {a: {} for a in ARMS}
    for idx, (name, arm) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        F[arm][name] = _fid(getattr(r.data, reg).get_counts(), shots, 0)
    print(f"Exp160 TELEPORT RELAY decode | job {man['job_id']} | backend {man['backend']} | bound {CLASSICAL_BOUND:.3f}")
    print(f"{'state':>6} {'F(chain)':>9} {'F(single)':>10} {'F(noent2)':>10} {'F(nocorr2)':>11}")
    for name in STATES:
        print(f"{name:>6} {F['chain'][name]:>9.3f} {F['single'][name]:>10.3f} "
              f"{F['noent2'][name]:>10.3f} {F['nocorr2'][name]:>11.3f}")
    avg = {a: float(np.mean(list(F[a].values()))) for a in ARMS}
    sup_noent = float(np.mean([F["noent2"][s] for s in SUPERPOS]))
    hop_cost = avg["single"] - avg["chain"]
    se = np.sqrt(avg["chain"] * (1 - avg["chain"]) / (6 * shots))
    beats = avg["chain"] > CLASSICAL_BOUND
    print(f"\nCHAIN (two hops, end-to-end): {avg['chain']:.3f} vs bound {CLASSICAL_BOUND:.3f} "
          f"(margin {avg['chain']-CLASSICAL_BOUND:+.3f}, ~{(avg['chain']-CLASSICAL_BOUND)/se:.0f} sigma)")
    print(f"SINGLE HOP (same job):        {avg['single']:.3f}  -> per-hop cost {hop_cost:+.3f}")
    print(f"FALSIFIERS: noent2 superpositions {sup_noent:.3f} (chance) | nocorr2 avg {avg['nocorr2']:.3f} (chance)")
    f1 = avg["single"]; fp1 = (3 * f1 - 1) / 2
    pred2 = (2 * fp1 * fp1 + 1) / 3
    print(f"COMPOSITION CHECK: process-fidelity square of same-job single hop predicts "
          f"{pred2:.3f} for the chain (measured {avg['chain']:.3f}, diff {avg['chain']-pred2:+.3f})")
    ok = beats and abs(sup_noent - 0.5) < 0.06 and abs(avg["nocorr2"] - 0.5) < 0.06
    print(f"VERDICT: {'RELAY WORKS — the state crossed two hops and the end-to-end channel is quantum' if ok else 'FAILED a gate (honest accounting above)'}")
    out = {"job_id": man["job_id"], "backend": man["backend"], "fidelities": F, "averages": avg,
           "per_hop_cost": float(hop_cost), "noent2_superpos": sup_noent,
           "composition_predicted": float(pred2), "beats_bound": bool(beats), "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp160_relay_decode.json"), "w"), indent=1)
    print("-> results/exp160_relay_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=4096)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
