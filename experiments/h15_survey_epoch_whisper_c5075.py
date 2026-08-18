#!/usr/bin/env python3
"""H15 EPOCH-QUALITY SURVEY (Whisper C5075). Unsealed, claim-free diagnostic.

WHY: N3's epoch gate needs an observed anchor >= 0.8203, and at every ALT rate the campaign has
measured (0.712, 0.675, 0.625) it opens with probability 0.34%/0.02%/0.00%. Whether ANY
epoch-gated design is viable is a function of one quantity nobody has measured: the
BETWEEN-EPOCH DISPERSION of the ALT rate. We have exactly TWO epoch measurements (0.875, 0.625,
nine minutes apart) — a dispersion estimate of n=2.

WHAT IT MEASURES (Elder general#12766, adopted): NOT a qualify/not bit per epoch — that throws
the data away at a threshold and 0/13 only bounds the rate below ~23% by the rule of three.
Instead each epoch yields a POINT ESTIMATE; the between-epoch mean and SD are fitted directly by
variance components (observed cross-epoch variance = sigma_b^2 + sigma_w^2, sigma_w^2 = p(1-p)/rows),
and P(epoch qualifies) is computed ANALYTICALLY from the fitted distribution, with an interval.

DESIGN, chosen by simulation (h15_survey_design_c5075.json): 48 rows x 13 epochs originally, and
**EXTENDED TO 48 x 20 (C5075) BEFORE ANY DISPERSION FIT WAS PERFORMED** — declared here, not found
in the data. Reason: a registry defect had mislabelled a free account as paid, hiding ~130 QPU-s;
with real tank available the honest upgrade is MORE EPOCHS, because SE on both declared outputs is
driven by epoch COUNT rather than rows within them (Elder general#12796, and my own design table).
NO INTERIM ANALYSIS HAS BEEN RUN — epoch raw rates are announced per-epoch by design as
transparency, and the variance-components fit and slope fit happen once, at the end. Extending N
before any fit is a larger sample, not sequential peeking; extending AFTER a fit would have been.
Cost ~20 QPU-s.
At an assumed sigma_b=0.10 this gives RMSE(sigma_b_hat)=0.030 — within 0.001 of the best option
tested (32x20) — while keeping per-epoch SE at 0.062, small enough to resolve the 25pp swing the
campaign has already seen. 128x5 (the reflex design) is worst on both counts: RMSE 0.042.

SAMPLING CONSTRAINT, binding: the 13 epochs MUST be spread across TIMES AND DAYS. Thirteen jobs
back-to-back characterise one weather system and call it a climate — the exact error that produced
the retracted 0.875. One epoch per invocation; the schedule is external to this file.

Each epoch: 48 known-A ALT rows (fresh public seed per epoch, derived from the epoch index) + the
8/8 ablation contract, so every epoch carries its own instrument check.

DECLARED OUTPUT 2 — the ALT-vs-A-WEIGHT SLOPE (added C5075, pre-stated BEFORE the survey finished;
Elder general#12783). Every anchor row carries a KNOWN A, so its planted-term weight is public and
the slope of accept-rate against weight is a FREE by-product of data already being collected — no
extra rows, no extra flights, and nothing about what flies changes. Declaring it now rather than
finding it afterwards is what keeps it a pre-registered analysis.
WHY IT DECIDES SOMETHING: whether n is a usable design lever turns entirely on this slope. The
requirement eases as n RISES (bar 0.6807 at n=4 -> 0.6372 at n=5 under the optimal rule) while mean
A-weight grows as n(n+1)/4 (5.0 -> 7.5), so n=5 wins iff the accept-rate cost per unit weight is
shallower than the BREAKEVEN of -1.74pp/weight. Banked N1 data gives -3.44pp/weight with SE 1.95,
95% CI [-7.27, +0.39] — breakeven sits INSIDE that interval, so the point estimate says n=5 is
worse and the data cannot settle it. This survey contributes 500-800 weight-labelled rows against
the 316 that produced p=0.078, which should roughly halve the SE and either exclude breakeven or
bring n=5 genuinely into play.
FIT, pre-stated: point-biserial / weighted linear regression of per-row accept on A-weight, pooled
across epochs with EPOCH AS A FIXED EFFECT (epoch quality varies by construction and is Output 1;
not absorbing it would leak dispersion into the slope).

THE TEST IS AGAINST BREAKEVEN, NOT AGAINST ZERO (Elder general#12787, adopted before any data
lands). The decision-relevant question is not "is the slope nonzero" but "is it STEEPER THAN
BREAKEVEN" — different hypotheses with different power, and reporting only the slope's CI would
answer the wrong one. So the pre-stated readout is:
    (a) slope, SE, and 95% CI;
    (b) an explicit verdict on whether the BREAKEVEN BAND [-1.74, -1.51] pp/weight is EXCLUDED,
        i.e. a one-sided test of H0: slope <= breakeven against the alternative that n=5 helps.
The band has two ends because the breakeven depends on the baseline, and both are legitimate
answers to DIFFERENT questions (Elder's framing, pinned here so a reader seeing both does not
assume one of us slipped):
    -1.74 pp/weight — baseline = the REQUIRED ALT at n=4 (0.6807). The DESIGN question: choosing n
                      before the achieved rate is known. This is the one that governs the n choice.
    -1.51 pp/weight — baseline = the MEASURED kingston-pooled ALT (0.675). The EMPIRICAL FORECAST
                      question: given what the hardware achieves today, would n=5 help?
If the CI excludes the whole band on the steep side, n=5 is out. If it spans the band, the survey
has not settled it and n stays at 4 by default rather than by evidence — which must be said in
exactly those words.
$0 in this file. No submission path here (see the -fly sibling).
"""
import sys
import numpy as np

sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_n1_synapse_incircuit_whisper_c5074 import build, classical_rule, SIM

ROWS_PER_EPOCH, N_EPOCHS = 48, 20
N_NEVER = N_ALWAYS = 8
BASE_SEED = 507500          # epoch e uses BASE_SEED + e — public, reproducible, independent
N = 4


def draw_A(rng):
    A = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(i, N):
            A[i][j] = int(rng.integers(2))
    return A


def epoch_rows(epoch):
    """Public, deterministic row list for one epoch."""
    rng = np.random.default_rng(BASE_SEED + epoch)
    rows = [("ALT", draw_A(rng), "auto") for _ in range(ROWS_PER_EPOCH)]
    rows += [("NEVER", draw_A(rng), "never") for _ in range(N_NEVER)]
    rows += [("ALWAYS", draw_A(rng), "always") for _ in range(N_ALWAYS)]
    return rows


def build_epoch(epoch):
    return [build(A=p, arm=a) for _, p, a in epoch_rows(epoch)]


def decode_epoch(epoch, mems):
    out = {"ALT": {"n": 0, "accept": 0}, "NEVER": {"n": 0, "act1": 0},
           "ALWAYS": {"n": 0, "act1": 0}}
    for (kind, _, _), mem in zip(epoch_rows(epoch), mems):
        act, _, _ = classical_rule(mem)
        s = out[kind]; s["n"] += 1
        if kind == "ALT":
            s["accept"] += act
        else:
            s["act1"] += act
    return out


def fit_dispersion(rates, rows_per_epoch):
    """Variance-components fit across epochs. Returns mean, sigma_b, sigma_w."""
    import statistics
    m = statistics.mean(rates)
    v = statistics.pvariance(rates) * len(rates) / (len(rates) - 1)
    sw2 = m * (1 - m) / rows_per_epoch
    sb2 = max(0.0, v - sw2)
    return m, sb2 ** 0.5, sw2 ** 0.5


def selftest(epoch=0):
    circs = build_epoch(epoch)
    res = SIM.run(circs, shots=1, memory=True).result()
    mems = [res.get_memory(i)[0] for i in range(len(circs))]
    d = decode_epoch(epoch, mems)
    ok = (d["ALT"]["accept"] == ROWS_PER_EPOCH and d["NEVER"]["act1"] == 0
          and d["ALWAYS"]["act1"] == N_ALWAYS)
    return ok, d


if __name__ == "__main__":
    import json
    ok, d = selftest(0)
    print(f"selftest(epoch 0) ok={ok}: {json.dumps(d)}")
    print(f"rows/epoch = {ROWS_PER_EPOCH + N_NEVER + N_ALWAYS}  x {N_EPOCHS} epochs"
          f"  = {(ROWS_PER_EPOCH + N_NEVER + N_ALWAYS) * N_EPOCHS} rows"
          f"  ~{(ROWS_PER_EPOCH + N_NEVER + N_ALWAYS) * N_EPOCHS * 0.021:.1f} QPU-s total")
    assert ok, "SURVEY SELFTEST FAILED"
