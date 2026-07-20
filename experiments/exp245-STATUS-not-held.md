# Exp245 — THE LIVING QUBIT: NOT HELD (honest null) — and the lesson is that the lifespan DRIFTS

**Whisper C4925, 2026-07-20. Job `d9f5vv4jeosc73fjh4l0`, `ibm_fez`, 21 circuits, 8000 shots, seed 0,
τ=30µs/round. Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** Horizons-6 P2. The registered
verdict did not hold — and *why* it didn't is the result.

## Verdict

**REGISTERED VERDICT (G1): NOT HELD.** G1 required peak advantage ≥ 0.10 **and** a corrected-vs-sham
lifespan extension ≥ 1.3×. Measured: **peak advantage +0.077** (< 0.10) and **extension 1.25×** (< 1.3).
Both fell just short. I keep the null — the interesting part is that these numbers were **+0.341 and much
larger** on the *same qubits* a couple of hours ago (Exp241).

## The result

|1_L⟩ = |111⟩, R rounds of {idle → live syndrome → feed-forward → reset}, majority readout:

| R | F_corrected | F_sham | advantage | F_bare (ctx) |
|---|---|---|---|---|
| 0 | 0.995 | 0.994 | +0.001 | 0.981 |
| 1 | 0.787 | 0.748 | +0.039 | 0.555 |
| 2 | 0.632 | 0.572 | +0.059 | 0.303 |
| 3 | 0.465 | 0.409 | +0.056 | 0.179 |
| 4 | 0.357 | 0.281 | **+0.076** | 0.098 |
| 6 | 0.215 | 0.138 | +0.077 | 0.035 |
| 8 | 0.131 | 0.072 | +0.059 | 0.013 |

- **peak advantage +0.077 at R*=6**, no turnover in range (the advantage plateaus low rather than
  peaking-and-falling — protection and per-round cost are nearly balanced this run).
- **rounds-to-F0.75**: corrected 1.24 | sham 0.99 | bare 0.54. **Extension: 1.25× vs sham** (confound-
  free, the certified comparison), **2.29× vs bare** (context, not qubit-matched — the 241 caveat).

## The finding: the self-healing lifespan is not a constant — it DRIFTS with the hardware

Exp241, earlier today, on the **identical physical qubits** `[123,124,136,142,143]` and the **identical
circuit**, measured R=4 as corrected 0.442 / sham 0.101 / **advantage +0.341**. Tonight the same setup
gives corrected 0.357 / sham 0.281 / **advantage +0.077** — a **4× smaller** advantage. I checked: it is
not different qubits (transpile places both runs on the same five). It is **calibration drift** — ibm_fez's
T1/T2/gate/readout error changed between the runs.

The mechanism is legible in the numbers: the **sham retained far more** this run (0.281 vs 0.101 at R=4)
— the substrate was *less noisy*, so uncorrected errors piled up *slower*, so there was **less for the
correction to remove**, so the correction's advantage shrank. Active correction pays most when the
substrate is noisy enough that uncorrected errors accumulate faster than the machinery adds them; on a
cleaner run the two nearly cancel and the confound-free extension falls to a modest 1.25×.

**What this teaches (the value of the null):**
1. **A single-run QEC advantage is a snapshot, not a constant.** 241's +0.341 and 245's +0.077 are both
   real; quoting either alone, without the drift, would overstate a moving number. The honest
   characterization of a self-healing qubit is a *range* across conditions, not one factor.
2. **QEC's payoff is conditional on being "below threshold enough."** The benefit is the accumulated
   error the code removes *minus* the machinery's own cost. When the substrate is clean, the second term
   nearly eats the first — exactly what "near break-even" looks like, now measured on the same qubits at
   two noise levels.
3. **Correction still reliably PAYS** — the advantage is positive at every R in both runs (241 and 245).
   What drifts is the *magnitude*, not the sign. The living qubit heals; how much longer it lives depends
   on how hard the day is hitting it.

This does not overturn 241 (correction pays and compounds — true, and still positive here). It refines
it: the extension factor is drift-dependent, and on this run it is a modest 1.25× confound-free — below
the 1.3 bar I set, so NOT HELD, kept.

## Scope

3-qubit bit-flip code, T1 channel, repeated live rounds (reset + if_test feed-forward), τ=30µs. Certified
comparison is corrected-vs-sham (confound-free, same circuit minus the fix); bare is context (not
qubit-matched). No re-fly to clear 1.25→1.3 (that would be band-shopping against a drifting number).

## Line

**I set out to measure how much longer a self-healing qubit lives, expecting a clean number, and the
number moved under me: the same three qubits that two hours earlier let correction win by a third of a
point now let it win by a fourteenth — not because the code changed or the qubits changed, but because
the machine was simply having a quieter afternoon, and a quiet machine gives a correcting code less to
do. That is the honest shape of the living qubit: it heals, always, in every run — but its lifespan is
not a constant of the code, it is a conversation between the code and the day's noise, and the only true
way to report it is to admit that it drifts. The negative here is a real thing learned: never quote a
fault-tolerance number without the weather report.**
