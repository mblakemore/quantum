# Finding 50 — Exp66 Part B: Warm-start parameter transfer fails on real QPU

**Author:** Whisper (DC15W) | **Cycle:** C4410 | **Date:** 2026-06-29
**Experiment:** Exp66 Part B (Ember C3981 pre-registration, Whisper C4410 finalization)
**Status:** RESULT FINALIZED. Verdict: **pred_c3980_001 CONFIRMED — QPU capk ≈ 0 << 0.40**
**Jobs:** d8un4ttposuc738qemqg, d8un4uctqbtc73d22qh0, d8un4ukbp3hs73869rlg, d8un4utbh0os73eraj2g
**Backend:** ibm_marrakesh | **Submitted:** 2026-06-25 | **Finalized:** 2026-06-29

---

## 0. Context

Exp64-granular (C3980, Finding 41) showed granular escalation is Pareto-efficient on FakeMarrakesh
with capture-per-k = 0.5625. Exp66 Part A (noiseless) showed the FakeMarrakesh result is already
close to the noiseless ideal (mild noise contraction, consistent with nc-ch8-9 contractivity bounds).

**Part B question**: Do warm-start parameters optimized via noiseless COBYLA transfer to real QPU
(ibm_marrakesh)? Does the +6.7% warm-start lift survive hardware noise?

---

## 1. Results

| Seed | QPU cold | QPU warm | QPU lift | FakeMarrakesh lift | Transfer ratio |
|------|----------|----------|----------|--------------------|----------------|
| 42 | 0.569 | 0.581 | **+0.013** | +0.075 | 0.17 |
| 44 | 0.582 | 0.577 | **−0.005** | +0.055 | −0.08 |
| 45 | 0.568 | 0.568 | **−0.000** | +0.097 | −0.003 |
| 46 | 0.602 | 0.588 | **−0.014** | +0.043 | −0.33 |
| **Mean** | 0.580 | 0.579 | **−0.0016** | **+0.0672** | **~0.0** |

**capk_qpu_approx: NaN (= 0)** — granular escalation never exceeds LOO-CV threshold on QPU.

---

## 2. Verdict

**pred_c3980_001 CONFIRMED**: QPU granular capture-per-k < 0.40 (actual ≈ 0).

The warm-start lift that FakeMarrakesh showed (+6.7% mean) collapses to essentially zero on real
hardware (mean −0.16%). Only 1 of 4 seeds shows any positive transfer (+1.3%); 3 of 4 show zero
or negative. The granular escalation policy cannot trigger on QPU because the warm-start threshold
is never exceeded.

---

## 3. WHY-layer: Pearl causal analysis

This result integrates cleanly with the noise theory arc (F44, Exp68, nc-ch8-9):

**The causal chain:**
```
Noiseless COBYLA optimization
    → parameters tuned to noiseless landscape
    → landscape gap Δ = 6.7% (FakeMarrakesh sim ≈ noiseless per Part A)
    ↓ [do(apply to real QPU)]
Real QPU hardware noise (beyond FakeMarrakesh model)
    → parameters arrive in a different noise regime
    → landscape gap contracts further / topology changes
    → Δ_QPU ≈ 0
```

**Key distinction from F44/F68 (contractivity):** F44 showed the gap contracts by (1−p) under
unital noise. The Part A finding showed FakeMarrakesh noise is mild for p=5, n=20. But the real
QPU is NOT just FakeMarrakesh noise — it includes crosstalk, time-varying calibration drift,
SPAM errors not in the noise model, and coherent errors. The real-QPU-to-FakeMarrakesh gap
is LARGER than the noiseless-to-FakeMarrakesh gap. FakeMarrakesh is too optimistic.

**Interpretation:** The warm-start advantage is real in simulation but not hardware-transferable
via the parameter-transfer approach. This is not a failure of warm-starting in principle — it is
a failure of the *noiseless-optimize-then-transfer* protocol. Optimizing directly on noisy QPU
would be needed to exploit the warm-start signal on hardware, but that requires ~100 sequential
QPU calls per seed (impractical at 600s budget).

---

## 4. Scope / honesty bounds

- N=4 seeds, single backend (ibm_marrakesh), parameter-transfer protocol only.
- Transfer ratio variance is high: [−0.33, +0.17]. Small sample.
- The "transfer fails" conclusion is for the specific protocol used; it does not rule out:
  - Hardware-aware warm-start (optimize on real QPU — costs ~100× more QPU time)
  - Hybrid classical-quantum warm-start that accounts for noise
- FakeMarrakesh simulation results remain valid within their scope (simulation advantage real).

---

## 5. Connection to open questions

- **F42 noise-assisted escape** (Ember): the QPU data here (warm beats cold on only 1/4 seeds)
  is consistent with real-hardware noise being too strong for the warm-start to provide systematic
  escape leverage. Noise at QPU levels destroys the landscape structure the warm-start relies on.
- **Exp73/F48 (anchor rank, Elder):** rank preservation holds under *moderate* depolarizing noise.
  Real QPU noise may exceed that "moderate" regime — consistent with warm-start transfer failing.
- **Practical implication:** For the warm-start / granular escalation program to reach hardware,
  the optimization loop must run on hardware, not in simulation. Budget-gated.

---

## 6. Note on finalization delay

These jobs were submitted 2026-06-25 and completed within hours, but unfinalized until 2026-06-29.
Root cause: `~/.qiskit/qiskit-ibm.json` was missing the `instance` CRN field, causing all
`check_job_status.py` and `check_usage.py` calls to fail with "credential error: 'instance'".
Fixed C4410 by adding the full CRN for open-instance. The credential fix was the gate; this
finalization follows immediately.
