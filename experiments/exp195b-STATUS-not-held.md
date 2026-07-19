# Exp195b BEAM THE POWER — STATUS: NOT HELD on QPU (pre-registered primary failed; C4887)

Job `d9e70csinv1c73apt6cg`, ibm_fez, 8000 shots. Selftest was clean (Aer −0.1056 vs exact
−0.1028); the hardware said no.

## Result

| arm | ⟨Z_B⟩ | ⟨X_A X_B⟩ | E_B | Δ vs ground baseline (−1.7) |
|---|---|---|---|---|
| qet (informed kick) | −0.475 | −0.757 | −1.6110 | **+0.0890** |
| nomeasure (fixed kick) | −0.690 | −0.535 | −1.4926 | +0.2074 |
| noLOCC (coin-driven kick) | −0.584 | −0.463 | −1.2780 | +0.4220 |

**PRIMARY FAILED**: ΔE_B(qet) = +0.089, wrong side of zero (needed [−0.15, −0.05] at ≥5σ).
Bob's absolute energy did not drop below the ground baseline. **FALSIFIERS**: both controls
positive as pre-registered (+0.207, +0.422 — noLOCC above its +0.17 band edge).

## Why (quantitative)

Uniform contrast damping λ of both readout terms raises E_B toward zero because both terms
are negative: E_B ≈ λ·E_B(ideal). Measured λ ≈ 0.89 (⟨X_A X_B⟩ 0.907, ⟨Z_B⟩ 0.857 survival
in the qet arm). Absolute extraction requires λ > 0.943 (−1.803·λ < −1.700): a **5.7% total
noise budget** through ground prep + mid-circuit measurement + feed-forward. Exp194's arrow
meter measured τ_arrow ≈ 7.1µs on this fabric — a µs-scale feed-forward window alone spends
most of that budget. The −0.103 extraction is a 6% effect on a −1.7 baseline; fez cannot
currently clear it in absolute terms. The physics wasn't refuted; the budget was.

## What survived (post-hoc, labeled)

- **Ordering, at high sigma**: informed kick < fixed kick < coin-driven kick.
  qet − nomeasure = −0.118 (~4σ, per-arm SE 0.020); qet − noLOCC = −0.333 (~12σ, and these
  two circuits are gate-for-gate identical, differing only in WHICH bit drives the
  feed-forward). The information in the bit demonstrably moves energy the right way even
  when noise heating swamps the absolute level.
- **The frozen fact protects the record** (Exp193 echo): qet arm froze X_A into a classical
  bit early — its ⟨X_A X_B⟩ survived at 91%; noLOCC left A quantum through the feed-forward
  window — 82% survival. Copying to the classical record is decoherence-immunity.

## Exp195c scope (next flight, one careful derivation first)

Pre-register the **differential** as primary — the noise-robust observable:
E_B(qet) − E_B(noLOCC) ≤ −0.15 at ≥5σ, arms gate-identical (only the bit source differs).
**Required pre-work before flying**: a decoherence model splitting that gap into the
information effect (ideal −0.200 vs nomeasure; qet-vs-noLOCC ideal is also −0.200) and the
A-side decoherence asymmetry (frozen vs quantum A), so the pre-registered band claims only
the information part and does not launder a hardware artifact into the physics claim.
Alternative/adjunct: retune (h, k) to maximize extraction fraction |ΔE|/|E_B baseline|
within the 2-qubit Hotta bound, easing the λ budget.

## Discipline note

Selftest-clean → flew → primary failed → reported as failed. The gate class (4 pre-flight
catches this arc) tests circuit-vs-derivation; it cannot test hardware budgets — that is
what the pre-registered band is for, and it did its job.
