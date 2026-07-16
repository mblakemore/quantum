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

## Exp140b — the readout-CONTROLLED re-test (tensored REM on every arm, seeded layout, 3 chips)

Jobs: kingston `d9c4kgv550hc73dksojg`, marrakesh `d9c4kj41osis73bjcf00`, fez `d9c4klh6dkoc73fh6g9g`.
REM removes the readout confound; C-vs-B is now pure bulk placement (both opt3). Result:

| Chip | REM factors A·C / B | C−B (bulk placement, REM'd) | usable? |
|---|---|---|---|
| kingston | 0.94 / 0.97 | **+5.5σ (B better)** | yes (clean readout) |
| marrakesh | 0.92 / 0.84 | **−4.0σ (B worse)** | yes (clean readout) |
| fez | **0.20** / 0.96 | +4.2σ | **NO** — A/C on ~40%/qubit readout; REM×5 amplifies variance → noise, not a datapoint |

**Honest tally: 1 better, 1 worse, 1 unusable → the effect does NOT replicate.** It is *not* a readout
artifact (it survives REM at 4–5σ per clean chip), but on the two chips where the test is clean it
comes out with **opposite signs**.

## Final status (Exp140 + 140b)

- **The supportable statement**: the transpiler's noise-aware layout is **not a reliable improvement**
  over the trivial baseline for this circuit — better on one clean chip (+5.5σ), worse on the other
  (−4.0σ). Nothing stronger.
- **What is NOT supportable** (and is deliberately not claimed): each arm B is a *single seeded layout
  draw*, so this cannot separate chip-identity from which-region-was-drawn — so **not** "sign is
  chip-dependent," and **no** mechanism (published-cal-misled, drift) is pinned. It also gives no
  support to any live-calibration/weather-service remedy — there is no live-cal arm here.
- **Scope w.r.t. bridge A**: this is the **α=0 mirror echo** (ideal 1.0), placement-vs-arbitrary-trivial
  -baseline — **not** the tracked α≠0 observable and **not** the stack+mitigation-vs-mitigation
  *rescaled-residual* race metric. So Exp140/140b resolves bridge A in **neither** direction. It is a
  narrow methodological finding: *noise-aware transpiler placement is not a dependable lever for this
  circuit class.*
- **The process worked**: replication caught a false positive twice (single-window 6σ → raw 3-chip →
  REM-controlled), each pass shrinking the claim to what the data supports. The fly-loop is complete.

**The one open item that would actually speak to bridge A** is the deferred **rescaled-residual test**
(stack+mitigation vs mitigation-alone, the metric the tracker's mitigated contenders are graded on) —
which needs the α≠0 instance and a non-circular rescaling design. Everything here is upstream of that.

*Data: `results/exp140_graded_*.json`, `results/exp140b_graded_*.json`. Supersedes the "mechanism
confirmed" framing of the first single-window run.*
