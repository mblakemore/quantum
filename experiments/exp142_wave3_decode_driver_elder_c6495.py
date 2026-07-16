#!/usr/bin/env python3
"""Exp142 THREE-WAVE decode driver — Elder C6495.

WHY THIS EXISTS (disclosed bridge, frozen artifacts untouched): the frozen
`exp142_decode_meter.py` (8323461e...) accepts exactly TWO manifests
(--manifest wave-1, --manifest2 one continuation). Wave-3 decode requires
concatenating wave-1 + wave-2 + wave-3 per-basis streams before the SPRT walk.
This driver imports the FROZEN module and uses ONLY its functions for every
piece of math (fetch_pub_bits, parity_stream, bell_fidelity,
conventional_decode, quantum_decode — all frozen); it replicates main()'s
stream-assembly orchestration verbatim, generalized from one continuation
manifest to a list.

FAITHFULNESS PROOF (run before first real use): invoked with wave-1 + wave-2
only, output must EXACTLY equal the committed two-wave answers produced by the
frozen script itself (answers_n{N}_final_elder_c6493.json). --regression flag
does this comparison automatically.

Each continuation manifest must carry alive_bases_input (the alive list its
rows were built over) — injected from the 2-of-2-converged committed lists,
same discipline as the C6493 wave-2 bridge.

Usage:
  python3 exp142_wave3_decode_driver_elder_c6495.py --n 4 \
      --manifest ../results/exp142_wave1_n4_manifest.json \
      --cont ../results/exp142_wave2_n4_manifest_aug_elder.json \
      --cont ../results/exp142_wave3_n4_manifest_aug_elder.json \
      [--emit-answers out.json] [--emit-alive out.json] [--regression FILE]
"""
import argparse
import itertools
import json
import math
import sys

import exp142_decode_meter as dm  # FROZEN module — functions used unmodified


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--cont", action="append", default=[],
                    help="continuation manifest(s) in wave order, each with alive_bases_input")
    ap.add_argument("--emit-answers")
    ap.add_argument("--emit-alive")
    ap.add_argument("--regression",
                    help="compare output against a committed answers JSON; exit 3 on mismatch")
    args = ap.parse_args()
    n = args.n

    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()

    with open(args.manifest) as f:
        man1 = json.load(f)
    job1 = svc.job(man1["job_id"])
    pubs = man1["pubs"]

    idx = {k: [i for i, p in enumerate(pubs) if p["kind"] == k]
           for k in ("sentinel_start", "sentinel_end", "cal", "quantum")}
    conv_idx = [i for i, p in enumerate(pubs) if p["kind"].startswith("conv_wave")]

    s_start = dm.bell_fidelity(dm.fetch_pub_bits(job1, idx["sentinel_start"][0]))
    s_end = dm.bell_fidelity(dm.fetch_pub_bits(job1, idx["sentinel_end"][0]))
    print(f"sentinels: start {s_start:.3f} end {s_end:.3f}")

    # q_hat from wave-1 cal blocks (identical to frozen main)
    odd_tot, shots_tot = 0, 0
    for i in idx["cal"]:
        bits = dm.fetch_pub_bits(job1, i)
        stream = dm.parity_stream(bits, pubs[i]["b"])
        odd_tot += sum(stream)
        shots_tot += len(stream)
    q_raw = max(odd_tot / shots_tot, 1e-4)
    se = math.sqrt(q_raw * (1 - q_raw) / shots_tot)
    q_hat = min(q_raw + se, 0.49)
    print(f"q_hat(n={n}) = {q_raw:.4f} ({odd_tot}/{shots_tot}) "
          f"+ 1SE {se:.4f} -> q_used = {q_hat:.4f}")

    # wave-1 conventional streams (identical to frozen main)
    bstrs = man1["conv_b_strings"]
    streams = []
    row_base = 0
    for i in conv_idx:
        bits = dm.fetch_pub_bits(job1, i)
        rows, shots = pubs[i]["rows"], pubs[i]["shots"]
        for r in range(rows):
            chunk = bits[r * shots:(r + 1) * shots]
            streams.append(dm.parity_stream(chunk, bstrs[row_base + r]))
        row_base += rows

    # continuation waves (frozen main's manifest2 block, looped over manifests)
    bases = ["".join(t) for t in itertools.product(dm.PAULIS, repeat=n)]
    for cpath in args.cont:
        with open(cpath) as f:
            man2 = json.load(f)
        job2 = svc.job(man2["job_id"])
        alive_prev = man2.get("alive_bases_input") or []
        b2 = man2["conv_b_strings"]
        pubs2 = man2["pubs"]
        if sum(p["rows"] for p in pubs2) != len(alive_prev):
            print(f"FATAL: {cpath} rows != alive_bases_input length")
            return 2
        row_base2 = 0
        for i, p in enumerate(pubs2):
            bits = dm.fetch_pub_bits(job2, i)
            rows, shots = p["rows"], p["shots"]
            for r in range(rows):
                gidx = bases.index(alive_prev[row_base2 + r])
                chunk = bits[r * shots:(r + 1) * shots]
                streams[gidx].extend(dm.parity_stream(chunk, b2[row_base2 + r]))
            row_base2 += rows

    conv = dm.conventional_decode(streams, n, q_hat)
    print(f"conventional: identified={conv['identified']} P_hat={conv['P_hat']} "
          f"alive={len(conv['alive_bases'])} meter_median={conv['meter_median']}")

    qbits = dm.fetch_pub_bits(job1, idx["quantum"][0])
    quantum = dm.quantum_decode(qbits, n)
    print(f"quantum: P_hat={quantum['P_hat']} meter={quantum['meter']} "
          f"budget={quantum['shots_budget']}")

    answers = {"n": n,
               "quantum": quantum,
               "conventional": {"P_hat": conv["P_hat"],
                                "meter_median": conv["meter_median"],
                                "identified": conv["identified"],
                                "overage_submitted": conv["consumed_per_basis_total"]},
               "sentinels": {"start": s_start, "end": s_end},
               "q_hat_raw": q_raw, "q_used": q_hat}

    if args.emit_alive and conv["alive_bases"]:
        with open(args.emit_alive, "w") as f:
            json.dump({"n": n, "alive_bases": conv["alive_bases"]}, f)
        print(f"alive list -> {args.emit_alive}")

    if args.emit_answers:
        with open(args.emit_answers, "w") as f:
            json.dump(answers, f, indent=1)
        print(f"answers -> {args.emit_answers}")

    if args.regression:
        with open(args.regression) as f:
            ref = json.load(f)
        # overage_submitted in the frozen emit path = consumed_per_basis_total;
        # compare every graded/reported field
        mism = []
        for path, a, b in [
                ("quantum", answers["quantum"], ref["quantum"]),
                ("conventional", answers["conventional"], ref["conventional"]),
                ("sentinels", answers["sentinels"], ref["sentinels"]),
                ("q_hat_raw", answers["q_hat_raw"], ref["q_hat_raw"]),
                ("q_used", answers["q_used"], ref["q_used"])]:
            if a != b:
                mism.append((path, a, b))
        if mism:
            print("REGRESSION MISMATCH:")
            for p, a, b in mism:
                print(f"  {p}: driver={a} frozen={b}")
            return 3
        print("REGRESSION: EXACT MATCH vs frozen decode_meter output ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
