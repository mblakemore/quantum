#!/usr/bin/env python3
"""P1 EXECUTED C1/Q ADVANTAGE SCALING CURVE, n = 4 / 6 / 8 — Elder C6575.

THE CLAIM IS THE CURVE, NOT A HEADLINE RATIO (my own C6567 standing fix). A single-n margin is
modest by design and invites the exact over-reach that inflated my n=4 number 4x. What the P1
protocol actually asserts is a SEPARATION IN SCALING: the classical single-copy arm should climb
like the 3^n covering emission while the two-copy Bell arm climbs only like the Wald threshold,
i.e. linearly in n. This bills every rung through ONE harness so the ratios mean something.

  CURRENCY  = copies of rho on BOTH arms (Q = 2 x Bell samples, never samples-vs-copies)
  CRITERION = ONE Wald SPRT per rung, A(n) = log((4^n - 1)/0.01), same familywise correction
  q         = COMMON across rungs for the headline curve, so the SHAPE is not confounded by
              per-epoch readout drift (n=4/n=6 predate the in-flight cal; only n=8 has a measured
              epoch q). A second common-q column shows the shape is q-insensitive.

SEAL-FREE VALIDATION AT EVERY RUNG: the C1 arm (single-copy covering SPRT) and the Q arm (two-copy
Bell constraint) are INDEPENDENT estimators of the same sealed P. Their agreement is checkable
WITHOUT the seal — and at n=8 it is the strongest evidence we have, because the Q arm's own
separation there is thin (0.056, ~1.4 SE) while a chance agreement between the two arms is
1/(4^8-1) ~ 1.5e-5.

Reads C1 artifacts produced by exp142_p1_c1_n8_decode_elder_c6575.py; meters Q from the flown
quantum jobs. Frozen c5003 meters imported, never reimplemented.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_robust_decoder_sim as G2
import exp142_decode_meter as M
from exp142_p1_c1_decoder_elder_c5003 import two_copy_Q, wald_AB, candidates
from run_exp66_qpu_partb import _get_ibm_service

R_BELL_FROZEN = {4: 0.933, 6: 0.882, 8: 0.846}     # pre-registered on-device Bell constraint rate
RES = os.path.join(HERE, "..", "results")
C1_ART = {4: "exp142_p1_c1_curve_n4_elder_c6575.json",
          6: "exp142_p1_c1_curve_n6_elder_c6575.json",
          8: "exp142_p1_c1_n8_decode_elder_c6575.json"}
Q_JOB = {4: "d9hr6n50k0jc738ild80", 6: "d9hrarshonhs73adh7og", 8: None}   # n8 Q read from saved artifact
N8_QARM = "exp142_p1_n8_qarm_fetch_elder_c6568.json"


def stream(bits, n, P, mapping, csign):
    Pb = G2.pauli_to_bits(P); want = csign[P.count("Y") % 2]
    return [int(G2.sp_inner(G2.outcome_to_bits(s, n, mapping), Pb, n)) == want for s in bits]


def q_arm(bits, n, mapping, csign):
    """BLIND: argmax constraint-rate over ALL 4^n-1 candidates, then meter that winner under the
    shared Wald A in COPIES. Returns winner, runner-up (separation) and the billed cost."""
    rates = sorted(((sum(stream(bits, n, P, mapping, csign)) / len(bits), P) for P in candidates(n)),
                   reverse=True)
    (r1, P1), (r2, P2) = rates[0], rates[1]
    rb = R_BELL_FROZEN[n]
    used = two_copy_Q(stream(bits, n, P1, mapping, csign), n, rb)
    A, _ = wald_AB(n)
    s_pass, s_fail = math.log(rb / 0.5), math.log((1 - rb) / 0.5)
    llr = sum(s_pass if h else s_fail for h in stream(bits, n, P1, mapping, csign)[:used])
    return {"P_hat_Q": P1, "rate": r1, "runner_up": P2, "runner_rate": r2, "separation": r1 - r2,
            "bell_samples_available": len(bits), "bell_samples_used": used, "copies": 2 * used,
            "r_bell": rb, "wald_A": A, "RESOLVED": bool(llr >= A), "censored": bool(llr < A)}


def main():
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    svc = None
    rows, curve = [], {}
    for n in (4, 6, 8):
        art = os.path.join(RES, C1_ART[n])
        if not os.path.exists(art):
            print(f"n={n}: C1 artifact missing ({C1_ART[n]}) — skipping"); continue
        c1 = json.load(open(art))
        if n == 8:
            bits = json.load(open(os.path.join(RES, N8_QARM)))["raw_bitstrings"]
        else:
            svc = svc or _get_ibm_service()
            bits = list(M.fetch_pub_bits(svc.job(Q_JOB[n]), 0))
        q = q_arm(bits, n, mapping, csign)
        c1_copies = c1["result"]["C1_distinct_copies"]
        agree = (c1["P_hat_C1"] == q["P_hat_Q"])
        m = c1_copies / q["copies"]
        # second common-q column from the sweep the C1 driver already ran
        alt = c1.get("q_sweep", {})
        alt_k = next(iter(alt), None)
        m_alt = (alt[alt_k]["C1_distinct_copies"] / q["copies"]) if alt_k else None
        curve[n] = {"C1_copies": c1_copies, "C1_q": c1["q_used"], "P_hat_C1": c1["P_hat_C1"],
                    "Q": q, "cross_arm_agree": agree, "margin": m,
                    "C1_copies_alt_q": (alt[alt_k]["C1_distinct_copies"] if alt_k else None),
                    "alt_q": alt_k, "margin_alt_q": m_alt}
        rows.append((n, c1_copies, q["copies"], m, agree, q["P_hat_Q"], c1["P_hat_C1"],
                     q["separation"], q["censored"], m_alt))

    print("\n" + "=" * 100)
    print("P1 EXECUTED ADVANTAGE — one currency (copies), one criterion (Wald A(n)=log((4^n-1)/0.01))")
    print("=" * 100)
    print(f"{'n':>2} | {'C1 copies':>10} | {'Q copies':>8} | {'margin':>8} | {'margin@altq':>11} | "
          f"{'arms agree':>10} | {'Q sep':>7} | {'Q cens':>6}")
    print("-" * 100)
    for (n, c, qc, m, ag, pq, pc, sep, cen, malt) in rows:
        print(f"{n:>2} | {c:>10} | {qc:>8} | {m:>7.1f}x | "
              f"{(f'{malt:.1f}x' if malt else 'n/a'):>11} | {('YES' if ag else '*** NO ***'):>10} | "
              f"{sep:>7.3f} | {str(cen):>6}")
    print("-" * 100)
    for (n, c, qc, m, ag, pq, pc, sep, cen, malt) in rows:
        print(f"   n={n}: P_hat_C1={pc}  P_hat_Q={pq}  {'(independent estimators AGREE)' if ag else '(DISAGREE)'}")

    if len(rows) >= 2:
        print("\nSCALING (per +2 in n):")
        for i in range(1, len(rows)):
            n0, c0, q0, m0 = rows[i-1][0], rows[i-1][1], rows[i-1][2], rows[i-1][3]
            n1, c1_, q1, m1 = rows[i][0], rows[i][1], rows[i][2], rows[i][3]
            print(f"  n={n0}->{n1}:  C1 x{c1_/c0:.2f} (3^2=9 predicted)   "
                  f"Q x{q1/q0:.2f} (linear-in-n predicted ~{n1/n0:.2f})   margin x{m1/m0:.2f}")
        print(f"\n  C1 copies per emission basis (3^n): "
              + "  ".join(f"n={r[0]}:{r[1]/3**r[0]:.2f}" for r in rows))
        print(f"  Q copies per qubit:                 "
              + "  ".join(f"n={r[0]}:{r[2]/r[0]:.2f}" for r in rows))

    out = os.path.join(RES, "exp142_p1_scaling_curve_elder_c6575.json")
    json.dump({"curve": {str(k): v for k, v in curve.items()},
               "currency": "copies of rho both arms (Q = 2 x Bell samples)",
               "criterion": "one Wald SPRT per rung, A(n)=log((4^n-1)/0.01)",
               "claim": "SEPARATION IN SCALING: C1 ~ 3^n emission-covering, Q ~ linear in n",
               "seal_free_validation": "C1 and Q are independent estimators; agreement is checkable "
                                       "without the seal (chance agreement = 1/(4^n-1))",
               "caveats": ["n=4/n=6 predate the in-flight readout cal; headline curve uses a COMMON q "
                           "so the SHAPE is not confounded by epoch drift",
                           "each rung is ONE draw of P; the C1 meter depends on where P falls in the "
                           "committed candidate walk order (n=8 P sits 22.6% in => cheaper C1 => "
                           "SMALLER margin, i.e. the conservative direction)",
                           "n=8 seal NOT revealed at time of writing; both P_hat are blind estimates"]},
              open(out, "w"), indent=1)
    print(f"\nSAVED {out}")


if __name__ == "__main__":
    main()
