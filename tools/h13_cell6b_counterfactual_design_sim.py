#!/usr/bin/env python3
"""H13 Cell 6b (counterfactual computation) Tier-0 design sim — Whisper C5052.

Envelope model: eta_ideal(N) = cos^(2N)(pi/2N) (Zeno IFM, per-segment projective
check — Cell 6's corrected mechanism); noise envelope (1-eps_cz)^(n_cx*N) with
eps_cz = 0.0072 (Elder hardware calibration C4999, f=0.9928/CZ, Heron-r2).
Planning-grade ONLY (no readout/MCM error, full-depolarizing-to-failure envelope);
freeze-time bands require the full noise-model sim (4x heuristic applies).
"""
import math, json, sys

EPS_CZ = 0.0072
SEG_CX = {"A_query_ccx": 6, "B_machine_cccx": 16}

def table():
    rows = []
    for N in [1, 2, 4, 6, 8, 12, 16]:
        eta = math.cos(math.pi / (2 * N)) ** (2 * N)
        row = {"N": N, "eta_ideal": round(eta, 4)}
        for k, ncx in SEG_CX.items():
            row[k + "_eta_noisy"] = round(eta * (1 - EPS_CZ) ** (ncx * N), 4)
            row[k + "_f0_envelope"] = round((1 - EPS_CZ) ** (ncx * N), 4)
        rows.append(row)
    return rows

if __name__ == "__main__":
    out = {"eps_cz": EPS_CZ, "seg_cx": SEG_CX, "table": table(),
           "verdict": {"A_rollover_N": 12, "A_peak": [8, 0.5183],
                       "B_rollover_N": 6, "B_peak": [4, 0.3343],
                       "recommend": "A ladder {1,2,4,8}; B headline {2,4}"}}
    json.dump(out, sys.stdout, indent=1)
    print()
