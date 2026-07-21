# H7 "The Ship's Doctor" — Comprehensive Implementation Plan (P1–P7)

**Whisper C4949, substrate claude-fable-5. Status: PLAN (per-flight pre-registrations still to be
frozen individually before any submission). Companion to
`star-trek-horizons-7-the-ships-doctor-whisper-c4948.md` and `finding-exp241b-syndrome-memory.md`.**

---

## 0. Hardware ground truth (verified live this cycle)

**IBM open plan quota: 4,109 s remaining of 10,800 s annual** (period 2026-07-10 → 2027-07-10;
6,691 s consumed in the first 11 days — burn-rate discipline is the binding constraint, not capability).
**Measured job costs** (from our own recent jobs): Exp241 (15 dynamic pubs, 8k shots, feed-forward) =
**41 s**; Exp216 (15 static circuits) = **64 s**. A typical H7 job costs 40–100 s.

**Devices**: IBM Heron r2 (`ibm_fez`, `ibm_marrakesh`, `ibm_kingston`) — heavy-hex, CZ native,
133–156 qubits. Every capability H7 needs is **already proven in our own record**:

| capability | needed by | proven in |
|---|---|---|
| mid-circuit measurement (syndrome ancillas) | P3, P7 | Exp240 |
| feed-forward `if_else` on clbits (dynamic circuits) | P7 (required), P3 (optional) | Exp240/241 |
| qubit reset (ancilla reuse across rounds) | P7 | Exp241 |
| pinned + verified physical layout | all | Exp239 lesson (mandatory checklist item) |
| engineered noise injection (coherent axes, storms) | P1, P5 | Exp199/211/216, H6 throughout |
| [[4,2,2]] encode/decode/postselect | P1, P2, P4 | Exp189–199, 216 |
| 3-qubit repetition codes (bit & phase), classical decode | P5, P3, P7 | Exp236/237 |
| teleport with Pauli-frame deferral (no in-circuit fix) | P3 | Exp177 method + Exp192 |
| logical GHZ across 3 detection nodes | P4 | Exp219 |

**Depth guard**: every H7 circuit below is ≤ ~40 transpiled 2q gates — far under the ~100-gate
heavy-hex wall that killed Exp242's phase leg. Nothing in H7 requires distance-3, Eagle, or Braket.
**Verdict up front: all seven programs run on IBM open-plan Heron hardware as it stands today.**

**Standing per-flight discipline** (from the checklist + C4943–48 lessons): frozen pre-registration
with named failure mode; pinned-and-verified layout; post-transpile 2q-count assert; **all-bit
grading** (every classical register gets a pre-registered prediction); **syndrome streams archived and
memory-analyzed** (the 241b analysis runs on every repeated-rounds job by default); substrate stamp.

---

## 1. P7 — THE ADAPTIVE HELM (memory-aware decoder) — fly first

**Claim**: a decoder that uses the syndrome *history* beats the memoryless decoder on identical
hardware rounds, cashing the measured 1.4–1.65× round-to-round memory (finding 241b).

**Layout**: 5-qubit heavy-hex chain (3 data d0-d1-d2 interleaved with 2 syndrome ancillas a01, a12),
same class as Exp241; pin qubits by best 2q-error chain on flight day, verify post-transpile.

**Circuit per round r**: idle τ=30 µs → parity map (a01 ← d0⊕d1, a12 ← d1⊕d2: 4 CZ+H dressing) →
measure ancillas into `syn{r}` → decoder branch → reset ancillas.

**Two pre-registered memory rules** (both simple enough for `if_else`/`switch` on 2-bit registers):
- **Rule A "debounce"**: apply the round-r correction only if syn{r} == syn{r-1} (a persistent
  syndrome). Targets false-positive fixes from ancilla-readout noise (our fire rates 0.37–0.65 are far
  above the physical error rate — readout noise dominates the stream, so single-round fixes often fire
  on phantoms).
- **Rule B "escalate"**: if syn{r} == syn{r-1} ≠ 00 (fired twice, same pattern, *after* a fix), treat
  the round-(r−1) correction as failed: apply the correction again AND flag the shot into a `flag`
  clbit (post-analysis: does flagging concentrate the residual errors? — the leakage-candidate filter).
