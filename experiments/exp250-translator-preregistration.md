# Exp250 (H7-P5, redesigned) — PRE-REGISTRATION: THE UNIVERSAL TRANSLATOR

**FROZEN before submission. Whisper C4959, substrate claude-opus-4-8. Creator directive: "@whisper
Fly P5" (ship-computer general#419). Builder+grader frozen together: `experiments/exp250_translator.py`.**

## Pre-flight physics scout (PD-0, $0) — the two-storm over-claim FALSIFIED before spend
The H7-plan literal claim (a state survives an X-storm then a Z-storm by switching codes) hits a
**distance-1 wall**: each 3-qubit code protects exactly ONE logical basis (bit-flip guards Z, phase-flip
guards X), so a both-basis (Y/superposition) logical state is unprotectable by switching distance-1
codes, and the full sequenced translated arm reads **random (0.502 in sim)**. This boundary is REPORTED,
not flown; the both-basis demo needs the distance-3 Shor [[9,1,3]] code (past the depth wall).

## Claim actually flown (clean, computational-basis readout, PD-1 verified)
Each 3-qubit code is a SPECIALIST; transversal-H is the translator that carries a logical value between
them so a qubit always sits in the code matched to the incoming noise. Three frozen gates:
- **G1 CONVERSION**: |0L>,|1L> convert bit-flip→phase-flip preserving the logical value (destination
  X-majority reads 0 / 1). Rule: conv0 leakage < 0.10 AND conv1 logical-1 > 0.90.
- **G2 RETARGET**: after conversion to phase-flip, a Z-storm is corrected (X-majority), beating bare |+>.
  Rule: leakage(pf) < leakage(bare_z) − 5·se.
- **G3 SOURCE**: bit-flip corrects its native X-storm (Z-majority), beating bare |0>. Rule: analogous.
- **PASS-TRANSLATOR** = G1 ∧ G2 ∧ G3.

## Flight
`ibm_fez`, 7 pubs × 8,000 shots, static, transpiled 2q ≤ 6 (asserted). Coherent storms θ=0.3π
(single-qubit P_flip=0.206). Est. 25–50 s of 4,031 s remaining. PD-1: conversion exact (0.000/1.000);
G2 sep +0.093 (16σ), G3 sep +0.103 (18σ) ideal.

## Pre-filed prediction (before any data)
**PASS-TRANSLATOR, confidence 0.6.** Conversion (G1) high-confidence (0.85). G2/G3 lower: the ideal code
advantage is ~0.10, and **encoding overhead (~4 CZ + majority readout) may erode it on hardware** — the
same small-code overhead that Exp239b measured. Predicted hardware: conv leakage < 0.06; code leakage
0.13–0.20; bare 0.19–0.23; separations +0.03–0.09. **Named failure mode**: G2 or G3 separation ≤ 5se —
the 3-qubit code's overhead eats its protection advantage at θ=0.3π. That is a real small-scale-QEC
result (kept with full weight), and G1 (conversion) would still stand as CONVERSION-ONLY.
