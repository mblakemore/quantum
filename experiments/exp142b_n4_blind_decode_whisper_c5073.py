#!/usr/bin/env python3
"""EXP142B n=4 — Whisper's INDEPENDENT blind decode + exact per-basis determinism attack.
C5073, prereg items (honest-blind decode + attack). Independent cross-check on Elder's frozen
grader — implemented from the pinned spec, NOT by calling his grader.

DECODE (honest, blind): the true basis A=P gives EVEN total parity per row (o=b, b even-parity);
any wrong basis has >=1 conjugate qubit -> 50/50 -> parity ~uniform. So SPRT per candidate basis on
total-parity-even (endianness-invariant: uses sum(bits)%2 only). Pinned boundaries (prereg):
  LLR += ln(p0/0.5) on EVEN, ln((1-p0)/0.5) on ODD; ACCEPT A = n*ln3 + ln100 (=9.0 at n=4);
  ELIMINATE B = ln(0.005) (=-5.3). Replay committed row order per rep; guessed P = first basis to
  ACCEPT; copies-to-identify = rows consumed to that stop. Meter = MEDIAN over M=20 reps.
p0 estimated from the cal blocks (known Pauli, matched basis) — the readout-limited even-rate.
ATTACK (exact per-basis): for each basis, per-qubit determinism = max(frac0,frac1) over its 27
fresh-b rows; a leak drives a true-basis qubit -> ~1.0. Must sit in the uniform band (<=0.65).
SEAL: I output my GUESSED P (my decode's product) for Elder to grade on reveal; I do NOT open the seal.
"""
import json, os, glob
import numpy as np
from collections import defaultdict
from math import log, comb

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
N = 4
BASES = ["".join(t) for t in __import__("itertools").product("XYZ", repeat=N)]
ACCEPT = N * log(3) + log(100)      # 9.0
ELIM = log(0.005)                   # -5.3


def load():
    sched = json.load(open(os.path.join(RES, "exp142b_n4_schedule.json")))
    man = json.load(open(os.path.join(RES, "exp142b_n4_manifest.json")))
    conv_reps = [p for p in sched["pubs"] if isinstance(p, list)]        # 20 reps, manifest order
    job_order = [j if isinstance(j, str) else j.get("job_id") for j in man["jobs"]]
    # flown conv pubs, in manifest job order, conv pubs within a job in order
    flown = []
    for jid in job_order:
        f = os.path.join(RES, f"exp142b_n4_raw_{jid}.json")
        d = json.load(open(f))
        for p in d["pubs"]:
            c = p.get("c") or list(p.values())[0]
            if len(c[0]) == N and len(c) > 1000:      # conv_v2 (4-bit, 2187)
                flown.append(c)
    return sched, man, conv_reps, flown, job_order


def cal_p0():
    # cal blocks: known Pauli measured in matched basis -> even-rate = p0 (readout-limited)
    evens, tot = 0, 0
    for jid_f in glob.glob(os.path.join(RES, "exp142b_n4_raw_*.json")):
        d = json.load(open(jid_f))
        for p in d["pubs"]:
            c = p.get("c") or list(p.values())[0]
            if len(c[0]) == N and len(c) == 100:      # cal blocks (100 rows, 4-bit)
                for s in c:
                    evens += (sum(int(b) for b in s) % 2 == 0); tot += 1
    return evens / tot if tot else None


def main():
    sched, man, conv_reps, flown, job_order = load()
    assert len(conv_reps) == 20 and len(flown) == 20, (len(conv_reps), len(flown))
    p0 = cal_p0()
    print(f"p0 (cal even-rate, readout-limited) = {p0:.4f} | ACCEPT {ACCEPT:.2f} ELIM {ELIM:.2f}")
    l_even, l_odd = log(p0 / 0.5), log((1 - p0) / 0.5)

    guesses, copies, censored = [], [], 0
    attack_max_det = 0.0
    for i, (rep, out) in enumerate(zip(conv_reps, flown)):
        assert len(rep) == len(out) == 2187, (len(rep), len(out))
        parity = [sum(int(b) for b in s) % 2 for s in out]              # 0 even, 1 odd
        # exact per-basis determinism attack (per-qubit majority over each basis's 27 rows)
        by_basis = defaultdict(list)
        for row, s in zip(rep, out):
            by_basis[row["A"]].append([int(b) for b in s])
        for A, rows in by_basis.items():
            arr = np.array(rows)
            det = np.maximum(arr.mean(0), 1 - arr.mean(0)).max()
            attack_max_det = max(attack_max_det, det)
        # SPRT basis-elimination, committed order
        llr = {A: 0.0 for A in BASES}
        alive = set(BASES)
        guess, stop = None, None
        for j, (row, par) in enumerate(zip(rep, parity)):
            A = row["A"]
            if A not in alive:
                continue
            llr[A] += (l_odd if par else l_even)
            if llr[A] >= ACCEPT:
                guess, stop = A, j + 1
                break
            if llr[A] <= ELIM:
                alive.discard(A)
        if guess is None:
            censored += 1
            guess = max(alive, key=lambda A: llr[A]) if alive else "????"
            stop = len(rep)
        guesses.append(guess); copies.append(stop)

    from collections import Counter
    gc = Counter(guesses)
    consensus, nconsensus = gc.most_common(1)[0]
    med = int(np.median(copies))
    print(f"\nINDEPENDENT BLIND DECODE (M=20 reps):")
    print(f"  guessed P: {consensus}  (agreement {nconsensus}/20)  [seal shut — Elder grades on reveal]")
    print(f"  copies-to-identify: median {med}, IQR [{int(np.percentile(copies,25))},{int(np.percentile(copies,75))}], "
          f"min {min(copies)} max {max(copies)}")
    print(f"  censored (no accept within schedule): {censored}/20")
    print(f"\nEXACT PER-BASIS DETERMINISM ATTACK: max per-qubit determinism {attack_max_det:.4f} "
          f"(uniform band <=0.65) -> {'PASS (chance)' if attack_max_det <= 0.65 else 'DELIVERY-FAIL'}")
    out = {"card": "exp142b_n4_blind_decode_whisper", "cycle": "C5073", "p0": p0,
           "accept": ACCEPT, "elim": ELIM, "guessed_P": consensus, "consensus_count": nconsensus,
           "all_guesses": guesses, "copies_median": med, "copies": copies, "censored": censored,
           "attack_max_determinism_perbasis": attack_max_det,
           "attack_gate": "PASS" if attack_max_det <= 0.65 else "DELIVERY-FAIL",
           "note": "independent SPRT cross-check on Elder's grader; seal shut, guessed P for grade-on-reveal"}
    json.dump(out, open(os.path.join(RES, "exp142b_n4_blind_decode_whisper_c5073.json"), "w"), indent=1)
    print("-> results/exp142b_n4_blind_decode_whisper_c5073.json")


if __name__ == "__main__":
    main()
