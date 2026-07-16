#!/usr/bin/env python3
"""Exp142 post-flight decode + meter — Whisper C4746. FROZEN at prereg freeze.

Consumes ONLY outcome bitstrings + the P-independent manifest (blind protocol 5b);
never reads circuit definitions from retrieved jobs.

Pipeline per n:
  1. sentinels: Bell fidelity start/end (window integrity, report only)
  2. q_hat(n): pooled odd-rate on the 3 known-Pauli cal blocks (300 shots)
  3. SPRT barriers by FROZEN FORMULA: alpha = 0.01/3^n (Bonferroni FW 1%),
     beta = 0.01;  A = ln((1-beta)/alpha), B = ln(beta/(1-alpha))
     per-shot LLR: odd -> ln(q_hat/0.5); even -> ln((1-q_hat)/0.5)
  4. conventional: per-basis parity streams vs manifest b -> SPRT crossing status
     -> alive list (wave 2) | after all crossed: P_hat_c = max-final-LLR accepted
     basis (sigma-independent); METER = MEDIAN over 1001 precommitted permutations
     (seeds 142000..143000) of sequential-replay consumption
  5. quantum: Bell outcomes -> Gate-2 ML decoder -> P_hat_q; meter = stable prefix
     (smallest m whose argmax equals final and never changes after), budget = all rows

Usage:
  python3 exp142_decode_meter.py --n 8 --manifest ../results/exp142_wave1_n8_manifest.json
      [--manifest2 ../results/exp142_wave2_n8_manifest.json] [--emit-alive out.json]
      [--emit-answers ../results/answers_n8.json]
"""
import argparse
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_robust_decoder_sim as g2

PAULIS = "XYZ"
PERM_SEEDS = list(range(142000, 143001))  # 1001 precommitted (prereg section 4)


def fetch_pub_bits(job, pub_index):
    """Outcome bitstrings for one PUB: array of '0101...' strings, shape (rows*shots,)
    grouped row-major. Reads only measurement data."""
    res = job.result()[pub_index]
    # SamplerV2: res.data.<creg>.get_bitstrings() ; creg name 'c' default
    reg = list(res.data.keys())[0] if hasattr(res.data, "keys") else "c"
    arr = getattr(res.data, reg)
    return arr.get_bitstrings()


def parity_stream(bitstrings, b_str):
    b = np.array([int(c) for c in b_str])
    out = []
    for s in bitstrings:
        v = np.array([int(c) for c in s.replace(" ", "")[::-1][: len(b)]])
        out.append(int((v.sum() - b.sum()) % 2))
    return out  # 1 = odd


def sprt_barriers(n, q_hat):
    alpha = 0.01 / (3 ** n)
    beta = 0.01
    A = math.log((1 - beta) / alpha)
    B = math.log(beta / (1 - alpha))
    l_odd = math.log(q_hat / 0.5)
    l_even = math.log((1 - q_hat) / 0.5)
    return A, B, l_odd, l_even


def sprt_walk(stream, A, B, l_odd, l_even):
    """Returns (status, shots_consumed, final_llr): status accept/reject/open."""
    llr = 0.0
    for k, odd in enumerate(stream, 1):
        llr += l_odd if odd else l_even
        if llr >= A:
            return "accept", k, llr
        if llr <= B:
            return "reject", k, llr
    return "open", len(stream), llr


def conventional_decode(streams, n, q_hat):
    """streams: list over bases (product order) of parity lists (wave1+wave2 concat).
    Returns dict with per-basis status, P_hat, alive list, meter median."""
    A, B, l_odd, l_even = sprt_barriers(n, q_hat)
    walks = [sprt_walk(s, A, B, l_odd, l_even) for s in streams]
    bases = ["".join(t) for t in itertools.product(PAULIS, repeat=n)]
    alive = [bases[i] for i, (st, _, _) in enumerate(walks) if st == "open"]
    accepted = [(i, llr) for i, (st, _, llr) in enumerate(walks) if st == "accept"]
    P_hat = bases[max(accepted, key=lambda t: t[1])[0]] if accepted else None
    meter = None
    if not alive:  # meter only defined once every SPRT has crossed
        cons = np.array([w[1] for w in walks])
        acc_set = {i for i, _ in accepted}
        meters = []
        for seed in PERM_SEEDS:
            order = np.random.default_rng(seed).permutation(len(bases))
            tot = 0
            for idx in order:
                tot += cons[idx]
                if idx in acc_set:
                    break
            meters.append(tot)
        meter = float(np.median(meters))
    return {"P_hat": P_hat, "alive_bases": alive, "meter_median": meter,
            "identified": P_hat is not None and not alive,
            "barriers": {"A": A, "B": B}, "q_hat": q_hat,
            "consumed_per_basis_total": int(sum(w[1] for w in walks))}


