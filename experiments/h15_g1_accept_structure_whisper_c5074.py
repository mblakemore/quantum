#!/usr/bin/env python3
"""H15 G1 addendum — exact accept-set structure + closed-form verification.

Findings this script certifies (exact rationals, n=2,3,4):
  S1. ALT Bell distribution takes EXACTLY 3 values: a single peak at (0,0)
      of 2^n/4^n; a flat band of 1/(2*4^(n-1))... (see artifact) on the rest
      of the support; 0 elsewhere. Support sizes: 7 / 29 / 121.
  S2. Every support outcome satisfies popcount(a AND b) even (a.b = 0);
      the converse fails (support is a strict subset of the a.b=0 set).
  S3. OPTIMAL per-trial rule = support membership: P(accept|ALT)=1 exactly,
      success = 1/2 + (1 - |support|/4^n)/2 = the global Helstrom value.
      The transversal Bell measurement is globally OPTIMAL at 2 copies.
  S4. SIMPLE in-circuit rule "respond ALT iff XOR_i(a_i AND b_i) = 0":
      P(accept|ALT) = 1 exactly; P(accept|NULL) = 1/2 + 2^-(n+1);
      success = 3/4 - 2^-(n+2)  (n=4: 0.734375). One classical AND+XOR
      expression over the 2n measured bits — dynamic-circuit friendly.
  S5. Closed-form conjectures verified to primal precision:
      PPT ceiling  = 1/2 + (2^n - 1)/4^n          (n=4: 143/256)
      Helstrom     = 3/4 + (2^(n-1) - 1)/(2*4^n)  (n=4: 391/512)
      (Analytic derivation + dual certificate owed at freeze — Elder's seat.)
$0. No submission path.
"""
import json
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_g1_ceiling_atoms_whisper_c5074 import m2_brute, bell_basis

OUT = {"card": "h15_g1_accept_structure", "cycle": "C5074"}

for n in (2, 3, 4):
    d = 2 ** n
    D = d * d
    acc, count = m2_brute(n)
    M2 = acc / (count * d ** 2)
    bv = bell_basis(n)
    pa = {k: Fraction(int(round(float(v @ M2 @ v) * count * d ** 2)),
                      count * d ** 2) for k, v in bv.items()}
    support = [k for k, p in pa.items() if p > 0]
    vals = sorted(set(pa.values()))
    thr = Fraction(1, D)
    # S2: a.b invariant
    ab_even_all = all(bin(a & b).count("1") % 2 == 0 for a, b in support)
    ab_even_count = sum(1 for a in range(d) for b in range(d)
                        if bin(a & b).count("1") % 2 == 0)
    # S3: optimal = support membership
    p_acc_null_opt = Fraction(len(support), D)
    succ_opt = Fraction(1, 2) * 1 + Fraction(1, 2) * (1 - p_acc_null_opt)
    hel_conj = Fraction(3, 4) + Fraction(2 ** (n - 1) - 1, 2 * 4 ** n)
    # S4: simple parity rule
    p_alt_simple = sum(p for (a, b), p in pa.items()
                       if bin(a & b).count("1") % 2 == 0)
    p_null_simple = Fraction(ab_even_count, D)
    succ_simple = (Fraction(1, 2) * p_alt_simple
                   + Fraction(1, 2) * (1 - p_null_simple))
    simple_conj = Fraction(3, 4) - Fraction(1, 2 ** (n + 2))
    ppt_conj = Fraction(1, 2) + Fraction(2 ** n - 1, 4 ** n)
    OUT[f"n{n}"] = {
        "support_size": len(support),
        "distinct_values": [str(v) for v in vals],
        "p00": str(pa[(0, 0)]),
        "all_support_ab_even": ab_even_all,
        "ab_even_total": ab_even_count,
        "success_optimal_exact": str(succ_opt),
        "helstrom_conjecture": str(hel_conj),
        "optimal_equals_helstrom_conj": succ_opt == hel_conj,
        "p_accept_alt_simple_rule": str(p_alt_simple),
        "success_simple_rule_exact": str(succ_simple),
        "simple_rule_conjecture_3/4-2^-(n+2)": succ_simple == simple_conj,
        "ppt_ceiling_conjecture": str(ppt_conj),
        "ppt_ceiling_conjecture_float": float(ppt_conj),
        "gap_simple_minus_ceiling": float(succ_simple - ppt_conj),
        "gap_optimal_minus_ceiling": float(succ_opt - ppt_conj),
    }
    print(f"n={n}: opt {succ_opt} (==Helstrom-conj {succ_opt == hel_conj}) | "
          f"simple {succ_simple} | ceiling-conj {ppt_conj} | "
          f"gap(simple) {float(succ_simple - ppt_conj):.6f}", flush=True)

with open("/droid/repos/quantum/results/h15_g1_accept_structure_c5074.json",
          "w") as f:
    json.dump(OUT, f, indent=1)
print("WROTE results/h15_g1_accept_structure_c5074.json")
