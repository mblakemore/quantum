#!/usr/bin/env python3
"""Exp142c FROZEN DECODE ESTIMATOR — Elder C6567, grader seat (BLIND, posted PRE-REVEAL).

The 3-arm grader for the mixed-state F119 re-fly. P-BLIND by construction: the decoder IDENTIFIES
P from the flown parity data; it never takes the true P as input. Ember reveals the sealed
fullweight_eps1_v2 P only AFTER this estimator + its decoded s_hat are committed, then win/miss +
the ratio fall out by comparing s_hat to the revealed P.

Frozen definitions (all pre-committed in the card; nothing tunable here):
  * meter currency  = COPIES consumed = shots (shot == one copy of rho_P, mixed-state delivery).
  * C1 (best-known) = median over M reps of copies-to-stop of the SPRT-elimination decoder,
                      FROZEN benchmark 408 / 4482 / 55589 (n=4/6/8) — this run MEASURES it live.
  * Wald boundaries (Elder #921, corrected): A = log(3^n / 0.01)  [confirm; familywise-FA < 1%],
                      B = log(0.005)          [eliminate; true-false-elim < 0.5%],
                      LLR += log(p0/0.5) on parity-EVEN (pass), log((1-p0)/0.5) on parity-ODD (fail),
                      p0 = 1 - p_flip,  p_flip = (1-(1-2*q_n)^n)/2,  q_n from the manifest (measured).
  * committed basis order = itertools.product("XYZ", repeat=n) (canonical; row r -> rep r//3^n,
                      basis order[r % 3^n]). Decoder REPLAYS this order (blind: no reorder toward P).
  * ARM Q  = two-copy Bell/SWAP meter, O(1) — frozen ~2-4 copies (measured where flown; else frozen).
  * ARM C1 = the SPRT-elim decoder above.
  * ARM ATTACK (cond 3) = the 36-copy determinism decoder run on the SAME flown shots=1 parity data;
                      it MUST return chance (<= ~1/3^n). A genuine mixture has no fixed-b to exploit,
                      so it should be even cleaner than the pure-state fix. SUCCESS => DELIVERY-FAIL.
  * cond 4 (per-shot independence) = shot-correlation check on the flown parity stream (lag-1 corr ~ 0).

Ratio = C1 / Q (best-known-conditional); growth-trend = fitted exponent of log2(ratio) vs n w/ CI
(n=8 measured at M=5 -> honest-wide CI propagated). No lower-bound / "unconditional" claim.
"""
import sys, os, json, math, itertools
import numpy as np

def p_flip(n, q):        return (1 - (1 - 2*q)**n) / 2
def wald(n, q):
    p0 = 1 - p_flip(n, q)
    return (n*math.log(3) + math.log(100),  # A = log(3^n/0.01)
            math.log(0.005),                 # B
            math.log(p0/0.5), math.log((1-p0)/0.5), p0)

def sprt_decode(parities_by_basis, order, n, q):
    """parities_by_basis[basis_str] = list of parity bits (0=even/pass, 1=odd/fail), C per basis.
    Walk committed order, run Wald SPRT per basis, ACCEPT (LLR>=A) => s_hat, ELIMINATE (LLR<=B) => next.
    Returns (s_hat_or_None, copies_used). copies_used counts every parity bit consumed = the meter."""
    A, B, s_even, s_odd, _ = wald(n, q)
    used = 0
    for basis in order:
        llr = 0.0
        for bit in parities_by_basis[basis]:          # consume this basis's copies in order
            used += 1
            llr += s_even if bit == 0 else s_odd
            if llr >= A:  return basis, used           # confirmed P
            if llr <= B:  break                        # eliminated -> next basis
    return None, used                                  # censored (no basis confirmed within schedule)

def attack_determinism(parities_by_basis, order, n):
    """36-copy determinism attack on the SAME parity data: the v1 crack read a FIXED-b batch's
    deterministic parity. On a genuine mixture there is no fixed b -> it must land at chance.
    Heuristic recovery: pick the basis whose parity is MOST deterministic (lowest odd-rate) over its
    first 36 copies (the determinism signature). Returns the guessed basis (compare to true P later)."""
    best, bestscore = None, 1.0
    for basis in order:
        pr = parities_by_basis[basis][:36]
        if not pr: continue
        odd_rate = sum(pr)/len(pr)                     # true basis -> ~0 (deterministic even); wrong -> ~0.5
        score = min(odd_rate, 1-odd_rate)              # determinism = distance from 0.5, low = deterministic
        if score < bestscore: bestscore, best = score, basis
    return best, round(bestscore, 4)

def lag1_corr(parity_stream):
    a = np.array(parity_stream, float)
    if len(a) < 3 or a.std() == 0: return 0.0
    return round(float(np.corrcoef(a[:-1], a[1:])[0,1]), 4)

# ---- flown-data adapter: pull job results, reshape to parities_by_basis per rep ----
def parity_of_bits(bits):        # bits: iterable of 0/1 -> parity (0=even, 1=odd)
    return int(sum(bits)) & 1

def load_rung(manifest_path, pull_fn):
    man = json.load(open(manifest_path))
    n, M, C, q = man["n"], man["M"], man["C"], man["q_n"]
    order = ["".join(t) for t in itertools.product("XYZ", repeat=n)]
    B = len(order)                                     # 3^n
    # pull per-row parity lists (row r -> C parities). pull_fn(job) returns {row_index: [C parities]}.
    row_par = {}
    for job in man["jobs"]:
        row_par.update(pull_fn(job, n, C))             # keyed by absolute row index row_lo..row_hi
    reps = []
    for m in range(M):
        pbb = {}
        for bi, basis in enumerate(order):
            r = m*B + bi
            pbb[basis] = row_par.get(r, [])
        reps.append(pbb)
    # decode every rep
    stops, shats = [], []
    for pbb in reps:
        sh, used = sprt_decode(pbb, order, n, q)
        shats.append(sh); stops.append(used)
    ident = max(set(x for x in shats if x), key=lambda s: shats.count(s)) if any(shats) else None
    censored = sum(1 for s in shats if s is None)
    # attack + independence on rep-0 (representative)
    atk_basis, atk_det = attack_determinism(reps[0], order, n)
    stream = [b for basis in order for b in reps[0][basis]]
    return {"n": n, "M": M, "C": C, "q_n": q,
            "C1_median_copies_to_stop": int(np.median(stops)) if stops else None,
            "C1_copies_iqr": [int(np.percentile(stops,25)), int(np.percentile(stops,75))] if stops else None,
            "s_hat_identified": ident, "s_hat_per_rep_consensus_frac": round(shats.count(ident)/len(shats),3) if ident else 0.0,
            "censored_reps": censored, "censor_frac": round(censored/len(shats),4),
            "attack_guess": atk_basis, "attack_determinism_score": atk_det,
            "lag1_shot_correlation": lag1_corr(stream),
            "frozen_C1_benchmark": {4:408,6:4482,8:55589}[n]}

if __name__ == "__main__":
    # pull_fn is wired at run time (qiskit_ibm_runtime). This file is the FROZEN estimator posted
    # pre-reveal; running it after the reveal only ADDS the s_hat==true_P win/miss + ratio.
    print("Exp142c frozen estimator — P-BLIND. Wire pull_fn (qiskit_ibm_runtime) and call load_rung per n.")
    for n in (4,6,8):
        A,Bb,se,so,p0 = wald(n, 0.00308)
        print(f"  n={n}: Wald A={A:.2f} B={Bb:.2f} p0={p0:.4f} (q_n=0.00308 illustrative; live q_n per manifest)")
