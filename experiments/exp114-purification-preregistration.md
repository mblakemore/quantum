# Exp114 — Entanglement Purification: Resurrecting a Dead Bell Violation (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4606. Horizons P2 — the network stack's missing layer
(confirmed white space: zero purification experiments in 115+ findings).
**Status**: FROZEN at commit. Grade on return; R5 noiseless selftest mandatory first
(shared estimator `chsh_from_run`, sim module = fixture).

## Claim structure (the Exp113 template: binary discrimination, one job, one window)

Inject exact pooled-twirl noise at p*=0.3 into Bell pairs. Three frozen facts must hold
together: the noisy raw pair's Bell violation is DEAD (below the exact classical bound 2),
BBPSSW purification of two such pairs brings it back ALIVE (above 2), and the GAIN is
resolved. Sim: no-harm validator at p=0 PASS; ideal gain +0.266; Fake tier: raw@p* 1.899,
purified@p* 2.2197 (keep 0.734), gain +0.321 — purification beats injected AND chip noise.

## Arms and budget (~88 pubs, ~104k shots)

raw@p=0 window anchor (4 pubs × 6000) · raw@p* (16 weighted pubs, 12000/setting — doubled
after the linter showed DEAD marginal at 6k) · purified@p* (64 weighted pubs, 6000/setting,
coincidence post-selection keep≈0.73) · readout sentinels ×4. Chain: best 4-qubit path;
circuit order B2-A2-A1-B1; ONE non-adjacent bilateral CX (B1→B2) — its routed CZ cost is
recorded at scan and must be uniform across purified pubs (audit).

## Frozen gates (all linted OK, C4606)

- **G1**: readout sentinels ≥ 0.95 → else NO-TEST.
- **G2 (anchor)**: S_raw@0 − 5·SE > **2.4** → else NO-TEST (bad window).
- **DEAD**: S_raw@p* + 5·SE < **2.0** (linted pass margin 0.036 at 12k shots; an
  alive-raw 2.15 scenario fails decisively).
- **ALIVE**: S_purified@p* − 5·SE > **2.0** (margins 0.095/0.050).
- **GAIN**: (S_purified − S_raw@p*) − 5·SE_diff > **0.1** (margins 0.080/0.044).
- WIN = DEAD ∧ ALIVE ∧ GAIN. Any single failure with G1/G2 passing = LOSS on that leg
  (graded independently). Reported ungated: keep rate vs 0.734 preview, per-setting E's.

## Prediction

WIN (all three legs) conf 0.70; DEAD 0.9; ALIVE 0.75; GAIN 0.85; keep ∈ [0.6, 0.8] 0.7.
