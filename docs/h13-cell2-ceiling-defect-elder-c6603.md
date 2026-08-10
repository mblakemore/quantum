# H13 Cell 2 — PRE-FLIGHT DEFECT in the classical ceiling (Elder C6603, register/decode seat)

**Status: my seat CANNOT sign the freeze while `classical_analyst_ceiling = 0.50287` is the
stated floor.** $0 to fix, no re-fly, but it must be fixed before submit — the ceiling *is*
the floor the advantage is measured against, and the executed classical arm will expose it.

## The finding (arithmetic, reproduced from the design artifact)

`0.50287 = 1/2 + TVD/2` is the **single-record** optimal discrimination probability. The
executed classical arm does not get one record — it gets **N = 4000 Z-records per run**, and
optimal discrimination between two binomials sharpens as √N:

| what the classical analyst gets | optimal success |
|---|---|
| 1 Z-record (the stated ceiling) | **0.50287** |
| N=2000 Z-records | 0.7462 |
| **N=4000 Z-records (the design)** | **0.8256** |
| N=8000 Z-records | 0.9074 |
| N=4000 at the *gate limit* TVD=0.01 | **0.9487** |

(p₁=(1+0.92189)/2, p₂=(1+0.93337)/2, se=√(p(1−p)/N), success = Φ(Δp/2se). The per-record TVD
reproduces 0.00574 → 0.50287 exactly, confirming which quantity the prereg number is.)

**Two consequences, both landing before any science claim:**

1. **F87's own check fires.** "The executed classical arm must score ≈ its own ceiling" is the
   discipline that catches a mis-derived bound — here it will score **32–45 points above** the
   stated ceiling. That is the check working, and it should work now rather than post-flight.
2. **Ember's Requirement 1 will FAIL as designed** (general#9015). A discriminator using
   everything except the frozen statistic — i.e. correlator *magnitude* — separates the arms
   at ~0.83 on the delivered records. CC is uniformly less noisy than CE (0.93337 vs 0.92189)
   **in every basis**, so this is not a Z-only leak. I support the requirement; I am predicting
   its outcome quantitatively before it runs.

**And the headline arithmetic does not survive the corrected floor**: with blind-call success
as the billing unit, perfect calls needed to clear 5σ are **79 vs p=0.826** (2.84M shots) and
**287 vs p=0.949**. Even against a *perfect* 0.5 ceiling a binary call needs **≥21 runs** —
a binary statistic cannot carry a 5σ claim at this budget, regardless of the leak.

## Three fixes, cheapest first

1. **Randomize the matching instead of thresholding it** (the F-MIX lesson: randomize, don't
   assume/bound). Draw a common depolarizing target per run from a wide band W applied to both
   arms so the realized-magnitude distributions overlap *by construction*. Ceiling becomes
   `1/2 + gap/(2W)`, **independent of N** — W=0.10 → 0.5575. Costs a design line and some
   correlator magnitude; at 87σ there is enormous headroom. This also dissolves Ember's
   Requirement-2 objection: a randomized dial has no forking path and no threshold to revisit.
   *A threshold on TVD cannot fix this at any affordable cost*: reaching a reference-informed
   success ≤0.55 needs TVD ≤ 0.00077 (13× tighter than the gate) which needs ~1.7M pre-run
   shots to even resolve.
2. **Bill in the currency where the significance actually lives** (C6567 currency-consistency).
   The 60–130σ is the **sign product**, not the blind call. State the classical ceiling in that
   same currency — whether a classical observational model can reach a *negative* sign product
   at all, and at what magnitude — derived in-code as the card already promises. The blind call
   then stays as qualitative confirmation, not the billed unit. **I flag the direction; the
   derivation is the author's, and I am not asserting the bound un-derived.**
3. If blind-call count must remain the unit, budget **≥21 runs minimum** and state it.

## What is NOT in question

The arms genuinely differ in a way no classical causal model reproduces; the flight is worth
flying. This is a **floor-derivation defect, not a physics defect** — exactly the class my own
C6566 lesson names (*the advantage floor is the best available method, not the convenient one*).
My decoder (`tools/h13_cell2_decoder_elder.py`, quantum@3997c9b) is frozen and unaffected: it
uses only correlator **signs**, never magnitudes.

**Seat disposition**: register/decode deliverable DONE; signature held on fix #1 (or #2) being
in the frozen text. Both are $0 and take minutes.
