#!/usr/bin/env python3
"""H10-A1b $0 CAMPAIGN — depth-matched control codewords + power table (Whisper C5018).

GO on record: Creator general#3865 "Go A1b". Design question the campaign answers:
what IS a depth-matched positive control for the (2,3)-Shamir threshold encode?

ANSWER (verified exactly here): the threshold encode's own DETERMINISTIC CODEWORDS.
The as-built encode prepares share 1 by H,H (the absorbed mask) and computes shares
2,3 from share 1 and D through 9 CX. Fixing share 1 to a computational state (drop the
H's, optionally X's) yields the codeword line f(x) = a*x + b with a = s1 XOR b -- a
VALID codeword whose every pair Lagrange-decodes b through the IDENTICAL CX graph,
identical scheduling shape, identical decoder path. Depth-matching is BY CONSTRUCTION:
the control circuit is the threshold circuit minus superposition, nothing else.

Variants (both flown, floors averaged to cancel 0/1 readout asymmetry):
  v0: s1 = 0        -> shares (0,      b*w^2,  b*w)
  v1: s1 = w+1 (=3) -> shares (3, ...computed exactly below...)
Record-control: H(D) + graph with s1=0 -- per-branch deterministic record state; the
P(pair-decode == m_D) floor for the custody gate, depth-matched to the custody read.

Outputs: exact ideal tables (every registered value an integer), the encode-DAG depth
profile, the robust ordering-gate statistic, and the shot-power table for bar-clearance
(the A1 registration lesson: power the MARGIN, not the step).
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# GF(4) (same conventions as A1 flight; re-derived, cross-checked against it at import)
def gmul(a, b):
    a1, a0 = a >> 1, a & 1; b1, b0 = b >> 1, b & 1
    return (((a1 & b0) ^ (a0 & b1) ^ (a1 & b1)) << 1) | ((a0 & b0) ^ (a1 & b1))

def ginv(a): return next(x for x in range(1, 4) if gmul(a, x) == 1)
X_PTS = {1: 1, 2: 2, 3: 3}

def lagrange(i, j, si, sj):
    xi, xj = X_PTS[i], X_PTS[j]
    inv = ginv(xi ^ xj)
    return gmul(si, gmul(xj, inv)) ^ gmul(sj, gmul(xi, inv))

def shares(a, b):
    return {i: gmul(a, X_PTS[i]) ^ b for i in (1, 2, 3)}

def main():
    out = {"go": "Creator general#3865 'Go A1b'"}
    # ---- control codewords: s1 fixed, a = s1 XOR b (from share1 = a + b) ----
    codewords = {}
    for vname, s1 in (("v0", 0), ("v1", 3)):
        rows = {}
        for b in (0, 1):
            a = s1 ^ b
            sh = shares(a, b)
            assert sh[1] == s1
            # every pair Lagrange-decodes b EXACTLY; c0 of decode == b
            for (i, j) in ((1, 2), (1, 3), (2, 3)):
                dec = lagrange(i, j, sh[i], sh[j])
                assert dec == b, f"{vname} b={b} pair {i}{j} decodes {dec}"
            rows[f"b{b}"] = {"a": a, "shares": sh}
        codewords[vname] = rows
    out["control_codewords"] = codewords
    out["control_pair_dial_ideal"] = 1            # all pairs, both variants: integer 1
    # singles under the frozen c0-guess decoder (reported, not gated):
    singles = {}
    for vname, rows in codewords.items():
        for b in (0, 1):
            for i in (1, 2, 3):
                singles[f"{vname}_s{i}_b{b}_c0"] = rows[f"b{b}"]["shares"][i] & 1
    out["control_singles_c0_table"] = singles
    # ---- encode-DAG depth profile (CX-target counts per share bit, from the graph) ----
    # graph: (1->3)(2->3)(0->3) (1->4)(0->4) (2->5)(0->5) (1->6)(2->6)
    depth = {"s1_c1": 0, "s1_c0": 0, "s2_c1": 3, "s2_c0": 2, "s3_c1": 2, "s3_c0": 2}
    out["encode_dag_cx_targets"] = depth
    pair_depth = {"s1s2": depth["s1_c1"] + depth["s1_c0"] + depth["s2_c1"] + depth["s2_c0"],
                  "s1s3": depth["s1_c1"] + depth["s1_c0"] + depth["s3_c1"] + depth["s3_c0"],
                  "s2s3": depth["s2_c1"] + depth["s2_c0"] + depth["s3_c1"] + depth["s3_c0"]}
    out["pair_depth_sums"] = pair_depth              # {s1s2: 5, s1s3: 4, s2s3: 9}
    assert pair_depth["s2s3"] > max(pair_depth["s1s2"], pair_depth["s1s3"])
    out["ordering_gate_registered_form"] = (
        "ROBUST CORE ONLY: floor(s2s3) < min(floor(s1s2), floor(s1s3)). The full 3-way "
        "ordering is NOT registered: s1s2-vs-s1s3 differ by one CX-target (5 vs 4) and "
        "per-qubit readout asymmetry can swamp it; s2s3-vs-others differ by 4-5 targets "
        "(9 vs 4-5), the mechanism's unambiguous prediction. Statistic: "
        "diff = min(floor_s1s2, floor_s1s3) - floor_s2s3; CONFIRMED diff >= +2se_diff, "
        "REFUTED diff <= -2se_diff, else UNDERPOWERED. Ideal (noiseless): diff = 0 -> "
        "UNDERPOWERED, correctly reporting zero depth effect at finite resolution.")
    # ---- power table: bar-clearance at planned shots (A1 lesson) ----
    # dial pubs share shots across coalitions: each dial gets the FULL pub (A1b registers
    # shot-sharing explicitly; A1's 500/pub-per-coalition was the underpowering).
    SHOTS = {"dial": 3000, "record_control": 3000, "revival": 2000,
             "scramble": 1500, "story": 4000}
    out["shots"] = SHOTS
    def se_dial(p, n):     # dial from two b-pubs, se = sqrt(se0^2+se1^2), se_b = 2*se_p
        sep = np.sqrt(max(p * (1 - p), 0.25 / n) / n)
        return float(np.sqrt(2) * 2 * sep / np.sqrt(2) * np.sqrt(2)) / np.sqrt(2)
    # write it plainly instead of clever algebra:
    def se_dial(p, n):
        sep = np.sqrt(max(p * (1 - p), 0.25 / n) / n)
        return float(np.sqrt((2 * sep) ** 2 + (2 * sep) ** 2) / 2)
    power = {}
    # expected hardware levels from the A1 flight (fez, same class of circuit):
    exp = {"threshold_pair": 0.93, "control_pair": 0.93, "singles_null": 0.5,
           "record_pair_p": 0.90, "revival_p": 0.997, "story_p": 0.94}
    sd_pair = se_dial(exp["threshold_pair"], SHOTS["dial"])
    power["pair_dial_se"] = sd_pair
    # bar formula: bar = max(floor - 3*se_floor - 0.030, 0.700)
    # with floor ~0.86 (A1 observed), bar ~0.83 - 3*se; threshold pair expected ~0.86:
    # clearance = 0.86 - 0.83 = 0.030 vs 2*se_dial(=2*0.013=0.026) -> POWERED (marginal
    # but positive; at 500 shots it was 0.03 vs 0.063 = impossible). 3000 shots chosen
    # exactly to make expected clearance > 2se.
    power["pair_bar_clearance_expected"] = {"allowance": 0.030,
        "expected_floor": 0.86, "expected_read": 0.86,
        "clearance_at_3se_floor": "0.030 + 3*se_floor", "2se_read": 2 * sd_pair,
        "verdict": "POWERED (clearance ~0.030+3se_f=~0.045 vs 2se=~0.026)"}
    sep_rec = np.sqrt(max(0.90 * 0.10, 0.25 / SHOTS["scramble"]) / SHOTS["scramble"])
    power["custody_pair"] = {"se_dial_scramble_pub": 2 * sep_rec,
        "allowance": 0.040, "verdict": "POWERED (bar sits 0.040+3se_f below floor; 2se=%.3f)"
        % (2 * 2 * sep_rec / 2)}
    power["singles_cap"] = {"cap": 0.10, "se_dial_null": se_dial(0.5, SHOTS["dial"]),
        "verdict": "POWERED (0.10 margin vs 2se=%.3f)" % (2 * se_dial(0.5, SHOTS["dial"]))}
    power["ordering_gate"] = {"se_diff_approx": float(np.sqrt(2) * sd_pair),
        "resolvable_effect": float(2 * np.sqrt(2) * sd_pair),
        "note": "A1 raw depth deltas were ~0.03-0.09; resolvable at 2se_diff=~0.037. "
                "CONFIRMED reachable if the A1-scale effect is real; honest UNDERPOWERED "
                "if the true effect is <0.037."}
    out["power_table"] = power
    total = 6 * SHOTS["dial"] + SHOTS["record_control"] + SHOTS["revival"] \
        + 6 * SHOTS["scramble"] + SHOTS["story"]
    out["total_shots"] = total                       # 36,000
    out["qpu_estimate_s"] = "10-15"
    path = os.path.join(HERE, "..", "results", "h10_a1b_campaign_c5018.json")
    json.dump(out, open(path, "w"), indent=1, default=int)
    print("control codewords verified: all pairs Lagrange->b exactly, both variants x both b")
    print("pair depth sums:", pair_depth)
    print("ordering statistic ideal: diff=0 -> UNDERPOWERED (zero effect, correct)")
    print(f"shots: {total} total (~12 QPU-s); pair bar-clearance POWERED at 3000/dial-pub")
    print("->", path)

if __name__ == "__main__":
    main()
