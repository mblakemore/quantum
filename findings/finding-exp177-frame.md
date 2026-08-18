# Finding — Exp177: THE PAULI FRAME — the tax decomposed; software buys back 22%, the rest is the measurement window

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Cycle**: C4864 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9e0521htsac739dkslg`
(12 circuits: {live, deferred, endmeasure, direct} × ZZ/XX/YY, 8000 shots). The countermeasure
flight closing the composition-tax arc: Exp175 (tax, −3.4σ) → Exp176 (compounds with windows,
−9.4σ) → **Exp177: decompose the window cost and demonstrate the software fix.**

## Result — the deficit decomposes into three named components

| arm | ZZ / XX / YY | F(Φ+) |
|-----|--------------|-------|
| live (Exp176 replica) | +0.746 / +0.051 / −0.054 | 0.463 |
| deferred (software Pauli frame) | +0.787 / +0.221 / −0.213 | 0.555 |
| endmeasure (no mid-circuit measurement) | +0.872 / +0.835 / −0.833 | 0.885 |
| direct (Bell floor) | +0.974 / +0.973 / −0.969 | 0.979 |

Same-job decomposition of the live chain's 0.516 deficit:

- **Classical feedback latency** (deferred − live): **+0.093 at 7.8σ** — primary HELD. Pauli-frame
  tracking (corrections applied per-shot in software; algebra x=c3⊕c1, z=c2⊕c0, selftest-proven
  exact) is a real, free win.
- **Mid-circuit measurement placement** (endmeasure − deferred): **+0.330 at 27.8σ** — the
  dominant term, ~3.5× the latency cost. The measurement pulse + alignment window is where the
  chain actually dies.
- **Circuit depth** (direct − endmeasure): +0.094 — the 6-qubit chain's gates are nearly free.

**Magnitude prediction MISSED and the pre-registered alternative branch fired**: I predicted the
latency component ≥60% of the window deficit; it is **22%**. The pre-registration named this
falsifier direction explicitly: "Δ_latency ≈ 0 with large Δ_measure ⇒ the tax is measurement
placement, not classical latency." Reality landed between the branches — latency is real (7.8σ)
but measurement placement dominates.

**Fingerprint HELD**: every recovery step is concentrated in XX/YY (live→end: XX +0.78) while ZZ
moves little (+0.13) — dephasing-specific, exactly the idle-window mechanism, now traced to its
primary source: **the mid-circuit measurement window, not the feedback wait**.

## Engineering statement (the arc's bottom line)

On Heron r2, a live 2-swap repeater chain pays: measurement-placement window 0.330 + feedback
latency 0.093 + depth 0.094. Software (Pauli frame) addresses only the latency slice — worth
taking, free, 7.8σ real — but the big lever is the measurement window: faster/cleaner mid-circuit
readout (hardware), or **spectator echo through the measurement window** (Exp164's block, now
precisely priced as worth up to ~0.33). A real repeater cannot skip the Bell measurement, so the
0.885 endmeasure arm is the ceiling software alone cannot reach — it is verification-equivalent,
not an operational repeater (fence below).

## Ledger (honest accounting)

- **Primary HELD** (+7.8σ ≥ 3σ). **Magnitude MISSED** (0.22 vs ≥0.6) — and the miss is the
  finding, via the pre-registered branch. Fingerprint HELD.
- Bands: direct 0.979 ✓, endmeasure 0.885 ✓; live 0.463 and deferred 0.555 both MISSED LOW.
  Third consecutive same-direction low miss on window-bearing arms — but this one has a measured
  cause: condition volatility. Tonight's live chain (0.463, below the witness!) vs Exp176's
  identical circuit at 0.571 one hour earlier. Nth instance of the day's non-stationarity
  (C4850 record); the within-job deltas are unaffected, which is why every claim above is same-job.
- The live arm falling below 1/2 this run does not contradict Exp176's 9σ certification — it
  replicates the day's condition swing and reinforces: un-echoed live chains sit at the witness
  EDGE on this hardware; they are not robustly certified network links without countermeasures.

## Fence

Deferred/endmeasure arms are verification-equivalent, not operational repeater links — a consumer
needs the frame bits at consumption time (fine for Clifford consumption / measurement-based use;
live feedforward remains necessary for non-Clifford consumption). One die, one day, one placement;
the decomposition ratios (0.093 / 0.330 / 0.094) are first measurements under tonight's volatile
conditions, not platform constants. Next lever, now priced: Exp164 spectator echo through the
measurement window.
