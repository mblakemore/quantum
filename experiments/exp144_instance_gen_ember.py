#!/usr/bin/env python3
"""Exp144 instance generator (Ember) — §1 ensemble `dynamics_fullweight_m3`.

Frozen sampling rules, read from the prereg (NOT invented here):
  * rungs n ∈ {4,6,8}; K=5 independent instances per rung; 15 total.
  * m=3 planted terms, each FULL-WEIGHT (alphabet {X,Y,Z} only — NO identity letters;
    this is what restores the exponential single-copy floor, the R2 lesson).
  * mutually COMMUTING.
  * multiplicatively INDEPENDENT: all 2^3 subset products distinct; no subset product
    equals another planted term or the identity.
  * coefficients: one each from the frozen grid {0.15,0.20,0.25}, signs uniform ±.
  * sampled uniformly from full-weight strings subject to the constraints, AT SEAL TIME.

METHOD — symplectic F2 representation. Both constraints are linear algebra, not search:
  letter -> (x,z):  X=(1,0)  Y=(1,1)  Z=(0,1)   (I=(0,0) is excluded by full-weight)
  * commute(P,Q)            <=> symplectic form <P,Q> = x_P·z_Q + z_P·x_Q = 0 (mod 2)
  * multiplicative indep.   <=> the m symplectic vectors are LINEARLY INDEPENDENT over F2.
    Pauli multiplication (ignoring phase) IS XOR of these vectors, so "all 2^m subset
    products distinct" and "no subset product = identity" are the SAME condition as linear
    independence — and a subset product equalling another planted term would make the set
    dependent too. One check covers all three clauses of the prereg sentence.

Sampling is uniform-with-rejection over full-weight strings; the constraints are checked,
never constructed around, so the sample stays uniform on the constrained set.
"""
import random

PAULIS = ("X", "Y", "Z")
SYM = {"X": (1, 0), "Y": (1, 1), "Z": (0, 1)}
GRID = (0.15, 0.20, 0.25)


def to_symplectic(p):
    """Pauli string -> (x_bits, z_bits) as tuples over F2."""
    xs, zs = zip(*(SYM[ch] for ch in p))
    return tuple(xs), tuple(zs)


def commutes(p, q):
    """Symplectic form <P,Q> = x_P·z_Q + z_P·x_Q == 0 (mod 2).

    Equivalently: full-weight strings commute iff they differ on an EVEN number of sites.

    BUG HISTORY (C4194, caught by the known-answer test below, NOT by the ensemble check):
    v1 computed `a*d + c*b` over zip(xp, zp, zq, xq) = x_P·x_Q + z_P·z_Q — the wrong
    bilinear form. It declared XX and XY commuting (they anti-commute). All 15 sampled
    instances "validated" clean because validate_instance() calls THIS function too:
    generator and validator shared the defect and agreed perfectly. Sealing that would have
    committed 15 instances with non-commuting terms, breaking the §1 premise that makes
    V = Π e^{−i c_j t P_j} exact with no Trotter error — silently, behind valid hashes,
    discoverable only at decode. A validator that reuses the primitive it validates is not
    a check; only ground truth is.
    """
    xp, zp = to_symplectic(p)
    xq, zq = to_symplectic(q)
    s = sum(a * c + b * d for a, b, c, d in zip(xp, zp, zq, xq)) % 2
    return s == 0


def commutes_by_sitecount(p, q):
    """INDEPENDENT oracle: full-weight Paulis commute iff they differ on an even number
    of sites. Deliberately shares NO code with commutes() — different derivation, so a
    bug in the symplectic form cannot hide in both."""
    return sum(1 for a, b in zip(p, q) if a != b) % 2 == 0


