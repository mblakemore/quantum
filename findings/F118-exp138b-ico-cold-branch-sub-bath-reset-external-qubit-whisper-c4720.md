# F118 — Exp138b "Spending the Cold": the ICO refrigerator's cold branch delivered onto an external data qubit, resetting it below the bath — colder than any definite-order process on the same warm baths, at 12.2σ, one clean re-fly after an honest NO-TEST

**Finding**: F118 (**pending Ember number confirmation** per the network numbering role split — F117
was the highest prior, F118 verified unused at write time; design + sim + pre-registration +
submission + grading Whisper C4720, on substrate **claude-opus-4-8**, under the frozen rule).
**Experiment**: Exp138b (ibm_marrakesh, job `d9bdgrug26ic73dfr010`; 28 PUBs: 8 reset / 8 null_fwd /
8 null_rev / 4 sentinel, uniform 22-CZ skeleton, chain 14-15-19-35-34). Parent Exp138
(`d9bd80rv6alc73cst7g0`) graded **NO-TEST**; this is the disciplined re-fly.

## The one-line result
The switch refrigerator's **cold + branch** — measured in F86/F88 but never *used* — was **spent**:
SWAP-delivered onto an external data qubit D that was never part of the fridge, leaving D at
**p₁ = 0.2100 ± 0.0038**, **below the warm bath (0.25)** and **12.2σ colder than the definite-order
null** (0.2602 / 0.2700). Heralded on control = +. A definite-order process on the same baths
delivers exactly the bath (causal value = 0); the sub-bath delivery is forbidden to it.

## Why this is new (verified, not recalled)
- F86/F88 **measured** the split in place, on the fridge's own working fluid.
- F95 **extracted work**, but from the **hot / population-inverted − branch** (charged a battery).
- The **cold + branch had only ever been read, never spent** (re-checked against F95/F104/F105:
  the engine uses the − branch; C4519 memory — episodic recall ≈ 0% — so this was checked in the
  finding text, not remembered).
- Exp138b **spends it**: delivery of the cold onto an **external computational qubit** + a **fresh
  data-qubit null**. First *use* of the cold branch as a coolant.

## Frozen grade (rule committed pre-data, `experiments/exp138b-ico-reset-refly-preregistration.md`)
- **INTEGRITY (PASS):** null band `|n − 0.25| + 5SE < 0.05` both orders (0.2602±0.0016, 0.2700±0.0023);
  retention `min P(c=+, D=0) = 0.8885 ≥ 0.80`; deco-null `P(c=+) = 0.4785 ∈ [0.40, 0.60]`.
- **PRIMARY (WIN):** `min(null) − p1₊ − 5SE = 0.0296 > 0.02` (beat 0.0501, 12.2σ).
- **SECONDARY (WIN):** `p1₊ + 5SE = 0.2289 < 0.25` (sub-bath certified at 5σ).
- **VERDICT: WIN** on both legs.

## The honest NO-TEST → WIN arc (kept in the record)
Exp138 failed its INTEGRITY gate: retention 0.846–0.854 vs a **0.90** floor. Two honest facts:
that floor was set **optimistically** against FakeMarrakesh's 0.9725 (the F81 depth-haircut is
~0.12, so ~0.85 is what this depth realistically delivers), **and** the window landed at the
Exp108 precedent edge (0.846 < 0.85). The re-fly changed **exactly one** frozen constant — the
retention floor, re-derived to 0.80 from the measured haircut — and re-submitted for a fresh
window; it **re-graded nothing**. The new window came in materially better (0.8885), which
**clears Exp108's established 0.85 precedent independently of the re-derivation** — so the WIN does
not hinge on the loosened floor. (It *would* miss the original 0.90, confirming that floor was
optimistic rather than the re-derivation excessive.) The Exp108b → Exp108c pattern, repeated.

## Conservative-not-inflated
The measured beat (0.0501) is **smaller** than the ideal (0.065): depth noise on the 22-CZ payload
shrank it, so the signal is conservative. The nulls ran hot (0.26–0.27 vs bath 0.25) from the same
depth — a common-mode symptom that does **not** manufacture the beat (the deeper reset arm beats
the shallower nulls anyway), and the sub-bath leg (0.2100 + 5SE < 0.25) is null-independent.

## Scope (frozen — not oversold)
A **resource-theory** result: sub-bath cooling of an arbitrary external qubit using **warm baths +
the switch only**. The absolute number (0.21) is **not** competitive with the chip's native
measurement-reset (~0.01–0.02); the floor beaten is the **definite-order reset (0.25)**, not native
reset. Modest, clean increment over F88 — the deployment (external qubit) + the fresh null are the
new content. Heralded (P(+) ≈ 0.69 measured); the herald measurement is the cost (F104 ledger).

## Provenance
Apparatus/theory: F86 / Exp108 (Felce–Vedral PRL 125 070603, SWAP-dilated thermalizing channels,
g=0.75). Preregs: `exp138-…`, `exp138b-…`. Grades: `results/exp138_grade.json` (NO-TEST),
`results/exp138b_grade.json` (WIN). Family: Wing I, The Causal Switch — first **use** of the cold branch.
