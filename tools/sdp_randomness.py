#!/usr/bin/env python3
"""sdp_randomness.py — one-sided device-independent (1SDI) randomness from a
steering assemblage, the EXACT SDP (Whisper C4679; the tool the Exp136k wall
flagged. Substrate claude-opus-4-8).

WHY AN SDP AND WHY IT IS EXACT HERE: certified 1SDI randomness of the untrusted
party's (Alice's) outcome = -log2 P_guess, where Eve maximizes her guess of
Alice's outcome subject to reproducing the OBSERVED assemblage {sigma_{a|x}} on
the trusted qubit (Bob). Candidate ANALYTIC bounds failed the boundary check
(certified randomness at the unsteerable bound where it must be 0, C4678). The
correct object is an SDP. For a TRUSTED QUBIT Bob it is EXACT (no NPA hierarchy):
by GHJW/Schrodinger-HJW, a qubit assemblage is quantum-realizable iff it is PSD
and no-signaling — exactly the SDP constraints below.

SDP (Passaro-Acin et al. 2015, NJP 17 113010, adapted):
  variables: sigma^e_{a|x}  (2x2 Hermitian), e = Eve's guess of Alice's outcome
  maximize   P_guess = sum_e Tr[ sigma^e_{e | x*} ]        (Eve guesses e=a at x*)
  s.t.       sum_e sigma^e_{a|x} = sigma_{a|x}   (recover observed assemblage)
             sigma^e_{a|x} >= 0                  (PSD)
             sum_a sigma^e_{a|x} indep. of x     (no-signaling per Eve-branch)
  H_min = -log2(P_guess).

Consumes an assemblage {(a,x): 2x2 rho}. Build one from Werner-state models
(validation) or from hardware assemblage tomography (Bob's X/Y/Z conditional
states per Alice outcome/setting — a cheap follow-up flight).
"""
import itertools
import json
import math
import os

import numpy as np

I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = {"X": SX, "Y": SY, "Z": SZ}
BELL = np.array([1, 0, 0, 1], dtype=complex) / math.sqrt(2)
DIRS3 = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}
DIRS2 = {"X": (1, 0, 0), "Z": (0, 0, 1)}


def bloch_op(n):
    return n[0] * SX + n[1] * SY + n[2] * SZ


def werner_assemblage(v, dirs):
    """Assemblage on Bob from rho_v = v|Phi+><Phi+| + (1-v)I/4, Alice measuring
    each direction (outcome a=+/-1). sigma_{a|x} = Tr_A[(M_a^x (x) I) rho_v]."""
    rho = v * np.outer(BELL, BELL.conj()) + (1 - v) * np.eye(4) / 4
    asm = {}
    for x, n in dirs.items():
        for a in (+1, -1):
            M = (I2 + a * bloch_op(n)) / 2         # Alice projector
            op = np.kron(M, I2)
            full = op @ rho
            # partial trace over A (qubit 0): sigma_B[i,j] = sum_k full[k,i ; k,j]
            f = full.reshape(2, 2, 2, 2)           # (A_out,B_out,A_in,B_in)
            sigma = np.einsum('kikj->ij', f)
            asm[(a, x)] = sigma
    return asm


def cjwr_S(asm, dirs, signs=None):
    """CJWR steering value S_n = (1/sqrt n)|sum_k s_k <A_k B_k>|,
    <A_k B_k> = sum_a a Tr[sigma_{a|x_k} B_k], B_k = trusted Pauli in dir k."""
    n = len(dirs)
    tot = 0.0
    for x, nvec in dirs.items():
        Bk = bloch_op(nvec)
        e = sum(a * np.real(np.trace(asm[(a, x)] @ Bk)) for a in (+1, -1))
        s = 1.0 if signs is None else signs[x]
        tot += s * e
    return abs(tot) / math.sqrt(n)


