#!/usr/bin/env python3
"""Exp142b C1 benchmark re-sim (Ember C4215) — for Elder's grade + re-freeze.

Court ruling (3/3, coordination#919-921): C1 = MIN over known readout-robust single-copy
decoders (best-known-conditional; freezing the expensive fixed-threshold would inflate C1/Q
~3x = the F119 naive-baseline error pointed at our own benchmark).

Elder handed calibrated Wald SPRT boundaries (#921). This RUNS them through Elder's
CALIBRATION-VERIFICATION BAR (measure familywise-FA<1% AND true-accept>99% BEFORE freezing --
the explicit guard against my prior wrong-P bug), measures C1 median copies-to-identify, and
compares against random-basis 'classical-shadows' to confirm the MIN. e=2% is design-time;
A/B re-size from measured q_n at flight.

Decoders (both use the SAME per-copy primitive: prepare rho_P=(I+P)/2^n, measure all n qubits
in an n-Pauli basis A, parity is even-deterministic iff A==P else 50/50; readout flips parity
w.p. p_flip):
  (a) SPRT basis-elimination -- DIRECTED: walk committed basis order, run a Wald SPRT per basis.
  (b) random-basis shadows   -- UNDIRECTED: random basis per copy, eliminate on parity-odd.
"""
import numpy as np, itertools

def p_flip(n, e):
    return (1 - (1 - 2*e)**n) / 2

def parity_even(is_true, p0, rng):
    """One shots=1 fresh-b copy: even w.p. p0 if basis==P (true) else 1/2. p0=1-p_flip."""
    return rng.random() < (p0 if is_true else 0.5)

# ---- Elder's Wald boundaries (#921) --------------------------------------
def wald(n, p0):
    A = n*np.log(3) + np.log(100)      # confirm: familywise-FA < 1% over 3^n  (= log(3^n/0.01))
    B = np.log(0.005)                   # eliminate: true-false-elim < 0.5%
    s_even = np.log(p0/0.5)             # LLR step, parity-even (pass)
    s_odd  = np.log((1-p0)/0.5)         # LLR step, parity-odd  (fail)
    return A, B, s_even, s_odd

def sprt_decode(P, order, n, e, L, rng):
    """Directed SPRT elimination. Returns (identified_basis_or_None, copies_used)."""
    p0 = 1 - p_flip(n, e)
    A, B, s_even, s_odd = wald(n, p0)
    used = 0
    for basis in order:
        is_true = (basis == P)
        llr = 0.0
        while True:
            if used >= L:
                return None, used                     # censored
            used += 1
            llr += s_even if parity_even(is_true, p0, rng) else s_odd
            if llr >= A:
                return basis, used                    # CONFIRM
            if llr <= B:
                break                                  # ELIMINATE -> next basis
    return None, used

def shadows_decode(P, cands, n, e, L, rng):
    """Undirected random-basis: each copy picks a uniform random n-Pauli basis; a parity-odd
    eliminates that basis (SPRT-robust per basis via a small odd-count). Confirm the sole
    survivor after a Wald-confirm run. Reference decoder (expected worse -- no direction)."""
    p0 = 1 - p_flip(n, e)
    A, B, s_even, s_odd = wald(n, p0)
    alive = {c: 0.0 for c in cands}     # per-basis LLR
    used = 0
    while used < L:
        basis = cands[rng.integers(0, len(cands))]
        if basis not in alive:
            continue
        used += 1
        alive[basis] += s_even if parity_even(basis == P, p0, rng) else s_odd
        if alive[basis] >= A:
            return basis, used
        if alive[basis] <= B:
            del alive[basis]
        if not alive:
            return None, used
    return None, used

print("="*76)
print("Exp142b C1 re-sim @ e=2% (design-time; A/B re-size from measured q_n at flight)")
print("Elder Wald: A=n*ln3+ln100, B=ln0.005 ; CALIBRATION BAR: FA<1% AND true-accept>99%")
print("="*76)
summary = {}
for n in [4, 6, 8]:                     # all three flown rungs
    reps = 4000 if n <= 6 else 400      # n=8: 3^8=6561 candidates, fewer reps (still tight)
    e = 0.02
    cands = ["".join(t) for t in itertools.product("XYZ", repeat=n)]
    Lbig = 80 * 3**n                    # generous: measure the true distribution (no censoring)
    rng = np.random.default_rng(4215 + n)
    sprt_stop, sprt_true, sprt_fa, sprt_cens = [], 0, 0, 0
    for _ in range(reps):
        P = "".join(rng.choice(list("XYZ"), n)); order = list(cands); rng.shuffle(order)
        got, used = sprt_decode(P, order, n, e, Lbig, rng)
        if got is None: sprt_cens += 1
        elif got == P: sprt_true += 1; sprt_stop.append(used)
        else: sprt_fa += 1; sprt_stop.append(used)
    ta = sprt_true/reps; fa = sprt_fa/reps
    med = int(np.median(sprt_stop))
    p95 = int(np.percentile(sprt_stop, 95))
    # shadows reference (fewer reps -- slower, only needs an order-of-magnitude compare)
    sh_reps = 600 if n <= 6 else 80
    sh_stop, sh_true = [], 0
    for _ in range(sh_reps):
        P = "".join(rng.choice(list("XYZ"), n))
        got, used = shadows_decode(P, cands, n, e, 200*3**n, rng)
        if got == P: sh_true += 1; sh_stop.append(used)
    sh_med = int(np.median(sh_stop)) if sh_stop else -1
    barA = "PASS" if fa < 0.01 else "FAIL"; barT = "PASS" if ta > 0.99 else "FAIL"
    summary[n] = (med, p95, sh_med, ta, fa)
    print(f"\n n={n}: SPRT  true-accept={ta:.4f} [{barT}]  familywise-FA={fa:.4f} [{barA}]  censored={sprt_cens}")
    print(f"        C1(SPRT) median-copies-to-ID = {med}   p95(L-sizing) = {p95}")
    print(f"        classical-shadows median = {sh_med}  ->  MIN = {'SPRT' if med <= sh_med else 'shadows'} = C1")
print("\n" + "="*76)
print("FREEZE (if both bars PASS): C1 = median(SPRT) = the smaller of {SPRT, shadows};")
print("fixed-threshold (606/10149/125k) = reported UPPER reference only, never the tile number.")
print("n=8: same rule; A/B/median re-sized from measured q_n at flight (enumeration of 3^8 heavy).")
print("="*76)
