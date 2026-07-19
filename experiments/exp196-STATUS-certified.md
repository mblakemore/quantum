# Exp196 THE SHIELDED VERDICT — CERTIFIED: logical CHSH violated at 30σ (C4888)

Job `d9e79thhtsac739dteu0`, ibm_fez, 8000 shots × 12 circuits. All five pre-registered gates held.

## Result

| arm | Z̄Z̄ | Z̄X̄ | X̄Z̄ | X̄X̄ | S_L1 | S_L2 |
|---|---|---|---|---|---|---|
| logical | +0.975 | −0.002 | +0.013 | +0.989 | **2.7779** | 1.382 |
| nocx | +0.006 | −0.015 | +0.995 | −0.023 | −0.025 | 1.442 |
| bare | +0.951 | −0.045 | −0.012 | +0.972 | 2.7195 | — |

- **PRIMARY**: S_L1(logical) = 2.7779 vs classical bound 2 → **30σ**, inside band [2.40, 2.85],
  under Tsirelson 2.8284. Exp191's contrast predicted ~2.79; it landed there.
- **INTERNAL CONTROL**: L2, the product logical pair riding the same shields in the same
  shots, sits at 1.382 ≈ √2 — BELOW the classical bound, exactly where a non-entangled pair
  must sit. ✓
- **NULLS**: mixed-basis logical correlators −0.002 / +0.013 (band ±0.15). ✓
- **FALSIFIER**: remove the transversal CNOT → L1 dead (−0.025) while L2 stays at √2 (1.442). ✓
- **REFERENCE**: bare physical pair 2.7195 — the shielded logical pair beat the unshielded
  physical one by +0.058 (descriptive; same direction as Exp191's post-hoc finding, now
  reproduced).
- **GAUGES**: per-basis acceptance 0.71–0.83 (floor 0.70). ✓

## What was demonstrated

Two error-detecting [[4,2,2]] shields, entangled by a transversal CNOT, share correlations
that no local-hidden-variable account allows — the full CHSH bound (not just the separable
witness of Exp191), violated at 30σ at the LOGICAL level, with the in-shot product pair
calibrating exactly where the bound sits. Scope as pre-registered: expectation-value CHSH
(settings by linearity from four measured logical basis pairs), no locality/detection
loopholes closed, logical-level fair sampling via stabilizer postselection.

## Process notes

- **C4887 hardware-budget rule, first application, worked**: λ_req = 0.707 vs measured
  λ ≈ 0.985 → flew and landed dead-on prediction. Contrast with 195b (λ_req 0.943 vs 0.89 →
  failed): the rule discriminates feasible from infeasible absolutes BEFORE spending QPU.
- Shields arc extended: SHIELDS UP (189) → SHIELD PAYS (190/b) → HANDSHAKE (191, witness) →
  TRANSPORTER (192) → **VERDICT (196, CHSH)**. Nonlocality — the strongest correlation
  certificate — survives the armor, and the armor helps (beats bare, twice now).
