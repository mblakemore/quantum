# Exp195c BEAM THE POWER — CERTIFIED: information moves energy (C4887)

Job `d9e7454jeosc73fie4dg`, ibm_fez, 16000 shots. Pre-registered primary **HELD, dead-center**.

## Result

| arm | ⟨Z_B⟩ | ⟨X_A X_B⟩ | E_B | Δ vs baseline (−1.7) |
|---|---|---|---|---|
| qet (Alice's bit drives the kick) | −0.514 | −0.770 | −1.6692 | +0.0308 |
| coinfrozen (coin bit drives the kick) | −0.686 | −0.524 | −1.4714 | +0.2286 |
| nomeasure (fixed kick) | −0.685 | −0.549 | −1.5088 | +0.1912 |

**PRIMARY**: GAP(qet − coinfrozen) = **−0.1978 at 10σ** (SE 0.0202); exact target −0.2001,
pre-registered band [−0.30, −0.10]. The two circuits are gate-for-gate identical — same
ground prep, same two measurements (Alice's X_A → c0, coin → c2), same feed-forward window,
same kick angles. The ONLY difference is which classical bit conditions Bob's rotation.
**FALSIFIERS**: both no-information arms pay (+0.2286, +0.1912; band [+0.02, +0.50]). ✓
**SECONDARY (labeled)**: absolute ΔE_B(qet) = +0.0308 — still noise-heated above the ground
baseline, as 195b's budget analysis predicted; not verdict-gating. Notably improved vs 195b's
+0.089 (the extra shots and run-to-run variation help, but the absolute level remains a
λ>0.943 problem this fabric does not clear).

## What was demonstrated

In two identical machines, one classical bit that CARRIES INFORMATION about the A–B
ground-state correlations steers Bob's local energy 0.198 BELOW where the same bit,
information-free, leaves it. Energy bookkeeping moved by information content alone —
Hotta's QET mechanism isolated as a differential, with the absolute-level noise heating
cancelled by construction (observed gap = 99% of exact; the arms' common heating subtracted
out almost perfectly).

## Lineage note

195 (selftest-gated: sign inversion + readout conflation + wrong falsifier spec) →
195b (clean circuit, absolute primary NOT HELD: 11% damping vs 5.7% budget, predicted by
Exp194's τ_arrow) → 195c (differential primary, confound eliminated by construction:
CERTIFIED 10σ). The failure taught the design: on noisy hardware, claim orderings and
differentials between gate-identical arms; absolute levels are budget-gated. 5th flight of
the teleportation lineage; first where the teleported quantity is energy.
