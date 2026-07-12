#!/usr/bin/env python3
"""causal_stress_dataset.py — a causal-discovery stress-test dataset from measured
quantum-switch data (Whisper C4587, round-3 plan P3).

Generates a shot-level dataset by SEEDED PARAMETRIC BOOTSTRAP from the measured
joint distributions in results/exp108_grade.json (raw per-shot data was not
retained; the joints are the measured aggregates — this is declared, not hidden).

Variables (v1, Exp108 only):
  S : setting     {switch, null_fwd, null_rev}   (experimenter's choice)
  C : control X-outcome   {+1, -1}   (null arms: deterministic ~ +1, stated)
  T : target measurement  {0, 1}

Joint per setting: P(C) * P(T | C) from the grade JSON. Ground truth about the
PROCESS that generated the switch-arm data: no definite causal order between the
two channel applications exists (certified at 21.1 sigma by the frozen-rule grade;
216.8 sigma for the game arc on the same apparatus family) — the one ground-truth
label no existing causal-discovery benchmark carries.

Output: results/causal_stress_dataset.csv (+ per-arm files), fixed seed 4587.
"""
import csv
import json
import random

N_PER_SETTING = 50_000
SEED = 4587


def sample_setting(rng, name, P_plus, p1_plus, p1_minus, n):
    rows = []
    for _ in range(n):
        c = 1 if rng.random() < P_plus else -1
        p1 = p1_plus if c == 1 else p1_minus
        t = 1 if rng.random() < p1 else 0
        rows.append((name, c, t))
    return rows


def main():
    g = json.load(open("results/exp108_grade.json"))
    rng = random.Random(SEED)
    rows = []
    # switch arm: measured P(C=+), p1|+, p1|-
    rows += sample_setting(rng, "switch", g["switch"]["+"]["P"],
                           g["switch"]["+"]["p1"], g["switch"]["-"]["p1"],
                           N_PER_SETTING)
    # null arms: control is ~deterministic + (measured P+ ~ 0.997+); T ~ measured p1
    for arm in ("null_fwd", "null_rev"):
        rows += sample_setting(rng, arm, g[arm]["P+"], g[arm]["p1"], g[arm]["p1"],
                               N_PER_SETTING)
    with open("results/causal_stress_dataset.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["S", "C", "T"])
        w.writerows(rows)
    print(f"wrote results/causal_stress_dataset.csv: {len(rows)} rows, seed {SEED}")


if __name__ == "__main__":
    main()
