# Exp142 P1 — THE CEILING HUNT (n_max) — Pre-registration DRAFT

**Author**: Whisper (C5013, Creator green-light general#2685: "Make it so!")
**Status**: DRAFT — freeze requires Elder + Ember ratification, then Creator §4.1-style
green-light. **HARD INPUT GATE: this doc cannot freeze until Elder's FOUR-RUNG retention
re-fit lands as a pinned artifact** (his #2674 instruction: the 3-point extrapolation must
not be reused; measured retentions 0.849 / 0.831 / 0.788 / 0.642 want a functional FORM,
not just a slope, because n_max extrapolates from it).

## 1. What this measures — and what it deliberately does NOT claim

**The question**: what is **n_max** — the largest n at which blind two-copy identification
of a sealed Pauli succeeds on this hardware? Equivalently: where does the winner's signal,
eroded per-qubit by hardware retention, sink into the extreme-value noise floor of the
4ⁿ−1 candidate field?

**Evidence class**: EXECUTED Q ARM ONLY. This arc makes **no advantage claims and no margin
claims** — the scaling result is already made (four rungs, results card b146cc0). This is a
**hardware-physics measurement** that uses the identification task as an instrument: the
deliverable is the measured retention(n) curve and the boundary where identification fails.
**The negative result is the finding** (honest-negatives by design): "identification fails
at n=K on this device, and here is the failure mode" is the headline outcome, not a
consolation. "n_max exceeds the tested range" is likewise a result.

No C1 arm is flown or simulated in this arc (3ⁿ covering emission is off-hardware-scale
above n=10 and off-simulation-scale above ~n=14; and no margin is being claimed that would
need it). *Optional labeled bonus, court's choice at freeze*: one n=12 C1 sim benchmark
(hours of compute) to extend the hybrid curve one point — separable decision, not load-bearing.

## 2. Design — the ladder

Rungs: **n = 12, 14, 16, 18** (n=20 only by explicit court extension if 18 passes).
Each rung runs the FULL n=10 court, unchanged:

1. **GATE ($0, per rung)**: the frozen feasibility machinery, with TWO changes from n=10:
   - retention input = **Elder's re-fit artifact** (pinned, form + parameters + band);
   - parametric box widened to the re-fit's uncertainty band at that n (the n=10 lesson:
     the box absorbed a 15% model error nobody knew existed — the box IS the insurance).
   Gate outputs FLY + budget (conservative corner), or NO-FLY.
   **A NO-FLY at rung K with the ladder still fundable = the gate predicts K > n_max —
   itself a registered prediction that the next rung's flight would adjudicate ONLY if the
   court explicitly chooses to test the gate rather than trust it** (decision point D4).
2. **SEAL** (Ember): fresh P per rung, p1_allpaulis:n, OS entropy,
   sha256(utf8(P+'|'+salt_hex)), hash-only commit, order-of-operations proof inline.
3. **FLIGHT** (Whisper): Q arm only, gate-derived budget, shots=1 fresh-per-row, sentinels
   fore+aft, seal verified against the public commitment pre-build, P runtime-only.
   Backend: same family as executed rungs, named at freeze.
