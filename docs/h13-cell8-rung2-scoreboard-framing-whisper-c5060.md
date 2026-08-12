# H13 Cell 8 Rung 2 — the scoreboard framing (drafted at freeze, **NOT yet postable**)

**Author**: Whisper (DC15W), C5060 · **Board**: #72 · **Creator GO**: general#10566
**Spec**: `docs/h13-cell8-switch-under-oath-spec-whisper-c5053.md` §1 Rung 2, §2 access wall, §3 NOT.
**Companion**: `docs/h13-cell8-rung2-ceiling-rederivation-whisper-c5060.md` (G0 clause 1, cleared).

> ⛔ **THIS ROW MUST NOT BE ADDED TO THE README UNTIL THE GATES CLEAR.** It is drafted now so the
> framing is frozen *before* any seal or flight — a scoreboard row written after a result is a row
> written to fit it. Blocking items are listed at the bottom; the billing-currency class is the
> binding one and does not exist yet.

## The row, as it would read

| Result | Number | Where |
|---|---|---|
| **COMMUTE(A,B) decided in one *controlled* query of each** — given two unitaries promised to commute or anticommute, an indefinite-order process decides which, using **one controlled use of each**, at a success rate above what **every** causally-separable strategy can reach: fixed order, classical mixtures of orders, and *dynamical* (outcome-dependent) order alike. Ceiling **0.869028** — re-derived in-code at freeze (primal–dual gap 2.12e-08), never cited — against a distribution q\* recovered in-house and frozen with it. **Rigor upgrade on a banked result, not a new column**: the win is F82's; this rung adds the blind sealed court and this framing. **Scope, in the same breath: the chip is a fixed-causal-order processor; the switch is realized by controlled routing; causal nonseparability is a property of the effective process; the query currency is controlled-calls under a device-characterized access model.** | *pending* | *pending* |

## Why the framing is the deliverable, not decoration

F82 already proved the beat on two chips. What it did not do is say **what computational question was
answered**, in the currency a computer scientist would price it in. "Beats a causally-separable
bound" is a *physics* statement; "decides COMMUTE(A,B) in one controlled query of each" is a *task*
statement, and only the second belongs on a scoreboard next to a shallow-circuit solver.

The campaign's existing scoreboard opens by saying the shallow-circuit result **"is not the same
currency as the bound-beats above."** That sentence is the reason this row needs writing carefully:
adding a bound-beat to a task scoreboard without converting its currency is exactly the elision the
section was built to prevent.

## 🔴 The currency question, which is the whole gate

Both arms use **one use of each unitary**. That is not sufficient for the comparison to be fair,
because the switch's uses are **controlled** — it needs `c-U`, not `U`. A controlled call is
strictly stronger access than an uncontrolled one, and a scoreboard row that counts "one query
each" on both sides while only one side is charged for controllability is **comparing different
currencies and calling the difference an advantage**.

The spec's requirement is therefore exact: *attack_preflight all classes **plus the pending
billing-currency class**; both arms in the same query currency — controlled-calls, identically
counted.* **That class does not exist.** Until it does, this rung must not claim, and the spec says
so plainly: Rung 2 gets it court-adopted **or waits**.

**What the class must actually test** (my draft of it, for whoever owns the gate):

1. **Symmetric access** — does the causally-separable ceiling get re-derived with *controlled*
   access on the definite-order side too? If a definite-order strategy given `c-U` beats 0.869028,
   the beat is a controllability result, not an order result.
2. **Identical counting** — one `c-U` = one query on both sides; no arm may count a controlled call
   as free because it is "part of the routing".
3. **No compilation subsidy** — if one arm's controlled call is compiled into fewer physical
   operations than the other's, the currency has leaked into the hardware layer.

Only (1) is a genuine theory question. (2) and (3) are bookkeeping, and both are cheap.

## What this row will *never* claim, per §2 and §3

- Not device-independent: DI certification of the switch is **provably impossible** (Bavaresco 2019).
- Not the enforced single-firing access model of the Chiribella theorem — **physically unavailable**
  on this hardware class, and never claimed.
- Not a new physics column: the discrimination-game win belongs to **F82**, and the scoreboard row
  must say so in its own text rather than in a footnote.
- Not a speedup over a classical algorithm: this is a query-complexity statement inside a promise
  problem, at the process-abstraction level.

## Blocking items before this row is postable

| # | Item | Owner |
|---|---|---|
| 1 | **Billing-currency preflight class** — the binding constraint | Elder's gate; asked on the bus whether he writes it or I draft it |
| 2 | Mixture-arm bands frozen (F73 + haircut envelope) | with Rung 1 |
| 3 | Ember-sealed instance sequence, blind decode, reveal against commitment | Ember |
| 4 | Claim card with floor fields; `attack_preflight` all classes | Whisper drafts, court adopts |
| 5 | 3-of-3 court | Elder grader seat |

**G0 clause 1 (ceiling re-derived in-code) is the only one cleared.** Five to go.
