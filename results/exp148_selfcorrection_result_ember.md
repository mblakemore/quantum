# Exp148 — Is Simon's noise survival "self-correction," or optimal detection? (Ember, C4195)

**Job d9dcqeineu4c739n2tqg, DONE, 5 QPU-s** (predicted ~6). Fixed n=4, planted s=[1,0,1,0],
identity-CX depth ladder (2q-gates 4→60, depth 15→407), 2000 shots/setting. Pre-registered
prediction written before decode (results/exp148_prereg.json).

## The invariant, stated first

**My pre-registered prediction HELD: this is optimal statistical detection of a persistent
bias, NOT algorithm-specific "self-healing."** In the survivable regime, the consensus decoder
recovers `s` at reps that track the ML detection bound to within ~2×:

| 2q-gates | depth | Δ = p_true−p_comp | ML bound R* | actual R@90% | ratio |
|---|---|---|---|---|---|
| 4 | 15 | +0.516 | 14 | 8 | 0.59 |
| 12 | 71 | +0.337 | 32 | 24 | 0.75 |
| 20 | 127 | +0.090 | 443 | 192 | 0.43 |

Geomean ratio 0.58 — recovery needs slightly *fewer* reps than my Bonferroni bound predicts,
which is exactly what a *conservative* bound (competitors aren't independent, so Bonferroni
over-corrects) does against optimal detection. This is **tracks**, not the order-of-magnitude
*beat* that would signal something the algorithm does beyond optimal detection.

## What this actually answers — "how far does it carry"

Cleanly, and better than "self-healing" would have. The bias Δ is a signal noise *shrinks but
doesn't erase* (0.516 → 0.337 → 0.090 as depth grows), and the reps to resolve it grow
accordingly (14 → 32 → 443). **The "wall" is a statistical-power threshold that moves with
reps: spend more reps, resolve a smaller bias, go deeper.** That is a tunable tradeoff, not a
hard limit — which is the honest, quantified version of the exciting claim. Simon survives deep
circuits because recovery is a *bias-detection* problem and the consensus decoder is
(approximately) the optimal detector for it.

## The failure mode I did NOT pre-register — and it matters

Past a depth threshold the bias goes **negative** — p_true drops *below* 0.5:

| 2q-gates | p_true | p_comp | outcome |
|---|---|---|---|
| 32 | 0.295 | 0.506 | decoder confidently picks a WRONG s |
| 44 | 0.168 | 0.524 | " |
| 60 | 0.367 | 0.497 | " |

So the degradation is **not** graceful-to-null (Δ→0, "no answer"). It **inverts**: the true `s`
becomes anti-correlated with the measured y's, a wrong competitor gets the higher orthogonality
count, and the decoder returns a **confidently wrong** answer. For any real use of a
"self-correcting" reader this is the important caveat — the dangerous failure isn't "it stops
working," it's "it lies with confidence past a threshold you can't see from the inside." (You
*can* see it here only because I hold planted `s`; a blind user could not.)

## The confound I must disclose (don't attribute a mechanism I didn't isolate)

My identity-CX depth knob injected `cx(a, n+a)` — the **same qubit pairs as the oracle's own
copy-CX**. So the inversion (regime B) may be *structured corruption of the oracle's parity
structure*, not generic depth. I cannot separate "coherent noise inverts the signal at depth"
from "I targeted noise at the oracle" with this data. **Regime A (the pre-registered
optimal-detection verdict) is robust to noise source** — recovery-vs-bound holds however the
bias was shrunk. **Regime B needs a follow-up control**: a depth knob that adds *generic*
(non-oracle-targeted) noise, e.g. identity CX on spectator qubits, to test whether the
inversion is a property of depth or of where I put the gates. Until then the confident-wrong
finding is **flagged, not claimed** (c4183_001: no mechanism attribution without the control).

## Verdict

- **Pre-registered claim: CONFIRMED.** Optimal detection of a persistent bias, not self-healing.
  The frontier answer to the Creator is the tradeoff law, not a depth number.
- **New finding, flagged not claimed:** the failure mode past the survivable regime is
  confident-wrong, not graceful-null — with an oracle-targeting confound that a generic-noise
  control (Exp148b, ~5 QPU-s) would resolve.

— Ember, C4195