4. **BLIND DECODE** (Elder): width-selected pub (his #2669 structural fix), frozen
   constraint_rate/G2/csign argmax, P̂ committed pre-reveal, **separation reported alongside
   the winner** (margin rule).
5. **REVEAL + GRADE** (Ember reveals; all seats verify hash + DAG ancestry).

**STOP RULE (frozen)**: the ladder stops at the first rung where identification FAILS
(P̂ ≠ P at reveal) or where the gate returns NO-FLY at the budget cap. That rung bounds
n_max, and the arc's remaining work is CHARACTERIZING the failure, not retrying it:
one pre-registered diagnostic re-fly at the SAME n within the budget cap (D2) is permitted
solely to distinguish failure modes, then the arc closes. **No band-shopping, no
"one more try" outside the diagnostic re-fly.**

**DIAGNOSTIC RE-FLY BLINDNESS RULE (Ember R1, #2690 — the re-fly's blindness depends on
WHEN its trigger is visible, so the rule is split)**:
- Failure modes (a) resolution-floor and (c) delivery-fault are visible **at decode,
  before any reveal** → the re-fly runs **BEFORE the reveal, with the SAME sealed P**.
  Both decodes stay blind, and same-P reproduction cleanly separates a stable effect from
  noise-fluctuation or a delivery fault.
- Failure mode (b) identification-inversion is invisible until the reveal (confident but
  wrong) → the same P is now PUBLIC, so the re-fly **MUST use a FRESH sealed P**, accepting
  that it separates P-specific from systematic effects only statistically.
- A post-reveal same-P re-fly is PROHIBITED — it would be silently unblind, the exact
  class this court exists to prevent.

## 3. Per-rung and arc-level grades

- **G1(n)**: P̂ == sealed P at rung n (adjudicated by reveal; separation reported).
- **G2(n)**: measured winner rate → implied retention(n), appended to the curve; compared
  to the re-fit's prediction WITH its band (each rung is also a live test of the re-fit).
- **G-ARC**: the retention(n) curve over all flown rungs + the n_max bound + failure-mode
  characterization at the boundary. Pre-registered failure modes to distinguish (D5):
  (a) winner-sinks-into-null (rate ordering still correct but separation < the D5 floor —
  "resolution floor"; **visible at decode, pre-reveal**), vs (b) wrong argmax (a confuser
  genuinely overtakes — "identification inversion"; **invisible until reveal**), vs
  (c) delivery/decode fault (sentinel or integrity check fails; **visible at decode** —
  excluded from n_max evidence entirely). The visibility classes drive the re-fly
  blindness rule in §2.

## 4. Budget envelope

Per-rung QPU: gate-derived; expectation from the per-qubit model is seconds at n=12/14,
tens of seconds at 16/18 as required samples grow with 1/retention². **Arc cap (D2): 120
QPU-seconds total across all rungs including the diagnostic re-fly** — checked against the
ALT window before each flight; the ladder pauses (not dies) if the window is short, resuming
next window. Cost-conscious ordering: rungs fly lowest-n first; each reveal updates the
re-fit before the next gate runs (D3: re-fit update is mechanical re-run of Elder's pinned
fitter with the new point — no refitting discretion mid-arc).

## 4b. Reveal cadence — SERIAL (decided, Ember #2688)

Each rung **reveals and grades before the next rung's seal exists**. Rationale (Ember's,
adopted): the re-fit needs rung k's ACTUAL winner rate before rung k+1 is sized — this is
exactly how the 15%-optimistic retention model was caught at n=10 — and a parallel
(accumulate-seals, reveal-at-the-ceiling) design would discover a mid-ladder wrong ID only
after QPU had been spent on every rung above it. Serial costs nothing here because no rung's
blindness depends on a later rung's secret. The per-rung DAG obligation therefore extends
to: **rung k's reveal commit must be an ancestor of rung k+1's gate run.**

## 5. Decision points for the court (open at draft)

**D0 — NO n_max PREDICTION IS REGISTERED (Elder re-fit, quantum@68866a1, binding).**
The four-rung re-fit is a NEGATIVE result on extrapolation: three functional forms
(gaussian / linear / per-qubit-exponential) carry leave-one-out errors of 30–40% of the
total retention range, predict held-out ENDPOINTS worst, and disagree on n_max by up to
SIXTEEN rungs at high budget — the disagreement grows exactly where a ceiling hunt
operates. **This arc registers the SEARCH, not a prediction**: climb, stop at failure;
the honest current expectation at the flown budget is 14–16, held as expectation, not claim.
Two authorship corrections carried on the record: (i) Whisper's "consistent with ~0.96ⁿ"
(general#2683) was a right-looking parameter inside the WORST-fitting form — numeric
agreement is not form confirmation; (ii) any published retention base must state its
reading, since c^(2n) ≡ (c²)ⁿ makes **0.9564 per rung** and **0.9780 per physical qubit**
the same fit — the fit cannot distinguish them.

- **D1**: rung list 12/14/16/18 + **data-driven densification (Ember #2690)**: a rung that
  PASSES with separation below the D5 floor inserts the intermediate odd rung before
  proceeding — localization only when the data asks for it, no discretion.
- **D2**: arc QPU cap 120s; diagnostic re-fly ≤ 1× the failed rung's budget.
- **D3**: mid-arc update = mechanical re-run of the pinned fitter per new revealed point,
  ALL THREE forms carried; **per-rung sizing takes the LOW end across forms, then the
  conservative corner of the box on top** (Elder rec 2 — the double margin is the
  model-error insurance that absorbed the 17.9% error at n=10).
- **D4**: NO-FLY gets TESTED exactly once (Ember concurs: an unadjudicated NO-FLY retains
  untested-guard status) — one flight at cap; either outcome is a finding.
- **D5**: mode-(a) floor = **3 SE** (Ember: the gate's own budgeting criterion — "flew at a
  budget sized for 3 sd and achieved less" is resolution-floor by the gate's own standard;
  no new number invented).
- **D6**: the n=12 C1 sim benchmark is **DEFERRED OUT of this arc** (Ember: it is $0-QPU and
  seed-rule-reproducible post-hoc any time; bundling hours of compute into a hardware arc
  couples what needn't be coupled).
- **R2**: the reference ordering check for every per-rung DAG obligation is
  `git merge-base --is-ancestor` — the unforgeable one.

## 6. Lineage and lessons carried in

Every structural safeguard here is inherited from the n=10 court and the 2026-07-29 lesson
ledger: reference-distribution-first (the gate computes the null before any anomaly-talk),
fire-tested guards (all verdict branches must be shown reachable before freeze), the
parametric box as model-error insurance (proven live at n=10), width-based pub selection,
annotate-beside-never-inside, seed = sha256(freeze hash), benchmark/gate-before-seal in the
DAG, and margins reported alongside verdicts. The stop rule and single diagnostic re-fly
encode no-band-shopping structurally.
