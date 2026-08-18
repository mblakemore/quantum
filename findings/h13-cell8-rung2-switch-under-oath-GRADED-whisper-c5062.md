# H13 Cell 8 Rung 2 — The Switch Under Oath: the causal game, sealed and blind — PASSED, 74.0σ

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Author/booking**: Whisper (DC15W), C5062 — closing board #131 (the grade existed only in
`results/h13_cell8_rung2_GRADE_elder.json` + the commit trail; this card books it).
**Seats**: Whisper (design/flight) · **Elder (grading seat, C6608 — the verdict is his)** ·
Ember (sealer, instance sequence) · Creator GO general#10566.
**Prereg**: [`docs/h13-cell8-rung2-prereg-FROZEN-whisper-c5060.md`](../docs/h13-cell8-rung2-prereg-FROZEN-whisper-c5060.md)
(frozen `0c82cda`, amendments A1–A9) · claim card
[`experiments/h13_cell8_rung2_claim_card_c5060.json`](../experiments/h13_cell8_rung2_claim_card_c5060.json)
· grade record [`results/h13_cell8_rung2_GRADE_elder.json`](../results/h13_cell8_rung2_GRADE_elder.json).
**Job**: `d9uj7vs98n5s7392uan0`, ibm_marrakesh, **16 QPU-s**. Board #72 closed on this flight.

## 0. Genre, stated before anything else (verbatim from the frozen prereg)

The discrimination-game win is **F82's**. Rung 2 adds two things and nothing else: a **blind
sealed court**, and an **explicit computational-task framing**. Per the arc spec §3: *"Not a
new column."* Any reader taking this card as a fresh physics result has been misled by it,
and that would be a defect in this card.

## 1. The claim

COMMUTE(A,B) vs ANTICOMMUTE(A,B) decided in **one use of each unitary per shot** by an
indefinite-order process (the quantum switch as controlled routing), blind against a sealed
instance sequence, at a q\*-weighted per-round success probability of **0.988383** against
the causally-separable ceiling **0.869028** — **74.0σ (conservative)**, registered bar ≥5σ,
**PASSED**.

## 2. The apparatus of the claim (all frozen before flight)

- **Game**: 10-unitary generator set `1, X, Y, Z, (X±Y)/√2, (X±Z)/√2, (Y±Z)/√2`; promise
  commute-or-anticommute; input distribution q\* (SDP-optimal, recovered in-house — the
  source paper omits it), support = **51 ordered pairs** (27 commuting + 24 anticommuting);
  the (1,1) identity pair carries zero optimal weight and was not flown. Gate G0b:
  support(q\*) == flown manifest, refuse on mismatch.
- **Ceiling**: **0.869028, re-derived in-code at freeze** (`scripts/causal_game_sdp.py`,
  primal–dual gap 2.12e-08; solver flag `optimal_inaccurate` on the record — the
  primal–dual bracket certifies the value independently of it), never cited from F82.
  Quoted at six figures per the precision-fork rule. Both source-paper gates pass
  (Haar 0.928813; finite 0.869028). The SDP cone covers fixed order, classical mixtures
  of orders, AND dynamical (outcome-dependent) order.
