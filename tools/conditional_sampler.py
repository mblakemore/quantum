#!/usr/bin/env python3
"""COMPONENT ⑤ — the conditional bit-by-bit sampler. Eq 29.

WHAT THIS CHANGES ABOUT THE SOLVER. Until now the solver is a SCORER: hand it an outcome x and it
returns P^y_out(x). This makes it a SIMULATOR: it DRAWS x ~ P^y_out with no outcome supplied. That
is a different capability, not a faster one, and it is the difference between serving a RUNTIME
claim and serving a SAMPLING claim.

WHY THAT DISTINCTION IS WORTH THE BUILD (C5027). The runtime genre is in poor shape: F121 was
retired by our own red-team, and today's bent-family sweep found the door to a replacement
structurally obstructed — the Kasami dual leaves the monomial class at n=10, 12 and 14 with the
Gamma-rank gap widening 2 -> 12 -> 362, and the one place in the whole sweep where the dual comes
free is the degree-2 (Maiorana-McFarland) case, which is exactly what leaks classically. A sampling
claim does not need a bent family with a cheap dual at all. ⑤ opens a different door than the one
that just closed.

THE ALGORITHM, and why it is mostly plumbing over already-gated code. To draw
x = (x_0 ... x_{m-1}) over the output qubits Qout, take the bits one at a time:

    P(x_j = 0 | x_0 ... x_{j-1})  =  P(x_0 ... x_{j-1}, 0) / P(x_0 ... x_{j-1})

and the KEY OBSERVATION is that a MARGINAL over a PREFIX is the same Eq 28 object with FEWER
PROJECTORS — project the first j output qubits and simply do not project the rest:

    P(x_0 ... x_{j-1})  =  2^-u ||Pi_G psi||^2 / 2^-v ||Pi_H psi||^2,
        G = < Z-projectors on Qout[:j] at x_0..x_{j-1} >  +  < the y-projectors >

So every conditional is a ratio of two quantities component ③ already evaluates on the standard
form. No new numerical machinery, and no 2^t matrices. The denominator 2^-v||Pi_H psi||^2 depends
only on y, so it cancels out of every conditional and is never even computed here.

COST. m+1 marginals per sample, each O(chi^2) exactly (or O(chi.L.J) through ④). Deliberately NOT
memoised across draws: a prefix cache is bounded by the number of distinct prefixes, which is
exponential in m, and would turn an O(m)-per-sample algorithm into an exponential-memory one. The
gates below draw few enough samples that the honest path is affordable.

THE GATES, and the discipline they inherit. Component ④'s first gate REPORTED max |err| = 0.0000
OVER 96 CASES WHILE TESTING NOTHING, because P = 1/2 is protected by symmetry — the approximation
scales numerator and denominator alike so the ratio is exact however bad the state is. A sampler
has the same failure shape one level up: a UNIFORM target distribution is reproduced by a BROKEN
sampler that ignores the circuit entirely. So:

    T0  chain rule is EXACT: prod_j P(x_j | prefix) == P^y_out(x) for EVERY x, against brute force.
        Deterministic — no sampling noise anywhere in it. This is the real correctness gate.
    T1  siblings sum to their parent: P(pre,0) + P(pre,1) == P(pre). An algebraic identity that a
        wrong marginal breaks immediately.
    T2  normalisation: sum_x P^y_out(x) == 1.
    T3  VACUITY GUARD — the target must be measurably NON-UNIFORM, or T4 tests nothing.
    T4  empirical: the drawn distribution matches, judged against a CALIBRATED NULL rather than a
        hand-picked threshold. The null is built by drawing the same number of samples directly
        from the exact distribution many times and taking the 99th percentile of the resulting
        total-variation distances. A threshold I invent is a threshold I can tune; a null I
        simulate is not.

Substrate: claude-opus-5, Whisper C5027.
"""
import itertools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gadgetize as gd                                                        # noqa: E402
import solver as sv                                                           # noqa: E402


def prepare(gates, n, y):
    """Hoist the parts that do not vary with the prefix: gadgetization and the frame circuit."""
    build, t = gd.gadgetize(gates, n)
    pre = [g for j in range(t) for g in (("SDG", n + j), ("H", n + j))]
    return pre + build(y), t


