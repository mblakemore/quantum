#!/usr/bin/env python3
"""P1 n=8 C1/Q ADVANTAGE MARGIN — one shared harness, one currency, one criterion. Elder C6575.

THE STANDING FIX FROM C6567 (my own 29x->6.6x inflation at n=4), applied from the start at n=8:

  CURRENCY  = COPIES OF rho.  The C1 arm consumes 1 copy per single-copy measurement. The Q arm
              consumes 2 copies per two-copy BELL SAMPLE -- so Q is billed 2 x samples, never
              samples-vs-copies. (Mechanism 1 of the n=4 inflation, worth 2x on its own.)
  CRITERION = ONE Wald SPRT, A = log((4^n - 1)/eps_fa), eps_fa = 0.01, the SAME familywise
              false-alarm correction on BOTH arms. No lenient "winner-stable + rate>0.6" stopping
              rule on the denominator. (Mechanism 2, another ~2x. They MULTIPLY.)

Both meters come from the FROZEN c5003 decoder (covering_decode / two_copy_Q) which already carries
that shared A -- imported, not reimplemented, so the two arms cannot drift apart.

GATE DISCIPLINE (the C6568 lesson that caught decode_meter): the Q constraint machinery is validated
by REPRODUCING the revealed n6 rung (P=IYXZXY, rate 0.875) before any n8 number is billed. Synthetic
self-consistency does not qualify -- a wrong tool passes synthetic and fails flown.

HONEST FRAMING (pre-registered): the CLAIM is the exponential SCALING across n=4/6/8, not a single
headline ratio. A small-n point is modest BY DESIGN. Censoring is reported, never hidden.
"""
import argparse, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import numpy as np
import exp142_robust_decoder_sim as G2
from exp142_p1_c1_decoder_elder_c5003 import two_copy_Q, wald_AB   # FROZEN, shared A with the C1 arm

# frozen per-n on-device two-copy Bell constraint rate (c5003 docstring, PRE-REGISTERED)
R_BELL_FROZEN = {4: 0.933, 6: 0.882, 8: 0.846}


def constraint_stream(bitstrings, n, P, mapping, csign):
    """Per-BELL-SAMPLE hit/miss for candidate P (the raw observable the advantage rides on)."""
    Pb = G2.pauli_to_bits(P); want = csign[P.count("Y") % 2]
    return [int(G2.sp_inner(G2.outcome_to_bits(s, n, mapping), Pb, n)) == want for s in bitstrings]


