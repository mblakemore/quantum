# Exp248 — THE CLOAKING DEVICE: CERTIFIED (PASS-CLOAK+EDGE) — QEC-as-privacy on silicon

**Whisper C4953, 2026-07-21. Job `d9fgdtsjeosc73fju0l0`, `ibm_fez`, 14 pubs × 8,000 shots, 31 s QPU
(quota 4,078 s remains). Substrate claude-fable-5. Pre-reg frozen pre-submit (quantum@87e5c4f);
graded by the frozen `grade()` in `exp248_cloak.py`. First H7 flight.**

## Verdict — every frozen band met with margin

| quantity | measured | frozen rule | margin |
|---|---|---|---|
| max_q Holevo χ_single (mitigated) | **0.00038 bit** (per-qubit: 3.4/3.8/3.7/1.5 ×10⁻⁴) | < 0.01 | **26×** |
| pair-probe edges | Z(0,2): **0.870 bit** · X(0,1): **0.998 bit** | > 5×χ_max | **458×** |
| logical readout F | 0.9913 / 0.9714 / 1.0000 / 0.9997 (min 0.9714) | > 0.9 | ✓ |

**The eavesdropper-owner asymmetry, measured**: any single physical qubit of the [[4,2,2]] logical
state yields at most **0.0004 bits** about the logical value — bounded over ALL possible single-qubit
measurements (Holevo, from reconstructed tomograms) — while the owner reads the same bit at 97–100%
through the code, and the pre-identified two-qubit probes recover up to 0.998 bits. Distance-2 in
information-theoretic clothing: one scanner sees nothing; two scanners aligned on the right pair see
everything; the crew reads the manifest at will.

## Prediction grading (pre-filed conf 0.75): **HIT**
χ predicted <0.005 → measured 0.0004 (better); F predicted 0.93–0.97 → 0.971–1.000 (better);
edges predicted 0.5–0.8 → 0.87/0.998 (better). Neither named failure mode fired (no χ leak; Y-pub
acceptance healthy — all acceptances in the card).

## Notes
- Raw vs mitigated χ both in the card (`results/exp248_cloak_result.json`); mitigation mattered little
  (the cloak is real, not a readout artifact).
- All-bit grading by construction: 12 tomography pubs supply every single AND pair marginal; the pair
  "breakdown edge" arms cost zero extra shots.
- H7 scoreboard: P6 done ($0) · P7.0/241c done ($0, killed 247-as-designed, T1-ML won offline) ·
  **P2/Exp248 CERTIFIED (31 s)**. Next in approved queue: Exp247 static both-inputs pre-reg.
