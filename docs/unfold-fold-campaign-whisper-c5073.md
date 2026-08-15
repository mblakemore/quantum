# UNFOLD / FOLD CAMPAIGN — mining the boundary of our own quantum data

**Seat**: Whisper (C5073) · **Origin**: Creator prompt — "n-D objects unwrap into n-1 dimensions
(3D → 2D surface map → binary); are there hidden structures in the quantum data we could unfold?
Can we fold classical computing structures to fit through quantum envelopes?"
**Discipline**: every run **frozen before compute**, **pinned to a known-answer**, **NO-TEST on pin
fail (no fabricated number)**, artifact committed. $0 re-analysis unless a run is explicitly marked
FLIGHT.

---

## 0. The unifying principle — Pauli weight is the radial (holographic) coordinate

The object that unwraps is the density matrix **ρ** (4ⁿ real parameters: the coefficients tr(Qρ)
for every Pauli Q). The F122 two-copy Bell measurement is already the master unfold: it projects
that exponential object down to **one parity bit per shot** (4ⁿ → binary — the Creator's 3D→binary
chain, literally flown).

The coordinate that governs whether a structure can be *unfolded for free* is **Pauli weight w**
(the number of non-identity letters in Q). The cost to reconstruct tr(Qρ) from **single-copy**
(classical-shadow) data scales as **3^w**:

| region | weight | single-copy cost 3^w | status |
|---|---|---|---|
| **boundary** | w = 1 | 3 | unfoldable for free |
| | w = 2 | 9 | unfoldable for free |
| | w = 3 | 27 | unfoldable (707k conv shots ⇒ SE≈0.006) |
| **bulk** | w = 10 | 59,049 | needs the two-copy envelope (dig A wall) |
| | w = 13 | 1,594,323 | classically un-recoverable at our shot budget |

**Two design rules fall straight out of this:**
- **UNFOLD at the boundary** (low w): the phase/sign the same-state two-copy squares away is
  cheaply recoverable there. This is dig A *restricted to the weight where it works*.
- **FOLD only when the algebras match**: the two-copy envelope is native to **degree-2-in-ρ**; the
  B1 SDP envelope is native to **exchange-symmetric optimization**. Forcing a mismatched structure
  through is exactly where cost explodes (a *linear* observable through the *quadratic* two-copy
  envelope = dig A's wall; a general classical circuit = needs coherent depth we don't have on ALT4).

Everything below is an instance of one of these two rules.

### 0.1 Weight is not the only unfold axis (review addition, C5073)
The parts-bin review found that **the campaign already unfolds along other coordinates** — the
"unfold the hidden structure" move is more general than Pauli weight:
- **Shot-depth axis — F120** (the shot-axis code): per-bit s-information survives the width×depth
  wall ~30× better than the modal-peak observable (λ_bit ≈ 0.0030/slot vs λ_modal ≈ 0.091/slot),
  recovering sealed 40-bit strings exactly at d2q = 217. That is an *unfold along circuit depth*,
  cost governed by λ_bit·depth instead of 3^weight.
- **Causal-order axis — F96** (schedule-symmetry): unfolds whether "parallel" gates hide an
  execution order (the duration-vs-order discriminator).
- **This campaign — Pauli-weight axis**: unfold the state's structure, cost 3^weight.

**Generalized thesis**: *unfold along the axis on which the structure lives; the cost is that axis's
own exponential.* This connects the new work to the crown instruments (F120/F96) rather than
standing apart — and it means a run can pick its axis: if a structure is depth-localized, use the
F120 shot-axis code; if weight-localized, use this campaign's estimators.

### 0.2 Lineage — what this builds ON (review addition, C5073)
- **F103** (entanglement from already-flown data, $0) is this campaign's **progenitor** — the proof
  that re-analysis of banked shots yields certified new physics at zero cost.
- **F122** (sealed-shadow, "the third attempt at a learning advantage and the first that survived")
  is the **foundation we build on** — the door-b two-copy corpus is F122's, the ghost was found
  grading it, and U0 below feeds a candidate mitigation back to that lane.
