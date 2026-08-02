#!/usr/bin/env python3
"""Steth λ_anc PRE-SEAL FIDELITY GATE — build of the LOCKED DESIGN (Ember C4215 → C4224).

Design: docs/steth-lambda-anc-preseal-gate-design-ember-c4215.md (advisor-reviewed, greenlit
C5010). This file is the mechanical pickup; the specification/de-risking was done there and
NOTHING here re-decides it.

WHAT THIS GATE CERTIFIES
    Before a hidden Haar-U is sealed, fly a PUBLIC representative channel through the
    Choi-prep + two-copy SWAP and confirm the Choi-purity witness SURVIVES ON-DEVICE — i.e.
    a sealed-class U will read pure enough to separate from D, so the flight is not washed
    before it flies. (exp142-preseal analogue: public test-P → even-rate survives.)

WHY IT IS BUILT NOW (C4224)
    The design was parked at C4215 with the reason, in my own commit message: "Non-urgent
    (QPU hard-floored, #2.5 behind n8)." QPU is no longer hard-floored — the Creator opened
    ALT2 with a fresh 600s pool and steth holds top priority in the arc. The premise that
    deferred the build expired and nothing in my queue noticed; that is c3933_001 (action
    queues accumulate stale premises) sitting inside my own backlog.

BUILT ON THE DELIVERED CIRCUITS — NOT RE-IMPLEMENTED (advisor #4 / c4215_003):
    exp_steth_3b_twocopy_ember.two_copy_estimator  — per-shot P2 = (-1)^(Σ uᵢ∧vᵢ)
    exp_steth_a_flight.twocopy_circuit             — Bell-pair Choi prep + ancilla DD echo

FROZEN, NOT CHOSEN HERE:
    FLOOR_U = 0.7   from results/exp_steth_c4998_g3_sims.json B_q_rule_purity_table
                    (u→m_Q = {1.0→6, 0.9→12, 0.8→16, 0.7→24}); arm-n-toy froze m_Q=24.
    MARGIN  = 0.25  separation floor, clear of noise.
    Gate is on RAW u, never on label-recovery accuracy (c4215_005: label-recovery absorbs
    degradation through the m_Q margin exactly when u is marginal).

USAGE
    python3 exp_steth_lambda_anc_preseal_gate_ember_c4224.py --sim-only            # $0
    python3 exp_steth_lambda_anc_preseal_gate_ember_c4224.py --predict --backend ibm_fez
    python3 exp_steth_lambda_anc_preseal_gate_ember_c4224.py --validate --backend ibm_fez
"""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import random_unitary

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "experiments"))

# --- delivered primitives: imported, never re-implemented -------------------------------
from exp_steth_3b_twocopy_ember import two_copy_estimator          # noqa: E402

# --- FROZEN constants (design §"The observable + FROZEN floor") -------------------------
FLOOR_U = 0.7
MARGIN = 0.25
PUBLIC_HAAR_SEED = 20260801          # public, documented — NOT the sealed U's seed
DELAY_NS = 4000                      # matches exp_steth_a_flight's Λ idle
SHOTS = 4096
OUT = os.path.join(REPO, "results", "steth_lambda_anc_preseal_gate_c4224.json")


def p_odd_targets(k):
    """Noiseless self-check targets (design §observable). U pure → p_odd 0;
    D completely depolarizing → Choi is maximally mixed on 2k qubits → Tr[rho^2]=4^-k."""
    return 0.0, (1.0 - 4.0 ** (-k)) / 2.0