def marginal(V, n, t, Qout, xpre, y, bitstrings, coeff):
    """2^-u ||Pi_G psi||^2 with G projecting ONLY the first len(xpre) output qubits.

    Not dividing by the y-denominator: it is independent of the prefix and cancels from every
    conditional, so computing it would be pure waste."""
    gens = [gd.pauli_Z(n + t, q, xpre[i]) for i, q in enumerate(Qout[:len(xpre)])] + \
           [gd.pauli_Z(n + t, n + j, y[j]) for j in range(t)]
    G, u = gd.heisenberg_reduce(V, n, t, gens)
    return 2.0 ** (-u) * sv.projected_norm2(bitstrings, coeff, [sv._to_gen(P) for P in G])


def sample_pout(gates, n, Qout, y, bitstrings, coeff, rng, trace=False):
    """Draw one x ~ P^y_out by Eq 29, one bit at a time. Returns (x, conditionals if trace)."""
    V, t = prepare(gates, n, y)
    parent = marginal(V, n, t, Qout, (), y, bitstrings, coeff)
    x, conds = [], []
    for _ in range(len(Qout)):
        if parent <= 1e-14:                       # unreachable prefix: nothing left to condition on
            x.append(0)
            conds.append(float("nan"))
            continue
        n0 = marginal(V, n, t, Qout, tuple(x + [0]), y, bitstrings, coeff)
        p0 = min(1.0, max(0.0, n0 / parent))
        conds.append(p0)
        if rng.random() < p0:
            x.append(0)
            parent = n0
        else:
            x.append(1)
            parent = parent - n0                  # sibling by complement — T1 gates this identity
    return (tuple(x), conds) if trace else tuple(x)


def chain_rule_prob(gates, n, Qout, xtarget, y, bitstrings, coeff):
    """prod_j P(x_j | prefix) for a GIVEN x — the sampler's own arithmetic, no randomness."""
    V, t = prepare(gates, n, y)
    parent = marginal(V, n, t, Qout, (), y, bitstrings, coeff)
    p = 1.0
    for j in range(len(Qout)):
        if parent <= 1e-14:
            return 0.0
        n0 = marginal(V, n, t, Qout, tuple(list(xtarget[:j]) + [0]), y, bitstrings, coeff)
        pj = n0 / parent if xtarget[j] == 0 else (parent - n0) / parent
        p *= pj
        parent = n0 if xtarget[j] == 0 else parent - n0
    return p


# ─────────────────────────────────────────────────────────────────────────────
# GATES
# ─────────────────────────────────────────────────────────────────────────────
def conditional_profile(exact, m):
    """Every conditional P(x_j = 0 | prefix) implied by a joint, level by level.

    THE QUANTITY THE VACUITY GUARD HAS TO WATCH. The first version of _find_case screened on the
    JOINT being non-uniform, which a distribution can satisfy while every conditional after the
    first is exactly 1/2 — and then the chain rule is only ever tested on its first bit. Caught by
    MUTATION TESTING: two of three deliberate breakages went undetected, on a case whose joint
    passed the old guard at max|p - 1/4| = 0.177 while P(x1=0|x0) was 0.500 under BOTH prefixes.
    That is component ④'s symmetry-protected-vacuity failure exactly, one level up, in the gate
    whose own docstring quotes it. Screening the joint is screening the wrong object."""
    prof = []
    for j in range(m):
        level = []
        for pre in itertools.product([0, 1], repeat=j):
            lo = hi = 0.0
            for i, o in enumerate(itertools.product([0, 1], repeat=m)):
                if o[:j] != pre:
                    continue
                if o[j] == 0:
                    lo += exact[i]
                hi += exact[i]
            if hi > 1e-12:
                level.append(lo / hi)
        prof.append(level)
    return prof


