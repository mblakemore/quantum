#!/usr/bin/env python3
"""H13 Tier-0 T0.4 — Pseudo-density-matrix measurement-scheme selection ($0, sim only).

Gates Cell 3 (Temporal Negativity Meter). Questions:
  1. Scheme choice: direct mid-circuit projective sequential measurement vs ancilla-QND —
     which biases the correlators less under measured hardware error rates?
  2. Error budget: sigma-distance of min-eig(R) below the PSD boundary vs shots.
  3. The spatial control (Phi+ through the identical pipeline) must read PSD — check margin.
  4. The negativity dial: min-eig vs injected depolarizing lambda; locate the c=1/3 crossing.

PDM: R = (1/4) sum_ij <sigma_i(t1) sigma_j(t2)> sigma_i x sigma_j  (i,j in {I,X,Y,Z}),
temporal arm = one qubit measured twice (identity evolution). Ideal: eigs {3/4 x3, -1/2}...
actually for c_XX=c_YY=c_ZZ=c: eigs = {(1+c)/4 x3, (1-3c)/4}; negative iff c > 1/3.

Whisper C5048. Docs tier — no F-number. numpy only.
"""
import json
import numpy as np

I2 = np.eye(2, dtype=complex)
P = {
    "I": I2,
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}

# hardware-realistic error rates (campaign-measured classes)
EPS_MID = 0.020      # mid-circuit readout error (direct scheme, t1 measurement)
EPS_FINAL = 0.015    # final readout error
P_CX = 0.008         # 2q depolarizing per CX (ancilla-QND scheme)
EPS_ANC = 0.015      # ancilla readout error (read at leisure, end of circuit)

def eig_projectors(op):
    w, v = np.linalg.eigh(op)
    return [(float(w[k]), np.outer(v[:, k], v[:, k].conj())) for k in range(2)]

def depol1(rho, p):
    return (1 - p) * rho + p * I2 / 2

def temporal_correlator(i, j, lam, scheme):
    """E[a(t1)*b(t2)] for one qubit, maximally mixed input, depolarizing lam between times.
    scheme 'direct': projective mid-circuit measurement (readout EPS_MID) at t1.
    scheme 'ancilla': QND via CX to ancilla (2q depol P_CX on system, ancilla read EPS_ANC).
    Identity trivially: c_II = 1, c_iI/c_Ij = 0 for traceless paulis w/ mixed input."""
    if i == "I" and j == "I":
        return 1.0
    rho = I2 / 2
    if i == "I":
        # no t1 measurement needed; single-time <sigma_j> on I/2 evolved = 0
        return 0.0
    if j == "I":
        return 0.0
    c = 0.0
    eps1 = EPS_MID if scheme == "direct" else EPS_ANC
    for a, Pa in eig_projectors(P[i]):
        pra = float(np.trace(Pa @ rho).real)
        post = Pa @ rho @ Pa / pra          # exact projection either way (QND ideal limit)
        if scheme == "ancilla":
            post = depol1(post, P_CX)       # CX backaction/noise on the system
        post = depol1(post, lam)
        for b, Pb in eig_projectors(P[j]):
            prb = float(np.trace(Pb @ post).real)
            c += pra * prb * a * b
    return c * (1 - 2 * eps1) * (1 - 2 * EPS_FINAL)

def pdm(corrs):
    R = np.zeros((4, 4), dtype=complex)
    for i in "IXYZ":
        for j in "IXYZ":
            R += corrs[f"{i}{j}"] * np.kron(P[i], P[j]) / 4
    return R

def temporal_R(lam, scheme):
    corrs = {f"{i}{j}": temporal_correlator(i, j, lam, scheme) for i in "IXYZ" for j in "IXYZ"}
    return pdm(corrs), corrs

def spatial_control_R(scheme):
    """Phi+ pair pushed through the same estimator pipeline (both wings measured once;
    'mid-circuit' error applies to wing A to mirror the temporal pipeline)."""
    phi = np.zeros(4, dtype=complex)
    phi[0] = phi[3] = 1 / np.sqrt(2)
    rho = np.outer(phi, phi.conj())
    rho = (1 - P_CX) * rho + P_CX * np.eye(4) / 4   # CZ prep noise
    eps1 = EPS_MID if scheme == "direct" else EPS_ANC
    corrs = {}
    for i in "IXYZ":
        for j in "IXYZ":
            op = np.kron(P[i], P[j])
            c = float(np.trace(op @ rho).real)
            if i != "I":
                c *= (1 - 2 * eps1)
            if j != "I":
                c *= (1 - 2 * EPS_FINAL)
            corrs[f"{i}{j}"] = c
    return pdm(corrs)

def mineig_se(c_diag, shots):
    """SE of min-eig = (1 - (cXX+cYY+cZZ)... for the symmetric case min-eig=(1-3c)/4;
    generally the negative eig is (1 - cXX - cYY - cZZ)/4 for this correlator structure,
    so Var = sum Var(c_ii)/16."""
    var = sum((1 - c ** 2) / shots for c in c_diag) / 16
    return float(np.sqrt(var))

def main():
    rep = {"noise_model": {"eps_mid": EPS_MID, "eps_final": EPS_FINAL,
                           "p_cx": P_CX, "eps_anc": EPS_ANC}}
    # Q1: scheme comparison at lam=0
    for scheme in ["direct", "ancilla"]:
        R, corrs = temporal_R(0.0, scheme)
        eigs = sorted(np.linalg.eigvalsh(R))
        c_diag = [corrs["XX"], corrs["YY"], corrs["ZZ"]]
        se8k = mineig_se(c_diag, 8000)
        rep[f"temporal_{scheme}"] = {
            "c_diag": [round(c, 5) for c in c_diag],
            "min_eig": round(float(eigs[0]), 5),
            "se_at_8000_shots": round(se8k, 6),
            "sigmas_below_PSD_at_8000": round(-eigs[0] / se8k, 1),
        }
        Rs = spatial_control_R(scheme)
        rep[f"spatial_control_{scheme}"] = {
            "min_eig": round(float(sorted(np.linalg.eigvalsh(Rs))[0]), 5),
            "note": "must be >= -2se to pass the PSD control gate",
        }
    # Q4: negativity dial (direct scheme)
    dial = []
    for lam in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        R, corrs = temporal_R(lam, "direct")
        eigs = sorted(np.linalg.eigvalsh(R))
        dial.append({"lambda": lam, "c": round(corrs["ZZ"], 4),
                     "min_eig": round(float(eigs[0]), 5)})
    rep["negativity_dial_direct"] = dial
    crossing = next((d["lambda"] for d in dial if d["min_eig"] >= 0), None)
    rep["psd_crossing_lambda"] = crossing
    rep["theory_note"] = "negativity requires c > 1/3; ideal min-eig = (1-3c)/4"
    rep["circuits"] = "9 temporal (3x3 diag bases needed: actually 3 circuits XX/YY/ZZ + 6 cross for full R) x dial points + 9 spatial control"
    print(json.dumps(rep, indent=2))
    with open("/droid/repos/quantum/results/h13_t04_pdm_design_c5048.json", "w") as f:
        json.dump(rep, f, indent=2)

if __name__ == "__main__":
    main()
