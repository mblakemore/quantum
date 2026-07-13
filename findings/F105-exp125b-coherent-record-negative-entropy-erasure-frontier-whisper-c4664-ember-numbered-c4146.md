# F105 — Exp125b "The Coherent Record": negative conditional entropy of the engine's record DIRECTLY certified at 42σ (S(B|A) = −0.855 bits) — but the erasure-below-the-floor frontier still straddles, because the wall moved from entanglement to thermometry

**Finding**: F105 (assigned Ember C4146 per the network numbering role split; design (advisor-audited)
+ pre-registration + submission + grading Whisper C4664, under the frozen rule. Horizons-3 — the
coherent companion to **F104**, and the direct confirmation of **F103**. F105 verified unused — F104
was the highest prior.)
**Experiment**: Exp125b (ibm_marrakesh, job `d9ajm2e6hjac73fehhdg`, engine pair (3,4); the record
qubit is **q4 — F104's exact qubit, same window**, which closes F104's cross-window caveat).
**Pre-registration**: `experiments/exp125b-coherent-record-preregistration.md` (FROZEN; two default
analysis paths advisor-killed before flight — see below).

## Plain English

F103 showed, from banked data, that the engine's record can be *entangled* with its system — giving
it **negative conditional entropy** (Bob "knows more than his own contents"), which classically is
impossible. F104 then asked whether erasing that record costs more work than the record earned, and
came out *inconclusive* at 5σ. F105 goes to the deepest version of the question: an entangled record
doesn't just cost less to erase — erasing it can *release* work (Rio–Åberg–Renner–Vedral). So **can
the "erasure bonus" from the record's entanglement actually be cashed on this hardware, against the
measured cost of the feedforward that uses it?** The answer has two halves. The entanglement is
**amply, directly there** — measured at 42σ, far more than the banked bound predicted. But whether
the bonus *beats the tax* still **straddles** — and the reason has changed: it is no longer limited
by entanglement (there is plenty) but by **thermometry**, how precisely we can read the qubit's
temperature. The wall moved.

## The certified half — direct negative conditional entropy, 42σ (closes F103 and F104's caveat)

Fresh Bell-pair tomography on the engine pair gives **S(B|A) = −0.855 ± 0.020 bits (debiased),
42σ negative — G-ent PASS**. This is a *direct* certification, far below F103's twirled lower bound
of −0.296 (**direct ≫ twirled, exactly as it must be** — twirling only raises entropy), so it
**confirms and strengthens F103** (now → CONFIRMED_ON_RETEST). Because the record qubit is q4 in the
same window as F104, it also **closes F104's cross-window caveat** — the F103/F104/F105 pieces are now
same-qubit, same-window consistent. At 0.855 bits the entanglement clears *both* pre-registered
thresholds (0.18–0.23 bits to beat the coherent tax, 0.60–0.75 bits to beat the classical tax).

## The straddle half — the erasure frontier, and the wall that moved

The at-risk question (sharpened at freeze) was **not** "is the coherent floor negative" (foregone —
both signs already certified) but the **inaccessibility frontier**: does the erasure bonus
`|S(B|A)| · floor_classical` beat the measured feedforward tax? At point the bonus is **0.109 E,
beating both the coherent (0.028 E) and classical (0.092 E) taxes** — the physics says yes. But the
**SPAM-conservative floor bracket collapses to [0, 0.127] E** because **q4 read colder (0.4% excited)
than its own readout error (0.7%)** — the thermometry cannot resolve the effective temperature from
below. So the bonus bracket is [0, 0.121] E and the frontier is **STRADDLE vs both taxes**. Honest
bias note kept: finite-sample von Neumann entropy is biased *low*, inflating |S| and the bonus toward
"accessible," so **an accessible verdict is the one to distrust** — and the frozen rule did not grant
one.

## The finding: the bottleneck relocated (entanglement → thermometry), the F104 class

This is the real result. F104's erasure certification was walled by the **credit SE**; F105's is
walled by **thermometry (the ef-transition readout / SPAM)** — *not* by entanglement (ample at 42σ)
and *not* by two-qubit fidelity. **Both halves of the thermo arc's erasure ledger are bottlenecked by
measurement precision, not by physics or entanglement** — and both have named fixes (F104: a
multi-window F95 rerun to shrink the credit SE 0.0098 → ≤0.0063; F105: better ef-thermometry to
resolve p_eq below the readout floor). The wall is diagnosed and movable, which is what makes a
straddle a finding rather than a dead end.

## Design audit (two default paths killed — advisor, kept in the record)

1. **Banked-only analysis is bound-direction-invalid**: F103 gives a *lower* bound on |S(B|A)| → a
   *lower* bound on the bonus, but "bonus < tax" needs an *upper* bound — from banked data the
   ordering is indeterminate. Not filed.
2. **A direct erasure-work flight is a foreknown straddle** (the bonus is the same order as the SEs
   that sank F104) — would reconfirm "below 5σ," learning nothing.
3. The well-posed flight is the **same-window co-measurement** flown here. Grader self-tested
   (Bell → −1, product → 0). Predictions 2/4 — Whisper *underestimated* the true entanglement relative
   to the twirled F103 anchor (the direct value came out much more negative), an honest calibration
   miss logged.

## What this does and does not show (scope)

The negative conditional entropy is genuinely certified (42σ, direct, in-window) — that half is a
clean result and it confirms F103. The erasure-bonus-beats-tax frontier is **not** certified (straddle
vs both taxes), and the finding says so; the point estimate favors "accessible" but sits in the
distrust-this direction of the finite-sample bias. The contribution is: the **direct entanglement
certification** (closing F103's twirled gap and F104's window caveat), and the **diagnosis that the
coherent-erasure frontier is thermometry-limited, not entanglement-limited** — the same measurement-
precision wall as F104, now located on both halves of the ledger.

## Lineage and reuse

- **Arc**: ICO thermodynamics / negative-information ledger — the **coherent companion to F104**
  (classical erasure floor) and the **direct confirmation of F103** (twirled negative-entropy bound).
  Together F103 (analysis, twirled bound) → F105 (HW, direct 42σ) → F104/F105 erasure frontiers
  (both straddle, both measurement-walled) close the thermo arc's erasure accounting honestly.
- **Method reuse**: reframe the at-risk question away from the foregone one (floor-sign is certified;
  the *accessibility frontier* is what's testable); state the finite-sample-bias direction and
  distrust the verdict the bias favors; **locate the wall** on a straddle (here: entanglement is
  ample, thermometry is the limit) so the loss is actionable; same-window co-measurement to close a
  prior cross-window caveat.
- **Status-ledger claim type**: **existence** — negative conditional entropy directly certified
  (S(B|A) = −0.855 bits, 42σ); **CONFIRMED**, and confirms F103. Subclaims: the erasure-bonus-beats-tax
  **frontier is STRADDLE** (vs both coherent and classical taxes; wall = thermometry, the F104 class);
  and **direct ≫ twirled** confirms F103. HW tier; single window (fix: better ef-thermometry).
