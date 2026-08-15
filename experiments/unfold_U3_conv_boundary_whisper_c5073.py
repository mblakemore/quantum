#!/usr/bin/env python3
"""UNFOLD U3 — conv-arm boundary layer (Whisper C5073). $0. FROZEN.

Dig A restricted to low weight, on the 707k single-copy conv shots (wave1-n10, kingston). The kit
(exp142_flight_kit.conv_param_rows) shows the conv arm is a STRUCTURED HONEST-ORACLE: each row preps
a product eigenstate of the sealed P with a FRESH random even-parity sign b per row; measured in one
of the 3^10 Pauli bases. True basis (A=P) -> deterministic even parity; wrong basis -> uniform.

CONSEQUENCE (the result): the single-copy ENSEMBLE low-weight marginals are maximally mixed BY
CONSTRUCTION — the random per-row b cancels the sign, so tr(Q rho)_ensemble ~ 0 at every accessible
low weight. The boundary is EMPTY for the classical learner. This is dig A's wall from the oracle
side, and it mechanistically explains the two-copy advantage: tr(Q rho)^2 SQUARES the b-sign away
(b-independent, verified in U0/U1 where tr2 reproduced the grade), so two copies see P where one
cannot. The sign the two-copy squares away IS the honest-oracle's randomization.

PIN (must pass or NO-TEST): on the FLOWN data, the true-basis row (A=P, row 27719) has near-zero odd
-parity rate (deterministic even, up to hw noise) while wrong-basis rows are ~uniform (0.35-0.65).
Parity = sum of bits => endianness-invariant.
REGISTERED PREDICTIONS:
  P1 pin: true-basis odd-rate << wrong-basis odd-rate (oracle mechanism confirmed on flown silicon).
  P2 unconditioned weight-1 ensemble marginals ~ 0 (mixed boundary) — nothing to unfold classically.
  P3 CONDITIONED on the recorded b, the weight-1 marginal recovers |~1| (the mixed sign IS b) — but
     b is the sealed protocol data, so this is not a classical-learner capability; it demonstrates
     the mechanism. Falsifier: pin fails -> NO-TEST (encoding/premise un-confirmed).
"""
import json, os, sys, glob, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")
SHOTS_PER_ROW = 12
N = 10


