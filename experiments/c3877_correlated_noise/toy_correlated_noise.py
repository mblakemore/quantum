#!/usr/bin/env python3
"""
Exp-C3877: marginal vs correlated (ZZ) noise — magnitude bound.
2-qubit density-matrix toy. Pure numpy, ~zero compute (no contention with exp54/exp59).
See PREREG.md for the pre-registered refutation line. Reality > theory.

Mechanism (N&C Ch8): from_backend composes MARGINAL per-qubit channels independently.
Question: with single-qubit marginals MATCHED, how big is the 2-qubit correlation the
marginal model structurally cannot reproduce, at calibration-plausible ZZ strength?
"""
import numpy as np

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def kron(*ops):
    out = ops[0]
    for o in ops[1:]:
        out = np.kron(out, o)
    return out

def plus():
    v = np.array([1, 1], dtype=complex) / np.sqrt(2)
    return v

def init_pp():
    v = np.kron(plus(), plus())
    return np.outer(v, v.conj())  # |++><++|

def phase_damp_kraus(lam):
    """Single-qubit phase damping (N&C 8.3.5), param lam in [0,1]."""
    E0 = np.array([[1, 0], [0, np.sqrt(1 - lam)]], dtype=complex)
    E1 = np.array([[0, 0], [0, np.sqrt(lam)]], dtype=complex)
    return [E0, E1]

def apply_kraus_1q(rho, kraus, qubit):
    """Apply single-qubit Kraus set to a 2-qubit rho on `qubit` (0 or 1)."""
    out = np.zeros_like(rho)
    for E in kraus:
        Efull = kron(E, I) if qubit == 0 else kron(I, E)
        out += Efull @ rho @ Efull.conj().T
    return out

def zz_unitary(theta):
    """Coherent static ZZ: U = exp(-i (theta/2) Z⊗Z)."""
    ZZ = kron(Z, Z)
    # Z⊗Z is diagonal with eigenvalues ±1 -> exp is diagonal
    from scipy.linalg import expm
    return expm(-1j * (theta / 2.0) * ZZ)

def channel_B(theta, lam):
    """Correlated 'truth': coherent ZZ then matched marginal phase damping each qubit."""
    rho = init_pp()
    U = zz_unitary(theta)
    rho = U @ rho @ U.conj().T
    rho = apply_kraus_1q(rho, phase_damp_kraus(lam), 0)
    rho = apply_kraus_1q(rho, phase_damp_kraus(lam), 1)
    return rho

def channel_A(lam_eff):
    """Marginal 'from_backend-style': independent phase damping each qubit, NO 2q term."""
    rho = init_pp()
    rho = apply_kraus_1q(rho, phase_damp_kraus(lam_eff), 0)
    rho = apply_kraus_1q(rho, phase_damp_kraus(lam_eff), 1)
    return rho

def expval(rho, op):
    return np.real(np.trace(rho @ op))

def single_x(rho):
    return expval(rho, kron(X, I)), expval(rho, kron(I, X))

def match_marginal_lam(rhoB):
    """Find lam_eff so Channel A's <X_1> matches Channel B's <X_1>.
    Phase damping on |+>: <X> = (1-lam)^? -> for phase damping, <X> scales by sqrt(1-lam) per
    the off-diagonal shrink. Solve closed-form, then verify numerically."""
    x1B, x2B = single_x(rhoB)
    # |++> under coherent ZZ: reduced <X> = cos(theta)*1 ... but matching is empirical.
    # <X> for marginal phase-damp on |+> = sqrt(1-lam). So lam_eff = 1 - (target)^2.
    # Channel B marginal <X> already includes the ZZ-induced reduction; match to it.
    target = max(min(x1B, 1.0), 0.0)
    lam_eff = 1.0 - target**2
    lam_eff = float(np.clip(lam_eff, 0.0, 1.0))
    return lam_eff, x1B, x2B

def run_point(zeta_kHz, t_us, lam):
    theta = 2 * np.pi * (zeta_kHz * 1e3) * (t_us * 1e-6)  # rad
    rhoB = channel_B(theta, lam)
    lam_eff, x1B, x2B = match_marginal_lam(rhoB)
    rhoA = channel_A(lam_eff)
    x1A, x2A = single_x(rhoA)
    xxB = expval(rhoB, kron(X, X)); xxA = expval(rhoA, kron(X, X))
    yyB = expval(rhoB, kron(Y, Y)); yyA = expval(rhoA, kron(Y, Y))
    zzB = expval(rhoB, kron(Z, Z)); zzA = expval(rhoA, kron(Z, Z))
    return {
        "zeta_kHz": zeta_kHz, "t_us": t_us, "lam": lam, "theta_rad": theta,
        "marg_match_err": abs(x1A - x1B) + abs(x2A - x2B),
        "dXX": abs(xxB - xxA), "dYY": abs(yyB - yyA), "dZZ": abs(zzB - zzA),
        "XX_B": xxB, "XX_A": xxA,
    }

def main():
    print("=" * 78)
    print("Exp-C3877 marginal-vs-correlated ZZ noise | 2q density-matrix toy")
    print("Refutation floor (G1-scale): |dXX| < 0.02 across plausible grid => WEAKENS C3876")
    print("=" * 78)
    FLOOR = 0.02
    grid_zeta = [1, 10, 50, 100]    # kHz
    grid_t = [0.1, 0.5, 2.0]        # us
    grid_lam = [0.05, 0.15]
    rows = []
    # S1 structural check: strong theta, marginals matched -> dXX must be > 0
    s1 = run_point(zeta_kHz=160, t_us=1.0, lam=0.05)  # theta ~ 1 rad
    print(f"\n[S1 structural] theta={s1['theta_rad']:.3f} rad, marg_match_err={s1['marg_match_err']:.2e}, "
          f"|dXX|={s1['dXX']:.4f}  (must be >0 => marginal CANNOT match correlation)")
    print("\n[grid] zeta(kHz)  t(us)  lam   theta(rad)  marg_err   |dXX|    |dYY|    |dZZ|")
    max_plausible = 0.0
    extreme_corner = (100, 2.0)
    for zeta in grid_zeta:
        for t in grid_t:
            for lam in grid_lam:
                r = run_point(zeta, t, lam)
                rows.append(r)
                tag = ""
                is_extreme = (zeta, t) == extreme_corner
                if not is_extreme:
                    max_plausible = max(max_plausible, r["dXX"])
                else:
                    tag = " <-extreme-corner(excluded)"
                print(f"        {zeta:5d}  {t:4.1f}  {lam:.2f}   {r['theta_rad']:8.4f}  "
                      f"{r['marg_match_err']:.1e}  {r['dXX']:.4f}  {r['dYY']:.4f}  {r['dZZ']:.4f}{tag}")
    print("=" * 78)
    s1_ok = s1["dXX"] > 1e-6
    verdict = "WEAKENS C3876 (artifact unlikely; sim-fail more likely real error-level)" \
        if max_plausible < FLOOR else "KEEPS C3876 ALIVE (omitted term reaches G1 scale)"
    print(f"S1 structural (marginal cannot match correlation): {'CONFIRMED' if s1_ok else 'FALSIFIED!'}")
    print(f"max |dXX| over plausible grid (extreme corner excluded): {max_plausible:.4f}  (floor {FLOOR})")
    print(f"VERDICT vs pre-registered refutation line: {verdict}")
    print("=" * 78)

if __name__ == "__main__":
    main()