def guessing_probability(asm, x_star, outcomes=(+1, -1)):
    """Exact 1SDI SDP for P_guess of Alice's outcome at setting x_star."""
    import cvxpy as cp
    settings = sorted({x for (_, x) in asm}, key=str)
    # sub-assemblage variables sigma[e][(a,x)]
    var = {e: {(a, x): cp.Variable((2, 2), hermitian=True)
               for a in outcomes for x in settings} for e in outcomes}
    cons = []
    for a in outcomes:
        for x in settings:
            cons.append(sum(var[e][(a, x)] for e in outcomes) == asm[(a, x)])
            for e in outcomes:
                cons.append(var[e][(a, x)] >> 0)
    for e in outcomes:                                   # no-signaling per branch
        marg = {x: sum(var[e][(a, x)] for a in outcomes) for x in settings}
        for x in settings[1:]:
            cons.append(marg[x] == marg[settings[0]])
    obj = cp.Maximize(cp.real(sum(cp.trace(var[e][(e, x_star)])
                                  for e in outcomes)))
    prob = cp.Problem(obj, cons)
    prob.solve(solver=cp.SCS, eps=1e-7, max_iters=50000)
    pg = float(prob.value)
    return pg, prob.status


def hmin(pg):
    pg = min(max(pg, 1e-12), 1.0)
    return -math.log2(pg)


def certify(asm, x_star, dirs):
    pg, status = guessing_probability(asm, x_star)
    return {"P_guess": pg, "H_min_bits": hmin(pg),
            "S_n": cjwr_S(asm, dirs), "solver_status": status}


def main():
    out = {}
    print("=== VALIDATION: Werner n=3 (X,Y,Z) — the boundary the analytic "
          "bounds FAILED ===")
    thr = 1 / math.sqrt(3)                    # n=3 MUB steering threshold
    rows = []
    for v in [1.0, 0.95, 0.90, 0.80, 0.70, thr + 1e-3, thr, thr - 0.02, 0.5]:
        asm = werner_assemblage(v, DIRS3)
        pg, st = guessing_probability(asm, "Z")
        S = cjwr_S(asm, DIRS3, signs={"X": 1, "Y": -1, "Z": 1})
        rows.append({"v": v, "S3": S, "P_guess": pg, "H_min": hmin(pg)})
        print(f"  v={v:.4f}  S3={S:.4f}  P_guess={pg:.4f}  "
              f"H_min={hmin(pg):.4f} bits   [{st}]")
    out["werner_n3"] = rows
    # boundary check: H_min ~0 at threshold, ~1 at v=1
    at_thr = [r for r in rows if abs(r["v"] - thr) < 1e-6][0]
    at_one = [r for r in rows if r["v"] == 1.0][0]
    boundary_ok = at_thr["H_min"] < 0.02 and at_one["H_min"] > 0.98
    print(f"BOUNDARY CHECK: H_min(threshold v={thr:.4f}, S3=1)="
          f"{at_thr['H_min']:.4f} (~0?), H_min(v=1, S3=sqrt3)="
          f"{at_one['H_min']:.4f} (~1?) -> "
          f"{'PASS' if boundary_ok else 'FAIL'}")

    print("\n=== VALIDATION: Werner n=2 (X,Z), threshold v=1/sqrt2 ===")
    thr2 = 1 / math.sqrt(2)
    for v in [1.0, 0.85, thr2 + 1e-3, thr2, 0.6]:
        asm = werner_assemblage(v, DIRS2)
        pg, _ = guessing_probability(asm, "Z")
        print(f"  v={v:.4f}  S2={cjwr_S(asm, DIRS2):.4f}  "
              f"P_guess={pg:.4f}  H_min={hmin(pg):.4f} bits")

    # Map Exp136 S3 -> equivalent Werner v -> SDP randomness (Werner MODEL est.)
    print("\n=== Exp136/136k mapping (Werner-model estimate, NOT rigorous "
          "without assemblage tomography) ===")
    for dev, S3obs in (("marrakesh", 1.6813), ("kingston", 1.6582)):
        # Werner S3 = v*sqrt3  => v = S3/sqrt3
        v = S3obs / math.sqrt(3)
        asm = werner_assemblage(v, DIRS3)
        pg, _ = guessing_probability(asm, "Z")
        print(f"  {dev}: S3_obs={S3obs} -> Werner v={v:.4f} -> "
              f"H_min={hmin(pg):.4f} bits/use (MODEL est.)")
        out[f"exp136_{dev}_werner_est"] = {"S3": S3obs, "werner_v": v,
                                           "H_min_bits": hmin(pg)}
    out["boundary_check_pass"] = bool(boundary_ok)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "results",
                                     "sdp_randomness_validation.json"), "w"),
              indent=1, default=float)
    print("\nwrote results/sdp_randomness_validation.json")
    print("BOUNDARY CHECK:", "PASS" if boundary_ok else "FAIL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
