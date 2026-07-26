#!/usr/bin/env python3
"""F119 P1 per-candidate RATE STRUCTURE — the confusion spectrum of the flown n6 C1 arm (Whisper C5006,
Creator directive: "tear through F119 per-candidate rate structure"). $0: reads the cached flown n6 C1
covering shots (results/cache/n6_c1_chunk_*.json), spends no QPU.

WHAT'S NEW: we have only ever reported the AGGREGATE margin (6.6x n4 -> 24.3x n6). Never the internal
shape. THEORY (from the decoder's own model): the true state is (I + 0.95 P_true)/2^n; measured in a
full-weight covering basis A, candidate P's support-parity reads the Pauli (x)_{i in supp(P)} A_i. Its
expectation on rho is 0.95 IFF that operator == P_true (=> only the EXACT true candidate), else 0. So
IDEALLY exactly ONE candidate (P_true=IYXZXY) sits at ~0.975 and ALL 4094 others sit at 0.5. The
untouched question is the EMPIRICAL confusion spectrum: does the flown data show that clean 1-vs-rest
separation, or do some non-true candidates carry systematic elevated rate (a coherent-error signature)?

PRE-REGISTERED QUESTIONS (focus.json C5005->C5006, written before numbers):
  Q1 weight structure  Q2 physical-qubit signature  Q3 where the margin lives  Q4 winner comfort.

GUARDRAILS (focus.json + phys16 C5005 near-miss):
  * SAMPLE-SIZE ARTIFACT: a weight-w candidate pools 3^(6-w) covering bases x 64 shots. Low-weight =>
    many shots (tight around 0.5); high-weight => few shots (wide around 0.5). Any weight-dependence in
    SPREAD is binomial sample-size, NOT physics. Compare every field rate to its OWN binomial sigma.
  * Q2 CENSUS LINK IS UNTESTABLE HERE: this register is physical [6,110,59,132,4,147]; the drift census
    {26,53,73} is a different chip/experiment. Do NOT force it. Report the answerable version instead:
    per-register-position confusion on the actual flown qubits.
  * FLAT IS A VALID RESULT: a clean 1-vs-rest separation with a flat 0.5 field is exactly what the
    theorem predicts. Do not manufacture structure.
"""
import json, os, sys, math, itertools
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from exp142_p1_c1_decoder_elder_c5003 import candidates, support, support_parity, full_weight_bases, covers

TRUE_P = "IYXZXY"      # the REVEALED n6 seal (n6 revealed => blind-safe; n8 UNTOUCHED)
NOMINAL_Q = 0.015


