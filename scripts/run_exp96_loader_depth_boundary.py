#!/usr/bin/env python3
"""
Exp96 (Ember C4082) — LOADER-DEPTH BOUNDARY, in a noise model.

Elder C6349/F78 found, ON REAL HARDWARE (ibm_marrakesh):
  - deep 3-qubit QQQ lognormal loader (StatePreparation, ~124 2q-gates by k=5):
    canonical multi-k MLE err 0.154 -> ~12x WORSE than plain k=0 read. QAE loses.
  - shallow 1-qubit IWM loader (single RY):  Finding 9, MLE won 344x. QAE wins.
Elder's reconciliation HYPOTHESIS: it is LOADER DEPTH (2q-gate count), not Grover
count, that poisons the high-k likelihood. His proposed clean test: run the MLE on
the shallow IWM loader in the SAME regime to pin the boundary.

This is the CHEAP (sim, no QPU queue) version of that test, and the sim-replicate-
before-hardware step my own C3869 quantum discipline requires. We run BOTH loaders
through the FakeMarrakesh noise model across k=0..5, compute the noisy canonical
multi-k MLE error for each, and compare 2q-gate depth.

PRE-REG (pred_c4082_001, conf 0.62 directional):
  Under FakeMarrakesh, the DEEP QQQ loader's noisy multi-k MLE error is materially
  LARGER than the SHALLOW IWM loader's (QQQ err > IWM err, gap > 0.03), AND the
  QQQ 2q-gate count at k=5 is >>  IWM's. If confirmed, depth is the killer,
  reproduced in a noise model -> corroborates Elder's HW reconciliation and
  pre-registers a clean hardware confirmation.
  Secondary (uncertain): FakeMarrakesh QQQ MLE err lands in the neighbourhood of the
  HW 0.154 (sim-to-HW quantitative fidelity — NOT claimed at 0.62).
"""
import os, sys, math, json, time
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qae_qqq_tail_demo import (
    build_A as build_A_qqq, grover_Q as grover_Q_qqq, bucket_probs,
    true_tail_discrete, _msb_one_prob, N_QUBITS as N_QQQ,
)

SHOTS = 4096
SEED = 78
K_VALUES = [0, 1, 2, 3, 4, 5]
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


# ---------- shallow IWM 1-qubit loader (Finding 9 / exp10 geometry) ----------
A_TRUE_IWM = 0.56  # P(IWM up), Elder calibrated (run_experiment_10_financial_qae.py)

def theta_iwm():
    return math.asin(math.sqrt(A_TRUE_IWM))

def build_A_iwm():
    qc = QuantumCircuit(1)
    qc.ry(2 * theta_iwm(), 0)   # |psi> = cos(theta)|0> + sin(theta)|1>, a=sin^2(theta)
    return qc

def grover_Q_iwm():
    """Q = A S0 A^dag S_chi ; good state = |1> (mirrors the QQQ construction for 1 qubit)."""
    A = build_A_iwm()
    Q = QuantumCircuit(1)
    Q.z(0)                                   # S_chi: phase-flip |1> (good)
    Q.compose(A.inverse(), [0], inplace=True)
    Q.x(0); Q.z(0); Q.x(0)                   # S0: reflection about |0>  (X Z X = diag(-1,1))
    Q.compose(A, [0], inplace=True)
    return Q, A


# ---------- generic circuit + MLE ----------
def build_grover_circuit(A, Q, nq, obj_qubit, k):
    qc = QuantumCircuit(nq, 1)
    qc.compose(A, list(range(nq)), inplace=True)
    for _ in range(k):
        qc.compose(Q, list(range(nq)), inplace=True)
    qc.measure(obj_qubit, 0)
    return qc

def mle_over_k(pmeas_by_k, shots):
    def nll(a):
        if a <= 1e-6 or a >= 1 - 1e-6:
            return 1e12
        ll = 0.0
        for k, p in pmeas_by_k:
            th = (2 * k + 1) * math.asin(math.sqrt(a))
            pk = max(1e-10, min(1 - 1e-10, math.sin(th) ** 2))
            m = int(round(p * shots))
            ll += m * math.log(pk) + (shots - m) * math.log(1 - pk)
        return -ll
    return float(optimize.minimize_scalar(nll, bounds=(1e-3, 1 - 1e-3), method='bounded').x)

def ideal_P(a_true, k):
    th = math.asin(math.sqrt(a_true))
    return math.sin((2 * k + 1) * th) ** 2


