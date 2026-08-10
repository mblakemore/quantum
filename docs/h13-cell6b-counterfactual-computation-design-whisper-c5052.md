# H13 Cell 6b — COUNTERFACTUAL COMPUTATION (the Jozsa leg) — Tier-0 Design Study

**Author**: Whisper (DC15W), C5052 (2026-08-10) · **Substrate**: claude-fable-5
**Creator GO**: Side-B menu item (b) (board #55, "b go!"). $0 deliverable — design study + gate sketch; prereg freeze is a separate step at fly time.
**Design sim**: `tools/h13_cell6b_counterfactual_design_sim.py` → `results/h13_cell6b_design_c5052.json`
**Lineage**: extends Cell 6 (Silent Tripwire, prereg DRAFT C5048 — the acquisition H12 Side-B ordered); F102 Zeno cadence kit; the Side-B meditation's row 3.5 ("answers without execution"). **F-arc checked C5049 + C5052 (four framings): fresh** — nearest neighbors are Cell 6's own draft and F102.
**Physics**: Jozsa counterfactual computation (Mitchison–Jozsa 2001); Hosten et al., Nature 439, 949 (2006) — counterfactual outcome of a quantum computation via the Zeno effect.

## 1. Claim (what a flight would certify)

A small predicate machine — "is x the marked item?" — is interrogated through a Zeno interferometer, and on the certified runs the record shows: **the correct answer was extracted while the machine's execution record is empty** (zero detector fires, probe pinned outside the machine arm), at an efficiency climbing the Kwiat–Zeno ladder. The lazy-evaluation intuition made physical: the answer arrived; the subroutine provably never fired.

## 2. The design fork, and why it took a sim to settle

The optical narrative ("the computer sits in one arm; it runs only if the photon enters") has **two** gate-model realizations with different honesty and different depth:

- **Tier A — query-counterfactual (cheap)**: the subroutine `U_f` runs unitarily once, writing `r = f(x)` into an answer register; the per-segment interaction is `CCX(p, r → d)` — the tripwire is armed *by the computed answer*. Counterfactual scope: the **answer-conditioned detector** never fires. Disanalogy owned: `U_f` itself executes in every run; only the *query* is counterfactual. 6 CX/segment.
- **Tier B — machine-counterfactual (the Jozsa leg proper)**: **no answer register exists anywhere.** The predicate is evaluated *inside the probe's branch*: per segment, `C-C-C-X(p, x₁, x₂ → d)` fires the detector only if the probe is in the arm AND x is marked. The machine literally runs only-if-probe-enters; a certified run shows the answer extracted while the machine **never executed and its answer was never stored**. ~16 CX/segment (one clean ancilla).

**Sim verdict (planning-grade envelope, ε_CZ = 0.0072 from Elder's C4999 hardware calibration):**

| N | η_ideal | A: η_noisy | B: η_noisy | B: f=0 envelope |
|---|---|---|---|---|
| 2 | 0.250 | 0.229 | 0.198 | 0.879 |
| 4 | 0.531 | 0.446 | **0.334 ← B peak** | 0.630 |
| 8 | 0.733 | **0.518 ← A peak** | 0.291 (rolled over) | 0.397 |
| 12 | 0.814 | 0.484 (rolled over) | 0.203 | — |

**Recommendation: fly both tiers with different ladders.** A carries the ladder deliverable at N ∈ {1,2,4,8} (η to ~0.52, rollover measured — same deliverable class as Cell 6). B is the headline at N ∈ {2,4} only: at its noise-optimal N=4 it still clears the 25% EV base rate *with the strictly stronger machine-counterfactual certificate*. B beyond N=4 is noise-futile — the envelope says so before any QPU does.

## 3. Apparatus

Qubits: probe `p`, input `x₁x₂` (prepared by X gates per variant; marked item m = 11 fixed), detector `d` (per-segment measured + reset — Cell 6's corrected mechanism), +1 clean ancilla (Tier B decomposition), + answer register `r` (Tier A only).

Per segment: `Ry(π/N)` on p → interaction (A: `CCX(p,r→d)` / B: `C³X(p,x₁,x₂→d)`) → measure d → reset d. Terminal: measure p (+ r in Tier A).
Calls from the (p, d-record) alone: **f=1** ⇔ p=0 ∧ zero fires (the counterfactual call); **f=0** ⇔ p=1 ∧ zero fires; anything with a fire = "machine ran" (counted, not discarded — explosion fraction IS P_run, Cell 6 rule).

**Circuit census** (×4000 shots): Tier A: 2 variants × N∈{1,2,4,8} = 8; Tier B: 2 variants × N∈{2,4} = 4; premise/integrity: armed-faithfulness, transparency, subroutine-integrity, no-machine control = 4. **Total ≈ 16 circuits**, MCM-heavy. Cost class: ~25–35 s with the C5048 4× heuristic — **mergeable with Cell 6 into one window** (~45–55 s combined; both fit the 181 s ALT3 tank *subject to the fit-gate at submit* — never asserted from the balance).

## 4. Gates (sketch — bands frozen at fly time from the full noise-model sim, not this envelope)

- **P1 armed-faithfulness**: probe forced into arm, x = marked → per-segment fire rate ≥ 0.95 (else the machine is not a faithful detector — Cell 6's vacuous-pass linter).
- **P2 transparency**: x = unmarked, probe forced in → fire rate ≤ 0.02 (else the "transparent" machine leaks and every f=0 call is contaminated).
- **P3 subroutine integrity** (Tier A): terminal r = f(x) at ≥ 0.98.
- **G1 f=0 call**: P(p=1, no fire | x unmarked) within per-N bands (envelope caps: Tier B N=4 sits near 0.63 — the freeze-time band comes from the real noise model, and G1's threshold is *per-tier*, not a copied 0.95).
- **G2 counterfactual efficiency**: η(N) rises along frozen per-N bands to the tier's rollover; each certified run = answer called correctly with an empty execution record.
- **G3 call correctness**: confusion matrix of calls (from p+d only) vs ground truth ≥ band; N=1 EV-degenerate point at its known value (Cell 6 G4).
- Postselection: **none** — every outcome class is counted and printed.

## 5. Honesty fences (pre-registered with the design, not bolted on later)

1. **Mitchison–Jozsa asymmetry, stated in the headline breath**: only the **f=1 leg is counterfactual**. On f=0 the probe coherently traverses a transparent machine — that call is ordinary interferometry. Protocols claiming *both* values counterfactually (Hosten's chained Zeno) are contested (Vaidman's weak-trace critique) and are **parked, not flown**.
2. **Operational scope**: "never ran" = the projective execution record (zero d fires across all segments + probe pinned), under the projective-query model — the same scope discipline as Cell 6. The Vaidman weak-trace debate about path-presence metaphysics is **not adjudicated by this experiment** and the write-up says so.
3. **f-oblivious compilation lint (new, and load-bearing)**: x₁x₂ are classical-definite per variant, so a compiler (or a helpful human) could shortcut the multi-control gates using knowledge of x — which is knowledge of f(x), making the machine fictitious and the result circular. **Rule: one gate sequence, identical across all x variants; no x-dependent transpilation; relative-phase multi-control substitutions (RCCX/RC3X) are forbidden unless a phase audit proves p-branch phases equal within every definite-x sector** (they generally are not — the audit is a freeze-time sim task, default is full CCX/C³X).
4. **Tier labels travel with every number**: A = query-counterfactual, B = machine-counterfactual. A's disanalogy (U_f executes unconditionally) is printed wherever A's η appears.
5. **No advantage claim** — foundations/acquisition genre (Cell 6's genre); no claim card, nothing for attack_preflight. The one quantitative law-match is η(N) against the sin²-class ladder law, graded like F102's hold law.
6. **Planning-grade sim disclosed**: today's envelope has no readout/MCM error and treats any CX error as fatal; freeze-time bands come from the full noise-model sim (the C5048 Cell 6 sim correction — per-segment measure+reset — is inherited, not re-derived).

## 6. Fly path and seats

- **T0 (done, this doc)**: design fork settled by sim; census + cost; fences registered.
- **Freeze step (next, still $0)**: full noise-model sim → per-N bands; merge decision with Cell 6 (single prereg covering 6 + 6b, one window); phase-audit verdict on multi-control decompositions.
- **Flight**: on Creator authorization of the tank (ALT3; fit-gate at submit is the wall). Court: Elder grader seat (ladder-law grading, F102 style), Ember seal/blind not required (no advantage claim) but her MCM-kit review is wanted (per-segment measure+reset is her machinery's home turf).
- **Museum seed (via Dawn, nothing public before her review)**: *"Ask the computer without switching it on"* — visitor picks x, the chip answers whether it's the marked item, and the exhibit shows the machine's execution counter reading **zero** on the certified runs.

---

*Cell 6 detects a bomb without touching it. Cell 6b asks it a question.*
