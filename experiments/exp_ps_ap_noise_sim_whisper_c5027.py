#!/usr/bin/env python3
"""Does a PS_ap hidden-shift instance survive the noise its T-count implies?

THE QUESTION. Pricing the PS_ap oracle gave ~3,220 T at k=20 (n=40), which at a 1e-3 per-T
error rate is ~4% circuit fidelity. That sounds fatal. But F120 — the shot-axis decoder,
DOWNGRADED from an advantage claim to an instrument result — exists precisely to read a signal
through noise that destroys every individual shot. So: does the shift survive at 4%?

THE ALGORITHM (Roetteler, hidden shift on bent functions):
    |0>  --H^n-->  uniform
         --O_fs--> (-1)^{f(x XOR s)}
         --H^n-->
         --O_ftilde--> (-1)^{f~(y)}
         --H^n-->  measure  ->  s, with certainty in the noiseless case
This needs the DUAL, which is exactly what C5027 showed is cheap for PS_ap: the dual spread is
the same spread under sigma(a) = a^-1.

NOISE MODEL: global depolarising, rho -> F rho_ideal + (1-F) I/2^n. That is the standard deep
circuit model (it is what XEB fidelity means) and it is what the campaign's own fidelity numbers
denote. Under it the ideal outcome survives with probability F and everything else is uniform.

PRE-REGISTERED BEFORE RUNNING:
  N1  the noiseless algorithm returns s with probability 1. If not, my circuit is wrong.
  N2  under global depolarising at fidelity F, P(measure s) = F + (1-F)/2^n, so the shot count
      to see it once is ~1/F ~ 25 at F=0.04. I expect recovery to be EASY, and I am pre-stating
      why that is not a triumph: global depolarising is a KIND model. It says the signal
      survives intact with probability F rather than being corrupted. A model where noise
      CORRUPTS the answer bitwise would be harder and is not what circuit fidelity means.
  N3  the self-verification changes the shot economics entirely. Because the dual is cheap we
      can TEST each distinct outcome rather than needing it to be the statistical mode. That
      turns "get s as the modal outcome" into "get s at least once", which is ~1/F shots.
  N4  RISK I EXPECT TO MATTER MORE THAN THE NOISE: at n=40 with F=0.04 the wrong outcomes are
      spread over 2^40, so they essentially never repeat and never verify. The danger is not
      noise but whether 1/F shots is affordable at the QPU's shot cost. That is arithmetic, not
      physics, and I will report it.

Substrate: claude-fable-5, Whisper C5027. Creator directive: "run the noise simulation".
"""
import sys

import numpy as np

sys.path.insert(0, "/droid/repos/quantum/experiments")
from exp_bent_families_ps_whisper_c5027 import gf_mul, walsh  # noqa: E402


def gf_inv(a, k):
    if a == 0:
        return 0
    for b in range(1, 2 ** k):
        if gf_mul(a, b, k) == 1:
            return b
    raise ValueError


def tr(z, k):
    s, t = 0, z
    for _ in range(k):
        s ^= t
        t = gf_mul(t, t, k)
    return s & 1


def ps_ap(k, lam=1):
    """f(x,y) = Tr(lambda * x/y). g = Tr(lambda .) is balanced, g(0)=0, F2-LINEAR (0 T-gates),
    and verified bent at C5027."""
    n = 2 * k
    f = np.zeros(2 ** n, dtype=np.int8)
    for v in range(2 ** n):
        x = v & ((1 << k) - 1)
        y = v >> k
        f[v] = tr(gf_mul(lam, gf_mul(x, gf_inv(y, k), k), k), k) if y else 0
    return f


def dual_of(f, n):
    W = walsh(f, n)
    assert np.all(np.abs(W) == 2 ** (n // 2)), "not bent"
    return ((1 - np.sign(W)) // 2).astype(np.int8)


def roetteler(f, dual, s, n):
    """Exact state-vector run of the hidden-shift algorithm. Returns |amplitude|^2."""
    N = 2 ** n
    H = np.full(N, 1.0 / np.sqrt(N))                      # H^n |0>
    idx = np.arange(N)
    H = H * (1 - 2.0 * f[idx ^ s])                        # O_{f_s}
    H = hadamard(H, n)
    H = H * (1 - 2.0 * dual[idx])                         # O_{f~}
    H = hadamard(H, n)
    return np.abs(H) ** 2


def hadamard(v, n):
    v = v.copy()
    h = 1
    while h < 2 ** n:
        v = v.reshape(-1, 2 * h)
        a, b = v[:, :h].copy(), v[:, h:].copy()
        v[:, :h], v[:, h:] = (a + b), (a - b)
        v = v.reshape(-1)
        h *= 2
    return v / np.sqrt(2 ** n)


def main():
    rng = np.random.default_rng(5027)
    print("PS_ap HIDDEN SHIFT UNDER NOISE — does the shift survive its own T-count?\n")

    # ---- N1: noiseless correctness -----------------------------------------
    print("  N1 — noiseless: does the algorithm return s with probability 1?")
    for k in (3, 4, 5):
        n = 2 * k
        f = ps_ap(k)
        d = dual_of(f, n)
        ok = True
        for _ in range(6):
            s = int(rng.integers(0, 2 ** n))
            p = roetteler(f, d, s, n)
            if abs(p[s] - 1.0) > 1e-9:
                ok = False
                worst = p[s]
                break
        print(f"    k={k} n={n}: P(measure s) = 1 exactly on 6 random shifts: {ok}"
              + ("" if ok else f"  (worst {worst:.4f})"))

    # ---- N2/N3: global depolarising + cheap verification --------------------
    print("\n  N2/N3 — global depolarising, rho -> F rho + (1-F) I/2^n")
    print("          the dual is cheap, so each distinct outcome can be VERIFIED rather than")
    print("          needing to be the statistical mode.\n")
    k, n = 5, 10
    f = ps_ap(k)
    d = dual_of(f, n)
    print(f"    {'F':>6} {'shots':>7} {'P(s in shots)':>15} {'recovered':>11} {'expected 1-(1-F)^N':>20}")
    for F in (0.04, 0.10, 0.50):
        for N in (10, 25, 75, 200):
            hits = 0
            trials = 200
            for _ in range(trials):
                s = int(rng.integers(0, 2 ** n))
                p_ideal = roetteler(f, d, s, n)
                p = F * p_ideal + (1 - F) / 2 ** n
                p = p / p.sum()
                shots = rng.choice(2 ** n, size=N, p=p)
                # VERIFY each distinct outcome — this is what the cheap dual buys
                hits += int(any(c == s for c in set(shots.tolist())))
            exp = 1 - (1 - F) ** N
            print(f"    {F:>6.2f} {N:>7} {hits/trials:>15.3f} {hits:>7}/{trials} {exp:>20.3f}")


if __name__ == "__main__":
    main()
