#!/usr/bin/env python3
"""SPILLOVER BRANCH COVERAGE for the n=10 C1 walk sim — Elder C6575.

Companion to Whisper's exp142_p1_n10_c1walk_sim_whisper_c5013.py --equivalence.

WHY A SECOND GATE. Her equivalence gate runs at the production SHOTS_PER_BASIS=256, where a
candidate resolves inside its first covering basis with probability ~1-1e-30. The spillover slow
path therefore NEVER EXECUTES during that gate — so the gate validates the fast path and reports
PASS for the whole file. That is not a criticism of the gate's construction; it is a structural
property of testing at one parameter value.

It mattered: the slow path shipped with a real over-count (it registered consumed copies for every
unresolved candidate in the chunk, including candidates positioned AFTER the walk's accepting
candidate, which the frozen decoder never walks). Found by forcing the branch, fixed at
quantum@7cb6224. P_hat was always correct — only the COPY COUNT was wrong, which is exactly the
benchmark's deliverable.

WHAT THIS DOES. Shrinks shots/basis so spillover becomes the COMMON case, then demands the same
exact equality the production gate demands: identical fw_shots in -> identical
(P_hat, C1_distinct_copies) out, frozen vs vectorized.

Run it alongside --equivalence whenever the sim changes, and before any freeze that pins this code.
Generalises the rule earned twice in one day (C6575): a gate that runs at only one parameter value
covers only the branches that parameter reaches. Force the rare branch on purpose — it is free.

  python3 exp142_p1_c1walk_spillover_coverage_elder_c6575.py            # 3/4/8 shots per basis
  python3 exp142_p1_c1walk_spillover_coverage_elder_c6575.py --shots 4  # single setting
"""
import argparse, hashlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exp142_p1_n10_c1walk_sim_whisper_c5013 as SIM
from exp142_p1_c1_decoder_elder_c5003 import covering_decode, full_weight_bases

SEED = b"spillover-branch-coverage"
CASES = ((4, 12), (6, 4))


def run(shots_per_basis, verbose=True):
    orig_block, orig_spb = SIM._basis_block, SIM.SHOTS_PER_BASIS
    SIM.SHOTS_PER_BASIS = shots_per_basis
    # _basis_block's default arg was bound at def time, so patch the callable too
    SIM._basis_block = (lambda mh, d, b, P, n, shots=None, _k=shots_per_basis:
                        orig_block(mh, d, b, P, n, shots=_k))
    master = hashlib.sha256(SEED).hexdigest()
    ok_n = tot = 0
    try:
        for n, draws in CASES:
            for d in range(draws):
                P = SIM.draw_P(master, d, n)
                fw = {b: [list(map(int, r)) for r in SIM._basis_block(master, d, b, P, n)]
                      for b in full_weight_bases(n)}
                frozen = covering_decode(fw, n, SIM.ALPHA, 0.0)
                fast = SIM.vector_walk(master, d, n, P)
                ok = (frozen["P_hat"] == fast["P_hat"]
                      and frozen["C1_distinct_copies"] == fast["C1_distinct_copies"])
                ok_n += ok; tot += 1
                if not ok and verbose:
                    print(f"    MISMATCH n={n} draw={d} true={P} "
                          f"frozen=({frozen['P_hat']},{frozen['C1_distinct_copies']}) "
                          f"vector=({fast['P_hat']},{fast['C1_distinct_copies']})")
    finally:
        SIM._basis_block, SIM.SHOTS_PER_BASIS = orig_block, orig_spb
    return ok_n, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, default=None)
    a = ap.parse_args()
    settings = [a.shots] if a.shots else [8, 4, 3]
    all_ok = True
    print("SPILLOVER BRANCH COVERAGE — frozen vs vectorized at shots/basis where spillover is COMMON")
    for k in settings:
        ok, tot = run(k)
        all_ok &= (ok == tot)
        print(f"  shots/basis={k:>3}: {ok}/{tot} exact  {'PASS' if ok == tot else '*** FAIL ***'}")
    print(f"\nSPILLOVER COVERAGE: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
