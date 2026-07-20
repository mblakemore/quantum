# H6-P4 — THE REPLICATOR'S PURIFIER: detection purifies the injected magic (the distillation seed)

**Whisper C4926, 2026-07-20. No new QPU** — a re-analysis of Exp243's magic-injection job
(`d9f5ahhhtsac739evee0`, ibm_fez), on the Creator's "run P4". The C4921 move (raw vs postselected),
applied to magic instead of a Bell pair.

## The question

Real fault tolerance needs a *magic factory* — **distillation**, taking noisy magic states to clean
ones. The full factory ([[15,1,3]] 15-to-1) is depth-blocked on ibm_fez. But the *seed* costs nothing:
does error **detection** — postselecting on the [[4,2,2]] stabilizers — improve the fidelity of an
injected magic state? If the *accepted* magic is cleaner than the *raw* magic, detection purifies, and
that is the first rung of the factory.

## The result — yes, detection purifies the magic toward the ideal

⟨X̄_A⟩ of the injected state, raw (all shots) vs postselected (XXXX_A & ZZZZ_B), from 243's job:

| injected | raw ⟨X̄⟩ | postselected ⟨X̄⟩ | purification (|Δ|) | acceptance |
|---|---|---|---|---|
| I | +0.881 | +0.996 | +0.115 | 0.83 |
| **T (magic)** | **+0.609** | **+0.690** | **+0.081** | 0.83 |
| S (Clifford) | −0.009 | −0.018 | +0.010 | 0.84 |
| Z | −0.868 | −0.993 | +0.126 | 0.81 |
| no-CNOT | +0.968 | +0.998 | +0.031 | 0.89 |

**Ideal magic |⟨X̄⟩| = cos(π/4) = 0.707.**

- **The magic state is purified**: detection lifts the injected T's ⟨X̄⟩ from **0.609 (raw)** to **0.690
  (postselected)** — toward the ideal 0.707, recovering **~83% of the error-induced gap** (0.098 raw
  shortfall → 0.017 after detection), at the cost of discarding ~17% of shots (acceptance 0.83).
- **The effect is systematic**: every non-trivial state is purified *toward its ideal* (I → +1, Z → −1,
  magic → 0.707); the Clifford S point sits at 0 (a stabilizer axis) with nothing to purify. Detection
  removes the errored shots that had dragged each state off its target.

## Scope (honest)

- **This is detection-purification, NOT true distillation.** Postselection *discards* the shots that
  trip the stabilizer check — it improves the *accepted* state's fidelity, bounded by what a single
  detectable error can move, at an acceptance cost. **True distillation** (a [[15,1,3]] code) improves
  fidelity *beyond any input* and *compounds* across rounds — that is the depth-blocked factory, named
  not flown. This is its conceptual seed, measured.
- **A snapshot, not a constant** (the P2/245 lesson): the *magnitude* (+0.081) is drift-dependent and
  would move with hardware conditions. The **sign is robust** — detection always purifies toward the
  ideal, because it removes error, not signal.

## What it means

The magic state is the *fuel* of universal quantum computation (243 injects it; 244 steers it). Its
fidelity sets the quality of every injected T. This flight shows the shield does not merely *carry* the
magic — it *cleans* it: the accepted magic is closer to ideal than the raw magic. That is the first,
smallest step of the magic factory, and it came free — read from the job we already ran, in the shots we
would have thrown away.

## Line

**We already knew the shield could carry magic without breaking it; the question here was gentler and
stranger — can throwing away the broken shots make the surviving magic *better*? It can: the injected T
came off the raw chip at 0.61, and the same T, kept only on the runs the code declared clean, sits at
0.69 — a little closer to the perfect 0.71 it was always trying to be. It is the humblest possible
version of a magic factory: not a machine that manufactures purity, just a sieve that keeps the good
grain — but every distillery starts with a sieve, and ours works, for free, on a job already flown.**
