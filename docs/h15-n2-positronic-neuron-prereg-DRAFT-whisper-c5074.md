# Pre-registration SKELETON — H15/N2: the Positronic Neuron reflex flight

**Whisper C5074 · substrate `claude-fable-5` · Creator GO for the charter+skeleton draft (this session); NO flight GO exists**
**Charter**: `docs/star-trek-horizons-15-the-positronic-neuron-whisper-c5074.md`
**Status of this document: SKELETON. Nothing here is frozen. It cannot freeze before Cell N1 passes its pin and the comparator ruling (§4) lands.**

---

## ⬛ STATUS — the single most dangerous field in this document

| gate | state | owner |
|---|---|---|
| **G0** Cell N1: in-circuit decision == classical decode, exact, simulated; depth/MCM budget survivable | ✅ **G0-PIN-PASS (Whisper C5074, `experiments/h15_n1_synapse_incircuit_whisper_c5074.py` → `results/h15_n1_pin_c5074.json` + `h15_n1_noise_survival_c5074.json`)** — pin run STRONGER than specced: shot-by-shot in-circuit response == classical decode over **ALL 1024 A × 8 shots (ALT) + 8192 sampled NULL shots: ZERO mismatches**; P(accept\|ALT) = **1.0 exactly** (8192/8192); NULL accept 0.53210 Wilson [0.52129, 0.54289] ∋ 17/32; success 0.73395 ≈ 47/64. Bell convention calibrated in-script (map (a,b)→(b,a) on measured bits, pair-preserving → Toffoli rule valid). Ablation arms behave (never→0, always→1). **Resources: 28 CZ transpiled (6% of the 475 wall), depth 87, ONE MCM (+1 if_else)**; noise-survival ESTIMATE under representative Heron-class noise (2q 0.3%/1q 0.02%/RO 1% — labeled estimate, not a snapshot; flight predicts from day-of spectrometer f at G3): success 0.7126, **margin over provisional ceiling +0.154** — clears any 2.3-SD threshold (~0.60 at S=632-class) with room. Built against the PROVISIONAL 143/256 per Elder's building≠freezing ruling. | Whisper |
| **G1** comparator ruling: per-trial k=0 ceiling (exact), claim shape, comparator symmetry, frozen criterion + power | ✅ **G1 COMPLETE (Elder C6627, `docs/h15-g1-completion-elder-c6627.md` + `experiments/h15_g1_completion_elder_c6627.py` → `results/h15_g1_completion_elder_c6627.json`)** — the Gauss-sum derivation landed: **M₂ = 4⁻ⁿ(I + SWAP + 2ⁿP_Φ − 2D)** proven and brute-verified n=1..4; both closed forms are now THEOREMS at all n (quantum 3/4+(2ⁿ⁻¹−1)/(2·4ⁿ) via ‖X‖₁ = 4ⁿ+2ⁿ−2; **ceiling 1/2+(2ⁿ−1)/4ⁿ EXACT** via matching primal E\* = P_Φ+2^(1−n)(P_sym−D) [PT-invariant] and Elder's independent ANALYTIC dual Y=((2ⁿ−2)/4ⁿ)P_Φ, Z=(1/2ⁿ)P_Φ with exact slack identity Y+Z^Γ−Δ=(2/4ⁿ)(D−P_Φ), ZERO gap — no solver, no ansatz). Two-seat diff on record (§7): Whisper's solver dual converged onto the exact form from above (+2.8e−11/+4.0e−10/+2.7e−9 at n=2/3/4), Elder's certificate = the W=0 face of Whisper's dual program. Bonus theorems: M₂ is transversal-Bell-diagonal with outcome law P(a,b)=4⁻ⁿ[1+(−1)^(a·b)+2ⁿ·1[a=b=0]−2·1[b=0]] ⇒ support rule = Helstrom exactly, simple-rule P(accept|ALT)=1 exactly (the G0 8192/8192 is a theorem), NULL accept 1/2+2^−(n+1) = 17/32 ✓, n=2 vacuity analytic. **CEILING FROZEN: 143/256 at the n=4 micro — PROVISIONAL label retired.** Criterion inherits unchanged: margin ≥ 2.3 per-trial SD at flown S over 143/256; severed-synapse must NOT beat 143/256 (G3). Prior history: **ROUTE RULED, NUMBER PENDING** (Elder C5074, coordination#12393): (1) ceiling needs its OWN derivation — neither HH25 (many-copy statistic, wrong task) nor A&S (asymptotic, wrong granularity) hands it over; ruled route = exact 2-copy moment operator E_A[ψ⊗ψ] for the deg-2 ensemble (closed form via quadratic Gauss sums; E_A[ψ]=I/2ⁿ is EXACT from the door(a) court), official ceiling = **separable-measurement SDP optimum** over it, symmetry-reduced, EXACT at flown n — separable ≥ LOCC ≥ adaptive-k=0, so any overstatement is HARDER for us (safe side); **pin numerically at n=4 brute + attempt closed form, BOTH must agree before freeze**. (2) claim shape: per-trial closed-loop accuracy vs the exact ceiling **ADMISSIBLE AS FLOWN** (F123 currency-ruling consistent; door(a) excess-over-noise was two-arm-specific); **no slope claims at single-n micro**. (3) comparator symmetry: ideal noiseless classical agent **RATIFIED, zero actuation-cost charges** (c1-leaves-hardware verbatim; charging the comparator = certifying a handicapped opponent, F119-family costume, refused). (4) criterion = exact-ceiling + margin **≥ 2.3 per-trial SD at flown S** (S-lever lesson, flights 4→6); in-job known-A cal rows pin decode convention + response-accuracy τ analogue; zero-flip sensitivity row pre-registered. **G1 lands when the ceiling number exists.** → **CEILING ATOMS COMPUTED (Whisper C5074, same session — `experiments/h15_g1_ceiling_atoms_whisper_c5074.py` + `h15_g1_accept_structure_whisper_c5074.py`, artifacts `results/h15_g1_ceiling_atoms_c5074.json` + `h15_g1_accept_structure_c5074.json`)**: M2 exact, brute==Gauss byte-identical n=2,3,4; single-copy mixture exact. **n=4 numbers**: PPT ceiling primal **0.5585937496 ≈ 143/256** (matches closed-form candidate **1/2+(2ⁿ−1)/4ⁿ** to 4e-10 at all three n; PRIMAL ONLY — analytic derivation + dual certificate owed at freeze); quantum ideal: transversal-Bell **EQUALS global Helstrom exactly, 391/512 = 0.763671875** (= 3/4+(2ⁿ⁻¹−1)/(2·4ⁿ), exact all n) via support-membership rule with P(accept|ALT)=1; simple in-circuit rule XOR_i(a_i AND b_i)=0 gives **47/64 = 0.734375** (= 3/4−2^−(n+2)), one AND+XOR classical expression. **Gaps over ceiling: optimal +0.2051, simple +0.1758.** Caution row: **n=2 is VACUOUS for the simple rule (gap exactly 0)** — MICRO must be n=4. 4-copy symplectic parity computed and INFERIOR per copy (0.749/4 copies vs 0.734/2) — the 2-copy per-trial framing stands. Awaiting Elder ratification of the closed forms + dual certificate before this row turns ✅. → **ASKS ANSWERED (Elder C5074, coordination#12398, with his own independent execution — mixture 0.0e0 exact, Helstrom form MATCHED exactly at n=2,3 on his code)**: quantum closed form **RATIFIED numerically two-seat** (analytic Gauss-sum derivation = Elder's work item, lands as the G1 completion doc); ceiling form PRIMAL-ONLY — analytic ratification travels WITH the dual; **dual spec = B1 G3 verbatim** (producer extracts PPT dual + out-of-solver feasibility via eigenvalue residuals + rigorous rounding to U′; Elder re-derives independently; diff on record; two-seat independent derivation NOT optional); **official ceiling PROVISIONAL at 143/256 — N1 may BUILD against it (building ≠ freezing)**; n=4 load-bearing micro RATIFIED; 2-copy per-trial framing RATIFIED (4-copy inferior per copy, measured). Elder's close: "Build G0." → **PRODUCER DUAL DONE (Whisper C5074, `experiments/h15_g1_dual_certificate_whisper_c5074.py` → `results/h15_g1_dual_certificate_c5074.json`)**: PPT dual extracted, PSD-repaired and re-verified OUT-OF-SOLVER (numpy eigvalsh, every shift on the bound-inflating side), rigorous U′: **n=4 sandwich 0.5585937500 ≤ ceiling ≤ U′ 0.5585937518** (gap 1.8e-9), closed form 143/256 INSIDE the sandwich at all three n (n=2 gap 5e-10, n=3 7e-10), certificate_ok all n. **Remainder of G1 = Elder's fresh-sitting Gauss-sum derivation + his independent dual re-derivation, landing together as the G1 completion doc** (his call coordination#12402 — convention-sensitive algebra deferred off marathon-tail, correctly). | Elder |
| **G2** seals: sealed stimulus ensemble (degree-2 phase states, door(a) drawing convention verbatim), secrets+salts off-git 0600, **G-PUBLIC**: commitment pushed to origin BEFORE any flight exists | ⬜ OPEN — awaits G0+G1 | Ember |
| **G3** $0 sims + vacuity guards: known-answer pin (G0), planted-mutation catches (parity-blind decision; coin-flip actuator), severed-synapse arm must NOT beat the G1 ceiling in sim, F90 feedforward price inside margin | ✅ **G3-PASS (Whisper C5074, `experiments/h15_g3_guards_whisper_c5074.py` → `results/h15_g3_guards_c5074.json`)** — **M1 parity-blind CAUGHT** (912 pin mismatches + NULL-accept 1.0 vs 17/32); **M2 coin-flip CAUGHT** (1523 pin mismatches + ALT-accept 0.52 vs 1.0-exact); **severed-synapse arms DO NOT beat the frozen ceiling**: X⊗Z 0.5142, X⊗X 0.5056 vs 143/256 = 0.5586 — the Bell memory link is load-bearing, the design is non-vacuous; **F90 feedforward price applied** (integrity 0.947, whole-chain → conservative; fake backends carry NO ff-noise model, so priced on top of the N1 estimate): success 0.6901, **margin over frozen ceiling +0.1315, clears the 2.3-SD threshold at S=632**. Same detection pipeline as G0 (pin + aggregates) — the guards guard. | Whisper |
| **G4** budget + Creator GO: free-tank fit with **MCM ≈ 3× billing multiplier applied**, instance pinned per #151, seal-bound GO citing the staged digest | ⬜ OPEN | Creator |

**STATUS ✅ = FROZEN. NOTHING BELOW IS FROZEN.**

> ### ⚠️ PROPAGATION RULE — binding, inherited verbatim from the door(a) card
> Any ruling that changes a gate state must be written **into this block, at the top, with its
> citation, in the same cycle it is made**. A commit message does not count. A document cannot
> report its own invalidation, so the check is "is there a newer ruling on this gate", never
> "does this document look complete."

---

## 0. Task, currency, claim shape

**Task (per reflex trial).** The agent receives **two copies** of a sealed, unknown n-qubit stimulus
state ρ and must set an **actuator qubit** to the correct response — all inside one circuit, with no
classical processing between stimulus and response:

| | stimulus | correct response |
|---|---|---|
| **NULL** | `I/2ⁿ` (maximally mixed) | actuator ends `|0⟩` |
| **ALT** | sealed uniformly-random degree-2 phase state `|ψ_A⟩` (door(a) drawing convention verbatim: A upper-triangular INCL diagonal, n(n+1)/2 bits, Z on diagonal, no exclusions) | actuator ends `|1⟩` |

**The loop, one circuit**: prep 2 copies → two-copy Bell interaction (the memory link) → outcome-bit
parity accumulated into decision ancilla → **mid-circuit measurement** of the ancilla → **feedforward**
conditional gate on the actuator → readout of the actuator ONLY as the graded response. Three arms in
one job (transmission pattern): **auto** (live feedforward) / **never** / **always** (frozen-decision
ablations).

**Currency — declared once.** **Copies consumed per trial = 2.** The comparator is charged in the
same unit. (door(a) lesson: one unit, stated once, grader carries a units row.)

**Claim shape if WIN — ⬜ OPEN, awaits G1 rulings 2+3.** Placeholder, NOT admissible until ruled:
closed-loop per-trial response accuracy p̂_auto vs the exact classical-memory per-trial ceiling
p_C1(n) at 2 copies/trial, with criterion and any excess-over-noise-only structure per Elder's ruling.
**No runtime claim. No simulation-cost baseline. No new theory floor** — the floor is inherited:

| floor_status | floor_scale | measured_effect |
|---|---|---|
| **PROVEN-IN-PRINT** (A&S arXiv:2607.02444 Thm 1.1; full-text verified C5027) | constant-vs-Θ(n) copies, k=n vs k=0 | **none — nothing flown** |

## 1. Rungs

**Powered design — RATIFIED (Elder coordination#12427, re-derived before confirming: 40-graded-events threshold 0.7392 ✓ impossible, S>1 currency-barred ✓, P(win) rows ✓, copies 1392 ✓; error class owned on the record as TRIALS-vs-SHOTS, door(a) Amendment-3 family — "every cost unit carries ITS OWN multiplier"). BINDING TRIPLE: n=4 · M=632 sealed graded single-shot trials (316/316 balanced) · S=1, + 64 UNGRADED known-A cal rows outside the sealed set. THRESHOLD FROZEN 0.6040 = 143/256 + 2.3·√(p_C(1−p_C)/632). Ember directed to cut at --n 4 --M 632 --balanced, G-PUBLIC before any flight exists.** Original proposal row follows (Whisper C5074, G3 seat — reconciled Elder #12418 with the frozen per-trial claim): **M = 632 sealed graded trials (316 ALT / 316 NULL balanced), S = 1 shot per trial**, + **64 UNGRADED known-A calibration rows** (32/32; decode-convention + τ pin per G1 item 4; known-A by design, need no seal). **S=1 is FORCED by currency**: the claim is per-trial at 2 copies — a shot-averaged trial consumes extra copies against a 2-copy ceiling (F119 units-inflation class, refused at design). **Units catch on record**: the 2.3-SD denominator counts GRADED RESPONSE EVENTS; Elder's threshold arithmetic (0.604) already assumes 632 graded events, but a door(a)-style (M=40 × S=632-aggregate) structure would grade 40 events → threshold 0.7392 > noiseless ideal 0.7344 = win IMPOSSIBLE as frozen. "S=632" (Elder) and "M=632" (this row) are the same number: 632 single-shot reflexes. **Threshold 0.6040; P(win): 100% at N1-noise 0.7126, 100% at F90-priced 0.6901, 99.2% at pessimistic 0.65.** Copies 1264 graded + 128 cal = 1392; 696 single-shot executions, one job, door(a)-flight scale; MCM 3× priced at G4.

**MICRO n=4 first** (F119-remedy precedent): 2n=8 stimulus qubits + 1 decision ancilla + 1 actuator
= 10 qubits. Register chosen by U2b-spectrometer per-qubit f + layout-gate safe scores (marrakesh
≤ 0.039 / aachen ≤ 0.036 — paid, so effectively marrakesh/kingston/fez per #151). Escalation to
n=8 only after MICRO certifies, as its own gated flight.

## 2. Decode + custody

- Whisper independent blind decode **from the actuator record alone**, hashed pre-unseal.
- Elder grades against sealed truth; Ember integrity-gates the reveal.
- **G-PUBLIC enforced at submit** (flight-6 precedent: commitment public on origin before the job
  exists — attestation is not custody).
- Cal-pins-the-convention: in-flight calibration rows (known-A instances) select the decode
  convention and anchor the criterion in-job (τ_Q analogue — exact design ⬜ OPEN, G1 ruling 4).

## 3. Controls (each with a fault-injected positive control proving it can block)

| control | must show | else |
|---|---|---|
| **Severed synapse** (single-copy product-basis measurement, same circuit shape, same decision+actuator) | does NOT beat the G1 ceiling | instrument broken; every N2 number void |
| **never / always arms** | auto beats both frozen-decision arms | the decision doesn't matter; no agent claim |
| **NULL-stimulus rows** | response at chance/`|0⟩`-side per criterion | decision ancilla is reading something other than the stimulus |
| **Planted mutations (sim, G3)** | parity-blind decision + coin-flip actuator both CAUGHT | G3 fails closed |

## 4. Kill criteria (pre-committed)

1. G0 depth/MCM wall → **NO-TEST at $0**, the wall is the finding (charter's N1 branch).
2. Severed-synapse sim arm beats the ceiling → design vacuous, back to N1.
3. F90-priced feedforward error floor eats the sim margin → NO-GO before spend.
4. Any cross-job phase dependence in the design (currency map law) → design error, back to N1.
5. Comparator ruling makes the per-trial claim inadmissible at n=4 → escalate rung or stop; no
   band-shopping the claim shape.

## 5. Open items ledger

| item | owner | blocking |
|---|---|---|
| Cell N1 build + exact pin | Whisper | G0 |
| Comparator four rulings | Elder | G1 → §0 claim shape, §2 criterion |
| Seal + G-PUBLIC staging | Ember | G2 (after G0+G1) |
| MCM-priced budget row + GO | Creator | G4 (last) |
