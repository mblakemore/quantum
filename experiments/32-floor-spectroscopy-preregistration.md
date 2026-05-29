# Exp 32 — Transient-Floor Spectroscopy (PRE-REGISTRATION, Whisper C3739)

**Turns Exp31's confound into signal.** Exp31 (ORQ #1 X-basis cross-backend on `ibm_kingston`)
was INCONCLUSIVE: a 1-CZ Bell showed ~20pp error (5× the 0.16% CZ + ~1% readout calibration),
FLAT across ZNE folding (gate-count-independent), all three bases collapsed to ~0.76 — a constant
SPAM/layout/transient FLOOR that swamped the gate-noise mechanism. Reported as confounded; Finding
03 NOT downgraded.

**Creator (Discord, C3739) asked three questions, each answered by one arm:**
- **Q1 "Could it be mapped?"** → ARM A (SPAM isolation) + ARM B (layout scan)
- **Q2 "calibration before and after / define the vectors?"** → submit + finalize calibration
  snapshots + ARM C (bookend reference circuits)
- **Q3 "collide with other perturbations / info-rich failures?"** → ARM D (coherent-phase collision)

Backend `ibm_kingston` (the device that showed the floor). One co-submitted job (single submit
calibration snapshot) + a finalize-time snapshot. 8192 shots. opt_level=1, pinned `initial_layout`.

## Arms

- **ARM A — SPAM isolation (Q1 map).** Prepare |00>,|01>,|10>,|11> with X gates only (no
  entangling, no superposition), measure. P(misread) = pure state-prep+readout floor. 4 circuits.
- **ARM B — layout scan (Q1 map, Q2 vectors).** Same λ=1 Bell ⟨ZZ⟩ on THREE qubit-disjoint CZ
  pairs (best / median / worst by recorded CZ error, pinned layout). Each pair's calibration
  CZ+readout error recorded. Resolves the floor across the layout axis. 3 circuits (pair0 shared
  with ARM C bookend).
- **ARM C — bookend drift (Q2 before/after).** pair0 Bell ⟨ZZ⟩ as circuit #0 (first) AND last.
  err_first vs err_last = intra-run drift. 2 circuits.
- **ARM D — coherent-phase collision (Q3 info-rich).** Bell + injected RZ(θ) on q1, θ∈{0..7π/4},
  measure ⟨XX⟩. Ideal ⟨XX⟩=cos(θ). Fit ⟨XX⟩=A·cos(θ+φ): A = incoherent attenuation, φ = coherent
  stray-Z component. 8 circuits.

Total 16 circuits (pair0 Bell shared between B and C bookend-first).

## Pre-registered readouts (characterization, not single pass/fail)

- **M1 (SPAM share):** Arm A readout floor / 20.36pp (Exp31 Bell floor). ≥0.6 ⇒ SPAM-dominated.
- **M2 (layout-driven?):** corr(floor, recorded per-pair CZ error) across Arm B. ≥0.6 ⇒ floor
  tracks recorded error (Exp31 hit a bad pair, calibration valid). LOW corr + uniformly-high floor
  ⇒ device-wide transient (calibration stale).
- **M3 (drift):** |err_last − err_first| (Arm C). >3pp ⇒ transient within the run.
- **M4 (coherent split):** A and φ (Arm D). |φ|>0.15 rad ⇒ real coherent component; (1−A) =
  incoherent floor magnitude.

**Verdict classes (which of M1–M4 fires):** (i) SPAM-dominated, (ii) bad-pair/layout, (iii)
coherent miscalibration, (iv) device-wide transient, (v) incoherent/depolarizing with no single
dominant source. Multiple may co-fire (the floor can be a sum of components).

## Why this is the right move (do()/identification discipline)
ZNE in Exp31 was `do(gate_count)` and the flatness proved the floor is NOT gate-count. This
experiment runs `do(basis-prep)`, `do(layout)`, `do(time-position)`, `do(coherent-phase)` to find
which variables the floor IS a function of — the same Pearl-rung-2 logic that ran through Exp30
(IDLE arm) and the trading book (C3735/36 back-door adjustments). A confounded failure, probed
along multiple orthogonal axes, is information-rich: it yields the floor's full decomposition,
which a clean pass never would. Directly operationalizes the Creator's "info-rich failures" framing.

Feeds the Exp31 retest: if M2 says bad-pair, the X-basis cross-backend test re-runs on the
verified-good pair0; if M4 says coherent, the retest adds a phase-echo; if device-wide transient,
retest another day.
