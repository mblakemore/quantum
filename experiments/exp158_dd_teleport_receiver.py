#!/usr/bin/env python3
"""Exp158 — DD ON THE TELEPORT RECEIVER: does dynamical decoupling recover the feedforward-idle
dephasing that costs Exp154's superposition states ~0.07 fidelity?
Creator directive C4847. Direct test of the Exp154 forward lever, downgraded to
plausible-not-established after Ember's C4198 marker null (+0.019±0.012, z=1.53).

DESIGN (to Ember-C4198 standards — her three lessons baked in):
  * WITHIN-JOB A/B/C: one job, three matched arms x 6 cardinal states (drift cannot fake a delta).
  * ESTIMATOR BEFORE THE GATE: direct per-state fidelity P(0) (unbiased binomial — no extreme-point
    statistics). Primary endpoint Delta = mean over the four superposition states (X±, Y±) of
    [F_DD - F_noDD]; SE propagated binomially. RESOLVABLE iff Delta > 2*SE AND Delta > 0.01.
  * REFOCUS, NOT BRACKET: the DD arm subdivides the idle window (CPMG-2: X between the two Bell
    measurements, X at the start of the feedforward latency; XX = I so the correction algebra is
    untouched). The BRACKET arm (X before both measurements, X after) inverts the accumulated
    phase instead of cancelling it — Ember's mechanism control; it must track no-DD.
  * TRANSPILE SURVIVAL: single-qubit barrier between the pulse pair (adjacent on the receiver's
    wire in the DAG — an optimizer would cancel XX = I). Asserted on the transpiled circuits
    before submission; abort if the pulses are gone.

ARMS:
  nodd    — Exp154 teleport circuit verbatim (within-job baseline; also a 154 stability check)
  dd      — + CPMG-2 on the receiver inside the idle window
  bracket — + X...X enclosing the whole window (phase inversion, no refocusing expected)

NEGATIVE CONTROL: Z± states ride in every arm — the mechanism is T2 dephasing, which Z eigenstates
do not feel; a large Delta_Z would flag pulse miscalibration, not recovery.

NULL IS FIRST-CLASS (pre-reg ~0.5): a null says the receiver-idle dephasing is not
echo-refocusable at Heron-r2 timescales (fast noise / readout-resonator-induced), matching
Ember's marker null — and the Exp154 lever line stays downgraded.

FENCE: program-order pulse placement — pulse-level timing is the scheduler's choice, so this
tests the DD sequence as the standard pipeline schedules it, not an optimally-timed echo.

Usage:
  python3 exp158_dd_teleport_receiver.py --selftest
  python3 exp158_dd_teleport_receiver.py --submit [--backend ibm_fez --shots 8000]
  python3 exp158_dd_teleport_receiver.py --decode --manifest ../results/exp158_dd_teleport_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

STATES = {
    "Z+": {"prep": [],            "verify": []},
    "Z-": {"prep": ["x"],         "verify": ["x"]},
    "X+": {"prep": ["h"],         "verify": ["h"]},
    "X-": {"prep": ["x", "h"],    "verify": ["h", "x"]},
    "Y+": {"prep": ["h", "s"],    "verify": ["sdg", "h"]},
    "Y-": {"prep": ["h", "sdg"],  "verify": ["s", "h"]},
}
SUPERPOS = ("X+", "X-", "Y+", "Y-")
ARM_NAMES = ("nodd", "dd", "bracket")


def _apply(qc, gates, q):
    for g in gates:
        getattr(qc, g)(q)


def teleport_circuit(prep, verify, arm):
    """Exp154 circuit with the receiver-idle window instrumented per arm.
    nodd: verbatim. dd: X between the two Bell measurements + X after (CPMG-2 subdividing;
    XX = I, algebra untouched). bracket: X before both measurements + X after (phase inversion
    control). Single-qubit barriers stop the optimizer cancelling the pair on q2's wire."""
    qc = QuantumCircuit(3, 3)
    _apply(qc, prep, 0)
    qc.h(1); qc.cx(1, 2)
    qc.barrier()
    qc.cx(0, 1); qc.h(0)
    if arm == "bracket":
        qc.x(2); qc.barrier(2)
    qc.measure(0, 0)
    if arm == "dd":
        qc.x(2); qc.barrier(2)
    qc.measure(1, 1)
    if arm in ("dd", "bracket"):
        qc.x(2); qc.barrier(2)
    with qc.if_test((qc.clbits[1], 1)):
        qc.x(2)
    with qc.if_test((qc.clbits[0], 1)):
        qc.z(2)
    qc.barrier()
    _apply(qc, verify, 2)
    qc.measure(2, 2)
    return qc


def _fidelity(counts, shots):
    """F = P(q2 measured 0); creg string 'c2 c1 c0', c2 leftmost."""
    return sum(c for b, c in counts.items() if b.replace(" ", "")[0] == "0") / shots


def _endpoint(F_arm, F_base, shots):
    """Delta = mean over superposition states of (F_arm - F_base), binomial SE."""
    d = np.mean([F_arm[s] - F_base[s] for s in SUPERPOS])
    var = sum(F_arm[s] * (1 - F_arm[s]) + F_base[s] * (1 - F_base[s]) for s in SUPERPOS) / shots
    return float(d), float(np.sqrt(var) / len(SUPERPOS))


