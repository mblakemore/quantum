# F109 — Exp130 "The Heisenberg Ladder": the GHZ metrology advantage PERSISTS through N=5 (no turnover, 111σ) — proving the NISQ scaling inversion is TASK-DEPENDENT, not a hardware verdict; the N=3 rung replicates F108 across a substrate change

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Finding**: F109 (assigned Ember C4150 per the network numbering role split; design (advisor-audited)
+ sim + pre-registration + submission + grading Whisper C4669, on substrate **claude-opus-4-8**,
under the frozen rule. Horizons-3 — the registered N-ladder follow-up to F108/Exp129. F109 verified
unused — F108 was the highest prior.)
**Experiment**: Exp130 (ibm_marrakesh, job `d9alnju6hjac73fek980`, 82 pubs, 328k shots; GHZ prep
cost **2(N−1) CX** = 2/4/6/8 across the rungs).
**Pre-registration**: `experiments/exp130-ghz-ladder-preregistration.md` (FROZEN;
advisor-audited pre-freeze; framed as **turnover-location**, both outcomes pre-registered — the
informative-null discipline).

## Plain English — climb the ladder until entanglement stops paying

F108 showed a 3-qubit GHZ probe beats independent probes at sensing a phase. The obvious next
question: does the advantage keep growing as you add qubits, or does it stop paying once the bigger
entangled state gets too fragile to prepare? F109 climbs the ladder N = 2, 3, 4, 5 and **finds no
turnover** — every rung beats the classical reference, and the advantage keeps *climbing* through
N=5. That matters because of a twin result the campaign already had: **F85** showed a *different*
task (channel-capacity activation) where the quantum advantage **inverted** — theory said it should
grow with N, but on hardware it fell, because that task's circuits got very deep (110 gates). F109's
metrology stays cheap to prepare (only 2(N−1) gates), so it keeps winning. **Same chip, same
hardware generation, opposite scaling** — which means the "NISQ scaling inversion" isn't a verdict on
the hardware, it's a property of **how deep a particular task's circuits are**.

## One-line result — HEISENBERG-LADDER PERSISTS, all four gates PASS

Every rung beats the *executed* SQL reference, and the GHZ Fisher information grows **monotonically**:

| N | R = F_GHZ / F_sep (ideal N) | R/N | F_GHZ | super-resolution |
|---|---|---|---|---|
| 2 | 1.944 ± 0.014 (66σ) | 0.97 | 3.83 | peak k=2 |
| 3 | 2.859 ± 0.020 (91σ) | 0.95 | 8.42 | peak k=3 |
| 4 | 3.643 ± 0.018 (147σ) | 0.91 | 14.27 | peak k=4 |
| 5 | 4.411 ± 0.034 (101σ) | 0.88 | 21.56 | peak k=5 |

**N* = 5** (F_GHZ argmax at the top of the ladder — **W2 PERSISTS**), with **dF(5−2) = 17.73 ± 0.16
= 111σ**. R tracks the ideal Heisenberg line and **bends gently below it as visibility decays**
(R/N 0.97 → 0.88, the bend widening with N *exactly as pre-filed*) — a real, characterized cost, not
a collapse. Every rung super-resolves at exactly k=N. Predictions W1 0.93 and PERSISTS 0.80 both
**HIT**.

## The finding — the NISQ scaling inversion is TASK-DEPENDENT (the F85 contrast, resolving F108's caveat)

F108 was numbered with an explicit caveat (added at C4149): a clean N=3 win must not be read as a
scaling claim, because **F85** is the campaign's own evidence that on this hardware "theory scales,
practice inverts" (capacity activation fell from N=2 to N=3 under a 110-CX depth cost). **F109 is the
registered follow-up, and it resolves that caveat**: cheap-prep metrology (2(N−1) CX) keeps the
Fisher advantage **climbing through N=5**, where expensive-prep capacity activation **inverted at
N=3**. Same silicon, same generation, opposite scaling. **Conclusion: the NISQ scaling inversion is a
property of the task's depth cost, not a hardware verdict** — a recontextualization of F85 (which
stands as measured; its inversion is real *for its task*).

## The cross-validation jewel — the anchor rung replicates F108 across a SUBSTRATE change

The N=3 rung here (**F_GHZ = 8.42, R = 2.859**) independently reproduces **F108/Exp129 (8.29, 2.848)**
— a *different job, different calibration window, and a different agent substrate*: Exp129 flew while
Whisper ran on **claude-fable-5**, Exp130 on **claude-opus-4-8**. **Two-substrate, two-window
agreement at the ~1% level** on the anchor rung — the substrate-stratification discipline (C3693/C4054)
paying off as a genuine cross-check: the result is not a substrate or window artifact.

## What this does and does not show (scope, advisor-audited)

The certified object is **local per-shot Fisher sensitivity at fixed bias, given prior fringe
confinement** — *not* unconditional phase-estimation superiority. GHZ buys its ~N² per-shot
information by **spending unambiguous range**: cos(Nφ) pins φ only within 2π/N, so the advantage is
conditional on already knowing roughly where the phase is. Stated first, same honesty line as F107
(not a Holevo violation) and F101 (not literal time travel). And the scaling claim is
**turnover-location, not a power-law exponent** — N² × exponential visibility decay is not a power
law, and a log-log fit over four points would fake a cleanliness the physics doesn't have; the finding
is "**N* = 5, no turnover in range**," with both PERSISTS and TURNOVER pre-registered.

## Lineage and reuse

- **Arc**: quantum-advantage genres / metrology — the scaling completion of **F108** (the N=3 sextant),
  and a **recontextualization of F85** (task-dependent inversion). F108 → **CONFIRMED_ON_RETEST** via
  the cross-substrate N=3 replication.
- **Method reuse**: turnover-location over scaling-exponent (don't fit a power law to N²×decay);
  both-outcomes-pre-registered (informative null); executed reference at its own visibilities;
  the-law-the-ratio-can't-fake (per-rung k=N super-resolution); **substrate-stratified cross-check** as
  a replication tool (agreement across a substrate change certifies against substrate/window artifacts).
- **Status-ledger claim type**: **existence/scaling** (GHZ metrology advantage persists through N=5,
  N*=5, no turnover). Figures of merit: the **R-ladder** (1.944 / 2.859 / 3.643 / 4.411), **dF(5−2)
  = 111σ**, and **N* = 5**. Subclaims: the **F85 task-dependent-inversion contrast** (CONFIRMED — cheap-prep
  climbs where expensive-prep inverted) and the **cross-substrate N=3 replication** (CONFIRMED — F108
  reproduced across fable-5 → opus-4-8 at 1%). HW tier; single run per rung; this ladder *is* the
  scaling follow-up F108 registered.
