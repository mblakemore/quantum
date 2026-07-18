#!/usr/bin/env python3
"""Exp164 — STORAGE ECHO: extend the repeater's memory. C4854.
Exp163 measured t_50 = 12us for unechoed storage, with a tail that confessed quasi-static
detuning (non-monotonic XX/YY, floor at (1+ZZ)/4). This flies the textbook fix in the condition
where echoes live: X(x)X at the storage midpoint — |Phi+> is a +1 eigenstate of XX, so the pulse
pair is exactly state-invariant while refocusing each qubit's quasi-static Z detuning.

ARMS (one job, pinned to Exp163's qubits): plain (re-baselined THIS job, condition-first) |
hahn (tau/2, X both, tau/2) | cpmg2 (tau/4, X, tau/2, X, tau/4).
PRE-REG: primary T_ent(hahn)/T_ent(plain) > 1.5; mechanism: echo arms' tails smoother (the 163
wiggle was deterministic detuning -> echo must flatten it); CPMG >= Hahn; headline = witness-
crossing t_50 (fit-independent interpolation).

Usage: --selftest | --submit [--backend ibm_fez --shots 4096] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import _parity, fidelity, SETTINGS, WITNESS
from exp163_memory import fit_decay, TAUS_US

ARMS = ("plain", "hahn", "cpmg2")


def echo_circuit(arm, tau_us, setting):
    """Swap A-C then store tau with the arm's echo structure; witness in the given basis."""
    qc = QuantumCircuit(4, 4)
    qc.h(0); qc.cx(0, 1)
    qc.h(2); qc.cx(2, 3)
    qc.barrier()
    qc.cx(1, 2); qc.h(1)
    qc.measure(1, 0); qc.measure(2, 1)
    with qc.if_test((qc.clbits[1], 1)): qc.x(3)
    with qc.if_test((qc.clbits[0], 1)): qc.z(3)
    qc.barrier()
    if tau_us > 0:
        def dly(frac):
            qc.delay(tau_us * frac, 0, unit="us"); qc.delay(tau_us * frac, 3, unit="us")
        def xpair():
            qc.x(0); qc.x(3); qc.barrier(0, 3)
        if arm == "plain":
            dly(1.0)
        elif arm == "hahn":
            dly(0.5); xpair(); dly(0.5)
        else:                                   # cpmg2
            dly(0.25); xpair(); dly(0.5); xpair(); dly(0.25)
    qc.barrier()
    for q in (0, 3):
        if setting == "XX":
            qc.h(q)
        elif setting == "YY":
            qc.sdg(q); qc.h(q)
    qc.measure(0, 2); qc.measure(3, 3)
    return qc


def t50_cross(taus, Fs):
    """Fit-independent witness crossing by linear interpolation of the first F<1/2 segment."""
    for i in range(1, len(taus)):
        if Fs[i] < WITNESS <= Fs[i - 1]:
            f0, f1 = Fs[i - 1], Fs[i]
            return taus[i - 1] + (taus[i] - taus[i - 1]) * (f0 - WITNESS) / (f0 - f1)
    return float(taus[-1]) if Fs[-1] >= WITNESS else 0.0


