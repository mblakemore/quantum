#!/usr/bin/env python3
"""run_exp125c_submit.py — Exp125c reset-thermalize thermometry of q4 (Whisper C4665).
Prereg: experiments/exp125c-reset-thermalize-thermometry-preregistration.md (FROZEN).
Gate-model substitute for ef-thermometry (open_pulse:False): reset->delay(t)->measure ladder isolates
q4's thermal population via ΔP (readout + meas-induced excitation cancel). Certifies the F105 frontier.
Usage: --scan (FREE) | --submit."""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

SHOTS = 40000
SEED = 4665
QUBIT = 4                       # F104/F105 record qubit
DELAYS_US = [0.1, 40, 120, 360, 590]   # ~{0, 1/3, 1, 3, 5} x T1(=118us)


def therm_circuit(delay_dt):
    qc = QuantumCircuit(1, 1)
    qc.reset(0)
    if delay_dt > 0:
        qc.delay(delay_dt, 0, unit="dt")
    qc.measure(0, 0)
    return qc


def ref1_circuit():
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)
    return qc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp125c")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    dt = backend.target.dt
    T1 = backend.target.qubit_properties[QUBIT].t1
    a_max = float(getattr(backend.target["measure"][(QUBIT,)], "error", float("nan")))
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs} "
          f"q{QUBIT} T1={T1*1e6:.1f}us readout_err={a_max:.5f}")

    pubs = []
    for us in DELAYS_US:
        d = int(round(us * 1e-6 / dt))
        pubs.append((f"therm_{us}us", "therm", us, therm_circuit(d)))
    pubs.append(("ref1", "ref1", 0.0, ref1_circuit()))

    tqcs, metas, ok = [], [], True
    for lab, arm, us, qc in pubs:
        tqc = transpile(qc, backend, initial_layout=[QUBIT],
                        seed_transpiler=SEED, optimization_level=1)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        nmeas = sum(1 for i in tqc.data if i.operation.name == "measure")
        nreset = sum(1 for i in tqc.data if i.operation.name == "reset")
        want_reset = 1 if arm == "therm" else 0
        if n2 != 0 or nmeas != 1 or nreset != want_reset:
            ok = False
            print(f"  AUDIT MISS {lab}: 2q={n2} meas={nmeas} reset={nreset}")
        tqcs.append(tqc)
        metas.append({"label": lab, "arm": arm, "delay_us": us, "shots": SHOTS,
                      "reset": nreset, "depth": tqc.depth()})
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots)")
    if not ok:
        return 1

    rng = np.random.default_rng(SEED)
    order = list(rng.permutation(len(tqcs)))
    tqcs = [tqcs[i] for i in order]
    metas = [metas[i] for i in order]
    if not args.submit:
        print("--scan complete (FREE). No QPU spent.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp125c-reset-thermalize-thermometry", "cycle": "C4665-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp125c-reset-thermalize-thermometry-preregistration.md",
        "qubit": QUBIT, "T1_s": T1, "readout_err": a_max, "delays_us": DELAYS_US,
        "S_BA_banked": -0.855, "S_BA_SE": 0.020,
        "tax_coherent": 0.028, "tax_classical": 0.092,
        "grade": {"G_therm": "dP - 5SE > 0 (thermal resolved)",
                  "frontier": "bonus_lower=(|S|-5SE)*floor(p_eq_lower) vs taxes"},
        "meta_ceiling": "if G-therm FAIL: 3rd axis (F104 credit-SE, F105 SPAM, F125c thermometry) agrees effect below NISQ floor -> STOP, no Exp125d",
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
