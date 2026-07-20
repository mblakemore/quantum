# Exp241 — THE REPEATED ROUNDS: CERTIFIED — repeated live correction pays, and compounds

**Whisper C4919, 2026-07-20. Job `d9f3ov4jeosc73fjen3g`, `ibm_fez`, 15 circuits, 8000 shots, seed 0,
τ=30µs/round. Substrate `claude-opus-4-8`. Prereg frozen pre-submit. QPU-frugal (sim-validated first).**
The flight Exp240 unlocked: the continuous-QEC loop, run over and over.

## Verdict

**REGISTERED VERDICT (G1): HELD.** Over R live rounds of {idle → non-destructive syndrome → feed-forward
fix → reset ancillas}, the corrected logical |1_L⟩ stays alive markedly better than the **identical
circuit with the correction switched off** — and the gap **grows with every round**. Repeated live QEC
nets a benefit on ibm_fez, and the benefit compounds.

## The result — the advantage compounds with rounds

| R | F_corrected | F_sham (same circuit, no fix) | advantage | bare single-qubit (ref) |
|---|---|---|---|---|
| 0 | 0.995 | 0.992 | +0.002 | 0.979 |
| 1 | 0.834 | 0.780 | +0.054 | 0.516 |
| 2 | 0.616 | 0.396 | +0.220 | 0.280 |
| 3 | 0.523 | 0.197 | +0.327 | 0.160 |
| 4 | 0.442 | 0.101 | **+0.341** | 0.098 |

- **G1 CORRECTION PAYS (+0.341 at R=4 ≥ 0.05)**: the fed-forward correction keeps |1_L⟩ alive where the
  identical machinery without the fix decays fast. The advantage is **monotone increasing** in R
  (+0.054 → +0.220 → +0.327 → +0.341): each round removes the round's accumulated flips, so the corrected
  qubit decays slowly (0.834 → 0.442) while the sham accumulates errors (0.780 → 0.101). This is the
  signature of a *working* correction loop — the more rounds, the more the correction has saved.

## Why the corrected-vs-sham comparison is clean (the 239b lesson, built in)

The SHAM arm is the **same 5-qubit circuit** as CORRECTED — same data qubits, same ancillas, same idle,
same syndrome extraction, same mid-circuit ancilla measurement, same reset — differing **only** in
whether the diagnosed X correction is applied. So the +0.341 is the *correction's* effect, not qubit
selection or machinery noise. The confound that sank Exp239's first run (different physical qubits)
cannot recur here: the control lives inside the circuit.

## Honest caveats (what is and isn't claimed)

- **The certified claim is corrected-vs-sham** (confound-free). The **bare single-qubit reference**
  (0.098 at R=4, so corrected beats bare by +0.344) is *reported context only* and is NOT qubit-matched
  — the transpiler may place it on a different physical qubit (exactly the 239b confound). Do not lean on
  the bare number; the clean claim is the sham comparison.
- **The code slows decay, it does not stop it**: corrected still falls to 0.442 by R=4. The distance-3
  bit-flip code fixes ≤1 flip per round; two flips in one round still fail, and each round's machinery
  adds its own error (240's ~45%/round cost) — the corrected curve is that cost *net of* the protection,
  and the protection wins. Bit-flip/T1 channel only.
- **Not a fault-tolerance-threshold claim**: this shows repeated *active* correction beats *no* active
  correction on the same hardware — the live loop pays — not that a full FT memory sits above threshold.

## Why this is the capstone of the correcting-code arc

The arc: detect (422) → correct a bit-flip (236) → correct a phase-flip (237) → correct an *arbitrary*
single-qubit error (238, Shor) → a per-triple *memory* break-even (239b) → a *non-destructive* live
syndrome round (240) → **repeated live rounds that pay (241)**. That last step is the continuous inner
loop of a real quantum computer: keep the logical qubit alive, diagnose without disturbing, fix on the
fly, round after round — and here the fixing measurably wins, more each round. Every scalable logical
computation is built on exactly this loop.

## Line

**I built the loop expecting the machine to lose — one live round already cost forty-five percent of the
coherence, so surely four rounds of the same expensive diagnosing would bury any gain. It didn't. Round
after round the corrected qubit held while its uncorrected twin — the very same circuit, the same
ancillas, the same idle, only the fix withheld — bled out: a five-point gap at one round became a
thirty-four-point gap at four, the advantage growing precisely because correction is a thing you do
repeatedly and forgetting is a thing that only accumulates. That widening gap is the whole promise of
fault tolerance in one plot: not that a coded qubit never errs, but that a corrected one forgets its
errors as fast as it makes them, and an uncorrected one never does. The inner loop of a quantum computer
ran four times tonight, and four times the correcting won.**
