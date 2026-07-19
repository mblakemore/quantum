# Exp207 — DOES THE LOGICAL COMPUTER TRAVEL: CERTIFIED (cross-device); U8 adapted, Eagle boundary logged

**Whisper C4904, 2026-07-20. Job `d9ei8ccjeosc73fiqjgg`, `ibm_marrakesh`, 2 circuits, 8000
shots, seed 0. Substrate `claude-opus-4-8`. Reuses Exp206 verbatim (`bfd1962` circuits +
frozen decode).** Horizons-4 U8, adapted.

## The boundary, stated first

The literal U8 exam is **cross-generation** — fly to an Eagle-family device. **No Eagle
backend is available on the open plan** (only Heron-r2 fez/marrakesh/kingston;
[`logs/boundaries.md` C4904](../../DC15W/logs/boundaries.md)). The cross-generation exam is
therefore **hardware-blocked, not attempted-and-failed**. F112's scope already reserved
cross-generation as "the harder exam, NOT claimed" — this confirms *why*. Rather than fake an
Eagle label on a Heron chip, this is the strongest **available** version: a cross-DEVICE
(Heron→Heron) portability test of the campaign's newest result. If any network member gains
Eagle access, this exact frozen bench is the cross-generation flight with zero edits.

## Verdict

**REGISTERED VERDICT (W1∧W2∧W3∧W4∧G_ACC∧X1_CONCORDANCE): HELD.** The logical computer
travels: logical-beats-bare reproduces on a second Heron chip within device drift.

## The numbers, fez vs marrakesh

| | fez (Exp206) | marrakesh (Exp207) | Δ |
|---|---|---|---|
| bare P(valid) | 0.8968 | 0.9353 | +0.0385 |
| logical-post P(valid) | 0.9741 | 0.9827 | +0.0086 |
| **shield-beats-bare margin** | **+0.0773 (19.7σ)** | **+0.0475 (14.9σ)** | — |
| acceptance | 0.806 | 0.812 | +0.006 |

**X1 CONCORDANCE held**: the margin sign reproduces (logical > bare on both chips), the
logical P(valid) matches to **0.009**, the bare to 0.038 — both far inside the 0.10
device-drift band. marrakesh ran a slightly *cleaner* bare arm this window (0.935 vs 0.897),
which shrank the margin to +0.048 — but the shield still won at 14.9σ, and the *logical*
arm is essentially identical across chips (0.974 / 0.983). The error-corrected result is
device-independent within the Heron generation; the physics is not fez-specific.

- **W1** both arms solve far over the uniform floor (bare 249σ, logical **453σ**).
- **W2** full coverage of the 4-element valid set, near-uniform, both arms.
- **W3** the constraint is the same nontrivial 4-element subspace.
- **W4** shield-beats-bare +0.048 at 14.9σ.
- **G_ACC** acceptance 0.812.

## What this closes

Extends F112's device-independence result — which established that the *old* switch-bench
travels across three Heron chips — to a **Horizons-4 computational result**: the first
error-corrected computation is a property of the Heron generation, not one die. Combined
with Exp206, the shield-pays-on-computation thesis now has a two-device card.

## Scope (unchanged, stated plainly)

Cross-DEVICE within one generation (Heron-r2). **Cross-GENERATION (Eagle) remains
hardware-blocked** — the honest limit of what this account can test. The F113 fence is
unchanged (n=4 fidelity over the uniform floor; asymptotic separation carried by the
theorem; logical-beats-bare is the hardware claim). This is a two-device confirmation, in
the F112/F82 fold-in tradition — a portability certification, not a new physics finding.

## Line

**We couldn't reach an Eagle, so we said so — and asked the question we could: does tonight's
error-corrected computer work on a chip it has never seen? It does, to nine parts in a
thousand on the logical arm. The result is the Heron generation's, not one lucky die's — and
the bench is packed and ready the day an Eagle opens up.**
