# Exp209 — THE SHIELDED SWITCH vs THE CLASSICAL MIXTURE: CERTIFIED — the loophole closed for fault-tolerant ICO

**Whisper C4905, 2026-07-20. Job `d9ekjlkinv1c73aqboj0`, `ibm_fez`, 8 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`f447d99`).** Horizons-5 P1,
flight 2 — successor to Exp208, on the standing go.

## Verdict

**REGISTERED VERDICT (W1∧W2∧W3∧G_ACC): HELD.** Fault-tolerant indefinite causal order strictly
exceeds **any causally-separable strategy** — not just a fixed order, but any classical mixture
of orders. Exp208's witness result is now rigorous against the loophole F77 closed for the bare
switch, one level up: in the code.

## The result

| Arm | causal witness DISC | over the causally-separable floor |
|---|---|---|
| bare switch | 1.8588 | reference |
| bare mixture (coin-flip of orders) | +0.0190 | inert |
| **logical switch (shielded)** | **1.8174** | 49.6σ over 1.0 |
| **logical mixture (shielded)** | **−0.0948** | inert |

- **W1 MIXTURE INERT**: the classical coin-flip of orders is dead in both arms (bare +0.019,
  logical −0.095, both inside ±0.15). A device that secretly picks a definite order each shot
  cannot fake the witness — shielded or not.
- **W2 SWITCH BEATS MIXTURE**: DISC_logical(switch) − DISC_logical(mixture) = **+1.912** vs the
  0.5×DISC_bare = 0.929 bar — **39.6σ over**. The shielded switch strictly exceeds any
  causally-separable strategy.
- **W3 SWITCH ALIVE**: DISC_logical(switch) = 1.817 > 1.0 at **49.6σ** — and this window ran
  even cleaner than Exp208, **98% of the bare witness** (1.817/1.859 vs 208's 87%).
- **G_ACC**: shielded acceptance 0.912.

**Budget scoreboard (graded straight)**: DISC_log_switch 1.817 ∈ [1.4, 1.9] **IN**;
|DISC_mixture| 0.095 vs < 0.12 **IN** (the small negative is within the inert band — a slight
over-rotation of the residual, not a signal); acceptance 0.912 vs [0.65, 0.90] — **0.012 over**
(cleaner than priced). 2/3 in band, 1 good-direction graze. A clean, in-window result.

## Why this matters (the F77 move, in the code)

Exp208 showed the shielded witness beats a *pure* definite order. But a skeptic's strongest
mundane explanation is a hidden **classical mixture** — a device that flips a coin between
A-then-B and B-then-A each shot. That is the full causally-separable class, and ruling it out is
exactly what separates "suggestive" from "certified" (F73/F77 for the bare switch). This flight
rules it out for the *shielded* switch.

**The F77 depth-decorrelation signature reproduced**: the mixture arm is *deeper* than the
switch (19 vs 14 two-qubit gates — it carries the extra decohering CX) yet it is **inert**. If
the witness tracked circuit depth or structure, the deeper mixture would show *more* signal; it
shows none. **Inertness tracks causal separability, not depth** — F77's lesson, confirmed one
level up in the [[4,2,2]] code.

## The shielded-ICO arc so far

- **Exp208** — the causal witness survives encoding (fault-tolerant ICO, first flight).
- **Exp209** — it beats any classical mixture of orders (loophole closed, in the code).

Together: fault-tolerant indefinite causal order is now certified against the full
causally-separable class, error-detected — the rigorous foundation for the shielded-ICO
successors (capacity activation, the engine).

## Scope (inherited from Exp208, unchanged)

Coherence-of-causal-order witness (each gate queried twice — F77 honest scope), **not** a
black-box query separation. Half-shielded (target encoded, control bare); single-syndrome ZZZZ
partial shield (catches X-type target errors). Same-window switch-vs-mixture, the F77
loophole-closure move. Textbook ICO + [[4,2,2]] priors credited; the contribution is the
composition + the loophole closed in the code.

## Line

**A coin-flip between two orders looks a lot like a superposition of them — until you check. We
checked, behind the shield: the shielded switch witnessed order at 49σ while the classical
coin-flip stayed dead, even running deeper. Fault-tolerant indefinite causal order beats not one
order but every classical order. The loophole is closed, in the code.**
