#!/usr/bin/env python3
"""
Exp93 — Classical-Mixture Control for the Causal-Order Witness: HARDWARE SUBMIT (Elder C6341)
Pre-reg: experiments/exp93-classical-mixture-control-preregistration.md (SIM arm C6328, PASS)
Sim:     experiments/exp93_classical_mixture_control_sim.py (W2=+2.00 ideal / +1.92 FakeMarrakesh)

WHY THIS RUN (Ember C4072 named residual): Exp91's HW witness W1 = DISC_switch - DISC_definite
ran on ibm_marrakesh (F75, W1=+1.781). Ember's Exp94b phi=pi endpoint (kingston) showed the
classical mixture is INERT on hardware (DISC(pi)=0.027) — but that is a DIFFERENT device and a
DIFFERENT construction (continuous cry(phi) damping, not the co-submitted dephasing ancilla).
The one thing still un-run is a SAME-DEVICE, SAME-JOB switch-vs-mixture W2: co-submit the coherent
switch AND its Z-dephased (classical-mixture) twin in ONE SamplerV2 job so W2 = DISC_switch -
DISC_mixture shares a single calibration window (drift-free, F68 discipline). That closes the
causal-SEPARABILITY loophole on silicon, not just the pure-definite-order loophole (Exp91) or the
cross-device continuous law (Exp94b).

Co-submits 6 circuits (switch/definite/mixture x commute/anticommute) in ONE job:
  W1 = DISC_switch - DISC_definite   (reproduces Exp91 in THIS window)
  W2 = DISC_switch - DISC_mixture    (NEW headline — same device, same window)
Switch/definite = 2 qubits (control,target); mixture = 3 qubits (control,target,ancilla).
Calibration-gated TRIPLE: control C with two native-2q neighbors T,Anc (both CNOT(C->.) native),
min cz_error(C,T)+cz_error(C,Anc)+readout(C). Only the control is measured (ancilla traced out).

Usage:
  python3 run_exp93_mixture_control_submit.py --scan     # FREE: pick triple, transpile, noiseless check
  python3 run_exp93_mixture_control_submit.py --submit    # spends QPU (shared budget)
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service

# reuse the SIM-validated builder + estimator verbatim (single source of truth)
from exp93_classical_mixture_control_sim import build_arm, exp_x_control

BACKEND = "ibm_marrakesh"
SHOTS = 6000   # <X_c> SE ~0.013/PUB -> W2 SE ~0.026; expected W2~1.78 => ~68 sigma margin. Small = good budget citizen.

PAIRS = {'commute': ('X', 'X'), 'anticommute': ('X', 'Z')}
# (label, A, B, mode) — order groups arms so the manifest pub_order is unambiguous
CIRCUITS = []
for mode in ('switch', 'definite', 'mixture'):
    for pk, (A, B) in PAIRS.items():
        CIRCUITS.append((f"{mode}_{pk}", A, B, mode))


def _twoq_props(target):
    name = 'cz' if 'cz' in target.operation_names else ('ecr' if 'ecr' in target.operation_names else None)
    return name, (target[name] if name else {})


def pick_triple(backend):
    """Calibration-gated: control C with two native-2q neighbors T,Anc.
    cost = err2(C,T) + err2(C,Anc) + readout(C). Only control is measured."""
    target = backend.target
    twoq_name, props_2q = _twoq_props(target)
    # neighbor map: qubit -> {neighbor: err2}
    neigh = {}
    for (a, b), inst in props_2q.items():
        err2 = getattr(inst, 'error', None)
        if err2 is None:
            continue
        neigh.setdefault(a, {})[b] = err2
        neigh.setdefault(b, {})[a] = err2  # treat undirected (CZ symmetric)

    def readout(q):
        try:
            return target['measure'][(q,)].error or 0.0
        except Exception:
            return 0.0

    best, best_cost = None, 1e9
    for C, nbrs in neigh.items():
        if len(nbrs) < 2:
            continue
        # two lowest-error neighbors of C
        ranked = sorted(nbrs.items(), key=lambda kv: kv[1])
        (T, eT), (Anc, eAnc) = ranked[0], ranked[1]
        cost = eT + eAnc + readout(C)
        if cost < best_cost:
            best_cost, best = cost, (C, T, Anc)
    return best, best_cost, twoq_name


def transpile_all(backend, triple):
    from qiskit import transpile
    C, T, Anc = triple
    tqcs, metas = [], []
    for label, A, B, mode in CIRCUITS:
        qc = build_arm(A, B, mode)              # q0=control, q1=target, (q2=ancilla for mixture)
        layout = [C, T, Anc] if mode == 'mixture' else [C, T]
        tqc = transpile(qc, backend=backend, initial_layout=layout,
                        optimization_level=1, seed_transpiler=42)
        twoq = sum(1 for i in tqc.data if i.operation.num_qubits == 2)
        tqcs.append(tqc)
        metas.append({"label": label, "A": A, "B": B, "mode": mode,
                      "layout": layout, "depth": tqc.depth(), "twoq": twoq})
    return tqcs, metas


def noiseless_check(triple):
    """Reproduce the sim witnesses on the routed intent (sanity: W2~+2, DISC_mixture~0)."""
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    sim = AerSimulator()
    vals = {}
    for label, A, B, mode in CIRCUITS:
        qc = build_arm(A, B, mode)
        tqc = transpile(qc, sim)
        c = sim.run(tqc, shots=20000).result().get_counts()
        vals[label] = exp_x_control(c, 20000)
    ds = vals['switch_commute'] - vals['switch_anticommute']
    dd = vals['definite_commute'] - vals['definite_anticommute']
    dm = vals['mixture_commute'] - vals['mixture_anticommute']
    W1, W2 = ds - dd, ds - dm
    print(f"  noiseless routed-intent: DISC_switch={ds:+.3f} DISC_definite={dd:+.3f} "
          f"DISC_mixture={dm:+.3f}  W1={W1:+.3f} W2={W2:+.3f}")
    return abs(ds - 2.0) < 0.05 and abs(dm) < 0.05 and W2 > 1.90


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

    triple, cost, twoq_name = pick_triple(backend)
    print(f"Calibration-gated triple C={triple[0]} T={triple[1]} Anc={triple[2]} "
          f"(2q={twoq_name}, cost={cost:.5f})", flush=True)
    tqcs, metas = transpile_all(backend, triple)
    for m in metas:
        print(f"  {m['label']:22s} mode={m['mode']:8s} layout={m['layout']} depth={m['depth']} twoq={m['twoq']}")
    ok = noiseless_check(triple)
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
        job = sampler.run(tqcs)      # ONE job, 6 PUBs -> single calibration window
        jid = job.job_id()
        manifest = {
            "experiment": "exp93-classical-mixture-control",
            "cycle": "C6341", "backend": BACKEND, "shots": SHOTS,
            "triple_control_target_ancilla": list(triple), "triple_cost": cost,
            "twoq_gate": twoq_name, "job_id": jid,
            "pub_order": [m["label"] for m in metas], "metas": metas,
            "witnesses": {"W1": "DISC_switch - DISC_definite",
                          "W2": "DISC_switch - DISC_mixture (headline)"},
        }
        outp = os.path.join(os.path.dirname(__file__), "..", "experiments", "exp93_jobids.json")
        with open(outp, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"\nSubmitted ONE job, {len(tqcs)} PUBs -> job_id={jid}")
        print(f"Manifest -> {os.path.abspath(outp)}")
        print("Grade next cycle: fetch counts, DISC_switch/definite/mixture, W1/W2 vs H1/H2/H3/H_HW.")


if __name__ == "__main__":
    main()
