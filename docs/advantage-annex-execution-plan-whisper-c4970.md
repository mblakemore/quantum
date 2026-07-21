# Advantage Annex — Execution Plan for Items 2–5 (with friction-reduction layer and Round-2 gap review)

*Whisper C4970, 2026-07-21, substrate claude-fable-5. Creator directive: "create a detailed execution
plan for 2–5 with tips to reduce friction, then revisit that plan for gaps and pre-execution planning
structure." Items numbered per the [annex](advantage-annex-unconventional-paths-whisper-c4969.md)
recommended order: **2** classical cost map · **3** hidden-shift $0 scout · **4** the race flight ·
**5** two-copy self-certification (stethoscope). Item 1 (booking) was delivered this same cycle
(README + complete-answer + campaign-arcs, quantum@ this commit).*

*Structure: §A per-item plans (Round 1) · §B friction-reduction layer (drawn from the campaign's own
friction reports + the Exp142/144 process record) · §C **Round 2 — the gap review** (what a second
pass found wrong or missing in §A, kept visible rather than silently merged) · §D the standing
pre-execution PREP-card template that generalizes this planning structure.*

---

## §A — Per-item execution plans (Round 1)

### Item 2 — The Classical Cost Map (`P-CCM`) — $0 QPU, pure classical metering

**Claim shape**: an instrument, not an advantage claim. Output: frozen cost curves
CPU-seconds & joules per *verified* solution vs (n, T-count, bond dimension χ), per named solver, on
named hardware. Makes every future crossover statement computable and falsifiable.

**Phases**
1. **Metering harness** (`tools/classical_cost_meter.py`): wall + process CPU time
   (`perf_counter` + `psutil`), memory peak, and energy via RAPL
   (`/sys/class/powercap/intel-rapl/*/energy_uj`) with a documented fallback (TDP × busy-time upper
   bound, labeled `energy_bound_not_measured`) if RAPL is unreadable. Hardware fingerprint (CPU
   model, core count, RAM, governor) stamped into every row.
2. **Solver bench**: three classes, correctness-gated before any timing —
   (a) statevector (Aer), (b) **stabilizer-rank / extended-stabilizer** (Aer `extended_stabilizer` +
   a survey pass for a stronger open implementation — see §C gap G1), (c) MPS (Aer `matrix_product_state`,
   χ swept). **Correctness gate**: each solver must reproduce the known planted answer / exact
   amplitudes on small verifiable instances before its timings enter the map (a fast wrong solver
   poisons the map — the Exp144 detector lesson applied classically).
3. **Instance generator**: the hidden-shift family (shared with Item 3 — one generator, two
   consumers), the HLF family (F113 receipts as cross-check), and a random-Clifford+T control.
4. **Sweep + fit**: log-cost vs n (statevector), vs T (stabilizer-rank), vs χ (MPS). Censored fits
   for timeouts (record `>cap`, never drop). Both single-thread and all-core configs metered; the
   race config (Item 4) is declared here, in advance.
5. **Card**: `results/classical_cost_map_v1.json` + a short doc, same freeze discipline as the
   attenuation map — future races *quote* it, and each race grades the map's prediction for free.

**Roles**: Whisper builds; Elder red-teams the fits + correctness gates; Ember replicates 3 sampled
rows on a second machine (machine-relativity check — if her numbers differ beyond the declared
hardware delta, the card gains a variance column, not a dispute).

**Estimated effort**: 2–3 cycles. **Budget**: $0 QPU; CPU-hours capped (per-row timeout 10 min,
sweep cap ~6 CPU-hours v1).

### Item 3 — Hidden-Shift $0 Scout (`P-HSS`) — the go/no-go for the race

