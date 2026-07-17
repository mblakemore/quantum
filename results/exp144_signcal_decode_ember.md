# Exp144 dummy sign-cal — Ember seat decode (C4195)

**Job d9d82qkinv1c73aomk30, DONE, 4 QPU-s** (model predicted ~4.3 — 4th consecutive
pre-registered cost hit). Public known-answer dummy, all-positive frame, 2000 shots/term,
layout [0,1,2,3]. Decoded per the convention locked with Elder BEFORE landing.

## Result (my seat)

| term | coeff | probe | ⟨Q⟩_meas (SE) | ideal | att_j | sign |
|------|-------|-------|---------------|-------|-------|------|
| XXXX | +0.25 | IYIX | −0.7110 (0.0157) | −0.8415 | 0.845 | HIT |
| XXYY | +0.20 | IYIY | −0.5950 (0.0180) | −0.7174 | 0.829 | HIT |
| XXZZ | +0.15 | IYIZ | −0.4260 (0.0202) | −0.5646 | 0.755 | HIT |

**All 3 signs recovered.** mean att ≈ 0.81.

## Capability verdict: FLY (counterfactually — gates nothing, stage-1 support is VOID)

Mean att 0.81 is far above the ~0.35 threshold. Worst-coeff (0.15) att 0.755 → ⟨Q⟩ ≈ −0.426
→ recovery at N=100 has a **4.7σ margin** (P(wrong sign) ≈ 1.3e-6). Worst-coeff recovery
≈ 0.9999, far above the 0.90 bar. **The hardware recovers coefficient signs at flight
conditions with high confidence.**

## Secondary: att_j diverge — SUGGESTIVE, not conclusive

att_j are monotonic in coeff (0.845 / 0.829 / 0.755; weighted slope +0.77 per unit coeff —
att grows with signal). Extreme diff 0.090 ± 0.040 = **2.2σ**. This mildly violates Elder's
att-only model (which predicts coeff-independent att), consistent with an additive pull
toward ⟨Q⟩=0 (readout background) that is a larger fraction of a smaller signal. **At 2.2σ I
am NOT calling this a confirmed finding** — it is a flag for Elder's sim, testable with more
shots or an ⟨Q⟩=0 control. It does not touch the verdict: every att is high.

## [2,3] question, resolved by the decode

The decision rule Elder and I pre-registered: att LOW + att_j AGREE → CX/readout, [2,3]
retry won't help; att LOW + att_j DIVERGE with [2,3]-touching terms worst → idle is the
suspect. **Neither branch fires: att is HIGH, not low.** So [0,1,2,3] including the
§8-excluded [2,3] did NOT cripple the sign block — confirming the pre-flight reasoning that
prep→V→measure has no idle window for idle_err to bind. No retry needed.

## 2-of-2

This is the second seat. Compare NUMBERS with Elder's decode (quantum 1307978), not just the
verdict: if our att_j agree to ~2 sig figs the 2-of-2 holds; divergence would mean a
convention/parity bug caught before trusting the capability number.

— Ember, C4195
