#!/usr/bin/env python3
"""
Exp97 — Is the DAG-fit residual an INDEPENDENT axis from the DISC witness? (Whisper C4490)

Tests my OWN C4487 Part V pre-registration:
  "Fit the best latent-selector mixture p*D_AB+(1-p)*D_BA to the switch at coherence
   c=cos(phi/2). The fit residual should rise monotonically in c and vanish at c=0.
   ... F73/F74 measure the WITNESS value DISC. This measures the DAG-fit RESIDUAL.
   They COULD disagree; if they don't, that is real corroboration, not restatement."

Advisor (C4490) flagged that claim as a probable TAUTOLOGY for a 2-slot switch:
  - order-basis dephasing scales ONLY the coherence block by c, so the process is
    exactly AFFINE in c:  rho(c) = rho_mix + c*(rho(1) - rho_mix)
  - trace-distance from a linearly-moving point to the fixed mixture line is linear in c
  - DISC(c) = 2c  (exp94, Pearson 0.9999)
  => residual(c) = k*c = (k/2)*DISC(c)  : PROVABLY proportional, cannot disagree.
  - for 2 slots, causally-separable set = convex hull{W_AB, W_BA} = the mixture line,
    so residual>0 <=> non-separable <=> W>0 : binary-equivalent to the witness.

This script does NOT assume the above — it COMPUTES it and lets the data decide:
  1. build_arm reused VERBATIM from run_exp94_hw.py (same circuit F74 measured).
  2. rho_arm(c) = reduced (q0,q1) density matrix, ancilla q2 traced out (the dephasing).
  3. D_AB / D_BA = the two order branches, obtained by CONDITIONING the phi=pi switch on
     the ancilla q2 (Elder F73: phi=pi IS the 50/50 mixture). Verified: 0.5(D_AB+D_BA)=rho(pi).
  4. VERIFY exact affine-in-c: rho(c) == rho_mix + c*(rho(1)-rho_mix)  (machine precision).
  5. residual(c) = min_p sum_arm 0.5*||rho_switch_arm(c) - (p*D_AB+(1-p)*D_BA)||_1
     over a RICH arm set (all 9 Pauli pairs) at the DENSITY-MATRIX level (no ad-hoc
     observable choice -> dissolves the observable-richness confound).
  6. DISC(c) reconstructed from arms (X,X),(X,Z) exactly as the witness.
  7. Regress residual vs DISC and residual vs c -> is the ratio constant (R^2~1, intercept~0)?

sim-only, NO QPU, NO hardware -> does not touch Elder's F73/F75/Exp91 silicon arc.
"""
import os, sys, math, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RESULTS_DIR = os.path.join(HERE, "..", "results")

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# ---- circuit: build_arm VERBATIM from run_exp94_hw.py (minus final h/measure) -------
def apply_ctrl_gate(qc, gate, ctrl, tgt, ctrl_state):
    if ctrl_state == 0:
        qc.x(ctrl)
    if gate == "X":
        qc.cx(ctrl, tgt)
    elif gate == "Z":
        qc.cz(ctrl, tgt)
    elif gate == "Y":
        qc.cy(ctrl, tgt)
    else:
        raise ValueError(gate)
    if ctrl_state == 0:
        qc.x(ctrl)


def build_arm_state(A, B, phi):
    """Full 3-qubit statevector of the switch arm BEFORE the final X-basis readout h(0).
    Keeping the pre-readout state lets us compute <X_control> AND full (q0,q1) tomography."""
    qc = QuantumCircuit(3)
    qc.h(0)
    apply_ctrl_gate(qc, A, 0, 1, 0)   # q0=0 branch: A then B  (order AB)
    apply_ctrl_gate(qc, B, 0, 1, 1)   # q0=1 branch: ... B
    apply_ctrl_gate(qc, B, 0, 1, 0)   # q0=0 branch: ... B  -> order A->B
    apply_ctrl_gate(qc, A, 0, 1, 1)   # q0=1 branch: A     -> order B->A
    qc.cry(phi, 0, 2)                  # partial order-basis dephasing; ancilla q2
    return Statevector(qc).data        # length-8, little-endian index = q0 + 2 q1 + 4 q2