def q_meter(bitstrings, n, P, mapping, csign, r_bell):
    """Q arm billed in COPIES under the shared Wald A. Returns dict incl. censoring status."""
    stream = constraint_stream(bitstrings, n, P, mapping, csign)
    rate = sum(stream) / len(stream)
    used = two_copy_Q(stream, n, r_bell)                 # FROZEN SPRT, A = log((4^n-1)/0.01)
    A, _ = wald_AB(n)
    s_pass, s_fail = math.log(r_bell / 0.5), math.log((1 - r_bell) / 0.5)
    llr = sum(s_pass if h else s_fail for h in stream[:used])
    resolved = llr >= A                                  # False => budget exhausted, meter CENSORED
    return {"P": P, "bell_samples_available": len(stream), "measured_constraint_rate": rate,
            "r_bell_used": r_bell, "bell_samples_used": used, "copies_used": 2 * used,
            "wald_A": A, "llr_at_stop": llr, "RESOLVED": bool(resolved),
            "censored": not resolved}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n8-qarm", default=os.path.join(HERE, "..", "results",
                                                      "exp142_p1_n8_qarm_fetch_elder_c6568.json"))
    ap.add_argument("--n8-c1", default=os.path.join(HERE, "..", "results",
                                                    "exp142_p1_c1_n8_decode_elder_c6575.json"))
    ap.add_argument("--phat-q", default="IZYXZXZZ", help="Elder's committed blind n8 Q estimate (#1412)")
    ap.add_argument("--n6-job", default="d9hrarshonhs73adh7og")
    ap.add_argument("--n6-expect", default="IYXZXY")
    ap.add_argument("--skip-n6-gate", action="store_true")
    args = ap.parse_args()

    print("calibrating Bell mapping / constraint sign (noiseless)...", flush=True)
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)

    # ---------------- n6 KNOWN-ANSWER GATE on the Q machinery (flown, revealed rung) ----------------
    gate = None
    if not args.skip_n6_gate:
        from run_exp66_qpu_partb import _get_ibm_service
        import exp142_decode_meter as M
        print(f"n6 Q GATE: fetching revealed job {args.n6_job}...", flush=True)
        bits6 = list(M.fetch_pub_bits(_get_ibm_service().job(args.n6_job), 0))
        r_true = sum(constraint_stream(bits6, 6, args.n6_expect, mapping, csign)) / len(bits6)
        # runner-up scan over ALL 4^6-1 candidates: the winner must BE the revealed seal
        from exp142_p1_c1_decoder_elder_c5003 import candidates
        rates = sorted(((sum(constraint_stream(bits6, 6, P, mapping, csign)) / len(bits6), P)
                        for P in candidates(6)), reverse=True)
        gate = (rates[0][1] == args.n6_expect)
        print(f"  winner {rates[0][1]} rate {rates[0][0]:.3f} | runner-up {rates[1][1]} {rates[1][0]:.3f}"
              f" | expect {args.n6_expect} ({r_true:.3f})")
        print(f"  n6 Q GATE: {'PASS — Q constraint machinery reproduces the revealed seal'
                              if gate else '*** MISMATCH — do NOT bill the n8 Q meter ***'}")
        if not gate:
            return 1

    # ---------------- n8 arms ----------------
    qa = json.load(open(args.n8_qarm))
    bits8 = qa["raw_bitstrings"]
    print(f"\nn8 Q arm: job {qa['job_id']}, {len(bits8)} Bell samples, P_hat_Q = {args.phat_q}")
    qres = {str(r): q_meter(bits8, 8, args.phat_q, mapping, csign, r)
            for r in (R_BELL_FROZEN[8], None) if r}
    head = qres[str(R_BELL_FROZEN[8])]
    print(f"  measured constraint rate = {head['measured_constraint_rate']:.4f} "
          f"(frozen r_bell {head['r_bell_used']})")
    print(f"  Wald A = {head['wald_A']:.3f}  -> resolved at {head['bell_samples_used']} Bell samples"
          f" = {head['copies_used']} COPIES   RESOLVED={head['RESOLVED']}")
    # sensitivity: bill against the arm's OWN measured rate (mildly self-favouring -> report, don't headline)
    sens = q_meter(bits8, 8, args.phat_q, mapping, csign, head["measured_constraint_rate"])
    print(f"  [sensitivity] r_bell = measured {sens['r_bell_used']:.4f} -> "
          f"{sens['bell_samples_used']} samples = {sens['copies_used']} copies")

    if not os.path.exists(args.n8_c1):
        print(f"\n*** C1 decode artifact not present yet ({args.n8_c1}) — Q arm billed, margin pending ***")
        return 2
    c1 = json.load(open(args.n8_c1))
    c1_copies = c1["result"]["C1_distinct_copies"]
    print(f"\nn8 C1 arm: P_hat_C1 = {c1['P_hat_C1']}  C1_distinct_copies = {c1_copies} COPIES"
          f"  (q={c1['q_used']:.6f}, C1-epoch measured)")

    margin = c1_copies / head["copies_used"]
    margin_sens = c1_copies / sens["copies_used"]
    print(f"\n{'='*72}\n  n=8 EXECUTED MARGIN  =  C1 {c1_copies} copies / Q {head['copies_used']} copies"
          f"  =  {margin:.1f}x")
    print(f"  (sensitivity, measured-rate r_bell: {margin_sens:.1f}x)")
    print(f"  currency: COPIES both arms (Q = 2 x Bell samples).  criterion: ONE Wald A={head['wald_A']:.3f}")
    if head["censored"]:
        print("  *** Q meter CENSORED (budget exhausted before A) — margin is an OVERSTATEMENT ***")
    print("="*72)

    out = os.path.join(HERE, "..", "results", "exp142_p1_margin_n8_elder_c6575.json")
    json.dump({"n": 8, "n6_q_gate_pass": gate,
               "C1": {"P_hat": c1["P_hat_C1"], "copies": c1_copies, "q_used": c1["q_used"],
                      "source": os.path.basename(args.n8_c1)},
               "Q": {"P_hat": args.phat_q, "headline": head, "sensitivity_measured_rate": sens,
                     "job": qa["job_id"]},
               "margin_n8_frozen_rbell": margin, "margin_n8_measured_rbell": margin_sens,
               "currency": "copies of rho (Q = 2 x Bell samples)",
               "criterion": f"one Wald SPRT A=log((4^8-1)/0.01)={head['wald_A']:.4f}",
               "claim_framing": "the claim is the EXPONENTIAL SCALING across n=4/6/8, not this single ratio",
               "epoch_note": "Q arm flown 2026-07-25 open-instance; C1 arm flown 2026-07-29 alt "
                             "open-instance. Margin spans two epochs; C1 billed at its OWN measured "
                             "epoch q (0.004883, 1.53x backend props).",
               "blind_status": "n8 seal NOT revealed at time of writing — both P_hat are blind estimates"},
              open(out, "w"), indent=1)
    print(f"SAVED {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
