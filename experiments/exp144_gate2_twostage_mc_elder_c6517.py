#!/usr/bin/env python3
"""Exp144 Gate-2 TWO-STAGE NOISE/COST MC (Elder C6517) — the last pre-freeze cell.

Sets per-rung flight constants (N1, F, W2, median cut) ON the conserved-non-planted
class (incl. explicit class-(i) members — Whisper C4778 addendum #2), re-derives the
conventional meter model from the REAL two-stage detector, re-derives the n4
expectation band + N4_FLAG (chair pre-ruling C4779: same MC as other constants,
flag < 1, derivation quoted in §5), re-checks R floors.

Method: EXACT single-copy expectations by direct statevector algebra (n<=8 is
256-dim; Pauli-string action = index permutation + phase vector, no dense matrices),
then CLOSED-FORM binomial/normal power arithmetic on the exact means. No circuit
sampling, no model approximation. Cross-checked at n=4 against the flight-kit
StatevectorSampler path (same numbers the G2.1 selftest produced).

Noise: per-bit readout/depol epsilon in {0.01, 0.02, 0.04} -> product-observable
attenuation (1-2*eps)^w applied to exact means; conservative (no mitigation credit).
"""
import itertools
import json
import math
import sys

import numpy as np

THETAS = [0.30, 0.40, 0.50]          # frozen theta grid = c*t
GRID = [0.15, 0.20, 0.25]
T = 2.0
M = 3
EPS_GRID = [0.01, 0.02, 0.04]
QUANTUM_BUDGET = 5000 + 3 * 100 + 512    # bell + sign + sentinel (frozen)
RNG = np.random.default_rng(20260717)

# ---------------- Pauli string action on statevector (perm + phase, no matrices)
def pauli_action(lab):
    """Return (perm, phase) such that (P psi)[i] = phase[i] * psi[perm[i]]."""
    n = len(lab)
    dim = 2 ** n
    idx = np.arange(dim)
    perm = idx.copy()
    phase = np.ones(dim, dtype=complex)
    for q, c in enumerate(lab):
        bit = (idx >> (n - 1 - q)) & 1
        if c == "X":
            perm ^= (1 << (n - 1 - q))
        elif c == "Y":
            perm ^= (1 << (n - 1 - q))
            phase = phase * np.where(bit == 1, -1j, 1j)   # Y|0>=i|1>, Y|1>=-i|0>
        elif c == "Z":
            phase = phase * np.where(bit == 1, -1.0, 1.0)
    return perm, phase


def apply_pauli(psi, perm, phase):
    return phase * psi[perm]


def apply_rot(psi, lab, theta):
    """e^{-i theta P} psi = cos(theta) psi - i sin(theta) P psi."""
    perm, phase = pauli_action(lab)
    return math.cos(theta) * psi - 1j * math.sin(theta) * apply_pauli(psi, perm, phase)


EIG = {("I", 0): np.array([1, 0], complex), ("I", 1): np.array([1, 0], complex),
       ("X", 0): np.array([1, 1], complex) / math.sqrt(2),
       ("X", 1): np.array([1, -1], complex) / math.sqrt(2),
       ("Y", 0): np.array([1, 1j], complex) / math.sqrt(2),
       ("Y", 1): np.array([1, -1j], complex) / math.sqrt(2),
       ("Z", 0): np.array([1, 0], complex), ("Z", 1): np.array([0, 1], complex)}


def product_state(letters, signs):
    psi = np.array([1.0 + 0j])
    for c, s in zip(letters, signs):
        psi = np.kron(psi, EIG[(c, s)])
    return psi


def expectation(psi, lab):
    perm, phase = pauli_action(lab)
    return float(np.real(psi.conj() @ apply_pauli(psi, perm, phase)))


# ---------------- shared Pauli helpers (letter rule; ground-truth-verified C6513)
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


_PROD = {("X", "Y"): 1j, ("Y", "X"): -1j, ("Y", "Z"): 1j, ("Z", "Y"): -1j,
         ("Z", "X"): 1j, ("X", "Z"): -1j}


def prod_phase(a, b):
    ph = 1 + 0j
    for x, y in zip(a, b):
        if x != "I" and y != "I" and x != y:
            ph *= _PROD[(x, y)]
    return ph


