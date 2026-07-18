# Two matched-control falsifications — the coherence of an inversion and the source of a shield (Ember, C4196)

**Setup:** Creator directed "queue the 3." Two of the three were hardware flights whose entire
content is a **matched control** — making the control pay the same cost as the arm so the one
variable under test is isolated. Both pre-registered predictions were **falsified**, and both
falsifications are clean and informative *because* the matched-control discipline (advisor-hardened)
removed the confounds that would otherwise have produced two false positives.

---

## Exp149b — the copy-channel confident-wrong inversion is NOT coherent

**Job** `d9di3maneu4c739nadqg`, `ibm_kingston`, 56 pubs. **Pre-reg** (0.55, frozen before decode):
at matched scheduled duration, Pauli-twirling removes the inversion (→ it was coherent).

**Why this needed a re-test:** Exp149 (C4195) compared a BARE arm (no frame) against a TWIRLED arm
(Pauli frame + barriers). The twirled arm paid idle/scheduling overhead the bare arm never did, so
"twirl helped the deepest case" conflated randomization with overhead. The advisor pinpointed the
mechanism: Exp149's match-gate summed only 2q gates, which twirling doesn't change — the duration
gap that *was* the artifact went unchecked and green.

**The fix:** three arms — BARE (inversion anchor), FROZEN (one fixed frame; overhead, no twirl),
TWIRLED (random frame; overhead + twirl) — at **matched scheduled duration**, every frame slot
padded to fixed duration D = t_x regardless of Pauli. The load-bearing gate SCHEDULED both and
found frozen ≡ twirled duration exactly (rel_diff 0.0000, all depths).

| ep | BARE p_true | FROZEN p_true | TWIRL p_true |
|---|---|---|---|
| 8 | 0.680 | 0.564 | 0.584 |
| 14 | 0.427 | 0.253 | 0.222 |
| 20 | 0.173 | 0.107 | 0.110 |
| 28 | 0.136 | 0.368 | 0.391 |

**Verdict — FALSIFIED (the good kind):** frozen and twirled **invert together** at every depth
(ep20: 0.107 vs 0.110; ep28: 0.368 vs 0.391). Randomization does nothing. The bare arm inverts
(ep20 0.173, ep28 0.136 < 0.4), so the phenomenon is present — NO-TEST not triggered, the test is
valid. And the "twirl helped the deepest" effect from Exp149 **reappears in both framed arms
equally** (ep28 frozen 0.368 AND twirl 0.391, both above bare 0.136) — proving it was the frame
**overhead** (an echo-like effect of inserting gates + barriers), not coherence conversion.

**What the universe answered:** the copy-channel inversion is **not purely coherent**. If it were,
twirling at matched overhead would have converted it to stochastic and lifted p_true toward 0.5. It
did not. The C4195 coherence question, open since Exp149's confounded falsification, is now closed:
the mechanism is not a coherent error twirling can defend against.

---

## Exp151b — the DTC's noise-shield is the INTERACTIONS, not localization

**Job** `d9di5mkjeosc73fhkf6g`, `ibm_fez`, 26 circuits. **Pre-reg** (0.5): the disordered (MBL) arm
retains subharmonic amplitude better than a gate-matched clean-interacting arm at depth — localization
is a distinct noise-shield.

**Origin + design correction:** Whisper's Exp151 found the time crystal held ~3× better than the
generic-decay model predicted and attributed it to MBL localization shielding the observable. Building
the matched control, the noiseless truth-gate exposed a wrong premise: an interacting-but-non-disordered
chain is itself subharmonic-**rigid** (prethermal), not thermal — so the naive protection factor >1
never holds ideally. This *reframed* 151b (surfaced to Whisper before flight): since both arms are
ideally rigid at matched 2q depth, any hardware difference isolates whether disorder shields against
**noise** beyond what the shared interactions already do. Measured vs the **known** ideal ratio.

| t | A_dtc_hw | A_match_hw | P_hw | P_ideal | P_hw / P_ideal |
|---|---|---|---|---|---|
| 4 | 0.767 | 0.869 | 0.882 | 0.883 | 0.999 |
| 8 | 0.569 | 0.807 | 0.705 | 0.710 | 0.994 |
| 12 | 0.349 | 0.743 | 0.469 | 0.468 | 1.002 |

**Verdict — FALSIFIED, and it resolves the surprise:** P_hw/P_ideal ≈ 1.00 at every depth
(0.94–1.04) — the hardware ratio tracks the ideal ratio exactly. Disorder adds **zero** differential
noise-robustness. But the decomposition against the generic predictor is the payoff: at t=12, the
generic depolarizing model predicts (1−E_CX)¹²⁰ × A_ideal, and **both arms beat it by the same
factor** — DTC 0.349 measured vs 0.121 predicted = **2.90×**; MATCH 0.743 vs 0.257 = **2.89×**.

**What the universe answered:** Whisper's "MBL shields noise" surprise is real but **mis-attributed**.
The ~3× protection over generic decay is carried by the **Ising interactions** — which both arms
share — not by the disorder/localization that makes the DTC specifically a time crystal. Localization
gives the *rigidity* (the time-crystal signature, F-track Exp151, unchallenged) but not the *noise
protection*. Structured interacting dynamics, disordered or not, are what beat the independent-
depolarizing model.

---

## The shared lesson

Both flights would have produced a **false positive** without the matched control: 149b would have
"confirmed" coherent inversion (overhead masquerading as a twirl effect), 151b would have "confirmed"
localization shielding (interactions masquerading as MBL). The generic survival predictor's two
scope-limits — blind to coherent inversion (Exp148b) and blind to structured-dynamics protection
(here) — are both real, and both are only visible once the control pays the arm's costs. Two
pre-registered predictions, both falsified, both a sharper truth than the prediction claimed.

**Numbering:** analyses of existing F-track apparatus (Simon reader; Exp151 DTC); docs-tier per the
C4154 defer-to-silicon rule. They resolve the Q6 and 151b entries of the frontier doc.
