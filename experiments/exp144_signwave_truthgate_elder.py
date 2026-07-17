#!/usr/bin/env python3
"""Exp144 SIGN-WAVE P3 TRUTH-GATE (Elder) — must recover KNOWN signs under the
MEASURED noise channel BEFORE the sign wave flies (chair P3, C4810).

The sign wave is a SINGLE-COPY measurement (prep +1 eigenstate of iQⱼPⱼ, evolve
V=e^{-iHt}, measure Qⱼ → ⟨Qⱼ(t)⟩ = ∓sin(2cⱼt)) — the SAME detector class the
conv conservation filter belonged to, which the measured noise DROWNED (n=4 conv
falsified, C4195/C4810). P3 rule: a detector with no test that can fail must not
fly. This gate builds the EXACT sign circuit, applies the measured noise as an
attenuation calibrated FROM the flown data, samples N_SIGN, and asks: is the sign
RECOVERED with margin? Kill if not.

Calibration (honest, from flown n=4): a genuinely-conserved candidate ideal
⟨P(t)⟩=1 read at most 0.83 (rate 0.665) → single-copy ~26-CX attenuation
att_best≈0.66; most candidates drowned to att≈0 (rate 0.5). So the sign readout
amplitude is att·sin(2cⱼt) with att swept over the MEASURED span [0.0, 0.66].
"""
import itertools, math, sys
import numpy as np
from scipy.linalg import expm

I2 = np.eye(2, dtype=complex)
PX = np.array([[0, 1], [1, 0]], complex)
PY = np.array([[0, -1j], [1j, 0]], complex)
PZ = np.array([[1, 0], [0, -1]], complex)
MAT = {"I": I2, "X": PX, "Y": PY, "Z": PZ}
N_SIGN = 100
T = 2.0
GRID = [0.15, 0.20, 0.25]
RNG = np.random.default_rng(20260717)


def kron(s):
    m = np.array([[1.0 + 0j]])
    for c in s:
        m = np.kron(m, MAT[c])
    return m


def commutes(a, b):
    return sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y) % 2 == 0


def string_prod(a, b):
    out = []
    for x, y in zip(a, b):
        if x == "I": out.append(y)
        elif y == "I": out.append(x)
        elif x == y: out.append("I")
        else: out.append(({"X", "Y", "Z"} - {x, y}).pop())
    return "".join(out)


def sample_instance(n):
    while True:
        c = ["".join(RNG.choice(list("XYZ"), n)) for _ in range(3)]
        if len(set(c)) == 3 and all(commutes(a, b) for a, b in itertools.combinations(c, 2)):
            labs = set()
            ok = True
            for r in range(1, 4):
                for S in itertools.combinations(range(3), r):
                    g = "I" * n
                    for j in S: g = string_prod(g, c[j])
                    if g in labs: ok = False
                    labs.add(g)
            if ok:
                return c


def ideal_signreadout(n, terms, coeffs, j):
    """EXACT noiseless ⟨Qⱼ(t)⟩ via statevector — confirms = -sin(2 cⱼ t)."""
    d = 2 ** n
    all_p = ["".join(p) for p in itertools.product("IXYZ", repeat=n)]
    Pj = terms[j]
    probe = next(q for q in all_p if q != "I"*n and not commutes(q, Pj)
                 and all(commutes(q, terms[k]) for k in range(3) if k != j))
    # +1 eigenstate of iQP (matrix, sim only)
    R = 1j * kron(probe) @ kron(Pj)
    w, v = np.linalg.eigh(R)
    psi = v[:, np.argmin(np.abs(w - 1))]
    V = np.eye(d, dtype=complex)
    for lab, c in zip(terms, coeffs):
        V = V @ expm(-1j * c * T * kron(lab))
    psit = V @ psi
    return float(np.real(psit.conj() @ kron(probe) @ psit)), coeffs[j]


def gate(att, reps=400, n=4):
    """Sign-recovery probability at attenuation att, N_SIGN shots, per grid coeff."""
    per_c = {c: [0, 0] for c in GRID}
    for _ in range(reps):
        terms = sample_instance(n)
        signs = RNG.choice([-1, 1], 3)
        coeffs = [s * g for s, g in zip(signs, RNG.permutation(GRID))]
        for j in range(3):
            ideal, cj = ideal_signreadout(n, terms, coeffs, j)   # = -sin(2 cj t)
            mu = att * ideal                                       # measured-noise attenuation
            p = (1 + mu) / 2
            draws = RNG.binomial(N_SIGN, p, size=1)[0]
            mean = 2 * draws / N_SIGN - 1
            recovered = (-np.sign(mean)) == np.sign(cj)            # sign(cj) = -sign(<Q>)
            g = abs(round(cj, 2))
            per_c[g][0] += int(recovered); per_c[g][1] += 1
    return {c: per_c[c][0] / per_c[c][1] for c in GRID}


if __name__ == "__main__":
    print(f"SIGN-WAVE P3 TRUTH-GATE — N_SIGN={N_SIGN}, per-grid sign-recovery prob")
    print("att = single-copy attenuation (measured n=4 span: 0.66 best-candidate → 0 drowned)\n")
    print(f"{'att':>5} | {'c=0.15':>7} {'c=0.20':>7} {'c=0.25':>7} | worst-term")
    worst_by_att = {}
    for att in (0.66, 0.5, 0.35, 0.2, 0.1):
        r = gate(att)
        worst = min(r.values())
        worst_by_att[att] = worst
        print(f"{att:>5.2f} | {r[0.15]:>7.2f} {r[0.20]:>7.2f} {r[0.25]:>7.2f} | {worst:.2f}")
    print("\nKILL CONDITION (P3): sign wave flies ONLY if worst-term recovery >= 0.90")
    print("at the CREDIBLE measured att. Best-candidate att≈0.66 governs the")
    print("cleanest instances; drowned att≈0.1-0.2 is the typical n4 reality.")
    verdict = "FLIES (best-att)" if worst_by_att[0.66] >= 0.90 else "MARGINAL/KILL"
    typ = "FLIES" if worst_by_att[0.2] >= 0.90 else "DROWNED at typical att"
    print(f"\nVERDICT: best-att(0.66) worst-term {worst_by_att[0.66]:.2f} -> {verdict};"
          f" typical-att(0.2) worst-term {worst_by_att[0.2]:.2f} -> {typ}")
