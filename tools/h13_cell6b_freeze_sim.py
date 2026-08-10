#!/usr/bin/env python3
"""H13 Cell 6+6b FREEZE-TIME full-noise sim (board #66) — Whisper C5056.

Exact density-matrix simulation of the Zeno IFM ladder with per-segment projective
detector measurement + reset (Cell 6's corrected mechanism), under:
  - 2q depolarizing scaled by the interaction's CX count (eps_cz = 0.0072, Elder C4999)
  - mid-circuit readout assignment error eps_ro_mid = 0.02 (T0.3 noise model)
  - final readout error eps_ro_final = 0.015
  - reset failure p_reset_fail = 0.005
Also runs the PHASE AUDIT numerically: relative-phase multi-control substitutions
(Margolus RCCX for Tier A; phase-tolerant C3X for Tier B) vs full CCX/C3X, uniform
across variants (f-oblivious), comparing every graded statistic.

Model notes (stated, not hidden): gate noise = one 2q-depolarizing channel on (probe,
detector) with strength n_cx * eps_cz applied per segment (linearized composite; valid
for n_cx*eps << 1 — worst case here 16*0.0072 = 0.115). The classical-definite input
register is held definite (f-oblivious lint: same gate SEQUENCE all variants; here the
sequence is identical and the definite controls collapse the multi-control gate to its
sector action, with the substitution's sector phases retained exactly).
"""
import numpy as np, json, sys, math

EPS_CZ, RO_MID, RO_FIN, RESET_FAIL = 0.0072, 0.02, 0.015, 0.005
SEG_CX = {"A": 6, "B": 16}

# 2-qubit system: probe (q0), detector (q1). Basis |p d>: 00,01,10,11
def kron(*ops):
    out = np.array([[1.0+0j]])
    for o in ops: out = np.kron(out, o)
    return out
I2 = np.eye(2); X = np.array([[0,1],[1,0]],dtype=complex)
def ry(th): return np.array([[math.cos(th/2), -math.sin(th/2)],[math.sin(th/2), math.cos(th/2)]],dtype=complex)

# Sector action of the interaction on (p,d), given definite non-probe controls:
#   armed (answer=1):  CX(p->d), possibly with substitution sector phases
#   transparent:       I, possibly with substitution sector phases
# Phases from relative-phase gates, computed from the FULL gate matrices:
def sector_ops(sub: bool, tier: str):
    """Return (U_armed, U_transparent) 4x4 on |p d> for full vs relative-phase gate."""
    if not sub:
        cx = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],dtype=complex)  # CX p->d
        return cx, np.eye(4,dtype=complex)
    # Build full RCCX (Margolus) / RC3X matrices and slice the definite-control sectors.
    # Margolus RCCX on (c1,c2,t) = Toffoli up to -1 phase on |1,0,1> (c1=1,c2=0,t=1).
    if tier == "A":
        # controls (p, r): armed sector r=1 -> exact CCX sector = CX. transparent r=0 ->
        # diag(1,1,1,-1) on |p d> (phase on p=1,d=1).
        armed = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],dtype=complex)
        transparent = np.diag([1,1,1,-1]).astype(complex)
        return armed, transparent
    else:
        # RC3X (qiskit rc3x) phases live on control-configs with t=1; marked sector
        # (x=11) is exact C(CX); unmarked sectors acquire diag phases incl. (p=1,d=1)
        # and possibly (p=0,d=1) with DIFFERENT phases (i vs -1 class). Worst case:
        transparent = np.diag([1, 1j, 1, -1]).astype(complex)   # p0d1 -> i, p1d1 -> -1
        armed = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],dtype=complex)
        return armed, transparent

def depolarize(rho, lam):
    return (1-lam)*rho + lam*np.trace(rho)*np.eye(4)/4

def run_ladder(N, armed, tier, substitution):
    """Return dict of record-class probabilities: eta (p=0,no fire), f0call (p=1,no fire),
    fired (any recorded fire), other."""
    U_arm, U_trans = sector_ops(substitution, tier)
    U = U_arm if armed else U_trans
    lam = min(1.0, SEG_CX[tier]*EPS_CZ)
    rot = kron(ry(math.pi/N), I2)
    # branches: (rho_unnormalized 4x4, prob_weight, fired_flag)
    branches = [(np.outer([1,0,0,0],[1,0,0,0]).astype(complex), 1.0, False)]
    for _ in range(N):
        nxt = []
        for rho, w, fired in branches:
            rho = rot @ rho @ rot.conj().T
            rho = U @ rho @ U.conj().T
            rho = depolarize(rho, lam)
            # projective measure detector (q1): P0 = |p0>+|p1> with d=0
            P0 = np.diag([1,0,1,0]).astype(complex); P1 = np.diag([0,1,0,1]).astype(complex)
            for proj, dbit in ((P0,0),(P1,1)):
                r2 = proj @ rho @ proj
                p = float(np.real(np.trace(r2)))
                if p < 1e-12: continue
                r2 = r2/p
                # readout assignment error on the RECORD:
                for rec, prec in ((dbit, 1-RO_MID),(1-dbit, RO_MID)):
                    # reset detector to |0> (fail -> |1>)
                    rho_d0 = np.zeros((4,4),dtype=complex)
                    # trace out d, re-tensor with |0><0| (or |1><1| on fail)
                    pr = np.array([[r2[0,0]+r2[1,1], r2[0,2]+r2[1,3]],[r2[2,0]+r2[3,1], r2[2,2]+r2[3,3]]])
                    for dstate, pfail in ((0,1-RESET_FAIL),(1,RESET_FAIL)):
                        dd = np.zeros((2,2)); dd[dstate,dstate]=1
                        rr = np.kron(pr, dd)
                        nxt.append((rr, w*p*prec*pfail, fired or rec==1))
        # merge branches with same fired flag to keep branch count bounded
        merged = {}
        for rho, w, f in nxt:
            if f in merged: merged[f] = (merged[f][0]+w*rho, merged[f][1]+w)
            else: merged[f] = (w*rho, w)
        branches = [(rho/w if w>0 else rho, w, f) for f,(rho,w) in merged.items()]
    out = {"eta":0.0,"f0call":0.0,"fired":0.0,"other":0.0}
    for rho, w, fired in branches:
        if fired: out["fired"] += w; continue
        p_p1 = float(np.real(rho[2,2]+rho[3,3]))
        p_p0 = float(np.real(rho[0,0]+rho[1,1]))
        # final readout error on probe
        p1_meas = p_p1*(1-RO_FIN) + p_p0*RO_FIN
        p0_meas = p_p0*(1-RO_FIN) + p_p1*RO_FIN
        out["eta"] += w*p0_meas
        out["f0call"] += w*p1_meas
    return out

if __name__ == "__main__":
    res = {"model": {"eps_cz":EPS_CZ,"ro_mid":RO_MID,"ro_fin":RO_FIN,"reset_fail":RESET_FAIL,"seg_cx":SEG_CX},
           "table": {}, "phase_audit": {}}
    for tier in ("A","B"):
        for N in (1,2,4,8):
            for armed in (True, False):
                k = f"{tier}_N{N}_{'armed' if armed else 'transparent'}"
                full = run_ladder(N, armed, tier, substitution=False)
                sub  = run_ladder(N, armed, tier, substitution=True)
                res["table"][k] = {kk: round(vv,4) for kk,vv in full.items()}
                dev = max(abs(full[s]-sub[s]) for s in full)
                res["phase_audit"][k] = round(dev, 6)
    json.dump(res, sys.stdout, indent=1); print()
