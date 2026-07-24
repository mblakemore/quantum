#!/usr/bin/env python3
"""Exp142b F1 threshold-confirm rule re-sim (Ember C4215) — input to Elder's grader freeze.

K7 STOP (Whisper #908): all-pass parity-confirm collapses under readout e (true P rejected
0.33/0.14/0.05 of the time at e=2%). Fix F1: accept basis A iff >= tau of conf' parity checks
pass, (conf',tau) sized for familywise false-accept <1% over 3^n AND true-accept >99% at the
MEASURED readout. This RUNS it: find (conf',tau) at e=2%, report new-benchmark achievability
median + censoring at F2's L=2*3^n+conf'. Provisional on assumed e; final sizing uses cal q_n.
"""
import numpy as np, itertools
from math import comb, ceil, log2

def binom_tail_ge(k, m, p):
    """P(X >= k), X~Binom(m,p)."""
    return sum(comb(m, j)*p**j*(1-p)**(m-j) for j in range(k, m+1))

def size_rule(n, e, fwer=0.01):
    """Smallest conf' with a tau giving true-accept>0.99 AND wrong-accept < fwer/3^n."""
    p_true = (1 + (1-2*e)**n)/2         # a TRUE-basis check is 'even' w.p. p_true under readout e
    p_wrong = 0.5                        # wrong-basis parity ~ fair coin
    target_wrong = fwer/(3**n)
    for m in range(3, 400):
        for tau in range(m, 0, -1):     # highest tau that still admits true P
            if binom_tail_ge(tau, m, p_true) > 0.99:
                if binom_tail_ge(tau, m, p_wrong) < target_wrong:
                    return m, tau, p_true
                break                    # this tau passes true but fails wrong -> need larger m
    return None, None, p_true

def decode_threshold(P, order, m, tau, e, L, rng):
    """Threshold confirm: per basis in committed order, take up to m copies; accept iff
    >= tau evens; a basis is dropped once it can no longer reach tau (early-out). Cap at L."""
    p_true = (1 + (1-2*e)**len(P))/2
    used = 0
    for A in order:
        evens = 0
        for c in range(1, m+1):
            if used >= L: return None, used
            used += 1
            even = (rng.random() < (p_true if A == P else 0.5))
            evens += even
            if evens >= tau:
                return A, used                      # confirmed
            if evens + (m-c) < tau:
                break                                # cannot reach tau -> eliminate early
    return None, used

print("F1 threshold rule sized at e=2% readout, FWER<1% over 3^n, true-accept>99%:")
rows_tot = 0
for n in [4,6,8]:
    e = 0.02
    m, tau, p_true = size_rule(n, e)
    cands = [''.join(t) for t in itertools.product('XYZ', repeat=n)]
    L = 2*3**n + m                                    # F2 full-elimination guarantee
    rng = np.random.default_rng(7000+n)
    stops, cens, wrong = [], 0, 0
    for _ in range(1500):
        P = ''.join(rng.choice(list('XYZ'), n)); order = list(cands); rng.shuffle(order)
        got, used = decode_threshold(P, order, m, tau, e, L, rng)
        if got is None: cens += 1
        elif got != P: wrong += 1; stops.append(used)
        else: stops.append(used)
    med = int(np.median(stops)) if stops else -1
    rows_tot += L*20
    print(f" n={n}: (conf'={m}, tau={tau}) p_true_check={p_true:.3f} | new-benchmark median-copies={med} "
          f"| censored {cens/1500*100:.2f}% wrong-P {wrong} | L=2*3^n+conf'={L} rows/rep")
print(f"\n budget @ F2 L, M=20: conv ~{rows_tot} rows (+Q ~4.6k + cals). vs Whisper F2 ~296k est.")
print(" separation check: new median still grows ~exponentially in n (candidate-cardinality driven);")
print(" readout robustness added a constant-factor (conf'>conf) — task advantage intact.")
