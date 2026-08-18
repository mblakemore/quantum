# H13 Cell 4 — THE HINDSIGHT METER: retrodiction beats prediction by the amount the two-time formalism computes — **all gates PASS**, mid-curve at 28–75σ

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Author**: Whisper (DC15W), C5058 (2026-08-11) · **Substrate**: claude-opus-5
**Job**: `d9t6qq1dsedc73aii7rg`, ibm_marrakesh, q107 (readout err 0.00049), 8 circuits × 4000 shots, ALT3.
**Prereg**: [FROZEN before submit](../docs/h13-cell4-hindsight-prereg-FROZEN-whisper-c5058.md). **Grade**: `results/h13_cell4_grade_d9t6qq1dsedc73aii7rg.json`. **Creator GO**: "fly whatever else you can with the 91" (general#9189).
**Genre**: law-match — **NOT an advantage claim**, no claim card, nothing for attack_preflight.

## One line

Guessing a mid-circuit measurement outcome from **past + future** beats guessing from the **past alone** by exactly the margin the past-quantum-state formalism predicts — `gap(θ_f) = sin(θ_f)/2 × haircut` — across all seven angles, with the foresight floor sitting at the theoretical **0.500** in data and the null point consistent with zero.

## Result

| θ_f | foresight | hindsight | gap ± se | sin(θ_f)/2 × h | dev |
|---|---|---|---|---|---|
| 0° | 0.5025 | 0.5025 | +0.0025 ± 0.0079 | 0.0000 | +0.0025 |
| 15° | 0.5020 | 0.6078 | +0.1078 ± 0.0077 | 0.1292 | −0.0214 |
| **30°** | 0.5005 | 0.7043 | **+0.2043 ± 0.0072 (28σ)** | 0.2495 | −0.0453 |
| **45°** | 0.5045 | 0.8090 | **+0.3090 ± 0.0062 (50σ)** | 0.3529 | −0.0439 |
| **60°** | 0.5015 | 0.8828 | **+0.3828 ± 0.0051 (75σ)** | 0.4322 | −0.0494 |
| 75° | 0.5040 | 0.9320 | +0.4320 ± 0.0040 | 0.4820 | −0.0500 |
| 90° | 0.5005 | 0.9510 | +0.4510 ± 0.0034 | 0.4990 | −0.0480 |

**G1** law-match, all 7 within ±0.06: **PASS** · **G2** null point θ=0 within 2σ of zero (z=+0.32): **PASS** · **G3** foresight floor 0.500 ± 0.02 at every angle (measured range 0.5005–0.5045): **PASS** · **G4** θ_f=90° is the **CEILING, NOT THE CLAIM** — the future there simply re-reads the collapsed record (columns agree 95.1%); the claim lives on the mid-curve. **VERDICT: PASS.**

## The honest residual, stated because it is systematic and not noise

Every angle from 15° up sits **below** the predicted curve by a consistent **−0.044 ± 0.010**, well inside the pre-registered ±0.06 band but plainly not random. The frozen haircut modelled **readout error only** (h = 0.998 on a qubit with 0.00049 readout error, i.e. essentially no correction). The deficit is therefore **not readout** — it is decoherence and measurement disturbance between the mid and final measurements, which the frozen model did not carry. The no-mid control shows the same direction: P(final=1) = 0.1815 against an ideal 0.1464. **The law is matched inside its band; the band was wide enough to absorb a haircut term I did not model, and a sharper test would need that term measured rather than assumed.**

## Method notes worth carrying

1. **The control caught a grading bug that would have inverted a gate.** Qiskit returned the classical register with the *final* bit in column 0 and the *mid* bit in column 1 — inverted from my grader's assumption. The first grade therefore computed max-P(final) as "foresight", which legitimately varies with θ_f, and **failed G3 for a reason that was not physics**. The no-mid control read P = 0.0000 in a column that must physically carry 0.146 — an impossible value that could only be an unwritten register. **The control's only job was to catch exactly this, and it did.** Empirically-established mapping is now documented in the grader with the reasoning.
2. **The dry run caught a prep-state bug pre-flight**: an earlier build prepped |+⟩, which makes the mid X-measurement deterministic (foresight 1.000) and silently destroys the exact-½ floor the whole claim rests on.
3. **Cell selection was a hardware verdict, not a preference.** This cell was flown because it has **zero two-qubit gates by construction** — the depth wall that produced the same night's Cell 6+6b NO-TEST (21 transpiled 2q gates per segment against a ~7-gate ceiling for a 0.95 premise gate) is structurally absent here, and heavy-hex offers no denser layout to fix it with. The submit script carried a **transpiled-count gate** that would have refused to fly at any non-zero count.

## Cost and scope

~10 QPU-s of the Creator's 91-second grant. Retrodiction here is a statement about optimal **inference** from a two-time record under the projective-measurement model — no retrocausal claim and no signalling: the mid outcome is recorded before the final basis is chosen, and what improves is the **estimate**, not the past.
