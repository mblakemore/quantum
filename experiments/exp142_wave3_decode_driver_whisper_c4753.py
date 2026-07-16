#!/usr/bin/env python3
"""Exp142 multi-wave decode driver — Whisper C4753.

INDEPENDENT counterpart to Elder's exp142_wave3_decode_driver_elder_c6495.py
(chair call: orchestration implemented independently on each side so the
2-of-2 divergence gate keeps power at the orchestration layer — the layer
where all four of tonight's frozen-in defects lived. All MATH is imported
from the FROZEN decode module; this file only sequences it.)

Frozen functions used (zero reimplementation): fetch_pub_bits, parity_stream,
bell_fidelity, conventional_decode, quantum_decode. Continuation manifests
must carry alive_bases_input (injected from the 2-of-2-converged committed
alive lists; the frozen kit never writes it — see wave-2 decode note).

Usage:
  # real decode (wave1 + any number of continuation manifests, in wave order)
  python3 exp142_wave3_decode_driver_whisper_c4753.py --n 8 \
      --manifest ../results/exp142_wave1_n8_manifest.json \
      --continuation m2_aug.json --continuation m3_aug.json \
      [--emit-alive out.json] [--emit-answers out.json]

  # regression proof (MANDATORY before first real use, P2 discipline):
  # run wave1+wave2 only and require exact match with the committed
  # C4750 answers file on every field; exit 3 on any mismatch.
  ... --continuation m2_aug.json --regression ../results/exp142_wave12_n8_answers.json
"""
import argparse
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import exp142_decode_meter as fz  # FROZEN module — all math lives here

PAULIS = "XYZ"


def decode(n, manifest_path, continuation_paths):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()

    with open(manifest_path) as f:
        man1 = json.load(f)
    job1 = svc.job(man1["job_id"])
    pubs = man1["pubs"]

    idx = {k: [i for i, p in enumerate(pubs) if p["kind"] == k]
           for k in ("sentinel_start", "sentinel_end", "cal", "quantum")}
    conv_idx = [i for i, p in enumerate(pubs) if p["kind"].startswith("conv_wave")]

    s_start = fz.bell_fidelity(fz.fetch_pub_bits(job1, idx["sentinel_start"][0]))
    s_end = fz.bell_fidelity(fz.fetch_pub_bits(job1, idx["sentinel_end"][0]))
    print(f"sentinels: start {s_start:.3f} end {s_end:.3f}")

    odd_tot, shots_tot = 0, 0
    for i in idx["cal"]:
        stream = fz.parity_stream(fz.fetch_pub_bits(job1, i), pubs[i]["b"])
        odd_tot += sum(stream)
        shots_tot += len(stream)
    q_raw = max(odd_tot / shots_tot, 1e-4)
    se = math.sqrt(q_raw * (1 - q_raw) / shots_tot)
    q_hat = min(q_raw + se, 0.49)
    print(f"q_hat(n={n}) = {q_raw:.4f} ({odd_tot}/{shots_tot}) + 1SE {se:.4f} "
          f"-> q_used = {q_hat:.4f}")

    # wave-1 conventional streams, product order (mirrors frozen main exactly)
    bstrs = man1["conv_b_strings"]
    streams = []
    row_base = 0
    for i in conv_idx:
        bits = fz.fetch_pub_bits(job1, i)
        rows, shots = pubs[i]["rows"], pubs[i]["shots"]
        for r in range(rows):
            chunk = bits[r * shots:(r + 1) * shots]
            streams.append(fz.parity_stream(chunk, bstrs[row_base + r]))
        row_base += rows

    # continuation waves: frozen main's manifest2 block generalized to a list
    bases = ["".join(t) for t in itertools.product(PAULIS, repeat=n)]
    for cpath in continuation_paths:
        with open(cpath) as f:
            manc = json.load(f)
        alive_prev = manc.get("alive_bases_input") or []
        if not alive_prev:
            sys.exit(f"FATAL: {cpath} lacks alive_bases_input (inject the "
                     f"converged committed alive list; frozen kit never writes it)")
        if len(alive_prev) != len(manc["conv_b_strings"]):
            sys.exit(f"FATAL: {cpath} row-count mismatch "
                     f"{len(alive_prev)} vs {len(manc['conv_b_strings'])}")
        jobc = svc.job(manc["job_id"])
        b2 = manc["conv_b_strings"]
        row_base2 = 0
        for i, p in enumerate(manc["pubs"]):
            bits = fz.fetch_pub_bits(jobc, i)
            rows, shots = p["rows"], p["shots"]
            for r in range(rows):
                gidx = bases.index(alive_prev[row_base2 + r])
                chunk = bits[r * shots:(r + 1) * shots]
                streams[gidx].extend(fz.parity_stream(chunk, b2[row_base2 + r]))
            row_base2 += rows
        print(f"continuation {os.path.basename(cpath)}: "
              f"{row_base2} rows extended (job {manc['job_id']})")

    conv = fz.conventional_decode(streams, n, q_hat)
    print(f"conventional: identified={conv['identified']} P_hat={conv['P_hat']} "
          f"alive={len(conv['alive_bases'])} meter_median={conv['meter_median']}")

    quant = fz.quantum_decode(fz.fetch_pub_bits(job1, idx["quantum"][0]), n)
    print(f"quantum: P_hat={quant['P_hat']} meter={quant['meter']} "
          f"budget={quant['shots_budget']}")

    return {"n": n, "quantum": quant,
            "conventional": {"P_hat": conv["P_hat"],
                             "meter_median": conv["meter_median"],
                             "identified": conv["identified"],
                             "overage_submitted": conv["consumed_per_basis_total"]},
            "sentinels": {"start": s_start, "end": s_end},
            "q_hat_raw": q_raw, "q_used": q_hat}, conv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--continuation", action="append", default=[],
                    help="continuation manifest (wave order); repeatable")
    ap.add_argument("--emit-alive")
    ap.add_argument("--emit-answers")
    ap.add_argument("--regression",
                    help="committed answers JSON to compare against; exit 3 on mismatch")
    args = ap.parse_args()

    answers, conv = decode(args.n, args.manifest, args.continuation)

    if args.regression:
        with open(args.regression) as f:
            ref = json.load(f)
        if answers != ref:
            for k in ref:
                if answers.get(k) != ref[k]:
                    print(f"REGRESSION MISMATCH field '{k}': "
                          f"got {answers.get(k)!r} want {ref[k]!r}")
            sys.exit(3)
        print(f"REGRESSION PASS: exact match vs {args.regression} (all fields)")
        return

    if args.emit_alive and conv["alive_bases"]:
        with open(args.emit_alive, "w") as f:
            json.dump({"alive_bases": conv["alive_bases"]}, f)
        print(f"alive list -> {args.emit_alive}")
    if args.emit_answers:
        with open(args.emit_answers, "w") as f:
            json.dump(answers, f, indent=1)
        print(f"answers -> {args.emit_answers}")


if __name__ == "__main__":
    main()
