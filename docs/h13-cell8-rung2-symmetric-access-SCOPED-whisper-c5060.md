# H13 Cell 8 Rung 2 — the symmetric-access question: **narrowed, not answered**, and scoped

**Author**: Whisper (DC15W), C5060 · **Board**: #72 · **Creator**: "run next priority", general#10590
**Predecessor**: `docs/h13-cell8-rung2-billing-currency-declaration-whisper-c5060.md`, where I
recorded the rejected convention's number as **unknown** and named this as the rung's sharpest open
question. This document is the attempt. **QPU spent: none.**

## The question

The billing-currency class forced a declared unit (*one use of each unitary, at the
process-abstraction level*) and forced me to record what the **rejected** convention would give.
The rejected convention is billing in **hardware controlled-calls**, and its honest form is:

> Re-derive the causally-separable ceiling with **controlled access granted to the definite-order
> side too**. If a separable strategy given `c-U` reaches 0.9769, the F82 result is a statement about
> **controllability**, not about **order**.

## ✅ What this run established — a real structural narrowing

**Controlled access cannot manufacture order indefiniteness.**

A definite-order strategy computes `U_B U_A` in **every branch where both parties fire**. The
commutator sign — the only thing that distinguishes the commuting from the anticommuting promise —
lives in the difference between `U_B U_A` and `U_A U_B`. **Controlled access lets a party superpose
*apply* against *do-not-apply*; it never produces the opposite ordering.** So `c-U` does not buy the
one resource the task actually turns on.

Checked directly rather than argued: over the promise-satisfying ordered pairs of the game's
generator set, the commuting pairs are exactly those where the two orderings coincide as operators
and the anticommuting ones are exactly those where they differ. There is no third case for a
controlled branch to exploit.

## 🔴 What it does **not** establish, stated plainly

**This is a constraint on ACCESS, not a CEILING.** It shows `c-U` cannot reach the commutator by the
route the switch uses. It does **not** bound the extra information that the superposed
apply/not-apply branches might leak by some other route — and the existing ceiling of 0.869028 is
already well above the 0.6165 prior, which proves separable strategies *do* extract real information
without touching the commutator. Whether controlled access widens that extraction is exactly what an
SDP would answer and this argument does not.

**I am not going to let a structural argument stand in for the number I recorded as unknown.**

## Scoping: why the SDP is a project rather than a task

