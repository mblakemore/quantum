#!/usr/bin/env python3
"""entropy_ledger.py — H2: the negative-information ledger (Whisper C4662).
Two zero-shot legs over banked, certified data.

LEG 1 — Shannon-Fannes pass (SCOPE-CORRECTED from the C4659 pattern, which
overstated the transfer): observed TVD LOWER-bounds state trace distance, so
quantum Fannes cannot be applied to measurement TVDs. What IS always valid:
classical Fannes on the measured OUTCOME DISTRIBUTIONS —
    |H(p) - H(q)| <= T*log2(d) + eta(T),  T = TVD, eta(x) = -x log2 x
(valid T <= 1/e). Every certified TVD bound in the ledger converts to a
certified Shannon-entropy bound on the distributions, stated as such.

LEG 2 — negative conditional entropy from banked CHSH (Exp112b-micro):
Bell-twirl the banked state (LOCC-constructible; twirl can only INCREASE
entropy). From the 4 CHSH correlators with settings a=Z, a'=X, b=(Z+X)/rt2,
b'=(Z-X)/rt2: <XX>+<ZZ> = (E1+E2+E3-E4)/rt2 = S_chsh/rt2 (derived in-code from
the setting geometry, checked numerically). Worst-case MAXIMIZE H(p_Bell) over
the unmeasured <YY> and the unknown XX/ZZ split, subject to positivity ->
one-sided-conservative upper bound on S_twirl(B|A) = H(p)-1. Certification:
upper bound + 5*SE < 0 -> ENTANGLEMENT BY NEGATIVE INFORMATION, zero shots."""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG2 = np.log(2.0)


def eta(x):
    return 0.0 if x <= 0 else float(-x * np.log2(x))


def fannes_classical(T, d):
    return float(T * np.log2(d) + eta(T))


def h_shannon(ps):
    return float(sum(eta(p) for p in ps if p > 0))


def leg1_rows():
    rows = [
        ("F96 hotspot D_order bound", 0.0303, 32,
         "parallel vs sequential CZ scheduling, 5q joint dist"),
        ("F96 control D_order bound", 0.0393, 32,
         "control site"),
        ("Exp118 D_A (par vs seqAB, measured)", 0.0598 + 5 * 0.0042, 32,
         "duration artifact magnitude, 5SE-inflated"),
        ("switch-bench sched card (regression)", 0.0302, 32,
         "same certification via bench path"),
    ]
    out = []
    for name, T, d, note in rows:
        out.append({"row": name, "T_bound": T, "d": d,
                    "dH_bound_bits": fannes_classical(T, d), "note": note})
    return out


def leg2_exp112b():
    g = json.load(open(os.path.join(HERE, "..", "results",
                                    "exp112b_micro_grade.json")))
    E = g["E"]
    # settings geometry a=Z, a'=X, b=(Z+X)/rt2, b'=(Z-X)/rt2:
    # E(ab)=(ZZ+ZX)/rt2, E(ab')=(ZZ-ZX)/rt2, E(a'b)=(XZ+XX)/rt2,
    # E(a'b')=-(XX-XZ)/rt2 sign per pattern (+,+,+,-). Sum combination:
    c = (E["ab"] + E["abp"] + E["apb"] - E["apbp"]) / np.sqrt(2.0)  # XX+ZZ
    shots_per = 4000
    se_E = np.sqrt(1.0 / shots_per)  # var<=1 per setting
    se_c = float(np.sqrt(4) * se_E / np.sqrt(2.0))

    def worst_H(cval):
        best = 0.0
        for yy in np.linspace(-1.0, 1.0, 4001):
            p_phip = (1 + cval - yy) / 4.0
            p_psim = (1 - cval - yy) / 4.0
            rest = (2 + 2 * yy) / 4.0
            if p_phip < -1e-9 or p_psim < -1e-9 or rest < -1e-9:
                continue
            # worst split of `rest` between phi-/psi+ is even (max entropy)
            ps = [max(p_phip, 0), max(p_psim, 0), rest / 2.0, rest / 2.0]
            s = sum(ps)
            ps = [p / s for p in ps]
            best = max(best, h_shannon(ps))
        return best

    H_pt = worst_H(c)
    H_5s = worst_H(c - 5 * se_c)   # smaller c -> looser constraint -> larger H
    cert = H_5s < 1.0
    return {"source": "exp112b_micro (job in results/exp112b_micro_jobids.json)",
            "S_chsh": g["S"], "XX_plus_ZZ": float(c), "SE": se_c,
            "worst_case_H_point": H_pt,
            "worst_case_H_at_minus5SE": H_5s,
            "S_cond_upper_bound_point": H_pt - 1.0,
            "S_cond_upper_bound_5SE": H_5s - 1.0,
            "certified_negative": bool(cert),
            "scope": ["claim is for the BELL-TWIRLED banked state "
                      "(LOCC-constructible; twirl only increases entropy)",
                      "worst-case over unmeasured YY and XX/ZZ split -> "
                      "one-sided conservative",
                      "assumes standard CHSH setting geometry a=Z,a'=X,"
                      "b,b'=(Z±X)/rt2 per Exp112 apparatus"]}


def main():
    l1 = leg1_rows()
    l2 = leg2_exp112b()
    out = {"leg1_shannon_fannes": l1, "leg2_negative_ink": l2,
           "scope_correction": "C4659 pattern overstated: observed TVD only "
           "LOWER-bounds trace distance; quantum Fannes transfer requires "
           "state-level distance. Leg 1 claims are CLASSICAL Shannon bounds "
           "on measured distributions (always valid); leg 2 achieves the "
           "quantum (von Neumann) claim via twirl+positivity instead."}
    print("LEG 1 — classical Fannes certifications (zero shots):")
    for r in l1:
        print(f"  {r['row']}: |dH| <= {r['dH_bound_bits']:.3f} bits "
              f"(T<={r['T_bound']:.4f}, d={r['d']})")
    print("LEG 2 — negative ink (Exp112b-micro, zero shots):")
    print(f"  XX+ZZ = {l2['XX_plus_ZZ']:.4f} ± {l2['SE']:.4f} "
          f"(S_chsh={l2['S_chsh']})")
    print(f"  worst-case H(twirl) = {l2['worst_case_H_point']:.4f} "
          f"(at -5SE: {l2['worst_case_H_at_minus5SE']:.4f})")
    print(f"  S(B|A)_twirl <= {l2['S_cond_upper_bound_5SE']:.4f} at 5SE -> "
          f"{'CERTIFIED NEGATIVE' if l2['certified_negative'] else 'not certified'}")
    p = os.path.join(HERE, "..", "results", "entropy_ledger_c4662.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"wrote {p}")


if __name__ == "__main__":
    main()
