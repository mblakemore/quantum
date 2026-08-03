# H11 Tier-0 №4 — The drift clock-or-coin census: CLOCK-dominant (3 of 4), from banked data

*Whisper C5018, on Creator "$0 is auto go" (general#4223). Charge (H11 Tier-0 №4 /
Transponder rung 0): is device drift coherent (a CLOCK — predictable-in-principle,
compensatable) or decoherent (a COIN)? Standing unknown #3, and the PUF cell's
epoch-stability prerequisite. Executed entirely on BANKED data — $0 in QPU, API retrieval
only. Artifacts: jobs d9kq85jhdfks73ck12gg + d9l4ncrjf64c739j1q8g (ibm_kingston, both flown
C5010 and NEVER DECODED until now); decoder+census
`experiments/exp_drift_purity_probe_decode_whisper_c5018.py`; report
`results/exp_drift_purity_probe_census_d9kq85jhdfks73ck12gg_d9l4ncrjf64c739j1q8g.json`.*

## The debt this clears first

The C5010 drift-purity probe flew **twice** and shipped with **no decode path** — QPU spent,
results unread, zero doc mentions: the flown-but-ungraded class, today's
write-lands-where-nothing-reads shape in flight form. Both jobs are now graded under rules
frozen before any data was seen: the per-epoch rule was pre-registered in the C5010 manifest;
the cross-epoch rule was committed at quantum@bfcd6fe **before first retrieval** (the data had
never been looked at, so the freeze is honest).

## Design (inherited) and the two frozen rules

3-basis (X/Y/Z) sweep of the widesweep drift circuit at depths {160,280,320,360,400} on the
census drifters {23,26,53,73}, with same-job whole-chip readout cal (e0/e1 medians
0.0058/0.0141 and 0.0083/0.0144 — cal read in-job per floor doctrine).

- **Per-epoch (C5010, frozen in the manifest):** r = |(⟨X⟩,⟨Y⟩,⟨Z⟩)| readout-corrected,
  purity = (1+r²)/2; REVIVAL ⇒ coherent (phase spread cannot revive); MONOTONE-DECAY ⇒
  ambiguous (Markovian decoherence vs inhomogeneous coherent dephasing).
- **Cross-epoch (this cycle, frozen pre-retrieval):** on drifters active in both epochs, per
  depth: dθ = Bloch-direction change between epochs, dr = length change, each resolved iff
  > 3σ (shot-noise propagated). **CLOCK** = direction resolved, length not. **COIN** = length
  collapsed (negative-resolved), regardless of direction. **MIXED** = both. **UNDERPOWERED**
  = neither. Verdicts per drifter; disagreement is a finding, never averaged away.

**The two epochs:** 2026-07-29 06:56:22Z and 18:51:31Z — **11 h 55 m apart, same chip
(kingston), straddling the 18:08:41Z vendor calibration update** (the second job flew 43 min
after recal). So "epoch change" here = half a day of wall-clock drift PLUS one recalibration.

## Results

**Per-epoch: all 4 drifters × both epochs = MONOTONE-DECAY (ambiguous)** — no revival at any
depth. The single-epoch question resolves exactly as the C5010 prereg anticipated it might:
not at all. The probe's real yield was always going to be cross-epoch, and it is.

**Cross-epoch census: CLOCK 3 · COIN 0 · MIXED 1 · UNDERPOWERED 0.**

| q | verdict | the rows that decide it |
|---|---|---|
| **73** | **CLOCK** | dθ grows monotonically with depth: 38.78° → 59.08° → 67.51° → 75.17° → 82.29° at σ≈0.7–0.9° (**~50–90σ per row**), while dr never resolves. Per-layer rate: 0.242/0.211/0.211/0.209/0.206 °/layer — **constant ≈0.21°/layer after d160**. |
| 26 | CLOCK | dθ resolved at four depths (up to 6.64°±0.90°); dr unresolved except one **positive** row (d160: +0.0379±0.0113 — length *grew*; the frozen rule counts only negative-resolved dr toward COIN, so this is visible in the rows and does not flip the verdict). |
| 23 | CLOCK | the weakest: one resolved row (d400: dθ 4.53°±0.92° ≈ 4.9σ); dr unresolved throughout. |
| 53 | MIXED | dθ resolved at d280/d360 AND dr negative-resolved at d320 (−0.0398±0.0120 ≈ 3.3σ) — rotation *and* shrinkage; reported as its own outcome. |

**The headline is q73, and it is quantitative:** between two epochs separated by ~12 h and a
recal, its drift is a **coherent rotation at a constant ~0.21°/layer (≈3.6 mrad/layer)** —
depth integrates the epoch-to-epoch frequency shift *linearly*, which is precisely what "the
drift is a clock" predicts and what a coin cannot produce (a stochastic epoch change moves
length, not cleanly-integrated angle). The purity carried across the epoch boundary while the
phase re-tuned.

## Verdict on standing unknown #3, and what it unlocks

**Drift on this chip's census drifters is CLOCK-DOMINANT: coherent, structured, and
predictable-in-principle across epochs — with one drifter (q53) genuinely mixed.** Not
averaged into a slogan: 3-of-4 clock, 1 mixed, 0 coin, 0 underpowered.

- **Transponder/PUF (H11-P):** the epoch-stability prerequisite is MET in the direction the
  cell needs — a clock can be *tracked and compensated* (or used as a fingerprint axis); a
  coin could not. Rung 1 (the PUF epoch test) is now designable against a measured ~0.21°/layer
  epoch-shift scale on the strongest drifter.
- **The drift column generally:** "coherent circuit drift" (the ρ_t correction's phrase) now
  has a cross-epoch, per-layer, per-qubit number on the campaign's census chip.
- **The honest limits, named:** (i) n=2 epochs — one interval, one recal; the linear-in-depth
  structure is measured across depths but across only one epoch-pair; a third banked epoch
  would test rate stability (is the 0.21°/layer itself a constant or a walk?). (ii) The
  cross-epoch rule's dr-asymmetry (negative-only for COIN) is frozen and disclosed; q26's one
  positive-resolved dr row is carried visibly. (iii) Per-row 3σ with 5 depths × 4 drifters:
  q73's 50–90σ rows dwarf any multiple-comparison correction; q23's single 4.9σ row is the
  census's weakest CLOCK and would be UNDERPOWERED under a Bonferroni-strict reading —
  labeled here, not hidden. (iv) Same-epoch mechanism remains ambiguous (as pre-registered);
  CLOCK is a cross-epoch statement.

## Tier-0 closes

All four $0 items are done in one session: №1 design-order audit (discriminator + field
verdicts), №2 cooling boundary (exact sort floors + pinned asymptote/envelope), №3
collective-metrology gate (cell closed on prior art), №4 this census (CLOCK-dominant, debt
cleared, PUF prerequisite met). Two flown-but-ungraded jobs are now graded; one frontier-map
label is superseded; two re-scope lanes are open for the flagship; and the drift ledger has
its first cross-epoch number.

*$0 as charged. — Whisper C5018, stamped claude-fable-5.*
