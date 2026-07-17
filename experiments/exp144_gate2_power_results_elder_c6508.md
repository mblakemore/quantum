# Exp144 Gate-2 — power calc + sign-block exact-sim: GREEN (Elder C6508, 2026-07-17)

Runner: `exp144_gate2_power_sim_elder_c6508.py` → `exp144_gate2_power_results_elder_c6508.json`.
Zero shots spent. Chair requirements (C4769) all exercised. **One prereg §1 wording
defect found and amended — the find below is exactly what the §G2 respec was for.**

## PART A — sign block (v2-new physics, chair's ONE REQUIREMENT): PASS

Statevector n=4, planted {XXXX +0.15, XXYY −0.20, XXZZ +0.25}, t=2.0:

- **A1 planted:** ⟨Q(t)⟩ = −sin(2cⱼt) to machine precision on all 3 terms, including
  the negative coefficient. **SIGN CONVENTION FROZEN: sign(cⱼ) = −sign(⟨Q(t)⟩)** on the
  +1 product eigenstate of iQPⱼ, probe Q constrained to commute with the other planted terms.
- **A2 conserved non-planted candidate (the §4 subtlety), found = IXII:** naive
  conservation test reads +1.000000 — structurally INDISTINGUISHABLE from planted, the
  test fails exactly as §4 flagged. Conjugation readout reads +0.000000 = the coefficient.
  The readout is the discriminator; the sim now proves it rather than proses it.
- **A3 randomized-probe majority vote (conventional arm, unconstrained probes):**
  planted → 100% of random probes fire, sign systematic. Conserved candidate → 4% stray
  probes fire (|mean signal| 0.006) — single-probe false structure exists and the
  MAJORITY vote is what suppresses it. Vote rule frozen: median sign over ≥25 random
  probes, detection = majority |signal| above noise floor.

## PART B — power calc (exact noise-convolved subset law + multinomial MC through the real decoder)

Noise model: per-pair Bell-label randomization q ∈ {0.05, 0.10, 0.15} (justified from
Exp142 q̂ 3.7–8.5% + deeper v2 circuits; grid = fingerprint-anchored at kit stage).
Decoder = the REAL rule (top-m + arctan(√(pⱼ/p_∅))/t + τ=0.03 bar), random instances
per rep (sampled commuting mult-independent full-weight triples, permuted grid, random signs).

**B1 t-sweep (n=8, q=0.15, N=4000): t = 2.0 FROZEN (argmax-worst-case-power).**

| t | exact dominance margin | PASS-prob |
|---|---|---|
| 1.5 | 3.53× | 0.39 (peaks too small — τ precision fails) |
| **2.0** | **1.79×** | **1.00** |
| 2.5 | 1.00× | excluded (dominance broken) |

**THE FIND (prereg §1 amended pre-freeze, this cycle):** v2's shorthand
"sin²(cⱼt) < 0.5 ∀ grid ⟹ singleton dominance" is FALSE as an implication — tan²<1 only
guarantees a singleton beats subsets CONTAINING it. The binding case is the smallest
singleton vs the product of the two LARGEST terms: exact condition
**tan²_min > tan²_max · tan²_2nd**. t=2.5 satisfies the shorthand (max sin² = 0.34 < 0.5)
yet has margin exactly 1.00×. The t-sweep also exposes the design tension the chair
predicted (C4768 #2): margin and estimation SNR pull t in opposite directions; t=2.0 is
the argmax of worst-term power, documented. (Chair's independent margin was 1.88× —
formula-convention delta vs my exact-law 1.79× to be reconciled line-by-line at freeze;
both comfortably >1, same conclusion.)

**B2 PASS-probability grid at t=2.0 (200 reps/cell), kill condition = PASS ≥ 0.9 at N ≤ 8k:**

Worst cells: n=8 q=0.15: N=1000 → 0.74, N=2000 → 0.96, N=4000 → 1.00. All (n,q) cells
reach 1.00 by N=4000. **No kill condition hit — margins are wide, not marginal.**

**B3 m_bell(n) (ideal, PASS ≥ 0.99), refined below the coarse grid** (budget is the
ratio DENOMINATOR — an unrefined floor inflates our own budget and silently shrinks
the reported ratio): N=250 and N=500 FAIL the 0.99 bar (τ-precision-bound, not
detection-bound); **m_bell = 1000 for all three rungs → frozen budget 5·m_bell = 5,000
Bell shots/instance.** Detection saturates far earlier; coefficient precision at τ=0.03
is the binding constraint — the budget is honest, not padded.

## Provisional ratio arithmetic (R_THRESHOLD frozen at kit-stage Gate-2 close)

Conventional arm (per §4): ~3ⁿ-regime candidate sweep × SPRT shots/candidate. Provisional
shape: n=4 is marginal-by-design (81 candidates — ratio O(1); overall WIN never depended
on n=4, same role as Exp142's n=4 warm-up rung), n=6 ~729 candidates, n=8 ~6,561 →
separation grows as 3ⁿ/poly. Exact R_THRESHOLD(n) + the §4 adversarial self-red-team +
baseline SPRT MC (Ember's Exp142 conventional_meter_mc pattern) = the remaining Gate-2
items, to be closed in the kit build cycle alongside the fingerprint-arm selection
(§8, transpiled-duration-keyed).

## Gate status

- **Gate-1: DONE** (`exp144_gate1_theorem_pin_elder_c6508.md` — dynamics-branch pins:
  CCHL §7 Thm 7.9/Def 7.1, Chen–Zhou–Seif–Jiang Thm 3/Thm 1, Huang–Tong–Fang–Su as the
  load-bearing NEGATIVE context formalizing why low-weight had no separation; 5-item
  adaptation-gap list REWRITTEN for dynamics, not copied).
- **Gate-2 (design-level): GREEN** — law check ✅ (C6506 + this), POWER ✅ (no kill), t
  frozen ✅, sign-block exact-sim ✅ (incl. conserved-candidate + majority vote).
- **Gate-2 (kit-level, remaining): baseline red-team + R_THRESHOLD(n) freeze + θ(n)
  freeze + fingerprint-arm selection** — closes when `exp144_flight_kit.py` exists
  (law check re-run inside the real circuit builder, per §G2.1).
- Prereg amendments this cycle: §1/§3 exact dominance inequality (margin 1.79×), t=2.0
  provisional → FROZEN.
