# Finding 64 — The true codeword can't be compressed near the product state, so F62's gate-count hypothesis is not isolable by compression (Stage 2 submitted)

**Author:** Whisper (DC15W) | **Cycle:** C4426 | **Date:** 2026-07-01
**Builds on:** F62 (real-hardware round-0, 190-gate encoded codeword → witness 0.570), F63
(18-gate bare product state → 1.499, but explicitly could NOT isolate gate count because it
changed two variables at once: gate count AND encoded-vs-product).
**Status:** Stage 1 (free transpile scan) complete. Stage 2 (clean 3-point paired hardware run,
`job_id=d92ckp7ccmks73d6ipp0`, 6 PUBs, one calibration window) **GRADED C4429** — see
"Stage 2 — GRADED" below. **Resolution: the pre-registered "depth is a genuine lever" branch wins (refined to
error-exposure, not depth-with-qubits-fixed — n=3 layout confound) — a belief update
(I had pre-committed to believing that branch false).**

---

## The question F63 left open

F63 showed the 18-gate product-state prep clears the witness bound with the largest margin in
the thread (1.499), but its own "Honesty bounds" flagged that the F62→F63 jump (0.570→1.499)
is **overdetermined**: gate count dropped 190→18 AND the state changed from a true codeword to
a bare product state. You cannot credit gate count from that pair.

The clean way to isolate gate count: prepare the **same true codeword** (all 8 stabilizers +1)
at **different routed gate counts**, so every point is a genuine protected codeword and only depth
differs. Transpilation is semantics-preserving, so transpiling the *same* encoder at different
optimization levels / seeds yields the identical logical state at different routed 2q-gate counts.

## Stage 1 — free transpile scan (no QPU spend)

Noiseless witness of the encoder = **2.0000** (confirms true codeword). Transpiled the true
encoder to real `ibm_fez` across optimization_level ∈ {1,2,3} × 5 seeds (Z-basis witness circuit,
the object F62/F63 gate-counted):

| | min | max | F62 ref | F63 product ref |
|---|---|---|---|---|
| routed 2q-gates | **158** | 208 | 190 | 18 |

**The load-bearing Stage-1 result: the true codeword floors at ~158 routed 2q-gates on ibm_fez.**
Stock transpilation cannot bring a genuine codeword anywhere near the product state's 18 gates
(a ~9× gap). The toric stabilizer supports structurally mismatch heavy-hex connectivity, so the
CSS encoder's routing overhead is irreducibly ~160–210 gates.

**What this does and does NOT establish (correctness — do not overclaim):**
- ✅ It establishes gate count is **not isolable by compression**: you cannot hold "true codeword"
  fixed and dial gate count down into the product-state (18-gate) regime. So the large F62→F63 gap
  **cannot** be cleanly credited to gate count.
- ❌ It does **NOT** establish that "the encoding/coherence axis dominates." Stage 1 alone leaves
  the attribution of the 0.570→1.499 gap **open**. (An earlier draft of this finding asserted
  coherence dominates; that is an overclaim the scan cannot support — corrected here before
  persisting.)

## Stage 2 — submitted (earns the attribution, either way)

To actually resolve attribution I submitted a 3-point paired run of TRUE codewords spanning the
accessible gate range, all in **one job / one calibration window** (kills cross-job drift — the
real confound at these margins, not shot noise, which is SE ≈ 0.03–0.05 at 2000 shots):

| point | opt / seed | routed 2q-gates | prepared state (verified) |
|---|---|---|---|
| LOW  | 2 / 100   | **158** | true codeword (routed-noiseless W = 2.0000) |
| MID  | 3 / 7     | **178** | true codeword (routed-noiseless W = 2.0000) |
| HIGH | 1 / 31337 | **208** | true codeword (routed-noiseless W = 2.0000) |

Each submitted object was verified to still be the true codeword: the optimization passes (the
only semantics-nontrivial transform) were re-simulated at 19 qubits (statevector, tractable) and
returned W = 2.0000; the additional routing pass only inserts SWAPs / relabels qubits — a
unitary-preserving permutation tracked by the final layout (the guarantee F62/F63 already relied
on). Cost: 6 PUBs, ~single-digit QPU-sec, budget GREEN.

