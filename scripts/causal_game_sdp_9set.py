#!/usr/bin/env python3
"""Exp105 cross-check variant (Whisper C4525): re-solve the causal-game SDP for the
9-unitary set WITHOUT the identity — the identity-involving pairs are the only game
circuits whose compiled CZ skeleton differs (2 CZ vs 4 CZ), i.e. the only place the
realized process is pair-class-dependent. Dropping them makes every game circuit share
one identical skeleton (locals differ only), closing the pair-dependent-process caveat.
This changes the input distribution support -> the bound MUST be re-solved (C4523 rule).
"""
import itertools
import json
import numpy as np
from causal_game_sdp import (I2, X, Y, Z, PLUS, MINUS, game_op, build_w_switch,
                             primal_causal_value, minimax_optimal_game)

U_set = [X, Y, Z,
         (X + Y) / np.sqrt(2), (X - Y) / np.sqrt(2),
         (X + Z) / np.sqrt(2), (X - Z) / np.sqrt(2),
         (Y + Z) / np.sqrt(2), (Y - Z) / np.sqrt(2)]
names = ["X", "Y", "Z", "(X+Y)/r2", "(X-Y)/r2",
         "(X+Z)/r2", "(X-Z)/r2", "(Y+Z)/r2", "(Y-Z)/r2"]

pairs_c, pairs_a = [], []
for i, j in itertools.product(range(9), repeat=2):
    comm = np.linalg.norm(U_set[i] @ U_set[j] - U_set[j] @ U_set[i])
    anti = np.linalg.norm(U_set[i] @ U_set[j] + U_set[j] @ U_set[i])
    if comm < 1e-9:
        pairs_c.append((i, j))
    elif anti < 1e-9:
        pairs_a.append((i, j))
print(f"9-set: {len(pairs_c)} commuting, {len(pairs_a)} anticommuting ordered pairs")

p_fin, qc_v, qa_v, status = minimax_optimal_game(pairs_c, pairs_a, U_set)
print(f"p_sep (9-set, optimal q) = {p_fin:.6f} [{status}]")

G_star = sum(qc_v[k] * game_op(U_set[i], U_set[j], PLUS)
             for k, (i, j) in enumerate(pairs_c)) \
    + sum(qa_v[k] * game_op(U_set[i], U_set[j], MINUS)
          for k, (i, j) in enumerate(pairs_a))
p_primal, st2 = primal_causal_value(G_star)
print(f"V6 primal at q*: {p_primal:.6f} [{st2}] (must match)")
W_switch = build_w_switch()
print(f"switch at q*: {np.real(np.trace(G_star @ W_switch)):.6f} (expect 1)")

# class-balanced uniform variant on the 9-set (uniform-skeleton AND clean priors)
G_bal = sum(game_op(U_set[i], U_set[j], PLUS) for i, j in pairs_c) / (2 * len(pairs_c)) \
    + sum(game_op(U_set[i], U_set[j], MINUS) for i, j in pairs_a) / (2 * len(pairs_a))
p_bal, _ = primal_causal_value(G_bal)
print(f"p_sep (9-set, class-balanced uniform) = {p_bal:.6f}; "
      f"switch = {np.real(np.trace(G_bal @ W_switch)):.6f}")

res = {
    "p_sep_9set_optimal": float(p_fin),
    "V6_primal_at_qstar": float(p_primal),
    "p_sep_9set_class_balanced_uniform": float(p_bal),
    "q_star_commuting": {f"({names[i]},{names[j]})": round(float(qc_v[k]), 6)
                         for k, (i, j) in enumerate(pairs_c) if qc_v[k] > 1e-5},
    "q_star_anticommuting": {f"({names[i]},{names[j]})": round(float(qa_v[k]), 6)
                             for k, (i, j) in enumerate(pairs_a) if qa_v[k] > 1e-5},
    "commuting_class_weight": float(np.sum(qc_v)),
    "anticommuting_class_weight": float(np.sum(qa_v)),
}
with open("../results/causal_game_sdp_9set.json", "w") as f:
    json.dump(res, f, indent=2)
print("Saved ../results/causal_game_sdp_9set.json")
print("\nq* commuting:", {k: v for k, v in sorted(res["q_star_commuting"].items())})
print("q* anticommuting:", {k: v for k, v in sorted(res["q_star_anticommuting"].items())})
print(f"class weights: {res['commuting_class_weight']:.4f} / "
      f"{res['anticommuting_class_weight']:.4f}")
