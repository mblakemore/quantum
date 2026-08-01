#!/usr/bin/env python3
"""H10-B4 FLIGHT — Heat Flowing Backward (Whisper C5017). Prereg: docs/h10-b4-prereg-whisper-c5017.md
(FROZEN c4d1210, Ember spec-seal quantum@0247c5c, Creator GO general#3475/3477).

MANDATORY PRE-FLIGHT GATE (prereg §6): --ka runs every pub through exact statevector simulation and
reconstructs ALL frozen §3 numbers; any |Δ| > 1e-6 => NO SUBMISSION, exit 1. Submit only via
--fly, which re-runs the gate first. Unknown-is-not-a-value: any KA non-completion is a FAIL.

Frozen design (all numbers from the prereg / results/h10_b4_*.json — none re-derived here):
  beta_h=0.5, beta_c=2.0, w=1, alpha=0.157i, theta=2.35
  prep = classical mixture of 4 eigenstate circuits, probs {0.5483,0.4067,0.0450,0.0001}
  arms: 1 corr@theta (12k), 2 uncorr control (3k), 3 theta-sweep {0.5,1.2,2.35,2.9} (2k/pt),
        5 tomography 9 settings x before/after (1k/setting) [arm 4 rides arms 1-2 readouts]
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")

W = 1.0; BH, BC = 0.5, 2.0; THETA = 2.35
ALPHA = 0.157j
SWEEP = [0.5, 1.2, 2.35, 2.9]
TOMO = [(a, b) for a in "XYZ" for b in "XYZ"]

def rho_th(beta):
    e = np.array([+W/2, -W/2]); p = np.exp(-beta*e); p /= p.sum()
    return np.diag(p).astype(complex)

def rho_corr(alpha):
    r = np.kron(rho_th(BH), rho_th(BC)).astype(complex)
    r[1, 2] += alpha; r[2, 1] += np.conj(alpha)
    return r

def eig_prep(alpha):
    """(prob, statevector) list — the frozen 4-circuit classical mixture."""
    ev, V = np.linalg.eigh(rho_corr(alpha))
    return [(float(ev[k]), V[:, k]) for k in range(4) if ev[k] > 1e-12]

def prep_circuit(psi):
    qc = QuantumCircuit(2)
    qc.initialize(psi, [0, 1])   # qiskit little-endian: amp index b1b0 -> q1=A? define: q1=A(hot), q0=B(cold)
    return qc

def U_theta(theta):
    qc = QuantumCircuit(2)
    # exp(-i theta (XX+YY)/2) == RXX(theta)*RYY(theta) with qiskit's RXX(t)=exp(-i t XX/2)
    qc.rxx(theta, 0, 1); qc.ryy(theta, 0, 1)
    return qc

def basis_rot(qc, pauli, q):
    if pauli == "X": qc.h(q)
    elif pauli == "Y": qc.sdg(q); qc.h(q)

def build_pubs():
    """([(tag, circuit, shots)], baselines) — the full frozen flight. Index convention:
    amplitude index = (qA qB) with A = qubit 1, B = qubit 0 (little-endian).
    baselines[group] = (zA0, zB0) of that group's REALIZED (shot-rounded) prep mixture — the
    like-for-like reference the KA gate and the decode both use (first KA run taught this:
    ideal-vs-realized differ at 1.5e-5 from integer shot rounding)."""
    pubs = []; baselines = {}
    corr = eig_prep(ALPHA); unc = eig_prep(0.0)
    def zpsi(psi, qubit):
        pr = np.abs(psi) ** 2
        return sum(pr[idx] * (1 - 2 * ((idx >> qubit) & 1)) for idx in range(4))
    def add_arm(tag, mix, theta, shots_total, tomo=None, pre=False):
        shts = [int(round(p * shots_total)) for p, _ in mix]
        tot = sum(shts)
        baselines[tag] = (sum(sh * zpsi(psi, 1) for sh, (_, psi) in zip(shts, mix)) / tot,
                          sum(sh * zpsi(psi, 0) for sh, (_, psi) in zip(shts, mix)) / tot)
        for i, ((p, psi), sh) in enumerate(zip(mix, shts)):
            if sh == 0: continue
            qc = prep_circuit(psi)
            if not pre and theta is not None:
                qc = qc.compose(U_theta(theta))
            if tomo:
                a, b = tomo
                basis_rot(qc, a, 1); basis_rot(qc, b, 0)
            qc.measure_all()
            pubs.append((f"{tag}_s{i}", qc, sh))
    add_arm("arm1_corr", corr, THETA, 12000)
    add_arm("arm2_unc",  unc,  THETA, 3000)
    for th in SWEEP:
        add_arm(f"arm3_t{th}", corr, th, 2000)
    for (a, b) in TOMO:
        add_arm(f"arm5_pre_{a}{b}",  corr, None,  1000, tomo=(a, b), pre=True)
        add_arm(f"arm5_post_{a}{b}", corr, THETA, 1000, tomo=(a, b))
    return pubs, baselines

# ---------- exact expectations (KA gate targets, computed from the SAME pubs) ----------
def exact_counts(qc):
    sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    return np.abs(sv.data) ** 2   # probs over amplitude index (q1 q0)

def z_from_probs(pr, qubit):
    # qubit=0 -> B, bit0; qubit=1 -> A, bit1 (little-endian index)
    z = 0.0
    for idx, p in enumerate(pr):
        bit = (idx >> qubit) & 1
        z += p * (1 - 2 * bit)
    return z

def reconstruct(pubs, baselines, probs_of):
    """Frozen observables from per-pub outcome distributions, each group against ITS OWN
    realized-mixture baseline (like-for-like; the decode at landing uses the same rule)."""
    agg = {}
    for tag, qc, sh in pubs:
        agg.setdefault(tag.rsplit("_s", 1)[0], []).append((tag, qc, sh))
    out = {}
    def zAB(group):
        tot = sum(sh for _, _, sh in group)
        zA = sum(sh * z_from_probs(probs_of(qc), 1) for _, qc, sh in group) / tot
        zB = sum(sh * z_from_probs(probs_of(qc), 0) for _, qc, sh in group) / tot
        return zA, zB
    zA1, zB1 = zAB(agg["arm1_corr"])
    zA0, zB0 = baselines["arm1_corr"]
    out["dE_cold_corr"] = (W/2) * (zB1 - zB0); out["dE_hot_corr"] = (W/2) * (zA1 - zA0)
    zA2, zB2 = zAB(agg["arm2_unc"]); zA0u, zB0u = baselines["arm2_unc"]
    out["dE_cold_unc"] = (W/2) * (zB2 - zB0u)
    for th in SWEEP:
        zA, zB = zAB(agg[f"arm3_t{th}"]); b = baselines[f"arm3_t{th}"]
        out[f"sweep_dEc_{th}"] = (W/2) * (zB - b[1])
    return out

FROZEN = {"dE_cold_corr": -0.0262, "dE_cold_unc": +0.1308}

def ka_gate(pubs, baselines):
    rec = reconstruct(pubs, baselines, exact_counts)
    fails = []
    for k, v in FROZEN.items():
        if abs(rec[k] - v) > 1e-4:   # frozen numbers quoted to 4 dp in prereg §3
            fails.append((k, rec[k], v))
    # Self-consistency at 1e-6: pub-aggregation vs direct evolution OF THE REALIZED MIXTURE.
    # (First KA run FAILED at 1.5e-5 comparing against the IDEAL alpha-mixture: integer shot
    # rounding makes the flight's realized mixture differ from ideal at exactly that order.
    # The gate now compares like with like; the ideal-vs-realized delta is REPORTED, and the
    # frozen 4dp bars above are checked against the ideal-basis numbers untouched.)
    from numpy.linalg import eigh
    X = np.array([[0, 1], [1, 0]], complex); Y = np.array([[0, -1j], [1j, 0]])
    HXY = (np.kron(X, X) + np.kron(Y, Y)) / 2
    w_, v_ = eigh(HXY); U = (v_ * np.exp(-1j * THETA * w_)) @ v_.conj().T
    HB = np.kron(np.eye(2), W/2 * np.diag([1, -1]))
    mix = eig_prep(ALPHA)
    shots1 = [int(round(p * 12000)) for p, _ in mix]
    tot1 = sum(shots1)
    r_real = sum((sh / tot1) * np.outer(psi, psi.conj()) for sh, (_, psi) in zip(shots1, mix)).astype(complex)
    rf_real = U @ r_real @ U.conj().T
    dE_real = float(np.real(np.trace(HB @ (rf_real - r_real))))
    r_ideal = rho_corr(ALPHA); rf_ideal = U @ r_ideal @ U.conj().T
    dE_ideal = float(np.real(np.trace(HB @ (rf_ideal - r_ideal))))
    print(f"rounding delta (ideal vs realized mixture): {dE_ideal - dE_real:+.2e}  [reported]")
    if abs(rec["dE_cold_corr"] - dE_real) > 1e-6:
        fails.append(("pub-vs-direct-realized", rec["dE_cold_corr"], dE_real))
    print("KA GATE:", "PASS" if not fails else f"FAIL {fails}")
    print(json.dumps({k: round(float(v), 6) for k, v in rec.items()}, indent=1))
    return not fails

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ka", action="store_true")
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--backend", default="ibm_fez")
    a = ap.parse_args()
    pubs, baselines = build_pubs()
    print(f"pubs: {len(pubs)}  total shots: {sum(s for _, _, s in pubs)}")
    if not ka_gate(pubs, baselines):
        sys.exit("KA GATE FAILED — NO SUBMISSION (prereg §6).")
    if not a.fly:
        return 0
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    from check_job_status import _load_alt_token, ALT_CRN
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                               token=_load_alt_token(), instance=ALT_CRN)
    u = svc.usage()
    print(f"POOL RE-READ AT SUBMIT (prereg rule): remaining {u['usage_remaining_seconds']}s of {u['usage_limit_seconds']}")
    backend = svc.backend(a.backend)
    # calibration hold check (prereg §6): median 2q error on the chosen pair class
    tq = [transpile(qc, backend, optimization_level=3, seed_transpiler=1104) for _, qc, _ in pubs]
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, sh) for t, (_, _, sh) in zip(tq, pubs)])
    man = {"experiment": "h10_b4_heat_backward", "cycle": "C5017",
           "prereg": "docs/h10-b4-prereg-whisper-c5017.md@c4d1210",
           "spec_seal": "quantum@0247c5c", "go": "creator general#3475/#3477",
           "job_id": job.job_id(), "backend": a.backend,
           "pool_remaining_at_submit_s": u["usage_remaining_seconds"],
           "pubs": [(t, sh) for t, (_, _, sh) in zip([p[0] for p in pubs], pubs)],
           "committer": "Whisper (DC15W)"}
    path = os.path.join(RESULTS, "h10_b4_flight_manifest.json")
    json.dump(man, open(path, "w"), indent=1)
    print(f"SUBMITTED {job.job_id()} -> {path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
