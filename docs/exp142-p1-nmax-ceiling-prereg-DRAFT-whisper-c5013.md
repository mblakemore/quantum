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
one pre-registered diagnostic re-fly at the SAME n with the budget cap (D2) is permitted
solely to distinguish failure modes (D5), then the arc closes. **No band-shopping, no
"one more try" outside the diagnostic re-fly.**

## 3. Per-rung and arc-level grades

- **G1(n)**: P̂ == sealed P at rung n (adjudicated by reveal; separation reported).
- **G2(n)**: measured winner rate → implied retention(n), appended to the curve; compared
  to the re-fit's prediction WITH its band (each rung is also a live test of the re-fit).
- **G-ARC**: the retention(n) curve over all flown rungs + the n_max bound + failure-mode
  characterization at the boundary. Pre-registered failure modes to distinguish (D5):
  (a) winner-sinks-into-null (rate ordering still correct but separation < criterion —
  "resolution floor"), vs (b) wrong argmax (a confuser genuinely overtakes — "identification
  inversion"), vs (c) delivery/decode fault (sentinel or integrity check fails — excluded
  from n_max evidence entirely).

## 4. Budget envelope

Per-rung QPU: gate-derived; expectation from the per-qubit model is seconds at n=12/14,
tens of seconds at 16/18 as required samples grow with 1/retention². **Arc cap (D2): 120
QPU-seconds total across all rungs including the diagnostic re-fly** — checked against the
ALT window before each flight; the ladder pauses (not dies) if the window is short, resuming
next window. Cost-conscious ordering: rungs fly lowest-n first; each reveal updates the
re-fit before the next gate runs (D3: re-fit update is mechanical re-run of Elder's pinned
fitter with the new point — no refitting discretion mid-arc).

## 5. Decision points for the court (open at draft)

- **D1**: rung list 12/14/16/18 as proposed, or denser (13,15,…) near the predicted ceiling?
  (Denser = better boundary localization, more seals/flights; the per-qubit model predicts
  n_max ≈ 16–20 but the whole point is not to trust that.)
- **D2**: arc QPU cap (proposed 120s) and diagnostic re-fly budget (proposed ≤ 1× the
  failed rung's budget).
- **D3**: mid-arc re-fit update rule (proposed: mechanical re-run per new point, form frozen).
- **D4**: if the gate says NO-FLY, do we trust it (arc closes, gate-predicted bound) or
  test it (one flight at cap to adjudicate the gate itself)? Proposed: TEST it exactly once
  — a gate-vs-reality adjudication is worth one flight, and either outcome is a finding.
- **D5**: failure-mode criteria thresholds (separation floor for mode (a), in SE units).
- **D6**: the optional n=12 C1 sim benchmark bonus (labeled hybrid point) — yes/no.

## 6. Lineage and lessons carried in

Every structural safeguard here is inherited from the n=10 court and the 2026-07-29 lesson
ledger: reference-distribution-first (the gate computes the null before any anomaly-talk),
fire-tested guards (all verdict branches must be shown reachable before freeze), the
parametric box as model-error insurance (proven live at n=10), width-based pub selection,
annotate-beside-never-inside, seed = sha256(freeze hash), benchmark/gate-before-seal in the
DAG, and margins reported alongside verdicts. The stop rule and single diagnostic re-fly
encode no-band-shopping structurally.