- **Floor**: 0.6165 (the commuting-class weight of q\*) — verified on-chip, not assumed
  (F82's null arms measured 0.6146/0.6153, within 0.2pp on both devices).
- **Billing currency, declared before any ratio**: one use of each unitary per shot at the
  process-abstraction level — **forced by the scenario** (both arms are process matrices
  over [A_I, A_O, B_I, B_O, C_I]; the control lives in C_I as part of the process).
  Stopping rule: fixed 1,000 shots per ordered pair, 51 pairs, no sequential test, no
  early stop. **Rejected convention recorded with a stated NOT COMPUTED**: billing in
  hardware controlled-calls would require re-deriving the separable ceiling with
  controlled access granted to the definite-order side (dim 512 vs dim 32, ~4096× solve
  cost) — recorded as UNKNOWN rather than as absent
  ([declaration](../docs/h13-cell8-rung2-billing-currency-declaration-whisper-c5060.md),
  [scope](../docs/h13-cell8-rung2-symmetric-access-SCOPED-whisper-c5060.md)).
- **Attack preflight**: all classes fired, CLEAR — including the billing-currency class
  (fired and answered, unit forced by construction) and the 6th class
  [index-space-underdetermined], **found with this rung as the only live instance
  campaign-wide** (a hash binds the bytes, not the parse: two legal parses of the sealed
  artifact gave canonical orders differing in 51/51 positions with every hash green —
  fixed by A4's lexicographic rule + index-table digest `8371d260`, asserted by both
  flier and decoder). A deliberately all-yes positive-control claim was fired at the
  same gate and **blocked** (exit 1), so the CLEAR is a decision, not a gate that
  cannot fire.
- **The blind protocol (the ORDER is the protocol)**: Ember draws and seals the instance
  sequence → commitment digest published to the bus before flight → flight → blind decode
  against the frozen public grader → **decisions hash published before unseal**
  (`a0984134f583ec633309d82999309aae2dbc7a6f5763d6bbc5e94341f04866c9`) → unseal and
  reveal against the commitment. A step performed out of order voids the seal.

## 3. The amendment stack (A1–A9 — each a defect the freeze process caught in itself)

| # | What it fixed |
|---|---|
| A1 | G0b names BOTH artifacts by path and hash (the manifest side had the same defect) |
| A2 | §4 gains a CUSTODY column; reading (B) binds — **the flight never receives the sequence** |
| A3 | Elder's seal-stands ruling + the custody/hash scope limit; corrects the author's too-strong post-draw rule |
| A4 | Canonical order pinned (lexicographic over the merged q\* key sets, parser-invariant); index-table digest `8371d260`; unshoppability argument (raised by Elder, general#10755) |
| A5 | G0e: entanglement survives transpilation — arm-aware, opt≤1, **per-pair**, manifest-recorded |
| A6 | §7 zero-query qualifier per court ruling general#10796 (an adversary holding the gate descriptions needs ZERO queries — demonstrated twice unrecognised) |
| A7 | Gates report **PASS/FAIL/N-A — a vacuous pass never counts**; every gate carries a positive control; G0b non-emptiness precondition |
| A8 | §6 gains an **UPPER falsifier** (a rate above the haircut envelope is NO-TEST — the collapse invisible to every noiseless check shows only as TOO GOOD) + `record_as_submitted()` on the exact PUB objects, `--submit` blocked without it (a build-time assertion cannot prove what the DEVICE received) |
| A9 | G1 restated as a CONDITION discharged by a **fault-injected runtime guard** — supersedes A7 rule 3, which mandated re-running a checker that passes an empty file |

Also on the flight path: the **routed-intent separation gate** (simulate the TRANSPILED
circuit as-is, MPS, no re-transpile — G0e proves the gates survive; this proves the
*separation* does; ideal separation 2.0000), and the artifact-vs-spec provenance split
(sealed sha256 vs prereg head at build, both asserted). Four defects were caught before
flight by these gates; four in-cycle retractions across three seats are in the commit
record, none caught by their own author — the court caught them.

## 4. The flight and the grade

**Flight** (`38af7eb`): 51 pairs × 1,000 shots, ibm_marrakesh, 16 QPU-s.
**Blind decode: 51/51 pair decisions correct, 0 mismatches; separation +1.9080
(ideal 2.0000); mean |Z| = 0.9756.** Seal intact through the full protocol order.

**Grade** (Elder, C6608, `16bc173` — quoted from the grade JSON):

- **Ruling**: the §6 denominator is the **q\*-weighted per-round success probability**
  ("the ceiling and the measurement must be the same kind of quantity:
  p_sep_finite_optimal is a per-ROUND success probability optimised under q\*").
- **Accepted**: p̂ = **0.988383** vs ceiling **0.869028**; se under null 0.001614 →
  **74.0σ conservative (null-variance)**; se propagated 0.000503 → **237.2σ** — the
  smaller number is the headline, "chosen because the grading seat holds the pen."
- **Rejected denominators, on the record**: 51 majority-decisions (3.16σ — rejected as a
  category error, a statistic about shot budget, *not* on its σ); unweighted 51,000 shots
  (p̂ 0.987784, 79.5σ — shots ARE rounds, but the ceiling is q\*-weighted and q\* spans
  0.01304–0.03912, 3×).
- **Registered bar**: ≥5σ. **Result: PASSED.**

## 5. Scope fences (carried in the same breath as the number)

The chip is a **fixed-causal-order processor**; the switch is realized by **controlled
routing**; the query currency is **controlled-calls at the process-abstraction level,
device-characterized**. Enforced single-firing is unavailable in the gate model (C4999
scout: controlled-U compiles two applications; gate-teleportation escape fails for blind
decoding). Device-independence is **provably impossible** for this scenario class
(Bavaresco 2019); SDI is photonic-only to date. The **symmetric-access ceiling**
(separable arm granted controlled access) is the rung's sharpest open question: **that
number does not exist and this card does not imply it is small** — only the narrowing is
banked (controlled access cannot manufacture the opposite ordering; a constraint on
access, not a ceiling). The scoreboard framing drafted at freeze remains NOT POSTABLE
until that gate is resolved (`docs/h13-cell8-rung2-scoreboard-framing-whisper-c5060.md`).

## 6. What this rung bought the campaign (beyond the number)

The **template for sealed courts on banked results**: re-derive the ceiling in-code at
freeze; declare the currency before any ratio, with the rejected convention priced or
marked NOT COMPUTED; custody such that the flight never receives the secret; positive
controls on every gate including the attack-preflight itself; an upper falsifier for
too-good collapses; provenance asserted at build AND fly; and a grading seat that rules
on the denominator *before* choosing between two correct rulers, then takes the smaller
number. The 6th attack class (index-space underdetermination) was discovered here and
swept across 337 files campaign-wide — this rung was its only live instance.

**Status: PASSED and closed (board #72). Rung 1 (the mixture arm on silicon, closes F75
caveat 3) is flight-ready and Elder-owned (board #63). Rung 3 (constants-or-weather) is
optional and unflown.**
