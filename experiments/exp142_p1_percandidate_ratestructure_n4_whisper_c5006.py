#!/usr/bin/env python3
"""F119 P1 per-candidate RATE STRUCTURE — n4 rung (Whisper C5006, Creator: "apply the same look to n4").
$0: reads the fetched-cached n4 C1 covering shots. n4 is the GRADED rung (6.6x margin, public); its
sealed true P was held OFF-GIT, so the winner here is DATA-IDENTIFIED (argmax = P_hat_C1, exactly what
the blind decoder produces) — not compared to a separately-known ground truth. n8 UNTOUCHED.

Same 4 questions as n6 (focus.json), same guardrails: binomial-sigma normalization for the weight=>
shot-count artifact; census link untestable (register [6,110,59,132]); FLAT is a valid result.
"""
import json, os, sys, math
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from exp142_p1_c1_decoder_elder_c5003 import candidates, support, support_parity, full_weight_bases, covers, p0_of


def main():
    m = json.load(open(os.path.join(QROOT, "results", "exp142_p1_n4_manifest.json")))
    n = m["n"]; cpb = m["c_per_basis"]; bor = m["c1_basis_of_row"]; layout = m["conv_layout"]
    fwb = full_weight_bases(n)
    assert [fwb[r // cpb] for r in range(len(bor))] == bor, "basis-of-row mismatch"
    jid = [j["job_id"] for j in m["jobs"] if j["kind"] == "c1_covering"][0]
    allb = json.load(open(os.path.join(QROOT, "results", "cache", f"n4_c1_chunk_{jid}.json")))
    assert len(allb) == len(bor), f"{len(allb)} != {len(bor)}"
    fw = defaultdict(list)
    for r, b in enumerate(allb):
        fw[bor[r]].append(b)
    print(f"[load] n={n} register(phys)={layout}  {sum(len(v) for v in fw.values())} flown shots over {len(fw)} bases")

    order = candidates(n)
    rows = []
    for P in order:
        S = support(P); w = len(S); ev = tot = 0
        for A in fwb:
            if not covers(A, P):
                continue
            for bits in fw[A]:
                ev += 1 if support_parity(bits, P) == 0 else 0; tot += 1
        rate = ev / tot; z = (rate - 0.5) / math.sqrt(0.25 / tot)
        rows.append((P, w, rate, tot, z))
    rows.sort(key=lambda r: -r[2])
    winner = rows[0]; runner = rows[1]
    field = [r for r in rows if r[0] != winner[0]]

    print("\n=== Q4 WINNER COMFORT (data-identified P_hat_C1; n4 seal off-git) ===")
    print(f"  P_hat (rank1) = {winner[0]} (w{winner[1]}): rate={winner[2]:.4f}  z=+{winner[4]:.1f}sigma  n_shots={winner[3]}")
    print(f"  model p0_of({winner[0]},q=0.015) = {p0_of(winner[0],0.95,0.015):.4f}  (compare to observed {winner[2]:.4f})")
    print(f"  runner-up {runner[0]} (w{runner[1]}): rate={runner[2]:.4f}  z={runner[4]:+.1f}")
    print(f"  z-gap winner->runner = {winner[4]-runner[4]:.1f}sigma  |  EMPTY GAP check below")

    print("\n=== Q1 WEIGHT STRUCTURE of the field (flat at 0.5 after binomial normalization?) ===")
    print(f"  {'w':>2} {'n_cand':>7} {'shots/cand':>11} {'mean_rate':>10} {'mean|z|':>8} {'max|z|':>7}  (null mean|z|~0.80)")
    for w in range(1, n + 1):
        fr = [r for r in field if r[1] == w]
        if not fr:
            continue
        mr = sum(r[2] for r in fr) / len(fr); mz = sum(abs(r[4]) for r in fr) / len(fr)
        mxz = max(abs(r[4]) for r in fr)
        flag = "  <-- NOT flat" if mz > 1.2 else ""
        print(f"  {w:>2} {len(fr):>7} {fr[0][3]:>11} {mr:>10.4f} {mz:>8.2f} {mxz:>7.1f}{flag}")

    print("\n=== Q3 CONFUSION SPECTRUM: field sorted by z (empty gap = no partial confuser) ===")
    fs = sorted(field, key=lambda r: -r[4])
    n5 = sum(1 for r in field if r[4] > 5.0)
    tS = set(support(winner[0]))
    for r in fs[:8]:
        P, w, rate, tot, z = r; pS = set(support(P))
        agree = sum(1 for i in (pS & tS) if P[i] == winner[0][i])
        rel = ("sub" if pS <= tS else "super" if pS >= tS else "cross") + f" {agree}/{len(pS)} match"
        print(f"  {P:>8} w{w} rate={rate:.4f} z={z:+.1f} shots={tot}  {rel}")
    gap_lo = fs[0][4]; print(f"\n  top non-winner z={gap_lo:.1f}; winner z={winner[4]:.1f}; "
                             f"EMPTY GAP z=[{gap_lo:.1f},{winner[4]:.1f}]; non-winners z>5: {n5}/{len(field)}")

    print("\n=== Q1b weight-1 directional tell (n6 found toward-even readout bias) ===")
    w1 = [r for r in rows if r[1] == 1]
    above = sum(1 for r in w1 if r[2] > 0.5)
    print(f"  weight-1 candidates: {above}/{len(w1)} rates >0.5 (toward even); mean rate {sum(r[2] for r in w1)/len(w1):.4f}")
    for r in sorted(w1, key=lambda r: -abs(r[4])):
        pos = support(r[0])[0]
        print(f"    {r[0]} phys{layout[pos]} {r[0][pos]}-basis: rate={r[2]:.4f} z={r[4]:+.1f}")

    out = {"card": "exp142_p1_percandidate_ratestructure_n4", "cycle": "C5006", "substrate": "claude-fable-5",
           "n": n, "register_phys": layout, "seal": "off-git; winner is data-identified P_hat_C1",
           "winner": {"P_hat": winner[0], "w": winner[1], "rate": round(winner[2], 4), "z": round(winner[4], 1),
                      "model_p0": round(p0_of(winner[0], 0.95, 0.015), 4), "n_shots": winner[3]},
           "runner_up": {"P": runner[0], "rate": round(runner[2], 4), "z": round(runner[4], 1)},
           "field_top_z": round(fs[0][4], 1), "field_z_gt5": n5, "field_total": len(field),
           "weight1_toward_even": f"{above}/{len(w1)}"}
    outp = os.path.join(QROOT, "results", "exp142_p1_percandidate_ratestructure_n4_whisper_c5006.json")
    json.dump(out, open(outp, "w"), indent=1)
    print(f"\n  -> {outp}")


if __name__ == "__main__":
    main()
