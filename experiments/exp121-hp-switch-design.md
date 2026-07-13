# Exp121 — Hayden-Preskill × Switch: The Heralded Mirror (DESIGN)

**Author**: Whisper (DC15W), C4646. Horizons-2 Q3, Creator-directed.
**Status: DESIGN + sim tier this cycle; freeze on a fresh cycle (no-tired-freeze).**
Sim: `exp121_hp_switch_sim.py` → `results/exp121_feasibility.json`.

## The question

Hayden-Preskill: an old black hole returns swallowed information — the horizon is a
mirror. Standard decoders need the horizon's purification (the environment). Our
question: **does indefinite causal order change the retrieval economics — can the
probe ALONE give the diary back when no definite order of horizon-queries allows it?**

## Design lineage (two traps, one unification)

1. **Commutativity trap (C4643 lesson, caught again here)**: dephasing "horizon
   queries" into independent environments (CZ into E1, CZ into E2) COMMUTE — a switch
   of them nulls by construction. The queries must be incompatible recorders.
2. **The unification**: incompatible recorder queries (Z-query, X-query) are
   BYTE-IDENTICAL to Exp120's copy-Z/copy-X blocks. Exp121 is the SAME certified
   apparatus (same 4-slot CCZ skeleton, same star site class, hardware-validated at
   22σ/52σ at C4645) with only the encoding and readout changed: **diary in the
   probe's X basis; retrieval read from the probe alone.** Exp120 asked what the
   environments learned (Darwinism). Exp121 asks what the probe can still tell you
   (retrieval). One apparatus, two secrets of the universe.

## Exact theory (statevector, in-code — the numbers are the design)

| Arm / branch | S_P (probe-alone retrieval, ±0.5 scale) | Note |
|---|---|---|
| ordZX (definite) | **0 exactly** | diary dead; even E2 learns NOTHING (Z-query first blinds the X-recorder — the horizon keeps it: S_E2 = 0) |
| ordXZ (definite) | **0 exactly** | diary dead in P; E2 holds it perfectly (S_E2 = 0.5) |
| switch PLUS (rate 3/4) | **+1/6** | partial retrieval |
| **switch MINUS (rate 1/4)** | **−1/2 EXACTLY** | **PERFECT anti-retrieval: every shot anti-agrees — flip the bit and the ENTIRE diary reads back from the probe alone** |

The minus branch is a perfect heralded decoder for information that is measurably
inaccessible in every definite query order. The mirror exists — it lives in the
commutator branch, and it returns the diary phase-flipped.

**FakeMarrakesh at budget (30k/arm)**: minus S_P = −0.349 ± 0.004 (~90σ), plus
+0.142 (~43σ), definite arms 0.002/−0.006 (premise holds under noise), null clean.

## Frozen-freeze checklist (next fresh cycle)

- Arms ordZX/ordXZ/switch/null × diaries |±⟩ → 8 pubs × 30k = 240k shots, one job.
- Same star-site frozen rule as Exp120 (S-hub degree-3 junction; reuse
  `run_exp120_submit.select_star`).
- **Premise gates (F83 pattern)**: |S_P(ordZX)| and |S_P(ordXZ)| < 5σ-consistent-with-0
  band — the channel must be MEASURED dead in definite order or the retrieval claim
  is NO-TEST. Null classification gate + herald band as Exp120.
- **Headline W_MIRROR**: |S_P(minus)| − 5σ > band — heralded retrieval of
  definite-order-dead information (existence; the −0.349-class magnitude as reported
  figure of merit). Secondary W_PLUS on the plus branch.
- Subclaims reported, not gated: anti-correlation sign (theory: exactly −), S_E2
  ordering asymmetry (the horizon-keeps-it effect: S_E2(ordZX)=0 vs S_E2(ordXZ)=0.5 —
  a free bonus measurement of query-order-dependent environment learning).
- Predictions to hold honest: W_MIRROR ~0.85 (90σ fake margin, deep-skeleton risk
  already retired by Exp120's hardware run), W_PLUS ~0.80, NO-TEST ~0.07.

## Why this matters

F83 proved capacity activation for abstract channels. Exp121 does it with
scrambler-flavored queries and a NAMED information object (the diary), on the probe
alone, heralded, at ±0.5 scale — retrieval economics changed by causal indefiniteness.
The Exp120+121 pair on one apparatus: indefinite order rewrites what the environment
knows (Darwinism) AND what the system can still confess (the mirror).
