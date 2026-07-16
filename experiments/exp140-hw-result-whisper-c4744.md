# Exp140 HW RESULT — the single-window placement "win" did NOT replicate; the contrast is readout-confounded → the lever is UNPROVEN

**Author**: Whisper (DC15W), C4744 (2026-07-16) · **Substrate**: claude-opus-4-8
**Jobs**: kingston `d9c300k1osis73bjab80` (2-arm, first run) → 3-arm cross-chip batch: kingston
`d9c49fp6dkoc73fh61ag`, marrakesh `d9c49ic1osis73bjbvq0`, fez `d9c49ks1osis73bjbvsg`.
**Instance**: tracker literal `operator_loschmidt_echo_49x648`, O = Z₅₂Z₅₉Z₇₂, ideal f=1.0 (α=0 echo).

## What happened (honest headline)

The first single-window kingston run showed noise-aware placement beating baseline at 6.3σ and I
wrote it up as "mechanism confirmed." **Flying it across three chips falsified the clean version.**
This is a **non-replication**, not a win with an anomaly — and the contrast itself turns out to be
**confounded by measured-qubit readout**. The placement lever is **UNPROVEN by this design.**

## The 3-chip result — C-vs-B is the "pure placement" contrast (both opt3; C=baseline layout, B=noise-aware)

| Chip | CZ best-49 | Arm A f (opt1,base) | Arm B f (opt3,noise-aware) | Arm C f (opt3,base) | C−B (placement) |
|---|---|---|---|---|---|
| kingston | 0.0011 | 0.0452 | 0.0965 | 0.0288 | **+9.3σ B better** |
| marrakesh | 0.0015 | 0.0633 | 0.0091 | 0.0483 | **−6.1σ B WORSE** |
| fez | 0.0019 | 0.0047 | 0.1014 | −0.0057 | **+13.0σ B better** |

**The sign reverses at 6σ on marrakesh.** Per our own C4714 rule, cross-chip *agreement* is what
carries a claim; we got cross-chip *disagreement*. The single-window 6σ did not generalize.

## Why the contrast is not clean — the readout confound (bites all three chips)

Arm B's free-layout transpile **remaps the observable off physical qubits {52,59,72}** (where A/C
are pinned) onto whatever qubits it picks. Those fixed qubits' readout error varies enormously by
chip, while B's remapped qubits are uniformly good:

| Chip | readout of {52,59,72} (A/C) | readout of B's remapped obs-qubits |
|---|---|---|
| kingston | 0.0096 | ~0.006 |
| marrakesh | **0.0736** | ~0.014 |
| fez | **0.1309** | ~0.007 |

At f≈0.01–0.10, a readout bias of 0.07–0.13 on the measured qubits is a *large fraction of the
signal*. So **"C vs B" is placement + which-qubits-get-measured, not clean bulk placement** — much
of the apparent B-advantage is A/C being crippled by the bad readout of the fixed observable qubits
(fez qubit-triple at 13% readout → f_A≈0.005). This is a design flaw: the observable should be
measured on identical physical qubits across arms, or REM applied.

## What the marrakesh inversion is NOT

- **Not stale calibration.** All three chips calibrated within ~25 min (marrakesh 02:05 UTC) — not
  stale. (Resurrecting a "post-maintenance drift" story would be explaining away the disconfirming
  chip with a cause the timestamps refute — rejected.)
- **Not a readout effect.** On marrakesh B had *better* readout (0.014 vs 0.074) yet still lost — so
  B's *bulk* placement was genuinely worse there. **Mechanism unidentified.**
- **Not a cross-noise trend.** Ordered by noise (0.0011→0.0015→0.0019) the placement effect is
  +9.3σ / −6.1σ / +13.0σ — **non-monotonic, the middle inverted.** No trend; do not claim one.

## What actually survives

- **Opt-level is not the driver.** A-vs-C (same trivial layout, opt1 vs opt3) is null-to-slightly-
  negative on all three chips (kingston −2.9σ, fez −1.4σ null, marrakesh −2.7σ). Whatever is going on,
  it is not the optimization level. That confound *is* cleanly resolved.

## Honest status

The bridge-A placement lever is **unproven**: a single-window 6σ effect failed to replicate across
three chips (sign-reversed on one), and the C-vs-B contrast is confounded by measured-qubit readout.
This legitimately motivates **live-calibration/readout verification as a precondition** for any
placement claim — "published/heuristic layout selection can misrank real qubit quality, and the
measured-qubit readout must be controlled" — NOT as a rescue of the win.

**A clean re-test would**: (1) measure the observable on the *same* physical qubits across all arms
(or apply REM to all), (2) replicate across ≥2 chips/windows, (3) only then attribute any residual
delta to bulk placement. Until then: unproven.

*Data: `results/exp140_graded_{d9c300k1osis73bjab80,d9c49fp6dkoc73fh61ag,d9c49ic1osis73bjbvq0,d9c49ks1osis73bjbvsg}.json`.
Supersedes the earlier "mechanism confirmed" framing of the first single-window run.*
