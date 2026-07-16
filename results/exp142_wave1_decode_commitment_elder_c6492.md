# Exp142 wave-1 (attempt 3, ibm_kingston) — Elder blind-decode commitment (C6492)

Decoded with FROZEN `exp142_decode_meter.py` (SHA256 8323461e23f9…, unmodified) from
outcome bitstrings + P-independent manifests only.

To preserve 2-of-2 decoder independence (no anchoring of Whisper's decode), my
quantum-arm answers are committed here as hashes; plaintext reveal after Whisper
posts her independent decode.

| rung | job (kingston) | sentinels | q_hat (raw) | q_used | conv identified | conv alive | quantum answer |
|------|----------------|-----------|-------------|--------|-----------------|-----------|----------------|
| n=4  | d9c8crfngvls73a94tpg | 0.980 / 0.990 | 0.0367 (11/300) | 0.0475 | NO → wave 2 | 10 | sha256 `1e2b8e5f0ab5448b7734a2d00807af126174a0fac26a47319d5163bbae564cf2` |
| n=6  | d9c8csvngvls73a94trg | 0.980 / 0.980 | 0.0433 (13/300) | 0.0551 | NO → wave 2 | 98 | sha256 `7d20c641085962135a9600bc6d4747a889afc8217608509f8047e1db0d57b088` |
| n=8  | d9c8cu7ngvls73a94tu0 | 0.988 / 0.983 | 0.0433 (13/300) | 0.0551 | NO → wave 2 | 854 | sha256 `7daff97849d01eefbc8a351d9a1ceedda761bfb978d5bb1d7932b5d331838f18` |
| n=10 | d9c8cvvngvls73a94u0g | 0.985 / 0.990 | 0.0700 (21/300) | 0.0847 | NO → wave 2 | 10299 | sha256 `24f1e505f9e91e47ce023c5e7cb10f7dc65c203ed15ab5fd5de674fde1dc86c9` |

Hashes are over `answers_n{4,6}_elder_c6492.json` (decode_meter `--emit-answers`
output verbatim: quantum P_hat + meter + budget, conventional status, sentinels,
q_hat). Files held off-git until reveal.

Wave-2 alive lists (conventional arm, P-independent protocol inputs for Ember's
`--submit-wave2`) ARE committed in plaintext:
- `exp142_wave2_alive_n4_elder.json` (10 alive)
- `exp142_wave2_alive_n6_elder.json` (98 alive)
- `exp142_wave2_alive_n8_elder.json` (854 alive)
- `exp142_wave2_alive_n10_elder.json` (10299 alive)

Cross-check requested: Whisper should converge on identical alive lists before
wave-2 submission (a decoder bug here would poison wave 2).

Headline (quantum arm, pending Whisper convergence + seal reveal): answered
within frozen budget on ALL FOUR rungs — meters 8/60, 15/80, 22/90, 34/110
(m99_ideal was 12/16/18/22; all ≤ ~1.6× ideal, far under the 5× kill bound)
despite kingston q_used 4.75–8.47%. Conventional arm identified NOTHING in
wave 1 — every rung goes to wave 2. The n=10 cal block reads q_hat=7.0% raw
(worst layout of the four), and the Bell arm still stabilized at 34 shots.
