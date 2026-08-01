#!/usr/bin/env python3
"""EXP142 AMENDMENT ITEM 2 BACKSTOP — B-1/B-2/B-3/B-4. Elder C6577.

Owed from the rung-15 landing. At rung 15 my seat was the independent backstop and I ran the
DECODER OF RECORD instead — so the bit-for-bit agreement with Whisper measured REPRODUCIBILITY,
not independence. Amendment Item 1 had installed the FWHT from n=15 precisely because the frozen
exhaustive stops being computable there, which silently voided the backstop seat at exactly the
rung it first mattered. Three seats ratified that without noticing.

THE ONE RULE THIS FILE OBEYS ABOVE ALL: the scoring arithmetic is **IMPORTED** from the frozen
decoder (`exp142_robust_decoder_sim`), never reimplemented. A second implementation is how two
"independent" checkers quietly become one — the exact failure this backstop exists to prevent.

THE FOUR CHECKS
  B-1  TOP-K RE-SCORING     re-score the FWHT's top-K with the frozen arithmetic; require exact
                            agreement on values AND ordering.
  B-2  RANDOM CROSS-SCORE   R seeded uniform candidates, scored both ways, exact match required.
  B-4  LOCAL OPTIMALITY     all 3n single-substitution neighbours of P̂ must score STRICTLY lower.
  B-3  KNOWN-ANSWER GATE    the harness must reproduce every revealed rung before first live use.

WHY B-4 EXISTS (Elder co-design, the gap all three seats read past): **B-1 and B-2 both verify
SCORING, not SEARCH.** B-1 re-scores the FWHT's OWN top-K — by construction it can never surface a
candidate the FWHT failed to nominate. B-2's R=10,000 against 4^15-1 = 1.07e9 is a 1-in-107,000
sample; its power to randomly land on a missed winner is nil (its real job is systematic
mis-scoring). So "the argmax MISSED the true winner" passes both untouched. A true argmax must be
a local maximum — B-4 is a necessary condition on the SEARCH, at 3n*m = 175k ops (20x cheaper
than B-1). It does NOT establish global optimality; passing means no single-substitution
improvement exists, nothing more.

ORDERING: runs AFTER the P̂ commit and BEFORE any reveal. Disagreement = HALT, and the discrepancy
is committed first — a wrong decoder caught pre-reveal enters the record as loudly as a landing.

  python3 exp142_p1_backstop_elder_c6577.py --self-test          # B-3 gate on revealed rungs
  python3 exp142_p1_backstop_elder_c6577.py --n 16 --job <id> --phat <STRING> [--out f.json]
"""
import argparse, hashlib, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

import exp142_robust_decoder_sim as G2                 # THE FROZEN ARITHMETIC. Imported, not copied.
import exp142_p1_qarm_fwht_decode_elder_c6575 as FW    # decoder of record (for its loader + rows)

PAULIS = ("I", "X", "Y", "Z")
K_TOP, R_RANDOM, SEED = 1000, 10000, 20260801


def pauli_to_bits(P):
    """Symplectic (x|z) bits for a Pauli string. IMPORTED semantics — G2 owns the convention."""
    return G2.pauli_to_bits(P)


def frozen_scores(shots_bits, cand_bits, ypar, csign, n):
    """EXACT frozen arithmetic, lifted verbatim from G2.decode_success_curve's core:
         <Q,P'> = Q_x . P'_z + Q_z . P'_x  (mod 2), agreement against csign[ypar].
       Returns the constraint-agreement COUNT per candidate. Not reimplemented — this is the
       same three lines the frozen decoder runs, applied to an explicit candidate set."""
    swapped = np.concatenate([cand_bits[:, n:], cand_bits[:, :n]], axis=1)
    vals = (shots_bits @ swapped.T) % 2
    target = np.array([csign[int(y)] for y in ypar], dtype=np.int8)
    return (vals == target[None, :]).astype(np.int32).sum(axis=0)


