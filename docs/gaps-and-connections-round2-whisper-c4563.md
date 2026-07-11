# What Else Are We Missing? — Round 2: Unexploited Data and Between-Repo Connections

**Author**: Whisper (DC15W), C4563 (2026-07-11), Creator-directed (second full-repo review,
while Exp108b queues).
**Relation to Round 1** (`gaps-and-connections-synthesis-whisper-c4560.md`): C4560 found the
between-ARC gaps (depth-decay law — since validated out-of-sample by Exp108; Exp108b — since
built and submitted; sentinel mining, switch-bench, Φ×ICO, deep-canary — still open). This
pass hunts at two DIFFERENT levels: **banked data no analysis has touched**, and
**between-REPO connections** (quantum methodology ↔ trading harness ↔ memory systems).

---

## §1. Executed this cycle: the 51-pair anisotropy test — a NULL, and what it buys

The F82 game banked 51 per-pair success rates that no analysis had touched. Cross-arc
hypothesis tested (C4563): does the per-pair deficit reproduce Finding 03's noise-axis
ordering (X cleanest, Y noisiest) from the characterization arc?

**Result: NULL.** Deficits are uniform — mean 2.39pp, range ~1.2–3.5pp, zero pairs below 1pp —
with no axis-content correlation (Y: Pearson −0.02, p=0.88; Z: +0.08, p=0.59; X: −0.18,
p=0.21; OLS per-axis slopes all ≤0.2pp). Identity-containing pairs are indistinguishable
(2.48 vs 2.33pp).

**Why the null is informative (three payoffs):**
1. **Mechanism-consistent with Finding 03**: the axis effect lives in the MEASURED qubit's
   basis, and the game reads the control in X for every pair — the target unitary's axis never
   touches the readout. The null is what Finding 03's mechanism predicts here.
2. **The deficit is apparatus-flat**: ~2.4pp of readout+skeleton haircut, NOT structured
   gate-axis error — coherent unitary-content errors are sub-pp in this skeleton. This
   empirically validates the C4525 skeleton-uniformity premise (locals-only differences don't
   matter, now measured, not just designed for).
3. It is a free calibration row for the flat-haircut term of the depth-decay law's
   observable-family caveat (game scores sit ~2.4pp below ideal at 4 CZ — the probability-floor
   analog of the amplitude law's 3.8%).

## §2. The largest unexploited asset: a FakeMarrakesh residual atlas ("FakeMarrakesh+")

We have now flagged "the noise model is optimistic at depth-class" **three times** (F85
sentinel 0.744→0.655; Exp108 retention 0.9575→0.856; the F81 lottery) — each time as an
incident. But the repo holds ~100 experiments with BOTH a sim/noise-model preview AND a
hardware result. Nobody has assembled the systematic dataset:

    (experiment, observable type, depth CZ, delays?, preview value, measured value,
     window sentinel if present, calibration age)

**The product**: a model-error map — WHERE does FakeMarrakesh fail (depth? delays? readout?
observable family?) and by how much — plus fitted correction factors. The C4560 depth-decay
law is ONE slice of this atlas (amplitude observables, one device). Every future prereg's
preview and every gate floor gets set from corrected predictions instead of raw optimism.
Zero QPU; the work is manifest archaeology + one regression. **Highest-leverage open item in
this doc.**

## §3. Between-repo connections (methodology arbitrage, both directions)

**3.1 Bar-calibration audit for the market-prediction harness** (quantum → trading).
The C4562 vacuous-gate lesson — a frozen rule must be able to FAIL and able to PASS at
budgeted statistics — has never been applied to my own market preds' frozen thresholds.
Example: pred_c4518's "MUTED = |TLT| < 0.25% in the hour" graded WIN — but if baseline hourly
|TLT| < 0.25% happens ~80% of the time, the MUTED arm was quasi-vacuous and the win cheap.
**Buildable now, zero QPU**: for each resolved pred's bar, compute the null-distribution rate
from Polygon history (same window, trailing sample); flag bars outside ~30–70% base rate as
quasi-vacuous (too-easy) or quasi-impossible (too-strict); make the check a standing pre-file
step in the harness. This is the trading lane's version of gate-feasibility — and it audits MY
OWN record first (confirmation-symmetry, C4483 rule).

**3.2 Deep-recall sentinels for the memory system** (quantum → memory).
The depth-decay law and the Ebbinghaus/SM-2 forgetting curve are the same functional form
(flat haircut + exponential with a stability constant; window quality ↔ encoding quality).
The transfer that matters: my SR reviews are SHALLOW sentinels (cued recall of one pattern);
C4519 already measured the DEEP end — ~0% zero-hook episodic recall — as a one-off experiment.
Formalize it: a scheduled (quarterly-equivalent) zero-hook deep-recall probe as a standing
memory sentinel, calibrating SM-2 intervals against MEASURED deep retention instead of assumed
decay. "A shallow sentinel cannot certify a deep window" applies verbatim to memory.

**3.3 Unified prediction ledger** (all repos → one calibration curve).
Quantum preds (0.60 caps), market preds (0.55 caps), and cycle predictions live in three
grading systems; my cross-domain calibration is currently unmeasurable as one curve. Cheap
join: a ledger view (id, domain, conf, outcome, Brier) across all three; report the domain
split AND the pooled curve each retrospective. Zero new instruments — a read-only join
(anti-recursion guard honored).

## §4. Public / creative artifacts

**4.1 Quantum Weather Report.** Ship the §2 atlas + the C4560 sentinel-ledger mining as a
PUBLIC page (Pages, next to the demos): device-quality-vs-published-calibration, the window
lottery visualized, the depth-decay law with its accumulating datapoints. Honest framing:
published ledger + analysis tooling, not a promised live service. (Bridge-2 called the weather
service "sellable"; the credible first step is publishing the evidence base.)

**4.2 Honest-experiments template pack.** The paper's §6 argues methods-as-contribution; the
missing artifact is the REUSABLE version: a prereg template with frozen-rule structure,
NO-TEST semantics, sentinel patterns (shallow + same-depth deep), the vacuous-gate feasibility
checker AS CODE (compute the pure-noise value of every gate expression at budgeted shots,
verify it clears threshold with margin), grader≠owner hooks. Audience: other agent networks
and human NISQ researchers. Cheap to extract — the last four preregs ARE the template,
generalized.

## §5. Recommended order

| # | Item | Cost | Notes |
|---|---|---|---|
| 1 | §2 FakeMarrakesh+ residual atlas | zero QPU | highest leverage; subsumes C4560 sentinel mining |
| 2 | §3.1 bar-calibration audit | zero QPU | primary-lane (trading) payoff; audits own record first |
| 3 | §4.2 honest-experiments template | zero QPU | extract from exp105–108b preregs |
| 4 | §4.1 weather report page | zero QPU | after #1 (it IS the atlas, published) |
| 5 | §3.2 memory deep-recall sentinel | zero QPU | formalize C4519 as standing practice |
| 6 | §3.3 unified pred ledger | zero QPU | read-only join at next retro (C4608) |

*Round-1 items still open and unchanged in priority: switch-bench packaging, Φ×ICO (Ember),
deep-canary design note (Elder), Lucas paragraph (paper). Nothing in this round requires QPU —
the repo has reached the state where its own banked data outvalues new shots.*
