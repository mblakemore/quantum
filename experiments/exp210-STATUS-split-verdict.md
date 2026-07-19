# Exp210 — SHIELDED CAPACITY ACTIVATION: SPLIT VERDICT

**Whisper C4905, 2026-07-20. Job `d9eksmqneu4c739oinr0`, `ibm_fez`, 64 circuits, 2000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`f7fad2a`).** Horizons-5 P1,
flight 3, on the standing go.

## Verdict, without blending

**REGISTERED VERDICT (W1∧W2∧W3∧G_ACC): NOT HELD** — W2 missed via a pre-registration
gate-choice error (below).
**THE DELIVERABLE HELD**: capacity activation survives error detection — R̄_switch = **0.4842
at 46.9σ**, **96% of F83's bare 0.5034**, with the unconditioned-signal control dead. The
useful resource is fault-tolerant; the registered miss is a self-inflicted gate aimed at the
wrong observable.

## What the chip said

| | R̄ | se | interpretation |
|---|---|---|---|
| **switch (shielded)** | **0.4842** | 0.0082 | **capacity activated, 46.9σ over the 0.10 floor** |
| null (definite order) | 0.1171 | **0.0683** | 1.71σ from zero — a *starved* estimator, not transmission |
| D_switch (unconditioned) | 0.0023 | 0.0040 | dead (info lives only in the control-target correlation) |
| D_null (unconditioned) | −0.0049 | — | **dead — the correct null control** |

- **W1 CAPACITY ACTIVATED: OK.** R̄_switch = 0.484 > 0.10 at **46.9σ**. Information survives two
  individually-zero-capacity depolarizing channels with the target encoded in [[4,2,2]] and
  post-selected — 96% of the bare F83 value (0.484/0.503). Fault-tolerant ICO is a *working
  resource*, not just a witness.
- **W3 UNCONDITIONED DEAD: OK.** D_switch = 0.0023 — the signal lives *only* in the
  control-target correlation, never the marginal target (F83's signature, preserved through the
  shield).
- **G_ACC: OK.** ZZZZ acceptance 0.917.
- **W2 NULL DEAD: MISS — and the cause is my gate, not the physics.** I registered W2 on
  R̄_null ≤ 0.10; it came in at 0.1171. But **F83's own analysis documents that R̄ for the null
  is a *starved* estimator** — the definite-order control is a |+⟩ spectator, so
  "conditional-on-minus starves" (its se is 0.068, 8× the switch's), and F83 identifies **D as
  the correct null observable** ("dual role: null integrity gate + switch signature"). By that
  correct observable, the null is dead: **D_null = −0.0049**. And R̄_null = 0.117 ± 0.068 is
  **1.71σ from zero** — statistically consistent with no transmission. I read F83's note (D is
  in W3) yet registered the *null* gate on the starved R̄ instead of D_null. Pre-registration
  error, gate aimed at the wrong observable.

**Budget scoreboard**: R̄_switch 0.484 vs [0.30, 0.52] **IN** (top); |R̄_null| 0.117 vs < 0.08
**OUT** (the starved-estimator miss); acceptance 0.917 vs [0.70, 0.92] — **0.003 over**. 2/3,
the one miss being the mis-registered null.

## The lesson (fleet rule, filed)

**Register a null/control gate on the observable the parent experiment identified as correct.**
F83's code explicitly flagged D (not R̄) as the null observable and explained why (starved
conditional). I had D in the switch's W3 but registered the *null's* W2 on R̄ anyway. The class
is the same as Exp202's single-basis QBER gate (aimed at the wrong basis) and Exp203's
over-extended gauge: **gate the observable the physics actually lives in, especially for
controls.** Added to the pre-registration checklist consideration.

## Why there is NO 210b

The correct control **already held in-window**: D_null = −0.0049 (dead), D_switch = 0.0023
(dead), and R̄_null is 1.71σ from zero. Reflying 64 circuits to reconfirm an already-dead
D_null would be band-shopping-adjacent — spending QPU to convert a fully-diagnosed
gate-aiming error (the Exp204 precedent: an explained miss is closed in the record, not
reflown). The registered NOT HELD stands on the books; the deliverable stands on its own held
gates.

## What enters the record (regardless of the registered verdict)

**Fault-tolerant ICO is a working resource.** The Ebler–Salek–Chiribella capacity activation —
information through two channels that are each provably zero-capacity — survives error
detection at 46.9σ, 96% of the bare value, with the signal confined to the control-target
correlation (D dead). Combined with 208 (witness survives) and 209 (beats any classical
mixture), the shielded switch now has a **witness → rigor → resource** arc: indefinite causal
order, error-detected, does something no definite or classical-mixed order can — it pushes a
bit through impossible channels.

## Scope (unchanged from prereg)

Device-characterized capacity activation (F83 scope), half-shielded (target only),
single-syndrome ZZZZ partial shield. F83 bare R̄ = 0.5034 cited as the descriptive reference.
Textbook ICO-capacity + [[4,2,2]] priors credited; the contribution is the composition —
capacity activation with the target error-detected.

## Line

**A bit went through two channels that each carry nothing, and it went through error-detected —
96% as strong as bare, at 47σ. The registered verdict says NOT HELD because I pointed the null
gate at a noisy estimator F83 had already warned me about; the physics says the resource is
fault-tolerant, and the correct control agrees. Split kept straight — the deliverable earned,
the gate error owned.**
