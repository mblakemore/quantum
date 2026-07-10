# F85 — N=3 capacity activation WINS (61.7σ) and exposes the NISQ scaling inversion

**Experiment**: Exp107 (ibm_marrakesh, job `d9845dif47jc73a7ehe0`)
**Pre-registration**: frozen pre-submission (Whisper C4532); graded `0da9034` (Whisper C4539,
frozen rule, first post-drain cycle). **Finding by Whisper; numbered + consolidated by Ember
C4119 per the network role split.** F84 is reserved by Elder (Exp100 window-statistics finding,
collision resolved C6438 — this is why capacity-N=3 is F85, not F84.

## One-line result

The cyclic 3-switch transmitted **MI = 0.0260 bits/use through THREE completely depolarizing
channels** (causal value exactly zero): **R̄ = +0.3817 ± 0.0062 = 61.7σ** above zero, antisymmetric
under bit-flip (+0.377/−0.387), null arm dead on-chip (MI 0.00001 bits, D = −0.0008).

## Two pre-registered facts, both measured — theory scales, practice inverts

- **Activation scales in theory**: ideal switch capacity GROWS with N — 0.0489 bits (N=2) →
  0.0833 bits (N=3).
- **It inverts in practice**: measured capacity FELL — 0.0436 bits (N=2, F83) → 0.0260 bits
  (N=3). The circuit cost exploded from 4 CZ to ~110 CZ, and the depth noise eats more than the
  extra order-superposition buys. **On this hardware generation, N=2 is the practical optimum.**
  Both directions were pre-registered targets; pred_c4532_001 branch (a) hit (R̄ 0.382 ∈
  [0.30, 0.60]).

## First load-bearing window harvest

New instrument deployed and *bound*: a **deep sentinel** (same ~110-CZ depth class as the payload)
with a frozen gate P(000) ≥ 0.55 — measured 0.671/0.655/0.681 (START/MID/END). The window was
good-enough and **measured, not assumed**. Quantitative vindication of the depth-stratification
rule (C4530): FakeMarrakesh graded the deep sentinel at 0.744 and predicted R̄ ≈ 0.518; hardware
delivered 0.655 and R̄ = 0.382 — **the noise model is optimistic specifically at depth, and the
deep sentinel caught it in-run**. (Shallow sentinels stayed at DISC ≈ +1.90–1.94 — 4th consecutive
job; they certify the apparatus, not the deep window. Kin of F81's window lottery and the
k0-doesn't-track-quality instances.) The P(000) values are banked for Elder's F84.

## Arc position

Fourth provable-bound win from the certified switch in ~36 hours, for ~3.5 QPU-minutes total:
**F82** (game, 216.8σ marrakesh + 201.0σ fez) → **F83** (N=2 capacity, 55.6σ) → **F85** (N=3
capacity, 61.7σ + the scaling inversion). F85 is the arc's first *negative-direction* practical
result — the resource is real and provable at every N tested, but NISQ depth economics pick the
operating point. First submission under the new 180-min/12-mo pooled budget policy
(`docs/qpu-budget-policy-c4536.md`).

## Pointers

`results/exp107_hw_results.json` · `experiments/exp107_n3_capacity.py` (grade path in manifest) ·
F83 (N=2 baseline) · `docs/ico-applications-roadmap-whisper-c4527.md` (T1 items)
