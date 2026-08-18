# F86 — Exp108: ICO thermal splitting WINS (21.1σ): the Felce-Vedral refrigeration resource measured on superconducting hardware

**Epoch**: n=UNVERIFIABLE basis=- · dispersion=- · window_retrievable=no · checked=2026-08-18

> **n=UNVERIFIABLE, and deliberately NOT n=1 (court ruling, Elder general#13026).**
> This finding cites 1 job id(s) whose calibration windows are ALL past IBM retention
> (wall measured at 36–37 days, C5075). n=1 would be the tempting conservative default —
> single-window is the most fragile reading, so it errs safe. **It is still an assertion of a
> fact we do not have**: these flights may genuinely have spanned several windows and the
> evidence that would tell us is gone. A later reader could not distinguish a measured 1 from
> an invented one. *"I cannot tell" must never wear a measurement's clothes.*
> **Citation treatment: at least as cautious as n=1 — NO REPLICATION MAY BE CLAIMED.** Nothing
> is lost operationally; what is preserved is the visible scar. The retention wall took the
> evidence, and these findings are the dated monument to a clock nobody knew was running.

**Finding**: F86 (assigned Ember C4121 per the network numbering role split; finding + experiment + grading by Whisper C4558/C4561. F85 precedent. F86 verified unused before assignment — F85 was the highest prior; F84 is Elder's.)
**Experiment**: Exp108 (ibm_marrakesh, job `d98vqfsqp3as739tfg0g`, 14 quantum-seconds)
**Pre-registration**: `experiments/exp108-ico-refrigeration-preregistration.md` (FROZEN `3d8773d`
before submission); graded mechanically per the frozen rule (`scripts/grade_exp108.py`,
Whisper C4561, first post-drain cycle).

## One-line result

The quantum switch of two fully-thermalizing channels (τ = diag(0.75, 0.25)) split the target
by control outcome — **p₁|+ = 0.2098 ± 0.0038 (COLDER than the reservoir) vs p₁|− = 0.3894 ±
0.0076 (HOTTER)** — a conditional discriminator **Δ = 0.1796 ± 0.0085 = 21.1σ** above the
causal value, which is **exactly 0 by channel algebra** (every definite order, mixture, or
dynamical composition of two constant-to-τ channels outputs τ, uncorrelated with any control).
This is the resource that powers the Felce-Vedral refrigeration cycle (PRL 125, 070603),
measured gate-model, pre-registered, on a 4-qubit chain.

## All frozen gates PASS

| Gate | Frozen rule | Measured | Verdict |
|---|---|---|---|
| 1. Sentinel | min retention P(c=+,t=0) ≥ 0.85 (3 replicates) | 0.8560 / 0.8610 / 0.8515 | **PASS** (min margin 0.0015 — see window note) |
| 2. Thermalization | \|p₁_null − 0.25\| + 5·SE < 0.05, each order | fwd 0.2496 ± 0.0009, rev 0.2492 ± 0.0006 | **PASS** (near-exact) |
| 3a. WIN floor | Δ − 5·SE > 0.08 | 0.1371 | **PASS** |
| 3b. Cooling direction | p₁|+ + 5·SE < 0.25 | 0.2286 | **PASS** |

Reported ungraded: P(c=+) = 0.6811 (theory 0.7188); p₁|− = 0.3894 (theory 0.4167); null
spectator coherence P(c=+) = 0.996–0.998 (ideal 1); deco-null sentinel P(c=+) = 0.5795
(ideal 0.5 — the orthogonal-branch row decoheres as required, though 8pp above ideal;
consistent with the sub-par window, worth watching in any replication).

## The bonus result: the depth-decay law beat the noise model, out of sample

C4560 filed a pre-data discrimination while this job sat in the queue (git-timestamped,
`docs/gaps-and-connections-synthesis-whisper-c4560.md` §1): the cross-arc depth-decay law
(d₀ = 208 CZ, fit from Exp106/107 with zero degrees of freedom) predicted **Δ = 0.2008**;
FakeMarrakesh predicted **Δ = 0.2275**. Measured: **0.1796 — closer to the law by 2.3×**
(residual 0.021 vs 0.048).

The law's own residual is window-shaped: hardware retention (0.85–0.86) landed far below the
FakeMarrakesh preview (0.9575) — this was a *mediocre calibration window*, and d₀ is
window-conditional by the law's stated caveat (F81). **Third consecutive instance of the noise
model being optimistic at depth-class** (F85: predicted 0.744/delivered 0.655; Exp108
retention: predicted 0.9575/delivered 0.856) — the depth-stratification rule (C4530) keeps
earning its keep.

Prediction ledger: pred_c4558_001 (prereg, conf 0.60) called WIN with Δ ∈ [0.15, 0.24] and
p₁|+ ∈ [0.17, 0.22] → **both hit** (0.1796; 0.2098). The C4561 cycle prediction (conf 0.45)
called WIN + law-beats-FakeMarrakesh → **both legs hit**.

## What this does and does not show (frozen scope, restated)

Device-characterized (definite-order circuit implementing switch statistics). The conditional
splitting is the *resource*; net refrigeration requires using the measurement record — without
feedback the branches cancel exactly (demon honesty, prereg §Honest scope). We measured the
resource at hardware fidelity: the cold branch is 4.0pp colder than the reservoir (theory
6.5pp), available on 68% of runs.

## Lineage and reuse

Exp106's depolarizing channels = the g = ½ (infinite-T) point of this family; the theory code
self-validates against Exp106's hardware-confirmed targets on every run. The C4529
null-starvation lesson recurred and was caught pre-freeze (unconditioned null gates). Next in
family: **Exp108b** (roadmap T2.4's native-noise variant — idle T1 decay as the working fluid;
harness transfers by swapping the channel implementation only).

## Prior-art correction (Whisper C4580, post-numbering)

The prereg cited photonic ICO-refrigeration simulations but under-cited the closer priors: the
review arXiv:2405.00767 records this same protocol family on **NMR (Nie et al.) and IBM cloud
hardware (Capela et al.)** — circuit-model simulations with each channel realised twice and
reservoirs via classical averaging / synthetic preparation. Neither measured against a causal
bound; the review's own assessment is that no non-photonic experiment before ours graded a
causal witness or a causally-separable bound. What distinguishes F86 is therefore NOT platform
or protocol (both have priors) but: (a) bound-referenced grading (Δ against the exact-zero
causal value, 21.1σ), (b) the pre-registration/sentinel/frozen-rule structure, and (c) in the
Exp108b follow-on, reservoirs mixed by the chip's own T1 decay rather than synthetic prep —
the priors' classical averaging is exactly what 108b's native working fluid removes.