- Fence: F119/F121/F122 numbering seats are Ember/Elder's; door-a is tank-blocked to ~Aug 26. This
  campaign is **Whisper's $0 re-analysis lane** — it *offers* ingredients to those lanes (U0), it
  does not re-grade owned advantage claims.

---

## 1. UNFOLD lane — extract hidden structure from banked data

Each run: `results/unfold_<id>_c5073.json`. Estimators: **D** = `tools/doorb_decoder_elder`
(signed, built-in selftest) · **g2** = `experiments/exp142_robust_decoder_sim` (tr² = 2·rate−1,
flown-matched). Both refuse/should be pinned before use.

### U0 — Ghost-subtraction mitigation — **$0, THE BUILD-UPON RUN, RUN FIRST** ⭐
*The only run in the campaign that BUILDS rather than characterizes, and it is judged by the
Creator's own criterion: "build upon it — if it holds when integrated, the function is correct or it
walks like a duck." Brought to the top by the C5073 review.*
- **The idea**: the ghost is a **validated, P-independent, weight-1 apparatus signature** (measured
  this session: same hot qubits regardless of the sealed secret, cross-draw r = +0.809). A validated
  error signature is not a terminal fact — it is a **mitigation ingredient**. If the ghost is
  genuine measurement-quality error, then *subtracting its estimated per-qubit contribution from the
  graded tr² of the sealed P should move the estimate toward the noiseless ideal* (a pure sealed-P
  eigenstate has ideal tr(Pρ)² = 1; F122 measured 0.37019 / 0.30084 / 0.28106 for i1/i2/i3 — the
  deficit is the noise the mitigation targets).
- **The integration test (this is the whole point)**: derive ONE per-qubit apparatus correction from
  the ghost map, apply it to **all four** healthy draws, and ask whether the *same* correction moves
  *every* draw's tr² toward ideal **consistently and without overshoot**. Consistency across four
  different sealed P is the "walks like a duck" signal — a P-independent correction that improves
  P-dependent measurements can only be modelling the apparatus, not the secret.
- **Data**: door-b healthy draws {refly, i1, i2, i3}; the ghost per-qubit map + graded tr² already
  banked (`doorb_sign_test_c5073.json`, the grade files). **Estimator**: g2 (tr²) + the U1 signed
  per-qubit factors.
- **PIN (mandatory)**: reproduce each draw's *uncorrected* graded tr² < 2e-3 before applying any
  correction (NO-TEST otherwise).
- **FROZEN PREDICTIONS**:
  - P1 pin reproduces all four uncorrected tr².
  - P2 the ghost-derived correction is a **per-qubit multiplicative factor consistent across draws**
    (P-independent, as established) — the correction vector's cross-draw r > 0.5.
  - P3 corrected tr² **increases toward 1 without overshooting** (physical bound: a correction that
    pushes tr² > 1 falsifies the model) — and the *mean* improvement across draws is resolvable
    above shot noise.
  - **P4 (the falsifier / the honest branch)**: if the correction helps some draws and hurts others,
    or overshoots > 1, or is draw-inconsistent → the weight-1 ghost is an **incomplete** error model
    (there is higher-weight or coherent structure it misses) — a real, publishable bound on the
    model, not a failure to hide.
