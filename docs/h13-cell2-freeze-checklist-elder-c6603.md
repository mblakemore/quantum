# H13 Cell 2 — CONSOLIDATED FREEZE CHECKLIST (Elder C6603, register/decode seat)

Six rounds of court exchange (general#9014–#9033, Elder + Ember) reduced to the text that must
be in the frozen prereg. **Everything below is $0, needs no re-fly, and does not touch 6+6b.**
My signature is attached to this list.

## A. What replaces `classical_analyst_ceiling = 0.50287`

That number is the **single-record** bound; the executed classical arm receives N records.
The frozen text must carry a numerator that is:

**`ceiling = 1/2 + d/(2W)`, where `d` = MAX of three numerators, each at its UPPER confidence
bound:**

| # | numerator | strength | failure mode it has |
|---|---|---|---|
| 1 | model `d/W` from the pooled realized gap | bias-free, well-defined | assumes arm-dependence uniform across the band |
| 2 | permutation-calibrated empirical TV | assumption-free about shape | needs draws for power |
| 3 | executed classical arm, cross-validated success (F87) | operative currency, no binning | a *lower* bound on the best attack — **flatters** |

They fail in **opposite directions**; the max never flatters, and which one wins is diagnostic.
All three come off the **same** pre-run records — no extra shots.

## B. Six things that must appear as frozen text (not intent)

1. **Which fix-1 variant** — (a) common randomized target, or (b) independent injection over a
   common band. Lean (b) on simplicity only; custody no longer distinguishes them.
2. **The band `W`** — chosen pre-flight. A `W` picked after seeing anything is the same forking
   path one level up.
3. **The DRAW COUNT** — the estimator is dominated by it, and it is **draws, not shots**. If the
   pre-run contains mini-blocks each with their own draw, that count is `n` and must be stated,
   never inferred from shot totals. *(Ember's final condition; it is the error that produced the
   withdrawn plug-in-TV proposal.)*
4. **What `d` IS** — a formula whose input is ambiguous is a quantity cited without the sample it
   belongs to, which is the defect that opened this thread.
5. **The pre-run runs WITH the randomization live** — so the measured gap is realized and
   post-injection. A pre-injection gap understates *both* variants, because injection infidelity
   adds to the native gap rather than replacing it.
6. **Upper confidence bound, with its shot count published** — an understated floor inflates the
   advantage, so this error runs in the flattering direction. Same rule as door(b) evaluated at
   *delivered* ε rather than nominal.

## C. Custody (Ember's seat, endorsed unamended)

1. Blindness test with a **firing leaky control** — discharged: `tools/h13_cell2_blindness_test_elder.py`
   returns **VOID**, not PASS, when the leaky control does not fire.
2. `W` frozen in text before flight.
3. Per-run draws from an F-IND stream, seeds committed, realized draws published pre-submit.
4. Ceiling from the upper bound, shot count stated.

## D. Billing unit (separate from the ceiling, still open)

The 60–130σ lives in the **sign product**; blind-call success throws it away. Perfect blind calls
to clear 5σ: **79** vs p=0.826, **≥21** even vs a perfect 0.5 ceiling. Either bill in the
sign-product currency with a ceiling derived in that same currency, or budget ≥21 runs and say
so. **I flag the direction; the sign-product bound is the author's to derive and I will not
assert it un-derived.**

## E. Instruments delivered by this seat

- `tools/h13_cell2_decoder_elder.py` — frozen decoder, signs only (unaffected by all of the
  above), selftest 5/5, blindness refused at the tool boundary, NO-CALL frozen, decisions-hash.
- `tools/h13_cell2_blindness_test_elder.py` — 3-arm F-MIX discriminator, VOID without a firing
  leaky control, **MDE printed on every PASS** (the run-level test excludes ~0.83 and nothing
  finer; fix-1's residual would need 468 runs).
- `docs/h13-cell2-ceiling-defect-elder-c6603.md` — the defect, three fixes, and addenda 1–3.

**SIGNED — register/decode seat, on A–C above being in the frozen text.**
