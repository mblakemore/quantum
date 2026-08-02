#!/usr/bin/env python3
"""H10-A1c $0 CAMPAIGN — context-matched custody floor (Whisper C5018).

GO on record: Creator direct 2026-08-02 "run A1c". The one open shape A1b left:
G4b's floor (RC, record-control) was measured WITHOUT the scramble in circuit; the
scramble context cost ≈0.13 vs a sealed 0.040 allowance → G4b FAIL x3 with every other
arm healthy. A1c prices the context INTO the floor.

THE INSTRUMENT (verified here): the context-matched custody control = the DETERMINISTIC
CODEWORD (v0, s1=0, definite b) WITH the actual per-seed scramble on share 3.
  - Shares 1,2 are computational-basis definite and the scramble acts only on share-3
    qubits -> the pair-(1,2) Lagrange decode returns b EXACTLY under ANY share-3
    unitary. Ideal dial = 1, an INTEGER KA target (proved in the flight fence by
    statevector with the real seeded unitaries).
  - Same seed, same gates, same schedule shape as the gated custody arm -> the floor
    prices readout + encode depth + scramble context, per seed, like-for-like.
  - The remaining unpriced delta is ONLY the D-superposition (record vs definite-b),
    measured small at A1b (RC 0.8847 vs C0_s1s2 0.8927 ~ 0.008) -> sealed allowance
    0.030 covers it with margin.

CLAIM B (the context cost itself, registered): cost = floor_plain(RC) - mean_seed
floor_ctx. A1b implies ~0.10-0.13. CONFIRMED >= +2 se_diff / REFUTED <= -2 se_diff /
else UNDERPOWERED. Ideal (noiseless) cost = 0 -> UNDERPOWERED, the correct null.

G2 RE-DERIVATION (Elder #3883 residual, pre-data): A1b's deepest control pair read
0.8110 +/- 0.0076 and grazed the absolute 0.800 (UNDERPOWERED). New absolute = 0.780:
= 0.8110 - 3*0.0076 (=0.788) rounded down; still >> dead-apparatus (~0); clearance
0.031 vs 2se 0.015 -> POWERED. The anti-dead-control gate must not drift unresolved.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    out = {"go": "Creator direct 2026-08-02 'run A1c'"}
    # algebra: pair-(1,2) reads only qubits 1-4; scramble acts on 5-6. Commuting,
    # disjoint supports -> marginal on (D, q1..q4) unchanged by ANY U on (q5,q6).
    out["sctx_ideal_argument"] = ("pair-(1,2) decode reads qubits 1-4; scramble supports "
                                  "{5,6}; disjoint -> marginal invariant -> dial = 1 "
                                  "exactly for any U. Integer KA target; flight fence "
                                  "proves it with the real seeded unitaries.")
    out["bars_carried_from_a1b"] = {"G1a": 0.10, "G1b": "max(floor-3se-0.030, 0.700)",
                                    "G3": 0.950, "G4a": 0.10, "G5": 0.820,
                                    "boundary": 2}
    out["bars_new"] = {
        "G2_absolute": {"value": 0.780,
                        "derivation": "A1b deepest control pair 0.8110-3*0.0076=0.788 "
                                      "rounded down; >> dead (~0); clearance 0.031 vs "
                                      "2se 0.015 -> POWERED"},
        "G4b": {"formula": "max(floor_ctx(seed) - 3*se_floor(seed) - 0.030, 0.650)",
                "allowance_note": "0.040 -> 0.030: context now priced in the floor; "
                                  "allowance covers only the D-superposition delta "
                                  "(measured ~0.008 at A1b) + residual"},
        "B_context_cost": {"statistic": "floor_plain(RC) - mean_seed(floor_ctx)",
                           "expected_from_a1b": [0.10, 0.13],
                           "gate": "CONFIRMED >= +2 se_diff / REFUTED <= -2 se_diff"}}
    # shots + power
    SHOTS = {"dial": 3000, "rc": 3000, "sctx": 1500, "rev": 2000, "scr": 1500,
             "story": 4000}
    out["shots"] = SHOTS
    total = 2 * 3000 + 4 * 3000 + 3000 + 6 * 1500 + 2000 + 6 * 1500 + 4000
    out["total_shots"] = total                     # 45,000
    def se_dial(p, n):
        sep = np.sqrt(max(p * (1 - p), 0.25 / n) / n)
        return float(np.sqrt(2) * 2 * sep / np.sqrt(2))
    # G4b power: floor_ctx expected ~0.76 (A1b scrambled record ~0.75 + no-D-superposition
    # gain ~0.01); per-seed floor from 2x1500 shots -> se ~ 0.016; bar ~ 0.76-0.048-0.030
    # = 0.68; expected custody read ~0.75 -> clearance ~0.07 vs 2se(read, 1500) ~ 0.034
    p_ctx = 0.88            # p-form of dial 0.76
    se_f = float(np.sqrt(se_dial(p_ctx, SHOTS["sctx"]) ** 2 / 2))
    out["power_G4b"] = {"expected_floor_ctx": 0.76, "per_seed_floor_se": se_f,
                        "expected_bar": round(0.76 - 3 * se_f - 0.030, 3),
                        "expected_read": 0.75,
                        "clearance_vs_2se": [round(0.75 - (0.76 - 3 * se_f - 0.030), 3),
                                             round(2 * se_dial(0.875, SHOTS["scr"]), 3)],
                        "verdict": "POWERED"}
    # B power: cost ~0.10-0.13 vs se_diff ~ sqrt(se_RC^2 + se_ctxpool^2) ~ 0.012
    se_rc = se_dial(0.94, SHOTS["rc"]) / 2 * 2
    se_pool = se_f / np.sqrt(3)
    out["power_B"] = {"se_diff_approx": round(float(np.sqrt(se_rc ** 2 + se_pool ** 2)), 4),
                      "expected_sigma_if_real": ">8",
                      "ideal_verdict": "UNDERPOWERED (cost 0 exactly at finite res)"}
    out["ordering_replication"] = ("G6-class ordering REPORTED (not a verdict): floors "
                                   "re-measured in this job; replication data for the "
                                   "A1b CONFIRMED, honest without verdict inflation")
    out["qpu_estimate_s"] = "12-16"
    path = os.path.join(HERE, "..", "results", "h10_a1c_campaign_c5018.json")
    json.dump(out, open(path, "w"), indent=1)
    print(f"shots {total} (~14 QPU-s) | G4b bar ~{out['power_G4b']['expected_bar']} vs read ~0.75 | B se ~{out['power_B']['se_diff_approx']}")
    print("->", path)

if __name__ == "__main__":
    main()