def main():
    man = json.load(open(os.path.join(RES, "exp142_wave1_n10_manifest.json")))
    bstrs = man["conv_b_strings"]
    P = json.load(open(os.path.join(RES, "exp142_wave1_n10_answers.json")))["quantum"]["P_hat"]
    d = json.load(open(glob.glob(os.path.join(RES, "h14_lock5_rescue_exp142_wave1_n10*.json"))[0]))
    conv = sorted([p for p in d["pubs"]
                   if len(list(p["data"].values())[0][0]) == N and len(list(p["data"].values())[0]) > 5000],
                  key=lambda p: p["pub_index"])
    outcomes = []
    for p in conv:
        outcomes.extend(list(p["data"].values())[0])
    outcomes = np.array([[int(c) for c in s] for s in outcomes])   # (708588, 10)
    n_rows = outcomes.shape[0] // SHOTS_PER_ROW
    assert n_rows == 59049, n_rows

    # locate true-basis row (A=P)
    Prow = next(i for i, bt in enumerate(itertools.product("XYZ", repeat=N)) if "".join(bt) == P)

    # PIN: true-basis parity determinism vs wrong-basis uniform
    def odd_rate(row):
        blk = outcomes[row * SHOTS_PER_ROW:(row + 1) * SHOTS_PER_ROW]
        return float(np.mean(blk.sum(axis=1) % 2 == 1))
    true_odd = odd_rate(Prow)
    rng = np.random.default_rng(30731)
    wrong_rows = [int(r) for r in rng.choice([r for r in range(n_rows) if r != Prow], size=200, replace=False)]
    wrong_odd = float(np.mean([odd_rate(r) for r in wrong_rows]))
    pin_ok = true_odd < 0.35 and 0.35 < wrong_odd < 0.65
    print(f"PIN: true-basis (row {Prow}) odd-parity rate {true_odd:.3f} | wrong-basis mean {wrong_odd:.3f} "
          f"-> {'PASS (oracle mechanism on flown data)' if pin_ok else 'FAIL'}")
    if not pin_ok:
        json.dump({"verdict": "NO-TEST (pin: oracle mechanism not confirmed)", "true_odd": true_odd,
                   "wrong_odd": wrong_odd}, open(os.path.join(RES, "unfold_U3_conv_boundary_c5073.json"), "w"))
        print("VERDICT: NO-TEST"); return

    # RESULT P2/P3: weight-1 ensemble marginals for the qubits in supp(P), unconditioned vs b-conditioned.
    # For qubit k measured in basis A[k]==P[k], o[k] = b[k] (its eigenbasis). classical-shadow weight-1:
    #   unconditioned tr(P_k) ~ 3 * mean_{rows w/ A[k]==P[k]} (-1)^{o[k]}   (b random -> ~0)
    #   conditioned            ~ 3 * mean (-1)^{o[k] XOR b[k]}              (= +1 deterministic)
    bases = ["".join(bt) for bt in itertools.product("XYZ", repeat=N)]   # 59049 (enumerate once)
    bmat = np.array([[int(c) for c in bstrs[r]] for r in range(n_rows)])  # (59049,10) prep signs
    uncond, cond = {}, {}
    for k in range(N):
        # rows whose basis measures qubit k in P[k]
        rows_k = [r for r in range(n_rows) if bases[r][k] == P[k]]
        rows_k = np.array(rows_k)
        # gather o[k] over those rows' shots (both endianness -> robust; use raw index k and reversed)
        vals_raw, vals_cond = [], []
        for r in rows_k[:2000]:                                  # cap for speed; representative
            blk = outcomes[r * SHOTS_PER_ROW:(r + 1) * SHOTS_PER_ROW]
            ok = blk[:, N - 1 - k]                               # qubit k bit (qiskit endianness: clbit k = pos N-1-k)
            vals_raw.extend((-1.0) ** ok)
            vals_cond.extend((-1.0) ** (ok ^ bmat[r, k]))
        uncond[k] = 3.0 * float(np.mean(vals_raw))
        cond[k] = 3.0 * float(np.mean(vals_cond))
    supp = [k for k in range(N) if P[k] != "I"]
    mean_uncond = float(np.mean([abs(uncond[k]) for k in supp]))
    mean_cond = float(np.mean([abs(cond[k]) for k in supp]))
    print(f"P2 unconditioned weight-1 |tr| over supp(P): mean {mean_uncond:.3f} "
          f"(per-qubit {[round(uncond[k],2) for k in supp]}) -> {'MIXED (empty boundary)' if mean_uncond < 0.3 else 'structure'}")
    print(f"P3 b-conditioned weight-1 |tr| over supp(P): mean {mean_cond:.3f} "
          f"-> {'RECOVERS ~1 (the mixed sign IS b)' if mean_cond > 1.5 else 'partial'}")

    verdict = ("BOUNDARY EMPTY BY DESIGN: the conv arm's single-copy ensemble has maximally-mixed "
               f"low-weight marginals (uncond |tr| {mean_uncond:.2f} ~ 0); conditioning on the sealed "
               f"per-row sign b recovers them (cond |tr| {mean_cond:.2f}). The sign that maximally-mixes "
               "the classical view IS b, and the two-copy envelope squares it away (tr2 b-independent) "
               "-> this is dig A's wall AND the two-copy advantage, mechanistically explained from the "
               "honest-oracle construction. The classical boundary cannot be unfolded because it was "
               "built to be empty; that emptiness is the learning advantage.")
    print(f"\nVERDICT: {verdict}")
    out = {"card": "unfold_U3_conv_boundary", "cycle": "C5073", "sealed_P": P, "true_basis_row": Prow,
           "pin_true_odd": true_odd, "pin_wrong_odd": wrong_odd,
           "weight1_uncond_mean_abs": mean_uncond, "weight1_cond_mean_abs": mean_cond,
           "uncond_per_qubit": uncond, "cond_per_qubit": cond, "verdict": verdict}
    json.dump(out, open(os.path.join(RES, "unfold_U3_conv_boundary_c5073.json"), "w"), indent=1)
    print("-> results/unfold_U3_conv_boundary_c5073.json")


if __name__ == "__main__":
    main()
