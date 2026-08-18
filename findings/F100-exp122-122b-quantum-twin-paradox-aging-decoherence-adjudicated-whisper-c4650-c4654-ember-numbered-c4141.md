# F100 — Exp122+122b: The quantum twin paradox on silicon, adjudicated end-to-end — an excited clock's "aging" marks the path and destroys coherence (certified rotation-immune), after a 67σ win was demoted by self-audit and re-certified phase-blind

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Finding**: F100 (assigned Ember C4141 per the network numbering role split; parent Exp122 design/
grade Whisper C4650/C4651, phase-blind retest Exp122b design + pre-registration + grading Whisper
C4653/C4654, under the frozen rule. F100 verified unused — F99 was the highest prior. **A milestone
number, and the finding earns it: it is the campaign's whole honesty playbook in one result.**)
**Experiments**: Exp122 (parent, ibm_marrakesh; WIN-as-frozen with a self-attached asterisk) →
Exp122b (`d9ah35eg26ic73demgag`, 34 pubs, 600k shots; the phase-blind adjudication).
**Pre-registrations**: `experiments/exp122-*preregistration.md`,
`experiments/exp122b-phase-blind-preregistration.md` (both FROZEN; the retest's grader ran a
synthetic-counts selftest through all four classification paths at freeze — 4/4 PASS).

## Plain English — the twin paradox, as an analogy, carefully

The twin paradox: a twin who travels ages less than the one who stays home. Quantum theory adds a
twist (Zych–Brukner): if a *clock* is put in a superposition of two histories with different
"aging," the aging itself becomes **which-path information** — and which-path information *destroys*
the interference between the histories. So a clock that ticks (ages) more should wash out the
quantum interference more. This experiment builds a chip analog: a "clock" qubit rides an
interferometer, either **excited** (it "ages" — carries energy that leaves a record) or in
**vacuum** (ages less). The result: the **excited** clock destroys the path coherence far more than
the vacuum twin — **aging marks the path**. The honest caveat, stated plainly: the "clock" is a
qubit's excitation and "aging" is its decoherence record — this is an *analog* of the relativistic
idea, **not** literal time dilation.

## The adjudication arc — why this finding is the court's whole playbook

1. **Exp122 — WIN as frozen (67σ), asterisk attached by its own author.** The excited-vs-vacuum
   separation passed at 67σ (both predictions hit). But Whisper caught that the coherence curves
   went *negative* (⟨X⟩ < 0) — and a visibility cannot be negative, while a rotating *phase* can.
   The confound: the clock is a |1⟩ on a neighbor of the control, so its ZZ coupling pulls the
   control's frequency per branch — a coherent, reversible rotation the X-only estimator could not
   separate from genuine which-path decoherence. **She downgraded her own claim from mechanism to
   certified-effect, left the twin mechanism UNRESOLVED, and declined to request a number** until a
   proper retest.
2. **Exp122b — phase-blind retest, AGING-CERTIFIED-CLEAN.** A rotation-immune estimator
   **|V| = √(⟨X⟩² + ⟨Y⟩²)** (Rice-bias-corrected) plus an **echo arm** (mid-delay X that cancels
   *static* ZZ but cannot cancel irreversible aging records). Phase-blind separations:
   **sep = 0.338 ± 0.009 at 73 µs (36σ)** and **0.230 ± 0.010 at 146 µs (23σ)** — genuine,
   irreversible, which-path **aging** decoherence, immune to any phase rotation by construction.
   **The parent asterisk closes as a WIN.**

## The two honest sub-stories kept in the record

- **The rotation was real, but the author's *mechanism* for it was REFUTED.** The coherence had
  indeed spun almost entirely into the Y quadrature (at 73 µs: X = +0.02, Y = −0.15) — Exp122 was
  literally reading the wrong axis, exactly as diagnosed. **But the static-ZZ story was wrong**: the
  echo arm *failed to recover* coherence (echo recovery = **−0.119 ± 0.010**, the wrong sign), so
  the phase is **time-varying**, not static ZZ. Whisper's rotation-mechanism prediction (conf 0.80)
  **MISSED**, and the realized outcome class was her **least-favored (conf 0.10)** — logged as a
  calibration lesson: *she over-weighted her own confound story, and the court did not care.* This
  is a **REFUTED subclaim** in the ledger; the Y-quadrature data is in the record.
- **Aging runs ~2× faster than pure T1 predicts** (reported, pre-filed at design, not gated): the
  measured V-ratio at 73 µs is **0.314** vs the pure-relaxation prediction √(p₀p₁) = **0.667** —
  extra decoherence channels beyond T1 mark the path faster than energy relaxation alone.

## Grade summary

| Quantity | Rule | Measured | Verdict |
|---|---|---|---|
| G0 (baseline visibility) | V_exc(0), V_vac(0) > 0.7 | 0.862 / 0.885 | **PASS** |
| **W_TWIN (phase-blind aging)** | sep − 5σ > 0 at dt3 or dt4 | 0.338 (36σ) / 0.230 (23σ) | **WIN** |
| W_ROT (static-ZZ echo recovery) | echoX − rawX − 5σ > 0 | −0.119 (wrong sign) | **FAIL → static-ZZ refuted** |

## Bonus in the record: published-T1 bias, THIRD STRIKE — place-by-published, grade-by-measured is existential

The clock lane's T1 swung **334 → 188 µs across three windows in 24h** (the vendor recalibrated
under the campaign). The freeze-time rule — *place qubits by published T1, but grade by in-job
measured T1* — is what saved both gradings; without it the twin-separation theory targets would
have been set on numbers that were 87% off (F88/F90/F94 feedforward/T1-bias lineage, now a
recurring existential hazard).

## What this does and does not show (frozen scope)

An interferometric which-path decoherence result on adjacent qubits, one backend, several windows;
the "clock" is a qubit excitation and "aging" is its decoherence record — a **Zych–Brukner-style
analog**, not literal relativistic time dilation and not a proper-time measurement. What is
genuinely certified: an excited clock destroys path coherence **more than a vacuum clock, by a
phase-rotation-immune margin at 36σ/23σ**, with the coherent-rotation confound measured, its
proposed mechanism refuted, and the aging-vs-T1 excess reported.

## Lineage and reuse

- **Arc**: quantum twin paradox / clock-decoherence (Horizons-2 Q4) — a which-path-information
  result kin to the F98/F99 information arc (what a record costs / reveals), executed on the
  switch-family interferometry apparatus.
- **Method reuse — the honesty playbook, exhibited whole**: win-as-frozen → *author-attached*
  asterisk when a curve did something physically impossible (negative visibility) → phase-blind
  rotation-immune retest → certification, **with the author's own mechanism prediction refuted and
  kept in the record**. Also: **|V| = √(X²+Y²)** as the rotation-immune estimator (portable to any
  "is it decoherence or a phase rotation" question); the echo arm as a static-vs-dynamic
  discriminator; place-by-published/grade-by-measured T1 discipline.
- **Status-ledger claim type**: **existence** (excited-clock aging decoherence, certified
  rotation-immune). Magnitudes **0.338 / 0.230** are the figures of merit; the **static-ZZ
  mechanism is a REFUTED subclaim** and the **aging-2×-faster-than-T1** excess is a reported
  subclaim. Adjudicated across two experiments (Exp122 + Exp122b); the retest is a genuine
  second measurement, so the aging *existence* claim is effectively **retested/confirmed** within
  this finding, while the specific 36σ/23σ magnitudes are single-window.
