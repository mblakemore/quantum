#!/usr/bin/env python3
"""Exp165 — PURIFICATION: two faded pairs in, one brighter pair out. C4855.
The last repeater primitive, run on the wing's own noise: both Bell pairs are degraded by 10us
of plain (unechoed) storage — the Exp163/164 memory decay — then DEJMPS distills them:
local Rx(+-pi/2), bilateral CNOTs, measure the sacrificial pair, KEEP THE COINCIDENCES.

GATES (pre-registered): (1) F_kept > F_input at >3 sigma, both measured same-job with identical
storage; (2) free falsifier from the same shots: the DISCARD pile (anti-coincidence) must be
WORSE than the input; (3) success probability reported. Named risk: heavy-hex has no 4-cycles ->
the bilateral CNOTs pay routing SWAPs the input arm does not; a null prices purification on
this topology (informative).

ARMS: input (one stored pair, witness) | purify (two stored pairs + DEJMPS + witness on kept
pair, conditioned) | fresh (purify with tau=0: protocol overhead visible at high F).

Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import WITNESS, SETTINGS

TAU_US = 10.0
ARMS = ("input", "purify", "fresh")


def circuit(arm, setting, tau_us=TAU_US, inject_rz=0.0):
    """input: Bell(q0,q1)+storage+witness. purify/fresh: two pairs, storage (tau or 0), DEJMPS,
    witness kept pair conditioned on the sacrificial measurement (c0,c1). inject_rz: sim-only
    synthetic dephasing on q1(,q3)."""
    if arm == "input":
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.cx(0, 1)
        if tau_us > 0:
            qc.barrier(); qc.delay(tau_us, 0, unit="us"); qc.delay(tau_us, 1, unit="us")
        if inject_rz:
            qc.rz(inject_rz, 1)
        qc.barrier()
        for q in (0, 1):
            if setting == "XX": qc.h(q)
            elif setting == "YY": qc.sdg(q); qc.h(q)
        qc.measure(0, 0); qc.measure(1, 1)
        return qc
    qc = QuantumCircuit(4, 4)
    qc.h(0); qc.cx(0, 1)                       # pair 1 (kept):     A=q0, B=q1
    qc.h(2); qc.cx(2, 3)                       # pair 2 (sacrifice): A=q2, B=q3
    t = 0.0 if arm == "fresh" else tau_us
    if t > 0:
        qc.barrier()
        for q in range(4): qc.delay(t, q, unit="us")
    if inject_rz:
        qc.rz(inject_rz, 1); qc.rz(inject_rz, 3)
    qc.barrier()
    for q in (0, 2): qc.rx(np.pi / 2, q)       # DEJMPS local rotations (A side)
    for q in (1, 3): qc.rx(-np.pi / 2, q)      # (B side)
    qc.cx(0, 2); qc.cx(1, 3)                   # bilateral CNOTs
    for q in (0,): qc.rx(-np.pi / 2, q)        # undo rotations on the kept pair
    for q in (1,): qc.rx(np.pi / 2, q)
    qc.measure(2, 0); qc.measure(3, 1)         # sacrificial pair -> c0,c1 (coincidence keep)
    qc.barrier()
    for q in (0, 1):
        if setting == "XX": qc.h(q)
        elif setting == "YY": qc.sdg(q); qc.h(q)
    qc.measure(0, 2); qc.measure(1, 3)
    return qc


def _parity2(counts, shots, hi_bits, cond=None):
    """Parity of the two bits at positions hi_bits (from right, 0-indexed), optionally
    conditioned on (b0==b1) coincidence (cond=True) or anti (cond=False). Returns (parity, n)."""
    acc = n = 0
    for b, c in counts.items():
        b = b.replace(" ", "")
        if cond is not None:
            coin = (b[-1] == b[-2])
            if coin != cond: continue
        s = (1 if b[-1 - hi_bits[0]] == "0" else -1) * (1 if b[-1 - hi_bits[1]] == "0" else -1)
        acc += s * c; n += c
    return (acc / n if n else 0.0), n


def _F(par):
    return (1 + par["ZZ"] + par["XX"] - par["YY"]) / 4


def _run(sim, arm, shots, tau, rz):
    par_k, par_a, ns = {}, {}, {}
    for s in SETTINGS:
        counts = sim.run(circuit(arm, s, tau, rz), shots=shots).result().get_counts()
        if arm == "input":
            par_k[s], _ = _parity2(counts, shots, (0, 1))
        else:
            par_k[s], ns[s] = _parity2(counts, shots, (2, 3), cond=True)
            par_a[s], _ = _parity2(counts, shots, (2, 3), cond=False)
    return par_k, par_a, ns


def selftest():
    """[A] noiseless fresh: F_kept=1, coincidence deterministic. [B] injected dephasing
    (Rz 0.7 on B qubits): purified F must EXCEED the degraded input F (machinery proven)."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    print("Exp165 selftest")
    pk, _, ns = _run(sim, "fresh", shots, 0, 0.0)
    F = _F(pk); psucc = np.mean([ns[s] / shots for s in SETTINGS])
    print(f"  [A] noiseless fresh purify: F_kept={F:.3f}, p_success={psucc:.3f}")
    assert F > 0.99 and psucc > 0.99, "noiseless DEJMPS must keep Phi+ with deterministic coincidence"
    pi_, _, _ = _run(sim, "input", shots, 0, 0.7)
    Fin = _F(pi_)
    pk2, pa2, ns2 = _run(sim, "purify", shots, 0, 0.7)
    Fout, Fanti = _F(pk2), _F(pa2)
    print(f"  [B] injected Rz(0.7): F_in={Fin:.3f} -> F_out={Fout:.3f} (anti {Fanti:.3f}, "
          f"p={np.mean([ns2[s]/shots for s in SETTINGS]):.2f})")
    assert Fout > Fin + 0.03, "purification must beat degraded input in sim"
    assert Fanti < Fin, "discard pile must be worse than input"
    print("SELFTEST PASS: exact on fresh pairs; provably purifies the dephasing class; "
          "discard-pile falsifier armed. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for s in SETTINGS:
            circuits.append(transpile(circuit(arm, s), backend=backend, optimization_level=3))
            order.append([arm, s])
    twoq = [c.depth(lambda i: len(i.qubits) == 2) for c in circuits]
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 165, "slug": "purify", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "tau_us": TAU_US, "twoq_depths": twoq,
                "prereg": {"primary": "F_kept > F_input at >3 sigma (same job, same storage)",
                           "falsifier": "F_anti < F_input (discard pile worse)",
                           "prediction": "F_in 0.55-0.68; gain +0.03-0.12; p_success 0.4-0.7; "
                                         "null = routing SWAPs eat the gain (prices the topology)"}}
    out = os.path.join(HERE, "..", "results", "exp165_purify_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, 2q-depths {twoq}, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp165_purify_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        raw[(arm, s)] = getattr(r.data, reg).get_counts()
    out = {"job_id": man["job_id"]}
    print(f"Exp165 PURIFY decode | job {man['job_id']} | backend {man['backend']} | tau={man['tau_us']}us")
    Fs, ps = {}, {}
    for arm in ARMS:
        par_k, par_a, n_k = {}, {}, {}
        for s in SETTINGS:
            if arm == "input":
                par_k[s], _ = _parity2(raw[(arm, s)], shots, (0, 1))
            else:
                par_k[s], n_k[s] = _parity2(raw[(arm, s)], shots, (2, 3), cond=True)
                par_a[s], _ = _parity2(raw[(arm, s)], shots, (2, 3), cond=False)
        Fs[arm] = _F(par_k)
        if arm != "input":
            Fs[arm + "_anti"] = _F(par_a)
            ps[arm] = float(np.mean([n_k[s] / shots for s in SETTINGS]))
            print(f"  {arm:>7}: F_kept={Fs[arm]:.3f}  F_discard={Fs[arm+'_anti']:.3f}  p_success={ps[arm]:.2f}")
        else:
            print(f"  {arm:>7}: F={Fs[arm]:.3f}")
    n_eff = ps["purify"] * shots
    se = float(np.sqrt(0.75 ** 2 / n_eff + 0.75 ** 2 / shots))
    gain = Fs["purify"] - Fs["input"]
    nsig = gain / se
    falsifier = Fs["purify_anti"] < Fs["input"]
    ok = gain > 0 and nsig > 3 and falsifier
    print(f"\nPRIMARY: F {Fs['input']:.3f} -> {Fs['purify']:.3f}  gain {gain:+.3f} ({nsig:+.1f} sigma)")
    print(f"FALSIFIER: discard pile {Fs['purify_anti']:.3f} {'<' if falsifier else '>='} input "
          f"({'garbage confirmed' if falsifier else 'FALSIFIER FAILED'})")
    print(f"FRESH-PAIR overhead check: fresh purify F={Fs['fresh']:.3f} (protocol cost at high F)")
    print(f"VERDICT: {'PURIFICATION WORKS — two faded pairs traded for one brighter pair' if ok else 'NULL/FAIL — gain not resolved (routing price vs gain; honest accounting above)'}")
    out.update({"F": {k: float(v) for k, v in Fs.items()}, "p_success": ps,
                "gain": float(gain), "sigma": float(nsig), "falsifier_ok": bool(falsifier),
                "verdict_ok": bool(ok)})
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp165_purify_decode.json"), "w"), indent=1)
    print("-> results/exp165_purify_decode.json")


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
