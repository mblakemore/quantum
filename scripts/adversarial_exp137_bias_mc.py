#!/usr/bin/env python3
"""adversarial_exp137_bias_mc.py — Whisper C4713 ADVERSARIAL CYCLE (Creator-directed).

Tests the F117 headline claim: "0.65 rigorous 1SDI bits, and the model-free number
BEAT the Werner model (0.682 > 0.656), so the real state is closer to ideal than
isotropic noise assumes."

THESIS: the grade's 40-sample bootstrap resamples around the observed counts and re-runs
the SAME reconstruct->project->SDP pipeline, so it measures FLUCTUATION (which is a
non-issue: H_min/SE ~ 108, the '5sigma' gate clears zero by ~100 SE). It is structurally
BLIND to the tomographic BIAS between the point estimate and truth. If the full pipeline,
fed finite-shot data from a PLAIN ISOTROPIC (Werner) state whose true H_min is exactly the
0.656 'model estimate', systematically returns ~0.682, then the 0.026 'beats-the-model'
gap is pipeline bias, not physics.

GROUND TRUTH: Werner v = 1.6813/sqrt(3) = 0.9707 (the model's own fitted v).
  True H_min = 0.6556 bits, True S3 = 1.6813.

PRE-REGISTERED DISCRIMINATOR (filed before results seen, Whisper C4713):
  mean(H_min_recovered) >= 0.675  -> 'beats-the-model' COLLAPSES into bias (observed 0.682
                                     reproduced by isotropic noise + pipeline)
  mean(H_min_recovered) ~= 0.656  -> payoff is real signal; retract that part of the critique
  Also report bias = mean_recovered - 0.6556 and compare its magnitude to the reported
  bootstrap SE (0.0063): if bias >> SE, the certificate's error bar is on the wrong error.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from sdp_randomness import (werner_assemblage, guessing_probability, hmin,  # noqa
                            cjwr_S, bloch_op, DIRS3, I2)
from exp137_assemblage_tomography_sim import (reconstruct_assemblage,  # noqa
                                              project_valid, ns_violation, AXES)

SIGN = {"X": 1, "Y": -1, "Z": 1}
DIRS = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}
SHOTS = 20000            # matches exp137
NREP = 160
V_MODEL = 1.6813 / math.sqrt(3)


def werner_rho(v):
    bell = np.array([1, 0, 0, 1], dtype=complex) / math.sqrt(2)
    return v * np.outer(bell, bell.conj()) + (1 - v) * np.eye(4) / 4


def joint_probs(rho, xdir, tdir):
    """p(a,b | x,t) = Tr[(M_a^x ⊗ Π_b^t) rho], a,b in (+1,-1)."""
    p = {}
    for a in (+1, -1):
        Ma = (I2 + a * bloch_op(xdir)) / 2
        for b in (+1, -1):
            Pb = (I2 + b * bloch_op(tdir)) / 2
            op = np.kron(Ma, Pb)
            p[(a, b)] = float(np.real(np.trace(op @ rho)))
    return p


def sample_counts(rho, rng):
    """9 tomography circuits, SHOTS each, qiskit bit order 'q1 q0' = 'b a'."""
    counts = {}
    for x in AXES:
        for t in AXES:
            p = joint_probs(rho, DIRS[x], DIRS[t])
            keys = [(a, b) for a in (+1, -1) for b in (+1, -1)]
            pv = np.array([max(p[k], 0.0) for k in keys])
            pv = pv / pv.sum()
            draw = rng.multinomial(SHOTS, pv)
            c = {}
            for (a, b), n in zip(keys, draw):
                abit = "0" if a == +1 else "1"   # q0 = Alice
                bbit = "0" if b == +1 else "1"   # q1 = Bob
                c[f"{bbit}{abit}"] = int(n)       # qiskit 'q1q0'
            counts[(x, t)] = c
    return counts


def pipeline_hmin(counts):
    asm = project_valid(reconstruct_assemblage(counts))
    pg, _ = guessing_probability(asm, "Z")
    S3 = cjwr_S(asm, DIRS, signs=SIGN)
    return hmin(pg), S3


def main():
    rho = werner_rho(V_MODEL)
    asm_true = werner_assemblage(V_MODEL, DIRS3)
    pg_true, _ = guessing_probability(asm_true, "Z")
    h_true = hmin(pg_true)
    s3_true = cjwr_S(asm_true, DIRS3, signs=SIGN)
    print(f"GROUND TRUTH: v={V_MODEL:.4f}  H_min_true={h_true:.4f}  S3_true={s3_true:.4f}")
    print(f"OBSERVED (F117): H_min=0.6823  S3=1.6876  boot_SE=0.0063  (5SE margin=0.031)")
    print(f"Running {NREP} reps x 9 circuits x {SHOTS} shots through reconstruct->project->SDP...")

    rng = np.random.default_rng(4713)
    hs, s3s = [], []
    for i in range(NREP):
        h, s3 = pipeline_hmin(sample_counts(rho, rng))
        hs.append(h)
        s3s.append(s3)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{NREP}  running mean H_min={np.mean(hs):.4f}")
    hs = np.array(hs)
    s3s = np.array(s3s)
    mean_h = float(hs.mean())
    bias = mean_h - h_true
    print("\n=== RESULT ===")
    print(f"mean recovered H_min = {mean_h:.4f}  (std across reps {hs.std():.4f})")
    print(f"mean recovered S3    = {s3s.mean():.4f}")
    print(f"BIAS = mean_recovered - true = {bias:+.4f} bits")
    print(f"reported bootstrap SE = 0.0063  ->  bias / SE = {bias/0.0063:+.1f}")
    print(f"observed 'rigorous' value 0.6823 vs mean-recovered {mean_h:.4f} "
          f"(from isotropic truth)")
    verdict = ("COLLAPSES: isotropic noise + pipeline reproduces the observed value; "
               "'beats-the-model' is bias" if mean_h >= 0.675 else
               "PARTIAL: pipeline biased upward but does not fully reach 0.682" if bias > 0.010 else
               "PAYOFF REAL: pipeline ~unbiased; retract beats-the-model critique")
    print(f"PRE-REGISTERED VERDICT: {verdict}")
    import json
    json.dump({"v": V_MODEL, "h_true": h_true, "mean_recovered": mean_h,
               "bias": bias, "std": float(hs.std()), "nrep": NREP,
               "observed_f117": 0.6823, "boot_se": 0.0063, "verdict": verdict},
              open(os.path.join(HERE, "..", "results",
                                "exp137_adversarial_bias_mc.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