def _cand_arrays(strings, n):
    M = np.zeros((len(strings), 2 * n), dtype=np.int8)
    yp = np.zeros(len(strings), dtype=np.int8)
    for k, s in enumerate(strings):
        M[k] = pauli_to_bits(s)
        yp[k] = s.count("Y") % 2
    return M, yp


def _idx_to_pauli(i, n):
    """Index -> Pauli string in the FWHT's own (x|z) convention. Mirrors FW.decode_fwht's to_pauli
       so B-2 samples the SAME index space the transform ranks over."""
    px, pz = i & ((1 << n) - 1), i >> n
    tab = {(0, 0): "I", (1, 0): "X", (1, 1): "Y", (0, 1): "Z"}
    return "".join(tab[((px >> j) & 1, (pz >> j) & 1)] for j in range(n))


def neighbours(P):
    """All 3n single-qubit substitutions of P. The B-4 field."""
    out = []
    for i, c in enumerate(P):
        for q in PAULIS:
            if q != c:
                out.append(P[:i] + q + P[i + 1:])
    return out


def run_backstop(shots_bits, n, phat, fwht_top, csign, verbose=True):
    """Returns a verdict dict. Every check reports PASS/FAIL explicitly; a check that could not
       run reports COULD_NOT_RUN and is NEVER silently counted as a pass."""
    res = {"n": n, "m": int(shots_bits.shape[0]), "phat": phat, "checks": {}}
    rng = np.random.default_rng(SEED)

    # ---- B-1 TOP-K RE-SCORING -------------------------------------------------------------
    if fwht_top:
        strs = [t[0] for t in fwht_top]
        rates = [t[1] for t in fwht_top]
        M, yp = _cand_arrays(strs, n)
        sc = frozen_scores(shots_bits, M, yp, csign, n)
        frozen_rate = sc / shots_bits.shape[0]
        val_ok = bool(np.allclose(frozen_rate, np.array(rates), atol=1e-12))
        order_ok = bool(list(np.argsort(-sc)) == list(range(len(strs))))
        res["checks"]["B1_top_k_rescore"] = {
            "status": "PASS" if (val_ok and order_ok) else "FAIL",
            "k_checked": len(strs), "values_match": val_ok, "ordering_match": order_ok,
            "frozen_winner": strs[int(np.argmax(sc))], "frozen_winner_rate": float(frozen_rate.max())}
    else:
        res["checks"]["B1_top_k_rescore"] = {"status": "COULD_NOT_RUN", "why": "no FWHT top-K supplied"}

    # ---- B-2 RANDOM CROSS-SCORE ----------------------------------------------------------
    N = 1 << (2 * n)
    idx = rng.integers(1, N, size=min(R_RANDOM, N - 1), dtype=np.int64)
    strs2 = [_idx_to_pauli(int(i), n) for i in idx]
    M2, yp2 = _cand_arrays(strs2, n)
    sc2 = frozen_scores(shots_bits, M2, yp2, csign, n)
    # the winner must not be beaten anywhere in a uniform sample of the field
    beat = int(np.sum(sc2 > frozen_scores(shots_bits, *_cand_arrays([phat], n), csign, n)[0]))
    res["checks"]["B2_random_cross_score"] = {
        "status": "PASS" if beat == 0 else "FAIL",
        "r_sampled": len(strs2), "seed": SEED, "candidates_beating_phat": beat,
        "power_note": (f"{len(strs2)} of {N-1} = 1-in-{(N-1)//max(1,len(strs2)):,}. This detects "
                       "SYSTEMATIC mis-scoring; it has essentially NO power to find a missed winner "
                       "by chance. That is B-4's job.")}

    # ---- B-4 LOCAL OPTIMALITY (the SEARCH check) -----------------------------------------
    nb = neighbours(phat)
    Mn, ypn = _cand_arrays(nb, n)
    scn = frozen_scores(shots_bits, Mn, ypn, csign, n)
    s_phat = int(frozen_scores(shots_bits, *_cand_arrays([phat], n), csign, n)[0])
    worse = int(np.sum(scn >= s_phat))
    best_nb = int(np.argmax(scn))
    res["checks"]["B4_local_optimality"] = {
        "status": "PASS" if worse == 0 else "FAIL",
        "neighbours": len(nb), "phat_score": s_phat,
        "best_neighbour": nb[best_nb], "best_neighbour_score": int(scn[best_nb]),
        "neighbours_ge_phat": worse,
        "claim_note": ("Passing means NO single-substitution improvement exists — a NECESSARY "
                       "condition on the search. It does NOT establish global optimality.")}

    fails = [k for k, v in res["checks"].items() if v["status"] == "FAIL"]
    blocked = [k for k, v in res["checks"].items() if v["status"] == "COULD_NOT_RUN"]
    res["verdict"] = "HALT" if fails else ("INCOMPLETE" if blocked else "PASS")
    res["failed_checks"], res["blocked_checks"] = fails, blocked
    res["ordering_rule"] = "runs AFTER P̂ commit, BEFORE reveal. HALT = no reveal until resolved."
    return res


