#!/usr/bin/env python3
"""Exp-HSS RED-TEAM CO-VERIFY — Elder (classical-arm Grader seat), C6566.

Independent verification of Whisper C4996 white-box break of the Race-6 runtime win.
INDEPENDENCE: the attack below is implemented from Elder's OWN algebra derivation
(re-derived from f(x,y) = (-1)^(x.y XOR g(x)) before reading Whisper's extraction
formulas), shares ONLY the instance construction (make_g_spec from the original
generator — necessarily identical, it defines the problem) and queries an oracle
built by Elder. Fresh-instance robustness uses Elder-chosen seeds disjoint from
Whisper's.

Elder derivation (independent):
  f_s(x,y) = f(x^sx, y^sy) has, for FIXED x, the form  <x^sx, y> ^ c(x)   (linear in y),
    slope  = x ^ sx                      -> query x=0: slope(0) = sx      [k+1 queries]
  residual c(x) = f_s(x,0) = g(x^sx) ^ (x^sx).sy
    with sx known and g white-box:  f_s(sx^e_i, 0) = g(e_i) ^ e_i.sy = g(e_i) ^ sy_i
    -> sy_i = f_s(sx^e_i, 0) ^ g(e_i)                                   [k queries]
  Total 2k+1 = 41 oracle queries for n=2k=40. (Elder's sy route queries at x=sx^e_i,
  a DIFFERENT query set from Whisper's x=e_i route — same algebra family, independent
  implementation; both O(k).)

Grading question: does the classical attack recover the SEALED race-6 s exactly, in
time << 1,818 s (frozen classical floor) and << 3.82 s (quantum wall)? If yes, F121's
runtime-advantage claim is superseded per its own printed supersedable-by-design fence.
"""
import time, json, hashlib, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from exp_hss_generator import make_g_spec

K, N_CCZ = 20, 10
SEED_RACE = 2026072306
S_STR = "0101010111110000100110110100011000000011"
SALT = "e9634e6c3f67a4d228f8a6d4e3392aa5"
COMMIT = "e3839fc5b937a3b4df36442701c66e95647524fee69b5b5c990e42559f811a6c"


def g_eval(xb, gs):
    v = 0
    for i in gs["z"]:
        v ^= xb[i]
    for a, b in gs["cz"]:
        v ^= xb[a] & xb[b]
    for a, b, c in gs["ccz"]:
        v ^= xb[a] & xb[b] & xb[c]
    return v & 1


def make_fs_oracle(sx, sy, gs, counter):
    """f_s(x,y) as a bit in {0,1}: bit = (x^sx).(y^sy) ^ g(x^sx). Counts queries."""
    def fs(x, y):
        counter[0] += 1
        xs = x ^ sx
        ys = y ^ sy
        return (int(np.dot(xs, ys)) & 1) ^ g_eval(xs, gs)
    return fs


def elder_attack(fs, gs, k):
    """Elder's independent white-box attack. Returns recovered (sx, sy)."""
    zero = np.zeros(k, dtype=np.int64)
    base = fs(zero, zero)                      # c(0) = g(sx) ^ sx.sy
    sx = np.zeros(k, dtype=np.int64)
    for i in range(k):                         # slope at x=0 -> sx
        e = zero.copy(); e[i] = 1
        sx[i] = fs(zero, e) ^ base             # (0^sx).e_i = sx_i
    sy = np.zeros(k, dtype=np.int64)
    for i in range(k):                         # Elder route: query at x = sx^e_i
        e = zero.copy(); e[i] = 1
        gi = g_eval(e, gs)                     # g at e_i (white-box)
        sy[i] = fs(sx ^ e, zero) ^ gi          # = g(e_i)^e_i.sy ^ g(e_i) = sy_i
    return sx, sy


def run_instance(gs, sx_true, sy_true):
    counter = [0]
    fs = make_fs_oracle(sx_true, sy_true, gs, counter)
    t0 = time.perf_counter()
    sx, sy = elder_attack(fs, gs, K)
    wall = time.perf_counter() - t0
    exact = bool(np.array_equal(sx, sx_true) and np.array_equal(sy, sy_true))
    return exact, counter[0], wall, sx, sy


def main():
    # 0) seal identity re-check
    assert hashlib.sha256((S_STR + SALT).encode()).hexdigest() == COMMIT, "seal mismatch"

    # 1) the sealed race-6 instance
    gs = make_g_spec(K, N_CCZ, SEED_RACE)
    s_bits = np.array([int(c) for c in S_STR], dtype=np.int64)
    sx_t, sy_t = s_bits[:K], s_bits[K:]
    exact, q, wall, sx, sy = run_instance(gs, sx_t, sy_t)
    rec = "".join(map(str, list(sx) + list(sy)))

    # 2) fresh-instance robustness, Elder seeds (disjoint from Whisper's RNG stream)
    rng = np.random.default_rng(65660723)
    trials, hits, qs = 100, 0, []
    for t in range(trials):
        gs_t = make_g_spec(K, N_CCZ, int(rng.integers(1, 2**31)))
        s_t = rng.integers(0, 2, size=2 * K)
        ok, qt, _, _, _ = run_instance(gs_t, s_t[:K].astype(np.int64), s_t[K:].astype(np.int64))
        hits += ok; qs.append(qt)

    out = {
        "card": "exp_hss_redteam_coverify — Elder C6566 (classical-arm Grader seat)",
        "independence": "own algebra derivation; own attack code; sy route queries x=sx^e_i (differs from Whisper's x=e_i route); Elder-seeded fresh instances",
        "race6": {
            "seal_recheck": "sha256(s_str+salt) == commitment PASS",
            "exact_match": exact, "recovered": rec, "sealed": S_STR,
            "oracle_queries": q, "wall_s": wall,
            "speedup_vs_1818s_floor": 1818.0 / wall,
            "speedup_vs_3.82s_quantum_wall": 3.82 / wall,
        },
        "fresh_instances_elder_seeds": {"trials": trials, "exact": hits, "queries": {"min": min(qs), "max": max(qs)}},
        "verdict": None,
        "substrate": "claude-fable-5",
    }
    out["verdict"] = ("CONFIRMED — white-box classical attack recovers the sealed Race-6 answer exactly in O(k) queries; "
                      "F121 runtime-advantage claim SUPERSEDED per its own printed fence"
                      if exact and hits == trials else "NOT CONFIRMED — see fields")
    print(json.dumps(out, indent=1))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                           "exp_hss_redteam_coverify_elder_c6566.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
