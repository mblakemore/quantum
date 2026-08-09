#!/usr/bin/env python3
"""H13 Tier-0 T0.3 — Causal Compass matched-generator design study ($0, sim only).

Gates Cell 2 (the flagship). Questions:
  1. Construct the cause-effect (CE) and common-cause (CC) generators and compute their
     full observational correlator tables under a realistic noise model.
  2. THE PREMISE GATE: are the classical (Z-basis) joint statistics matched out of the box?
     If not, design the matching dial (noise injection into the stronger arm) and show it
     equalizes the classical record without disturbing the sign fingerprint.
  3. Enumerate the classical-analyst ceiling on the matched record (1/2 + TVD/2).
  4. Shot budget for a >=5 sigma sign-product call per arm.

Generators (Ried et al. Nat. Phys. 11, 414 class):
  CE: one qubit, maximally mixed input; Alice measures Pauli i mid-circuit (projective),
      state evolves through identity-with-noise, Bob measures Pauli j.
  CC: Phi+ pair (CZ-built), Alice measures Pauli i on wing A, Bob Pauli j on wing B.
Fingerprint: sign(C_XX * C_YY * C_ZZ) = +1 for CE (channel), -1 for CC (state).

Whisper C5048. Docs tier — no F-number. numpy only.
"""
import json
import numpy as np

I2 = np.eye(2, dtype=complex)
PAULIS = {
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}

# --- noise model (hardware-realistic, from campaign-measured numbers) ---
EPS_RO_FINAL = 0.015   # final readout error/bit (fez-class per-bit average)
EPS_RO_MID = 0.020     # mid-circuit readout slightly worse
P_CZ = 0.008           # effective 2q depolarizing for the Phi+ prep (CZ + locals)
P_IDLE_CE = 0.010      # idle/T2 depolarizing on the CE qubit between the two measurements

def eig_projectors(P):
    w, v = np.linalg.eigh(P)
    return [(float(w[k]), np.outer(v[:, k], v[:, k].conj())) for k in range(2)]

def depol1(rho, p):
    return (1 - p) * rho + p * I2 / 2

def ce_correlator(i, j, p_extra=0.0):
    """Two-time correlator E[a*b] for CE arm, with mid/final readout error and idle noise.
    p_extra = matching-dial depolarizing injected between the measurements."""
    rho = I2 / 2
    c = 0.0
    for a, Pa in eig_projectors(PAULIS[i]):
        pra = float(np.trace(Pa @ rho).real)
        post = Pa @ rho @ Pa / pra
        post = depol1(depol1(post, P_IDLE_CE), p_extra)
        for b, Pb in eig_projectors(PAULIS[j]):
            prb = float(np.trace(Pb @ post).real)
            c += pra * prb * a * b
    # readout errors flip recorded signs independently
    return c * (1 - 2 * EPS_RO_MID) * (1 - 2 * EPS_RO_FINAL)

def cc_correlator(i, j, p_extra=0.0):
    """<sigma_i x sigma_j> on noisy Phi+, both wings read with final-readout error."""
    phi = np.zeros(4, dtype=complex)
    phi[0] = phi[3] = 1 / np.sqrt(2)
    rho = np.outer(phi, phi.conj())
    rho = (1 - P_CZ) * rho + P_CZ * np.eye(4) / 4
    if p_extra:
        # matching dial applied symmetrically to one wing
        r = rho.reshape(2, 2, 2, 2)
        mixed = np.einsum("ijkl->jl", r) / 2  # not used; apply via kraus instead
        rho = (1 - p_extra) * rho + p_extra * np.kron(I2 / 2, np.einsum("ijil->jl", rho.reshape(2, 2, 2, 2)))
    op = np.kron(PAULIS[i], PAULIS[j])
    c = float(np.trace(op @ rho).real)
    return c * (1 - 2 * EPS_RO_FINAL) ** 2

