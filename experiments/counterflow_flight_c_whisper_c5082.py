#!/usr/bin/env python3
"""Counterflow Flight C — the Information Recuperator (QET), circuit build (Whisper C5082, board #196).

Pivot-to-C build. Status: CORE VALIDATED (gamma=0 extract matches sim to shot noise); GAD gradient +
4 arms + the two-regime sign-flip validation are the NEXT step (this file grows as each piece validates,
Flight A discipline — no fly until the TRANSPILED circuit reproduces the sign-flip).

CLAIM (sim_c): does the DIRECTION of the information stream matter in a thermal gradient? The "direction"
observable (extract_cf - extract_co) FLIPS SIGN across the gradient strength gamma: negative at low gamma
(co-flow wins, ~-0.04 at gamma 0.1-0.3), positive at high gamma (counterflow wins, +0.20 at 0.5, +1.04 at 0.7).

PROTOCOL (Hotta minimal QET, exp119 verbatim; H = Z0+Z1+2 X0X1, offset E_ground=0):
  ground prep |g>=cos a|00>-sin a|11>  ->  ry(-2a,0); cx(0,1)   [a from the ground eigenvector]
  measure site A in X (MCM) -> mu ; conditional Ry(-2 mu theta) on site B ; theta scanned to argmin e_post.
OBSERVABLE on the ROTATED site B: obs_B = Z_B + 2 X_B X_A. Since A is X-measured (mu known), X_A -> mu, so
  obs_B = Z_B + 2 mu X_B. Measured shot-wise: <Z_B> (Z setting) and <X_B> (X setting), binned by mu; then
  e = sum_mu p_mu (<Z_B|mu> + 2 mu <X_B|mu>). e_pre = obs BEFORE rotation, e_post = AFTER; extract=e_post-e_pre.
  CORE VALIDATION (gamma=0, cf): circuit e_pre -2.117 e_post -2.231 extract -0.114 vs sim -2.121/-2.236/-0.1147.

GAD THERMAL GRADIENT (next to validate): local generalized amplitude damping toward each site's bath
  population (hot P_HOT=0.40, cold P_COLD=0.05) at strength gamma. Circuit realization = partial-SWAP with
  a MIXED bath ancilla (Ry to p_bath then dephase, Flight A primitive); the swap-angle<->gamma mapping must
  be matched against sim.biased() before it is believed.
ARMS: cf (measure COLD site, rotate HOT), co (mirrored), severed (fresh coin at matched schedule), uncond
  (best fixed rotation, no measurement — the no-communication baseline). direction = extract_cf - extract_co.
"""
import sys, os
import numpy as np
from qiskit import QuantumCircuit, transpile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import counterflow_sim_c_whisper_c5080 as S   # ground/ham/local_obs/gad reference

N = 2
H = S.ham_chain(N)
GVEC = np.real(S.ground(H))
ALPHA = float(np.arctan2(-GVEC[3], GVEC[0]))
P_HOT, P_COLD = S.P_HOT, S.P_COLD

def prep(qc):
    qc.ry(-2 * ALPHA, 0); qc.cx(0, 1)

def core_qet(setting, rotate, theta, meas_site=0, rot_site=1):
    """CORE (validated gamma=0). meas_site X-measured -> c0; rot_site conditionally rotated then read in
    `setting` (Z or X). obs combined externally as <Z>+2 mu <X> binned by c0."""
    qc = QuantumCircuit(2, 2)
    prep(qc)
    qc.h(meas_site); qc.measure(meas_site, 0)
    if rotate:
        with qc.if_test((qc.clbits[0], 1)): qc.ry(-2 * theta, rot_site)
        with qc.if_test((qc.clbits[0], 0)): qc.ry(+2 * theta, rot_site)
    if setting == 'X': qc.h(rot_site)
    qc.measure(rot_site, 1)
    return qc

def extract_from(sim, rotate, theta, meas_site, rot_site, shots=200000):
    def eb(setting):
        cts = sim.run(core_qet(setting, rotate, theta, meas_site, rot_site), shots=shots).result().get_counts()
        num = {0: [0, 0], 1: [0, 0]}
        for k, v in cts.items():
            b = k.replace(' ', ''); num[int(b[-1])][int(b[-2])] += v
        return {c: (2 * (num[c][0] / max(sum(num[c]), 1)) - 1, sum(num[c])) for c in (0, 1)}
    Z = eb('Z'); Xr = eb('X'); e = 0.0; Ntot = sum(Z[c][1] for c in (0, 1))
    for c in (0, 1):
        mu = +1 if c == 0 else -1; pmu = Z[c][1] / Ntot
        e += pmu * (Z[c][0] + 2 * mu * Xr[c][0])
    return e

# --- self-check when run directly: reproduce gamma=0 core extract (no GAD yet) ---
if __name__ == "__main__":
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    best = (0.0, 9.9)
    for th in np.linspace(-0.4, 0.4, 33):
        ep = extract_from(sim, True, th, 0, 1)
        if ep < best[1]: best = (th, ep)
    e_pre = extract_from(sim, False, 0.0, 0, 1)
    print(f"CORE gamma=0 cf: e_pre={e_pre:.4f} theta*={best[0]:.3f} e_post={best[1]:.4f} "
          f"extract={best[1]-e_pre:.4f}  [sim extract -0.1147]  {'OK' if abs((best[1]-e_pre)+0.1147)<0.01 else 'MISMATCH'}")
    print("NEXT: add GAD gradient (partial-SWAP mixed baths) + arms + validate the two-regime sign-flip.")