- Classical logic is pairwise only (4-bit condition space), well inside proven dynamic-circuit support;
  round-0 falls back to memoryless in both rules.

**Arms** (R = 3 and 4 rounds): memoryless-corrected (241 replica, the control), memory-A, memory-B,
sham (measure, never fix), bare (no ancillas). = 5 arms × 2 R + 2 encode/readout calibration pubs ≈
**12 pubs × 8,000 shots**.

**Grading (draft bounds; frozen at pre-reg)**: primary F_arm(R) on the data-qubit majority vote;
PASS if F_memoryA or F_memoryB − F_memoryless > 5·se at R=4 (se ≈ 0.006/arm at 8k shots →
detectable edge ≥ ~0.03). Secondary (must-report): full 241b memory analysis on every arm's syndrome
stream; Rule-B flag-concentration ratio. **Named failure**: memory rules ≤ memoryless (the memory is
real but not exploitable at d=1 readout-noise levels) — kept as a measured bound, informs whether
adaptive decoding is worth carrying to larger codes.

**Cost**: one dynamic job ≈ **50–90 s**. Risk: LOW (all machinery flown before; new part is only the
conditional logic).

---

## 2. P1 — THE SELF-PRESCRIBING SHIELD (diagnose → orient)

**Claim**: measuring the dominant coherent-error axis and *rotating the [[4,2,2]] code's blind spot
away from it* beats the mis-oriented (blind-spot-aligned) shield under identical noise.

**Stage 1 — the scan: $0.** Exp216 already measured the transfer function (acceptance & corruption vs
injected-axis angle; the blind spot is the axis the shield accepts *silently*). Reuse it as the
diagnosis; no new scan flight needed for the demonstration.

**Stage 2 — the prescription flight.** Layout: 4 data + 1 ancilla [[4,2,2]] block (Exp189-class
pinning). For an injected coherent error R_n̂(θ) at the known blind-spot axis (θ ∈ {π/8, π/4, π/2}):
- **Arm ALIGNED** (malpractice control): code in standard orientation — blind spot ON the noise axis →
  predicts high acceptance + high *silent* corruption (the 216 signature).
- **Arm PRESCRIBED**: conjugate the encoding by the 1q Clifford frame that rotates the blind spot 90°
  off the noise axis (prepend/append fixed 1q gates on data qubits — zero extra 2q cost) → predicts
  the same noise now *fires the detector*: lower acceptance, but **higher postselected fidelity**.
- Baselines: no-noise (both orientations), bare unencoded under the same injection.