def table(fn, p_extra=0.0):
    return {f"{i}{j}": round(fn(i, j, p_extra), 5) for i in "XYZ" for j in "XYZ"}

def z_tvd(c_ce, c_cc):
    """TVD between the two arms' Z-basis joint distributions P(a,b)=(1+ab*c)/4."""
    return abs(c_ce - c_cc) / 2

def match_dial(target_cc_zz):
    """Solve for p_extra on the CE arm so CE Z-correlator == CC Z-correlator."""
    base = ce_correlator("Z", "Z", 0.0)
    if base <= target_cc_zz:
        return 0.0, base
    # depol between measurements scales c by (1-p): solve (analytic)
    p = 1 - target_cc_zz / base
    return p, ce_correlator("Z", "Z", p)

def sign_product(tab):
    return tab["XX"] * tab["YY"] * tab["ZZ"]

def shots_for_5sigma(prod, c_diag, shots_per_basis):
    """Delta-method SE of the product of three independently-measured correlators."""
    var = 0.0
    cs = c_diag
    for k in range(3):
        se_k2 = (1 - cs[k] ** 2) / shots_per_basis
        partial = prod / cs[k] if cs[k] != 0 else 0.0
        var += partial ** 2 * se_k2
    se = np.sqrt(var)
    return se, abs(prod) / se if se > 0 else np.inf

def main():
    rep = {"noise_model": {"eps_ro_final": EPS_RO_FINAL, "eps_ro_mid": EPS_RO_MID,
                           "p_cz": P_CZ, "p_idle_ce": P_IDLE_CE}}
    t_ce = table(ce_correlator)
    t_cc = table(cc_correlator)
    rep["ce_correlators_raw"] = t_ce
    rep["cc_correlators_raw"] = t_cc
    rep["ce_sign_product_raw"] = round(sign_product(t_ce), 5)
    rep["cc_sign_product_raw"] = round(sign_product(t_cc), 5)
    rep["z_tvd_raw"] = round(z_tvd(t_ce["ZZ"], t_cc["ZZ"]), 5)

    # premise gate + matching dial
    p_match, ce_zz_matched = match_dial(t_cc["ZZ"])
    t_ce_m = table(ce_correlator, p_match)
    rep["matching_dial"] = {
        "p_extra_on_CE": round(p_match, 5),
        "ce_zz_after": round(ce_zz_matched, 5),
        "cc_zz": t_cc["ZZ"],
        "z_tvd_after": round(z_tvd(t_ce_m["ZZ"], t_cc["ZZ"]), 6),
    }
    rep["ce_correlators_matched"] = t_ce_m
    rep["ce_sign_product_matched"] = round(sign_product(t_ce_m), 5)

    # classical-analyst ceiling on the matched record
    tvd_after = z_tvd(t_ce_m["ZZ"], t_cc["ZZ"])
    rep["classical_analyst_ceiling"] = round(0.5 + tvd_after / 2, 6)

    # shot budget
    budget = {}
    for shots in [2000, 4000, 8000]:
        ce_se, ce_sig = shots_for_5sigma(
            sign_product(t_ce_m), [t_ce_m["XX"], t_ce_m["YY"], t_ce_m["ZZ"]], shots)
        cc_se, cc_sig = shots_for_5sigma(
            sign_product(t_cc), [t_cc["XX"], t_cc["YY"], t_cc["ZZ"]], shots)
        budget[str(shots)] = {"ce_sigma": round(float(ce_sig), 1),
                              "cc_sigma": round(float(cc_sig), 1)}
    rep["sign_product_sigmas_vs_shots_per_basis"] = budget
    rep["circuits"] = "9 per arm (3x3 bases) x 2 arms + matching-calibration pre-run"

    print(json.dumps(rep, indent=2))
    with open("/droid/repos/quantum/results/h13_t03_compass_design_c5048.json", "w") as f:
        json.dump(rep, f, indent=2)

if __name__ == "__main__":
    main()