def independent(terms):
    """Linear independence of the symplectic vectors over F2 (Gaussian elimination)."""
    rows = []
    for p in terms:
        x, z = to_symplectic(p)
        rows.append(list(x) + list(z))
    rank, ncols = 0, len(rows[0])
    for col in range(ncols):
        piv = next((r for r in range(rank, len(rows)) if rows[r][col]), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for r in range(len(rows)):
            if r != rank and rows[r][col]:
                rows[r] = [a ^ b for a, b in zip(rows[r], rows[rank])]
        rank += 1
    return rank == len(terms)


def sample_instance(n, rng, m=3, max_tries=200000):
    """Uniform rejection sampling over full-weight strings subject to §1 constraints."""
    for _ in range(max_tries):
        terms = ["".join(rng.choice(PAULIS) for _ in range(n)) for _ in range(m)]
        if len(set(terms)) != m:
            continue
        if not all(commutes(terms[i], terms[j])
                   for i in range(m) for j in range(i + 1, m)):
            continue
        if not independent(terms):
            continue
        coeffs = list(GRID)
        rng.shuffle(coeffs)
        coeffs = [c * rng.choice((1, -1)) for c in coeffs]
        return terms, coeffs
    raise RuntimeError(f"no valid instance for n={n} in {max_tries} tries")


def validate_instance(n, terms, coeffs, m=3):
    """Independent re-check of every §1 clause. Used as an assertion at seal time —
    the generator and the validator must agree, or the instance does not get sealed."""
    errs = []
    if len(terms) != m or len(coeffs) != m:
        errs.append(f"m mismatch: {len(terms)}/{len(coeffs)} vs {m}")
    for t in terms:
        if len(t) != n:
            errs.append(f"{t}: length {len(t)} != n={n}")
        if any(ch not in PAULIS for ch in t):
            errs.append(f"{t}: NOT full-weight (identity letter or bad alphabet)")
    if len(set(terms)) != len(terms):
        errs.append(f"duplicate terms: {terms}")
    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            if not commutes(terms[i], terms[j]):
                errs.append(f"{terms[i]} and {terms[j]} do NOT commute")
    if len(terms) == len(set(terms)) and not independent(terms):
        errs.append(f"terms multiplicatively DEPENDENT: {terms}")
    if sorted(abs(c) for c in coeffs) != sorted(GRID):
        errs.append(f"coeffs {coeffs} are not one-each from grid {GRID}")
    return errs


if __name__ == "__main__":
    rng = random.Random(144)
    print("=== §1 instance generator selftest (dynamics_fullweight_m3) ===")
    fails = 0

    def check(label, cond, detail=""):
        global fails
        if not cond:
            fails += 1
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")

    # Known-answer checks of the primitives, so a bug in commutes/independent cannot
    # silently pass the whole ensemble.
    # Cross-oracle: symplectic form vs site-count parity, two independent derivations.
    # Exhaustive over all full-weight pairs at n=1..3 — this is what would have caught v1
    # instantly instead of after 15 "valid" instances.
    import itertools as _it
    disagree = []
    for nn in (1, 2, 3):
        for a in _it.product(PAULIS, repeat=nn):
            for b in _it.product(PAULIS, repeat=nn):
                A, B = "".join(a), "".join(b)
                if commutes(A, B) != commutes_by_sitecount(A, B):
                    disagree.append((A, B))
    check(f"cross-oracle: symplectic == site-count parity on ALL full-weight pairs n<=3",
          not disagree, f"{len(disagree)} disagreements e.g. {disagree[:3]}")

    check("commutes: XX,YY (differ on 2 sites = even)", commutes("XX", "YY"))
    check("commutes: XX,XY (differ on 1 site = odd) -> NOT", not commutes("XX", "XY"))
    check("commutes: XXXX,YYXX (differ on 2)", commutes("XXXX", "YYXX"))
    check("independent: X,Y,Z on 1 qubit -> XYZ dependent (Z=X*Y)",
          not independent(["X", "Y", "Z"]))
    check("independent: XX,YY,ZZ -> dependent (ZZ = XX*YY)",
          not independent(["XX", "YY", "ZZ"]))

    # Generate the real shape: 3 rungs x 5 instances, validate every clause.
    for n in (4, 6, 8):
        for k in range(1, 6):
            terms, coeffs = sample_instance(n, rng)
            errs = validate_instance(n, terms, coeffs)
            check(f"n={n} k={k} valid ({','.join(terms)})", not errs, "; ".join(errs))

    # Uniformity smoke: the constrained set should not collapse to a handful of instances.
    seen = set()
    for _ in range(300):
        t, _ = sample_instance(6, rng)
        seen.add(tuple(sorted(t)))
    check("n=6 sampling diverse (>100 distinct supports in 300 draws)", len(seen) > 100,
          f"{len(seen)} distinct")

    print(f"\nINSTANCE GEN SELFTEST: {'PASS' if fails == 0 else f'FAIL ({fails})'}")
    raise SystemExit(1 if fails else 0)