def selftest():
    """P3 TRUTH-GATE (noiseless Aer): every arm must give F=1 for all six states — the DD and
    bracket pulses are algebra-neutral (XX = I), so any noiseless deviation = a broken frame.
    NOTE: the arms are sim-identical by construction; the physics difference exists only on
    hardware (this test verifies the algebra, not the effect — Ember C4198 lesson, pre-reg 0.5)."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 4000
    print("Exp158 selftest (noiseless Aer) — algebra neutrality of all three arms")
    for arm in ARM_NAMES:
        fids = {}
        for name, s in STATES.items():
            qc = teleport_circuit(s["prep"], s["verify"], arm)
            fids[name] = _fidelity(sim.run(qc, shots=shots).result().get_counts(), shots)
        print(f"  {arm:>8}: " + " ".join(f"{n}={f:.3f}" for n, f in fids.items()))
        assert all(f > 0.99 for f in fids.values()), f"{arm} breaks the teleport algebra"
    print("SELFTEST PASS: XX pulse pairs are frame-neutral in every arm; teleportation exact. "
          "Effect (if any) is hardware-only, as pre-registered.")


def _survival(circuits, order, backend):
    """Transpile-survival gate: the dd/bracket arms must carry MORE 1q pulses on the receiver's
    wire than nodd (optimizer must not have cancelled XX=I). Compare x-family op totals."""
    def xcount(tqc):
        return sum(1 for inst in tqc.data if inst.operation.name in ("x", "sx", "rz")
                   and len(inst.qubits) == 1)
    base = {}
    for tqc, (name, arm) in zip(circuits, order):
        base.setdefault(name, {})[arm] = xcount(tqc)
    ok = all(base[n]["dd"] > base[n]["nodd"] and base[n]["bracket"] > base[n]["nodd"]
             for n in STATES)
    return ok, base


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARM_NAMES:
        for name, s in STATES.items():
            qc = teleport_circuit(s["prep"], s["verify"], arm)
            circuits.append(transpile(qc, backend=backend, optimization_level=1))
            order.append((name, arm))
    ok, counts = _survival(circuits, order, backend)
    if not ok:
        print("ABORT: DD pulses did not survive transpilation (XX cancelled). Op counts:", counts)
        sys.exit(1)
    print(f"transpile-survival PASS (example Z+ 1q-op counts: "
          f"{ {a: counts['Z+'][a] for a in ARM_NAMES} })")
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 158, "slug": "dd_teleport", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": [[n, a] for n, a in order],
                "prereg": {"estimator": "direct per-state P(0); primary Delta = mean over X±,Y± of "
                                        "F_dd - F_nodd; binomial SE",
                           "resolvable": "Delta > 2*SE AND Delta > 0.01",
                           "mechanism": "bracket arm must track nodd (|Delta_bracket| < max(2*SE, 0.01))",
                           "neg_control": "Z states: |Delta_Z| small in all arms",
                           "prediction": "Delta_dd in [0.000, 0.045] (2x-wide band, C4846 rule); "
                                         "P(resolvable) ~ 0.5; null is first-class"},
                "note": "DD on teleport receiver: nodd/dd(CPMG-2 subdividing)/bracket(inversion), "
                        "within-job A/B/C, direct Exp154-lever test"}
    out = os.path.join(HERE, "..", "results", "exp158_dd_teleport_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits = 3 arms x 6 states, {shots} shots) -> {out}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    F = {a: {} for a in ARM_NAMES}
    for idx, (name, arm) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        F[arm][name] = _fidelity(getattr(r.data, reg).get_counts(), shots)
    print(f"Exp158 DD-on-teleport-receiver decode | job {man['job_id']} | backend {man['backend']}")
    print(f"{'state':>6} {'F(nodd)':>9} {'F(dd)':>9} {'F(bracket)':>11}")
    for name in STATES:
        print(f"{name:>6} {F['nodd'][name]:>9.3f} {F['dd'][name]:>9.3f} {F['bracket'][name]:>11.3f}")
    d_dd, se_dd = _endpoint(F["dd"], F["nodd"], shots)
    d_br, se_br = _endpoint(F["bracket"], F["nodd"], shots)
    dz_dd = float(np.mean([F["dd"][s] - F["nodd"][s] for s in ("Z+", "Z-")]))
    avg154 = float(np.mean([F["nodd"][s] for s in STATES]))
    resolvable = (d_dd > 2 * se_dd) and (d_dd > 0.01)
    mech_ok = abs(d_br) < max(2 * se_br, 0.01)
    print(f"\nbaseline avg fidelity (154 stability check): {avg154:.3f} (Exp154 was 0.913)")
    print(f"PRIMARY   Delta_dd (X±,Y±) = {d_dd:+.4f} ± {se_dd:.4f}  (z = {d_dd/se_dd:+.1f})")
    print(f"MECHANISM Delta_bracket    = {d_br:+.4f} ± {se_br:.4f}  "
          f"({'tracks nodd as predicted' if mech_ok else 'DOES NOT track nodd — mechanism model wrong'})")
    print(f"NEG CTRL  Delta_Z(dd)      = {dz_dd:+.4f}  (should be ~0)")
    if resolvable:
        print(f"VERDICT: DD RECOVERY RESOLVED — the Exp154 lever is real; +{d_dd:.3f} on superpositions"
              f" ({'mechanism confirmed by bracket null' if mech_ok else 'but bracket arm complicates the mechanism story'})")
    else:
        print("VERDICT: NULL — receiver-idle dephasing is not resolvably echo-refocusable at these "
              "timescales (pre-registered first-class outcome; matches Ember C4198 marker null; "
              "Exp154 lever stays plausible-not-established -> now leaning NOT)")
    out = {"job_id": man["job_id"], "backend": man["backend"], "fidelities": F,
           "delta_dd": d_dd, "se_dd": se_dd, "delta_bracket": d_br, "se_bracket": se_br,
           "delta_z_dd": dz_dd, "baseline_avg": avg154,
           "resolvable": bool(resolvable), "mechanism_ok": bool(mech_ok)}
    fn = os.path.join(HERE, "..", "results", "exp158_dd_teleport_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp158_dd_teleport_manifest.json"))
    else: ap.print_help()
