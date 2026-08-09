#!/usr/bin/env python3
"""H13 Cell 6 (Silent Tripwire / Elitzur-Vaidman IFM) — design sim ($0).

Gate-model EV + Kwiat Zeno ladder. Probe qubit rotated Ry(pi/N) per segment, each
segment followed by CX(probe -> bomb). Bomb present: probe Zeno-pinned near |0>,
explosion P -> pi^2/4N; detection-without-explosion eta -> 1. Bomb absent: rotations
accumulate to pi, probe reads |1>.
Certificates: eta(N) inside frozen bands tracking theory; bomb-absent control reads |1>;
bomb-faithfulness premise (a probed bomb flips) measured as its own gate.
Noise: depolarizing p2 per CX, p1 per rotation, readout eps. Whisper C5048. Docs tier.
"""
import json
import numpy as np

I2 = np.eye(2, dtype=complex)
def ry(t):
    return np.array([[np.cos(t/2), -np.sin(t/2)], [np.sin(t/2), np.cos(t/2)]], dtype=complex)
CX = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)  # probe=MSB control

def depol(rho, p, nq):
    return (1-p)*rho + p*np.eye(2**nq)/2**nq

def run(N, bomb, p1=0.0005, p2=0.008, eps_ro=0.015):
    rho = np.zeros((4,4), dtype=complex); rho[0,0] = 1  # |probe=0, bomb=0>
    R = np.kron(ry(np.pi/N), I2)
    for _ in range(N):
        rho = R @ rho @ R.conj().T
        rho = depol(rho, p1, 2)
        if bomb:
            rho = CX @ rho @ CX.conj().T
            rho = depol(rho, p2, 2)
    # measure both in Z with readout error
    probs = np.real(np.diag(rho))  # order: p0b0, p0b1, p1b0, p1b1
    F = np.array([[1-eps_ro, eps_ro],[eps_ro, 1-eps_ro]])
    M = np.kron(F, F)
    return M @ probs

def main():
    rep = {"noise": {"p1": 0.0005, "p2": 0.008, "eps_ro": 0.015}}
    table = []
    for N in [1, 2, 4, 8, 16]:
        pb = run(N, bomb=True)
        pn = run(N, bomb=False)
        detect = pb[0]              # probe 0, bomb unflipped = interaction-free detection
        explode = pb[1] + pb[3]     # bomb flipped
        ideal_eta = np.cos(np.pi/(2*N))**(2*N)
        table.append({
            "N": N, "eta_detect": round(float(detect), 4),
            "P_explode": round(float(explode), 4),
            "ideal_eta": round(float(ideal_eta), 4),
            "control_no_bomb_P(probe=1)": round(float(pn[2] + pn[3]), 4),
            "cx_count": N,
        })
    rep["ladder"] = table
    # shots for 5-sigma on eta bands (binomial)
    rep["shots_note"] = "4000 shots/arm -> SE(eta) ~ 0.008; bands +/-0.04 give >5x margin"
    rep["circuits"] = "5 N-values x 2 arms (bomb/no-bomb) + 1 bomb-faithfulness = 11 circuits"
    rep["cost_est_seconds"] = "11 circ x 4000 shots ~ 44k shot-circuits; at 3x heuristic ~ 9-15s"
    print(json.dumps(rep, indent=2))
    with open("/droid/repos/quantum/results/h13_cell6_ifm_design_c5048.json", "w") as f:
        json.dump(rep, f, indent=2)

if __name__ == "__main__":
    main()