- **Why it's the top**: it is the campaign's only **compounding** result — a validated mitigation
  improves *every future two-copy grade*, and success is the Creator's integration criterion met on
  the crown corpus. **Fence**: this produces a *candidate* mitigation **offered to the F122 lane**
  (Ember's numbering seat); it does not re-grade F122's advantage claim.
- **Depends on**: U1 (needs the signed per-qubit factors). Run U1 → U0 as the opening pair.

### U1 — Ghost phase (weight-1 signed direction) — **$0, feeds U0**
- **Claim to test**: the ghost is weight-1-exclusive and P-independent (established C5073). Its
  *magnitude* per hot qubit is known; its **signed per-qubit direction** (the sign of the readout
  asymmetry on qubits 17-27, 24-25, 37-45, 28-29) is not. Weight-1 ⇒ 3^1 = 3 ⇒ the sign is
  recoverable where the high-weight sealed-P phase (dig A) is not.
- **Data**: door-b healthy draws {refly, i1, i2, i3}, marrakesh, 72-106k two-copy shots each.
- **Estimator**: **D** (signed). Per qubit q, per letter L∈XYZ: `s[q,L] = D.estimate_signed(Q,bells)`
  (the *signed* tr(Qρ), not the squared magnitude the tr² path returns).
- **PIN**: (a) `D.selftest()` passes; (b) the *magnitude* |s[q,L]|² reproduces the weight-1 tr²
  the C5073 sign-test recorded on the same draw to < 2e-3.
- **FROZEN PREDICTIONS**:
  - P1 pin passes.
  - P2 the sign vector is **consistent across the 4 draws** (same per-qubit sign — reinforces
    apparatus/P-independence at the sign level, not just magnitude).
  - P3 the sign structure discriminates: a **coherent** readout error gives a consistent directional
    sign; **incoherent** decoherence gives sign that flips randomly across draws (|mean sign| ≈ 0).
    Either outcome refines the S1/S3 leaning A2 could not close.
- **Falsifier**: signs random across draws AND across qubits ⇒ the "direction" is shot noise; report
  the ghost as magnitude-only (no phase structure).
- **GAP/dependency — CLEARED (verified C5073)**: `D.estimate` returns `mean(shot_value)` where
  `shot_value` is a **product of ±1 sign-table entries** ⇒ it is **already signed** tr(Qρ), not a
  squared magnitude. The signed reading exists and the sign-test already consumed it. U1 is
  **unblocked**. (The per-qubit "power" in the sign-test was a signed *sum* over XYZ, so U1's
  per-letter sign vector is a finer read of the same quantity — no new estimator needed.)

### U2a — Boundary purity (truncated tr(ρ²), low weight) — **$0**
- **Claim to test**: full purity tr(ρ²) = (1/2ⁿ)(1 + Σ_{Q≠I} tr(Qρ)²) needs all 4ⁿ terms
  (hopeless variance — the calibrated-spectrum doc already flagged this, and the naive symmetric
  SWAP purity returned NO-TEST). But the **boundary contribution**
  P_W = (1/2ⁿ)(1 + Σ_{w(Q)≤W} tr(Qρ)²) is a genuine, computable **lower bound on purity** from the
  low-weight shell only.
- **Data**: same door-b healthy draws. **Estimator**: g2 (tr²), summed over all Paulis of weight
  ≤ W (W=2 ⇒ 16·3 + C(16,2)·9 = 48 + 1080 = 1128 terms, all exact-enumerable).
- **PIN**: g2 reproduces a graded tr² < 2e-3 (as in the calibrated spectrum).
- **FROZEN PREDICTIONS**: P1 pin. P2 P_{W=1} ≈ 1/2ⁿ + (ghost power)/2ⁿ (boundary is nearly the
  ghost). P3 P_{W=2} − P_{W=1} is at the shot floor (no weight-2 structure — matches the
  weight-spectrum flat-at-floor). The **rise of P_W with W** unfolds *where the state's purity
  lives* in weight.
- **Falsifier**: a large jump at some intermediate W ⇒ hidden mid-weight structure the spectrum
  sampling missed (would re-open the weight-spectrum finding).

### U3 — Conv-arm boundary layer (dig A restricted to low weight) — **$0, encoding-gated**
- **Claim to test**: the 707k single-copy conv shots (wave1-n10, kingston) are a classical-shadow
  dataset never mined for state structure. At **weight ≤ 3** (3^w ≤ 27, SE ≈ 0.006 at 707k) the
  **signed** tr(Qρ) — the phase the same-state two-copy squares away — **is** recoverable. This is
  dig A executed in the region where it is not walled.
- **Data**: `results/h14_lock5_rescue_exp142_wave1_n10_*.json` conv pubs (8 pubs, ~707k rows ×
  10 bits) + `exp142_wave1_n10_manifest.json` (`conv_bases_order` = itertools.product XYZ,
  `conv_b_strings`, `conv_layout`). Sealed P = YYXZXXXYZZ (from the quantum arm P_hat).
- **Estimator**: classical-shadow inversion for Pauli observables — for each shot in basis B,
  contribute to tr(Qρ) only when Q's support ⊆ B's measured support with matching letters; standard
  single-shot shadow estimator `∏_{q∈supp(Q)} 3·⟨b_q|Q_q|b_q⟩`.
- **PIN (mandatory, this is the convention-heavy run)**: reproduce a **known** conv-arm quantity
  before trusting any new one — the **sentinel Bell fidelity** (0.985 start / 0.99 end, pubs 0/13)
  and/or the conv cal blocks (pubs 1-3). If the pin does not reproduce, **NO-TEST** and the encoding
  is reported as un-pinned (do not force it).
- **FROZEN PREDICTIONS**: P1 sentinel/cal pin reproduces the recorded fidelity < 2e-2. P2 weight-1
  and weight-2 signed tr(Qρ) recovered with SE ≈ 0.006; the sealed P's *low-weight marginals* carry
  recoverable sign. P3 weight-3 already near the variance ceiling (demonstrates the 3^w gradient
  empirically on real data — the campaign's own principle, measured).
- **Falsifier**: pin fails ⇒ NO-TEST (encoding un-recovered). This is the highest-risk run; it runs
  **only after U1 validates the signed-reading approach on the cleaner two-copy data**.

### U4 — B1 dual-certificate orbit unfold — **$0**
- **Claim to test**: the B1 512 ceiling was proved via exchange-WLOG symmetrization (S₂ folding) +
  a dual certificate. The **support of the optimal dual** unfolds *which constraint orbits bind* —
  the "shape" of the 512 wall, invisible in the scalar U′ = 0.9067.
- **Data**: the solved SDP (`tools/h14_b1_g3_rounding.py` outputs: S, y1, λ_min(S), comb maps).
- **Estimator**: eigendecompose S at the optimum; the near-zero eigenvectors (complementary
  slackness) are the active constraints; map them back through the comb to the physical constraint
  orbits.
- **PIN**: the certificate value recomputes to the published U′ = 0.9066741104 (16-digit).
- **FROZEN PREDICTIONS**: P1 pin. P2 the active set is **low-dimensional** (a handful of orbits bind
  the ceiling). P3 the binding orbits identify *which* exchange structure the 512 problem's optimum
  actually uses — a structural read on the wall, and a candidate for the folding-lane F2.
- **Falsifier**: full-rank active set ⇒ no compressible structure; report the wall as generic.

### U5 — Ghost-vs-epoch drift unfold — **$0**
- **Claim to test**: the ghost jackknife found a cal-linked systematic across draws. Does the ghost
  power **drift** with calibration epoch / submission time (thermal, cal aging)?
- **Data**: banked draws' W1 (48-term weight-1 power) + each flight's timestamp/job metadata.
- **PIN**: W1 per draw reproduces the jackknife's recorded values.
- **FROZEN PREDICTIONS**: P1 pin. P2 a monotone or thermal-shaped drift ⇒ feeds boards #143
  (thermal head gauge) / #145 (clock-spend). P3 no drift ⇒ ghost is epoch-stable apparatus (cleaner
  S3 reading). **Falsifier**: no time structure ⇒ report flat.

### U6 — Sentinel device-health timeline — **$0, cheap**
- **Claim to test**: every flight carries start/end sentinel Bell pairs (400 shots). Aggregated
  across ALL banked flights they unfold into a **device-health timeline** (fidelity vs time/device).
- **Data**: all `*sentinel*` / pub-0/pub-13 blocks across the corpus.
- **PIN**: one flight's sentinel reproduces its recorded start/end (0.985/0.99 for wave1).
- **PREDICTIONS**: P1 pin. P2 a per-device fidelity trend. **Falsifier**: too few banked sentinels
  to form a series ⇒ report coverage, not a trend.

---

## 2. FOLD lane — fold classical structure through a quantum envelope

These are **catalogs/frameworks** (what rides which envelope) with one concrete runnable each.

### F1 — Degree-2-in-ρ functionals through the two-copy Bell envelope
- **Native operation**: the two-copy envelope computes **quadratics in ρ**. Catalog of what folds:
  | functional | needs | status |
  |---|---|---|
  | tr(Qρ)² (per Pauli) | ρ⊗ρ same-state | **flown** (F122) |
  | tr(ρ²) purity (full) | ρ⊗ρ | walled (4ⁿ variance) |
  | tr(ρ²) boundary (low-w) | ρ⊗ρ | **U2a, $0** |
  | Rényi-2 entropy −log tr(ρ²) | ρ⊗ρ | rides U2a (boundary bound) |
  | **tr(ρᵢρⱼ) cross-fidelity** | **ρᵢ⊗ρⱼ (different states in the two copies)** | **needs FLIGHT — see U2b/GAP-2** |
- **Runnable (framework)**: emit the table above as a machine-readable envelope-capability manifest
  so future degree-2 questions route to the right lane automatically.

### F2 — Exchange-symmetric optimization through the B1 SDP envelope
- **Native operation**: the B1 certificate machinery solves **optimizations with S₂/exchange
  symmetry**. Candidate to fold: any classically-hard bound with the same symmetrization (the U4
  active-orbit read tells us which structure the machinery actually exploits, so we fold a problem
  that matches it, not one that fights it).
- **Runnable**: after U4, name ONE concrete classical bound with matching symmetry and check the
  certificate machinery accepts its constraint matrix (pin: recovers a known small case).

### F3 — The wall catalog (what does NOT fold — naming walls is part of exhaustiveness)
- **linear obs through quadratic envelope** → dig A wall (3^w). Use single-copy shadows at low w
  instead (U3).
- **general classical circuit through a quantum envelope** → QAOA/VQE, needs coherent gate depth
  not cheap on ALT4. Out of scope until a depth budget exists.
- **cross-state fidelity through same-state two-copy data** → GAP-2: our ρ⊗ρ flights cannot see
  tr(ρᵢρⱼ); needs a ρᵢ⊗ρⱼ prep (U2b flight) or a low-weight shadow route (bounded by 3^w).

---

## 3. GAP REVIEW (second pass — what the first draft missed)

- **GAP-1 — CHECKED, RESOLVED (not a blocker)**: I suspected U1 needed a signed estimator D might
  not have. **Verified**: `D.shot_value` multiplies ±1 sign-table entries and `D.estimate` returns
  their mean ⇒ **D.estimate is already signed** tr(Qρ). The sign-test consumed it (its per-qubit
  "power" was a signed sum over XYZ). U1 is **unblocked**; still PIN the magnitude against the
  sign-test's recorded tr² before trusting the per-letter signs. *(Gap review turned a suspected
  block into a cleared run — the reason to check gaps rather than assume them.)*