# ---------------------------------------------------------------------------------------
# Choi preparation: k Bell pairs, channel applied to the SYSTEM half -> 2k-qubit Choi state
# ---------------------------------------------------------------------------------------
def _choi_prep(qc, k, sys_q, anc_q, channel, rng, dd=False):
    """Bell pairs (sys i, anc i); then `channel` on the system half only."""
    for i in range(k):
        qc.h(sys_q[i])
        qc.cx(sys_q[i], anc_q[i])
    qc.barrier()

    if channel == "haar":
        # SAME CLASS as the sealed U (prereg §1 "fixed Haar-random U"). Deliberately NOT
        # identity: an identity-Choi carries no channel-gate noise and false-PASSes.
        U = random_unitary(2 ** k, seed=PUBLIC_HAAR_SEED)
        qc.append(U.to_instruction(), sys_q)
    elif channel == "depol":
        # Completely depolarizing = FRESH PER-SHOT uniform Pauli twirl (c4215_006).
        # A fixed draw misestimates the D-side purity, so the caller must rebuild this
        # circuit per shot with a fresh rng draw.
        for i in range(k):
            p = int(rng.integers(0, 4))
            if p == 1:
                qc.x(sys_q[i])
            elif p == 2:
                qc.y(sys_q[i])
            elif p == 3:
                qc.z(sys_q[i])
    else:
        raise ValueError(f"unknown channel {channel!r}")

    if dd:
        # Ancilla is the MEMORY: 2-pulse echo nets to I and refocuses low-frequency
        # dephasing (exp_steth_a_flight pattern, imported as a pattern not a call).
        for i in range(k):
            qc.delay(DELAY_NS // 2, anc_q[i], unit="ns")
            qc.x(anc_q[i])
            qc.delay(DELAY_NS // 2, anc_q[i], unit="ns")
            qc.x(anc_q[i])
    qc.barrier()


def choi_two_copy_circuit(k, channel, rng, dd=False):
    """Two copies of the 2k-qubit Choi state + transversal destructive SWAP over all 2k.

    Layout: copy1 sys 0..k-1, anc k..2k-1 ; copy2 sys 2k..3k-1, anc 3k..4k-1.
    The SWAP is over the FULL 2k-qubit Choi register of each copy (n = 2k in the
    delivered estimator's convention), because rho IS the Choi state.
    """
    n = 2 * k                       # width of the state being purity-tested
    qc = QuantumCircuit(4 * k, 2 * n)
    c1 = list(range(0, k)), list(range(k, 2 * k))
    c2 = list(range(2 * k, 3 * k)), list(range(3 * k, 4 * k))
    _choi_prep(qc, k, c1[0], c1[1], channel, rng, dd)
    _choi_prep(qc, k, c2[0], c2[1], channel, rng, dd)

    a = c1[0] + c1[1]               # copy-1 Choi register (2k)
    b = c2[0] + c2[1]               # copy-2 Choi register (2k)
    for i in range(n):              # Cincio destructive SWAP: CX, H, measure both
        qc.cx(a[i], b[i])
        qc.h(a[i])
    for i in range(n):
        qc.measure(a[i], i)         # u_i
        qc.measure(b[i], n + i)     # v_i
    return qc


# ---------------------------------------------------------------------------------------
# lambda_anc — DEDICATED measured ancilla-survival block (C4975 circularity fix)
# ---------------------------------------------------------------------------------------
def lambda_anc_circuit(k):
    """Bell pair per (system, ancilla); ancilla idles the FULL Lambda depth under DD; the
    system half is NOT touched. Measure the Bell correlation -> ancilla survival.

    Deliberately SEPARATE from the Choi data: inferring lambda_anc from the Choi run was
    circular (C4975 verdict), so any u-shortfall can only be ATTRIBUTED (ancilla loss vs
    channel-gate noise) if this is measured independently.
    """
    qc = QuantumCircuit(2 * k, 2 * k)
    for i in range(k):
        qc.h(i)
        qc.cx(i, k + i)
    qc.barrier()
    for i in range(k):
        qc.delay(DELAY_NS // 2, k + i, unit="ns")
        qc.x(k + i)
        qc.delay(DELAY_NS // 2, k + i, unit="ns")
        qc.x(k + i)
    qc.barrier()
    for i in range(k):              # Bell-basis readout
        qc.cx(i, k + i)
        qc.h(i)
    qc.measure(range(2 * k), range(2 * k))
    return qc


def lambda_anc_from_counts(counts, k, shots):
    """Survival = P(all-zeros) mapped off the 4^-k floor, so a fully decohered ancilla
    reads 0 rather than the accidental floor. Reported raw as well."""
    z = counts.get("0" * (2 * k), 0) / shots
    floor = 4.0 ** (-k)
    return max(0.0, (z - floor) / (1.0 - floor)), z


# ---------------------------------------------------------------------------------------
# runners
# ---------------------------------------------------------------------------------------
def _p_odd_from_counts(counts, k, shots):
    n = 2 * k
    bs = []
    for b, c in counts.items():
        bs.extend([b] * c)
    vals = two_copy_estimator(bs, n)          # delivered estimator, imported
    e_p2 = float(np.mean(vals))
    return (1.0 - e_p2) / 2.0, e_p2


def run_channel(k, channel, backend, shots, noise_model=None):
    """Depol REBUILDS the circuit per shot (fresh twirl); haar builds once."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(noise_model=noise_model) if noise_model else AerSimulator()
    rng = np.random.default_rng(PUBLIC_HAAR_SEED + (0 if channel == "haar" else 1))
    merged = {}
    if channel == "depol":
        for _ in range(shots):
            qc = choi_two_copy_circuit(k, channel, rng, dd=(backend is not None))
            tqc = transpile(qc, sim, optimization_level=1)
            for b, c in sim.run(tqc, shots=1).result().get_counts().items():
                merged[b] = merged.get(b, 0) + c
    else:
        qc = choi_two_copy_circuit(k, channel, rng, dd=(backend is not None))
        tqc = transpile(qc, sim, optimization_level=1)
        merged = sim.run(tqc, shots=shots).result().get_counts()
    return _p_odd_from_counts(merged, k, shots)


def verdict(u, sep, lam):
    ok_u = u >= FLOOR_U
    ok_s = sep >= MARGIN
    return {
        "u": round(u, 4), "separation": round(sep, 4), "lambda_anc": round(lam, 4),
        "floor_u": FLOOR_U, "margin": MARGIN,
        "u_pass": bool(ok_u), "separation_pass": bool(ok_s),
        "PASS": bool(ok_u and ok_s),
        "attribution": ("ancilla-loss-dominated" if (not ok_u and lam < 0.8)
                        else "channel-gate-noise-dominated" if not ok_u
                        else "n/a — passed"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim-only", action="store_true", help="$0 noiseless self-check")
    ap.add_argument("--predict", action="store_true", help="$0 noise-model forecast")
    ap.add_argument("--validate", action="store_true", help="on-device (spends QPU)")
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--k", type=int, default=2, choices=(2, 3))
    ap.add_argument("--shots", type=int, default=SHOTS)
    args = ap.parse_args()

    if not (args.sim_only or args.predict or args.validate):
        print("choose one of --sim-only / --predict / --validate")
        return 2

    k = args.k
    tgt_u, tgt_d = p_odd_targets(k)
    out = {"gate": "steth lambda_anc pre-seal fidelity gate", "design":
           "docs/steth-lambda-anc-preseal-gate-design-ember-c4215.md", "builder": "Ember C4224",
           "k": k, "shots": args.shots, "floor_u": FLOOR_U, "margin": MARGIN,
           "public_haar_seed": PUBLIC_HAAR_SEED,
           "noiseless_targets": {"p_odd_U": tgt_u, "p_odd_D": round(tgt_d, 6)}}

    # ---------------- $0 sim-only: validates observable + plumbing before any QPU --------
    if args.sim_only:
        print(f"SIM-ONLY self-check (k={k}, {4*k} qubits, shots={args.shots})")
        print(f"  noiseless targets: p_odd(U)={tgt_u:.5f}  p_odd(D)={tgt_d:.5f}")
        # D REBUILDS the circuit per shot (fresh twirl) so it is the expensive arm; it
        # still needs enough shots for the check to MEAN anything. C4224: an earlier
        # 512-shot D run read E[P2]=0.0156 against a 0.0625 target and I briefly took that
        # for a bug — it was ~1.1 sigma of ordinary sampling noise, and a flat +/-0.05
        # tolerance was simultaneously too loose to catch a real defect and loose enough
        # to make me distrust a correct result. The tolerance is now STATISTICAL.
        d_shots = min(args.shots, 4096)
        pu, e2u = run_channel(k, "haar", None, args.shots)
        pd, e2d = run_channel(k, "depol", None, d_shots)
        u = 1.0 - 2.0 * pu
        # sigma on E[P2] is 1/sqrt(N) for a +-1 per-shot estimator; p_odd = (1-E)/2
        sig_u = 1.0 / (2.0 * args.shots ** 0.5)
        sig_d = 1.0 / (2.0 * d_shots ** 0.5)
        z_u = abs(pu - tgt_u) / max(sig_u, 1e-12)
        z_d = abs(pd - tgt_d) / max(sig_d, 1e-12)
        print(f"  measured : p_odd(U)={pu:.5f}  (E[P2]={e2u:.4f}, u={u:.4f})   z={z_u:.2f}")
        print(f"             p_odd(D)={pd:.5f}  (E[P2]={e2d:.4f}, N={d_shots})  z={z_d:.2f}")
        ok = z_u <= 4.0 and z_d <= 4.0
        print(f"  SELF-CHECK: {'PASS' if ok else 'FAIL'} — observable and plumbing "
              f"{'agree with theory within 4 sigma' if ok else 'DISAGREE with theory; do not proceed'}")
        out["sim_only"] = {"p_odd_U": pu, "p_odd_D": pd, "u": u,
                           "z_U": round(z_u, 3), "z_D": round(z_d, 3),
                           "d_shots": d_shots, "self_check_pass": bool(ok)}

    # ---------------- $0 predict: noise model, no job submitted -------------------------
    if args.predict:
        print(f"\nPREDICT on {args.backend} noise model (no job submitted)")
        try:
            from run_exp66_qpu_partb import _get_ibm_service
            from qiskit_aer.noise import NoiseModel
            svc = _get_ibm_service()
            backend = svc.backend(args.backend)
            nm = NoiseModel.from_backend(backend)
            pu, _ = run_channel(k, "haar", backend, args.shots, noise_model=nm)
            pd, _ = run_channel(k, "depol", backend, min(args.shots, 256), noise_model=nm)
            u = 1.0 - 2.0 * pu
            sep = pd - pu
            from qiskit_aer import AerSimulator
            sim = AerSimulator(noise_model=nm)
            lc = transpile(lambda_anc_circuit(k), sim, optimization_level=1)
            lam, raw = lambda_anc_from_counts(
                sim.run(lc, shots=args.shots).result().get_counts(), k, args.shots)
            v = verdict(u, sep, lam)
            print(f"  u={v['u']}  separation={v['separation']}  lambda_anc={v['lambda_anc']}")
            print(f"  FORECAST: {'PASS' if v['PASS'] else 'FAIL'}  ({v['attribution']})")
            out["predict"] = {"backend": args.backend, **v, "lambda_anc_raw_allzero": raw}
        except Exception as exc:
            print(f"  PREDICT UNAVAILABLE: {type(exc).__name__}: {str(exc)[:120]}")
            print("  Recorded as UNAVAILABLE, not as a pass — unknown is not a value.")
            out["predict"] = {"status": "UNAVAILABLE", "error": type(exc).__name__}

    # ---------------- on-device: spends QPU -------------------------------------------
    if args.validate:
        print(f"\nVALIDATE on {args.backend} — ON-DEVICE, SPENDS QPU")
        print("  Not auto-running: this gate exists to be flown deliberately, and the")
        print("  pool must be re-read at submit (no frozen pool number is current).")
        print("  Arm it exactly like the n8 re-fly, with the pool printed at submit.")
        out["validate"] = {"status": "ARMED-NOT-RUN",
                           "reason": "on-device flight is a deliberate act; pool re-read required at submit"}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
