#!/usr/bin/env python3
"""H13 Tier-0 T0.2 — Deutsch-CTC fixed-point feasibility design study ($0, sim only).

Gates Cell 1 (The Kelvin Timeline). Questions:
  1. Does the Deutsch fixed-point iteration converge under realistic noise, and how fast?
  2. Does the BHW discrimination gadget beat the Helstrom ceiling at hardware-realistic noise,
     and where is the noise threshold p* where it stops?
  3. Grandfather two-rulebook table: D-CTC step-function vs P-CTC smooth law p(theta),
     including the noise-smoothed step width.
  4. What does the P-CTC rule predict for the SAME BHW gadget circuit (design honesty:
     the spec's "P-CTC <= Helstrom" line is checked here, not assumed).

Whisper C5048. Docs tier — no F-number. numpy only, no hardware access anywhere.
"""
import json
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
SWAP = np.array(
    [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex
)

def kron(*ops):
    out = ops[0]
    for o in ops[1:]:
        out = np.kron(out, o)
    return out

# BHW gadget: CU (apply X.H to system iff CTC=1), then SWAP(sys, ctc).
# Ordering convention: index = sys (x) ctc.
P0c = np.diag([1, 0]).astype(complex)
P1c = np.diag([0, 1]).astype(complex)
CU = kron(I2, P0c) + kron(X @ H, P1c)
V = SWAP @ CU

def depolarize(rho, p):
    """Single-qubit depolarizing with prob p (2x2 rho)."""
    return (1 - p) * rho + p * I2 / 2

def two_qubit_depolarize(rho4, p):
    """Uniform 2q depolarizing with prob p."""
    return (1 - p) * rho4 + p * np.eye(4, dtype=complex) / 4

def dctc_map(rho_ctc, psi_sys, p_noise):
    """One pass of the loop: CTC input rho_ctc -> CTC output (traced over sys).
    p_noise = effective 2q depolarizing per pass (gate + prep + tomography error proxy)."""
    rho_in = kron(psi_sys, rho_ctc)
    rho_out = V @ rho_in @ V.conj().T
    rho_out = two_qubit_depolarize(rho_out, p_noise)
    # partial trace over system (first factor)
    return rho_out.reshape(2, 2, 2, 2).trace(axis1=0, axis2=2)

def sys_output(rho_ctc_fp, psi_sys, p_noise):
    """CR (system) output at the fixed point."""
    rho_in = kron(psi_sys, rho_ctc_fp)
    rho_out = V @ rho_in @ V.conj().T
    rho_out = two_qubit_depolarize(rho_out, p_noise)
    return rho_out.reshape(2, 2, 2, 2).trace(axis1=1, axis2=3)

def superop_eigs(psi_sys, p_noise):
    """Eigenvalues of the linear CTC map (vectorized 4x4), sorted by |.| desc."""
    M = np.zeros((4, 4), dtype=complex)
    basis = [np.array([[1, 0], [0, 0]]), np.array([[0, 1], [0, 0]]),
             np.array([[0, 0], [1, 0]]), np.array([[0, 0], [0, 1]])]
    for k, b in enumerate(basis):
        M[:, k] = dctc_map(b.astype(complex), psi_sys, p_noise).reshape(4)
    ev = np.linalg.eigvals(M)
    return ev[np.argsort(-np.abs(ev))]

def fixed_point(psi_sys, p_noise, tol=1e-3, max_iter=200):
    """Iterate from I/2; return (fp, n_iter to tol in trace distance)."""
    rho = I2 / 2
    n_at_tol = None
    for k in range(1, max_iter + 1):
        nxt = dctc_map(rho, psi_sys, p_noise)
        d = 0.5 * np.abs(np.linalg.eigvalsh(nxt - rho)).sum()
        rho = nxt
        if n_at_tol is None and d < tol:
            n_at_tol = k
            break
    # polish: iterate a few more for the report values
    for _ in range(50):
        rho = dctc_map(rho, psi_sys, p_noise)
    return rho, (n_at_tol if n_at_tol is not None else max_iter)

def readout_flip(p1, eps):
    """Symmetric readout error eps applied to a Bernoulli prob."""
    return p1 * (1 - eps) + (1 - p1) * eps

HELSTROM = 0.5 * (1 + np.sqrt(1 - 0.5))  # {|0>,|+>}, equal priors = 0.85355

def bhw_success(p_noise, eps_ro=0.015):
    """Deterministic D-CTC discrimination success (all runs kept)."""
    psi0 = np.outer([1, 0], [1, 0]).astype(complex)
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    psip = np.outer(plus, plus.conj())
    fp0, it0 = fixed_point(psi0, p_noise)
    fpp, itp = fixed_point(psip, p_noise)
    out0 = sys_output(fp0, psi0, p_noise)
    outp = sys_output(fpp, psip, p_noise)
    p_call0_given0 = readout_flip(out0[0, 0].real, eps_ro)      # call "0" on Z=0
    p_call1_givenp = readout_flip(outp[1, 1].real, eps_ro)      # call "+" on Z=1
    return 0.5 * (p_call0_given0 + p_call1_givenp), max(it0, itp)

def pctc_gadget_success(eps_ro=0.015):
    """P-CTC rule on the SAME gadget: output ~ C|psi>, C = Tr_ctc[V] (Lloyd)."""
    # partial trace of V over ctc (second factor): C_{ij} = sum_k V_{(i k),(j k)}
    Vt = V.reshape(2, 2, 2, 2)
    C = Vt[:, 0, :, 0] + Vt[:, 1, :, 1]
    res = {}
    for name, vec in [("state0", np.array([1, 0], dtype=complex)),
                      ("state+", np.array([1, 1], dtype=complex) / np.sqrt(2))]:
        out = C @ vec
        keep = float(np.vdot(out, out).real)  # renormalization weight (postselection)
        if keep < 1e-12:
            res[name] = {"keep_weight": keep, "p_z1": None}
            continue
        outn = out / np.sqrt(keep)
        p1 = float(np.abs(outn[1]) ** 2)
        res[name] = {"keep_weight": round(keep, 6),
                     "p_z1": round(readout_flip(p1, eps_ro), 6)}
    return res

def grandfather_curve(p_noise, thetas):
    """D-CTC grandfather: loop qubit self-interaction U(theta)=exp(-i theta X/2).
    Returns p(Z-flip measured) at the fixed point for each theta.
    P-CTC comparison law (F101, measured on silicon): p = cos^2(theta/2)/2 -> 0 at pi...
    NOTE: F101's measured law is survival suppression; here we tabulate the D-CTC side."""
    out = []
    for th in thetas:
        U = np.cos(th / 2) * I2 - 1j * np.sin(th / 2) * X
        # loop map: rho -> depolarize(U rho U^dag)
        Mb = np.zeros((4, 4), dtype=complex)
        basis = [np.array([[1, 0], [0, 0]]), np.array([[0, 1], [0, 0]]),
                 np.array([[0, 0], [1, 0]]), np.array([[0, 0], [0, 1]])]
        for k, b in enumerate(basis):
            r = U @ b.astype(complex) @ U.conj().T
            Mb[:, k] = depolarize(r, p_noise).reshape(4)
        ev, vecs = np.linalg.eig(Mb)
        idx = int(np.argmin(np.abs(ev - 1)))
        fp = vecs[:, idx].reshape(2, 2)
        fp = fp / np.trace(fp)
        fp = 0.5 * (fp + fp.conj().T)
        # Deutsch max-entropy selection is automatic once p_noise>0 (unique fp).
        # "flip probability": prepare Z=0 reference; at fp the loop state's P(Z=1):
        out.append(float(fp[1, 1].real))
    return out

def main():
    rng_report = {}
    # --- Q1/Q2: convergence + discrimination vs noise ---
    sweep = []
    p_star = None
    for p in [0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.16, 0.20, 0.30]:
        s, iters = bhw_success(p)
        e2 = np.abs(superop_eigs(np.outer([1, 0], [1, 0]).astype(complex), p))[1]
        sweep.append({"p_noise": p, "success": round(float(s), 5),
                      "iters_to_1e-3": iters, "second_eig_mod": round(float(e2), 4)})
        if p_star is None and s < HELSTROM:
            p_star = p
    rng_report["helstrom_ceiling"] = round(float(HELSTROM), 5)
    rng_report["bhw_sweep"] = sweep
    rng_report["noise_threshold_p_star"] = p_star

    # --- Q4: P-CTC prediction on the same gadget ---
    rng_report["pctc_same_gadget"] = pctc_gadget_success()

    # --- Q3: grandfather step vs smooth ---
    thetas = [0.0, 0.1, 0.25, 0.5, 1.0, np.pi / 2, 2.0, np.pi]
    for p in [0.0, 0.02, 0.05]:
        rng_report[f"grandfather_dctc_pflip_p{p}"] = [
            round(v, 4) for v in grandfather_curve(p, thetas)]
    rng_report["grandfather_thetas"] = [round(float(t), 4) for t in thetas]
    rng_report["grandfather_pctc_law"] = "cos^2(theta/2)/2 (smooth; F101 measured on silicon)"

    # --- hardware protocol cost estimate ---
    worst_iters = max(r["iters_to_1e-3"] for r in sweep if r["p_noise"] >= 0.005)
    n_circuits = worst_iters * 3 * 2 + 6  # iters x tomo bases x 2 inputs + final scoring
    rng_report["hw_cost_estimate"] = {
        "iterations_worst": worst_iters,
        "circuits_total_approx": n_circuits,
        "note": "mixed-state re-prep per iteration via eigendecomposition + classical shot mixing",
    }
    print(json.dumps(rng_report, indent=2))
    with open("/droid/repos/quantum/results/h13_t02_dctc_design_c5048.json", "w") as f:
        json.dump(rng_report, f, indent=2)

if __name__ == "__main__":
    main()