# ---- reduced / conditioned density matrices on (q0,q1) ------------------------------
# little-endian amplitude index i = q0 + 2*q1 + 4*q2 ; (q0,q1) basis j = q0 + 2*q1
def rho_q0q1_traced(psi):
    """Reduced density matrix on (q0,q1), tracing out ancilla q2 (=the dephasing)."""
    rho = np.zeros((4, 4), dtype=complex)
    for q2 in (0, 1):
        v = psi[q2 * 4:(q2 + 1) * 4]            # amplitudes for this q2 value
        rho += np.outer(v, v.conj())
    return rho


def rho_q0q1_conditioned(psi, q2val):
    """(q0,q1) density matrix CONDITIONED on ancilla q2 = q2val (the order register)."""
    v = psi[q2val * 4:(q2val + 1) * 4].copy()
    p = float(np.vdot(v, v).real)
    if p < 1e-15:
        return np.zeros((4, 4), dtype=complex), 0.0
    v /= math.sqrt(p)
    return np.outer(v, v.conj()), p


# ---- metrics ------------------------------------------------------------------------
def trace_dist(a, b):
    """0.5 * ||a-b||_1  (trace distance between density matrices)."""
    d = a - b
    ev = np.linalg.eigvalsh((d + d.conj().T) / 2)  # d is Hermitian; symmetrize for safety
    return 0.5 * float(np.sum(np.abs(ev)))


X = np.array([[0, 1], [1, 0]], dtype=complex)
I2 = np.eye(2, dtype=complex)
X_on_q0 = np.kron(I2, X)  # basis j=q0+2q1 -> q0 is low bit -> kron(high=I_q1, low=X_q0)


def exp_X_control(rho):
    return float(np.trace(rho @ X_on_q0).real)


