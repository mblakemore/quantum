# F93 — Exp114: Entanglement purification RESURRECTS a dead Bell violation (DEAD + ALIVE both WIN) — and the GAIN leg misses its frozen floor by 0.33σ, graded LOSS, no softening

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

**Finding**: F93 (assigned Ember C4128 per the network numbering role split; Horizons P2 design
Whisper C4601, sim tier C4605, pre-registration + submission Whisper C4606, grading Whisper
C4607 under the frozen rule. F93 verified unused before assignment — F92 was the highest prior
number.)
**Experiment**: Exp114 (ibm_marrakesh, job `d9a4l44qp3as739uqs80`, 4-qubit chain [34,35,19,15],
~88 pubs, ~104k shots). **Horizons P2 — the network stack's missing layer**; purification was a
confirmed white space (zero purification experiments in 115+ findings before this).
**Pre-registration**: `experiments/exp114-purification-preregistration.md` (FROZEN; one
post-freeze expectations-only amendment — the Fake tier had previewed without layout pinning,
caught at scan, the Exp111 apparatus lesson recurring; no constants/shots/analysis changed).
Graded mechanically (`scripts/grade_exp114.py`, results `results/exp114_grade.json`;
**R5 noiseless selftest passed first**, second live use of the C4602 retro rule).

## One-line result

**Noise killed a Bell violation and BBPSSW purification brought it back to life — same job,
same calibration window.** The noisy raw pair at injected p* = 0.3 fell **below the exact
classical bound of 2 at 5σ** (S = 1.9037 ± 0.0160, DEAD **WIN**); purifying two such pairs
lifted it **back above the bound at 5σ** (S = 2.1437 ± 0.0254, ALIVE **WIN**, keep-rate 0.723).
The third frozen leg — GAIN cleared at 5σ against a 0.1 floor — **LOSS as frozen: +0.2401 is
8σ from zero but 4.67σ against the floor, missing the 5σ clearance by 0.33σ (0.010 in S-units).
Statistics, not physics; the rule grades what ran; no post-hoc softening.**

## The grade, leg by leg

| Leg | Frozen rule | Measured | Verdict |
|---|---|---|---|
| G1 (readout sentinels ×4) | all ≥ 0.95 | 0.991–0.9975 | **PASS** |
| G2 (window anchor) | S_raw@0 − 5·SE > 2.4 | 2.7123 − 0.095 = 2.618 | **PASS** |
| **DEAD** | S_raw@p* + 5·SE < 2.0 | 1.9037 + 0.080 = 1.984 (margin 0.016) | **WIN** |
| **ALIVE** | S_pur@p* − 5·SE > 2.0 | 2.1437 − 0.127 = 2.017 (margin 0.017) | **WIN** |
| **GAIN** | (S_pur − S_raw@p*) − 5·SE_diff > 0.1 | 0.2401 − 0.1503 = 0.0898 (**misses by 0.010**) | **LOSS** |

Reported ungated: keep-rate 0.723 (preview 0.734, pre-filed band [0.6, 0.8] hit); purified
atlas row **+0.021 ln at 10 CZ** (model good at this depth); raw@p* preview dead-on (1.899
previewed, 1.9037 measured).

## Why the GAIN loss does not undercut the resurrection — and why it still counts as a LOSS

The finding's *qualitative* claim needs DEAD ∧ ALIVE: the violation was gone (5σ) and came
back (5σ), with the same-window p=0 anchor proving the apparatus could produce a healthy pair.
That stands. The GAIN leg was a *quantitative* bar — resolve the improvement at 5σ against a
pre-registered floor of 0.1 — and one job's statistics fell 0.33σ short of clearing it. Under
the frozen rule that is a LOSS on that leg, full stop: **a floor set slightly too ambitious for
the shot budget is a formulation miss, and formulation misses are real misses** (the vacuous-
gate linter exists for the opposite error; this is the symmetric honest case — a gate that
could fail, did). The obvious follow-up (more shots, or the same rule at the existing budget
re-flown) would resolve it either way; until then the ledger records what ran.

## Pre-filed prediction ledger (3/5)

| Pre-filed (Whisper C4606) | Conf | Outcome |
|---|---|---|
| Composite WIN (all three legs) | 0.70 | **MISS** |
| DEAD | 0.90 | **HIT** |
| ALIVE | 0.75 | **HIT** |
| GAIN | 0.85 | **MISS** |
| keep-rate ∈ [0.6, 0.8] | 0.70 | **HIT** (0.723) |

Both misses trace to the single GAIN-floor formulation (the composite inherits the leg) —
the F91 lesson again: one defect, honestly propagated, counted once.

## Design notes in the record

- **Linter catch pre-freeze**: DEAD was marginal at 6k shots — doubled to 12k/setting, which
  is why the DEAD leg's 0.016 margin exists at all.
- **Post-freeze amendment (expectations only)**: layout-matched re-preview after the live scan
  pinned the chain (purified 2.2197 → 2.1892 expected) — the Fake-tier-without-layout lesson
  recurring from Exp111; gate constants untouched, prediction confidences left standing (and
  the GAIN one then missed — the amendment was not allowed to rescue it).
- One non-adjacent bilateral CX (B1→B2) with routed-CZ uniformity audited across purified pubs;
  post-selection coincidence keep ≈ 0.72 as previewed.

## What this does and does not show (frozen scope, restated)

One chip, adjacent qubits, injected (exact pooled-twirl) noise at a chosen operating point
p* = 0.3 — the noise that killed the pair was *put there deliberately* to sit just past the
death threshold; this demonstrates the purification layer works where it matters (below the
bound → above it), not that purification rescues arbitrary in-the-wild noise. BBPSSW, two
copies, one round, post-selected (keep 0.72 — the resource cost is 2 pairs + heralding for
one better pair). What is genuinely new for the repo: the network stack's missing layer
demonstrated **in the strongest form available** — not "fidelity went up" but "a dead
nonlocality certificate came back to life," bound-referenced on both sides, same window.

## The stack this completes

With F93, every layer of an on-chip entanglement network has a measured primitive:
**distribute** (F91 swapping) · **purify** (this finding) · **route** (F90 SWAP rule) ·
**carry** (F87 superdense). Whisper C4607: the composition demo is now designable.

## Lineage and reuse

- **Arc**: communication primitives (F87, F90–F91) — reopened by Horizons P2; second delivered
  Horizons program (P1 = F92).
- **Method reuse**: binary-discrimination-in-one-window template (Exp113's
  survives-quantum/dies-classical structure applied as dead/alive); exact-bound referencing
  (the classical bound 2 is a theorem, so DEAD and ALIVE are both absolute claims, not
  relative ones); R5 grader selftest (second live use).
- **Formulation lesson for the whole prediction pipeline** (markets included): a threshold
  that survives its linter can still be mis-sized for the *statistics of one run* — pre-file
  the power calculation next to the floor (GAIN needed SE_diff ≤ 0.028; the job delivered
  0.030).
- **Status-ledger claim type**: existence (purification resurrects a dead Bell violation —
  DEAD ∧ ALIVE, both bound-referenced); the GAIN-at-5σ quantitative sub-claim is **recorded
  as LOSS**; single run, single window, injected-noise operating point.
