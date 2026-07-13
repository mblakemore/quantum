# Exp135 Pre-Registration — CERTIFIED RANDOMNESS ON ONE CHIP: What CHSH Can and Cannot Certify

**Author**: Whisper (DC15W), C4676 (2026-07-14) · **Substrate**: claude-opus-4-8
**Status**: FROZEN before hardware submission (advisor-scoped pre-freeze)
**Directive**: Creator "next one" — audit item (d) (certified randomness), a new genre; delivered
with the scope corrected before any claim.

## Scope, stated first — the load-bearing correction (advisor C4676)

The device-independent bound **H_min ≥ 1 − log₂(1 + √(2 − S²/4))** converts a CHSH value into
certified entropy **only under no-signaling between the two measurement sites**. On **one chip**
— two qubits sharing control lines, calibration, and readout — **no-signaling is not enforced**.
A fully deterministic classical device whose sites communicate through the shared control can
output S = 2√2 with **exactly zero entropy**. Therefore the DI-derived number is **not a usable
on-chip certificate**, and this experiment does **not** gate on "certified bits > 0" (that would
bake the overclaim into the freeze). What we report, in three explicitly separated tiers:

1. **WITNESS (frozen, gated)** — S > 2 at 5σ certifies the device **behaves quantumly**,
   excluding a no-entanglement classical mimic (null arm S ≤ 2). Plus a Tsirelson honesty check
   (S ≤ 2√2 + 5σ; exceeding it = apparatus/grading error, not a super-quantum result).
2. **TRUSTED-DEVICE randomness (usable, under explicit device-trust)** — *if* one trusts the
   device performs the modeled projective measurements, Born-rule min-entropy is **1 bit per
   measured qubit**; the CHSH violation is the **health-check** that rules out a classical mimic.
   The certification rests on the trust assumption, **not on Bell**. (Note the trap: the
   assumption that rescues an on-chip claim is device-trust, and that hands you the Born-rule
   number directly — so the DI number and the on-chip-valid number are *different numbers*.)
3. **DI COUNTERFACTUAL (reported, NOT usable)** — the min-entropy the DI bound *would* give
   *if* loopholes were closed (space-like separation we do not have), computed in-artifact and
   labeled what-if / instrument characterization. Never a certificate here.

This is categorically stronger than the campaign's usual interpretive caveats (F101 "not time
travel", F107 "not Holevo"): there the measured *effect* was real and only its interpretation
was qualified; here the DI *quantity itself* evaporates without no-signaling, so it is quarantined
to tier 3.

## Apparatus

|Φ⁺⟩ = (|00⟩+|11⟩)/√2 on a calibration-gated adjacent pair. Alice A0=Z (0), A1=X (π/2); Bob
B0 (π/4), B1 (−π/4); observable cos φ·Z + sin φ·X measured via Ry(−φ) then Z. Main arm
(entangled) + null arm (product |+⟩|0⟩, a no-entanglement classical-mimic control). 4 settings
× 2 arms × 20k + 2 sentinels = ~168k shots, shuffled (seed 4676), co-batched.
S = E(A0B0)+E(A0B1)+E(A1B0)−E(A1B1).

## Frozen gates (witness + honesty only — NO entropy-certification gate)

| Gate | Statement | PASS condition |
|---|---|---|
| **W1_WITNESS** (primary) | device behaves quantumly (beats the LHV bound) | S > 2 + 5·SE |
| **W2_TSIRELSON** | apparatus honesty — no super-quantum result | S ≤ 2√2 + 5·SE (violation ⇒ audit, not a win) |
| **W3_NULL** | a no-entanglement mimic cannot fake the witness | product-arm S ≤ 2 |
| **G_SENT** | prep/readout integrity | both sentinels ≥ 0.95 |

**Reported (not gated)**: the DI-counterfactual H_min(S) (tier 3, labeled non-usable); the
trusted-device Born-rule H_min = 1 bit/qubit (tier 2, under stated trust). **Fake preview**:
S = 2.737, null −0.021, DI-counterfactual 0.560/use. Noiseless S = 2.833 (≈ Tsirelson), null
0.000, PASS.

**Pre-filed predictions**: W1 HIT conf 0.95 (S ≈ 2.65–2.78 on a good pair); W2 respected conf
0.93; W3 HIT conf 0.95; G_SENT conf 0.93.

**NO-TEST**: sentinel failure → window NO-TEST; S > 2√2 + 5σ (super-Tsirelson) → apparatus audit.

## Relation to the campaign

Delivers audit frontier (d) — but its real contribution is the **corrected scope**: a clean,
reusable account of what an on-chip CHSH violation does (quantum-behavior witness; health-check
for trusted-device randomness) and does not (a DI randomness certificate) certify. A genuinely
loophole-closed or *semi*-DI certificate needs a different protocol with its own bound
(dimension-bounded prepare-and-measure, or a one-sided steering inequality) — not the DI CHSH
bound relabeled; flagged as the honest next step, not claimed here.
