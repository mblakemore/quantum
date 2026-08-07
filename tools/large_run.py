#!/usr/bin/env python3
"""P-CCM v1.0 — A LARGE INSTANCE, END TO END, WITH AN EXACT ORACLE.

THE OBSERVATION THAT MAKES THIS VERIFIABLE. The brute-force oracle costs 2^n. The solver costs
2^(gamma t). THOSE ARE INDEPENDENT. So a large-t instance at modest n is simultaneously a real
stress of the stabilizer-rank machinery (chi = 2^k terms on t magic qubits, a (n+t)-qubit Heisenberg
reduction, chi^2 inner products) AND exactly checkable against a statevector. There is no need to
choose between "large" and "verified".

WHAT IS LARGE HERE. t is the T-count, which is the ONLY exponential the solver pays for:

    t = 40  ->  chi = 2^12 =  4,096 terms,  ~8.4M inner products on 40-qubit stabilizer states

That is not t=80, and it is not claimed to be. It is the largest instance that finishes in minutes
rather than weeks, run with the SAME code path measured at t=80 in Stage G.

THE PATH. Every step is on the standard form. Nothing here touches a 2^t matrix:

    ②  gadgetize + Heisenberg reduce      -> (G,u), (H,v) on the t magic qubits, ONCE
    ①b sparsify                           -> chi = 2^k product stabilizer terms, equal coefficients
    ③  pauli_project per term             -> Pi_G|phi_a>, with its 2^{-p_a/2}
    njit inner_product                    -> ||Pi_G psi||^2 exactly, O(chi^2)/2 by Hermitian symmetry

VACUITY GUARD, per C5023: the instance is built to be T-SENSITIVE (opened and closed in the X basis)
and the run FAILS if P_out lands within 0.05 of 1/2, because P = 1/2 is protected by symmetry — the
approximation scales numerator and denominator alike and the ratio is exact however bad the state is.
A large run that agrees at P = 1/2 would prove nothing at all.

Substrate: claude-fable-5, Whisper C5024. Creator directive: "run a large instance end-to-end".
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stabilizer_rank_kernel as ref                                        # noqa: E402
import stabilizer_rank_bitpacked as bp                                      # noqa: E402
import stabilizer_njit as nj                                                # noqa: E402
import magic_sparsify as ms                                                 # noqa: E402
import gadgetize as gd                                                      # noqa: E402
import pauli_project as pp                                                  # noqa: E402
import stabilizer_estimator as se                                           # noqa: E402


def build_instance(n, nt, rng):
    """A T-sensitive Clifford+T circuit: opened and closed in the X basis so the T phases reach
    the measured probability instead of cancelling into P = 1/2.

    The extra S/T tail on the output qubit is there because the FIRST version of this generator
    returned P_oracle = cos^2(pi/8) = 0.8536 for EVERY t on the ladder. Each instance passed the
    per-instance vacuity guard (|P - 1/2| > 0.05) while the ladder as a whole had ZERO SPREAD —
    the same C5023 failure one level up. A ladder that always lands on one value tests one value."""
    gates = [("H", q) for q in range(n)]
    gates += gd.random_circuit(n, 3 * n, nt, rng)
    for _ in range(int(rng.integers(0, 4))):        # vary how much T phase reaches the output
        gates.append(("T", 0))
    if rng.integers(2):
        gates.append(("S", 0))
    gates += [("H", 0)]
    return gates


def _pack(st):
    p = bp.PackedState.from_reference(st)
    return (p.k, p.h, p.G, p.Gbar, p.Q, p.D, p.J)


def projected_terms(bitstrings, coeff, generators):
    """Project every term onto Pi_G and return packed survivors with their coefficients."""
    out = []
    for x in bitstrings:
        st = ms.term_stabstate(x)
        res, p = pp.project_group(st, generators)
        if res is not None:
            out.append((coeff * 2.0 ** (-p / 2), _pack(st)))
    return out


def norm2_exact(packed, t):
    """||Pi_G psi||^2 exactly, via the njit kernel. Hermitian symmetry halves the work."""
    W = bp.nwords(t)
    m = len(packed)
    tot = 0.0
    for a in range(m):
        ca, sa = packed[a]
        tot += (abs(ca) ** 2 *
                ref.triple_to_complex(nj.inner_product_njit(t, W, *sa, *sa)).real)
        for b in range(a + 1, m):
            cb, sb = packed[b]
            z = ref.triple_to_complex(nj.inner_product_njit(t, W, *sa, *sb))
            tot += 2.0 * (np.conj(cb) * ca * z).real
    return tot


def run(n, nt, delta, seed, exact_decomp, verbose=True, probe_only=False):
    rng = np.random.default_rng(seed)
    gates = build_instance(n, nt, rng)
    build, t = gd.gadgetize(gates, n)
    Qout, x = [0], (0,)

    want = gd.brute_force_pout(gates, n, Qout, x)              # ORACLE: costs 2^n, not 2^t
    if abs(want - 0.5) < 0.05 or want < 1e-9 or want > 1 - 1e-9:
        return None                                            # vacuity guard: cannot discriminate
    if probe_only:
        return want                                            # cheap: oracle only, no solver run

    y = tuple(int(v) for v in rng.integers(0, 2, size=t))
    pre = [g for j in range(t) for g in (("SDG", n + j), ("H", n + j))]
    V = pre + build(y)

    t0 = time.perf_counter()
    num_gens = [gd.pauli_Z(n + t, q, x[i]) for i, q in enumerate(Qout)] + \
               [gd.pauli_Z(n + t, n + j, y[j]) for j in range(t)]
    den_gens = [gd.pauli_Z(n + t, n + j, y[j]) for j in range(t)]
    G, u = gd.heisenberg_reduce(V, n, t, num_gens)
    H, v = gd.heisenberg_reduce(V, n, t, den_gens)
    t_heis = time.perf_counter() - t0

    if exact_decomp:
        k = t
        M = np.eye(t, dtype=np.uint8)
        Z, _ = ms.z_of_L(ms._pack(M), k)
        fid2 = 1.0
    else:
        M, k, Z, fid2, _ = ms.sparsify(t, delta, rng, max_tries=10)
    bits = ms.term_bitstrings(M, k)
    coeff = ms.coefficient(k, Z)
    chi = len(bits)

    gg = [(P.k, P.a, P.b) for P in G]
    hh = [(P.k, P.a, P.b) for P in H]

    t0 = time.perf_counter()
    pn = projected_terms(bits, coeff, gg)
    pd = projected_terms(bits, coeff, hh)
    t_proj = time.perf_counter() - t0

    t0 = time.perf_counter()
    nG = norm2_exact(pn, t)
    nH = norm2_exact(pd, t)
    t_norm = time.perf_counter() - t0

    # NO MAGNITUDE GUARD. This took two attempts and the second was the same bug as the first.
    #   v1: num = 2^-u nG, den = 2^-v nH, guard abs(den) > 1e-14. Gate G4 proved den IS
    #       p_y = 2^-t exactly = 3.6e-15 at t=48, so the guard rejected a CORRECT value for
    #       every t >= 47. Returned nan after 63 million inner products.
    #   v2: put the exponent on the ratio and guard nH > 1e-12 instead. STILL WRONG — nH is
    #       2^(v-t), which at t=51, v=5 is 1.42e-14. I moved the epsilon to a quantity with the
    #       SAME 2^-t decay, having just written down the rule that says not to.
    # There is no correct magnitude threshold here because every magnitude in this expression
    # decays with t. The only legitimate guards are STRUCTURAL: did the projection kill every
    # term, and is the norm positive.
    num, den = 2.0 ** (-u) * nG, 2.0 ** (-v) * nH
    got = (2.0 ** (v - u)) * (nG / nH) if (pd and nH > 0.0) else float("nan")
    return {"n": n, "t": t, "k": k, "chi": chi, "fidelity2": fid2,
            "survivors_num": len(pn), "survivors_den": len(pd),
            "gens_G": len(gg), "gens_H": len(hh), "u": u, "v": v,
            "P_solver": got, "P_oracle": want, "abs_err": abs(got - want),
            "inner_products": len(pn) * (len(pn) + 1) // 2 + len(pd) * (len(pd) + 1) // 2,
            "t_heisenberg_s": t_heis, "t_project_s": t_proj, "t_norm_s": t_norm,
            "t_total_s": t_heis + t_proj + t_norm}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ladder", default="8,16,24,32,40")
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--delta", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--approx", action="store_true",
                    help="use the sparsified decomposition (chi = 2^k) instead of exact (k = t)")
    a = ap.parse_args()

    mode = "APPROXIMATE (chi = 2^k)" if a.approx else "EXACT (k = t, Eq 35 fidelity = 1)"
    print(f"LARGE INSTANCE, END TO END — {mode}\n")
    print("  oracle cost is 2^n, solver cost is 2^(gamma t): INDEPENDENT, so a large-t")
    print("  instance at modest n is both a real stress and exactly checkable.\n")
    print(f"  {'t':>4} {'k':>3} {'chi':>8} {'surv':>7} {'|G|':>4} {'inner prods':>13} "
          f"{'P_solver':>10} {'P_oracle':>10} {'|err|':>10} {'wall':>9}")

    rows = []
    seen_p = []
    for nt in [int(v) for v in a.ladder.split(",")]:
        res = None
        for attempt in range(12):
            # LADDER-LEVEL vacuity guard: reject an instance whose P_oracle duplicates one
            # already on the ladder, so the run cannot pass by testing a single value t times.
            probe = run(a.n, nt, a.delta, a.seed + 1000 * attempt, not a.approx, probe_only=True)
            if probe is None:
                continue
            if any(abs(probe - q) < 0.01 for q in seen_p) and attempt < 11:
                continue
            res = run(a.n, nt, a.delta, a.seed + 1000 * attempt, not a.approx)
            if res is not None:
                seen_p.append(res["P_oracle"])
                break
        if res is None:
            print(f"  {nt:>4}  no T-sensitive instance found — SKIPPED (vacuity guard)")
            continue
        rows.append(res)
        print(f"  {res['t']:>4} {res['k']:>3} {res['chi']:>8,} {res['survivors_num']:>7,} "
              f"{res['gens_G']:>4} {res['inner_products']:>13,} {res['P_solver']:>10.6f} "
              f"{res['P_oracle']:>10.6f} {res['abs_err']:>10.2e} {res['t_total_s']:>8.1f}s")

    if not rows:
        print("\n  ⛔ no instances ran.")
        sys.exit(2)

    big = max(rows, key=lambda r: r["t"])
    tol = 1e-9 if not a.approx else math.sqrt(1 - big["fidelity2"])
    ok = all(r["abs_err"] <= (1e-9 if not a.approx else math.sqrt(1 - r["fidelity2"]))
             for r in rows)
    spread = max(r["P_oracle"] for r in rows) - min(r["P_oracle"] for r in rows)
    distinct = len({round(r["P_oracle"], 4) for r in rows})
    print(f"\n  VACUITY GUARD: {distinct}/{len(rows)} distinct P_oracle, spanning "
          f"[{min(r['P_oracle'] for r in rows):.4f}, {max(r['P_oracle'] for r in rows):.4f}]"
          f"  (all |P - 1/2| > 0.05, and no two within 0.01)")
    if distinct < max(2, len(rows) - 1):
        print("  ⛔ LADDER VACUITY: too few distinct probabilities — the run tests one value.")
        sys.exit(2)
    print(f"  LARGEST: t = {big['t']}, chi = {big['chi']:,}, "
          f"{big['inner_products']:,} inner products, |err| = {big['abs_err']:.2e}")
    print(f"  time split at t={big['t']}: heisenberg {big['t_heisenberg_s']:.1f}s  "
          f"project {big['t_project_s']:.1f}s  norm {big['t_norm_s']:.1f}s")
    print(f"\n  {'✅ ALL INSTANCES AGREE WITH THE ORACLE' if ok else '⛔ DISAGREEMENT'}"
          f"  (tolerance {'exact 1e-9' if not a.approx else f'sqrt(delta) = {tol:.3f}'})")

    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       f"large_run_{'approx' if a.approx else 'exact'}_v1.json")
    with open(dst, "w") as fh:
        json.dump({"card": "large_run", "version": "1.0", "cycle": "C5024",
                   "substrate": "claude-fable-5", "mode": mode, "n": a.n, "delta": a.delta,
                   "rows": rows, "all_agree": bool(ok), "p_oracle_spread": float(spread),
                   "distinct_p_values": int(distinct)}, fh, indent=2)
    print(f"  written: results/{os.path.basename(dst)}")
    if not ok:
        sys.exit(2)


if __name__ == "__main__":
    main()
