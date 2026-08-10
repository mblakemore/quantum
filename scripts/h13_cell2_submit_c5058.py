#!/usr/bin/env python3
"""H13 Cell 2 — THE CAUSAL COMPASS — SUBMIT (prereg FROZEN: docs/h13-cell2-compass-prereg-FROZEN-whisper-c5058.md).

Two separately-budgeted line items (court #9057/#9060):
  PRE-RUN  20 draws x 6 circuits x 1000 shots  -> buys the FLOOR (precision)
  SCIENCE  40 runs  x 6 circuits x  400 shots  -> buys CALLS (1 bit each)
Usage: QPU_ACCOUNT_VAR=IBMQ_ALT3 python3 scripts/h13_cell2_submit_c5058.py [--dry-run]
"""
import json, os, sys, math, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.pop("QISKIT_IBM_INSTANCE", None)
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

DECLARED_BACKENDS = ("ibm_marrakesh", "ibm_fez")
PREREG = "docs/h13-cell2-compass-prereg-FROZEN-whisper-c5058.md"
SEED = 20260811                      # F-IND stream seed — COMMITTED here pre-submit (custody C3)
TAU_MAX_NS = 30000                   # 30 us band, frozen pre-flight (prereg B2)
N_DRAWS, PRERUN_SHOTS = 20, 1000     # pre-run: draw count n=20 is the estimator's sample (B3)
N_RUNS, SCIENCE_SHOTS = 40, 400
BASES = ("X", "Y", "Z")
EST_COST_S = 70.0

def basis_rot(qc, q, b, inverse=False):
    if b == "X": qc.h(q)
    elif b == "Y":
        if inverse: qc.h(q); qc.s(q)
        else: qc.sdg(q); qc.h(q)

def ce_circuit(basis, tau, name):
    """cause-effect: measure Pauli i -> idle tau -> measure Pauli i (one qubit, repeatability-forced)."""
    q = QuantumRegister(1, "q"); c = ClassicalRegister(2, "c")
    qc = QuantumCircuit(q, c, name=name)
    qc.h(q[0])                                   # non-trivial input state
    basis_rot(qc, q[0], basis); qc.measure(q[0], c[0]); basis_rot(qc, q[0], basis, inverse=True)
    qc.delay(tau, q[0], unit="ns")
    basis_rot(qc, q[0], basis); qc.measure(q[0], c[1])
    return qc

def cc_circuit(basis, tau, name):
    """common cause: Phi+ pair, idle tau, both wings measured in Pauli i."""
    q = QuantumRegister(2, "q"); c = ClassicalRegister(2, "c")
    qc = QuantumCircuit(q, c, name=name)
    qc.h(q[0]); qc.cx(q[0], q[1])
    qc.delay(tau, q[0], unit="ns"); qc.delay(tau, q[1], unit="ns")
    for k in (0, 1): basis_rot(qc, q[k], basis)
    qc.measure(q[0], c[0]); qc.measure(q[1], c[1])
    return qc

def build_block(n_units, tag, rng):
    """Each unit = one independent draw/run: tau drawn INDEPENDENTLY per arm over the common band (variant b)."""
    circs, labels = [], []
    for u in range(n_units):
        tau_ce = int(rng.integers(0, TAU_MAX_NS))
        tau_cc = int(rng.integers(0, TAU_MAX_NS))
        for b in BASES:
            circs.append(ce_circuit(b, tau_ce, f"{tag}{u}_CE_{b}"))
            labels.append({"unit": u, "arm": "CE", "basis": b, "tau_ns": tau_ce})
            circs.append(cc_circuit(b, tau_cc, f"{tag}{u}_CC_{b}"))
            labels.append({"unit": u, "arm": "CC", "basis": b, "tau_ns": tau_cc})
    return circs, labels