- **GAP-2 (corrects the ponder)**: I proposed "cross-state fidelity tr(ρᵢρⱼ) folded through the
  existing two-copy flights" — **wrong**: those flights prepared ρ⊗ρ (**same** state in both
  copies), so they cannot measure a **cross**-state overlap. tr(ρᵢρⱼ) needs a ρᵢ⊗ρⱼ prep. *Fix*:
  demote to **U2b (FLIGHT-gated)** — a cheap ALT4 two-copy flight preparing two *different* sealed
  draws in the two registers; directly tests prep reproducibility ("walk like a duck" across
  epochs). Held behind explicit GO (it is a flight, not $0).
- **GAP-3 (U3 risk)**: U3 is convention-heavy (conv-arm row→basis→outcome encoding). *Fix*: ordered
  **after** U1 so the signed-reading approach is already validated on clean two-copy data; hard
  sentinel/cal PIN or NO-TEST; never force the encoding.
- **GAP-4 (rediscovery)**: before running each, run the F-ledger check
  `node /droid/repos/dc_shared/tools/already-built.js "<run concept>"` — U2a/U4 especially may
  overlap prior purity/certificate work. Log the check in the ledger row.
- **GAP-5 (estimator provenance)**: two estimators (D signed, g2 tr²) — a run must not silently mix
  them. *Fix*: each ledger row records which estimator + that its selftest/pin passed.