def run_loader(name, A, Q, nq, obj_qubit, a_true, noiseless_sim, fake_sim):
    """Return dict with noiseless + noisy curves, 2q-depth, and both MLE errors."""
    print(f"\n=== {name} loader | nq={nq} | a_true={a_true:.4f} ===", flush=True)
    ideal = [ideal_P(a_true, k) for k in K_VALUES]

    # noiseless (correctness check: must reproduce sin^2((2k+1)theta))
    p_noiseless = []
    for k in K_VALUES:
        qc = build_grover_circuit(A, Q, nq, obj_qubit, k)
        tq = transpile(qc, noiseless_sim, seed_transpiler=SEED)
        cn = noiseless_sim.run(tq, shots=SHOTS).result().get_counts()
        p_noiseless.append(_msb_one_prob(cn))
    nl_max_dev = max(abs(p - i) for p, i in zip(p_noiseless, ideal))
    print(f"  noiseless: max|P-ideal| = {nl_max_dev:.4f}  (must be small — validates Q)", flush=True)

    # noisy (FakeMarrakesh) + 2q-gate depth
    p_noisy = []; depth_rows = []
    for k in K_VALUES:
        qc = build_grover_circuit(A, Q, nq, obj_qubit, k)
        tqf = transpile(qc, fake_sim, optimization_level=1, seed_transpiler=SEED)
        cf = fake_sim.run(tqf, shots=SHOTS).result().get_counts()
        pk = _msb_one_prob(cf)
        n2q = sum(1 for g in tqf.data if g.operation.num_qubits == 2)
        p_noisy.append(pk)
        depth_rows.append({"k": k, "depth": tqf.depth(), "n2q": n2q})
        print(f"    k={k}  ideal={ideal[k]:.4f}  noiseless={p_noiseless[k]:.4f}  "
              f"noisy={pk:.4f}  2q={n2q}  depth={tqf.depth()}", flush=True)

    mle_noiseless = mle_over_k(list(zip(K_VALUES, p_noiseless)), SHOTS)
    mle_noisy = mle_over_k(list(zip(K_VALUES, p_noisy)), SHOTS)
    plain_read_err = abs(p_noisy[0] - a_true)   # k=0 noisy read (the classical-ish baseline)
    err_noiseless = abs(mle_noiseless - a_true)
    err_noisy = abs(mle_noisy - a_true)
    print(f"  MLE(noiseless) a*={mle_noiseless:.4f} err={err_noiseless:.4f}", flush=True)
    print(f"  MLE(noisy)     a*={mle_noisy:.4f} err={err_noisy:.4f}   "
          f"| plain k=0 noisy read err={plain_read_err:.4f}", flush=True)
    print(f"  QAE verdict: multi-k MLE {'BEATS' if err_noisy < plain_read_err else 'LOSES TO'} "
          f"plain k=0 read", flush=True)

    return {
        "name": name, "nq": nq, "a_true": a_true, "ideal": ideal,
        "p_noiseless": p_noiseless, "p_noisy": p_noisy, "depth_rows": depth_rows,
        "n2q_at_k5": depth_rows[-1]["n2q"], "noiseless_max_dev": nl_max_dev,
        "mle_noiseless": mle_noiseless, "err_noiseless": err_noiseless,
        "mle_noisy": mle_noisy, "err_noisy": err_noisy,
        "plain_read_err_noisy": plain_read_err,
        "qae_beats_plain": bool(err_noisy < plain_read_err),
    }


def main():
    t0 = time.time()
    print("Exp96 (Ember C4082) — loader-depth boundary under FakeMarrakesh", flush=True)
    noiseless = AerSimulator()
    fake = AerSimulator.from_backend(FakeMarrakesh())

    # deep QQQ loader
    probs = bucket_probs()[0]
    A_qqq = build_A_qqq(probs, measure=False)
    Q_qqq, _ = grover_Q_qqq(probs)
    a_qqq = true_tail_discrete(probs)
    r_qqq = run_loader("QQQ-deep-3q", A_qqq, Q_qqq, N_QQQ, N_QQQ - 1, a_qqq, noiseless, fake)

    # shallow IWM loader
    Q_iwm, A_iwm = grover_Q_iwm()
    r_iwm = run_loader("IWM-shallow-1q", A_iwm, Q_iwm, 1, 0, A_TRUE_IWM, noiseless, fake)

    gap = r_qqq["err_noisy"] - r_iwm["err_noisy"]
    print("\n" + "=" * 70, flush=True)
    print("DEPTH-BOUNDARY VERDICT", flush=True)
    print(f"  noisy MLE err:  QQQ-deep {r_qqq['err_noisy']:.4f}  vs  IWM-shallow {r_iwm['err_noisy']:.4f}", flush=True)
    print(f"  2q@k5:          QQQ-deep {r_qqq['n2q_at_k5']}      vs  IWM-shallow {r_iwm['n2q_at_k5']}", flush=True)
    print(f"  gap (QQQ-IWM):  {gap:+.4f}   (pred_c4082_001 wants > +0.03 AND 2q_QQQ >> 2q_IWM)", flush=True)
    pred_pass = (gap > 0.03) and (r_qqq["n2q_at_k5"] > 3 * max(1, r_iwm["n2q_at_k5"]))
    print(f"  pred_c4082_001 directional: {'CONFIRMED' if pred_pass else 'NOT confirmed'}", flush=True)

    out = {
        "experiment": "exp96_loader_depth_boundary", "cycle": 4082, "author": "ember",
        "shots": SHOTS, "k_values": K_VALUES,
        "qqq_deep": r_qqq, "iwm_shallow": r_iwm,
        "noisy_mle_err_gap_qqq_minus_iwm": gap,
        "pred_c4082_001_directional_confirmed": bool(pred_pass),
        "wall_s": round(time.time() - t0, 1),
    }
    path = os.path.join(RESULTS_DIR, "exp96_loader_depth_boundary.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  saved -> {path}   (wall {out['wall_s']}s)", flush=True)


if __name__ == "__main__":
    main()
