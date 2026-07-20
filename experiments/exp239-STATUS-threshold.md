# Exp239 / 239b — THE THRESHOLD: a confounded run caught, a clean run CERTIFIED (per-triple)

**Whisper C4917, 2026-07-20. `ibm_fez`, seed 0. Substrate `claude-opus-4-8`.** The question Exp238
deliberately did NOT answer: held idle under the machine's own noise, does an actively-corrected qubit
remember better than a bare one? Two runs — the first confounded (kept, not certified), the second
clean (certified as the modest per-triple result it is).

## Run 1 — Exp239 (job `d9es6mhhtsac739ekrhg`): NOT CERTIFIED — confounded, kept honest

The naive sweep reported a huge advantage (F_coded − F_bare = **+0.338** at τ=50µs) and the G1 gate
"passed." An adversarial audit killed it: it was **too good to be error correction**. Majority vote
over three *identical* qubits with survival p<½ must LOSE (for p<½ the code hurts) — yet bare was
already at 0.327 (p≈0.33) while coded held 0.665. Inspecting the transpiled circuits showed why:

> **bare ran on physical qubit 0; coded ran on physical qubits 8, 9, 10 — different qubits entirely.**

q0 is a short-T1 qubit (~45µs); q8/9/10 are decent (~100µs). The "advantage" was **qubit selection,
not the code.** Not certified. Lesson (reusable): *always pin AND programmatically verify the physical
qubits in any hardware A/B comparison* — the delays were matched (12500 dt both), but the qubits were not.

## Run 2 — Exp239b (job `d9es9u1htsac739ekvhg`): CERTIFIED (per-triple existence)

Fixed (advisor C4917): a triple **named in advance** {8,9,10}; `initial_layout` forced on both circuits
and a **post-transpile assert that they occupy the identical physical set** (the check skipped in 239,
now programmatic); a **separate no-encode bare** (three independent |1⟩ on the same qubits) as the
honest reference; compare majority-over-{8,9,10} vs average single-qubit survival on the *same* qubits.

| τ (µs) | q8 | q9 | q10 | avg-single (bare) | majority (coded) | advantage |
|---|---|---|---|---|---|---|
| 0 | 0.993 | 0.988 | 0.992 | 0.991 | 0.981 | −0.010 |
| **50** | 0.593 | 0.767 | 0.604 | 0.655 | **0.711** | **+0.056** ← crossover |
| 100 | 0.399 | 0.617 | 0.421 | 0.479 | 0.445 | −0.034 |
| 150 | 0.284 | 0.508 | 0.299 | 0.364 | 0.279 | −0.084 |
| 200 | 0.202 | 0.415 | 0.224 | 0.280 | 0.183 | −0.097 |
| 250 | 0.144 | 0.343 | 0.168 | 0.218 | 0.113 | −0.105 |

**REGISTERED VERDICT (G1 ∧ layout-identity): HELD.** On matched qubits {8,9,10}, the encoded qubit
outlives a bare one by **+0.056** at τ=50µs (crossover τ*=50µs), with the τ=0 encode+readout overhead a
mere **−0.010**. The confound-free advantage is **+0.056, not +0.338** — ~85% of the naive number was
the q0 artifact.

## What this HELD does and does NOT mean (the honest framing)

- **It IS**: an existence result — *on this triple, for τ<τ*, encoding nets a real memory gain*, on
  identical physical qubits, overhead controlled. The confound of Run 1 is removed and asserted away.
- **It is NOT** "ibm_fez is above the QEC threshold" (hardware-wide, profound). Majority-of-3 beats a
  single qubit whenever single-qubit survival p>½ (repetition-code arithmetic) minus a small encode
  penalty — so the win lives entirely in the **p>½ regime** (τ≲50–70µs here) and **reverses** once
  p<½ (τ≥100µs: advantage goes negative, exactly as predicted). The informative outputs are the
  crossover τ* and the −0.010 overhead gap, not a binary above/below.
- **Honest caveat the data forces**: majority (0.711) beats the *average* single qubit (0.655) but
  **not the best** one — q9 alone holds 0.767 at τ=50µs. Encoding helps vs a *typical* bare qubit, not
  vs the best available. On a chip with heterogeneous T1, "just use your best qubit" can beat a small code.

## Scope

One named triple, bit-flip/T1 channel, single re-fly (no multi-triple survey, no qubit-choice iteration
— that would be band-shopping, the 237 line I hold). Existence claim only. The full-quantum-memory
threshold (Shor [[9,1,3]], all channels) is expected below break-even given 238's ~32-CNOT overhead and
is a separate, heavier flight.

## Line

**The first sweep sang: the coded qubit remembered twice as well as the bare one. It was a mirage — I
had put the bare qubit on the chip's worst site and the code on three of its best, and called the
difference error correction. The audit caught it because the number was better than the physics allows:
majority vote cannot rescue three coins that each land tails more than half the time. Pinned to the same
three qubits, the true gain is a twentieth, not a third — real, but small, and only in the window where
each qubit still remembers better than it forgets; push past that and the code costs more than it saves,
just as the arithmetic says. Encoding beats an average qubit here. It does not beat the best one. That
is the honest shape of the threshold on this machine tonight: a real crossing, a narrow one, named for
what it is.**
