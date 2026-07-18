#!/usr/bin/env python3
"""Exp163 — REPEATER WITH MEMORY: hold the match. C4853.
Entanglement-swap A-C (Exp162), then STORE for a swept delay tau before the witness reads it.
Deliverables: (1) the certified HOLD TIME t_50 — the storage time at which F crosses the 1/2
separable bound and the match stops being provable; (2) the PEDIGREE TEST — direct-Bell + the
identical delays on the SAME pinned physical qubits: does swapped entanglement decay at the
same rate as gate-made entanglement? (QM: decay is local physics, not pedigree.)

Fit: F(tau) = 0.25 + (F0 - 0.25) * exp(-tau / T_ent), parametric bootstrap through the fit.
Layout pinned across all circuits (transpile one reference at opt3, reuse its layout at opt1)
so both pedigrees age on identical T1/T2 — the C4199 baseline-to-qubits rule made physical.

FENCE: memory = idle storage on one die (no re-cooling, no QEC, no independent sources);
a hold-time measurement of the repeater primitive, not a deployed repeater.

Usage: --selftest | --submit [--backend ibm_fez --shots 4096] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import _parity, fidelity, SETTINGS, WITNESS

TAUS_US = [0, 5, 10, 20, 40, 80, 160]
ARMS = ("swap", "direct")
BOOT = 1000


def memory_circuit(arm, tau_us, setting):
    """Exp162 swap (or direct Bell) on A=q0..C=q3, then delay tau on A and C, then witness."""
    qc = QuantumCircuit(4, 4)
    if arm == "direct":
        qc.h(0); qc.cx(0, 3)
    else:
        qc.h(0); qc.cx(0, 1)
        qc.h(2); qc.cx(2, 3)
        qc.barrier()
        qc.cx(1, 2); qc.h(1)
        qc.measure(1, 0); qc.measure(2, 1)
        with qc.if_test((qc.clbits[1], 1)): qc.x(3)
        with qc.if_test((qc.clbits[0], 1)): qc.z(3)
    qc.barrier()
    if tau_us > 0:
        qc.delay(tau_us, 0, unit="us")
        qc.delay(tau_us, 3, unit="us")
    qc.barrier()
    for q in (0, 3):
        if setting == "XX":
            qc.h(q)
        elif setting == "YY":
            qc.sdg(q); qc.h(q)
    qc.measure(0, 2); qc.measure(3, 3)
    return qc


def fit_decay(taus, Fs, sigmas, rng=None):
    """Least-squares fit of F(tau)=0.25+(F0-0.25)exp(-tau/T) on a log-linearized grid search +
    refinement. Returns (F0, T_ent). Robust, no scipy."""
    taus = np.asarray(taus, float); Fs = np.asarray(Fs, float)
    best = None
    for T in np.geomspace(2, 2000, 400):
        w = np.exp(-taus / T)
        # linear LSQ for a in F = 0.25 + a*w
        a = np.sum(w * (Fs - 0.25)) / np.sum(w * w)
        r = np.sum((0.25 + a * w - Fs) ** 2)
        if best is None or r < best[0]:
            best = (r, a, T)
    _, a, T = best
    return 0.25 + a, T


def t50(F0, T):
    """Storage time where F crosses the 1/2 witness."""
    return float(T * np.log((F0 - 0.25) / (WITNESS - 0.25))) if F0 > WITNESS else 0.0


def selftest():
    """(A) Noiseless Aer: delays are noise-free in sim -> F=1 flat at every tau, both arms
    (verifies circuits+delay compile). (B) SYNTHETIC-DECAY gate: inject exponential decay
    (T=60us, F0=0.85) + binomial noise; fitter must recover T within 25% and t_50 within 30%."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 3000
    print("Exp163 selftest")
    for arm in ARMS:
        Fs = []
        for tau in (0, 40, 160):
            par = {s: _parity(sim.run(memory_circuit(arm, tau, s), shots=shots).result()
                              .get_counts(), shots) for s in SETTINGS}
            Fs.append(fidelity(par))
        print(f"  [A] {arm:>6} noiseless F at tau=0/40/160us: {['%.3f' % f for f in Fs]}")
        assert all(f > 0.99 for f in Fs), f"{arm}: noiseless memory must be lossless"
    rng = np.random.default_rng(163)
    T_true, F0_true = 60.0, 0.85
    taus = np.array(TAUS_US, float)
    F_true = 0.25 + (F0_true - 0.25) * np.exp(-taus / T_true)
    F_noisy = F_true + rng.normal(0, 0.008, len(taus))
    F0_fit, T_fit = fit_decay(taus, F_noisy, None)
    t_true, t_fit = t50(F0_true, T_true), t50(F0_fit, T_fit)
    print(f"  [B] synthetic: T {T_fit:.0f}us (true 60), t_50 {t_fit:.0f}us (true {t_true:.0f})")
    assert abs(T_fit - T_true) / T_true < 0.25 and abs(t_fit - t_true) / t_true < 0.30, "fitter FAIL"
    print("SELFTEST PASS: circuits+delays compile lossless; fitter recovers synthetic decay. Cleared.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    # pin one layout for every circuit: transpile a reference at opt3, reuse its qubits at opt1
    ref = transpile(memory_circuit("swap", 0, "ZZ"), backend=backend, optimization_level=3)
    layout = [ref.layout.final_index_layout()[i] for i in range(4)]
    print(f"pinned physical qubits (A,B1,B2,C): {layout}")
    circuits, order = [], []
    for arm in ARMS:
        for tau in TAUS_US:
            for s in SETTINGS:
                qc = memory_circuit(arm, tau, s)
                circuits.append(transpile(qc, backend=backend, optimization_level=1,
                                          initial_layout=layout))
                order.append([arm, tau, s])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 163, "slug": "memory", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "layout": layout, "taus_us": TAUS_US,
                "prereg": {"primary": "hold time t_50(swap) reported with bootstrap CI; "
                                      "F(0) must clear witness >5 sigma first",
                           "pedigree": "T_ent(swap)/T_ent(direct) in [0.7, 1.4] = same physics; "
                                       "outside with non-overlapping CIs = surprise finding",
                           "prediction": "T_ent 40-160 us; t_50(swap) 30-150 us; ratio 0.7-1.4"},
                "note": "entanglement hold time: swap + swept storage delay vs matched direct-Bell "
                        "on pinned qubits; fence: idle memory, not a deployed repeater"}
    out = os.path.join(HERE, "..", "results", "exp163_memory_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits = 2 arms x {len(TAUS_US)} taus x 3, "
          f"{shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp163_memory_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; rng = np.random.default_rng(1630)
    par = {}
    for idx, (arm, tau, s) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        par.setdefault((arm, tau), {})[s] = _parity(getattr(r.data, reg).get_counts(), shots)
    print(f"Exp163 MEMORY decode | job {man['job_id']} | qubits {man['layout']}")
    out = {"job_id": man["job_id"], "layout": man["layout"], "curves": {}}
    fits = {}
    for arm in ARMS:
        Fs = [fidelity(par[(arm, t)]) for t in man["taus_us"]]
        out["curves"][arm] = {str(t): float(f) for t, f in zip(man["taus_us"], Fs)}
        F0, T = fit_decay(man["taus_us"], Fs, None)
        # bootstrap
        Ts = []
        se_F = 0.75 / np.sqrt(shots)
        for _ in range(BOOT):
            Fb = np.array(Fs) + rng.normal(0, se_F, len(Fs))
            _, Tb = fit_decay(man["taus_us"], Fb, None)
            Ts.append(Tb)
        Tlo, Thi = np.percentile(Ts, [16, 84])
        fits[arm] = (F0, T, Tlo, Thi)
        print(f"  {arm:>6}: F(tau) = " + " ".join(f"{f:.3f}" for f in Fs))
        print(f"          F0={F0:.3f}  T_ent={T:.0f}us [{Tlo:.0f},{Thi:.0f}]  t_50={t50(F0,T):.0f}us")
    ratio = fits["swap"][1] / fits["direct"][1]
    same = 0.7 < ratio < 1.4
    F0s = out["curves"]["swap"]["0"]
    nsig0 = (F0s - WITNESS) / (0.75 / np.sqrt(shots))
    print(f"\nWITNESS AT tau=0: swap F = {F0s:.3f} ({nsig0:.0f} sigma over 1/2)")
    print(f"HOLD TIME (certified entanglement): t_50(swap) = {t50(*fits['swap'][:2]):.0f} us")
    print(f"PEDIGREE: T_ent ratio swap/direct = {ratio:.2f} "
          f"({'SAME physics — decay is local, not pedigree' if same else 'DIFFERENT — surprise, check CIs'})")
    out.update({"fits": {a: {"F0": float(fits[a][0]), "T_ent_us": float(fits[a][1]),
                             "T_lo": float(fits[a][2]), "T_hi": float(fits[a][3]),
                             "t50_us": float(t50(*fits[a][:2]))} for a in ARMS},
                "ratio": float(ratio), "pedigree_same": bool(same),
                "witness_sigma_tau0": float(nsig0)})
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp163_memory_decode.json"), "w"), indent=1)
    print("-> results/exp163_memory_decode.json")


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
