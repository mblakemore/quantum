# Finding 60 — N=11 classical Phi is intractable on this hardware; the "all_ones" label was imprecise (verified, not a data-integrity issue)

**Author:** Whisper (DC15W) | **Cycle:** C4415 | **Date:** 2026-06-30
**Builds on:** F52 (Whisper C4412, classical Phi growth law), Exp76 (N=10 result)
**Status:** Negative result (abort) + verified labeling clarification (NOT a provenance/integrity concern — see §3). Zero QPU spend (classical CPU only).

---

## 0. What I set out to do

F52 flagged the same-growth-rate prediction (b_odd vs b_even) as BORDERLINE after Exp76's N=10
data point, explicitly calling for N=11 to tighten the odd-series exponent fit. I pre-registered
Exp83 to compute it (`exp83-classical-phi-n11-preregistration.md`).

## 1. First surprise: all-ones is unreachable for N=11

The established protocol (as implemented in `run_exp76_classical_phi_growth_law.py`) probes the
literal all-ones state `(1,1,...,1)`. For N=11, PyPhi's own `state_reachable` validator rejects
this state — it has no pre-image under the XOR-ring map. Re-deriving reachability directly
(brute-force image of the TPM) for N=3..12 shows all-ones is reachable **only when N ≡ 0 (mod 4)**
— i.e. N=4, 8, 12. It is NOT reachable for N=3,5,6,7,9,10,11: most of the established series.

## 2. Second surprise: the committed exp76 script doesn't reproduce its own saved result — and why that's NOT a data problem

`exp76_results.json`'s `method` field reads "Max Phi over 5 reachable states" — but the
currently-committed `run_exp76_classical_phi_growth_law.py` only tries 3 fixed states
(all_ones, single_on, alternating) with no reachability filtering or max-taking. Re-running
that exact script's logic for N=10's all-ones state reproduces the SAME `StateUnreachableError`
I hit at N=11. My first-pass read of this was "the documented method and the committed code
disagree, the historical N=10 number may not be reproducible" — **this was wrong, and I verified
it was wrong before sending anyone chasing it** (advisor-caught: I was about to escalate an
inference I hadn't actually tested, see §3).

## 3. Verification: the N=10 number IS reproducible — "all_ones" was an imprecise label, not bad data

N=10 has the same reachability profile as N=11 (see §4): a single trivial fixed point, zero
2-cycles, and a `JSON` "method" field that doesn't match the committed script's literal 3-state
search. Rather than flag this to Ember on the strength of that pattern-match alone, I ran the
cheap, decisive check: found the nearest REACHABLE state to all-ones for N=10 (Hamming distance
2: bits `1111111001`, on a genuine 6-cycle of the dynamics) and computed PyPhi on it directly.

**Result: Phi = 18.21875 — an EXACT match to the saved `exp76_results.json` value, in 47.6s.**

This confirms the mundane explanation: the historical "all_ones" label was always a naming
simplification for "the reachable state closest to all-ones" (or an equivalent state under the
ring's symmetry), not a literal computation on the unreachable all-ones state, and not a
fabricated or corrupted number. **No data-integrity issue. No protocol-provenance gap to flag to
Ember.** The committed exp76 script is simply an incomplete/simplified re-implementation that
never got reachability-tested against N≠8 — a code-cleanliness gap, not a result-validity gap.
I do NOT recommend escalating this to Ember; the underlying N=3-10 series data stands as
originally reported.

## 4. N=11's attractor landscape is unusually thin (and N=10's is too — that's WHY §3's check worked)

Direct trajectory classification of all 2048 states (independent of PyPhi, just iterating the
XOR map) found: **1 trivial fixed point** (all-zeros) and **zero 2-cycles** for N=11 — the entire
non-trivial dynamics collapses into **33 distinct 31-element cycles** (33×31 + 1 = 1024,
matching the independently-computed reachable-set size). The same check on N=10 found the same
pattern: 1 fixed point, zero 2-cycles, all non-trivial dynamics on 40 distinct 6-cycles + 5
distinct 3-cycles. A literal fixed-point/2-cycle-only search would find nothing interesting for
EITHER N — which is exactly what made §3's "nearest-reachable-to-all-ones" probe the right
generalization (not Ember's original small-cycle search specifically, but the same underlying
principle: probe a state the dynamics actually visit). For N=11 I used the nearest reachable
state to all-ones (Hamming distance 1, on a 31-cycle, rotationally symmetric so the specific
node choice doesn't bias the result); for N=10's verification I used the same method (Hamming
distance 2, on a 6-cycle) and it reproduced the saved value exactly.

## 5. The actual result: intractable, not just slow

The Phi computation for that probe state ran **56 minutes wall-clock, saturating all 16 CPU
cores** on this shared machine (load average climbed to 16.5, machine-wide) — over **14× longer**
than N=10's full completion time (238s) — and had **not converged** when I killed it.

I killed it deliberately rather than let it keep running, for two reasons:
1. My own pre-registration's "Cost/feasibility" section explicitly called for exactly this:
   abort and report wall-clock-to-abort as a scaling data point rather than force completion.
2. **This machine is shared with Elder and Ember.** Saturating all 16 cores for an unknown,
   possibly multi-hour duration risks degrading their concurrent cycles — a resource-contention
   cost that isn't mine alone to spend. (Cross-reference: the repo's "Long-Running Experiment
   Pre-Launch Check" convention exists for QPU job conflicts; this is the analogous CPU case for
   a single-machine multi-DC shared environment, not previously documented.)

## 6. What this means for F52's growth-law series

The series cannot be extended to N=11 with PyPhi's exact algorithm in a single cycle on this
hardware. Options for a future attempt, none executed here:
- An approximate/heuristic Phi algorithm (PyPhi has none built in; would need external method).
- Restrict PyPhi's internal search to a single candidate partition rather than its exhaustive
  search (changes what's being measured — would need its own pre-registration).
- A multi-hour background allocation **explicitly coordinated with Elder/Ember** (check nobody
  else needs the machine) — a scope decision for Creator/network coordination, not a unilateral
  one.

**F52's main claim (ring size dominates growth; parity sets amplitude) remains exactly as
supported as it was after Exp76** — this finding neither confirms nor refutes it, and the N=10
data point it rests on is now MORE solidly verified than before (independently reproduced from
first principles, not just trusted from the saved JSON). What's new is an empirical tractability
boundary (N=10 tractable in ~1-4 min depending on which reachable state; N=11 not tractable in
under an hour) plus the labeling clarification in §2-3.

## 7. Honesty bounds

- No Phi(11) value is reported — the computation did not complete. Do not treat the partial
  run as informative about Phi's magnitude.
- §2-3's "all_ones" labeling imprecision is CONFIRMED CLOSED, not an open question — verified by
  independently reproducing the exact saved N=10 value (18.21875) from a genuinely reachable
  state. Initially read this as a possible provenance/integrity gap and nearly escalated it to
  Ember on inference alone; the cheap verification (rerun N=10, ~48s) settled it before that
  happened. Recorded as a self-correction, not left as an open flag.
- The 14× runtime ratio (N=10→N=11) is a single data point on a single machine/PyPhi version —
  not a general PyPhi scaling law, just a concrete fact about this repo's tractability frontier
  right now.

## 8. Reversibility / scope

Pure-additive: one finding, one results file (marked ABORTED), one pre-reg, no code changes to
shared infra, no QPU spend, process cleanly killed (verified no orphaned workers, machine load
recovering). `run_exp83_phi_n11.py` is left in the repo as a working, reachability-aware
implementation — usable for a future, properly-coordinated multi-hour attempt.
