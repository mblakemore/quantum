#!/usr/bin/env python3
"""EXP142B n=6 blind decode + determinism attack (Whisper C5073, my prereg deliverables).
Same court role as n=4, adapted for n=6's chunked flight (reps split across 8192-row pubs).

REASSEMBLY (validated): concatenate all 6-bit conv rows in manifest JOB order x pub order ->
510,300 rows = EXACTLY 20 reps x 25,515 (3x8192 + 939 per rep); slice into 20. schedule reps are
columnar {rep, rows:[{A,b}...]}. DECODE = parity-based SPRT basis-elimination (endianness-invariant):
LLR += ln(p0/.5) even / ln((1-p0)/.5) odd; ACCEPT=6*ln3+ln100; ELIM=ln(.005); first basis to accept
= guessed P; copies=rows-to-stop. ATTACK = per-basis per-qubit determinism vs the fresh-b NULL
(C=35 rows/basis simulated), null-calibrated (the C5073 threshold-vs-noise lesson). Seal shut.
"""
import json, os, sys, glob
import numpy as np
from collections import defaultdict, Counter
from math import log
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
N = 6
ACCEPT = N * log(3) + log(100); ELIM = log(0.005)
REP_ROWS = 25515


def reassemble():
    m = json.load(open(os.path.join(RES, "exp142b_n6_manifest.json")))
    order = [j if isinstance(j, str) else j.get("job_id") for j in m["jobs"]]
    conv = []
    for jid in order:
        f = os.path.join(RES, f"exp142b_n6_raw_{jid}.json")
        if not os.path.exists(f):
            continue
        for p in json.load(open(f))["pubs"]:
            c = p.get("c") or list(p.values())[0]
            if len(c[0]) == N and len(c) > 200:
                conv.extend(c)
    assert len(conv) == 20 * REP_ROWS, f"reassembly {len(conv)} != {20*REP_ROWS}"
    return [conv[i * REP_ROWS:(i + 1) * REP_ROWS] for i in range(20)]


def cal_p0():
    ev = tot = 0
    for f in glob.glob(os.path.join(RES, "exp142b_n6_raw_*.json")):
        for p in json.load(open(f))["pubs"]:
            c = p.get("c") or list(p.values())[0]
            if len(c[0]) == N and 50 <= len(c) <= 200:
                for s in c:
                    ev += (sum(int(b) for b in s) % 2 == 0); tot += 1
    return ev / tot if tot else 0.97


def null_max_determinism(C, n_est, trials=800):
    rng = np.random.default_rng(6)
    return float(np.mean([np.maximum((d := rng.binomial(C, 0.5, n_est) / C), 1 - d).max() for _ in range(trials)])), \
           float(np.percentile([np.maximum((d := rng.binomial(C, 0.5, n_est) / C), 1 - d).max() for _ in range(trials)], 95))


def main():
    sched = json.load(open(os.path.join(RES, "exp142b_n6_schedule.json")))
    reps_sched = [r["rows"] for r in sched["reps"]]
    flown = reassemble()
    p0 = cal_p0(); l_even, l_odd = log(p0 / 0.5), log((1 - p0) / 0.5)
    print(f"n=6: reassembled 20 reps x {REP_ROWS}, p0={p0:.4f}, ACCEPT={ACCEPT:.2f}")

    guesses, copies, cens = [], [], 0
    atk_max = 0.0
    for rep_rows, out in zip(reps_sched, flown):
        assert len(rep_rows) == len(out) == REP_ROWS
        parity = [sum(int(b) for b in s) % 2 for s in out]
        by = defaultdict(list)
        for row, s in zip(rep_rows, out):
            by[row["A"]].append([int(b) for b in s])
        for A, rr in by.items():
            arr = np.array(rr); atk_max = max(atk_max, float(np.maximum(arr.mean(0), 1 - arr.mean(0)).max()))
        llr = defaultdict(float); alive = set(r["A"] for r in rep_rows); g = st = None
        for j, (row, par) in enumerate(zip(rep_rows, parity)):
            A = row["A"]
            if A not in alive:
                continue
            llr[A] += (l_odd if par else l_even)
            if llr[A] >= ACCEPT:
                g, st = A, j + 1; break
            if llr[A] <= ELIM:
                alive.discard(A)
        if g is None:
            cens += 1; g = max(alive, key=lambda a: llr[a]) if alive else "?"; st = len(rep_rows)
        guesses.append(g); copies.append(st)

    cons, nc = Counter(guesses).most_common(1)[0]
    # attack: null-calibrate the per-basis max determinism (C=35, 729 bases x 6 q x 20 reps)
    null_mean, null_95 = null_max_determinism(35, 729 * N * 20)
    attack_pass = atk_max <= null_95
    print(f"\nBLIND DECODE: guessed P = {cons}  ({nc}/20)  [seal shut — Elder grades on reveal]")
    print(f"  median copies-to-identify {int(np.median(copies))}, censored {cens}/20")
    print(f"ATTACK: max per-basis determinism {atk_max:.4f} vs fresh-b null (mean {null_mean:.4f}, 95th {null_95:.4f}) "
          f"-> {'PASS (at chance)' if attack_pass else 'CHECK'}")
    out = {"card": "exp142b_n6_blind_decode_whisper", "cycle": "C5073", "N": N, "p0": p0,
           "guessed_P": cons, "consensus": nc, "median_copies": int(np.median(copies)),
           "censored": cens, "attack_max_det": atk_max, "attack_null_mean": null_mean,
           "attack_null_95": null_95, "attack_pass": bool(attack_pass),
           "weight_guessed": sum(c != "I" for c in cons)}
    json.dump(out, open(os.path.join(RES, "exp142b_n6_blind_decode_whisper_c5073.json"), "w"), indent=1)
    print(f"-> results/exp142b_n6_blind_decode_whisper_c5073.json")


if __name__ == "__main__":
    main()