**Claim shape**: a feasibility verdict with both cost curves on one plot. No QPU. Either verdict is
a deliverable (GO → flight design frozen; NO-GO → the measured gap between the peak-survival
frontier and the classical-minutes frontier, the computational twin of F54's wall number).

**Phases**
1. **Generator** (`experiments/exp_hss_generator.py`): Maiorana–McFarland bent-function pairs with
   planted shift s; hardness dial = count of cubic monomials (each → CCZ → T-count via chosen
   decomposition). Self-check: noiseless sim returns s with probability 1 at every dial setting
   (exactness gate — Simon/Exp145 style self-verification).
2. **Depth pricing**: transpile the family to `ibm_fez`/`ibm_marrakesh` at n ∈ {16, 24, 32, 40} ×
   T ∈ {0 (Clifford control), 14, 28, 48, 70}; record routed 2q-count/depth per CCZ-decomposition
   variant (enumerate 2–3 variants, keep the Pareto-optimal). `seed_transpiler` pinned.
3. **Peak-survival prediction**: λ_eff map → predicted peak retention; FakeFez sim per rung with the
   **measured** noise-model-optimism correction band applied (friction 01: the fake is optimistic at
   depth — the prediction interval must carry that band, not the raw sim number).
4. **Classical bill**: the same instances priced by the Item-2 map (stabilizer-rank curve vs T).
5. **The two-curve plot + frozen decision rule** (pre-committed *before* computing either curve):
   GO iff ∃ (n, T) with predicted peak detectable at ≥5σ over the strongest non-planted mode
   (FWER-corrected over the 2ⁿ candidate space) **and** classical bill ≥ 10 minutes on the declared
   race config. Else NO-GO + publish the gap.

**Roles**: Whisper builds + prices; Elder independently recomputes the classical-bill column;
Ember re-runs the peak-survival sim from the frozen generator (2-of-2 on both curves).

**Estimated effort**: 2 cycles after Item 2's map exists (the classical column depends on it).

### Item 4 — The Race Flight (`P-HSR`) — QPU, gated on Item 3 GO

**Claim shape**: an engineering runtime race vs named classical software on named hardware —
**supersedable by design** and said so (the Tracker's own mechanism); *not* a supremacy claim. The
deliverable is the measured crossover map with both sides metered, whatever it shows.

**Phases**
1. **Pre-registration** (frozen pre-submission, per house rule): instances (K ≥ 3 per rung — the
   Exp144 error-bar lesson; Exp142's one-instance-per-rung caveat not repeated), shots, layout via
   quiet-qubit picker, sentinel co-batched in-job (friction 03: window quality gated by our
   sentinel, not the vendor's calibration feed).
2. **Blindness**: planted s sealed per the Exp142 commitment machinery (Ember seals, salted hash
   committed pre-flight). Structural fence stated plainly: the circuit *encodes* s, so author-level
   blindness is partial by construction — the protocol is the set of things we refuse to leave to
   character: generator consumes the sealed seed mechanically, no seat inspects s, detection
   statistic frozen, reveal-then-grade.
3. **Metering protocol** (frozen): QPU side = job execution seconds (usage-reported), with queue
   and wall time disclosed separately, never mixed; classical side = Item-2 race config, run by a
   seat that did not build the quantum arm. Energy: classical joules measured (RAPL);
   QPU joules reported only if vendor-published, else the column reads `not published` (no
   fabricated estimates).
4. **Grading**: mode-of-shots == s per instance (the Exp145 self-verification pattern); frozen
   grader with negative controls that have been *seen to fail* (a guard never seen to trip is a
   hope); 2-of-2 independent decode; prediction pre-filed with all three outcomes named (quantum
   wins a region / classical wins everywhere in reach / peak dies — each citable).

**Roles**: Whisper chair + builder; Ember seal + submit; Elder decode + grade + classical-arm meter.
(The Exp142/144 three-seat structure, reused as-is — it worked.)

**Estimated effort**: 2–3 cycles + queue time. **Budget**: est. 30–90 s QPU (shots are modest;
width is the resource) — re-verify live quota pre-submission.

### Item 5 — Two-Copy Self-Certification (`P-STETH`) — the advantage pays its own bill

**Claim shape**: (a) a measured sample-complexity ratio for learning *the chip's own* Pauli channel
with entangled probes vs the executed conventional probe-measure arm, same window; (b) a retrofit:
one existing certification workload re-implemented two-copy, with measured shot savings.

**Phases**
1. **Gate-1 theorem pin** (blocking): the process-learning separation's exact conditions pulled from
   the papers (CCHL process-learning results), pinned in the pre-reg — *from the papers, not
   memory* (house rule; the Exp144 chair review caught exactly this class of error at R2).
2. **Design scout ($0)**: pick the target channel + input states so the two-copy signal is strong —
   the Exp144-R1 lesson is the hazard here (near-maximally-mixed targets kill Bell-sampling SNR);
   model probe noise including the ancilla tax (F06) — if the tax eats the advantage at our
   fidelities, that number is the finding and the flight is redesigned or reported, not forced.
3. **Flight**: entangled-probe channel-eigenvalue estimation vs conventional arm, co-batched, same
   window; ratio with CIs.
4. **Retrofit deliverable**: a named existing grader block (candidate: the Bell-pair tomography
   block of the F105-class certifications) re-implemented via destructive two-copy overlap test;
   measured shot-bill delta on a re-run.

**Roles**: Whisper design + chair; Elder theorem pin co-check + grade; Ember flight + blind where
applicable. **Effort**: 3–4 cycles, gated behind Exp144's post-mortem learnings. **Order note**:
runs *after* Items 2–4 or in parallel gaps; independent of the cost map.

---

## §B — Friction-reduction layer (from the campaign's own receipts)

**Hardware/model frictions** (the five filed friction reports, applied per item):
- **01 FakeMarrakesh depth-optimism** → every sim prediction carries the measured optimism band;
  stratified sentinels in-job (Items 3, 4, 5).
- **02 Published-T1 bias** → place by published, grade by measured; calib arms sized from live data
  (Items 4, 5).
- **03 Calibration-blind window quality** → sentinel co-batch in the same job, gate trust on it,
  report conditional AND unconditional (Item 4).
- **04 Dynamic conditional polarity / 05 fake feedforward zero-latency** → not applicable to Items
  2–4 (static circuits); applies to Item 5 only if a feedforward variant is used — check at design.

**Process frictions** (the Exp142/144 record, distilled to standing rules):
1. **Late-bind every constant** (c4187_001): drivers read frozen kits at call time; a hardcoded
   copy passes its own tests and flies stale.
2. **One serializer, explicit signatures**: producer/consumer file schemas drift silently
   (Exp142 wave-1 void); pass data as function arguments where possible; where files are
   unavoidable, run the **path-matrix gate against the real frozen consumer**, not a reference
   reimplementation.
3. **Dry-runs must exercise the submit path's imports** (Ember's Exp144 catch): a dry-run that
   returns before the submit branch proves everything except what only runs when it matters.
4. **Guards must be seen to fail**: every blindness/overwrite/refusal guard gets a forced-failure
   test before it's trusted.
5. **Refuse-on-overwrite + attempt tags** for manifests: deviations stay visible (Exp142 discipline
   — failures remain in the record).
6. **2-of-2 independent decode** on anything sealed; hold flights at the gate until both seats land
   (the 3.7h Exp142 wave-5 hold was the system working).
7. **Config-class overrides on frozen kits** are legitimate only with disclosure + pre-flight hash
   re-verification (the A5 ruling); code-path changes are never config-class.
8. **Meter the classical arm with quantum-arm rigor** (the Exp144 NOT-WIN root cause): the
   conventional detector gets its own truth-gate, red-team, and a pilot rung before freeze.
9. **Decide the claim's venue/shape before freezing** (C4762): sample-complexity vs runtime-race vs
   instrument — the fences write themselves once the shape is explicit.
10. **Book results into the synthesis docs at landing** (the C4969 scoreboard-lag lesson): the
    landing checklist ends with "arcs + scoreboard updated", not with the grade.

---

## §C — Round 2: the gap review (second pass over §A, kept visible)

Re-reading §A cold, these are the holes found and the fixes now incorporated above or flagged:

- **G1 — The classical adversary must not be a strawman (Item 2/4, severity: claim-invalidating).**
  Aer's `extended_stabilizer` is not the state of the art for Clifford+T simulation at T ≈ 48; the
  literature's stabilizer-rank methods (Bravyi–Gosset lineage) are stronger. Racing only Aer would
  overstate the quantum side. **Fix**: Item 2 phase 2 now includes a survey-and-adopt pass for the
  best available open implementation; if none is adoptable, the classical bill is quoted as a
  **lower bound calibrated to published scaling, labeled as such**, and the race claim weakens
  accordingly (stated in the pre-reg, not discovered by a referee).
- **G2 — QPU energy is not measurable by us (Item 4).** Vendor does not publish per-job energy.
  **Fix**: the energy column is asymmetric by declaration — classical joules measured, QPU joules
  `not published` — and no derived "quantum energy advantage" claim is permitted from an
  asymmetric column. (Original §A draft implied a two-sided energy race; corrected.)
- **G3 — Conflict of interest in race metering (Item 4).** The quantum-arm builder must not meter
  the classical arm. **Fix**: Elder meters classical (now in §A roles).
- **G4 — Structural blindness limit (Item 4).** Unlike Exp142 (state prep from sealed b), the
  hidden-shift *circuit* encodes s — full author-blindness is impossible. **Fix**: mechanical
  generator from sealed seed + frozen detection statistic + the fence stated in the pre-reg, per
  the Exp144 "protocol = what we refuse to leave to character" principle. A reviewer must see the
  limit before seeing the result.
- **G5 — Axis honesty (Item 2).** "Treewidth" in the annex was loose: the MPS cost axis is bond
  dimension χ (entanglement), not graph treewidth. Corrected throughout §A.
- **G6 — Dependency ordering.** Item 3 needs Item 2's stabilizer-rank column only; a partial map
  (rank curve first) unblocks the scout ~1 cycle earlier. Incorporated: Item 2 delivers the rank
  curve as v0.5 before the full card.
- **G7 — Missing kill-criteria symmetry (Item 5).** §A named the ancilla-tax hazard but no numeric
  kill-gate. **Fix**: the design scout must show the modeled two-copy arm beating the conventional
  arm by ≥3× at our measured fidelities before any pre-reg is written; below that, publish the
  negative scout as the finding.
- **G8 — No detection-statistic FWER spec had been written down (Items 3/4)** — "peak == s" over 2ⁿ
  outcomes needs the frozen mode-vs-runner-up statistic with family-wise correction; now explicit
  in Item 3 phase 5 / Item 4 phase 4.
- **G9 — Grader-selftest rule**: every new grader ships with a selftest that must pass before
  hardware grading (the R5 rule F92 flew under) — §A assumed it implicitly; PREP card (§D) makes
  it a named line so it cannot be skipped by being obvious.

## §D — The standing PREP card (pre-execution planning structure, reusable)

Every item above — and every future flight — freezes this one-page card *before* building:

```
PREP — <experiment id / name>
1. CLAIM SHAPE      instrument | sample-complexity | runtime-race | certification
                    + venue fence decided NOW (C4762 rule)
2. ROLES            builder / seal-submit / decode-grade-meter (no seat meters what it built)
3. GATES            G-1 theorem/conditions pin (from papers, not memory)
                    G-2 power & feasibility (measured-noise; optimism band applied)
                    Truth-gate: noiseless exactness + falsifiability + guards-seen-to-fail
                    Grader selftest (R5) before any hardware grading
4. FROZEN ARTIFACTS kit + hashes; late-bound constants listed; serializer single-sourced;
                    path-matrix gate vs real consumer if files cross seats
5. FRICTION SWEEP   the §B checklist walked line-by-line, N/A entries written as N/A
6. PREDICTION       pre-filed w/ confidence + ALL outcome branches named (each citable)
7. KILL / ABORT     numeric go-no-go, pre-committed before either side's curve is computed
8. BUDGET           QPU seconds est. + live quota check; CPU-hours cap; queue plan
9. BLINDNESS        seal protocol + structural limits stated (what cannot be blinded, and why
                    that is disclosed rather than papered over)
10. LANDING         grade → book into arcs/scoreboard/README same session → post to network →
                    grade the map/model predictions the flight carried for free
```

*The card is the §C gap review turned into structure: G1–G9 each map to a numbered line, so the
next plan starts where this one's second pass ended.*

---

*Execution order: Item 2 (start now, $0) → Item 3 (GO/NO-GO, $0) → Item 4 (only on GO) → Item 5
(gated on its own scout). Booking (Item 1) landed this cycle. Every flight through the PREP card;
every landing through line 10. Contact: Mike Blakemore (§12, H7 synthesis).*
