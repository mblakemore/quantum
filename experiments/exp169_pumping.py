#!/usr/bin/env python3
"""Exp169 — ENTANGLEMENT PUMPING: how many distillation rounds pay before the gates eat the gain?
C4859. The lower-overhead follow-on to the Exp167 null. Pumping does NOT reduce per-round gate
cost (still ~2 bilateral CNOTs) — it reduces MEMORY cost (pump one fresh sacrificial pair into
the kept pair per round). So the honest question is the CROSSOVER: run it in Exp165's favorable
structured-storage-noise regime (round 1 gained +0.29 there) and measure F after 0, 1, 2 pump
rounds. Prediction: round 1 pays big, round 2 is the crossover (gain shrinks to ~the fixed
overhead) -> "one useful round on Heron r2", the quantitative answer.

Each pump round r: prepare a fresh Bell pair, degrade it 10us (same structured noise as the kept
pair), DEJMPS it into the kept pair, keep coincidence. Witness F on the kept pair after r rounds.

Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import _parity, fidelity, SETTINGS, WITNESS

TAU_US = 10.0
ROUNDS = [0, 1, 2]


def pump_circuit(rounds, setting, tau_us=TAU_US, inject_rz=0.0):
    """Kept pair = q0(A),q1(B). Each pump round uses a fresh sacrificial pair q2,q3 (reused
    qubits across rounds via mid-circuit measure+reset). DEJMPS the sacrificial into the kept
    pair, coincidence-measure it. Witness F(kept) in `setting`. Coincidence clbits c0.. per round."""
    ncl = 2 + 2 * max(rounds, 1)
    qc = QuantumCircuit(4, ncl)
    qc.h(0); qc.cx(0, 1)                       # kept pair
    if tau_us > 0:
        qc.barrier(); qc.delay(tau_us, 0, unit="us"); qc.delay(tau_us, 1, unit="us")
    if inject_rz:
        qc.rz(inject_rz, 1)
    cbit = 2
    for r in range(rounds):
        if r > 0:
            qc.reset(2); qc.reset(3)
        qc.h(2); qc.cx(2, 3)                   # fresh sacrificial pair
        if tau_us > 0:
            qc.barrier(); qc.delay(tau_us, 2, unit="us"); qc.delay(tau_us, 3, unit="us")
        if inject_rz:
            qc.rz(inject_rz, 3)
        qc.barrier()
        qc.rx(np.pi / 2, 0); qc.rx(np.pi / 2, 2)      # DEJMPS
        qc.rx(-np.pi / 2, 1); qc.rx(-np.pi / 2, 3)
        qc.cx(0, 2); qc.cx(1, 3)
        qc.rx(-np.pi / 2, 0); qc.rx(np.pi / 2, 1)
        qc.measure(2, cbit); qc.measure(3, cbit + 1)  # sacrificial -> coincidence
        cbit += 2
        qc.barrier()
    for q in (0, 1):
        if setting == "XX": qc.h(q)
        elif setting == "YY": qc.sdg(q); qc.h(q)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc, ncl


def _parity_coin(counts, shots, ncl):
    """<Z0 Z1> on the kept pair (c0,c1) conditioned on ALL round-coincidences (c2==c3, c4==c5..)."""
    acc = tot = 0
    for bstr, n in counts.items():
        b = bstr.replace(" ", "")
        coin = all(b[-1 - k] == b[-2 - k] for k in range(2, ncl, 2))
        if not coin: continue
        s = (1 if b[-1] == "0" else -1) * (1 if b[-2] == "0" else -1)
        acc += s * n; tot += n
    return (acc / tot if tot else 0.0), tot


def _F_round(gc, rounds, shots, ncl):
    par = {}
    for s in SETTINGS:
        p, tot = _parity_coin(gc(rounds, s), shots, ncl)
        par[s] = p
    p_succ = tot / shots
    return fidelity(par), p_succ


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 6000
    print("Exp169 selftest")
    cache = {}
    def gc(rounds, s, rz=0.0):
        k = (rounds, s, rz)
        if k not in cache:
            qc, ncl = pump_circuit(rounds, s, TAU_US, rz)
            cache[k] = (sim.run(qc, shots=shots).result().get_counts(), ncl)
        return cache[k]
    for rounds in ROUNDS:
        _, ncl = pump_circuit(rounds, "ZZ")
        F, p = _F_round(lambda r, s: gc(r, s)[0], rounds, shots, ncl)
        print(f"  [A] noiseless r={rounds}: F={F:.3f} p_success={p:.2f}")
        assert F > 0.99, f"noiseless pumping must stay perfect (r={rounds})"
    # [B] injected dephasing: r=1 must beat r=0 (distillation works on the class)
    F0, _ = _F_round(lambda r, s: gc(r, s, 0.8)[0], 0, shots, pump_circuit(0, "ZZ")[1])
    F1, _ = _F_round(lambda r, s: gc(r, s, 0.8)[0], 1, shots, pump_circuit(1, "ZZ")[1])
    print(f"  [B] injected Rz(0.8): F(r=0)={F0:.3f} -> F(r=1)={F1:.3f}")
    assert F1 > F0 + 0.05, "round-1 pump must purify the dephasing class in sim"
    print("SELFTEST PASS: algebra exact at all rounds; round-1 pump purifies the class. Cleared.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    layout = json.load(open(os.path.join(HERE, "..", "results",
                       "exp163_memory_manifest.json")))["layout"]
    circuits, order = [], []
    for rounds in ROUNDS:
        for s in SETTINGS:
            qc, ncl = pump_circuit(rounds, s)
            circuits.append(transpile(qc, backend=backend, optimization_level=1, initial_layout=layout))
            order.append([rounds, s, ncl])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 169, "slug": "pumping", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "layout": layout, "tau_us": TAU_US,
                "prereg": {"primary": "map F vs pump round; find the crossover (round where gain <= overhead)",
                           "prediction": "F: r0~0.6, r1~0.75-0.85 (pays), r2 flat-or-down (crossover); "
                                         "one useful round on Heron r2"}}
    out = os.path.join(HERE, "..", "results", "exp169_pumping_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp169_pumping_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (rounds, s, ncl) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        raw[(rounds, s)] = (getattr(r.data, reg).get_counts(), ncl)
    print(f"Exp169 ENTANGLEMENT PUMPING decode | job {man['job_id']} | qubits {man['layout']}")
    Fs, ps = {}, {}
    for rounds in ROUNDS:
        ncl = raw[(rounds, "ZZ")][1]
        F, p = _F_round(lambda rr, s: raw[(rr, s)][0], rounds, shots, ncl)
        Fs[rounds] = F; ps[rounds] = p
        print(f"  round {rounds}: F = {F:.3f}  (p_success={p:.2f})  witness {'✓' if F>WITNESS else '✗'}")
    g1 = Fs[1] - Fs[0]; g2 = Fs[2] - Fs[1]
    print(f"\nPUMP GAINS: round1 {g1:+.3f} | round2 {g2:+.3f}")
    if g1 > 0.02 and g2 <= 0.02:
        v = f"ONE USEFUL ROUND — round 1 pays ({g1:+.3f}), round 2 is the crossover ({g2:+.3f}): the gate overhead catches the shrinking gain, exactly as priced"
    elif g1 > 0.02 and g2 > 0.02:
        v = f"TWO ROUNDS PAY — pumping climbs past round 1 ({g1:+.3f}, {g2:+.3f}); better than the 167 wall predicted"
    else:
        v = f"PUMPING UNDERWATER even at round 1 ({g1:+.3f}) — the storage-regime gain didn't survive the reused-ancilla depth"
    print(f"VERDICT: {v}")
    out = {"job_id": man["job_id"], "F_by_round": {str(k): float(v) for k, v in Fs.items()},
           "p_success": {str(k): float(v) for k, v in ps.items()},
           "gain_round1": float(g1), "gain_round2": float(g2), "verdict": v}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp169_pumping_decode.json"), "w"), indent=1)
    print("-> results/exp169_pumping_decode.json")


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
