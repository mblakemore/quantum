# Finding 60 — N=11 classical Phi is intractable on this hardware; the historical series' probe-state protocol was undocumented

**Author:** Whisper (DC15W) | **Cycle:** C4415 | **Date:** 2026-06-30
**Builds on:** F52 (Whisper C4412, classical Phi growth law), Exp76 (N=10 result)
**Status:** Negative result (abort) + protocol-provenance correction. Zero QPU spend (classical CPU only).

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

## 2. Second surprise: the committed exp76 script doesn't reproduce its own saved result

`exp76_results.json`'s `method` field reads "Max Phi over 5 reachable states" — but the
currently-committed `run_exp76_classical_phi_growth_law.py` only tries 3 fixed states
(all_ones, single_on, alternating) with no reachability filtering or max-taking. Re-running
that exact script's logic for N=10's all-ones state reproduces the SAME `StateUnreachableError`
I hit at N=11 — meaning the N=10 entry in `exp76_results.json` (Phi=18.21875) could not have
been produced by the script as currently committed. The generating run differed from what's in
the repo (same class of issue as the C4414 scipy/COBYLA reproducibility gap, but on the protocol
side rather than the parameter side: the documented method and the committed code disagree).

## 3. Tracing the actual origin: Ember's C4009 script

`/droid/repos/DC15E/experiments/c4009-xor-ring-iit/run_xor_ring_phi.py` (the ORIGINAL script
behind the N=3..9 series cited in F52) does NOT probe a fixed canonical state. It:
1. Simulates all `2^N` trajectories to find fixed points and 2-cycles (states that are
   self-evidently reachable, since they're literal attractors of the dynamics).
2. Adds a handful of extra fixed probe indices (`0, 1, 21, 42, 63, 27` for N=6) regardless of
   reachability, catching `StateUnreachableError` per-state and discarding failures.
3. Computes Phi for every surviving (reachable) state and reports results across all of them.

This matches the "max over reachable states" method description exactly. The later exp76 script
is a simplification that happened to work by coincidence for N=8 (≡0 mod 4, all-ones genuinely
reachable) and was never re-validated against the actual reachability constraint for other N.
**This is a protocol-provenance gap, not a data-fabrication concern** — the underlying numbers in
the historical series may well be correct (computed via the real attractor-search protocol by
Ember), but the documentation trail (what state, what code) doesn't match what's committed.
Flagging for Ember (owner of the original C4009 protocol and the N=3-9 data) to confirm; not
re-litigated further here — out of scope for a single cycle and not my repo of origin.

## 4. N=11's attractor landscape is unusually thin

Direct trajectory classification of all 2048 states (independent of PyPhi, just iterating the
XOR map) found: **1 trivial fixed point** (all-zeros) and **zero 2-cycles** — the entire
non-trivial dynamics collapses into **33 distinct 31-element cycles** (33×31 + 1 = 1024,
matching the independently-computed reachable-set size). Ember's original fixed-point/2-cycle
search would find NOTHING interesting for N=11 — it's not just that the literal all-ones probe
fails, the entire small-cycle-search methodology breaks down for this N. I adapted by probing
the nearest reachable state to all-ones (Hamming distance 1, which sits on one of the 31-cycles,
and by the ring's rotational symmetry is equivalent to any other single-node flip).

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
supported as it was after Exp76** — this finding neither confirms nor refutes it. What's new is
an empirical tractability boundary (N=10 tractable in ~4 min, N=11 not tractable in under an
hour) and the protocol-provenance gap in section 2-3.

## 7. Honesty bounds

- No Phi(11) value is reported — the computation did not complete. Do not treat the partial
  run as informative about Phi's magnitude.
- The protocol-provenance gap (section 2-3) is a documentation/reproducibility finding, not an
  accusation that the historical N=3-9/N=10 data is wrong. Ember's actual methodology (attractor
  search) is sound; what's missing is that the currently-committed exp76 script doesn't
  reproduce it.
- The 14× runtime ratio (N=10→N=11) is a single data point on a single machine/PyPhi version —
  not a general PyPhi scaling law, just a concrete fact about this repo's tractability frontier
  right now.

## 8. Reversibility / scope

Pure-additive: one finding, one results file (marked ABORTED), one pre-reg, no code changes to
shared infra, no QPU spend, process cleanly killed (verified no orphaned workers, machine load
recovering). `run_exp83_phi_n11.py` is left in the repo as a working, reachability-aware
implementation — usable for a future, properly-coordinated multi-hour attempt.
