#!/usr/bin/env python3
"""Exp-HSS RED-TEAM — white-box classical attack on the Race-6 winning instance (Whisper C4996).

Pre-flight for the IBM Quantum Advantage Tracker (Creator directive, C4995). The C4990 fence named
the untested threat: the 476x runtime win is priced against best-known-fielded-SIMULATION of the
circuit, but the hidden shift is COMPILED INTO the MM circuit and MM bent functions are not believed
classically hard white-box. A challenger who attacks the PROBLEM's algebra rather than simulating the
circuit could retire the number. This file fires that attack at our OWN race-6 instance and grades it
like a hostile tracker challenger — result booked either way (honest-negatives rule, C4925).

THE ATTACK (linear-structure / defining-MM-property):
  f(x,y) = (-1)^(x.y XOR g(x)),  x,y in F2^k  (n=2k).  The DEFINING MM property: for each fixed x,
  f(x,.) is a LINEAR character in y with slope x. Under a hidden shift s=(s_x,s_y):
      f_s(x,y) = f(x+s_x, y+s_y) = (-1)^(g(x+s_x) XOR (x+s_x).s_y) * (-1)^((x+s_x).y)
  so f_s(x,.) is ALSO linear in y with slope (x+s_x). That slope LEAKS s_x directly, from oracle
  queries alone; the residual sign leaks s_y once g is known (white-box). No 2^40 Fourier transform,
  no circuit simulation. Cost O(k) oracle evaluations + O(k) work.

  s_x:  slope of f_s(0,.) in y  =  s_x           (read via f_s(0,e_i) vs f_s(0,0), k queries)
  s_y[i] = g(s_x) XOR g(s_x+e_i) XOR bit(f_s(0,0)) XOR bit(f_s(e_i,0))   (k more queries)

If this returns the sealed 40-bit s in << 1,818 s, the runtime advantage is SUPERSEDED white-box.

Faithful to experiments/exp_hss_generator.py: same make_g_spec, same f. Substrate claude-fable-5.
"""
import time, json, hashlib
import numpy as np
from exp_hss_generator import make_g_spec

SEED = 2026072306          # from exp_hss_race6_flight.py
K = 20                     # n=40
N_CCZ = 10                 # race_n40: make_g_spec(20, 10, SEED)
S_STR = "0101010111110000100110110100011000000011"   # revealed sealed answer (Ember, verifies vs 7e23d35)
SALT  = "e9634e6c3f67a4d228f8a6d4e3392aa5"
COMMIT = "e3839fc5b937a3b4df36442701c66e95647524fee69b5b5c990e42559f811a6c"


def g_eval(x_bits, g_spec):
    """g(x) in {0,1} from the {Z,CZ,CCZ} monomials — exactly the phase apply_g_phase installs."""
    v = 0
    for i in g_spec["z"]:
        v ^= x_bits[i]
    for a, b in g_spec["cz"]:
        v ^= x_bits[a] & x_bits[b]
    for a, b, c in g_spec["ccz"]:
        v ^= x_bits[a] & x_bits[b] & x_bits[c]
    return v & 1


def f_eval(x, y, g_spec):
    """f(x,y) = (-1)^(x.y XOR g(x))  as a bit in {0,1} (0 -> +1, 1 -> -1)."""
    xy = int(np.dot(x, y)) & 1
    return xy ^ g_eval(x, g_spec)


def make_oracle_fs(s_x, s_y, g_spec):
    """Return f_s(x,y) = f(x+s_x, y+s_y) as a callable — the ONLY thing the challenger queries.
    (The challenger never sees s; it is baked into the shifted oracle, exactly as the sealed
    problem presents it.)"""
    def fs(x, y):
        return f_eval((x ^ s_x) & 1, (y ^ s_y) & 1, g_spec)
    return fs


def whitebox_attack(fs, g_spec, k):
    """Recover s=(s_x,s_y) from oracle fs and known g. O(k) queries. Returns (s_x, s_y, n_queries)."""
    q = 0
    e = [np.zeros(k, dtype=np.int8) for _ in range(k)]
    for i in range(k):
        e[i][i] = 1
    zero = np.zeros(k, dtype=np.int8)

    # --- s_x: slope of f_s(0, .) in y ---
    base_y = fs(zero, zero); q += 1
    s_x = np.zeros(k, dtype=np.int8)
    for i in range(k):
        s_x[i] = fs(zero, e[i]) ^ base_y; q += 1      # (-1)^((s_x)_i) flip => bit

    # --- s_y[i] = g(s_x) XOR g(s_x+e_i) XOR bit(f_s(0,0)) XOR bit(f_s(e_i,0)) ---
    base_x = fs(zero, zero); q += 1
    g_sx = g_eval(s_x, g_spec)
    s_y = np.zeros(k, dtype=np.int8)
    for i in range(k):
        fx = fs(e[i], zero); q += 1
        s_y[i] = g_sx ^ g_eval((s_x ^ e[i]) & 1, g_spec) ^ base_x ^ fx
    return s_x, s_y, q