def load_flown():
    m = json.load(open(os.path.join(QROOT, "results", "exp142_p1_n6_manifest.json")))
    n = m["n"]; cpb = m["c_per_basis"]; stored_bor = m["c1_basis_of_row"]; layout = m["conv_layout"]
    fwb = full_weight_bases(n)
    assert [fwb[r // cpb] for r in range(len(stored_bor))] == stored_bor, "basis-of-row mismatch"
    cache = os.path.join(QROOT, "results", "cache")
    c1jobs = [j["job_id"] for j in m["jobs"] if j["kind"] == "c1_covering"]
    all_bits = []
    for jid in c1jobs:
        cf = os.path.join(cache, f"n6_c1_chunk_{jid}.json")
        all_bits.extend(json.load(open(cf)))
    assert len(all_bits) == len(stored_bor), f"{len(all_bits)} != {len(stored_bor)}"
    fw_shots = defaultdict(list)
    for r, bits in enumerate(all_bits):
        fw_shots[stored_bor[r]].append(bits)
    return n, layout, dict(fw_shots), fwb


def main():
    n, layout, fw_shots, fwb = load_flown()
    print(f"[load] n={n} register(phys)={layout}  {sum(len(v) for v in fw_shots.values())} flown shots over {len(fw_shots)} bases")
    print(f"[theory] ideal: ONLY {TRUE_P} at rate ~0.975; all 4094 others at 0.5 (flat field).\n")

    # ---- per-candidate empirical even-rate, pooled over ALL its covering bases ----
    order = candidates(n)
    rows = []   # (P, weight, even_rate, n_shots, z_from_half)
    for P in order:
        S = support(P); w = len(S)
        evens = 0; tot = 0
        for A in fwb:
            if not covers(A, P):
                continue
            for bits in fw_shots[A]:
                evens += 1 if support_parity(bits, P) == 0 else 0
                tot += 1
        rate = evens / tot
        sigma = math.sqrt(0.25 / tot)                 # binomial sigma of a fair-coin rate at this n_shots
        z = (rate - 0.5) / sigma                       # standardized deviation from the flat-field null
        rows.append((P, w, rate, tot, z))

    rows.sort(key=lambda r: -r[2])                     # by rate, high first
    by_P = {r[0]: r for r in rows}
    true_row = by_P[TRUE_P]
    field = [r for r in rows if r[0] != TRUE_P]        # the 4094 non-true candidates
    field_sorted = sorted(field, key=lambda r: -r[2])  # by z (most anomalous non-winners first)

    # ---- Q4 WINNER COMFORT ----
    runner = rows[1] if rows[0][0] == TRUE_P else rows[0]
    print("=" * 90)
    print("  Q4 — WINNER COMFORT")
    print("=" * 90)
    rank = [r[0] for r in rows].index(TRUE_P)
    print(f"  TRUE P {TRUE_P}: rate={true_row[2]:.4f}  z=+{true_row[4]:.1f}sigma  n_shots={true_row[3]}  (rank {rank+1}/{len(rows)})")
    print(f"  runner-up {runner[0]} (w{runner[1]}): rate={runner[2]:.4f}  z={runner[4]:+.1f}  n_shots={runner[3]}")
    print(f"  winner-vs-runner rate gap = {true_row[2]-runner[2]:.4f}  |  z-gap = {true_row[4]-runner[4]:.1f}sigma")
    print(f"  => {'COMFORTABLE (true P is the clean rank-1 outlier)' if rank==0 and true_row[2]-runner[2]>0.2 else 'CHECK — not a clean separation'}\n")

    # ---- Q1 WEIGHT STRUCTURE (field only; winner excluded) ----
    print("=" * 90)
    print("  Q1 — WEIGHT STRUCTURE of the non-true FIELD (is it flat at 0.5 after binomial normalization?)")
    print("=" * 90)
    print(f"  {'w':>2} {'n_cand':>7} {'shots/cand':>11} {'mean_rate':>10} {'mean|z|':>8} {'max|z|':>7}  expect|z|~0.80 if pure-null")
    for w in range(1, n + 1):
        fw_rows = [r for r in field if r[1] == w]
        if not fw_rows:
            continue
        mr = sum(r[2] for r in fw_rows) / len(fw_rows)
        mz = sum(abs(r[4]) for r in fw_rows) / len(fw_rows)
        mxz = max(abs(r[4]) for r in fw_rows)
        shots = fw_rows[0][3]
        flag = "" if mz < 1.2 else "  <-- field NOT flat (elevated |z|)"
        print(f"  {w:>2} {len(fw_rows):>7} {shots:>11} {mr:>10.4f} {mz:>8.2f} {mxz:>7.1f}{flag}")
    print("  (mean|z| ~0.80 = half-normal mean = pure binomial null. >>0.80 across a weight = real structure.)\n")

    # ---- Q3 WHERE THE MARGIN LIVES: the confusion spectrum (top non-true candidates by z) ----
    print("=" * 90)
    print("  Q3 — CONFUSION SPECTRUM: most anomalous NON-TRUE candidates (elevated = coherent-error echo)")
    print("=" * 90)
    print(f"  {'candidate':>10} {'w':>2} {'rate':>7} {'z':>7} {'shots':>6}  relation to true P {TRUE_P}")
    def relation(P):
        # how P aligns to TRUE_P: agreements on TRUE_P's support, and whether supp(P) subset/superset
        tS = set(support(TRUE_P)); pS = set(support(P))
        agree = sum(1 for i in (pS & tS) if P[i] == TRUE_P[i])
        rel = []
        if pS <= tS: rel.append("sub-support")
        if pS >= tS: rel.append("super-support")
        rel.append(f"{agree}/{len(pS)} sites match trueP on overlap")
        return ", ".join(rel)
    n_sig = sum(1 for r in field if r[4] > 5.0)
    for r in field_sorted[:12]:
        P, w, rate, tot, z = r
        print(f"  {P:>10} {w:>2} {rate:>7.4f} {z:>+7.1f} {tot:>6}  {relation(P)}")
    print(f"\n  non-true candidates with z>5sigma: {n_sig} / {len(field)}  "
          f"(pure null expects ~{len(field)*2*(1-0.5*(1+math.erf(5/math.sqrt(2)))):.2f})")

    # ---- Q2 (answerable version): per-register-position confusion ----
    print("\n" + "=" * 90)
    print("  Q2 — PER-POSITION confusion (census {26,53,73} link UNTESTABLE: this register is different qubits)")
    print("=" * 90)
    print(f"  register positions -> physical qubits: {dict(enumerate(layout))}")
    print(f"  {'pos':>3} {'phys':>5} {'mean|z| of cands touching it':>28} {'max|z|':>7}")
    for pos in range(n):
        touch = [r for r in field if pos in support(r[0])]
        mz = sum(abs(r[4]) for r in touch) / len(touch)
        mxz = max(abs(r[4]) for r in touch)
        print(f"  {pos:>3} {layout[pos]:>5} {mz:>28.2f} {mxz:>7.1f}")
    print("  (a position whose candidates carry systematically higher |z| = a device-quality signature ON THIS chip;")
    print("   flat across positions = no per-qubit confusion structure. NOT the drift-census claim.)")

    # ---- persist ----
    out = {
        "card": "exp142_p1_percandidate_ratestructure", "cycle": "C5006", "substrate": "claude-fable-5",
        "true_P": TRUE_P, "n": n, "register_phys": layout,
        "winner": {"P": TRUE_P, "rate": round(true_row[2], 4), "z": round(true_row[4], 1),
                   "rank": rank + 1, "runner_up": runner[0], "runner_rate": round(runner[2], 4),
                   "rate_gap": round(true_row[2] - runner[2], 4)},
        "field_z_gt5": n_sig, "field_total": len(field),
        "top_confusion": [{"P": r[0], "w": r[1], "rate": round(r[2], 4), "z": round(r[4], 1)}
                          for r in field_sorted[:12]],
        "prereg": "focus.json C5005->C5006; Q2 census link retired (different register/chip)",
        "guardrail": "field spread normalized by per-candidate binomial sigma (weight=>shot-count artifact controlled)",
    }
    outp = os.path.join(QROOT, "results", "exp142_p1_percandidate_ratestructure_whisper_c5006.json")
    json.dump(out, open(outp, "w"), indent=1)
    print(f"\n  -> {outp}")


if __name__ == "__main__":
    main()
