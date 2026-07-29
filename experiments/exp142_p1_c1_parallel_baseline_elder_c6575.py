#!/usr/bin/env python3
"""IS OUR CLASSICAL BASELINE WEAK? — parallel-ML C1 decoder vs the committed sequential walk.

Elder C6575, in response to Whisper's n=10 hybrid proposal (general#2357).

THE CHALLENGE TO OUR OWN NUMBER. The proposal argues a noiseless simulated C1 is "the strongest
possible classical competitor, so the margin is a floor". That is true WITHIN our frozen algorithm
and false in general — and my C6575 walk-position decomposition is what makes the difference
matter: the committed C1 meter costs ~2 copies per CANDIDATE WALKED, i.e. it is essentially LINEAR
SEARCH over 4^n-1 candidates. A margin measured against linear search is an advantage over OUR
classical algorithm, not over the best-known one. (My own C6566 rule: the baseline choice IS the
claim; run the hypothesised attack before announcing.)

THE ALTERNATIVE, and it needs no new data. The sequential walk consumes fresh copies per candidate
it eliminates. But every covering measurement is informative about EVERY candidate it covers
simultaneously — so a PARALLEL decoder scores all 4^n-1 candidates against the SAME copies and
takes the argmax, exactly as the Q arm already does over its Bell samples. If that identifies P
from far fewer copies, our published C1 is not the best-known classical cost and the margin is
overstated.

This is deliberately an attack on our own headline. A negative result (parallel needs comparably
many copies) strengthens the claim; a positive result shrinks it. Either is publishable.

Reuses the FROZEN emission convention (full_weight_bases order, basis = row//c_per_basis, support
parity over P's support only). No QPU.
"""
import json, math, os, sys, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import numpy as np
from exp142_p1_c1_decoder_elder_c5003 import full_weight_bases, candidates

RES = os.path.join(HERE, "..", "results")
TRUE_P = "IZYXZXZZ"
N, C_PER_BASIS = 8, 64
LET = {"X": 0, "Y": 1, "Z": 2}


