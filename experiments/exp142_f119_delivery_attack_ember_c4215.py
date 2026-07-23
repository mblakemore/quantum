#!/usr/bin/env python3
"""F119 audit — the DELIVERY attack (Ember C4215, advisor-flagged hole).

The honest oracle (fresh sign b per copy) makes rho_P=(I+P)/2^n hard single-copy
(f119_audit.py: per-qubit scan gets zero signal). BUT the flight kit's conventional
arm delivered 12 shots per FIXED-b row (WAVE1_SHOTS=12): within a row the state is a
PURE eigenstate (x)|P_i,b_i>, and qubits with A[i]=P[i] are deterministic across the
12 shots. That leaks P per-qubit — the F121 pattern (idealized-hard, delivered-easy).

This RUNS the determinism decoder on a FAITHFUL simulation of the delivered rows
(12 shots, fixed even-parity b per row, incl. realistic readout noise) and compares
copies-to-identify vs the executed naive meter (~2*3^n).
"""
import numpy as np
rng = np.random.default_rng(88)

def deliver_row(P, A, readout_err, rng):
    """Faithful model of ONE flown conventional PUB row: fixed even-parity b, 12 shots,
    measure all qubits in basis A. Returns 12 x n array of +-1 outcomes."""
    n = len(P)
    b = rng.integers(0, 2, size=n)
    if b.sum() % 2:
        b[rng.integers(0, n)] ^= 1
    shots = np.zeros((12, n), dtype=int)
    for s in range(12):
        for i in range(n):
            if A[i] == P[i]:
                o = (-1) ** b[i]              # deterministic (fixed b within row)
            else:
                o = rng.choice([1, -1])       # conjugate basis: 50/50
            if rng.random() < readout_err:    # realistic readout flip
                o = -o
            shots[s, i] = o
    return shots

def determinism_decode(P, readout_err, rng):
    """Best delivery-aware decoder: use the all-X, all-Y, all-Z rows (present in the
    flown 3^n wave-1 set). A qubit that is (near-)deterministic in basis A has P_i=A.
    Cost = 3 rows * 12 shots = 36 copies, INDEPENDENT of n."""
    n = len(P)
    variance = {}
    for A in "XYZ":
        shots = deliver_row(P, A * n, readout_err, rng)
        # per-qubit fraction of majority outcome (1.0 = deterministic)
        frac = np.array([max((shots[:, i] == 1).mean(), (shots[:, i] == -1).mean())
                         for i in range(n)])
        variance[A] = frac
    guess = []
    for i in range(n):
        best_A = max("XYZ", key=lambda A: variance[A][i])
        guess.append(best_A)
    guess = "".join(guess)
    correct = sum(1 for i in range(n) if guess[i] == P[i])
    return guess, correct, 3 * 12

print("=" * 74)
print("DELIVERY ATTACK — determinism decoder on faithfully-simulated flown rows")
print("readout_err models real hardware; 12 shots/row as flown (WAVE1_SHOTS=12)")
print("=" * 74)
for n, P in [(4, "XXXX"), (6, "YYXYZY"), (8, "ZYYXXYZZ"), (10, "YYXZXXXYZZ")]:
    for ro in (0.0, 0.02, 0.05):
        accs, costs = [], []
        for _ in range(200):
            g, c, cost = determinism_decode(P, ro, rng)
            accs.append(c == n); costs.append(cost)
        naive = 2 * 3 ** n
        print(f" n={n:2d} P={P:10s} readout={ro:.2f}: exact-P recovered "
              f"{np.mean(accs)*100:5.1f}% of runs in {int(np.mean(costs))} copies  "
              f"| naive meter ~2*3^n = {naive:,}  => speedup ~{naive/np.mean(costs):,.0f}x")

print("\n" + "=" * 74)
print("If exact-P recovery is high at ~36 copies << 2*3^n, the DELIVERED conventional")
print("witness is crackable in O(1) copies regardless of n. The executed exponential")
print("meter measured a NAIVE decoder on exploitable batched-b data (F121 pattern).")
print("NOTE: this attack needs the raw per-row 12-shot outcomes, which are NOT committed")
print("to git (only decoded answers are) -> a PUBLIC attacker cannot run it; but the")
print("copy-ACCOUNTING (best single-copy method on the delivered oracle) is compromised.")
print("=" * 74)
