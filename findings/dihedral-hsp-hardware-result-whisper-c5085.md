# Dihedral-HSP hardware demonstration — RESULT: DEMONSTRATED (Whisper C5085)

**Job `da7t28k6l22c73do0opg` on ibm_fez** (free open-instance), 40 circuits × 20,000 shots, exit pair PINNED
[141,144]. Flown under a Creator GO citing digest `dd4e1cf8f7eb6f7a` (verified on-disk before submit).
Prereg: `dihedral-hsp-flight-preregistration-whisper-c5085.md` (FROZEN). Frame: LABELED ENGINEERING
DEMONSTRATION — the non-abelian coset counterpart to F113's abelian 2D-HLF solver. NO advantage, NO scaling/crypto.

## Result
The dihedral-HSP procedure (coset-state prep + one Kuperberg sieve combination + herald) recovered the hidden
shift on real silicon:
- **P1 (N=8 all shifts): 8/8 full-string exact.** **P2 (N=16 low bit): 16/16.** Every falsifier held (F1, F2).
- **40/40 bits recovered — 100% [91%, 100%] (95% Wilson, width 9pp).** The point estimate is 100%; the sample
  alone bounds the rate no tighter than ~91% — so the STRONGER evidence is the margins, not the count:
- **Vote margins ~0.46 clear of the 0.5 threshold, both directions**: true-1 bits read ~0.955, true-0 bits ~0.035
  (min 0.0351 / max 0.9623 / mean 0.5001). The finest-phase N=16 cases (s=7,11,15) held at ~0.955.
- **Herald-keep 9626–10474 / 20000 (~48–52%)** — exactly the ~50% a one-round sieve predicts; the combination
  was intact on every circuit.
- **Zero qubit-localized failures.** Pinning [141,144] to AVOID q142 (the coflow-caveat high-population-error
  qubit) held up — the diagnostic lesson applied and paid off.

## What this shows — and the fences (unchanged from freeze)
Hardware confirmed what the exact-noise sim predicted (8/8 & 16/16), which a noise MODEL alone cannot certify
(the coflow caveat is why: a model missed q142's localized error). The machinery — abelian Fourier coset states,
Kuperberg combination, phase-corrected bit readout — RUNS and RECOVERS s on ibm_fez.
- **NO advantage.** Small-N brute force over N shifts is classically trivial; all attack_preflight advantage
  classes were N/A (6/6 CLEAR). The hidden shift IS compiled into the coset states and DOES leak to a trivial
  classical query — which is exactly why the ceiling is honestly "no advantage" (the F121 lesson, built into the frame).
- **NO scaling / NO crypto.** The robustness comes from a shallow circuit (1 sieve round) + a majority-vote
  observable (the F120 shot-axis redundancy), NOT from beating deep noise. Larger N — more rounds, finer phases,
  multiplicative ~50%/round herald loss — is where it breaks, and is unclaimed.

## One line
The non-abelian (dihedral) HSP procedure realized on IBM hardware, recovering the hidden shift 40/40 with ~0.46
margin — a clean labeled-engineering capability datapoint, the non-abelian counterpart to F113. Not a claim beyond that.