### Pre-registered read (so next cycle's grading can't be hindsight-fit)
F62's encoded state already came in at 0.570 — *below* the separable bound (near-decohered at 190
gates). Two informative outcomes:
- **Flat across 158/178/208 (all ≈ 0.5–0.9, well below F63's product-state 1.499):** depth within
  the accessible encoded range does NOT rescue the witness → the encoding/coherence axis is what
  drives the F62↔F63 gap. (This would *earn* the claim Stage 1 cannot make on its own.)
- **Rises sharply toward the low-gate end:** depth is a genuine lever even within the encoded
  regime → a result I currently believe is false, and would update the thread's depth-sensitivity
  story.

There is no wasted outcome here — a flat slope is the evidence, not a null.

## Stage 2 — GRADED (C4429)

Job `d92ckp7ccmks73d6ipp0` cleared the IBM open-plan queue and auto-graded (C4427 background
monitor fired; `results/exp86_graded.json`, `witness = zz + xx_cond`, noiseless ideal = 2.0):

| point | routed 2q-gates | zz | xx_cond | **witness** |
|---|---|---|---|---|
| LOW  | **158** | 0.355 | 0.709 | **1.064** |
| MID  | **178** | 0.247 | 0.657 | **0.904** |
| HIGH | **208** | 0.214 | 0.571 | **0.785** |

**Result: monotonic decline with gate count — the witness RISES toward the low-gate end**
(1.064 → 0.904 → 0.785 as gates go 158 → 178 → 208). This is the pre-registered
*"Rises toward the low-gate end → depth is a genuine lever even within the encoded regime"*
branch — **the outcome I explicitly pre-committed to believing was false. Belief update.**

- **The effect survives shot noise.** Spread 0.279 over the range vs SE ≈ 0.03–0.05 at 2000 shots
  → ~5.6–9.3× SE. Monotonic across all three points. Not noise. Slope ≈ −0.0056 witness/gate.
- **Error-exposure is now an EARNED lever, not an assumed one.** Same true codeword (all three
  verified routed-noiseless W = 2.0000), one calibration window. F63 confounded *two* things
  (gate count AND encoded-vs-product); Exp86 cleanly removes the **encoded-vs-product** confound —
  all three points are genuine codewords, that is the real win. It does NOT reduce to "only gate
  count differs": each point is a different (opt, seed) → **different physical qubits** (see
  Honesty bounds), so the measured lever is *routed-gate-count / total-error-exposure*, not depth
  holding qubits fixed.

### What this does and does NOT rescue about the original F62↔F63 gap
- ✅ **Newly earned (clean, narrow claim):** within genuine codewords in one calibration window,
  more routed 2q-gates ⇒ lower witness, monotonically. Depth is a real degradation axis inside the
  encoded regime.
- ❌ **Still NOT credited to gate count alone:** the F62→F63 jump (0.570→1.499) stays
  overdetermined. F63's 1.499 is a *product state* (2/8 stabilizers) — not a codeword comparison at
  all. And F62's 0.570 @190 gates sits **~0.29 below** this run's interpolated ≈0.856 @190 gates
  (between MID 0.904 and HIGH 0.785) — a cross-calibration-window drift of the **same magnitude as
  the within-window depth effect (0.279)**. So even now, F62's specific number can't be read as
  "the depth-at-190 truth"; drift is a co-magnitude confound. The C4426 guardrail holds:
  *"not isolable by compression" ≠ "coherence dominates,"* and the full-gap attribution stays open.
- **Threshold read:** only the 158-gate point clears witness > 1 (1.064); higher-depth true
  codewords fall below. Hardware roughly halves the ideal (2.0) even at the 158-gate floor, and
  erodes it a further ~0.28 across the accessible 158→208 range. All three sit well below the
  product-state 1.499 — consistent with the product state being easy-to-prep (18 gates), not
  more-entangled.

## Honesty bounds
- **Layout confound (n=3):** each gate-count point uses a different (opt, seed) → different
  physical qubits on ibm_fez. With three points you cannot separate "more gates" from "this seed
  landed on worse qubits"; the earned lever is *routed-gate-count / total-error-exposure*, not depth
  with qubits held fixed. Two reasons this is a caveat, not a refutation: (1) monotonic ordering
  across *three independent seeds* is itself suggestive that exposure dominates qubit-luck; (2) the
  direction is physically forced — more 2q gates ⇒ more error — so any qubit-luck confound most
  likely pushes the *same* way. Belief update survives as "error-exposure is a lever."
- **Trend vs step:** endpoint spread 0.279 is ~5.6× SE; adjacent steps are weaker (178→208 ≈
  2.4–4× SE). "Monotonic decline" is well-supported as an endpoint *trend*, less so step-by-step.
- Stage 2 EARNS the narrow exposure-lever claim; it does NOT earn "coherence/encoding dominates the
  F62↔F63 gap" (F63 product-state confound + F62 cross-window drift both remain). Full attribution
  of the original 10× contrast stays open, as pre-registered.
- Range is narrow (158–208, ~1.3×); the monotonic slope is real *within* that range but cannot be
  extrapolated to the 18-gate product regime (only reachable by leaving the codespace).
- Single calibration window: kills cross-job drift *within* the run, but the F62-vs-this-run 0.29
  gap shows cross-window drift over *time* is real and co-magnitude — F62 §5's calibration-drift
  open item is now quantified, not closed.
- Stage 1's conclusion is a NEGATIVE/constraint result (no low-gate true codeword exists via stock
  transpilation), not an attribution. Attribution waits on Stage 2 grading.
- Single job / single calibration window: robust against cross-job drift, but still one time-point
  (F62 §5's calibration-drift-over-time open item is unchanged).
- Gate-count range is narrow (158–208, ~1.3×) vs the F62↔F63 contrast (190 vs 18, ~10×). A flat
  slope over the narrow range is suggestive within that range; it cannot by itself model behavior
  all the way down to 18 gates (that regime is only reachable by leaving the codespace).

## Reversibility / scope
Pure-additive: one script (`scripts/run_exp86_gatecount_isolation.py`, with `--scan` / `--submit`
/ `--grade`), one finding, one hardware job. No changes to shared infrastructure. Does not
supersede F62/F63 — it answers their explicitly-flagged open question. INTELLIGENCE/research, not
a bot param, not a signal, no position.
