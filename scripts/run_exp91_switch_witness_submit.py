#!/usr/bin/env python3
"""
Exp91 — Quantum-Switch Causal Witness: HARDWARE SUBMIT (Elder C6315)
Pre-reg: experiments/exp91-quantum-switch-causal-witness-preregistration.md (committed first)
Sim:     experiments/exp91_quantum_switch_witness_sim.py (W=+2.00 ideal / +1.93 FakeMarrakesh)

Co-submits 4 circuits (switch/definite x commute/anticommute) in ONE SamplerV2 job so all
DISC values share a single calibration window (drift-free, F68 discipline). Shallow: 4 two-qubit
gates each. Calibration-gated pair (min cz_error + readout). Saves manifest with job_id for
next-cycle grading.

Usage:
  python3 run_exp91_switch_witness_submit.py --scan     # FREE: pick best pair, transpile, noiseless check
  python3 run_exp91_switch_witness_submit.py --submit    # spends QPU (shared budget)
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service

BACKEND = "ibm_marrakesh"
SHOTS = 6000   # <X_c> SE ~0.013; witness ~1.9 has huge margin; small = good shared-budget citizen

# import the validated circuit builder + estimator from the sim
from exp91_quantum_switch_witness_sim import build_switch, exp_x_control

PAIRS = {'commute': ('X', 'X'), 'anticommute': ('X', 'Z')}
CIRCUITS = []  # (label, A, B, definite)
for pk, (A, B) in PAIRS.items():
    CIRCUITS.append((f"switch_{pk}", A, B, False))
    CIRCUITS.append((f"definite_{pk}", A, B, True))


def pick_pair(backend):
    """Calibration-gated: min (cz/ecr error + readout_c + readout_t) over coupled edges."""
    target = backend.target
    twoq_name = 'cz' if 'cz' in target.operation_names else ('ecr' if 'ecr' in target.operation_names else None)
    best, best_cost = None, 1e9
    props_2q = target[twoq_name] if twoq_name else {}
    for (a, b), inst in props_2q.items():
        err2 = getattr(inst, 'error', None)
        if err2 is None:
            continue
        try:
            roa = target['measure'][(a,)].error
            rob = target['measure'][(b,)].error
        except Exception:
            roa = rob = 0.0
        cost = err2 + (roa or 0) + (rob or 0)
        if cost < best_cost:
            best_cost, best = cost, (a, b)
    return best, best_cost, twoq_name


def transpile_all(backend, layout):
    from qiskit import transpile
    tqcs, metas = [], []
    for label, A, B, definite in CIRCUITS:
        qc = build_switch(A, B, definite=definite)  # q0=control, q1=target
        tqc = transpile(qc, backend=backend, initial_layout=list(layout),
                        optimization_level=1, seed_transpiler=42)
        twoq = sum(1 for i in tqc.data if i.operation.num_qubits == 2)
        tqcs.append(tqc)
        metas.append({"label": label, "A": A, "B": B, "definite": definite,
                      "depth": tqc.depth(), "twoq": twoq})
    return tqcs, metas


def noiseless_check(metas):
    """Reproduce the sim witness on the ROUTED intent (sanity: DISC_switch~2, DISC_definite~0)."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    from qiskit import transpile
    vals = {}
    for label, A, B, definite in CIRCUITS:
        qc = build_switch(A, B, definite=definite)
        tqc = transpile(qc, sim)
        c = sim.run(tqc, shots=20000).result().get_counts()
        vals[label] = exp_x_control(c, 20000)
    ds = vals['switch_commute'] - vals['switch_anticommute']
    dd = vals['definite_commute'] - vals['definite_anticommute']
    print(f"  noiseless routed-intent: DISC_switch={ds:+.3f} DISC_definite={dd:+.3f} W={ds-dd:+.3f}")
    return abs(ds - 2.0) < 0.05 and abs(dd) < 0.05


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(BACKEND)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} pending={st.pending_jobs}", flush=True)
    try:
        u = svc.usage()
        print(f"QPU budget: {u.get('usage_remaining_seconds')}s remaining / limit {u.get('usage_limit_seconds')}s", flush=True)
    except Exception as e:
        print("usage probe:", e)

    pair, cost, twoq_name = pick_pair(backend)
    print(f"Calibration-gated pair {pair} (2q={twoq_name}, cost={cost:.5f})", flush=True)
    tqcs, metas = transpile_all(backend, pair)
    for m in metas:
        print(f"  {m['label']:20s} depth={m['depth']} twoq={m['twoq']}")
    ok = noiseless_check(metas)
    print(f"  noiseless-intent gate: {'OK' if ok else 'FAIL — abort'}", flush=True)
    if not ok:
        print("ABORT: routed intent lost the witness.")
        return

    if args.scan:
        print("\n--scan complete (FREE). Re-run with --submit to spend QPU.")
        return

    if args.submit:
        from qiskit_ibm_runtime import SamplerV2
        sampler = SamplerV2(mode=backend)
        sampler.options.default_shots = SHOTS
        job = sampler.run(tqcs)      # ONE job, 4 PUBs -> single calibration window
        jid = job.job_id()
        manifest = {
            "experiment": "exp91-quantum-switch-causal-witness",
            "cycle": "C6315", "backend": BACKEND, "shots": SHOTS,
            "pair": list(pair), "pair_cost": cost, "twoq_gate": twoq_name,
            "job_id": jid, "pub_order": [m["label"] for m in metas], "metas": metas,
        }
        outp = os.path.join(os.path.dirname(__file__), "..", "experiments", "exp91_jobids.json")
        with open(outp, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"\nSubmitted ONE job, {len(tqcs)} PUBs -> job_id={jid}")
        print(f"Manifest -> {os.path.abspath(outp)}")
        print("Grade next cycle: fetch counts, DISC_switch/DISC_definite/W vs H1/H2/H3.")


if __name__ == "__main__":
    main()