def quantum_decode(bitstrings, n):
    mapping = g2.calibrate_bell_mapping()
    csign = g2.calibrate_constraint_sign(mapping)
    shots_bits = np.array([g2.outcome_to_bits(s, n, mapping) for s in bitstrings])
    cands, cand_M, ypar = g2.candidate_matrix(n)
    swapped = np.concatenate([cand_M[:, n:], cand_M[:, :n]], axis=1)
    vals = (shots_bits @ swapped.T) % 2
    target = np.array([csign[int(y)] for y in ypar], dtype=np.int8)
    cum = np.cumsum((vals == target[None, :]).astype(np.int32), axis=0)
    finals = cum[-1]
    win = int(np.argmax(finals))
    # stable prefix meter
    meter = len(bitstrings)
    for m in range(1, len(bitstrings) + 1):
        row = cum[m - 1]
        best = np.flatnonzero(row == row.max())
        if len(best) == 1 and best[0] == win:
            if all(np.argmax(cum[k]) == win and
                   (cum[k] == cum[k].max()).sum() == 1
                   for k in range(m, len(bitstrings))):
                meter = m
                break
    return {"P_hat": "".join(cands[win]), "meter": meter,
            "shots_budget": len(bitstrings)}


def bell_fidelity(bitstrings):
    good = sum(1 for s in bitstrings if s.replace(" ", "") in ("00", "11"))
    return good / len(bitstrings)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--manifest2")
    ap.add_argument("--emit-alive")
    ap.add_argument("--emit-answers")
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

    s_start = bell_fidelity(fetch_pub_bits(job1, idx["sentinel_start"][0]))
    s_end = bell_fidelity(fetch_pub_bits(job1, idx["sentinel_end"][0]))
    print(f"sentinels: start {s_start:.3f} end {s_end:.3f}")

    # q_hat from cal blocks
    odd_tot, shots_tot = 0, 0
    for i in idx["cal"]:
        bits = fetch_pub_bits(job1, i)
        stream = parity_stream(bits, pubs[i]["b"])
        odd_tot += sum(stream)
        shots_tot += len(stream)
    q_hat = max(odd_tot / shots_tot, 1e-4)
    print(f"q_hat(n={n}) = {q_hat:.4f}  ({odd_tot}/{shots_tot})")

    # conventional streams: rows across chunked PUBs, in product order
    bstrs = man1["conv_b_strings"]
    streams = []
    row_base = 0
    for i in conv_idx:
        bits = fetch_pub_bits(job1, i)  # rows*shots row-major
        rows, shots = pubs[i]["rows"], pubs[i]["shots"]
        for r in range(rows):
            chunk = bits[r * shots:(r + 1) * shots]
            streams.append(parity_stream(chunk, bstrs[row_base + r]))
        row_base += rows
    # wave 2 continuation
    if args.manifest2:
        with open(args.manifest2) as f:
            man2 = json.load(f)
        job2 = svc.job(man2["job_id"])
        bases = ["".join(t) for t in itertools.product(PAULIS, repeat=n)]
        alive_prev = man2.get("alive_bases_input") or []
        b2 = man2["conv_b_strings"]
        pubs2 = man2["pubs"]
        row_base2 = 0
        for i, p in enumerate(pubs2):
            bits = fetch_pub_bits(job2, i)
            rows, shots = p["rows"], p["shots"]
            for r in range(rows):
                gidx = bases.index(alive_prev[row_base2 + r])
                chunk = bits[r * shots:(r + 1) * shots]
                streams[gidx].extend(parity_stream(chunk, b2[row_base2 + r]))
            row_base2 += rows

    conv = conventional_decode(streams, n, q_hat)
    print(f"conventional: identified={conv['identified']} P_hat={conv['P_hat']} "
          f"alive={len(conv['alive_bases'])} meter_median={conv['meter_median']}")

    if args.emit_alive and conv["alive_bases"]:
        with open(args.emit_alive, "w") as f:
            json.dump({"alive_bases": conv["alive_bases"]}, f)
        print(f"alive list -> {args.emit_alive} (feed to --submit-wave2)")

    # quantum arm
    qi = idx["quantum"][0]
    qbits = fetch_pub_bits(job1, qi)
    quant = quantum_decode(qbits, n)
    print(f"quantum: P_hat={quant['P_hat']} meter={quant['meter']} "
          f"budget={quant['shots_budget']}")

    if args.emit_answers:
        with open(args.emit_answers, "w") as f:
            json.dump({"n": n, "quantum": quant,
                       "conventional": {"P_hat": conv["P_hat"],
                                        "meter_median": conv["meter_median"],
                                        "identified": conv["identified"],
                                        "overage_submitted": conv[
                                            "consumed_per_basis_total"]},
                       "sentinels": {"start": s_start, "end": s_end},
                       "q_hat": q_hat}, f, indent=1)
        print(f"answers -> {args.emit_answers}")


if __name__ == "__main__":
    main()