def load_rows():
    """Rebuild the n=8 flown C1 rows from the cached decode artifact if present, else refetch."""
    cache = os.path.join(RES, "cache", "n8_c1_rows.npz")
    if os.path.exists(cache):
        z = np.load(cache); return z["bits"], z["basis"]
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(RES, "exp142_p1_n8_c1_refly_manifest_ALT.json")))
    svc = _get_ibm_service()
    jobs = sorted([j for j in man["jobs"] if j["kind"] == "c1_covering"], key=lambda j: j["batch"])
    rows = []
    for j in jobs:
        res = svc.job(j["job_id"]).result()
        for pi in range(len(res)):
            r = res[pi]; reg = list(r.data.keys())[0] if hasattr(r.data, "keys") else "c"
            for s in getattr(r.data, reg).get_bitstrings():
                rows.append([int(x) for x in s.replace(" ", "")[::-1]])
        print(f"  fetched batch {j['batch']} ({len(rows)} rows)", flush=True)
    bits = np.array(rows, dtype=np.int8)
    fwb = full_weight_bases(N)
    basis = np.array([[LET[c] for c in fwb[i // C_PER_BASIS]] for i in range(len(bits))], dtype=np.int8)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    np.savez_compressed(cache, bits=bits, basis=basis)
    return bits, basis


def parallel_argmax(bits, basis, idx, cands, sup, let, alpha=0.95, q=0.004883):
    """Score EVERY candidate on the SAME subsample idx; return (best_P_index, llrs, rates).

    *** SCORED BY LOG-LIKELIHOOD RATIO, NOT RAW RATE. *** This is load-bearing and my first
    implementation got it wrong in the flattering direction, so it is worth stating why.

    A candidate of weight w is covered by 3^(n-w) of the 3^n bases, so in a uniform subsample of m
    copies it receives only ~m/3^w covered rows. That is a 3^(w2-w1) spread across candidates: at
    m=16384 a weight-4 candidate gets ~200 rows while the weight-7 truth gets ~7. Comparing RAW
    RATES across such unequal samples is meaningless — a spurious 1.0 from 3 rows outranks a
    genuine 0.97 from 3000, which is exactly what happened (argmax pinned to low-weight candidates,
    top-margin identically 0.0000 because dozens tied at 1.0).

    The LLR is the correct shared-budget statistic: it is the SAME per-candidate weight-dependent
    p0 the frozen SPRT uses, simply accumulated in parallel over a common budget instead of
    sequentially, so evidence scales with the number of covering rows automatically.
    """
    B, X = basis[idx], bits[idx]
    llrs = np.full(len(cands), -np.inf)
    rates = np.full(len(cands), 0.5)
    for k in range(len(cands)):
        S, L = sup[k], let[k]
        cov = np.ones(len(idx), dtype=bool)
        for pos, l in zip(S, L):
            cov &= (B[:, pos] == l)
        nc = int(cov.sum())
        if nc == 0:
            llrs[k] = 0.0; continue
        par = X[cov][:, S].sum(axis=1) & 1
        n_even = int((par == 0).sum())
        w = len(S)
        pf = (1 - (1 - 2 * q) ** w) / 2                       # frozen p_flip
        e = (1 + alpha) / 2
        p0 = e * (1 - pf) + (1 - e) * pf                      # frozen p0_of
        llrs[k] = n_even * math.log(p0 / 0.5) + (nc - n_even) * math.log((1 - p0) / 0.5)
        rates[k] = n_even / nc
    return int(np.argmax(llrs)), llrs, rates


def main():
    print("loading n=8 flown C1 rows...", flush=True)
    bits, basis = load_rows()
    print(f"  {len(bits)} rows", flush=True)

    cands = candidates(N)
    sup = [np.array([i for i, c in enumerate(P) if c != "I"]) for P in cands]
    let = [np.array([LET[c] for c in P if c != "I"]) for P in cands]
    true_k = cands.index(TRUE_P)

    committed = json.load(open(os.path.join(RES, "exp142_p1_c1_n8_decode_elder_c6575.json")))
    seq_copies = committed["result"]["C1_distinct_copies"]
    print(f"\ncommitted SEQUENTIAL walk: {seq_copies:,} copies (P_hat {committed['P_hat_C1']})")
    print(f"theorem distinguish floor Omega(2^n) = {2**N:,} copies\n")

    rng = np.random.default_rng(6575)
    print(f"{'copies m':>9} | {'argmax':>10} | {'correct':>7} | {'LLR margin':>13} | "
          f"{'true-P LLR':>10} | {'>=A':>5}")
    print("-" * 78)
    results = []
    first_ok = None
    for m in (256, 512, 1024, 2048, 4096, 8192, 16384):
        if m > len(bits): break
        idx = rng.choice(len(bits), size=m, replace=False)
        bk, llrs, rates = parallel_argmax(bits, basis, idx, cands, sup, let)
        srt = np.sort(llrs)[::-1]
        ok = (bk == true_k)
        A = math.log((4**N - 1) / 0.01)
        print(f"{m:>9,} | {cands[bk]:>10} | {str(ok):>7} | {srt[0]-srt[1]:>13.2f} | "
              f"{llrs[true_k]:>10.2f} | {'yes' if llrs[true_k] >= A else 'no':>5}")
        results.append({"m": m, "argmax": cands[bk], "correct": bool(ok),
                        "top_llr": float(srt[0]), "runner_llr": float(srt[1]),
                        "llr_margin": float(srt[0] - srt[1]),
                        "true_P_llr": float(llrs[true_k]), "wald_A": A,
                        "true_P_clears_A": bool(llrs[true_k] >= A)})
        if ok and first_ok is None:
            first_ok = m

    print("-" * 78)
    if first_ok:
        ratio = seq_copies / first_ok
        print(f"\nPARALLEL decoder identifies P from ~{first_ok:,} copies "
              f"vs the committed walk's {seq_copies:,} = {ratio:.1f}x CHEAPER")
        print(f"  => the published n=8 C1 cost is NOT the best-known classical cost.")
        print(f"  => margin 218.3x (as-flown) would fall to ~{first_ok/118:.1f}x on this baseline "
              f"(Q = 118 copies).")
        print(f"  NOTE: first_ok is a coarse grid point + ONE subsample draw — an upper bound on the "
              f"parallel decoder's true cost, so the real margin is if anything SMALLER still.")
    else:
        print("\nPARALLEL decoder did NOT identify P within the swept budget — the committed "
              "sequential walk is not obviously beatable this way, which STRENGTHENS the published "
              "margin. Report as a negative result.")

    out = os.path.join(RES, "exp142_p1_c1_parallel_baseline_elder_c6575.json")
    json.dump({"n": N, "true_P": TRUE_P, "sequential_walk_copies": seq_copies,
               "theorem_floor_2n": 2**N, "sweep": results,
               "parallel_first_correct_m": first_ok,
               "speedup_vs_committed_walk": (seq_copies / first_ok) if first_ok else None,
               "implication": ("published C1 is NOT best-known classical; margin overstated"
                               if first_ok else
                               "committed walk not beaten by parallel scoring in swept range"),
               "caveat": "coarse grid, single subsample draw per m, one sealed P. Establishes an "
                         "UPPER bound on the parallel decoder's cost, hence a bound on how much the "
                         "margin shrinks — not a precise replacement number.",
               "context": "raised against Whisper's n=10 hybrid proposal general#2357 rationale (3): "
                          "'noiseless simulated C1 = strongest possible classical competitor' holds "
                          "only WITHIN the frozen algorithm."},
              open(out, "w"), indent=1)
    print(f"\nSAVED {out}")


if __name__ == "__main__":
    main()