| Scenario | Systems | Total dim | PSD variable |
|---|---|---|---|
| Current (this rung's ceiling) | [A_I, A_O, B_I, B_O, C_I], all dim 2 | **32** | 32×32 |
| Symmetric access (each party +1 control ancilla) | A/B in and out at dim 4, C_I dim 2 | **512** | 512×512, 262,144 complex entries |

A **16× dimension** increase. The comb constraints (trace-and-replace hierarchy over five
subsystems) must be rebuilt at every one of those subsystems, giving roughly **256×** the PSD cone
and on the order of **4096×** the solve cost — against a current solve that already returns
`optimal_inaccurate` at dim 32. **That is a reformulation, not a re-run.**

## ✅ The pair-count discrepancy — RECONCILED (was flagged unresolved in this document's first draft)

My first draft flagged that I counted **42** promise-satisfying ordered pairs where F82 records
**51**, and said I had not reconciled them. **Now reconciled, and there is no error anywhere — the
three numbers count three different things:**

| Count | What it is | Composition |
|---|---|---|
| **52** | promise-satisfying ordered pairs, **self-pairs included** | 28 commuting + 24 anticommuting |
| **51** | **q\*'s support** — the pairs with nonzero optimal weight | 27 + 24 |
| **51** | pairs **flown** by F82 | matches q\*'s support exactly |
| **42** | my enumeration — I filtered `i != j`, dropping all **10** self-pairs | 18 + 24 |

`28 − 18 = 10`, exactly the generator-set size: self-pairs commute trivially and the SDP is right to
include them; my filter dropped them and that was my discrepancy, not an error in the record.

**The one pair in the promise class with ZERO optimal weight is `(1, 1)`** — identity against
identity. It is trivially commuting and carries no discriminating information at all, so the
optimizer assigns it nothing and flying it would spend shots on a pair that cannot contribute.
**q\* support = 51 = pairs flown**, which is the consistency that matters and it holds exactly.

*Recorded because the first draft published an unreconciled discrepancy, and an unreconciled number
left in a document is the "pending" pattern that cost this seat twice tonight.*

## Disposition

**Filed, not abandoned.** The rung's billing-currency declaration already records this convention's
number as *unknown*, and that record is now stronger: it carries a structural reason to expect the
answer is "no", and an explicit statement that the reason is not a proof. If Rung 2 is ever
challenged on currency, this is the document that shows the question was asked, narrowed, and left
open deliberately rather than quietly.

---

## AMENDMENT (C5069, H14 cell B1) — the symmetry door is OPEN: GO

The H14 charter's B1 cell attacked this document's wall through group-invariant reduction. Study artifact: `results/h14_b1_symmetry_study.json` (tools inline in the H14 record); every convention pinned numerically before use.

**The group**: the 10-generator set is the identity plus nine Bloch reflection axes (3 coordinate + 6 bisectors) — invariant under the octahedral single-qubit Clifford group C1 (order 24, generated and verified by projective closure), acting diagonally on both parties, times party exchange: **48 elements**. Verified against the frozen artifacts: all 24 Cliffords permute the generator set with promise classes preserved; **q\* is exactly orbit-invariant (deviation 0.00e+00) and exactly exchange-symmetric** — the optimum already has the symmetry, as convexity promised. The 32-dim representation (bar-placement pinned by commutation check: err 1.9e-15 across the group) commutes with G(q\*); exchange commutes at 2.7e-16.

**The collapse**:
| | full Hermitian params | commutant (free params) | reduction | irrep dims present |
|---|---|---|---|---|
| dim 32 (current problem) | 1,024 | **44** | 23× | ≤ 3 (blocks: 8×3, 2×2, 4×1) |
| dim 512 (symmetric access) | 262,144 | **7,904** | 33× | ≤ 3 (224 eigen-clusters) |

PSD blocks in the symmetry-adapted basis are multiplicity-sized: bounded by √7904 ≈ 89 at dim 512 (exact multiplicities land with the reduction implementation), versus the scoped monolithic 512×512 cone. Per-iteration cost collapses by ~10³ against the scoped estimate.

**Verdict: GO.** The scoped "~4096× the dim-32 cost — a reformulation, not a re-run" priced the UNREDUCED problem; the game's symmetry group is rich enough that the reduced symmetric-access solve sits in approximately the cost class of the CURRENT dim-32 solve. And the validation path is built in: the same reduction applied at dim 32 (44 parameters) must reproduce **0.8690277** before the 512 solve is trusted — a known-answer gate at every step, which also directly addresses this document's numerical-hygiene worry (`optimal_inaccurate` at 1,024 params should become clean at 44).

**What this does NOT do**: no number exists yet. The reduced-basis SDP implementation is the now-unlocked project; the fence stands exactly as this document left it until that solve lands, with both outcome readings still pre-committed in the H14 charter.

### CORRECTION to the C5069 amendment, same day — the 512 collapse is RETRACTED; the wall has a measured mechanism

The GO amendment above verified the octahedral symmetry against G(q\*) **at dim 32 only** and extrapolated the representation to 512. The stage-512 machinery's own invariance assertion refused it (`results/h14_b1_sign_obstruction.json`): octahedral conjugation maps generators to **±**U_π, and while a sign cancels in a plain CJ projector (dim 32: 24/24 elements commute — the study's finding stands there), **it does not cancel in controlled-U**: c(−U) = (Z_ctl)·c(U), a physically different instrument. Measured at 512: **1 of 24 elements survives (the identity)**; only party exchange remains (invariance 6.8e-16; true commutant 131,584 = a 2× fold, not 33×). Even the C3 about (1,1,1) dies — it maps (x−z)/√2 to −(x−y)/√2, hand-verified after the machine said so.

**What stands**: stage V's validation gate (the dim-32 restriction reproduces 0.8690277 cleanly — the machinery is sound where the symmetry exists); the exchange fold; and a sharper characterization of this document's wall: it is **structural, not merely computational** — the generator set's sign conventions, gauge at the process level, become physical under controlled access. **What is retracted**: the "reduced solve sits in the dim-32 cost class" claim. An exchange-only solve attempt is running as an empirical wall measurement; its outcome (number or measured infeasibility) will be appended here either way.
