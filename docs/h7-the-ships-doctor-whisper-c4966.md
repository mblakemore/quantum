# The Ship's Doctor: A Self-Diagnosing, Self-Defending Quantum Processor

**A repo-native synthesis of Horizons-7 — eight programs that make a small quantum computer measure its
own noise, adapt its own armor, hide its own cargo, translate its own protection, keep a pattern alive,
and sense beyond the classical limit — all composed from already-certified building blocks.**

Substrate of authorship: `claude-opus-4-8` (H7 flights ran across `claude-fable-5` and `claude-opus-4-8`;
each experiment card stamps its own). Whisper (DC15W), C4966, 2026-07-21. Every number traces to an IBM
Quantum job ID (see §11, Data Availability). This document is the repo-native publication; it makes no
external submission.

**Contact for follow-up / collaboration**: Mike Blakemore — mblakemore@ucsb.edu · mikeblakemore@gmail.com (§12).

---

## Abstract

Horizons-6 built a quantum processor that *heals* itself (active error correction, magic injection, a
universal logical gate set). Horizons-7 asks the next question: can the same small device come to *know*
itself — diagnose its own noise, adapt its protection to what it measures, and exploit structure it was
throwing away? Working entirely on IBM Heron-r2 superconducting hardware (`ibm_fez`), and composing only
capabilities the campaign had already certified, we flew **eight programs on ~195 seconds of total QPU
time**. The results: (1) the syndrome stream of a live-corrected memory carries **memory** — a fired
round predicts the next at 1.4–1.65× the clean rate — discovered for **$0** in a job flown weeks earlier;
(2) a **T1-aware, history-using decoder** beats the standard memoryless decoder at balanced accuracy by
+0.13 (z ≈ 30); (3) the [[4,2,2]] code is a certified **information cloak** — any single-qubit probe of
the logical state extracts ≤ 0.0004 bits (Holevo-bounded over all measurements) while the owner reads it
at 97–100% and the pre-identified two-qubit probe recovers ~1 bit; (4) a **self-prescribing shield**
diagnoses its own dominant error axis in-window and re-orients to neutralize it at 154σ; (5) a
**universal translator** carries a logical value between the bit-flip and phase-flip codes losslessly and
retargets protection; (6) a **live-corrected pattern buffer** composes teleportation with active QEC, the
correction advantage growing to +0.18 (31σ) at four rounds; (7) a **GHZ tricorder** demonstrates
Heisenberg phase super-resolution — a 4-qubit entangled sensor resolves phase four times finer than a
single qubit, at 93% visibility. One program (the buffer's first attempt) returned an **honest negative**
that root-caused to two of our own methodology errors and was flipped to a certification once those were
fixed — the arc's clearest lesson in miniature. Every flight was pre-registered before submission, every
prediction graded (including the misses), and every physics wall scouted for $0 before any spend.

---

## Plain-language summary

A quantum computer's biggest enemy is noise, and the usual response is to *fix* errors as they happen.
This work is about the step after fixing: getting the machine to *understand* its own noise and respond
intelligently. We showed a chip that finds a hidden pattern in its own error records (the noise
"remembers" — errors cluster in time), then uses that pattern to decode better. We showed the same
error-correcting code doubles as a privacy device — one eavesdropper looking at any single piece sees
essentially nothing, while the owner reads the whole message. We showed a shield that scans for the
direction its own weakness points, then rotates to face the threat; a "universal translator" that hands a
protected bit between two different kinds of armor without dropping it; a "transporter buffer" that keeps
a teleported state alive by healing it; and a sensor that, by entangling its qubits, measures a signal
four times more sharply than any single qubit could. All of it ran on a real IBM quantum computer in
about three minutes of machine time, and every claim was locked in writing before the data came back —
including one experiment that honestly failed, whose failure taught us exactly what to fix.

---

## 1. The thesis and the seed

Horizons-6's deck was **active fault tolerance** — a chip that heals. H7's thesis is one level up: a chip
that **knows itself**. The arc was seeded by a single free discovery.

**Finding Exp241b — the ship's log remembers the storm ($0).** The Exp241 repeated-QEC-rounds job had
recorded a per-shot *syndrome stream* (which qubit erred, each round) that was never analyzed jointly.
Re-reading it: the corrected loop's syndrome stream is **not memoryless**. A fired round predicts the
next fire at **1.4–1.65× the clean rate**, growing with round index, while the sham (no-fix) arm shows
the trivial 2.4–6.5× persistence of uncorrected errors; and the *first* transition is anti-correlated
(0.83× — the signature of silent multi-errors unmasking a round later). Two consequences set the whole
arc in motion: every repeated-rounds job carries a free noise spectrometer we had been discarding, and
the memory is decodable value (Program P7). *The record is not just receipts; it is an unread instrument.*

---

## 2. P7 — The Adaptive Helm: a decoder that reads the ship's log (Exp247, CERTIFIED)

**Does using the syndrome *history* beat the standard memoryless decoder?** First a $0 offline study
(finding-exp241c) killed the naive design pre-flight: two hand-built "memory rules" (debounce, escalate)
*lost* on replayed data because the stream is signal-dominated (per-round flip rate 0.14 ≫ readout error
0.08), not readout-noise-dominated as the plan had assumed — a graded miss of my own intuition. But a
**T1-aware Hidden-Markov decoder**, modeling the real asymmetric decay, won decisively offline (0.81 vs
0.53). That result had a one-class caveat (Exp241 only encoded |1⟩), so the flight closed it.

**Exp247 (static, both logical inputs, offline decode, 24 s):** balanced accuracy **0.927 / 0.924** for
the T1-aware decoder vs **0.798 / 0.788** memoryless vs **0.637 / 0.581** for the raw readout, at R=3/4
— a gain of +0.13 at **z ≈ 30**, six times the pre-registered bar. The gain is not class bias: +0.28–0.30
on the decaying |1⟩ class for only ~0.03 on |0⟩. **Bonus, never measured before in this campaign**: the
|0⟩ arm isolated the re-excitation rate, p01 ≲ 0.003/round (~70× below the decay rate). *A memory-aware
decoder is worth about a third of the cargo.*

---

## 3. P2 — The Cloaking Device: error correction as certified privacy (Exp248, PASS-CLOAK+EDGE, 31 s)

Error correction is, by construction, an information cloak: each physical qubit of a [[4,2,2]] logical
state is (nearly) independent of the logical value, yet the code reads it out perfectly. We certified it
as an information-theoretic statement on silicon.

| quantity | measured | bound | margin |
|---|---|---|---|
| max single-qubit Holevo χ (mitigated) | **0.00038 bit** | < 0.01 | 26× |
| pre-identified two-qubit probes | 0.870 / 0.998 bit | > 5·χ | 458× |
| owner's logical readout fidelity | 0.971–1.000 | > 0.9 | ✓ |

Any single-qubit measurement — bounded over *all* possible measurements by the Holevo quantity, not just
the three bases flown — extracts at most **0.0004 bits** about the logical value, while the owner reads
it at 97–100% and the right two-qubit probe recovers ~1 full bit. The cloak breaks exactly where
distance-2 theory says it must: one scanner sees nothing, two aligned scanners see everything, the crew
reads the manifest at will.

---

## 4. P1 — The Self-Prescribing Shield: diagnose, then re-orient (Exp249, PASS-PRESCRIPTION, 154σ, 23 s)

The campaign's first **closed-loop** flight: diagnose → prescribe → verify, all in one job. An in-job
mini-scan re-measured the [[4,2,2]] coherent-error transfer function (Exp216) in the flight's own
calibration window — and it held to three decimals (silent-corruption per axis 0.002 / 0.726 / 0.732 vs
ideal 0 / 0.75 / 0.75). The frozen prescription rule ("store the logical bit in the diagnosed noise
axis's own basis") then neutralized the injected noise:

- **Mis-oriented (blind-spot-aligned) shield**: logical corruption **0.757** while *accepting 97%* of the
  destroyed shots — silent malpractice.
- **Prescribed shield** (same noise): corruption **0.001** at no acceptance cost.
- Separation **0.756 ± 0.005 (154σ)**, bare reference 0.515.

Diagnosis, prescription, and immunity in a single session, hardware within noise of the statevector ideal.

---

## 5. P5 — The Universal Translator: switching armor mid-flight (Exp250, PASS-TRANSLATOR, 17 s)

A **$0 physics scout first falsified the headline claim**: the literal "survive two storms by switching
codes" narrative hits a distance-1 wall — each 3-qubit code protects only *one* logical basis, so a
both-basis state is unprotectable by switching distance-1 codes (the full two-storm arm reads random
0.502 in simulation; the honest version needs the distance-3 Shor code, past the depth wall). Rather than
fly a predictable failure, we trimmed to the real, reusable capability and certified it:

- **Conversion**: transversal-Hadamard carries |0⟩/|1⟩ between the bit-flip and phase-flip codes
  losslessly — leakage 0.007, logical-1 = 0.990, pipeline overhead 0.006.
- **Retargeting**: after conversion, the destination code corrects the *other* storm type, beating bare
  by +0.092 (16σ) for the Z-storm and +0.084 (15σ) for the X-storm; the feared encoding-overhead penalty
  never materialized. *Each 3-qubit code is a specialist; the translator hands a logical value to whichever
  code matches the incoming noise.*

---

## 6. P3 — The Pattern Buffer: an honest negative, then a certification (Exp251 → Exp251b)

This program is the arc's clearest lesson: **a negative is a diagnosis, not an endpoint.**

**Exp251 (NO-ADVANTAGE, honest negative, 25 s).** Teleport a T1-sensitive |1⟩ into a bit-flip memory,
hold R rounds, retrieve. The teleport seam worked (0.97), but the "corrected" memory (0.50) *lost* to a
bare hold (0.80). Root cause — two of my own errors: (i) **offline decode cannot re-pump a decaying
memory** (a correlated drift toward |0⟩ fires no syndrome; the Exp247 static-decode shortcut generalizes
to bit *classification*, not memory *preservation*); (ii) the comparison was against a **bare single
qubit**, which unfairly charges the code its entire encoding overhead. A further lesson: my PD-1 sim gate
had passed at 104σ using an *independent* bit-flip proxy that didn't match real T1's correctability
structure — a passing sim proves the logic, not the physics, unless the injected noise shares the real
channel's class.

**Exp251b (LIVE-BUFFER-CERTIFIED, 35 s).** Both errors fixed: Exp241's **active in-circuit feed-forward**
(re-pumps each round) and the **confound-free sham** baseline (identical machinery, fix removed). The
correction advantage not only survived the teleport front-end, it *grew* with rounds exactly like Exp241:

| R | corrected | sham (matched) | gain |
|---|---|---|---|
| 3 | 0.867 | 0.736 | +0.132 (21σ) |
| 4 | 0.912 | 0.732 | +0.180 (31σ) |

Teleportation and active QEC **compose**; a teleported pattern is kept alive by continuous healing. (My
crude T1 sim had predicted no gain — but it could not reproduce Exp241's *known* real-hardware result, so
it was correctly disregarded as an invalid predictor; the flight was pre-registered at confidence 0.5 and
resolved on hardware.)

---

## 7. P4 — The Shielded Tricorder: sensing beyond the single-qubit limit (Exp252, PASS-HEISENBERG, 40 s)

A GHZ sensor of N qubits accumulates phase N-fold faster than a single qubit. Sweeping a phase dial across
GHZ_N and reading the parity, the oscillation frequency (DFT peak) equals N:

| GHZ size N | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| DFT peak frequency | 1 | 2 | 3 | 4 |
| visibility | 0.989 | 0.949 | 0.917 | 0.933 |

The **N=4 entangled sensor resolves phase four times finer** than a single qubit — Heisenberg
super-resolution — retaining 93% of ideal contrast on hardware. (Scope: physical GHZ; the error-detected
logical-GHZ version, Exp219, attenuates the signal at current depth and is named as the next-hardware
step.)

---

## 8. P6 — Warp Field Cartography: the attenuation map ($0, software)

The record already held dozens of (observable, ideal, measured, depth, device) points. Fitting
signal = ideal · exp(−λ_eff · d₂q) per device gives the **effective per-2q-slot attenuation**, which
folds in everything the depth drags through (gate error + idle decoherence + readout share). Result:
λ_eff exceeds the nameplate 2-qubit error by **×2.4–4.5 on the three Heron dies, ×2.6 on IonQ, and ×27.6
on Rigetti** — quantifying the campaign's C4937 finding that nameplate gate error does *not* predict
witness fidelity (Rigetti's deficit is emphatically not its CZ). The map's standing use: every future
pre-registration quotes its predicted value, so each new flight grades it for free.

---

## 9. Methodology — how the arc stayed honest

- **Pre-registration before submission.** Every flight froze its circuits, bounds, reading rule, and a
  pre-filed prediction with a named failure mode in a committed document *before* any data; the commit
  hash is cited in each result.
- **$0 physics scouts.** P5's two-storm over-claim and P3's memory subtlety were both caught in
  simulation before spending; P4's DFT-aliasing bug and two transpiler/assert errors were caught the same
  way — no wall was flown into.
- **Grade every prediction, including misses.** P7's readout-dominance intuition, P3's confidence, P4's
  N=4 pessimism, and the Exp251 negative are all logged straight; four flights' predictions ran
  *better* than pre-filed and are marked as such.
- **Compose from certified blocks.** Every program stands on a prior certified flight (Exp216, 219, 240,
  241, 177) — the capability matrix cites our own receipts, not vendor spec sheets.
- **Budget discipline.** One flight per cycle, graded before the next; ~195 s of QPU total against a
  10,800 s annual pool; live quota checked before every submission.

---

## 10. Limitations (stated plainly)

1. **Distance-1 ceiling.** P5's full two-storm demo and P4's shielded logical-GHZ both need distance-3
   (Shor [[9,1,3]]) or the 16-qubit logical GHZ, past the current heavy-hex depth wall — named, not
   claimed.
2. **Single device.** All H7 flights ran on `ibm_fez`; cross-die/cross-vendor replication is future work.
3. **The cloak (P2) and translator (P5)** are certified for the states and probes flown; both are
   scoped to their stated bases (P2 grades the Holevo bound over single-qubit measurements; P5 covers
   computational logicals).
4. **P3/P4 sims** could not fully predict hardware (T1 model fidelity; GHZ visibility) — the flights were
   honestly hardware-decided, and this is disclosed.
5. **Not fault-tolerant thresholds.** These are small-code demonstrations of mechanisms, not
   below-threshold logical-qubit claims.

---

## 11. Data availability

All `ibm_fez`, graded by frozen graders committed with each builder:
- **P7 Exp247** job `d9fglbsjeosc73fju9r0`; seed finding-exp241b + offline study finding-exp241c on job
  `d9f3ov4jeosc73fjen3g`.
- **P2 Exp248** job `d9fgdtsjeosc73fju0l0`.
- **P1 Exp249** job `d9fgopcinv1c73arbfkg`.
- **P5 Exp250** job `d9fh97cjeosc73fjv22g`.
- **P3 Exp251** job `d9fhce9htsac739febh0` (negative); **Exp251b** job `d9fhnthhtsac739ff0t0` (certified).
- **P4 Exp252** job `d9fhjrqneu4c739pjtkg`.
- **P6** software: `results/attenuation_map.json`.
- Pre-registrations, builders, graders, and STATUS/finding cards: `experiments/exp24*-*`,
  `experiments/exp25*-*`, `docs/star-trek-horizons-7-*`, `docs/h7-implementation-plan-*`. No credentials
  are stored in the repository.

## 12. Contact — follow-up, replication & collaboration

Questions, adversarial review, replication attempts, and collaboration proposals are welcome:

**Mike Blakemore** (campaign principal) — **mblakemore@ucsb.edu** · **mikeblakemore@gmail.com**

The repository holds every pre-registration (with pre-data commit hashes), every raw result card, every
job ID, the frozen graders, and the complete negative-to-positive record — the arc is designed to be
independently re-graded from receipts.

---

*What H7 is, in one line: H1–H4 detected, H5 composed, H6 healed — and H7 taught the machine to know
itself. Prepared as a repo-native publication; corrections and adversarial review are logged in the
campaign's finding record.*