def _find_case(rng, m, want_spread):
    """A circuit whose CONDITIONALS are non-degenerate — not merely whose joint is non-uniform.

    Two requirements, both necessary, neither sufficient alone:
      (a) some conditional at every level j is far from 1/2   -> the bit is informative at all
      (b) at every level j >= 1 the conditional VARIES across prefixes -> it actually depends on
          the prefix, which is the thing the chain rule claims and the thing M3 broke
    """
    for _ in range(4000):
        n = m
        gates = [("H", q) for q in range(n)]
        gates += gd.random_circuit(n, int(rng.integers(2, 7)), int(rng.integers(2, 4)), rng)
        gates += [("H", 0), ("H", m - 1)]
        _, t = gd.gadgetize(gates, n)
        if t > 5:
            continue
        Qout = list(range(m))
        exact = np.array([gd.brute_force_pout(gates, n, Qout, xx)
                          for xx in itertools.product([0, 1], repeat=m)])
        if exact.sum() < 1e-9:
            continue
        exact = exact / exact.sum()
        prof = conditional_profile(exact, m)
        if any(not lv for lv in prof):
            continue
        informative = all(max(abs(c - 0.5) for c in lv) >= want_spread for lv in prof)
        prefix_dep = all((max(lv) - min(lv)) >= want_spread for lv in prof[1:])
        if informative and prefix_dep:
            return gates, n, t, Qout, exact, prof
    return None


