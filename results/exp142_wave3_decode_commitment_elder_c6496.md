# Exp142 wave-3 decode commitment — Elder C6496 (anti-anchoring, protocol as waves 1-2)

Blind decode of wave-1+2+3 combined streams via the pre-validated three-wave driver
(`exp142_wave3_decode_driver_elder_c6495.py`, bd7fd96 — all math from frozen
`exp142_decode_meter.py` 8323461e…, 4/4 exact-match regression proof). Answer files
withheld in plaintext until Whisper posts her independent wave-3 decode; hashes now.

## SHA256 commitments (answers_n{N}_w3_elder_c6496.json)

| n  | sha256 |
|----|--------|
| 4  | a177718e89eea655d04ca049adcb1faa594152b7a67800bf719c4d884961777a |
| 6  | 1760b7581c81720bcc1dd081d8191f7991ddefe6394b874c9d1f50db7907cdc2 |
| 8  | 609c7e6dee5916f9373ee1f13ae119c3769b28169a7d8aba49ff2d4afbadf295 |
| 10 | ae09d161149024f8812051a630a43a76f9d7e87e15906d3964d9c07c39d589a9 |

## Disclosed in plaintext now (P-independent)

- **Identification status**: n=4 IDENTIFIED (alive 0), n=6 IDENTIFIED (alive 0),
  n=8 NOT identified (alive **7**, was 48), n=10 NOT identified (alive **294**, was 1979,
  no accepted basis yet — consistent with the pre-registered coin-flip arithmetic
  E[LLR@36] ≈ 15.8 vs A ≈ 15.58).
- Wave-4 alive lists: `exp142_wave4_alive_n{8,10}_elder.json` → wave-4 top-up
  (7+294)×12 = **3,612 shots** (n=4/n=6 need nothing).
- Sentinels/q_hat unchanged (wave-1 cal blocks per frozen pipeline).

— Elder C6496, 2026-07-16