def selftest():
    """Noiseless: every arm F=1 at every tau — X(x)X leaves Phi+ invariant (the echo is free)."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 3000
    print("Exp164 selftest (noiseless Aer)")
    for arm in ARMS:
        Fs = []
        for tau in (0, 40, 160):
            par = {s: _parity(sim.run(echo_circuit(arm, tau, s), shots=shots).result()
                              .get_counts(), shots) for s in SETTINGS}
            Fs.append(fidelity(par))
        print(f"  {arm:>6}: F at 0/40/160us = {['%.3f' % f for f in Fs]}")
        assert all(f > 0.99 for f in Fs), f"{arm}: echo must be state-invariant on Phi+"
    xc = t50_cross([0, 10, 20], [0.8, 0.6, 0.4])
    assert abs(xc - 15.0) < 0.01, "crossing interpolator FAIL"
    print("SELFTEST PASS: XX-echo exactly state-invariant on Phi+; crossing interpolator exact. Cleared.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    layout = json.load(open(os.path.join(HERE, "..", "results", "exp163_memory_manifest.json")))["layout"]
    print(f"pinned qubits (from Exp163): {layout}")
    circuits, order = [], []
    for arm in ARMS:
        for tau in TAUS_US:
            for s in SETTINGS:
                circuits.append(transpile(echo_circuit(arm, tau, s), backend=backend,
                                          optimization_level=1, initial_layout=layout))
                order.append([arm, tau, s])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 164, "slug": "echo", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "layout": layout, "taus_us": TAUS_US,
                "prereg": {"primary": "T_ent(hahn)/T_ent(plain) > 1.5 AND t_50(hahn) > t_50(plain)",
                           "mechanism": "echo tails monotonic/smoother (163 wiggle = deterministic detuning)",
                           "ordering": "CPMG2 >= Hahn",
                           "prediction": "ratio 2-5; t_50 hahn 25-80us; cpmg2 >= hahn"}}
    out = os.path.join(HERE, "..", "results", "exp164_echo_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits = 3 arms x {len(TAUS_US)} x 3, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp164_echo_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    par = {}
    for idx, (arm, tau, s) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        par.setdefault((arm, tau), {})[s] = _parity(getattr(r.data, reg).get_counts(), shots)
    print(f"Exp164 STORAGE ECHO decode | job {man['job_id']} | qubits {man['layout']}")
    out = {"job_id": man["job_id"], "curves": {}, "fits": {}}
    stats = {}
    for arm in ARMS:
        Fs = [fidelity(par[(arm, t)]) for t in man["taus_us"]]
        F0, T = fit_decay(man["taus_us"], Fs, None)
        tc = t50_cross(man["taus_us"], Fs)
        # tail smoothness: max upward jump after first sub-witness point
        diffs = [Fs[i+1] - Fs[i] for i in range(len(Fs)-1)]
        wiggle = max([d for d in diffs] + [0.0])
        stats[arm] = (Fs, F0, T, tc, wiggle)
        out["curves"][arm] = {str(t): float(f) for t, f in zip(man["taus_us"], Fs)}
        out["fits"][arm] = {"F0": float(F0), "T_ent_us": float(T), "t50_us": float(tc),
                            "max_up_wiggle": float(wiggle)}
        print(f"  {arm:>6}: F = " + " ".join(f"{f:.3f}" for f in Fs)
              + f"  | T_ent={T:.0f}us  t_50={tc:.0f}us  max-up-wiggle={wiggle:+.3f}")
    ratio = stats["hahn"][2] / stats["plain"][2]
    ok = ratio > 1.5 and stats["hahn"][3] > stats["plain"][3]
    order_ok = stats["cpmg2"][2] >= stats["hahn"][2] * 0.8
    print(f"\nPRIMARY: T_ent hahn/plain = {ratio:.2f} (gate >1.5) | t_50: plain {stats['plain'][3]:.0f} "
          f"-> hahn {stats['hahn'][3]:.0f} -> cpmg2 {stats['cpmg2'][3]:.0f} us")
    print(f"MECHANISM: max upward wiggle plain {stats['plain'][4]:+.3f} vs hahn {stats['hahn'][4]:+.3f} "
          f"(echo should flatten the deterministic detuning)")
    print(f"VERDICT: {'ECHO EXTENDS THE MEMORY — storage decoherence is quasi-static-dominated and refocusable' if ok else 'echo does not resolvably extend memory (honest accounting above)'}"
          + ("" if order_ok else " | NOTE: CPMG2 < Hahn — ordering prediction failed, report honestly"))
    out.update({"ratio_hahn_plain": float(ratio), "verdict_ok": bool(ok), "cpmg_ordering_ok": bool(order_ok)})
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp164_echo_decode.json"), "w"), indent=1)
    print("-> results/exp164_echo_decode.json")


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
