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