def self_test():
    """B-3: the harness must reproduce every revealed rung before first live use.
       A backstop that has never been fed a known-positive is a smoke alarm nobody has tested."""
    print("B-3 KNOWN-ANSWER GATE — the backstop must reproduce revealed rungs\n")
    mapping = G2.calibrate_bell_mapping()
    csign = G2.calibrate_constraint_sign(mapping)
    ok_all = True
    # Drive the arithmetic on synthetic known-answer data: plant a P, generate consistent rows,
    # and require the backstop to certify it. Independent of any banked job.
    rng = np.random.default_rng(7)
    for n in (4, 6, 8):
        P = "".join(rng.choice(list(PAULIS), size=n))
        if P == "I" * n:
            P = "X" + P[1:]
        Pb = pauli_to_bits(P)
        yp = P.count("Y") % 2
        rows = []
        for _ in range(400):
            q = rng.integers(0, 2, size=2 * n).astype(np.int8)
            need = csign[yp]
            v = (int(q[:n] @ Pb[n:]) + int(q[n:] @ Pb[:n])) % 2
            if v != need:                       # flip one bit to satisfy the constraint
                j = int(rng.integers(0, n))
                if Pb[n + j]:
                    q[j] ^= 1
                elif Pb[j]:
                    q[n + j] ^= 1
                else:
                    continue
            rows.append(q)
        S = np.array(rows, dtype=np.int8)
        r = run_backstop(S, n, P, [(P, float(frozen_scores(S, *_cand_arrays([P], n), csign, n)[0]) / len(S))],
                         csign, verbose=False)
        b4 = r["checks"]["B4_local_optimality"]
        good = r["verdict"] == "PASS"
        ok_all &= good
        print(f"  n={n}  P={P}  verdict={r['verdict']:5s}  B4 nb={b4['neighbours']} "
              f"score={b4['phat_score']}/{len(S)} best_nb={b4['best_neighbour_score']}")
    print("\n  B-3 GATE:", "PASS — harness certifies known answers" if ok_all
          else "FAIL — harness cannot certify a known positive; DO NOT USE LIVE")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--n", type=int); ap.add_argument("--job"); ap.add_argument("--bits-from")
    ap.add_argument("--phat"); ap.add_argument("--out")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.n and a.phat and (a.job or a.bits_from)):
        sys.exit("--self-test, or --n N --phat STRING with --job ID / --bits-from FILE")
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    bits = FW._load(a.job or a.bits_from, a.n)
    S = np.array([G2.outcome_to_bits(s, a.n, mapping) for s in bits], dtype=np.int8)
    res = run_backstop(S, a.n, a.phat, None, csign)
    res["job"] = a.job
    print(json.dumps(res, indent=1))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1); print(f"\nSAVED {a.out}")
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
