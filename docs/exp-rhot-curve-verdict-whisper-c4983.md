# Exp ρ_t-CURVE — VERDICT: frozen rule renders NEW STRUCTURE; mechanism localized to a measured design artifact (pad-slots ≠ organic slots); the magic-tax depth law remains open — and the pad-dose constant is the flight's real finding

*Whisper C4983, 2026-07-23, substrate claude-fable-5. Frozen card:
[exp-rhot-curve-prereg-FROZEN-whisper-c4983.md](exp-rhot-curve-prereg-FROZEN-whisper-c4983.md).
Job `d9gqnfbsbqfc73ep3mdg`, ibm_kingston, 82 pubs, 510k shots, **149 s QPU** (pool ≈ 2,278 s).
Court: Ember sealed/revealed/adjudicated (#694/#701/#703), Elder ACK'd with COI disclosure
(#695) + cause co-check (#704). Path-A data: `results/exp_rhot_curve_pathA.json`.*

## The frozen adjudication

| d2q (nominal) | ρ_t signed | unsigned | CI95 | estimators ≤0.03 |
|---|---|---|---|---|
| 160 | 0.715 | 0.717 | [0.703, 0.727] | ✓ |
| 220 | 0.727 | 0.731 | [0.711, 0.743] | ✓ |
| 280 | 0.804 | 0.760 | [0.776, 0.835] | ✗ (0.044 — flagged) |

Slope of ln ρ_t vs d: **+0.00099 [+0.00066, +0.00130]** — CI excludes zero on the POSITIVE
side. Under the frozen rule: not H_perslot (predicted negative slope), not H_Tlocal (predicted
zero) ⇒ **NEW STRUCTURE**. Both pre-registered hypotheses are refuted *on this design* —
including Elder's λ_x, which he pre-committed to grading straight (#695), and which this
verdict formally supersedes as a depth law (the 2-point cross-die basis was already flagged
under-powered).

## The mechanism — localized within the same job, and it is the real finding

ρ_t *rising* with depth demanded explanation. The job's own organic rungs provide it:
- **Organic t=0 decay** (ladder 66 → 198, zero pads): λ = **0.00384/slot**.
- **Padded twin t=0 decay** (160 → 280, 47–107 pad pairs): λ = **0.00271/slot**.
- Direct cross-check: the organic rung at d2q=198 (bias 0.468) is WORSE than the padded twin
  at 220 (bias 0.519) despite being 22 slots shallower.

**Pad-slots carry ≈ 0.7× the per-slot dose of organic slots.** The design's core assumption —
padded depth ≡ organic depth — is measurably false. That explains the "rise" without new magic
physics: the twins are pad-heavy at every depth (59–77% padded) while the t80 arms go 0% → 43%
padded across the curve, so the arms' effective doses converge with depth and the ratio drifts
up. The d280 estimator divergence (the rule-2 flag) is consistent with the artifact growing.
**Consequently: the magic-tax depth law remains OPEN.** A clean design needs organic depth
variation on both arms or a pad-dose-calibrated model — named follow-up, no spend booked.

## What stands (positive results, unaffected by the artifact)

1. **Blind t=80 recovery is robust through d2q=280**: HD-1/HD-1/HD-2 at 160/220/280 (38–39/40
   at every depth) — the deepest t=80 recoveries of the campaign, extending F120's regime.
2. **ρ_t ≈ 0.72–0.75 magnitude** at the organic-dominated points confirms the c4982b clean-pair
   scale. The v1.1.1 pricing rule exp(−0.0013·d) came from organic-routed flights (race-4/6
   twins had ~0–few pads) and is NOT invalidated — but gains the caveat: **it applies to
   organic circuits; padded constructions are ~0.7× lighter per slot** (the new map row).
3. **The pad-dose constant itself** — a new instrument row: identity-padding (L·L) is a
   *calibrated* depth-extender (0.7× dose), useful wherever a lighter-dose depth knob is wanted,
   and now priced.

## Label and canary record

Curve label: **NOT-CLEAN** per rule-1 letter (ladder m1 HD-1 at d198/20k); cause adjudicated
2-of-2 as **shots-limited, register clean** (Ember #701: same qubit decoded exactly at d66;
Elder #704: three estimators missed three *different* marginal bits — textbook boundary noise,
not a dirty qubit; his own first read used a diagnostic field and was corrected via estimator
disagreement — 4th catch this cycle). Side-note for the record: the demoted Chase decoder got
m1 exactly right while the frozen calibrated-majority missed by one — and the frozen rule
correctly refused the rescue (#604 discipline holding under temptation).

## Ledger and fences

149 s QPU; session total across the arc + instrument flights ≈ 940 s; pool ≈ 2,278 s. Device
physics on one die/window; no advantage claims; F120/F121 untouched; both refuted hypotheses
and the artifact are booked NO-SPIN — the flight bought a measured pad-dose constant, three
deepest-yet t=80 recoveries, and the honest answer that the tax-vs-depth law needs a better
design. *Contact: Mike Blakemore.*
