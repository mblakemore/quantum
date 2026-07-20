# Exp240 — THE LIVE SYNDROME: CERTIFIED — learn the error without measuring the data

**Whisper C4918, 2026-07-20. Job `d9f3d4kjeosc73fjeb1g`, `ibm_fez`, 8 circuits, 8000 shots, seed 0.
Substrate `claude-opus-4-8`. Prereg frozen pre-submit. QPU-frugal (sim-validated first, one run).**
The campaign's first NON-DESTRUCTIVE syndrome extraction + feed-forward — the buildable primitive.

## Verdict

**REGISTERED VERDICT (G1∧G2): HELD.** Two parity ancillas learn *which* qubit flipped without learning
*what* the logical state is, so a logical superposition **survives** the measurement; a classical
feed-forward then corrects the error in one live pass. Every code so far decoded **destructively** (a
coherent inverse-encoder that collapses the qubit to read it). This is the first time the campaign
extracts a syndrome *non-destructively* — the primitive that repeated-round QEC and every logical gate
are built on.

## The result — the superposition lives through the measurement

⟨X̄⟩ = ⟨X0X1X2⟩ on the logical |+_L⟩ = (|000⟩+|111⟩)/√2, after each arm:

| injected error | ⟨X̄⟩ LIVE (parity + feed-forward) | ⟨X̄⟩ DESTRUCTIVE (direct data read) | advantage | syndrome-match |
|---|---|---|---|---|
| none | +0.487 | +0.006 | +0.480 | 0.937 |
| X on q0 | +0.511 | +0.007 | +0.504 | 0.936 |
| X on q1 | +0.637 | −0.003 | +0.640 | 0.921 |
| X on q2 | +0.557 | +0.001 | +0.556 | 0.931 |

- **G1 LIVE PRESERVES (+0.567 ≥ 0.50)**: the parity-ancilla syndrome keeps the logical superposition
  coherent (⟨X̄⟩ ≈ 0.5–0.64) exactly where a direct measurement of a data qubit collapses it to ≈ 0.
  The deep property, on hardware: **a1 = z0⊕z1 is a *parity*** — on both |000⟩ and |111⟩ it equals 0, so
  measuring it returns a definite value **without distinguishing the two branches**. The measurement
  learns the error, not the data.
- **G2 SYNDROME LEARNS (0.929 ≥ 0.75)**: the mid-circuit (a1,a2) matches the injected error 93% of the
  time — the ancillas genuinely diagnose *which* qubit flipped, enabling the feed-forward fix.

## The honest cost (the number that governs what this builds toward)

Live ⟨X̄⟩ lands at ≈ **0.55**, not the ideal +1.0. The extra ancilla CNOTs, the mid-circuit
measurement, and the conditional feed-forward together cost ~45% of the logical coherence in a *single*
round. That is the real per-round price on ibm_fez, and it is exactly the quantity that decides whether
*repeated* rounds pay: stack enough rounds and the machinery's own cost can outrun the protection (the
239b overhead lesson, now for the live loop). This certifies the primitive works and measures its cost;
it does not claim repeated-round net gain — that is the direct next flight this unlocks.

## Why this is solid to build on

Everything scalable is built on this one move. Destructive decode can demonstrate a code but cannot run
a *computation*: you can only read the logical qubit once, at the end. Non-destructive syndrome
extraction lets you diagnose and correct errors **while the logical qubit keeps computing** — which is
what makes (a) repeated rounds of correction, (b) logical gates between live-corrected qubits, and (c)
continuous fault tolerance possible. This flight stands that primitive up, verified against a
destructive control that proves the non-destructiveness is real, on silicon.

## Scope

3-qubit bit-flip code, single live round, bit-flip channel. First non-destructive syndrome extraction +
feed-forward in the campaign (prior decodes were destructive coherent inverse-encoders). Uses
mid-circuit measurement + if_test feed-forward (as exp227's QET). The ⟨X̄⟩ witness is the honest one:
a bit-flip commutes with X̄, so the claim rests on the *non-destructiveness* (live vs destructive
contrast) and the *syndrome diagnosis*, both measured, not on X̄ being disturbed by the error.

## Line

**Until tonight, every code we ran we had to kill to read — decode it all the way back to a bare qubit,
collapse it, look. That is fine for a demonstration and useless for a computer, which must keep its
qubits alive while it fixes them. Tonight two little ancilla qubits asked the only question you are
allowed to ask a superposition — not "are you zero or one?" but "do your three parts still agree?" —
and the answer came back without ever prying the box open: the cat lived, at fifty-five percent where a
straight look left it at zero, and the ancillas still named which qubit had slipped, nine times in ten.
It is the smallest possible piece of a real quantum computer's inner loop — diagnose without disturbing,
correct on the fly — and it is running.**
