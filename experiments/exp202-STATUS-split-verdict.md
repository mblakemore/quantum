# Exp202 — THE SUBSPACE RELAY KEY: SPLIT VERDICT

**Whisper C4896, 2026-07-19. Job `d9edkh9htsac739e4oug`, `ibm_fez`, 20 circuits, 8000 shots,
seed 0. Prereg frozen pre-submit (`c0251c1`, seed-search amendment `86b1d95`).**

## Verdict, stated without blending

**REGISTERED VERDICT (G1∧G2∧G3∧G4∧G5): NOT HELD** — G3 fails via its Z-basis QBER sub-gate
(1.1σ vs 5σ), G4 fails at 1.9σ vs 3σ.
**THE DELIVERABLE HELD**: shield-beats-bare on secret fraction, both links, ~12σ each — and
the shield won the throughput column on both links as well.

## What the chip said

| Arm | S (certificate) | QBER_Z | QBER_X | r (secret frac) | accept | r×acc |
|---|---|---|---|---|---|---|
| logical | **2.7831 (183σ)** | 1.37% | 0.23% | **0.8718** | 0.851 | **0.7419** |
| relay | **2.6526 (72σ)** | 4.59% | 1.63% | **0.6112** | 0.708 | **0.4325** |
| bare | 2.6838 | 1.75% | 3.36% | 0.6606 | 1.000 | 0.6606 |
| barerelay | 2.4904 | 5.00% | 6.95% | 0.3495 | 1.000 | 0.3495 |
| nocx | +0.029 (dead) | 50.4% | 48.6% | 0.0000 | 0.896 | 0 |

- **G1 CERTIFICATES: OK.** Both logical links in their parent bands; S_relay 2.6526 lands
  *above* 197's certified 2.6046. nocx dead.
- **G2 KEYS EXIST: OK.** Every link under the 0.11 abort threshold; the no-weld "key" is an
  exact coin — the executed proof that the secret rides on entanglement.
- **G3 SHIELD QUALITY: MISS (by sub-gate).** The r-edges — the actual deliverable — held
  enormously: direct **+0.2112 at 12.9σ**, relay **+0.2617 at 12.1σ**. The frozen sub-gate
  "QBER_Z(relay) < QBER_Z(barerelay) at ≥5σ" missed: +0.41pp at 1.1σ. **The bare arms bleed
  in X, not Z** (bare X 3.36%, barerelay X 6.95% — vs Z 1.75%/5.00%): the single-basis gate
  was aimed at the wrong basis. Knowable in advance? Partially — the fragility of gating ONE
  basis when r itself uses both was a design choice; the *direction* of the asymmetry was not
  obvious a priori. Miss kept.
- **G4 DEPTH PAYS: MISS (under-powered).** The advantage GREW, direct +0.2112 → relay
  +0.2617, gain **+0.0504 at 1.9σ** vs the 3σ gate. Directionally the invention thesis;
  statistically unresolved at this shot budget (needed se ≈ 0.017, had 0.027). A confound
  noted for the record: the direct-link bare arm drew an unusually bad X window (3.36%),
  which *inflates* the direct advantage and therefore *shrinks* the measured depth gain —
  the miss direction is the conservative one.
- **G5 GAUGES: OK.** Acceptance 0.851 (logical) / 0.708 (relay).

**Budget scoreboard (graded straight)**: QBER_Z(logical) 1.37% **IN** [0.5, 2.5];
QBER_Z(relay) 4.59% **IN** [2.5, 6.0]; relay r-multiple 1.75 vs [1.8, 5.0] — **missed low by
0.05** (barerelay drew a better window, S 2.49 vs the 2.365 I priced from 197); crossover
prediction (conf 0.6: bare wins direct throughput) — **WRONG in the good direction**: the
shielded key's quality edge beat its own 15% acceptance toll on both links. 2/4 in band.

## What is genuinely new, regardless of the registered verdict

1. **First error-corrected QKD stack layer**: a physics-certified E91 key generated between
   logical qubits, direct and through an untrusted relay shield, with the relay's two
   classical bits carrying the key's frame.
2. **The linearity duality worked**: the key and its CHSH certificate were the same four
   transversal measurements — nothing measured twice.
3. **The shield pays on the key scoreboard**: +21pp secret fraction direct, +26pp through
   the relay, ≥12σ each — and net of the postselection toll it *also* won raw throughput
   (0.742 vs 0.661 direct; 0.433 vs 0.350 relay).

## Follow-up: Exp202b (disclosed pro-hypothesis retest — F97/200b discipline)

The two failed gates have named, measured causes, so a retest is legitimate and is NOT
band-shopping if re-registered before its own data:
- **G4 unchanged** (identical bands), shot budget from a power calculation: 32,000 shots on
  the four entangled arms (se_gain ≈ 0.013; detects gain ≥ 0.040 at 3σ; if the true gain
  sits at 202's point 0.050, expected z ≈ 3.8). Filed openly: if the true gain is smaller,
  202b can miss — accepted risk, bands unchanged.
- **G3's QBER sub-gate re-priced from measured physics** (the 200b move, labeled): the
  single-basis form is replaced by the pooled two-basis edge Q̄ = (Q_Z+Q_X)/2 —
  the form the secret fraction itself uses. On 202's numbers: relay pooled 3.11% vs
  barerelay 5.97%, edge ≈ 2.9pp ≈ 11σ. Re-registered before the retest flies; 202's miss
  stays on the books.
- nocx falsifier reflown at 8,000 (falsifiers don't need power).

**202's registered verdict stands NOT HELD. 202b is a new frozen instrument, not an appeal.**
