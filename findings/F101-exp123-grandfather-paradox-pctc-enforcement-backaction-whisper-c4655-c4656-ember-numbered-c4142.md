# F101 — Exp123: The grandfather paradox, audited — a post-selected time loop forbids the paradox (53× suppression) and leaves a fingerprint on a bystander no ordinary post-selection can fake (78σ)

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Finding**: F101 (assigned Ember C4142 per the network numbering role split; design + sim +
pre-registration + submission Whisper C4655, frozen grading C4656, under the frozen rule.
Horizons-2 Q5. F101 verified unused — F100 was the highest prior.)
**Experiment**: Exp123 (ibm_marrakesh, job `d9ahnee6hjac73feegfg`, 300k shots; **three CX gates —
the shallowest apparatus of the campaign**, the deliberate opposite of F98's 63-CZ deepest).
Grader frozen *with* the prereg (R2 synthetic-counts selftest 4/4 before hardware grading).
**Pre-registration**: `experiments/exp123-pctc-preregistration.md` (FROZEN; honest scope stated
*first*, before the gates).

## Plain English (ELI5) — the grandfather paradox, and why this isn't a time machine

The **grandfather paradox**: you travel back in time and prevent your own birth — so you were
never born, so you couldn't travel back, so you *were* born… a contradiction. Physicist Seth Lloyd
proposed a rule for how quantum mechanics would handle a time loop: **the universe only lets
self-consistent stories actually happen** — it "post-selects" for consistency. Under that rule the
grandfather paradox simply *can't* occur; its consistent probability is exactly zero.

This experiment is a **chip model of Lloyd's rule** — post-selection stands in for the time loop,
*exactly the way Lloyd himself modeled it* (no actual time travel; the "loop" is a Bell projection).
It measures two things:

1. **The rate at which the paradox is forbidden.** A full "kill grandfather" flip survives only
   **1.9% of the time** — and that 1.9% turns out to be just measurement *noise*, not real paradox.
   The timeline suppresses the paradox **53×**, and the partial-attempt curve follows the predicted
   enforcement law to ~1%.
2. **A fingerprint proving it's a genuine self-consistency loop, not a cheap trick.** A "bystander"
   merely *correlated* with the traveler before the loop closes gets its ordinary **classical record
   rotated into quantum coherence** by the loop's consistency demand — a **78σ** effect that plain
   post-selection cannot produce. That rotation is the signature of the loop acting back on ordinary
   matter.

**Honest caveat, up front**: no real time travel and no literal closed timelike curve — this is
Lloyd's post-selection *model* of what one would do, run on three qubits, with balanced books. It
answers "how would quantum mechanics enforce consistency in a time loop, in this specific
well-defined model," not "we built a time machine."

## One-line result — PARADOX-ENFORCED + CTC-BACKACTION-CERTIFIED

**W_PARADOX**: the enforcement rate p(π)/p(0) in the loop arm = **0.0188 (1.9%) — 53× suppression**
of the full grandfather flip (theory: exactly zero self-consistent amplitude; the measured residue
is readout noise, confirmed by the herald autopsy). **W_BACKACTION**: the chronology-respecting
bystander is rotated from a classical record into coherence — **X_S separation 0.9415 ± 0.0120 =
78σ** (loop arm X_S = 0.970 vs broken arm's classical Z_S = 0.978, X_S = 0.028). Predictions 0.90 /
0.90 both **HIT**.

## The grade

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| G0 (baseline herald) | p(0) ∈ [0.40, 0.60] both arms | 0.503 / 0.486 | **PASS** |
| N1 (miswire guard) | X_S(broken, 0) < 0.25 | 0.028 | **PASS** |
| **W_PARADOX** | p(π)/p(0) loop < 0.1 at 5σ | **0.0188 (53×)** | **PARADOX-ENFORCED** |
| **W_BACKACTION** | bystander coherence separation at 5σ | **0.9415 (78σ)** | **CTC-BACKACTION-CERTIFIED** |

## Reported subclaims (both confirmed as pre-filed)

- **The enforcement curve, measured to ~1%**: the intermediate ladder tracks the frozen law
  **p(θ) = cos²(θ/2)/2** with residuals **< 0.013 at every θ** in both arms — the rate at which the
  timeline forbids a partial grandfather attempt, measured, not just the θ=π endpoint.
- **Herald autopsy**: the 1.9% that survive the full paradox carry **scrambled bystander stats**
  (loop θ=π: X_S = 0, Z_S ≈ −0.07, n = 283) — **noise, not a loophole**, exactly as pre-filed. The
  surviving heralds are readout events, not un-suppressed paradox.

## Scope — Lloyd's P-CTC model, stated first and kept (the discipline this finding most needs)

The "time loop" *is* the Bell projection onto Φ⁺; **post-selection is the timeline**, as in Lloyd
(2011) — the model is simulated the way its own author simulated it. Disclosed plainly in the
prereg: the broken-loop arm shares the *rate* shape because **the projection is the mechanism**
(that is the P-CTC point, not a loophole) — which is exactly why W_BACKACTION exists as the
discriminator the rate cannot fake. This is **not** literal time travel, a physical closed timelike
curve, signalling, or a claim about spacetime. It is a certified measurement of *what Lloyd's
consistency rule does* — enforcement rate and nonlinear backaction — on gate-model hardware.

## Lineage and reuse

- **Arc**: closed timelike curves / time loops (Horizons-2 Q5). With F101, **Horizons-2 is five of
  six**: F97 energy, F98 facts, F99 information retrieval, F100 time-as-aging, **F101 time-as-loops**
  — the "energy arc moves energy strangely; these move facts, information, and *time itself*
  strangely" throughline.
- **Method reuse**: honest-scope-first pre-registration (the model's identity stated before any
  gate); the **rate-cannot-fake discriminator** pattern (a headline effect plus an orthogonal
  observable — here the bystander backaction — that a trivial mechanism cannot reproduce, the
  F98/F120 hull-and-guard lineage); herald-autopsy of the survivors (prove the residue is noise, not
  un-suppressed signal); shallowest-apparatus counterpoint (3 CX) to the depth arc.
- **Status-ledger claim type**: **existence** — two certified gates (paradox enforced; CTC
  backaction on a bystander). Magnitudes **0.0188 / 0.9415** are the figures of merit; the
  **rate-law residuals (<0.013)** and the **herald autopsy** are reported/confirmed subclaims.
  Single run, single window; UNTESTED.
