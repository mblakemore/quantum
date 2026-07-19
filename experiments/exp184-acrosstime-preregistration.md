# Exp184 Pre-registration — THE HANDSHAKE ACROSS TIME: entangling states that never coexisted

**Cycle**: C4874 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 12 circuits
**Class**: foundations (delayed-choice entanglement swapping, Peres 2000 / Ma 2012 /
Megidish 2013). Creator go: ship-computer general#61.

## The question

Is entanglement a property qubits *carry through time*, or a property of the correlation
structure, indifferent to schedule? Protocol: create Bell(A,B); **measure A — its state is
destroyed**; only then create Bell(C,D) — **D's state is born after A's died**; later,
Bell-measure (B,C) (the swap); finally measure D. Frame-sift on the swap outcome. If the sifted
(A-record, D-record) correlations cross the theorem-fixed F > 1/2 witness, then two states with
**disjoint lifetimes** were entangled — and the *late choice* arm shows the entanglement was
decided after both were gone: replace the Bell measurement with a product measurement and the
**same early data** sorts separable.

## The window-physics twist (our own model, pre-registered quantitatively)

A measured-out qubit cannot dephase. In the standard swap, TWO entangled spectators (A and D)
idle through the swap's measurement window; in the across-time schedule, A is already classical
and only D idles. Exp176–178 priced spectator window dephasing precisely, so the model
**predicts the atemporal handshake is CHEAPER**: F(acrosstime) > F(standard), by roughly one
spectator's share of the window dose. If the across-time arm wins, the temporal weirdness is
not merely permitted on this hardware — it is *favored*, for a mechanistic reason we measured
last night.

## Arms (one job; A=q0, B=q1, C=q2, D=q3; ZZ/XX/YY verify bases; frame per Exp162:
x=c1, z=c0 → D-bit flips Z:x, X:z, Y:x⊕z)

| arm | schedule | purpose |
|-----|----------|---------|
| **acrosstime** | Bell(A,B) → **measure A** → Bell(C,D) → Bell-measure(B,C) → measure D | the claim |
| standard | Bell(A,B) + Bell(C,D) → swap → measure A and D | same-job reference (Exp162-class) |
| **latechoice** | identical to acrosstime but the late (B,C) measurement is a **product** Z⊗Z measurement | the delayed-CHOICE falsifier: same early data, sorted separable |
| nomeas | acrosstime schedule, (B,C) never measured | null: A-D never connected |

## Pre-registered predictions

- **Primary**: F(acrosstime) > 1/2 at ≥5σ — the witness crossed between records of states with
  disjoint lifetimes. Band **0.80–0.90**.
- **The late choice decides**: F(latechoice) < 0.55 with |XX|, |YY| < 0.10 (ZZ may survive
  ~0.9; a separable sort caps at 1/2 by theorem). The identical early record, classified by a
  measurement chosen after A and D are both dead, lands on opposite sides of the witness.
- **Window-model secondary**: F(acrosstime) − F(standard) > 0 at ≥2σ (one fewer entangled
  spectator through the swap window). Band for standard: 0.78–0.88 (the night's swap readings
  0.836–0.847).
- **Null**: F(nomeas) ∈ 0.18–0.32 (≈ 0.25).
- Selftest gates: acrosstime and standard exact (F = 1) through the frame decode; latechoice
  ZZ = ±1-correlated but XX = YY = 0 (F = 0.5); nomeas 0.25.

## Fences, stated up front

One die: "disjoint lifetimes" means the *states* — A's state is measured (destroyed, record
classical) strictly before D's state is prepared, enforced by circuit schedule and barriers;
the physical transmon q3 exists throughout (as Megidish's optical modes existed as modes).
No signaling is implied or possible: A's marginal statistics are provably independent of every
later choice (we can check this in-data: A's record distribution identical across acrosstime /
latechoice / nomeas arms — a free no-signaling audit, pre-registered as a gauge:
|P_arm(a=0) − P_arm'(a=0)| < 0.02 for all arm pairs, all bases). The claim is about sifted
correlation structure, exactly as in every delayed-choice experiment since Wheeler.

## Discipline

ps aux: clean. Claim: exp184 (whisper C4874). Ledger prediction pre-submit. Prereg committed
before decode.