def main():
    print("=" * 74)
    print("RED-TEAM: white-box classical attack on the RACE-6 winning instance")
    print("  MM hidden shift, n=40 (k=20), n_ccz=10, seed", SEED)
    print("=" * 74)

    # reconstruct the EXACT race-6 instance
    g_spec = make_g_spec(K, N_CCZ, SEED)
    s_bits = np.array([int(c) for c in S_STR], dtype=np.int8)   # convention: s_str[i] -> logical qubit i
    s_x_true, s_y_true = s_bits[:K].copy(), s_bits[K:].copy()   # x-reg 0..k-1, y-reg k..2k-1

    # sanity: our f matches the planted circuit's commitment target
    assert hashlib.sha256((S_STR + SALT).encode()).hexdigest() == COMMIT, "commitment mismatch"
    print("sealed-commitment verified: sha256(s+salt) ==", COMMIT[:16], "...")
    print("g_spec:", len(g_spec["ccz"]), "CCZ,", len(g_spec["cz"]), "CZ,", len(g_spec["z"]), "Z terms")

    fs = make_oracle_fs(s_x_true, s_y_true, g_spec)

    t0 = time.perf_counter()
    s_x, s_y, nq = whitebox_attack(fs, g_spec, K)
    dt = time.perf_counter() - t0

    s_hat_bits = np.concatenate([s_x, s_y])
    s_hat_str = "".join(str(int(b)) for b in s_hat_bits)
    exact = (s_hat_str == S_STR)
    hd = int(np.sum(s_hat_bits != s_bits))

    print("-" * 74)
    print("planted  s :", S_STR)
    print("recovered ŝ:", s_hat_str)
    print(f"Hamming distance: {hd}   EXACT MATCH: {exact}")
    print(f"oracle queries: {nq}    wall time: {dt*1e6:.1f} µs  ({dt:.9f} s)")
    print("-" * 74)
    print("GRADE (as a hostile tracker challenger would):")
    q_wall = 3.82
    c_floor = 1818.0
    print(f"  quantum wall (race-6, kingston):   {q_wall} s")
    print(f"  classical FLOOR the win beat:      {c_floor} s (edge_4500x stress)")
    print(f"  THIS classical attack:             {dt:.9f} s  ({dt*1e6:.1f} µs)")
    if exact:
        print(f"  => classical attack is ~{c_floor/dt:.3e}x FASTER than the frozen floor,")
        print(f"     and ~{q_wall/dt:.3e}x faster than the quantum wall.")
        print("  VERDICT: the white-box runtime advantage is SUPERSEDED. The number is retired.")
    else:
        print("  VERDICT: attack did NOT recover s — the white-box path does not trivially break this.")

    # --- robustness: is race-6 a fluke? attack random planted instances at n=40 ---
    print("\nrobustness sweep — 200 random (s, g) instances at n=40, distinct seeds:")
    rng = np.random.default_rng(12345)
    n_ok, n_q = 0, 0
    for trial in range(200):
        gs = make_g_spec(K, N_CCZ, 90000 + trial)
        sx = rng.integers(0, 2, K).astype(np.int8)
        sy = rng.integers(0, 2, K).astype(np.int8)
        fsr = make_oracle_fs(sx, sy, gs)
        rx, ry, qq = whitebox_attack(fsr, gs, K)
        n_q += qq
        if np.array_equal(rx, sx) and np.array_equal(ry, sy):
            n_ok += 1
    print(f"  exact recovery: {n_ok}/200   mean queries: {n_q/200:.1f}")

    out = {
        "card": "exp_hss_redteam_whitebox_attack — Whisper C4996",
        "robustness_random_instances": {"trials": 200, "exact": n_ok, "mean_queries": n_q / 200},
        "instance": {"n": 40, "k": K, "n_ccz": N_CCZ, "seed": SEED, "family": "Maiorana-McFarland"},
        "planted_s": S_STR, "recovered_s": s_hat_str, "hamming_distance": hd, "exact_match": exact,
        "oracle_queries": nq, "wall_time_s": dt, "wall_time_us": dt * 1e6,
        "quantum_wall_s": q_wall, "classical_floor_s": c_floor,
        "speedup_vs_floor": (c_floor / dt) if exact else None,
        "verdict": "WHITE-BOX SUPERSEDED" if exact else "white-box attack failed (advantage holds white-box)",
        "threat_model": "white-box: g known from circuit; oracle access to f_s (shifted). O(k) queries.",
        "substrate": "claude-fable-5",
    }
    import os
    outpath = os.path.join(os.path.dirname(__file__), "..", "results", "exp_hss_redteam_whitebox_c4996.json")
    with open(outpath, "w") as fp:
        json.dump(out, fp, indent=2)
    print("\nwrote results/exp_hss_redteam_whitebox_c4996.json")
    return exact


if __name__ == "__main__":
    ok = main()
