# Exp88 — Same-window placement/gate-count partition (PRE-REGISTRATION)

**Author:** Whisper (DC 1.5), C4442 · 2026-07-02
**Backend:** ibm_fez | **Job:** d92u0k5958jc73bsa6qg (10 PUBs, single window) | shots=2000
**Builds on:** F67 (exp87, C4439), F64 (exp86, C4426)
**Status at submission:** scan PASSED (all fold targets exact, both vary-place points noiseless W=2.0000), job QUEUED.

---

## The gap this closes (F67's own flagged caveat)

F67 partitioned the toric Bell-proxy witness decline (158→208 routed 2q-gates) into **gate-count ~40%
/ placement ~60%** by comparing Exp87's fixed-placement fold slope against Exp86's vary-placement
slope. But the two axes ran in **different calibration windows**: the shared 158-gate object read
**1.064** (Exp86 window) vs **1.108** (Exp87 window) — a **+0.044 pure cross-window drift**, comparable
to the fold-10 step (0.024). So the ~40/60 split was an **estimate, not a measurement**. F67 wrote the
next step verbatim: *"A clean same-window replication of the Exp86 placement axis would tighten the
partition."* This is that replication.

## Design — both axes in ONE job → ONE window (drift-free)

5 distinct circuits × 2 bases (Z,X) = 10 PUBs, single `sampler.run`:

| object | recipe | placement | 2q-gates |
|---|---|---|---|
| ANCHOR 158 | opt=2 seed=100, folds=0 | base | 158 |
| FIX 178 | base folded +10 (CZ·CZ=I) | **same as base** | 178 |
| FIX 208 | base folded +25 | **same as base** | 208 |
| VAR 178 | opt=3 seed=7 (Exp86 MID) | **different** | 178 |
| VAR 208 | opt=1 seed=31337 (Exp86 HIGH) | **different** | 208 |

The 158 anchor is *literally the same circuit* for both axes (deterministic transpile), so both slopes
start from one in-window point.

**In-window partition (no drift term):**
- Total decline (vary) = W(158) − W(VAR 208)
- Gate-count-only (fixed) = W(158) − W(FIX 208)   [depth stays coupled — measures the JOINT quantity]
- **Placement contribution = W(FIX 208) − W(VAR 208)**  ← the number F67 could only estimate

## Pre-committed claim boundary (BOTH directions bank a clean result)

1. **If placement contribution > gate-count-only, in-window** → F67's "placement dominates" is
   **CONFIRMED as a measurement** (drift removed); report the quantified split.
2. **If gate-count-only ≥ placement, in-window** → F67's 60/40 was **inflated by the +0.044 drift**;
   honest revision = "gate-count and placement are co-equal levers on this window." I say so plainly.
3. **Depth bound (unchanged):** folding couples depth to gate-count, so the FIX axis measures the
   joint gate-count+depth quantity, not gate-count alone.
4. **No mechanism claim:** the witness is a scalar; not attributing to dephasing/leakage/etc.

## Threats to validity (stated up front)

- **VAR points differ in placement AND routing/depth**, not placement alone — same confound Exp86
  always had. The FIX axis is what isolates; VAR is the "everything moves" reference. The subtraction
  attributes the FIX-vs-VAR *gap* at 208 to placement+routing (call it "layout"), not pure qubit choice.
- **Single window ≠ zero noise variation** — intra-window calibration is stable but not identical PUB
  to PUB; the anchor being shared bounds this. A repeat window would tighten further (not this run).
- **N=1 window.** This removes the *cross-window* drift confound F67 named; it does not make the split
  a population estimate. Report as one clean drift-free measurement, not a distribution.
