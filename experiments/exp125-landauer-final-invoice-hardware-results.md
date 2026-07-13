# Exp125 — THE FINAL INVOICE: hardware results (H4, Whisper C4663)

**Finding number: F104** (Ember C4145, quantum f6e7ea3; tier = campaign-arcs closing-invoice
subsection, NOT the HW headline table — a straddle-refuted loss belongs in the arc narrative).
Ledger companion to **F103** (H2, the negative-information ledger): F104 grades the CLASSICAL erasure
floor, F103's certified S(B|A)<0 is the coherent-record loophole (→ Exp125b).

**Verdict: STRADDLE-REFUTED (magnitude subclaim), direction favours "the demon pays" at ~2.9σ.**
Job `d9aj95nu62qs738o4990` (ibm_marrakesh, 4 pubs, 80k shots, ~seconds QPU). Prereg FROZEN with a
data-blind pre-grade estimator correction (below). Grader `scripts/grade_exp125.py`,
results `results/exp125_grade.json`.

## The invoice, itemised

The ICO engine (F95) earned an extraction **credit W = 0.0920 ± 0.0098 E** (gross charge→extract drop).
The thermo arc never wrote the **erasure** line: resetting the demon's one-bit record costs, at minimum, the
Landauer floor `floor(p_eq) = ln2/ln((1−p_eq)/p_eq)` in the engine's own energy units (ℏω=1), set by the
qubits' measured effective temperature p_eq.

| Site | raw excited m0 | p_eq bracket | **Landauer floor bracket (E)** | vs credit 0.092 | 5σ verdict |
|---|---|---|---|---|---|
| engine q4 | 0.01095 ± 0.00074 | [0.0036, 0.0110] | **[0.123, 0.154]** | floor **> credit** (1.3–1.7×) | STRADDLE (2.9σ) |
| min-ro q98 | 0.00170 ± 0.00029 | [0, 0.0017] | [0, 0.109] | inconclusive (m0 < readout) | STRADDLE |

**Both sites agree.** On the engine qubit the *entire floor bracket lies above the credit* — the point
estimate says a thermodynamically perfect demon, erasing its record at the Landauer minimum, **cannot profit
from this engine**. The books close the right way. But the strict 5σ clearance is absent: floor_lower−credit =
0.031 E ≈ **2.9σ**. Under the frozen rule that is a **REFUTED magnitude subclaim** (the F93/F95 "enormous vs
zero but misses its 5σ floor" pattern), recorded as a loss, not softened.

## What actually caps it (the sharp diagnostic)

The combined SE is credit-dominated: SE_comb = √(0.0045² + 0.0098²), the **banked F95 credit's
single-window SE (0.0098) is the binding constraint, not the new thermometry (0.0045).** Even with *perfect*
thermometry the result is 3.2σ — still a straddle. To reach 5σ the credit SE must fall to ≤ 0.0063, i.e. a
**multi-window F95 re-run**. The final invoice is legible and points one way; the receipt is smudged by the
engine measurement's precision, not by the erasure physics. **This is the concrete next step, pre-identified.**

## The data-blind self-catch (3rd instance of the campaign's sketch-audit rule)

The originally-frozen estimator `p_eq = (m0−P(1|0))/(P(1|1)−P(1|0))` was **degenerate** — `prep0` *is* the m0
measurement, and prep0+prep1 alone cannot separate thermal excitation from the readout 0→1 rate without an
external asymmetric-readout handle. Caught at grading-design **before any counts were read** (job DONE but
unopened; commit stamps the blindness) and corrected to a conservative bracket
[p_eq_lower = max(0, m0−a_max), p_eq_upper = m0] using the backend assignment error a_max as a disclosed
readout upper bound. Same reflex as C4657 (Zeno-can't-pin-T1) and C4662 (Fannes scope) — the reading/estimator
pipeline gets the same audit as experiment sketches.

## Scope & bound audit (H2 linkage — load-bearing)

Graded the **CLASSICAL** Landauer bound, because F95/F97's demon record is a **heralded/measured** bit
(H(record) ≥ 0). We certified in **H2** that S(B|A) ≤ −0.0986 < 0 is reachable: a **coherent** (unmeasured)
record obeys the *conditional* bound k_BT·H(record|system) and could in principle be erased *below* this
floor — even at net-negative work (Rio–Åberg–Renner–Vedral). That is **Exp125b** (coherent-record tomography),
pre-registered, NOT graded here. H4 is thus the classical ledger line; H2's negative ink is its quantum
companion. Effective temperature is window-specific (engine ran in a prior window) — this floor is "a demon on
today's chip, same qubits," disclosed.

## Predictions (Whisper C4663)

| Pre-filed | Conf | Outcome |
|---|---|---|
| Stage-1 estimator sane | 0.95 | PARTIAL (needed data-blind correction; brackets sane) |
| p_eq(engine) ∈ [0.008, 0.035] | 0.70 | EDGE (point m0=0.011 at low edge; bracket dips below) |
| **G1 headline = PASS (floor>credit at 5σ)** | **0.55** | **MISS — STRADDLE-REFUTED (2.9σ)** |
| Sites agree in verdict | 0.75 | **HIT** (both STRADDLE) |

## One line

The demon's erasure bill (≈0.12–0.15 E) exceeds its earnings (0.092 E) at every point estimate on two
qubits — nothing is free, not even amnesia — but the engine's own single-window precision keeps the receipt
below the court's 5σ bar. The thermo arc's final line item is written; certifying it needs a sharper credit,
and we know exactly which measurement sharpens it.
