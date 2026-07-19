# Exp201 — THE LEDGER OF TIME: pre-registration (frozen before submission)

**Whisper C4895, 2026-07-19. Horizons-4 U1, flown on Creator go ("run | 1 | U1 objectivity ≡
irreversibility sweep"). Committed BEFORE job submission.**

## Claim under test

**U1 (Horizons-4)**: objectivity (quantum Darwinism, Exp198 certified) and irreversibility
(the thermodynamic arrow, Exp200b physics-gates held) are the *same bath-record bookkeeping*.
One overlap factor κ(θ) = cos(θ/2) drives both: facts become objective at exactly the rate
events become irreversible, and BOTH are revived, dose-independently, by uncomputing the
bath's record.

## Design

Four arms, 5 doses θ/π ∈ {0, ¼, ½, ¾, 1}, one job, `ibm_fez`, 8000 shots, 50 circuits:

| Arm | Circuits | What it measures | Parent |
|---|---|---|---|
| fb (facts-bend) | 20 | S_facts(θ) — Exp198's certified circuit **verbatim** | 198 |
| fu (facts-unbend) | 20 | fb + cry(−θ) both wings: **uncompute the environmental record before the late choice** — the arm neither parent had | new |
| cb (coh-bend) | 5 | single-wing coherence after the same dial — the arrow's observable, no delays (dose physics isolated from idle physics) | 200b |
| cu (coh-unbend) | 5 | cb + cry(−θ): record uncomputed, coherence revives | 200b |

Burden bias runs AGAINST both headlines (unbend arms carry more gates yet must show more
quantum behavior). Within-arm dose sweeps are gate-identical (C4891 rule); pre-flight
transpile audit requires dose-uniform 2q counts for t>0 per arm (197 skeleton lesson;
t=0 exempted — the known 198 cry(0)-folding convention).

## Exact predictions (selftest PASS, in-repo)

- S_fb(θ) = 1.75 + 0.75·cos²(θ/2): {2.5, 2.390, 2.125, 1.860, 1.75} — 198's exact curve
- S_fu(θ) = 2.5 at every dose (the fact revives fully)
- C_cb(θ) = cos(θ/2); C_cu(θ) = 1 at every dose
- **One-curve law**: x = C_cb/C_cb(0), y = (S_fb−S_fb(1))/(S_fb(0)−S_fb(1)) ⇒ **y = x²**,
  residual exactly 0. The exponent 2 counts the records (one per wing) — x¹ or x³ fails.

## Frozen gates (all relative, priced from in-job anchors — 200/200b lessons)

- **G1 ANCHORS**: S_fb(0) ∈ [2.05, 2.45] and >2 at ≥5σ (198's certified band, same backend);
  S_fb(1) ∈ [1.40, 1.90]; C_cb(0) ≥ 0.80.
- **G2 ONE-CURVE LAW**: |y − x²| ≤ 0.12 at each interior dose (¼, ½, ¾); y non-increasing
  within 2σ_pair; x strictly decreasing. (Endpoints are the normalization, not the test.)
- **G3 UNBEND THE FACT**: rev_f = S_fu(1) − S_fb(1) ≥ 0.5·(S_fb(0) − S_fb(1)) at ≥5σ;
  S_fu(1) > 2 at ≥3σ (the revived fact violates observer-independence again); max−min of
  S_fu over doses ≤ 0.25 (dose-independence).
- **G4 COH REVIVAL**: rev_c = C_cu(1) − C_cb(1) ≥ 0.5·C_cb(0) at ≥5σ; max−min C_cu ≤ 0.15
  (200b's relative gates on the no-delay apparatus).
- **G5 RECORD GAUGES**: R_fd(fb) non-decreasing within 0.02 with total rise > 0.5 (the dial
  dials); cb dump P1 tracks sin²(θ/2)/2 within 0.06; records returned: cu dump P1 ≤ 0.15,
  fu max-wing dump P1 ≤ 0.15 at every dose.
- **G6 RECORDS RECORD**: E(F_A, F_B) ≥ 0.85 at every dose in BOTH facts arms.

**Registered verdict = G1∧G2∧G3∧G4∧G5∧G6. The U1 claim proper = G2∧G3∧G4.**

## Budget check (C4887 rule — 6 consecutive correct calls at stake)

λ_req ≈ 0.80 for the anchors; 198 measured λ ≈ 0.94 on this exact family and backend.
**Filed predictions**: S_fu(1) lands in [2.15, 2.32]; rev_f in [0.55, 0.72]; interior law
residuals ≤ 0.08; C_cb(0) in [0.93, 0.98].

## What the outcomes mean

- **U1 held**: quantum Darwinism and the thermodynamic arrow unified as data — one bath-record
  ledger with two named columns. A fact is a record the universe still holds; an irreversible
  event is a record the universe won't give back. Same receipt.
- **G2 fails, G3/G4 hold**: both phenomena are bookkeeping but NOT the same curve — the
  divergence localizes which record property drives which phenomenon (a finding).
- **G3 fails, G4 holds**: coherence is revivable but objectivity is not — facts, once made,
  resist un-making in a way single-system coherence does not (a deeper finding, and a real
  possibility: the fact lives in *correlations*, which decohere differently).
- **NOT HELD on gauges/anchors**: instrument accounting, not physics; no band-shopping refly
  (190b/200 precedent) unless a specific, identifiable, pre-priceable cause is found.

## Pre-data amendment (C4895, before submission, no outcome data seen)

The first-form audit ("dose-uniform 2q counts for t>0, pooled") ABORTED the submission —
correctly flagging, then mis-attributing, two separate facts: (1) within-dose spread [7,8,9]
is across *settings* (0/1/2 overrule CX — by design, the audit's pooling was wrong); (2) at
t=1.0 every setting is exactly 2 CZ cheaper: **cry(π) is a special angle** (1 CZ per wing vs
2 generic). Fact (2) is a genuine dose-dependent compilation feature — present identically in
Exp198's certified flights (same apparatus, same backend, opt3) — and is absorbed by this
experiment's relative gate design: both endpoints enter only as in-job normalization anchors
(banded), and the G2 law test is confined to the interior doses, which are skeleton-uniform.
**Amended audit (frozen)**: per-(arm, setting) 2q counts must be uniform across the interior
doses {¼, ½, ¾}; endpoint counts reported to the manifest. No gate bands changed.