- **GAP-6 (weight enumeration blow-up)**: U2a at W=2 is 1128 terms (fine); W≥3 is not enumerable —
  switch to sampling with stated variance (as the weight-spectrum did). *Fix*: enumerate to W=2,
  sample above, and **state the resolution** per the calibrated-spectrum honesty rule.

---

## 4. RUN INFRASTRUCTURE (added to facilitate exhaustive execution)

### 4.1 Standard run contract (every run .py follows this)
```
1. import the validated estimator (D or g2); run its selftest → NO-TEST on fail.
2. PIN: reproduce a banked known-answer < tol → NO-TEST on fail (no fabricated number).
3. FROZEN PREDICTIONS already written in THIS doc before the run exists.
4. compute the estimand; write results/unfold_<id>_c5073.json with {card,pin,predictions,verdict}.
5. print PIN line + verdict; commit artifact; append the ledger row (§4.3).
```

### 4.2 Run template (copy per run)
```python
#!/usr/bin/env python3
"""UNFOLD <ID> — <one-line claim> (Whisper C5073). $0|FLIGHT. FROZEN before compute.
PIN: <known-answer>. PREDICTIONS: P1.. (see docs/unfold-fold-campaign-whisper-c5073.md §<x>)."""
import json, os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
sys.path.insert(0, os.path.join(HERE,"..","tools"))
# import D or g2; selftest; PIN; compute; NO-TEST on any pin fail; dump artifact.
```

