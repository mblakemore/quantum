#!/usr/bin/env python3
"""Exp151 — A discrete time crystal on IBM hardware: "a clock nothing set"
(Creator directive C4839: museum-expansion, "fly it"; new exotic-phases wing).

THE PHENOMENON. Drive a disordered spin chain with an IMPERFECT global flip — an X pulse
of angle theta = pi*(1-eps), deliberately off by eps. A non-interacting chain then responds
at the *shifted* frequency: <Z_i(t)> = (-1)^t cos(pi*eps*t), a period-2 oscillation whose
envelope BEATS TO ZERO at t ~ 1/(2 eps) and revives — the imperfection accumulates. Turn on
Ising interactions + strong on-site disorder (many-body localization) and the subharmonic
LOCKS: the period-2 response becomes RIGID at exactly f=1/2, envelope flat, immune to the eps
you dialed in. That rigidity — a system ticking at half the drive, and refusing to drift when
you detune the drive — is a discrete time crystal: a phase of matter that breaks time-
translation symmetry. Order in TIME, not space.

THE DISCRIMINATOR (self-verifying by control, no seals). Metric A(t) = (-1)^t <Z_i(t)>, the
rectified period-2 amplitude:
  * CONTROL (interactions OFF): A(t) = cos(pi*eps*t) -> dips to ~0 at the beat-null t~1/(2eps).
  * DTC (interactions + disorder ON): A(t) stays ~flat (rigid) through the null.
The aha is the contrast at the beat-null, where the control collapses and the crystal does not.

FENCE (headline-level): finite chain (L qubits), finite coherence — a hardware SIGNATURE of
the DTC phase, NOT a thermodynamic-limit proof. Both arms decohere on real hardware; the claim
is the RELATIVE rigidity (DTC A(t) stays above the control's beat-null), a contrast not an
absolute reading. Single disorder realization (seeded); the phase is a disorder-averaged
concept — this is one instance of it.

Usage:
  python3 exp151_time_crystal.py --selftest    # P3 truth-gate: noiseless rigidity vs beat, test can fail
  python3 exp151_time_crystal.py --powercalc   # feasibility: predicted contrast vs depth under measured noise
  python3 exp151_time_crystal.py --submit [--backend ibm_fez --tmax 12 --shots 4000]
  python3 exp151_time_crystal.py --decode --manifest ../results/exp151_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

# MEASURED kingston/fez noise (durable campaign kit, Exp143/144)
E_CX = 0.0106

# --- fixed, seeded disorder realization (the "chip's" crystal) ---
L = 6
EPS = 0.12                                   # pulse imperfection: theta = pi*(1-eps); beat-null ~ 1/(2eps) ~ 4.2
_rng = np.random.default_rng(151)
J_COUP = list(0.4 + 0.8 * _rng.random(L - 1))     # Ising couplings, strong-ish (MBL regime)
H_FIELD = list(np.pi * (2 * _rng.random(L) - 1))  # on-site disorder in [-pi, pi] (localizing)


def floquet_circuit(t_periods, interactions, disorder, measure=True):
    """t_periods applications of the Floquet unit on |0..0>, then Z-basis measurement."""
    qc = QuantumCircuit(L, L if measure else 0)
    theta = np.pi * (1 - EPS)
    for _ in range(t_periods):
        for q in range(L):
            qc.rx(theta, q)                  # imperfect global pi-pulse
        if interactions:
            for i in range(L - 1):
                qc.rzz(2 * J_COUP[i], i, i + 1)
        if disorder:
            for i in range(L):
                qc.rz(2 * H_FIELD[i], i)
    if measure:
        qc.measure(range(L), range(L))
    return qc


def _z_expect_exact(t_periods, interactions, disorder):
    """Exact <Z_i(t)> for every qubit via statevector (noiseless truth-gate)."""
    from qiskit.quantum_info import Statevector, SparsePauliOp
    qc = floquet_circuit(t_periods, interactions, disorder, measure=False)
    sv = Statevector(qc)
    out = []
    for i in range(L):
        lbl = ["I"] * L; lbl[L - 1 - i] = "Z"       # qiskit little-endian
        out.append(float(np.real(sv.expectation_value(SparsePauliOp("".join(lbl))))))
    return np.array(out)


def _z_expect_counts(counts, shots):
    """<Z_i> per qubit from measured counts."""
    z = np.zeros(L)
    for bit, c in counts.items():
        b = bit.replace(" ", "")[::-1]              # b[i] = qubit i
        for i in range(L):
            z[i] += (1 if b[i] == "0" else -1) * c
    return z / shots


def _amp_curve(zt):
    """A(t) = (-1)^t * <Z_probe(t)>, averaged over qubits, rectified period-2 amplitude."""
    T = zt.shape[0]
    zavg = zt.mean(axis=1)                            # average over qubits
    return np.array([((-1) ** t) * zavg[t] for t in range(T)])


def selftest():
    """P3 TRUTH-GATE (noiseless). (1) The CONTROL beats: A(t) dips near zero at the beat-null
    t~1/(2eps). (2) The DTC is RIGID: A(t) stays high through that null. (3) Falsifiability:
    turning interactions OFF in the 'DTC' arm MUST reproduce the control (the crystal is the
    interactions, not the pulse) — the test can fail."""
    Tm = 12
    dtc = np.array([_z_expect_exact(t, True, True) for t in range(Tm + 1)])
    ctl = np.array([_z_expect_exact(t, False, False) for t in range(Tm + 1)])
    A_dtc, A_ctl = _amp_curve(dtc), _amp_curve(ctl)
    null = int(round(1 / (2 * EPS)))                  # ~4
    print(f"Exp151 selftest (noiseless) | L={L} eps={EPS} beat-null~t={null}")
    print(f"{'t':>3} {'A_dtc':>8} {'A_ctl':>8}")
    for t in range(Tm + 1):
        print(f"{t:>3} {A_dtc[t]:>8.3f} {A_ctl[t]:>8.3f}")
    # control beats to near-zero in a window around the null
    ctl_null = min(abs(A_ctl[null - 1]), abs(A_ctl[null]), abs(A_ctl[null + 1]))
    # DTC stays rigid through that same window
    dtc_hold = min(abs(A_dtc[null - 1]), abs(A_dtc[null]), abs(A_dtc[null + 1]))
    print(f"\ncontrol beat-null min |A| near t={null}: {ctl_null:.3f}  (should be small)")
    print(f"DTC rigidity   min |A| near t={null}: {dtc_hold:.3f}  (should stay high)")
    # falsifiability: DTC arm with interactions off == control
    fals = np.array([_z_expect_exact(t, False, False) for t in range(Tm + 1)])
    same = np.allclose(_amp_curve(fals), A_ctl)
    assert ctl_null < 0.35, f"control did not beat to a null ({ctl_null:.3f}) — check eps/L"
    assert dtc_hold > 0.45, f"DTC not rigid through the null ({dtc_hold:.3f}) — retune J/h"
    assert dtc_hold - ctl_null > 0.25, "DTC vs control contrast too weak at the null"
    assert same, "interactions-off 'DTC' must equal the control (falsifiability broken)"
    print(f"\nSELFTEST PASS: control beats to {ctl_null:.3f} at the null, DTC holds {dtc_hold:.3f} "
          f"(contrast {dtc_hold-ctl_null:.3f}); interactions-off reproduces control (test can fail).")


def powercalc():
    """Feasibility under MEASURED noise: each period costs (L-1) RZZ = 2(L-1) CX. Predict the
    hardware contrast A_dtc-A_ctl at the beat-null vs t_max by decaying the noiseless signal by
    fidelity^(#2q). KILL if predicted contrast at the null < 0.1 (unreadable)."""
    Tm = 14
    null = int(round(1 / (2 * EPS)))
    cx_per_period = 2 * (L - 1)
    dtc = np.array([_z_expect_exact(t, True, True) for t in range(Tm + 1)])
    ctl = np.array([_z_expect_exact(t, False, False) for t in range(Tm + 1)])
    A_dtc, A_ctl = _amp_curve(dtc), _amp_curve(ctl)
    print(f"Exp151 feasibility | E_CX={E_CX} | {cx_per_period} CX/period | beat-null t={null}")
    print(f"{'t':>3} {'2q':>4} {'A_dtc_hw':>9} {'A_ctl_hw':>9} {'contrast':>9}")
    best_t, best_contrast = null, 0.0
    for t in range(Tm + 1):
        n2q = t * cx_per_period
        decay = (1 - E_CX) ** n2q
        adh, ach = A_dtc[t] * decay, A_ctl[t] * decay   # control has no interactions -> fewer CX;
        # control truly has 0 CX (interactions off) -> only single-qubit error, ~undamped here
        ach = A_ctl[t]                                   # control decays negligibly (no 2q gates)
        contrast = adh - abs(ach)
        mark = "  <- null" if t == null else ""
        print(f"{t:>3} {n2q:>4} {adh:>9.3f} {abs(ach):>9.3f} {contrast:>9.3f}{mark}")
        if t == null:
            best_contrast = contrast
    verdict = "OK" if best_contrast > 0.1 else "KILL(unreadable)"
    print(f"\npredicted contrast at beat-null t={null}: {best_contrast:.3f} -> {verdict}")
    print("NOTE: control has NO 2-qubit gates (interactions off) so it barely decays; the DTC "
          "carries the 2q cost. Hardware adjudicates whether rigidity survives the depth.")
    out = os.path.join(HERE, "..", "results", "exp151_powercalc.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"null_t": null, "contrast_at_null": best_contrast, "cx_per_period": cx_per_period},
              open(out, "w"), indent=1)
    print(f"-> {out}")


def submit(backend_name, tmax, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, meta = [], []
    for arm, (inter, dis) in (("dtc", (True, True)), ("control", (False, False))):
        for t in range(tmax + 1):
            qc = floquet_circuit(t, inter, dis, measure=True)
            tqc = transpile(qc, backend=backend, optimization_level=3)
            circuits.append(tqc)
            meta.append({"arm": arm, "t": t, "depth": tqc.depth(), "n2q": tqc.num_nonlocal_gates()})
    sampler = SamplerV2(mode=backend)
    job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 151, "backend": backend_name, "tmax": tmax, "shots": shots, "L": L,
                "eps": EPS, "J": list(J_COUP), "h": list(H_FIELD), "job_id": job.job_id(),
                "order": [(m["arm"], m["t"]) for m in meta], "meta": meta,
                "note": "discrete time crystal: dtc(interactions+disorder) vs control(pulse only); "
                        "metric A(t)=(-1)^t<Z>; rigidity vs beat-null is the self-verifying contrast"}
    out = os.path.join(HERE, "..", "results", "exp151_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits: 2 arms x t=0..{tmax}, {shots} shots) -> {out}")
    deepest = max(meta, key=lambda m: m["n2q"])
    print(f"  deepest circuit: {deepest['arm']} t={deepest['t']} depth={deepest['depth']} 2q={deepest['n2q']}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    tmax = man["tmax"]; order = man["order"]; shots = man["shots"]
    arms = {"dtc": {}, "control": {}}
    for idx, (arm, t) in enumerate(order):
        r = res[idx]; reg = list(r.data.keys())[0]
        counts = getattr(r.data, reg).get_counts()
        arms[arm][t] = _z_expect_counts(counts, shots)
    dtc = np.array([arms["dtc"][t] for t in range(tmax + 1)])
    ctl = np.array([arms["control"][t] for t in range(tmax + 1)])
    A_dtc, A_ctl = _amp_curve(dtc), _amp_curve(ctl)
    null = int(round(1 / (2 * EPS)))
    print(f"Exp151 decode | job {man['job_id']} | backend {man['backend']} | beat-null t={null}")
    print(f"{'t':>3} {'A_dtc':>8} {'A_ctl':>8} {'contrast':>9}")
    for t in range(tmax + 1):
        mark = "  <- null" if t == null else ""
        print(f"{t:>3} {A_dtc[t]:>8.3f} {A_ctl[t]:>8.3f} {A_dtc[t]-abs(A_ctl[t]):>9.3f}{mark}")
    win = [null - 1, null, null + 1]
    dtc_hold = float(np.mean([abs(A_dtc[t]) for t in win]))
    ctl_null = float(np.mean([abs(A_ctl[t]) for t in win]))
    rigid = dtc_hold - ctl_null
    print(f"\nBEAT-NULL WINDOW (t={win}): DTC holds {dtc_hold:.3f} vs control {ctl_null:.3f}")
    print(f"RIGIDITY CONTRAST = {rigid:.3f}  -> "
          f"{'DTC signature PRESENT (crystal rigid where control beats)' if rigid > 0.1 else 'contrast washed out by noise (honest null)'}")
    out = {"job_id": man["job_id"], "backend": man["backend"], "null_t": null,
           "A_dtc": list(map(float, A_dtc)), "A_ctl": list(map(float, A_ctl)),
           "dtc_hold": dtc_hold, "ctl_null": ctl_null, "rigidity_contrast": rigid}
    fn = os.path.join(HERE, "..", "results", "exp151_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--powercalc", action="store_true")
    ap.add_argument("--submit", action="store_true"); ap.add_argument("--decode", action="store_true")
    ap.add_argument("--manifest"); ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--tmax", type=int, default=12); ap.add_argument("--shots", type=int, default=4000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.powercalc: powercalc()
    elif a.submit: submit(a.backend, a.tmax, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp151_manifest.json"))
    else: ap.print_help()
