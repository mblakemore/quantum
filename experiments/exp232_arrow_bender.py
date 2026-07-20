#!/usr/bin/env python3
"""Exp232 — THE ARROW-BENDER: hold a recorded event, then choose to revoke or make it permanent. C4914.

Open-question 7 of the frontier (docs/state-of-the-frontier-whisper-c4913.md) and the machine P3's
Guardian of Forever pointed at. Exp230 showed we can SELECT which past was real (sort histories).
This asks the deeper thing: can we build a working gadget that HOLDS an event in a reversible state
and, by a LATER choice, either REVOKES it (un-happens it) or RELEASES it (locks it in, permanent)?

An event is recorded when a system S writes its state into a bath B: cry(theta, S->B). While the
record lives only in B (held locally), the recording is REVERSIBLE — cry(-theta) uncomputes it and
S's coherence returns (the event un-happened). But if the record is RELEASED — copied into a second
environment fragment E (CNOT B->E), made redundant/objective — then uncomputing B no longer restores
S: the information escaped, the past is PERMANENT. The knob is the arrow of time itself: a window of
reversibility, closed by the release choice.

theta = pi (full record). Witness = system coherence <Xbar_S> = <X on q0> (H then measure).
  HELD:            cry(pi)                      -> <X_S> ~ 0  (recorded, held, not yet permanent)
  REVOKE:          cry(pi), cry(-pi)            -> <X_S> ~ 1  (un-happened: the past is rewound)
  RELEASE:         cry(pi), CNOT(B->E)          -> <X_S> ~ 0  (objectified / made redundant)
  RELEASE+REVOKE:  cry(pi), CNOT(B->E), cry(-pi)-> <X_S> ~ 0  (revocation FAILS: past is permanent)

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_REVOCABLE: <X_S>(revoke) >= 0.80 — while the record is held locally, the past is revocable;
     uncomputing restores the system's coherence (the event un-happens).
  G2_RELEASE_LOCKS_IT: <X_S>(release+revoke) <= 0.30 — once the record is released (copied to E),
     the same revocation FAILS; the past is permanent.
  G3_THE_WINDOW: <X_S>(revoke) - <X_S>(release+revoke) >= 0.5 — a real, measured window of
     reversibility, opened by holding and closed by the release choice.
  Registered verdict = G1 and G2 and G3.
SCOPE: 3 qubits (system + record + environment fragment). The "arrow of time" here is operational:
  irreversibility = the record escaping to an inaccessible fragment (the 200b/201 bath-record ledger
  made a controllable gadget). The delayed choice is the release/revoke ordering. No new physics —
  the composition (a working delayed-choice arrow-bender) is the point. KILL K1: trivial depth.
BUDGET CHECK (C4887): shallow (1 cry each arm + 1 CNOT). <X_S> ideal 1/0; hardware -> revoke ~0.85,
  release+revoke ~0.1; window ~0.7.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
ARMS = ("held", "revoke", "release", "release_revoke")


def circuit(arm):
    """S=q0, record B=q1, environment fragment E=q2. Witness <X_S>."""
    qc = QuantumCircuit(3, 1)
    qc.h(0)                                    # system in a superposition (the 'event')
    qc.cry(PI, 0, 1)                           # record the event into the bath B
    qc.barrier()
    if arm == "revoke":
        qc.cry(-PI, 0, 1)                      # uncompute the record while it is held locally
    elif arm == "release":
        qc.cx(1, 2)                            # release: copy the record into fragment E (permanent)
    elif arm == "release_revoke":
        qc.cx(1, 2)                            # release first...
        qc.cry(-PI, 0, 1)                      # ...then try to revoke (must fail)
    qc.barrier()
    qc.h(0); qc.measure(0, 0)                  # read system coherence <X_S>
    return qc


def _xs(counts):
    c = tot = 0
    for s, n in counts.items():
        c += (1 - 2 * int(s.replace(" ", "")[-1])) * n; tot += n
    return c / tot


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 100000
    print("Exp232 selftest | THE ARROW-BENDER — hold, then revoke or make permanent")
    r = {}
    for arm in ARMS:
        r[arm] = _xs(sim.run(circuit(arm), shots=shots).result().get_counts())
        print(f"  {arm:16s}: <X_S> = {r[arm]:+.3f}")
    window = r["revoke"] - r["release_revoke"]
    print(f"  window (revoke - release+revoke) = {window:.3f}")
    assert r["revoke"] > 0.98, "held-record revoke must restore coherence (un-happen)"
    assert abs(r["release_revoke"]) < 0.05, "released-record revoke must fail (permanent)"
    assert abs(r["held"]) < 0.05 and abs(r["release"]) < 0.05, "recorded/objectified states decohered"
    print("SELFTEST PASS: a held record is revocable (coherence returns, the event un-happens); "
          "release the record to a fragment and the same revocation fails — the past is permanent. "
          "A working delayed-choice arrow-bender. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    builds = [circuit(a) for a in ARMS]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp232_arrow_bender_manifest.json")
    man = {"exp": 232, "slug": "arrow_bender", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": list(ARMS),
           "prereg": {"G1_revocable": "<X_S>(revoke) >= 0.80",
                      "G2_release_locks_it": "<X_S>(release+revoke) <= 0.30",
                      "G3_the_window": "<X_S>(revoke) - <X_S>(release+revoke) >= 0.5",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "delayed-choice arrow-bender: hold a recorded event reversibly, then "
                               "revoke (un-happen) or release (permanent); irreversibility = record escaping to E"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp232_arrow_bender_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    r = {}; se = {}
    for idx, arm in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        ct = getattr(r0.data, reg).get_counts()
        r[arm] = _xs(ct); n = sum(ct.values()); se[arm] = float(np.sqrt(max(1e-9, 1 - r[arm] ** 2) / n))
    print(f"Exp232 THE ARROW-BENDER decode | job {man['job_id']}")
    for arm in man["order"]:
        print(f"  {arm:16s}: <X_S> = {r[arm]:+.3f} ± {se[arm]:.3f}")
    window = r["revoke"] - r["release_revoke"]
    se_w = float(np.sqrt(se["revoke"] ** 2 + se["release_revoke"] ** 2))
    g1 = r["revoke"] >= 0.80
    g2 = r["release_revoke"] <= 0.30
    g3 = window >= 0.5 and window / se_w >= 5
    print(f"\nG1 REVOCABLE (held record un-happens): <X_S>(revoke)={r['revoke']:.3f} >= 0.80 {'OK' if g1 else 'MISS'}")
    print(f"G2 RELEASE LOCKS IT (permanent): <X_S>(release+revoke)={r['release_revoke']:.3f} <= 0.30 {'OK' if g2 else 'MISS'}")
    print(f"G3 THE WINDOW: revoke - release+revoke = {window:.3f} at {window/se_w:.0f} sigma (>=0.5) {'OK' if g3 else 'MISS'}")
    ok = g1 and g2 and g3
    win = ("THE ARROW-BENDER — a recorded event held in a bath is REVOCABLE (uncomputing restores the "
           "system, the past un-happens); release the record to an environment fragment and the same "
           "revocation FAILS — the past is permanent. A working delayed-choice arrow-bender: a measured "
           "window of reversibility, opened by holding and closed by the release choice, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "xs": r, "window": window,
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp232_arrow_bender_decode.json"), "w"), indent=1)
    print("-> results/exp232_arrow_bender_decode.json")


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