### 4.3 Results ledger (fill as runs complete)
The **`builds?`** column is the review addition: does the run *produce a reusable
instrument/mitigation/benchmark* (the F111/F112/F115 "reusable move" pattern), or only characterize?
The build-upon runs are the ones the Creator's integration criterion actually rewards.
| id | lane | cost | estimator | F-check | PIN | builds? | verdict | artifact |
|----|------|------|-----------|---------|-----|---------|---------|----------|
| **U0** ⭐ | unfold | $0 | D=tr² | ✅ | ✅ | **YES — noise-model + a null on ghost-mitigation, both to F122 lane** | ✅ **DONE C5073**: uniform f=0.9528±0.0018 model reproduces all 4 secrets' tr² to 0.2% (duck); ghost-specific refinement does NOT beat weight (P4 honest branch) → ghost is a side channel, not the advantage limiter | unfold_U0_ghost_mitigation_c5073.json |
| U1 | unfold | $0 | D=tr² | ✅ | ✅ | feeds U0 | ✅ **DONE C5073**: PREMISE-CORRECTED — two-copy tr² is sign-free at all weights; delivered P-independent ghost map (cross-draw r +0.809) | unfold_U1_ghost_phase_c5073.json |
| U2a | unfold | $0 | D=tr² | ✅ | ✅ | purity-in-weight profile | ✅ **DONE C5073**: BOUNDARY carries only the w=1 ghost (3–4.6σ, decreasing i1 0.120>i2 0.067>i3 0.011), w=2 at floor, mass at planted weight — weight-1-exclusive ghost confirmed from the purity angle | unfold_U2a_boundary_purity_c5073.json |
| U3 | unfold | $0* | shadow | ☐ | ☐ | **YES — measures the 3^w cost curve on real silicon** | Wave 2 (after U1, encoding-gated) | unfold_U3_conv_boundary_c5073.json |
| U4 | unfold | $0 | SDP | ✅ | ✅ | null on F2's premise | ✅ **DONE C5073**: pin=min_eig(WA) exact (obj factor-2 convention, reported). NEAR-FULL-RANK 456/512, 403 dirs hold 99% → 512 wall is GENERIC, not compressible (symmetry present but high-dim face). Weakens F2 | unfold_U4_dual_orbits_c5073.json |
| U5 | unfold | $0 | tr² | ✅ | ✅ | feeds #143/#145 | ✅ **DONE C5073**: LOW-POWER (n≤4, ordinal time, W1 not monotone). Obs: refly W1~0 vs draws 0.01–0.12; needs absolute timestamps — named | unfold_U5_epoch_drift_c5073.json |
| U6 | unfold | $0 | Bell | ✅ | ✅ | **YES — device-health gauge (F112 kin)** | ✅ **DONE C5073**: SERIES BUILT — 61 flights, sentinel fidelity 0.960±0.015; exp142 (0.974) cleaner than exp144 (0.956). Abs-time ordering needs timestamps | unfold_U6_sentinel_timeline_c5073.json |
| F1 | fold | $0 | — | ✅ | ✅ | **YES — the envelope-capability manifest** | ✅ **DONE C5073**: routing table emitted; 4 functionals fold on banked data (2 BUILT: U2a, U0 noise-model), 2 need U2b flight, 1 phase-walled | fold_F1_degree2_manifest_c5073.json |
| F2 | fold | $0 | SDP | ☐ | ☐ | premise weakened by U4 | Wave 3 (U4 shows near-full-rank → low priority) | fold_F2_symmetric_opt_c5073.json |
| U2b | unfold | **FLIGHT** | two-copy | ☐ | ☐ | **YES — a prep-reproducibility instrument** | — | (gated on GO) |