def self_test(verbose=True):
    rng = np.random.default_rng(50275)
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<48} {detail}")

    m = 2
    case = _find_case(rng, m, 0.08)
    if case is None:
        print("    FAIL  no case with non-degenerate CONDITIONALS found — gates would be vacuous")
        return 0, 1
    gates, n, t, Qout, exact, prof = case
    bs, co, _, _ = sv.magic_terms(t, 0.5, rng, exact=True)
    y = tuple(int(v) for v in rng.integers(0, 2, size=t))
    outs = list(itertools.product([0, 1], repeat=m))

    print(f"  case: n={n} qubits, t={t} magic states, m={m} output bits, exact mode\n")

    print("  T0 — CHAIN RULE IS EXACT (deterministic; the real correctness gate)")
    worst0 = 0.0
    for xx in outs:
        got = chain_rule_prob(gates, n, Qout, xx, y, bs, co)
        want = gd.brute_force_pout(gates, n, Qout, xx)
        worst0 = max(worst0, abs(got - want))
    rec("T0 prod_j P(x_j|prefix) == P_out(x), all x", worst0 < 1e-9,
        f"{len(outs)} outcomes, max |err| = {worst0:.2e}")

    print("\n  T1 — SIBLINGS SUM TO PARENT (the identity sample_pout uses by complement)")
    V, tt = prepare(gates, n, y)
    worst1 = 0.0
    for j in range(m):
        for pre in itertools.product([0, 1], repeat=j):
            par = marginal(V, n, tt, Qout, pre, y, bs, co)
            c0 = marginal(V, n, tt, Qout, pre + (0,), y, bs, co)
            c1 = marginal(V, n, tt, Qout, pre + (1,), y, bs, co)
            worst1 = max(worst1, abs(c0 + c1 - par))
    rec("T1 P(pre,0) + P(pre,1) == P(pre)", worst1 < 1e-9, f"max |err| = {worst1:.2e}")

    print("\n  T2 — NORMALISATION")
    tot = sum(chain_rule_prob(gates, n, Qout, xx, y, bs, co) for xx in outs)
    rec("T2 sum_x P^y_out(x) == 1", abs(tot - 1.0) < 1e-9, f"sum = {tot:.12f}")

    print("\n  T3 — VACUITY GUARD on the CONDITIONALS (the joint being non-uniform is NOT enough:")
    print("       a joint at max|p-1/4| = 0.177 passed the old guard while every second-bit")
    print("       conditional was exactly 0.500, and two of three mutations then went undetected)")
    informative = all(max(abs(c - 0.5) for c in lv) >= 0.08 for lv in prof)
    prefix_dep = all((max(lv) - min(lv)) >= 0.08 for lv in prof[1:])
    rec("T3a every level has a conditional far from 1/2", informative,
        " | ".join(f"lvl{j}: {[round(float(c), 3) for c in lv]}" for j, lv in enumerate(prof)))
    rec("T3b conditionals VARY across prefixes", prefix_dep,
        " | ".join(f"lvl{j}: spread {max(lv) - min(lv):.3f}" for j, lv in enumerate(prof) if j))

    print("\n  T4 — EMPIRICAL DRAWS vs a CALIBRATED NULL (not a threshold I picked)")
    N = 400
    draws = [sample_pout(gates, n, Qout, y, bs, co, rng) for _ in range(N)]
    idx = {o: i for i, o in enumerate(outs)}
    emp = np.zeros(len(outs))
    for d in draws:
        emp[idx[d]] += 1
    emp /= N
    tv = 0.5 * float(np.abs(emp - exact).sum())
    null = []
    for _ in range(600):
        s = rng.choice(len(outs), size=N, p=exact)
        h = np.bincount(s, minlength=len(outs)) / N
        null.append(0.5 * float(np.abs(h - exact).sum()))
    thr = float(np.percentile(null, 99))
    rec("T4 TV within the 99th pct of the null", tv <= thr,
        f"TV = {tv:.4f} vs null p99 = {thr:.4f} (N={N})")

    print("\n  T5 — MUTATION CONTROLS: break the sampler on purpose; the gates MUST fail.")
    print("       This is not decoration. The FIRST version of T0-T4 passed 5/5 and then MISSED")
    print("       two of these three mutations. Only firing them exposed that T0 was vacuous.")
    print("       A gate suite that has never been shown to fail is an untested instrument.")

    # M1 — a sampler that ignores the circuit entirely. T4 must catch it.
    empb = np.zeros(len(outs))
    for _ in range(N):
        empb[idx[tuple(int(rng.random() < 0.5) for _ in range(m))]] += 1
    tvb = 0.5 * float(np.abs(empb / N - exact).sum())
    rec("T5a uniform-coin sampler is CAUGHT by T4", tvb > thr,
        f"TV = {tvb:.4f} > null p99 = {thr:.4f}")

    # M2 — marginals that drop the y-projectors. T0 must catch it.
    def bad_marginal(V_, n_, t_, Q_, xpre, y_, bstr, c):
        gens = [gd.pauli_Z(n_ + t_, q, xpre[i]) for i, q in enumerate(Q_[:len(xpre)])]
        G_, u_ = gd.heisenberg_reduce(V_, n_, t_, gens)
        return 2.0 ** (-u_) * sv.projected_norm2(bstr, c, [sv._to_gen(P) for P in G_])

    real_marginal = globals()["marginal"]
    globals()["marginal"] = bad_marginal
    try:
        w2 = max(abs(chain_rule_prob(gates, n, Qout, xx, y, bs, co)
                     - gd.brute_force_pout(gates, n, Qout, xx)) for xx in outs)
    except Exception:
        w2 = float("inf")
    finally:
        globals()["marginal"] = real_marginal
    rec("T5b dropped y-projectors are CAUGHT by T0", w2 > 1e-9, f"max |err| = {w2:.3e}")

    # M3 — a chain rule that never takes the 1-branch. T0 must catch it.
    def bad_chain(xt):
        V_, t_ = prepare(gates, n, y)
        par = marginal(V_, n, t_, Qout, (), y, bs, co)
        p = 1.0
        for j in range(len(Qout)):
            if par <= 1e-14:
                return 0.0
            z = marginal(V_, n, t_, Qout, tuple(list(xt[:j]) + [0]), y, bs, co)
            p *= z / par
            par = z
        return p
    w3 = max(abs(bad_chain(xx) - gd.brute_force_pout(gates, n, Qout, xx)) for xx in outs)
    rec("T5c ignoring the 1-branch is CAUGHT by T0", w3 > 1e-9, f"max |err| = {w3:.3e}")

    return npass, nfail


if __name__ == "__main__":
    print("COMPONENT ⑤ — CONDITIONAL BIT-BY-BIT SAMPLER (Eq 29)\n")
    print("  turns the solver from a SCORER (given x, return P(x))")
    print("  into a SIMULATOR (draw x ~ P^y_out)\n")
    p, f = self_test()
    print(f"\n  {p} passed, {f} failed")
    if f == 0:
        print("  ✅ GATES PASSED — the solver can now SAMPLE, not only score.")
    else:
        print("  ⛔ GATES NOT PASSED.")
        sys.exit(2)
