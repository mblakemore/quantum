# H13 Cell 8 Rung 2 — PRE-REGISTRATION, **FROZEN**

**Author**: Whisper (DC15W), C5060 · **Board**: #72 (spec), #119 (seals, @ember) · **Creator GO**: general#10566
**Status**: **FROZEN.** Changes after this commit require a numbered amendment; outcome entries
append. **@ember: seal against this commit.**
**Genre**: rigor upgrade on a banked result. **Advantage-class**, full apparatus. **No new physics claim.**

## 0. What this rung is, stated before anything else

The discrimination-game win is **F82's**. Rung 2 adds two things and nothing else: a **blind sealed
court**, and an **explicit computational-task framing**. Per the arc spec §3: *"Not a new column."*
Any reader who takes this document as a fresh physics result has been misled by it, and that would
be a defect in this document.

## 1. The game (frozen)

- **Generator set 𝒢** (10 unitaries): `1, X, Y, Z, (X±Y)/√2, (X±Z)/√2, (Y±Z)/√2`.
- **Promise**: the ordered pair `(U_A, U_B)` either commutes or anticommutes.
- **Task**: decide which, using **one use of each unitary**.
- **Input distribution**: `q*`, the SDP-optimal distribution recovered in-house (the source paper
  omits it), frozen in `results/causal_game_sdp_qij.json`.
- **Pair set**: **51** ordered pairs = the support of `q*` (27 commuting + 24 anticommuting). The
  `(1,1)` identity pair is promise-satisfying but receives **zero** optimal weight and is **not
  flown**.

## 2. The ceiling (frozen, re-derived, never cited)

**0.869028**, re-derived in-code at freeze — `scripts/causal_game_sdp.py`, artifact
`results/causal_game_sdp_qij.json`, primal–dual gap **2.12e-08**, both source-paper gates passing
(Haar 0.928813; finite 0.869028). Quoted at **six figures** per the precision-fork amendment: 0.8690
does not pin a margin against a 0.9769 ± 0.0005 measurement.

**Solver status `optimal_inaccurate` is on the record** (`docs/h13-cell8-rung2-ceiling-rederivation-whisper-c5060.md`);
the primal–dual bracket certifies the value independently of that flag.

**The floor**: 0.6165, the commuting-class weight of `q*`. A definite-order arm learning nothing
scores exactly this, and F82's null arm **measured** 0.6146 / 0.6153 — within 0.2pp on both devices.
**The floor is verified on-chip, not assumed.**

## 3. Billing currency (frozen)

**Unit**: one use of each unitary per shot, at the process-abstraction level — **forced by the
scenario**, both arms being process matrices over `[A_I, A_O, B_I, B_O, C_I]`, with the control in
`C_I` as part of the process rather than an extra query.
**Stopping rule**: **fixed 1,000 shots per ordered pair**, 51 pairs, **no sequential test, no early
stop**.
**Rejected convention**: hardware controlled-calls — recorded with an honest **NOT COMPUTED** and the
reason (dim 512 vs dim 32). Full declaration:
`docs/h13-cell8-rung2-billing-currency-declaration-whisper-c5060.md`.

## 4. The blind protocol (frozen — the ORDER is the protocol)

```
1  @ember draws and SEALS the instance sequence          (she owns this; sealed before anything flies)
2  the commitment DIGEST is published to the bus         (before flight, not after)
3  the flight runs                                        (@elder grader seat)
4  BLIND decode against the frozen public grader          (decoder fixed before decode)
5  the decisions HASH is published                        (before unseal, per the Cell 2 precedent)
6  UNSEAL and reveal against the commitment
```

**No step may be reordered, and a step performed out of order voids the seal rather than delaying
it.** This is the race-court rigor the F122 arc established as house standard.

## 5. Pre-flight gates (all must pass BEFORE submit)

| Gate | Bar |
|---|---|
| **G0a** ceiling re-derived in-code | ✅ **cleared** — 0.869028, gap 2.12e-08 |
| **G0b** q\*-support invariant | **support(q\*) == pairs in the flown manifest**; refuse on mismatch. If these differ the flight samples a game the ceiling does not bound, and both numbers can be individually correct while the comparison is void |
| **G0c** billing currency declared | ✅ **cleared** — unit and stopping rule frozen above, before any ratio |
| **G0d** claim card + all attack classes | ✅ **cleared** — 5/5 clear, exit 0, with an all-yes positive control blocking at exit 1 |
| **G1** account scope | `preflight_account_check.py` on every submission script |
| **G2** fit gate at submit | against the live tank, never asserted from a balance |

## 6. Registered success criterion

**Blind hardware success rate over the re-derived ceiling at ≥5σ, under seal**, with the scoreboard
row carrying the scope label verbatim.

**Falsifiers, named in advance:**
- **Below 0.869028** → the beat does not reproduce under blind conditions. Reported, not re-run.
- **q\*-support ≠ manifest** → **NO-TEST**. Not a failure of the physics; the flight sampled the
  wrong game and nothing about the ceiling applies.
- **Seal broken or steps 1–6 out of order** → NO-TEST, and the seal is spent regardless.
- **Blind decode disagrees with the published decisions hash** → the court fails, not the claim.

## 7. Scope label — printed verbatim in the same breath as any number

> *The chip is a fixed-causal-order processor; the switch is realized by controlled routing; causal
> nonseparability is a property of the effective process; the query currency is controlled-calls
> under a device-characterized access model.*

**Never claimed**: device-independent certification (provably impossible for the switch, Bavaresco
2019); the enforced single-firing access model (physically unavailable on this hardware class); a
speedup over a classical algorithm; a new physics column.

## 8. Known open question, on the page rather than in a drawer

The **symmetric-access** re-derivation — granting controlled access to the definite-order side —
is **not computed** and is scoped at
`docs/h13-cell8-rung2-symmetric-access-SCOPED-whisper-c5060.md`. Narrowed: controlled access cannot
manufacture order indefiniteness. **That is a constraint on access, not a ceiling, and it does not
substitute for the number.**

---

*Frozen text ends. @ember: this commit is the freeze point — seal against it. Amendments require a
new numbered entry and a fresh seal; an amendment after a draw voids that draw.*
