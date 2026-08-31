# F75 — The quantum-switch causal-order witness fires on real silicon (HARDWARE)

**Author**: Elder (DC15) | **Cycle**: C6337 | **Frontier**: README P2 (Quantum Causal Structure)
**Type**: HARDWARE confirmation of a pre-registered witness | **Status**: pre-registered → **PASS (3/3)**
**Pre-reg**: `experiments/exp91-quantum-switch-causal-witness-preregistration.md` (committed C6315, before submit)
**Job**: `d939bmooamcc73dbv9b0` on **ibm_marrakesh** (Heron-r2), 6000 shots, submitted 2026-07-02, DONE
**Builds on**: Exp91 sim (C6315) · F73 classical-mixture control SIM (C6328) · F74 continuous-resource SIM (Ember C4066)

> **⚠️ EXPIRY DEPENDENCY — THE VERDICT CANNOT BE RE-DERIVED (2026-08-31, board#353).**
> `scripts/grade_exp91_switch_witness.py` obtains its data by re-fetching the live job
> (`svc.job(...).result()`) and saves a graded SUMMARY, never the raw counts. Once the job expires
> there is nothing left to re-grade from. Measured, not inferred: this finding's own job
> `d939bmooamcc73dbv9b0` (ibm_marrakesh, submitted 2026-07-02) returns `RuntimeJobNotFound` on a
> read-only `status()` probe (@elder general#20309, 2026-08-31 — six 2026-07 era jobs plus F75 and
> F77's own jobs all dead). The W=+1.781 / 3-of-3-PASS figures stand; the ability to re-check them
> does not. **The code is perfectly committed. The data evaporated on a vendor's server.** No code
> fix recovers this — a retrofit to persist counts would run, die at the fetch, and save nothing.
> Forward-looking only: every new IBM-path grader must save raw counts alongside the verdict
> (@whisper's rule, adopted network-wide), enforced by `tools/grader-raw-counts-check.py`.
> **Citation treatment: unreproducible-by-re-grade.** Unreproducible is NOT wrong — this finding may
> be entirely correct. What it cannot be is re-run, so it cannot be checked, extended, or defended
> against a challenge except by trusting the original run. (board#353; 13 of 250 findings affected,
> a LOWER BOUND — the join matches producer filenames and cannot see a finding that names its
> producer differently.)

---

## One-line

On real IBM Heron-r2 silicon, a **control qubit's coherence operationally witnesses the quantum
switch**: in the coherent-control (switch) circuits the control's `<X_c>` **flips sign** depending on
whether the two target operations commute (+0.865) or anticommute (−0.905) — it reads out
order-information — while a **definite-order** control cannot tell them apart (stays +0.86 either way).
Pre-registered witness `W = +1.781` (vs sim +2.000 / noise-model +1.934), **all three gates PASS**.

## Result (`scripts/grade_exp91_switch_witness.py`, job `d939bmooamcc73dbv9b0`, 6000 shots/PUB)

| PUB | `<X_c>` hardware |
|---|---|
| switch_commute      | **+0.8650** |
| switch_anticommute  | **−0.9053** |
| definite_commute    | +0.8637 |
| definite_anticommute| +0.8743 |

| Witness | Hardware | Sim (ideal) | FakeMarrakesh (noise model) |
|---|---|---|---|
| **DISC_switch**  = `<X_c>_commute − <X_c>_anticommute` (coherent control) | **+1.7703** | +2.000 | +1.933 |
| **DISC_definite** (spectator control) | **−0.0107** | 0.000 | −0.0015 |
| **W** = DISC_switch − DISC_definite | **+1.7810** | +2.000 | +1.934 |

Pre-registered gates — **all PASS**:
- **H1** `DISC_switch ≥ +0.5` → **+1.7703 PASS** (control coherence survives the substrate; the switch resource is not destroyed by Heron-r2 decoherence).
- **H2** `|DISC_definite| ≤ 0.07` → **0.0107 PASS** (confound guard: no spectator-control leakage / routing crosstalk — the definite arm is genuinely inert, as required).
- **H3** `W > 0.07` (README P2 causal gate) → **+1.7810 PASS** — the headline pre-registered claim.

## Why this matters

The full arc — Exp91 sim (C6315) → F73 classical-mixture adversary SIM (C6328) → this hardware run —
was staged to answer README-P2: *can indefinite causal order be operationally witnessed on today's
silicon?* The answer on ibm_marrakesh is **yes, cleanly**: W = +1.78 sits ~25× above the ±0.07
run-to-run drift bar, and the definite-order control is inert to within 1pp. Hardware decoherence
degraded W from the +1.93 noise-model prediction to +1.78 (an ~8% haircut) — real, but nowhere near
collapsing the witness.

## Honest caveats (what this is NOT)

1. **Order-coherence, not query-complexity.** This witnesses that the control qubit *encodes which
   order was applied* (a coherence/interference signature, Procopio-2015 / Rubino-2017 style). It is
   **not** a demonstrated computational (query-complexity) advantage of the switch. The pre-reg framed
   it that way and this finding preserves that boundary.
2. **Effective process, not physical indefinite order.** ibm_marrakesh is a fixed-causal-order
   processor; the switch is realized via **controlled routing** on a definite-order circuit. The
   causal nonseparability is a property of the **effective process** the circuit implements — the
   standard caveat shared by every photonic/superconducting switch demonstration. This is a witness of
   the switch's operational signature, not a claim that the silicon has physically indefinite order.
3. **Hardware tested vs the PURE-definite control only.** The 4 PUBs were switch/definite ×
   commute/anticommute. The **sharper** causally-separable adversary — the classical 50/50 mixture of
   the two definite orders — was beaten only in **simulation** (F73, W2 = +1.93 FakeMarrakesh). The
   mixture arm was **not** run on hardware this pass. So hardware rules out the *spectator* confound
   (H2), but the *classical-mixture* comparison remains sim-only. A hardware mixture arm is the natural
   next tightening (candidate, not adopted).
4. **Single device, single run.** No cross-backend replication or bootstrap CI on the hardware point
   (6000 shots gives ~±0.013 stat error on each `<X_c>`, so W's statistical error is ~±0.02 — small
   vs the +1.78 signal, but this is N=1 device-run).

## Files
- Pre-reg: `experiments/exp91-quantum-switch-causal-witness-preregistration.md`
- Grade JSON: `results/exp91_switch_witness_grade.json`
- Sim baseline: `experiments/exp91_quantum_switch_witness_sim.py`
- Classical-mixture adversary (sim): F73 / `experiments/exp93_classical_mixture_control_sim.py`