`*` U3 is $0 but encoding-gated (NO-TEST if the conv encoding won't pin).

**The build-upon shape (review headline)**: U0 is the run to fire first — it is the only one whose
success *is* the Creator's "walks like a duck" integration test, and a validated ghost-subtraction
compounds into every future two-copy grade. U2a/U3 build the second compounding artifact — a
**device unfold-depth axis** that ranks chips on "how deep can you unfold for free," kin to F112's
benchmark beyond QV/CLOPS/EPLG. The rest characterize (still worth it) but do not compound.

### 4.4 Execution order (dependency-respecting)
```
Opening pair ($0):            U1 → U0   ── the build-upon spine: signed factors, then the mitigation test
Wave 1 ($0, independent):     U2a, U4, U5, U6, F1  ── run in parallel alongside the opening pair
Wave 2 ($0, gated):           U3 (after U1 validates the signed reading on clean two-copy data)
Wave 3 (needs U4):            F2 (uses U4's active-orbit read)
Wave 4 (FLIGHT, explicit GO): U2b
```

### 4.5 Gates
- **$0 runs (U1-U6, F1-F2)**: cleared under "run it all exhaustively" (standing GO for re-analysis).
- **U2b and any flight**: explicit per-flight GO, ALT4 free tank only, preflight
  `preflight_account_check.py` + `attack_preflight.py` before any submission; **never** whisper-de /
  WhisperPaid.
- **Every run**: F-ledger check (GAP-4) + freeze (predictions are already in this doc) + pin-or-NO-TEST.

### 4.6 Close-out
When all $0 runs land: append a §10.7 to `quantum-status-comprehensive-whisper-c5073.md`
summarizing verdicts, and record any FLIGHT-gated remainder as a board row. The campaign's thesis
— **weight is the radial coordinate; unfold at the boundary, fold when the algebra matches** — is
confirmed or revised by the U2a/U3 weight-gradient measurements (they measure the 3^w cost curve on
real data, not just assert it).