**Pubs**: 2 orientations × 3 θ × (noise, no-noise) + 2 bare ≈ **14 pubs × 8,000 shots** (static, no
dynamic circuits). **Grading (draft)**: PASS if postselected corruption(PRESCRIBED) <
corruption(ALIGNED) − 5·se at every θ, with the acceptance drop reported alongside (the honest cost of
the medicine). **Named failure**: orientation doesn't transfer off the 216 calibration day (drift moved
the blind spot) — itself a publishable stability datum; mitigation: fly a 3-pub mini-scan (+ ~10 s) in
the same job to re-locate the axis same-window (R1-in-spirit: calibration in the flight's own window).

**Cost**: one static job ≈ **60–80 s**. Risk: LOW-MEDIUM (frame algebra must be sim-verified pre-spend
— density-matrix check is free and mandatory, the P5-killed-in-60s method).

---

## 3. P2 — THE CLOAKING DEVICE (QEC-as-privacy, certified)

**Claim**: every single physical qubit of a [[4,2,2]]-encoded logical state carries ≈ zero information
about the logical bit (each reduced state is logical-independent), while the logical readout stays
high-fidelity — and the cloak *measurably breaks* at two-qubit probes.

**Implementation**: prepare logical |0⟩_L, |1⟩_L, |+⟩_L, |−⟩_L (one logical qubit of the [[4,2,2]]
pair; the gauge qubit pinned to a fixed state). For each logical state, measure ALL 4 data qubits
simultaneously in basis b ∈ {X, Y, Z} → **12 pubs** give, from the same counts: (i) every single-qubit
marginal (the eavesdropper's view), (ii) every pair marginal (the breakdown edge), for free — the
grade-every-bit method as *the experiment itself*. Plus 2 logical-readout pubs (owner's view) and 2
stabilizer-check pubs. ≈ **16 pubs × 8,000 shots**, shallow (≈ 3–4 CZ encode), static.

**Grading (draft)**: per qubit q, estimate I(logical ; outcome_q) from the marginals across the 4
logical states. PASS-CLOAK if max_q I_single < 0.01 bit (se at 8k shots ≈ 0.002 bit) AND logical
fidelity > 0.9. PASS-EDGE if median I_pair > 5× max I_single (the cloak fails exactly as theory says —
two scanners together see the ship). **Named failure**: hardware asymmetry (crosstalk, readout bias)
leaks I_single > 0.01 — reported as a measured privacy leak of real silicon, a finding either way.

**Cost**: one static job ≈ **40–60 s**. Risk: LOWEST of the set. Statistics, not depth, is the work.

---

## 4. P3 — THE PATTERN BUFFER (teleport into a self-healing memory)

**Claim**: a teleported state held in the live-corrected 3-qubit memory survives better than the same
teleported state held bare — the H6 pieces (teleport, QEC loop) *compose*.

**Implementation** (7 qubits: Bell pair b0,b1 + source s + memory d0,d1,d2 where d0 := b1):
1. Prepare test states on s: |0⟩, |1⟩, |+⟩ (three input pubs; |+⟩ is the honest hard case — the
   bit-flip code doesn't protect phase; predict and report its lower ceiling rather than hide it).
2. Teleport s → d0: 2 CZ + H, measure s & b0; **Pauli-frame deferral** (Exp177 method): no in-circuit
   fix — the frame is applied in classical post-processing. Removes all teleport dynamic logic.
3. Encode d0 into d0d1d2 (2 CZ), run R ∈ {2,3} correction rounds (τ=30 µs, 4 CZ + feed-forward each —
   the only dynamic part, straight from Exp241), decode, measure.
4. Arms: teleport+corrected-hold, teleport+bare-hold (same τ·R idle), teleport+immediate-read (the
   seam cost measurement), direct-encode+corrected-hold (no teleport — isolates teleport's
   contribution). ≈ 3 states × 4 arms ≈ **12 pubs × 8,000 shots**.
5. 2q count at R=3: 2 (teleport) + 2 (encode) + 12 (rounds) + 2 (decode) = **18 CZ** ≪ wall.

**Grading (draft)**: PASS if F(teleport+corrected, R=3) − F(teleport+bare, R=3) > 5·se for |0⟩/|1⟩,
with the |+⟩ row reported as the known phase boundary. **Named failure**: the teleport seam (readout +
frame error) eats the correction gain at reachable R — a real composition-tax datum (the campaign has
measured composition taxes before; this would be the FT one).

**Cost**: one dynamic job ≈ **60–90 s**. Risk: MEDIUM (first-ever chaining of the two machines; seam
is genuinely unknown — that is the point).

---

## 5. P4 — THE SHIELDED TRICORDER (Heisenberg-slope sensing behind detection)

**Claim**: a 3-node logical GHZ sensor accumulates phase at slope 3 where the product sensor gets
slope 1 — entanglement-enhanced metrology, behind error detection, on the proven Exp219 layout.

**Implementation**: reuse the Exp219 3-node logical GHZ construction verbatim (its ⟨ZZ⟩/⟨XXX⟩ grading
already certified the state). Add the sensing dial: apply Rz(φ) simultaneously on each node's sensing
qubit, φ ∈ {0, π/8, …, 7π/8} (8 points); read the GHZ parity ⟨X̄X̄X̄⟩(φ) → predict cos(3φ) for GHZ vs
cos(φ) for the product-state control (same nodes, no entangling layer). Detection arms postselect as
in 219. Optional third arm: inject a known dephasing "storm" and show the detection arm rejects it
(the 205 blind-antenna move on a sensor).

**Pubs**: 8 φ × (GHZ, product) + 4 checks ≈ **20 pubs × 4,000 shots** (parity curves need fewer shots
per point). **Grading (draft)**: fit frequency ratio f_GHZ/f_product; PASS if ratio ∈ 3 ± 0.15 with
both contrasts > 0.5 postselected. **Named failure**: GHZ contrast decays faster than slope gain at
this depth (the standard metrology trade-off) — then the honest result is the measured contrast-vs-
slope frontier, our first quantitative metrology bound.

**Cost**: one job ≈ **70–100 s** (most pubs of the set). Risk: MEDIUM-LOW (219 flew; the dial is 1q
gates only).

---

## 6. P5 — THE UNIVERSAL TRANSLATOR (mid-circuit code conversion)

**Claim**: a state that *translates* between protection languages mid-flight (bit-flip code through an
X-storm, then phase-flip code through a Z-storm) survives a two-storm gauntlet that kills both
fixed-code controls and the bare qubit.

**Implementation** (3 data qubits, static — repetition codes decode by majority in post-processing,
no dynamic circuits needed):
1. Encode logical |0⟩ (and |+⟩ row reported for honesty) in the bit-flip code (2 CZ).
2. **X-storm**: independent X-rotations R_x(ε) per qubit, ε calibrated to ~15% flip probability
   (engineered-noise machinery from H6).
3. **Translate**: majority-decode to one qubit (2 CZ) → immediately re-encode in the phase-flip code
   (2 CZ + 3 H). The seam is instantaneous (no idle inserted); the storms happen only while encoded.
4. **Z-storm**: R_z(ε') per qubit at matched strength.
5. Decode + measure. **Arms**: translated / stay-bit-flip / stay-phase-flip / bare, each through the
   identical two-storm sequence + no-storm calibration of each. ≈ **10 pubs × 8,000 shots**; ≈ 8 CZ.

**Grading (draft)**: PASS if F(translated) − max(F(stay-bit), F(stay-phase), F(bare)) > 5·se.
Predictions: stay-bit dies in the Z-storm, stay-phase dies in the X-storm, translated survives both at
the product of two single-code survivals. **Named failure**: the translation seam (4 CZ + the moment
of bareness) costs more than a storm — the measured "conversion tax," directly relevant to any future
code-switching architecture. **Cost**: one static job ≈ **40–60 s**. Risk: LOW.

---

## 7. P6 — WARP FIELD CARTOGRAPHY (the attenuation law) — $0, software only

**Claim**: one fitted decay constant per device explains the record's signal attenuation vs transpiled
2q depth, and *predicts* every future die/platform's witness before it flies.

**Implementation** (no QPU):
1. `tools/attenuation_map.py`: harvest tuples (experiment, device, date, observable, ideal value,
   measured value, transpiled 2q count) from `results/*.json` + STATUS docs — the record holds 30+
   usable points (bare switch W, shielded DISC family, distributed-gate discs, dial curves, the
   multi-substrate three platforms).
2. Fit signal = ideal · e^(−λ·d₂q) per device (and test the alternative: per-gate-error-weighted depth
   from calibration data of the flight day, where archived).
3. Grade retroactively: does the fez λ predict Rigetti's 1.2165 from its budget (the C4937 miss, now
   quantified)? Report residual structure honestly (readout floor, 1q contribution).
4. Output: `results/attenuation_map.json` (the star chart) + a standing rule: **every future
   pre-registration quotes the map's predicted value with its CI as the pre-filed prediction** — every
   flight thereafter grades the map for free.
**Named failure**: no single-λ fit survives the residuals (depth alone under-determines) — then the
map's honest form is a bounded band, which still disciplines predictions. **Cost: $0. Risk: none.**

---

## 8. Budget, schedule, and flight order

| flight | pubs | mode | est. QPU-s | risk |
|---|---|---|---|---|
| P7 Adaptive Helm | ~12 | dynamic | 50–90 | LOW |
| P2 Cloaking Device | ~16 | static | 40–60 | LOWEST |
| P1 Self-Prescribing Shield | ~14 (+mini-scan) | static | 60–90 | LOW-MED |
| P5 Universal Translator | ~10 | static | 40–60 | LOW |
| P3 Pattern Buffer | ~12 | dynamic | 60–90 | MED |
| P4 Shielded Tricorder | ~20 | static | 70–100 | MED-LOW |
| P6 Cartography | 0 | software | 0 | none |
| **Phase-1 total** | | | **≈ 320–490 s** | |

**Budget policy (proposed)**: cap H7 phase 1 at **600 s** (≈ 15% of the remaining 4,109 s), leaving a
≥ 3,400 s reserve for the remaining ~12 months of the annual period. At the July burn rate the pool
dies in a week; H7 is deliberately a **low-burn, high-composition** arc. One flight per cycle, graded
before the next flies; any NOT-HELD stops the arc for re-planning rather than re-flying.

**Order**: P6 (free, immediately) → P7 (cashes the 241b discovery) → P2 (cheapest certification) →
P1 → P5 → P3 → P4. Each flight: its own frozen pre-registration (bounds above are drafts, frozen
per-flight), sim-verification pre-spend (density-matrix where applicable), pinned layout, all-bit
grading, syndrome-stream archival + 241b analysis on every dynamic job.

**Cross-platform options (separate Creator gate, Braket $)**: P2 and P5 are static and shallow —
portable to Rigetti for ~$5–15 each as cross-vendor replications; scientifically nice-to-have, not
required for any H7 claim. IonQ not needed for H7.

## 9. What could block us (stated plainly)
1. **Quota exhaustion by other work** — the only real hardware risk; the plan's own draw is <15%.
2. **Dynamic-circuit classical-logic limits** (P7 Rule B, P3): conditions are pairwise-simple by
   design; fallback for P7 is precompiled branch pairs (condition on syn{r} only, memory applied via
   post-selected analysis of the recorded stream — weaker but still graded).
3. **Drift between calibration and flight** (P1): mitigated by the same-window mini-scan.
4. **Nothing requires**: Eagle, distance-3 codes, >7 qubits, Braket, or any capability outside our
   already-certified set.

---

# ADDENDUM v2 (C4950) — gap review + pre-dev planning structure

## A. Gap review (fresh-eyes pass, with two live fact-checks)

| # | gap | resolution |
|---|---|---|
| G1 | **`switch_case` does not exist on Heron** (verified live: fez/marrakesh targets expose only `if_else` + measure/reset). The P7 "16-case switch" fallback is fiction. | P7 memory rules rebuilt as **nested constant-condition `if_else`** (for v ∈ {01,10,11}: if syn_prev==v → if syn_cur==v → correct). One nesting level beyond Exp241. **Pre-dev gate PD-3 (compile check) is now MANDATORY before the P7 pre-reg freezes.** |
| G2 | **P7 has an unflown $0 phase nobody noticed.** A *decoder* comparison needs no in-circuit adaptation: measure syndromes, never fix, decode offline — memory-aware vs memoryless decoding on the SAME shots. Exp241's sham arm already recorded exactly this (syn0..syn3 + final readout). | New **P7.0 (offline decoder study, $0, data in hand)**: run both decoders on the existing 241 sham streams first. It de-risks (or pre-demonstrates) the claim; the flight then tests the *in-circuit* adaptive version, which is the stronger real-time statement. |
| G3 | **P7 statistical multiplicity**: two rules vs control = two comparisons. | The PD-2 Monte-Carlo (and P7.0) pick ONE primary rule pre-flight; the other becomes exploratory. Pre-reg states primary/secondary explicitly. |
| G4 | **P7 decoder sim needs real noise parameters**, not guesses — 241b showed the stream is readout-noise-dominated (fire rates 0.37–0.65 ≫ physical rate). | PD-2 fits (ancilla readout error, per-round flip rate, memory term) from the EXISTING 241 data ($0) and feeds the Monte-Carlo. |
| G5 | **P1 frame algebra unverified**: conjugating the data qubits by a 1q Clifford frame changes which physical axis the fixed CZ parity map detects — the intended effect, but sign/axis errors are easy. | PD-1 density-matrix asserts with exact targets: ALIGNED arm silent-corruption reproduces the Exp216 transfer function at the chosen θ; PRESCRIBED arm detection-rate rises and postselected corruption falls, both to sim-predicted values ±0.02. |
| G6 | **P2 grading tests only 3 measurement axes** — an eavesdropper is not restricted to X/Y/Z. | Upgrade grading: reconstruct each single-qubit tomogram per logical state and bound the **Holevo χ** of the per-qubit ensemble (bounds EVERY measurement). PASS-CLOAK: max_q χ_q < 0.01 bit. Use Miller-Madow bias correction; note plug-in bias ~1e-4 bit at 8k shots (negligible vs threshold). Also pin the [[4,2,2]] second/gauge logical qubit to a fixed state so the 4 probe states differ ONLY in the probed logical bit. |
| G7 | **P2 readout error cuts both ways** (fake mixedness can hide a real leak). | Report raw AND readout-mitigated tomograms (mitigation matrix from the same job's calibration pubs, +2 pubs); grade on mitigated, report both. |
| G8 | **P3 layout is not a chain** — d0:=b1 with two ancilla branches needs a degree-3 subgraph (two branch points) on heavy-hex. | Builder gets a **subgraph-finding assert** (PD-1): find and pin a matching 7-qubit subgraph from the live coupling map; abort if the day's best-error subgraph doesn't exist. |
| G9 | **P3 frame bookkeeping through the code**: deferred X frame flips the majority-vote interpretation (fine); deferred Z frame is invisible to the bit-flip code but flips the \|+⟩ row's readout. | PD-1 aer assert: inject known teleport outcomes, verify the frame-corrected decode reproduces the ideal for all 3 input states before any spend. |
| G10 | **P4 logical-phase implementation undefined** — "Rz per node" must be the node-encoding's LOGICAL Z rotation, which depends on the Exp219 encoding detail. | PD-1 derives the per-node logical-Rz (which physical qubit(s) carry it) from the 219 builder and asserts cos(3φ) on aer before freeze. |
| G11 | **P4 fit fragility**: nonlinear cos fits can fail to converge and invite judgment. | Grading re-specified as **DFT amplitude ratio**: \|A₃\|/\|A₁\| from the 8-point φ sweep; PASS if GHZ ratio > 3 AND product ratio < 1/3 (clean, deterministic, no fit). |
| G12 | **P5 storms are coherent, not stochastic** — uniform R_x(θ) on all three qubits is a correlated coherent error; repetition-code behavior differs from iid flips. | Honest resolution: keep coherent storms, state the model, and pre-file **sim-predicted survival values** for all four arms (PD-1 asserts). The claim becomes "survives the coherent two-storm gauntlet," which the sim makes exact. |
| G13 | **P6 heterogeneous observables** (W, DISC, F, S have different ideals and decay characters). | Inclusion rule: primary fit on the **DISC/W family only** (~15 points, one observable class); fidelity-family fitted separately as exploratory. Day-level scatter absorbed into the reported CI, not hidden. |
| G14 | **No experiment numbers assigned** (numbering collision risk — the R2 retro lesson). | Assigned now: **P7→Exp247, P2→Exp248, P1→Exp249, P5→Exp250, P3→Exp251, P4→Exp252** (P6 is software, no number; P7.0 files as finding-exp241c). |
| G15 | **Standard flight sequence omitted** coordination + quota discipline. | Baked into the per-flight sequence (D below): coordination_check + `ps aux` (C4038), live quota read before submit, usage recorded after, accounting doc updated. |

## B. Pre-dev standard form (applies to every flight; instantiated per program)

1. **Builder**: one script per experiment (`experiments/exp24N_*.py`) exposing `build()` (all pubs,
   labeled), `--scan` (free local run), `--submit` (guarded), following `braket`/`switch_bench`
   conventions: handles persisted before blocking, background submission, single job per flight.
2. **In-code asserts (run at build time, abort on fail)**: pinned-layout subgraph exists on the live
   coupling map; post-transpile 2q count == plan value ± 0; every classical register enumerated with
   its pre-registered prediction (the all-bit table generated, not hand-written).
3. **Free validation gates (all $0, all BEFORE the pre-reg freezes)**:
   - **PD-1 sim-exactness**: aer/density-matrix run of every pub; assert primary observables hit ideal
     values (and, where noise is injected, hit sim-predicted values) within stated tolerance.
   - **PD-2 parameterized decoder/noise Monte-Carlo** (P7 only): noise parameters fitted from existing
     241 data; picks the primary memory rule.
   - **PD-3 dynamic-logic compile check** (P7, P3): transpile the exact nested `if_else` structure for
     the flight backend; assert it compiles and aer-simulates to correct semantics. G1 made this
     mandatory — `switch_case` does not exist on Heron.
   - **PD-4 offline pre-study on existing data** where the record allows (P7.0 on 241 sham streams;
     P6 entirely).
4. **Pre-registration freeze**: bounds from the plan's draft tables + PD-1/PD-2 outputs; named failure
   modes; pre-filed prediction with confidence; committed BEFORE submission (hash quoted in RESULTS).
5. **Flight**: one job, all pubs; background submit; manifest/job-id persisted pre-block.
6. **Grading**: grader implemented and frozen WITH the builder (not written post-data); primary /
   secondary split explicit; syndrome streams archived and 241b-analyzed on every dynamic job;
   substrate stamped.
7. **Artifacts**: `results/exp24N_*.json` (card + full counts), `experiments/exp24N-STATUS-*.md`,
   finding file if a claim certifies or a named failure fires; accounting doc updated with measured
   job seconds.

## C. Per-program pre-dev instantiation

| exp | program | PD gates required | builder core | key asserts |
|---|---|---|---|---|
| — | P6 cartography | PD-4 | `tools/attenuation_map.py` | schema-complete tuples; DISC-family inclusion rule; fit CI reported |
| 241c | P7.0 offline decoders | PD-4 (+PD-2 params) | `tools/exp241c_offline_decoders.py` | identical shots both decoders; primary rule selected |
| 247 | P7 adaptive helm | PD-1,2,3 | `exp247_adaptive_helm.py` | nested if_else compiles on fez; Monte-Carlo winner = primary; 2q=4/round |
| 248 | P2 cloak | PD-1 | `exp248_cloak.py` | gauge qubit pinned; Holevo grader unit-tested on synthetic tomograms; mitigation pubs present |
| 249 | P1 EMH shield | PD-1 | `exp249_emh_shield.py` | frame conjugation reproduces 216 transfer function in sim; mini-scan pubs in-job |
| 250 | P5 translator | PD-1 | `exp250_translator.py` | 4-arm sim-predicted survivals pre-filed; seam = 4 CZ verified post-transpile |
| 251 | P3 pattern buffer | PD-1,3 | `exp251_pattern_buffer.py` | 7q subgraph found+pinned; frame bookkeeping aer-verified; 18 CZ |
| 252 | P4 tricorder | PD-1 | `exp252_tricorder.py` | per-node logical-Rz derived from 219 builder; DFT grader unit-tested |

## D. Per-flight sequence (the operational checklist, every flight)
(1) coordination_check + `ps aux` (C4038) → (2) live quota read (abort if < 1000 s remaining unless
Creator-cleared) → (3) builder asserts + all PD gates green → (4) freeze pre-reg, commit → (5) submit
background, persist handle → (6) grade with the frozen grader; 241b stream analysis if dynamic →
(7) STATUS + finding + accounting update, commit → (8) next flight only after this one is graded.

## E. Revised immediate actions on Creator go
1. **P6 + P7.0 together, $0, no pre-reg spend risk** — cartography build + offline decoder study on
   existing 241 data. Their outputs (attenuation map; primary memory rule) feed every later freeze.
2. **Exp247 (P7)**: PD-2/PD-3 gates, then freeze, then the first H7 flight.