def main():
    dry = "--dry-run" in sys.argv
    rng = np.random.default_rng(SEED)
    pre_c, pre_l = build_block(N_DRAWS, "PRE", rng)
    sci_c, sci_l = build_block(N_RUNS, "SCI", rng)
    print(f"[build] pre-run {len(pre_c)} circuits @{PRERUN_SHOTS} | science {len(sci_c)} circuits @{SCIENCE_SHOTS}")
    draws_hash = hashlib.sha256(json.dumps([l['tau_ns'] for l in pre_l + sci_l]).encode()).hexdigest()[:16]
    print(f"[custody] seed={SEED} committed; realized-draws sha256[:16]={draws_hash}")
    if dry:
        from qiskit_aer import AerSimulator
        sim = AerSimulator()
        tc = transpile(pre_c[:6] + sci_c[:6], sim, optimization_level=1, seed_transpiler=SEED)
        res = sim.run(tc, shots=4000).result()
        corr = {}
        for lab, c in zip(pre_l[:6] + sci_l[:6], tc):
            counts = res.get_counts(c); tot = sum(counts.values())
            e = sum(((-1) ** (int(k.replace(" ", "")[0]) + int(k.replace(" ", "")[1]))) * v for k, v in counts.items()) / tot
            corr[f"{lab['arm']}_{lab['basis']}_u{lab['unit']}"] = round(e, 4)
        print("[dry-run ideal correlators]", corr)
        ce = [v for k, v in corr.items() if k.startswith("CE")][:3]
        cc = [v for k, v in corr.items() if k.startswith("CC")][:3]
        print(f"  CE sign product = {np.prod(ce):+.4f} (QM repeatability forces all-positive)")
        print(f"  CC sign product = {np.prod(cc):+.4f} (entangled source is not forced)")
        return
    from ibm_multi_account import assert_explicit_account, service_for_submission, _load_env_files
    _load_env_files()
    acct = assert_explicit_account()
    if acct != "IBMQ_ALT3": raise SystemExit(f"prereg declares IBMQ_ALT3; got {acct} — REFUSING.")
    svc = service_for_submission(acct)
    u = svc.usage()
    remaining = float(u["usage_limit_seconds"]) - float(u["usage_consumed_seconds"])
    if u.get("usage_limit_reached") or remaining < EST_COST_S:
        raise SystemExit(f"FIT GATE REFUSES: remaining={remaining}s < est {EST_COST_S}s")
    print(f"[fit gate] {acct}: {remaining:.1f}s remaining >= est {EST_COST_S}s — OK")
    backend = None
    for name in DECLARED_BACKENDS:
        try:
            b = svc.backend(name)
            if b.status().operational: backend = b; break
        except Exception: continue
    print(f"[backend] {backend.name} queue={backend.status().pending_jobs}")
    props = backend.properties(); ro = {}
    for qq in range(backend.num_qubits):
        try: ro[qq] = props.readout_error(qq)
        except Exception: pass
    adj = {}
    for a, b_ in backend.coupling_map: adj.setdefault(a, set()).add(b_); adj.setdefault(b_, set()).add(a)
    q_ce = min(ro, key=ro.get)
    best_pair, best_s = None, 9e9
    for a, b_ in backend.coupling_map:
        if a in ro and b_ in ro and a != q_ce and b_ != q_ce:
            try: s = ro[a] + ro[b_] + props.gate_error("cz", (a, b_))
            except Exception: continue
            if s < best_s: best_pair, best_s = (a, b_), s
    print(f"[layout] live pick CE q{q_ce} (ro {ro[q_ce]:.4f}) | CC pair {best_pair} (score {best_s:.4f}) — never cached")
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    jobs = {}
    for tag, circs, shots, labels in (("prerun", pre_c, PRERUN_SHOTS, pre_l), ("science", sci_c, SCIENCE_SHOTS, sci_l)):
        tc = [transpile(c, backend, initial_layout=([q_ce] if c.num_qubits == 1 else list(best_pair)),
                        optimization_level=1, seed_transpiler=SEED) for c in circs]
        job = sampler.run(tc, shots=shots)
        jobs[tag] = job.job_id()
        print(f"[submitted] {tag}: job_id={job.job_id()} ({len(tc)} circuits @ {shots} shots)")
    man = {"cell": "H13-Cell2-CausalCompass", "prereg": PREREG, "account": acct, "backend": backend.name,
           "jobs": jobs, "seed": SEED, "tau_max_ns": TAU_MAX_NS, "n_draws": N_DRAWS, "n_runs": N_RUNS,
           "prerun_shots": PRERUN_SHOTS, "science_shots": SCIENCE_SHOTS,
           "layout": {"CE": q_ce, "CC": list(best_pair)}, "realized_draws_sha256_16": draws_hash,
           "labels_prerun": pre_l, "labels_science": sci_l,
           "fit_gate": {"remaining_at_submit": remaining, "est": EST_COST_S},
           "decoder": "tools/h13_cell2_decoder_elder.py (frozen pre-flight)"}
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     f"results/h13_cell2_manifest_{jobs['science']}.json")
    json.dump(man, open(p, "w"), indent=1)
    print(f"[manifest] {p}")

if __name__ == "__main__":
    main()
