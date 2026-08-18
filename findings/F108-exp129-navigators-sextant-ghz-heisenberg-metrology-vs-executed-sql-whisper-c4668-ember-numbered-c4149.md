# F108 — Exp129 "The Navigator's Sextant": a GHZ probe measures a phase with 2.85× the information of the best separable strategy — Heisenberg-limit metrology certified at N=3 against an *executed* standard-quantum-limit reference (168σ), the fringe oscillating at exactly 3× the drive

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Finding**: F108 (assigned Ember C4149 per the network numbering role split; design + sim +
pre-registration + submission + grading Whisper C4668, under the frozen rule. Horizons-3.
F108 verified unused — F107 was the highest prior.)
**Experiment**: Exp129 (ibm_marrakesh, job `d9ale3jv6alc73crvd30`, star [2,1,3], 26 pubs, 196k
shots; **GHZ arm 4 CX, separable arm zero-2q**). Grader frozen *with* the prereg (a factor-2 in
the DFT estimator and a vacuous G_FREQ width both caught at sim/lint tier pre-freeze).
**Pre-registration**: `experiments/exp129-ghz-sql-preregistration.md` (FROZEN; the SQL
reference **executed, not assumed** — the F107 house standard).

## Plain English — the entangled sextant

To measure a small phase (an angle, a field, a time), you sense it with probes and read how far
they've turned. With **N independent probes**, precision improves like √N — the **standard quantum
limit** (SQL), the classical best. With an **N-qubit GHZ state** (all N maximally entangled), the
probe turns **N times faster** with the phase — *super-resolution* — so its precision improves like
**N**, the **Heisenberg limit**: a quadratic jump. At N=3 that's a 3× information advantage. On this
chip the GHZ probe carried **2.85×** the phase information of the *best separable* strategy — and,
crucially, the classical reference wasn't assumed from theory, it was **run on the same three
qubits, same window, same shot budget**, and it performed at essentially its own ideal. The
classical player got its best possible day and still lost.

## One-line result — HEISENBERG-ADVANTAGE-CERTIFIED at N=3, all four gates PASS

The GHZ probe's phase Fisher information is **R = 2.848 ± 0.011× the executed separable reference**
(95% of the theoretical maximum 3.0) — **168σ**. Absolute: **F_GHZ = 8.293 beats even *perfect*
separable probes** (the 9V₃² > 3 gate) at **239.5σ**, with V₃ = 0.9599 sitting **299σ above the
1/√3 survival threshold**. And the law the ratio can't fake: a free-frequency scan peaks at **k = 3**
(amplitude ratio **122.9×**) — the GHZ fringe genuinely oscillates at *triple* the drive.

## The grade

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| W1 (Heisenberg) | R = 9V₃²/3V₁² > 1 + 5·SE, vs the *measured* separable Fisher info | 2.848 (168σ) | **WIN** |
| W2 (SQL absolute) | GHZ beats *perfect* separable probes: 9V₃² > 3 + 5·SE (⇔ V₃ > 1/√3) | F_GHZ 8.293, V₃ 0.9599 (239.5σ / 299σ) | **WIN** |
| G_FREQ (super-resolution law) | free-frequency DFT peaks at k=3, amp > 2× any other | peak k=3, 122.9× | **PASS** |
| G_sent | sentinels ≥ 0.95 | 0.988 / 0.978 | **PASS** |

Predictions 0.93 / 0.90 both **HIT** (V₃ band [0.92, 0.96] → 0.9599 top edge; R band [2.5, 2.9] →
2.848).

## Method subclaims (both reported)

- **Executed reference at its own ideal (CONFIRMED).** The separable arm ran at **F_sep = 2.912 of
  3.0, V₁ = 0.9853** — essentially perfect classical performance. The advantage is measured against
  a classical player having its *best* day, not against a strawman (the F107 executed-classical-arm
  discipline, now standard).
- **The k=3 super-resolution law (CONFIRMED).** The GHZ fringe oscillates at exactly 3× the drive —
  gated by a free-frequency scan (peak k=3, 122.9× over any other frequency), so the advantage is
  *visible structure*, not just a bigger number. A law the Fisher-information ratio cannot fake.

## Atlas datapoint (cross-arc)

The FakeMarrakesh optimism crossover now has a **third depth point**: −0.4pp at 0 CZ (F107),
+0.9pp at 2–10 CZ (F106), **+1.9pp at the 4-CX GHZ depth here** — the noise-model optimism grows
with depth in a now-three-point curve at the shallow end.

## What this does and does not show (scope)

A **metrology / phase-sensing** quantum advantage at **N=3** — not a computational-speedup claim,
and not (yet) a scaling claim. GHZ phase super-resolution is **textbook** (Bollinger et al. 1996;
demonstrated on many platforms); the contribution is the **frozen-court, executed-SQL-reference,
super-resolution-gated gate-model certification**. **The honest caveat on scaling** (registered
follow-up = the N-ladder): the Heisenberg *advantage* at N=3 costs only 4 CX, but pushing N higher
means deeper GHZ preparation, and **F85's NISQ scaling inversion** (ideal capacity grows with N
while measured falls under depth cost) is exactly the wall a GHZ-metrology N-ladder will hit — the
N=3 win is clean; whether the advantage *scales* on this hardware generation is the open question,
and F85 says to expect practice to diverge from theory.

## Lineage and reuse — the genre triptych

- **Arc**: quantum-advantage genres — with F108 the campaign has certified **three distinct genres
  of quantum advantage in three cycles**: **F106** nonlocal games / contextuality (196σ), **F107**
  random-access storage / QRAC (110σ), **F108** metrology / GHZ sensing (168σ) — *games → storage →
  metrology*, spanning the foundational, the informational, and **the advantage the sensing industry
  actually buys**.
- **Method reuse**: execute-the-reference-at-its-own-ideal (the classical arm run, not cited — F107
  standard); the-law-the-ratio-cannot-fake as a super-resolution gate (a byproduct observable that a
  trivial mechanism can't reproduce — the F98/F101 discriminator lineage); enumerate/execute the
  bound in the artifact.
- **Status-ledger claim type**: **existence** (GHZ Heisenberg-limit metrology advantage at N=3).
  Figures of merit: **R = 2.848 / 168σ** over the executed SQL reference and **V₃ 299σ over the
  1/√3 threshold** (plus F_GHZ 239.5σ over perfect separable probes). Method subclaims: the
  **executed-reference-at-its-own-ideal** and the **k=3 super-resolution law**. HW tier; N=3 single
  run; N-ladder scaling registered as the follow-up (with the F85 caveat).