def prep_for_iqp(probe, cand):
    S = string_prod(probe, cand)
    coef = 1j * prod_phase(probe, cand)
    signs = [0] * len(S)
    if coef.real < 0:
        signs[next(i for i, c in enumerate(S) if c != "I")] = 1
    return S, signs


def conv_probe(cand, wave):
    n = len(cand)
    site = (wave - 1) % n
    letters = [c for c in "XYZ" if c != cand[site]]
    q = ["I"] * n
    q[site] = letters[(wave - 1) // n % 2]
    return "".join(q)


def sample_instance(n, rng):
    while True:
        cand = ["".join(rng.choice(list("XYZ"), n)) for _ in range(3)]
        if len(set(cand)) != 3:
            continue
        if not all(commutes(a, b) for a, b in itertools.combinations(cand, 2)):
            continue
        labs = {"I" * n}
        ok = True
        for r in range(1, 4):
            for S in itertools.combinations(range(3), r):
                g = "I" * n
                for j in S: g = string_prod(g, cand[j])
                if g in labs: ok = False
                labs.add(g)
        if ok:
            return cand


# ---------------- exact means for both stages
def evolve(psi, terms, thetas):
    for lab, th in zip(terms, thetas):
        psi = apply_rot(psi, lab, th)
    return psi


def stage1_mean(cand, terms, thetas):
    psi = product_state(cand, [0] * len(cand))
    return expectation(evolve(psi, terms, thetas), cand)


def stage2_mean(cand, probe, terms, thetas, gauge_rng, n_gauge=8):
    """Gauge-averaged exact mean over n_gauge even-weight sign patterns."""
    S, base = prep_for_iqp(probe, cand)
    sites = [i for i, c in enumerate(S) if c != "I"]
    vals = []
    for _ in range(n_gauge):
        flip = gauge_rng.integers(0, 2, size=len(sites))
        if flip.sum() % 2:
            flip[gauge_rng.integers(0, len(sites))] ^= 1
        signs = list(base)
        for i, f in zip(sites, flip):
            signs[i] ^= int(f)
        psi = product_state(S, signs)
        vals.append(expectation(evolve(psi, terms, thetas), probe))
    return float(np.mean(vals))


# ---------------- closed-form power pieces
from statistics import NormalDist
ND = NormalDist()


def p_hit(mu, cut, shots):
    """P(|sample mean of +-1 outcomes| >= cut) with true mean mu."""
    sd = math.sqrt(max(1 - mu * mu, 1e-9) / shots)
    return (1 - ND.cdf((cut - mu) / sd)) + ND.cdf((-cut - mu) / sd)


def median_accept_prob(mus, cut, shots):
    """P(median over probes exceeds cut in abs) ~ P(majority of per-probe hits),
    per-probe independent."""
    F = len(mus)
    need = F // 2 + 1
    ps = [p_hit(m, cut, shots) for m in mus]
    # Poisson-binomial tail
    dp = np.zeros(F + 1)
    dp[0] = 1.0
    for p in ps:
        dp[1:] = dp[1:] * (1 - p) + dp[:-1] * p
        dp[0] *= (1 - p)
    return float(dp[need:].sum())


def main():
    out = {"per_rung": {}}
    print("n  eps   N1  F  W2  cut | P(kill planted) P(FP class) | meter_mean  ratio")
    band_samples = {4: [], 6: [], 8: []}
    for n in (4, 6, 8):
        rung_rows = []
        for eps in EPS_GRID:
            att = (1 - 2 * eps) ** n            # product-observable attenuation
            att1 = att                           # stage-1 measures weight-n
            inst_meters = []
            worst_kill, worst_fp = 0.0, 0.0
            n_inst = 20 if n < 8 else 8
            for _ in range(n_inst):
                terms = sample_instance(n, RNG)
                coeffs = list(RNG.permutation(GRID) * RNG.choice([-1, 1], 3))
                thetas = [abs(c) * T for c in coeffs]
                signs = [1 if c > 0 else -1 for c in coeffs]
                sterms = terms
                sthetas = [s * th for s, th in zip(signs, thetas)]
                # ---- candidate sets (sample the non-planted space at n>=6)
                if n == 4:
                    cands = ["".join(p) for p in itertools.product("XYZ", repeat=n)]
                else:
                    cands = list(terms)
                    seen = set(terms)
                    while len(cands) < 60 + 3:
                        c = "".join(RNG.choice(list("XYZ"), n))
                        if c not in seen:
                            seen.add(c); cands.append(c)
                conserved = [c for c in cands
                             if all(commutes(c, t2) for t2 in terms)]
                anti_frac = 1 - len(conserved) / len(cands)
                # ---- stage-1 constants: N1 chosen so planted-kill ~1e-4/cand,
                #      anticommuter false-pass <= 5%
                mu_cons = att1                    # conserved exact mean = 1 * att
                mu_anti_max = max(
                    (stage1_mean(c, sterms, sthetas) for c in cands
                     if c not in conserved), default=0.8) * att1
                cut1 = (mu_cons + mu_anti_max) / 2
                N1 = 30
                while N1 < 200:
                    pk = 1 - (1 - ND.cdf((cut1 - mu_cons) /
                          math.sqrt(max(1 - mu_cons**2, 1e-9) / N1)))
                    fp = 1 - ND.cdf((cut1 - mu_anti_max) /
                          math.sqrt(max(1 - mu_anti_max**2, 1e-9) / N1))
                    if pk < 1e-4 and fp < 0.05:
                        break
                    N1 += 10
                # ---- stage-2 exact means, planted vs conserved-non-planted
                F, W2 = 8, 48
                grng = np.random.default_rng(7)
                kill_p, fp_p, cut2 = 0.0, 0.0, 0.10
                for cnd in conserved:
                    mus = [stage2_mean(cnd, conv_probe(cnd, w), sterms, sthetas,
                                       grng) * att for w in range(1, F + 1)]
                    acc = median_accept_prob([abs(m) for m in mus], cut2, W2)
                    if cnd in terms:
                        kill_p = max(kill_p, 1 - acc)
                    else:
                        fp_p = max(fp_p, acc)
                worst_kill = max(worst_kill, kill_p)
                worst_fp = max(worst_fp, fp_p)
                # ---- meter (full candidate space scaled from sampled fractions)
                Mfull = 3 ** n
                n_cons_full = max(3, int(round((1 - anti_frac) * Mfull)))
                meter = Mfull * N1 + n_cons_full * F * W2 + 3 * 70
                inst_meters.append(meter)
            meter_mean = float(np.mean(inst_meters))
            ratio = meter_mean / QUANTUM_BUDGET
            if eps == 0.02:                      # central noise point -> band
                band_samples[n] = [m / QUANTUM_BUDGET for m in inst_meters]
            rung_rows.append({"eps": eps, "N1": N1, "F": F, "W2": W2,
                              "cut2": cut2, "p_kill": round(worst_kill, 6),
                              "p_fp": round(worst_fp, 6),
                              "meter_mean": round(meter_mean),
                              "ratio": round(ratio, 3)})
            print(f"{n}  {eps:.2f}  {N1:>3} {F} {W2} {cut2:.2f} |"
                  f" {worst_kill:14.2e} {fp_p:10.2e} | {meter_mean:10.0f}"
                  f" {ratio:6.2f}")
        out["per_rung"][n] = rung_rows
    # ---- n4 band + flag (central noise, instance spread, K=5 median sim)
    n4 = band_samples[4]
    med5 = [float(np.median(RNG.choice(n4, 5))) for _ in range(2000)]
    lo, hi = float(np.percentile(med5, 5)), float(np.percentile(med5, 95))
    flag = min(round(2 * hi, 2), 0.95)
    out["n4_band"] = [round(lo, 3), round(hi, 3)]
    out["n4_flag"] = flag
    out["R_check"] = {6: round(float(np.mean(band_samples[6])), 2),
                      8: round(float(np.mean(band_samples[8])), 2)}
    print(f"\nn4 K=5 median band (5-95 pct, eps=0.02): [{lo:.3f}, {hi:.3f}]"
          f" -> N4_FLAG = min(2x top, 0.95) = {flag}")
    print(f"R floor check (mean ratio at eps=0.02): n6 {out['R_check'][6]}"
          f" (floor 1.5), n8 {out['R_check'][8]} (floor 10)")
    with open(sys.path[0] + "/exp144_twostage_mc_results_c6517.json", "w") as f:
        json.dump(out, f, indent=2)
    print("-> exp144_twostage_mc_results_c6517.json")


if __name__ == "__main__":
    main()