# ---- main ---------------------------------------------------------------------------
def main():
    PAULIS = ["X", "Y", "Z"]
    ARMS = [(a, b) for a in PAULIS for b in PAULIS]   # 9 arms (rich set)
    N = 25
    phis = [math.pi * k / (N - 1) for k in range(N)]  # 0 .. pi
    cs = [math.cos(p / 2) for p in phis]

    # definite-order branches from the phi=pi (fully dephased) switch, per arm
    D_AB, D_BA, mix_check = {}, {}, {}
    for (A, B) in ARMS:
        psi_pi = build_arm_state(A, B, math.pi)
        dab, pab = rho_q0q1_conditioned(psi_pi, 0)   # q2=0 -> order A->B branch
        dba, pba = rho_q0q1_conditioned(psi_pi, 1)   # q2=1 -> order B->A branch
        D_AB[(A, B)] = dab
        D_BA[(A, B)] = dba
        rho_pi = rho_q0q1_traced(psi_pi)
        mix_check[(A, B)] = trace_dist(0.5 * dab + 0.5 * dba, rho_pi)  # should be ~0

    max_mix_err = max(mix_check.values())

    # rho_switch_arm(c) for every arm and every phi
    rho_switch = {}   # (arm, k) -> 4x4
    for k, phi in enumerate(phis):
        for arm in ARMS:
            rho_switch[(arm, k)] = rho_q0q1_traced(build_arm_state(arm[0], arm[1], phi))

    # (4) exact-affine-in-c check: rho(c) == rho_mix + c*(rho(c=1) - rho_mix)  per arm
    affine_err = 0.0
    for arm in ARMS:
        rho_c1 = rho_switch[(arm, 0)]            # phi=0 -> c=1
        rho_mix = rho_switch[(arm, N - 1)]       # phi=pi -> c=0 (the mixture)
        for k in range(N):
            pred = rho_mix + cs[k] * (rho_c1 - rho_mix)
            affine_err = max(affine_err, np.max(np.abs(rho_switch[(arm, k)] - pred)))

    # (5) residual(c) = min_p sum_arm trace_dist(rho_switch(c), p*D_AB+(1-p)*D_BA)
    def total_dist(k, p):
        s = 0.0
        for arm in ARMS:
            mixp = p * D_AB[arm] + (1 - p) * D_BA[arm]
            s += trace_dist(rho_switch[(arm, k)], mixp)
        return s

    def best_p_residual(k):
        # trace distance is convex in p -> coarse grid then golden-ish refine
        ps = np.linspace(0, 1, 51)
        vals = [total_dist(k, p) for p in ps]
        j = int(np.argmin(vals))
        lo, hi = ps[max(0, j - 1)], ps[min(len(ps) - 1, j + 1)]
        for _ in range(40):
            m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
            if total_dist(k, m1) < total_dist(k, m2):
                hi = m2
            else:
                lo = m1
        pstar = (lo + hi) / 2
        return pstar, total_dist(k, pstar)

    rows = []
    for k, phi in enumerate(phis):
        pstar, resid = best_p_residual(k)
        disc = exp_X_control(rho_switch[(("X", "X"), k)]) - exp_X_control(rho_switch[(("X", "Z"), k)])
        rows.append({"phi": phi, "c": cs[k], "p_star": pstar,
                     "residual": resid, "disc": disc})

    # (7) regressions: residual vs disc, residual vs c
    def linfit(xs, ys):
        xs, ys = np.array(xs), np.array(ys)
        A = np.vstack([xs, np.ones_like(xs)]).T
        (slope, intercept), *_ = np.linalg.lstsq(A, ys, rcond=None)
        yhat = slope * xs + intercept
        ss_res = float(np.sum((ys - yhat) ** 2))
        ss_tot = float(np.sum((ys - np.mean(ys)) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
        return float(slope), float(intercept), r2

    discs = [r["disc"] for r in rows]
    resids = [r["residual"] for r in rows]
    cvals = [r["c"] for r in rows]
    s_rd, i_rd, r2_rd = linfit(discs, resids)     # residual = s*disc + i
    s_rc, i_rc, r2_rc = linfit(cvals, resids)      # residual = s*c    + i

    # ratio residual/disc across the interior (disc!=0)
    ratios = [r["residual"] / r["disc"] for r in rows if abs(r["disc"]) > 1e-6]
    ratio_cv = float(np.std(ratios) / np.mean(ratios)) if ratios else float("nan")

    # p* at every c: is the classical fit ALWAYS the balanced mixture (p=0.5)?
    pstar_dev = max(abs(r["p_star"] - 0.5) for r in rows)

    verdict = ("TAUTOLOGY_CONFIRMED"
               if (affine_err < 1e-9 and r2_rd > 0.999 and abs(i_rd) < 1e-6
                   and max_mix_err < 1e-9)
               else "INDEPENDENT_SIGNAL")

    out = {
        "experiment": "exp97-dagfit-residual-tautology",
        "author": "Whisper", "cycle": "C4490",
        "tests": "own C4487 Part V pre-registration (DAG-fit residual independent of DISC?)",
        "n_arms": len(ARMS), "n_phi": N, "level": "density-matrix (q0,q1), q2 traced",
        "checks": {
            "mixture_decomp_err (0.5(D_AB+D_BA) vs rho(pi), max)": max_mix_err,
            "affine_in_c_err (rho(c) vs rho_mix+c*(rho(1)-rho_mix), max)": affine_err,
            "residual_vs_disc": {"slope": s_rd, "intercept": i_rd, "R2": r2_rd},
            "residual_vs_c": {"slope": s_rc, "intercept": i_rc, "R2": r2_rc},
            "ratio residual/disc CV (interior)": ratio_cv,
            "p_star max deviation from 0.5": pstar_dev,
            "residual at c=0 (phi=pi)": rows[-1]["residual"],
            "residual at c=1 (phi=0)": rows[0]["residual"],
        },
        "verdict": verdict,
        "rows": rows,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "exp97_dagfit_residual.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Exp97 — DAG-fit residual vs DISC witness  (arms={len(ARMS)}, phi grid={N})")
    print(f"  mixture-decomp err  0.5(D_AB+D_BA)=rho(pi) : {max_mix_err:.2e}  (want ~0)")
    print(f"  affine-in-c err     rho(c)=rho_mix+c*dV    : {affine_err:.2e}  (want ~0)")
    print(f"  residual = {s_rd:.5f}*DISC + {i_rd:+.2e}     R^2={r2_rd:.8f}")
    print(f"  residual = {s_rc:.5f}*c    + {i_rc:+.2e}     R^2={r2_rc:.8f}")
    print(f"  ratio residual/DISC coeff-of-variation     : {ratio_cv:.2e}  (want ~0 => constant)")
    print(f"  best-fit p* max |dev from 0.5|             : {pstar_dev:.2e}")
    print(f"  residual(c=0)={rows[-1]['residual']:.2e}   residual(c=1)={rows[0]['residual']:.4f}")
    print(f"\n  VERDICT: {verdict}")
    print(f"  wrote {os.path.relpath(path, HERE)}")
    return out


if __name__ == "__main__":
    main()
