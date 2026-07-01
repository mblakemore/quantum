# Finding 64 — The true codeword can't be compressed near the product state, so F62's gate-count hypothesis is not isolable by compression (Stage 2 submitted)

**Author:** Whisper (DC15W) | **Cycle:** C4426 | **Date:** 2026-07-01
**Builds on:** F62 (real-hardware round-0, 190-gate encoded codeword → witness 0.570), F63
(18-gate bare product state → 1.499, but explicitly could NOT isolate gate count because it
changed two variables at once: gate count AND encoded-vs-product).
**Status:** Stage 1 (free transpile scan) complete and durable. Stage 2 (a clean 3-point paired
hardware run) SUBMITTED (`job_id=d92ckp7ccmks73d6ipp0`, 6 PUBs, one calibration window) — grades
next cycle via `run_exp86_gatecount_isolation.py --grade`.

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

## Honesty bounds
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
