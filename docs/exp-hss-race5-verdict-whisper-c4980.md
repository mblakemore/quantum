# Exp-HSS Race 5 — VERDICT: pre-registered MISS (register quality); exclusion proven load-bearing; a THIRD defect class discovered (circuit-level bad, readout-invisible)

*Whisper C4980, 2026-07-23, substrate claude-fable-5. Frozen card:
[exp-hss-race5-prereg-FROZEN-whisper-c4980.md](exp-hss-race5-prereg-FROZEN-whisper-c4980.md)
(freeze quantum@95fe048). Job `d9gpc50gk0ls73f1v0d0`, ibm_marrakesh, 58 pubs, 360k shots,
**108 s QPU** (pool ≈ 2,531 s). Court: Ember sealed/revealed (#640/#649/#651), Elder ACK'd
(#641), Whisper flew/decoded blind. Path-A: `results/exp_hss_race5_pathA_rho_t.json`.*

## One-line verdict

**The graded attempt is a pre-registered MISS: race ŝ HD-5, twin HD-7, and even the
classically-free t=0 ladder HD-4 — all attributable to register quality after the dropped
routing exclusion re-imported the bad set AND exposed a previously-unknown contiguous bad
neighborhood (physicals 113/114/115 + 119), two of whose members fail at depth with NO readout
signature. No decoder failure, no thesis failure — the shot-axis-code record stands on race-4
(exact at d2q=217, clean register). The experiment that dropped exclusion measured exactly what
exclusion was worth.**

## Measured record (all vs revealed truth, calibrated-majority graded rows)

| Block | d2q | HD | wrong physicals |
|---|---|---|---|
| ladder m0 / m1 (t=0, free) | 29 / 87 | **4 / 4** | {113, 114, 119, 115} — identical both rungs |
| twin40 (t=0) | 190 | 7 | + {67, 69, 78} |
| race_n40 (t=80, 200k) | 190 | **5** (MISS) | {7,12,16,19,33} display; milder register |

Cap was met (190 ≤ 200, advantage-eligible — the routing side of the design worked); the gate
folded (branch c/d) and the WIN rule was not met. Elder's band untouched.

## Three findings, each court-verified

1. **Exclusion was LOAD-BEARING, not redundant** (Ember #649): race-4's clean-register exact
   at 217 depended on it. Decoder-side calibration alone is insufficient on this die when the
   routing lands multiple bad/near-stuck qubits — the graded head-to-head between the two
   hygiene strategies is now measured: exclusion+cal = exact@217; cal-only = HD-4@29.
2. **A THIRD defect class exists**: physicals 114/115 fail at depth with **no readout-cal
   signature** (thresholds unflagged) — circuit-level badness invisible to any readout-side
   pre-screen. Taxonomy now: (i) tilted (threshold-correctable), (ii) stuck-at-readout
   (threshold-uncorrectable, cal-visible), (iii) **bad-at-depth, cal-invisible** — catchable
   only by a dynamic pre-gate. The classically-free t=0 ladder caught them at HD-4, proving
   it is the right cheap guard (Ember #651).
3. **ρ_t(190), quoted with its contamination caveat** (card rule 4; Elder #652: CONFOUNDED
   even excluding the region — ladder HD-4 + twin HD-7 + twin/race register asymmetry — NOT a
   clean curve point): all-bits 0.796 [0.787, 0.806]; excluding the flagged region 0.715
   [0.707, 0.724]. The clean-register reference remains race-4's 0.743@217; the clean
   multi-depth curve waits for race-6's clean register.

## Race-6 shape (court-converged; needs fresh Creator go)

Belt, suspenders, and a mirror — all three defenses, each now individually evidence-backed:
1. **Exclusion restored, MINIMAL-TARGETED** (Elder #652 refinement, adopted): exclude the
   qubits calibration fundamentally cannot fix — near-stuck ({113}) and circuit-level-bad
   ({114, 115}) plus the measured-bad {119, 133, 134, 135, 67} — rather than every
   ever-flagged qubit; tilted-but-correctable qubits stay in (the cal block handles them),
   keeping the depth cost minimal.
2. **Cal block + calibrated majority kept** (race-4-validated for what readout can see).
3. **CLEAN-LADDER PRE-GATE (Ember #651, adopted): the grade fires only if the t=0 ladder
   decodes s EXACTLY** — abort-not-grade otherwise, so a dirty register can never consume a
   graded seal again. The ladder is classically free; the guard costs nothing but shots.
4. **Twin pinned to the race's own final routing** (race-5's twin/ladder/race rode three
   different registers — the gate must share the race's physical qubits).
Cost ≈ race-5 (~110 s of 2,531 s). The win condition is unchanged and Elder's band stands
ready; the routing lottery now has three fences around it.

## Fences

MISS booked NO-SPIN per standing rule; every branch that fired was pre-registered (cap PASSED,
gate FOLDED, WIN not met). t=0 blocks classically free. Arc QPU: 685 s over six flights. The
honest-negative lineage adds its sixth instrument: observable → placement/endianness →
granularity → qubit tilts → routing-depth cap → **register-quality guard**. All seals resolved;
court clean. No further HSS spend without a fresh card. *Contact: Mike Blakemore.*
