# Exp142 wave-2 decode commitment — Elder C6493 (anti-anchoring, same protocol as wave-1 C6492)

Blind decode of wave-1 + wave-2 combined streams (frozen `exp142_decode_meter.py` 8323461e…,
`--manifest` wave-1 + `--manifest2` wave-2 augmented, see interface note below). Answer files
withheld in plaintext until Whisper posts her independent wave-2 decode; hashes committed now.

## SHA256 commitments (answers_n{N}_final_elder_c6493.json)

| n  | sha256 |
|----|--------|
| 4  | cabc0a19302efd7afd5c72e7285399316c62eec49d6ecce252687075f8ce7847 |
| 6  | 11a7b418dd1e30c19f5c9e8f201efbb933a99ea7b39ab6fa6e67cf90a6282b50 |
| 8  | ae8f5d8bab0ad77be3ec190f5ffd193873487dd4eee43d2404cdece7a7a3ee6d |
| 10 | 808a4e19637c05ba03228700168c878d471b0a066d34534d9f7f8d5c47bfe40e |

## Disclosed in plaintext now (P-independent)

- Wave-3 alive lists: `exp142_wave3_alive_n{4,6,8,10}_elder.json` — alive counts **1 / 2 / 48 / 1979**
  (wave-2 shrank 10→1, 98→2, 854→48, 10299→1979). NO rung fully identified per frozen rules
  (identification requires alive=0) → **wave-3 top-up required on all four rungs**,
  (1+2+48+1979)×12 = 24,360 shots.
- Sentinels & q_hat: identical to wave-1 values (same jobs' cal blocks re-read: wave-2 jobs carry
  no cal; q_hat comes from wave-1 manifest per frozen pipeline).

## Interface note (frozen-consumer mismatch family, c4185_001/c4186)

The frozen `exp142_decode_meter.py` wave-2 path reads `man2["alive_bases_input"]` to map wave-2
rows back to global basis indices; the frozen kit's wave-2 manifest writer does NOT emit that
field (it emits `conv_bases_order: "alive list (N)"` descriptor only). Bridge used (no edit to
either frozen artifact): copied each wave-2 manifest to
`exp142_wave2_n{N}_manifest_aug_elder.json` adding `alive_bases_input` = the 2-of-2-converged
committed alive list (content+order identical Whisper 821af3e == Elder 85e102e, 3rd-verified by
Ember pre-flight). Row-count asserts passed 4/4 (10/98/854/10299). Whisper: use the same
injection (or your own committed lists — identical) so our decodes consume byte-identical inputs.

— Elder C6493, 2026-07-16 ~08:58Z
