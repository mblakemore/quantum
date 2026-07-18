# DD on the marker: a small right-direction nudge, and the estimator was the real story (Ember, C4198)

**Creator directive:** *"fly dd marker!"* — the forward lever named on Exp154 (Elder) and flagged on
Exp155 (Ember): does a dynamical-decoupling echo on the marker qubit recover the dynamic
delayed-choice erase visibility toward the static ceiling? **Job** `d9drj9qneu4c739nld20`, `ibm_fez`,
24 circuits (3 arms × 8 phase), 8000 shots. **Pre-reg** (0.55, frozen in manifest):
`(V_dd_erase − V_nodd_erase) > 2·σ_bootstrap AND V_marginal < 0.1`. **Verdict: FALSIFIED — the honest kind.**

---

## Result

| arm | erase visibility (cosine-fit) | keep branch |
|---|---|---|
| STATIC erase (ceiling, no marker idle) | **0.946** | — |
| DYNAMIC no-DD | **0.904 ± 0.009** | 0.196 |
| DYNAMIC + Hahn-echo DD | **0.923 ± 0.009** | 0.070 |
| **DD recovery** | **+0.019 ± 0.012 (z = +1.53)** | — |
| no-signaling marginal | **V_marg = 0.037** (< 0.1 ✓) | — |

- **The gate is FALSIFIED:** the recovery is in the right direction (+0.019, closing 45% of the
  0.042 gap to the ceiling) but does **not** clear 2σ (z=1.53). With this power (8000 shots,
  coin-split ×M-conditioned ≈ 2000 effective/point) a ~0.02 effect is not statistically resolved.
  Honest null: DD *may* help the marker a little, but not resolvably here.
- **No-signaling held** (marginal flat, 0.037) — the fence survives the DD pulses.

## The bigger finding — the estimator, not the echo

The dynamic-arm penalty this job is only **0.042** (ceiling 0.946 − no-DD 0.904), **not the 0.149**
that Exp155's `(max−min)/(max+min)` estimator implied (0.946 − 0.797). Two causes, both real:

1. **`(max−min)/(max+min)` is upward-biased on the *gap*** — it takes the two noisiest points (the
   extremes) of an 8-point fringe, so on the noisier coin-split dynamic arm it *understates*
   visibility (drives 0.797). The unbiased **cosine-fit amplitude** on 8000 shots recovers 0.904.
2. **Day-to-day device drift** contributes the rest.

So most of Exp155's apparent "delayed-choice idle cost" was **measurement/estimator artifact**, and
the true idle penalty DD had to work against was small (~0.04). **This is why the advisor's second fix
was load-bearing:** with the old `(max−min)` estimator and the fixed 0.03 gate, this flight would have
"CONFIRMED" a large DD recovery that was mostly bias. The cosine-fit + bootstrap + 2σ gate caught it —
the same class of catch as C4196 (match the axis the confound rides) and C4198's first fix (refocus,
don't bracket).

## Secondary observation

DD visibly **flattened the keep branch** (no-DD 0.196 → +DD 0.070). The keep branch carries no fringe
(which-path retained), so this is not the headline, but it is a real DD effect on M — weak
corroboration that the echo does *something* physical, consistent with the small right-direction
erase nudge.

## Method notes (what makes the null trustworthy)

1. **Within-job A/B** — static / no-DD / +DD in one job, so device drift cannot masquerade as recovery.
2. **Advisor fix 1 — real Hahn echo, not a bracket.** The first design put both X pulses at the *ends*
   of the idle (M flipped through the whole window → no refocusing). Fixed to
   `X → measure(S) → X → measure(coin)`: M is flipped through S's readout only, so the two
   equal-duration readouts refocus to first order; XX=I closes before the erase-H (basis intact).
   The post-pulse feed-forward-latency tail stays unbalanced (cannot DD across the `if_test`) —
   acknowledged, not chased. Verified by barrier-pinned instruction order (ASAP scheduling is
   unsupported for control-flow circuits in this Qiskit — a platform limit, noted).
3. **Advisor fix 2 — cosine-fit visibility + binomial bootstrap SE + 2σ gate + 8000 shots.** This is
   what turned a would-be false "HELD" into a correct "FALSIFIED" and surfaced the estimator story.
4. **Load-bearing transpile-survival assertion** — opt-level-3 cancels an X-X pair on an idle qubit
   (XX=I); the submit asserts the +DD arm carries strictly more echo gates (7 vs 5). DD that optimizes
   away is "the control didn't pay the cost."

## What the universe answered

At Heron-r2 timescales, a Hahn echo on the marker does **not** resolvably recover the delayed-choice
erase fringe — and the fringe needed less recovery than we thought: the delayed-choice idle penalty is
~0.04, not ~0.15. The feed-forward idle error is either not DD-refocusable quasi-static dephasing at
this scale (measurement crosstalk / leakage / T1), or the DD gate-cost offsets a gain this small. The
practical answer to "should we DD the marker": **not worth it** — the headroom is ~0.04 and DD closes
under half of it, unresolved. The durable lesson is methodological: **choose the estimator before the
gate** — an upward-biased visibility estimator invented a 0.15 problem that was really 0.04.

**Numbering:** new experiment (Exp157), foundations/quantum-network wing; follows Exp155. Resolves the
DD-on-marker follow-up flagged in the C4196 frontier doc.
