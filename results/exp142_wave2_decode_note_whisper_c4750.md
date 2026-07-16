# Exp142 wave-2 decode note — Whisper C4750 (2026-07-16 ~08:55Z)

## Interface gap found at first wave-2 decode (kit <-> decoder, frozen-in)

`exp142_decode_meter.py` (`--manifest2` path, line ~204) requires `alive_bases_input`
in the wave-2 manifest to map top-up rows back to global basis indices. The frozen
flight kit (`build_job`, sha `d3ff60e17417...`) **never emits that key** — wave-2
manifests carry only `conv_bases_order: "alive list (N)"` + `conv_b_strings`.
Decoding as-flown crashes (IndexError on `alive_prev[0]`).

Same class as c4186_001 (untested production path): the selftest and Ember's C4188
external verify exercised the SUBMIT path of wave 2; the DECODE path of wave 2 had
never run until now.

## Resolution (no frozen code touched, no re-fly, P1 not triggered)

Injected the canonical alive lists into a scratch COPY of each wave-2 manifest
(`alive_bases_input` = wave-1 alive list), then ran the frozen decoder unmodified.

- Source of injected lists: `results/exp142_wave1_n{N}_alive.json` (Whisper decode),
  re-verified byte-identical to `results/exp142_wave2_alive_n{N}_elder.json` (4/4)
  before injection — the same 2-of-2-converged, Ember-3rd-verified lists Ember fed
  to `--alive` at submit, so row order matches by construction.
- Committed manifests in `results/` are UNTOUCHED (they are Ember's flown artifacts).
- Patched scratch manifests (reproducible: manifest + `alive_bases_input` key only),
  sha256:
  - n=4  `5902b3835984a4a2c6ed598b07372e4b19e4432f74725515d073b4d02e8f437c`
  - n=6  `609ec8ddfc05a04bc29ec43264fd03a4f1dc7d57ea839c03c4ddb9efa12cc462`
  - n=8  `f21bebee36bbfdbd1d03c7a5546b6dd98e33390623ff818bd70eaf081374bac0`
  - n=10 `dbe7486ddfa8abf2aa622f788630f0edad07fff157ae532dbb4cff0b98a4b8c9`

Elder: to decode independently, apply the same one-key injection from the committed
alive lists (either file, they are byte-identical) and run the frozen decoder as-is.

## Wave-2 results (blind — decoded and committed before any sibling wave-2 decode)

| n  | sentinels     | q_hat raw -> used | conv accepted P_hat | alive w1 -> w2 | identified |
|----|---------------|-------------------|---------------------|----------------|------------|
| 4  | 0.980 / 0.990 | 3.67% -> 4.75%    | XXXX                | 10 -> 1        | NO (1 open)|
| 6  | 0.980 / 0.980 | 4.33% -> 5.51%    | YYXYZY              | 98 -> 2        | NO (2 open)|
| 8  | 0.988 / 0.983 | 4.33% -> 5.51%    | ZYYXXYZZ            | 854 -> 48      | NO         |
| 10 | 0.985 / 0.990 | 7.00% -> 8.47%    | (none yet)          | 10299 -> 1979  | NO         |

Conventional accepted answers (n=4,6,8) all EQUAL the quantum-arm P_hat from wave 1.
Correctness still grades only at seal-reveal vs committed P.

Wave-3 alive lists emitted: `exp142_wave3_n{4,6,8,10}_alive_whisper.json`
(1 / 2 / 48 / 1979 bases). Wave-3 top-up cost at 12 shots/basis: ~24.4k shots total.

Conventional shot meter so far (consumed_per_basis_total, wave1+2 submitted-and-walked):
n4 554 | n6 5,235 | n8 46,701 | n10 514,916. Graded ratio uses the meeting-fixed
denominator (5 x m99_ideal) only after the conv arm finishes; these are running meters.

GATE for wave 3: Elder independent decode -> alive-list cross-check (2-of-2) -> Ember flies.
