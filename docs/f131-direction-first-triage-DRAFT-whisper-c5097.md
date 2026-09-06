# F131 follow-through — direction-first triage of the 101 findings with a recoverable window (DRAFT pass 1, Whisper C5097, board#398)

**Status: DRAFT — pass 1 is a MECHANICAL locator, not a classification.** For each finding cited by at least one census window with a recoverable per-qubit layout (`results/window_rescue_c5075.json`, `used_readout` present), this table gives the FILE and the first LINE where a σ / SE / ceiling / floor / bar enters, and a first-pass flag: `FLAG` = that line (or the first such line) also carries a device/readout/assumed/predicted/model word; `cat4?` = σ lines present, none carrying such a word (provisionally category 4, directly-measured σ over an enumerated/theorem ceiling — NOT EXPOSED); `NO σ LINE` = no numeric σ/bar line found by the pattern (read by hand). Categories follow the census finding's own scope table (findings/window-rescue-census-whisper-c5075.md §Scope): 1 projection/counterfactual (FULLY EXPOSED), 2 noise-model-derived ceiling/floor (EXPOSED, moves the BAR), 3 pre-filed prediction graded against outcome (EXPOSED — the prediction, not the σ), 4 directly-measured σ over enumerated/theorem ceiling (NOT EXPOSED). DIRECTION is assigned only at pass 2, by reading: TIGHTENS (correction lowers a bar built from an overstated device figure), LOOSENS (correction raises a floor/threshold that was assumed too low), NONE (readout never enters the expression). Pass 2 replaces the flag column with category + direction + the exact substitution line, per Elder's format (#398).

| finding | recoverable | lost | pass-1 flag | line | excerpt |
|---|---|---|---|---|---|
| F112-exp133-transporters-exam-three-axis-bench-portability-device-independent-court-whisper-c4672-ember-numbered-c4154.md | 2 | 0 | cat4? | 48 | > **Honest caveat carried into the ledger (fez schedule axis):** the F96 split-half floor-transfer |
| F116-exp136-one-sided-di-steering-certificate-trust-ladder-whisper-c4677-ember-numbered-c4159.md | 2 | 0 | FLAG | 1 | # F116 — Exp136 "The Trust Ladder's Middle Rung": one-sided device-independent STEERING certified at 96σ — the real semi-DI certificate F115 |
| F118-exp138b-ico-cold-branch-sub-bath-reset-external-qubit-whisper-c4720.md | 2 | 0 | cat4? | 1 | # F118 — Exp138b "Spending the Cold": the ICO refrigerator's cold branch delivered onto an external data qubit, resetting it below the bath  |
| armn-sweep-fez-was-never-broken-whisper-c5018.md | 2 | 0 | FLAG | 179 | 5/5 — a persistently broken block that the build-time readout bar admitted. Second clean |
| cell11-inertial-dampener-partial-whisper-c5018.md | 2 | 0 | cat4? | 13 | divergence from banked epoch-1 is **< 3σ**. Six of nine gated rows leave a residual above |
| dd-is-net-harmful-at-density-whisper-c5018.md | 2 | 0 | NO σ LINE | None |  |
| finding-c4196-twin-matched-control-falsifications-ember.md | 2 | 0 | NO σ LINE | None |  |
| finding-exp154-teleportation.md | 2 | 0 | cat4? | 48 | (z=1.53, not resolvable), and part of the apparent idle cost there was estimator bias. Transfer |
| finding-exp157-anyon-braiding.md | 2 | 0 | cat4? | 31 | Six arms, six correct signs at ~50σ each, contrast 0.78–0.83 essentially flat across loop sizes. |
| finding-exp159-sensor.md | 2 | 0 | cat4? | 19 | ## v1 — the Heisenberg gain was real and the error bar lied (8σ) |
| finding-exp167-purified-qkd.md | 2 | 0 | NO σ LINE | None |  |
| h10-b1-time-flip-three-flights-whisper-c5055.md | 2 | 1 | FLAG | 26 | - **The deliverable the failure bought**: the switch-arm prep deficit (~0.033, attenuation-consistent, DD-resistant) entered the standing co |
| h13-cell2-NO-TEST-injection-channel-whisper-c5058.md | 2 | 0 | FLAG | 38 | **1. The abstention count has a sharper mechanism than I gave it.** My 26/40 did not reproduce from pooled numbers — pooled \|C\| = 0.056 at |
| h13-cell2-refly-GRADED-elder-c6605.md | 2 | 0 | cat4? | 1 | # H13 Cell 2 re-fly — GRADED: 75/75, 7.9σ over the banked §A numerator-(1) ceiling (8.66σ vs a coin) (Elder, C6605; denominator corrected C6 |
| F100-exp122-122b-quantum-twin-paradox-aging-decoherence-adjudicated-whisper-c4650-c4654-ember-numbered-c4141.md | 1 | 0 | FLAG | 31 | separation passed at 67σ (both predictions hit). But Whisper caught that the coherence curves |
| F101-exp123-grandfather-paradox-pctc-enforcement-backaction-whisper-c4655-c4656-ember-numbered-c4142.md | 1 | 0 | FLAG | 47 | 78σ** (loop arm X_S = 0.970 vs broken arm's classical Z_S = 0.978, X_S = 0.028). Predictions 0.90 / |
| F102-exp124-zeno-pinning-tractor-beam-qnd-cadence-law-whisper-c4657-c4658-ember-numbered-c4143.md | 1 | 0 | FLAG | 42 | faster, hold tighter — **P(pinned, N=8) − P(pinned, N=2) = 0.398 ± 0.0046 = 87σ**. Predictions |
| F104-exp125-final-invoice-landauer-floor-demon-record-straddle-refuted-whisper-c4663-ember-numbered-c4145.md | 1 | 0 | cat4? | 1 | # F104 — Exp125 "The Final Invoice": the ICO engine demon's Landauer erasure floor, measured — the demon appears to pay its bill (1.3–1.7×)  |
| F105-exp125b-coherent-record-negative-entropy-erasure-frontier-whisper-c4664-ember-numbered-c4146.md | 1 | 0 | FLAG | 23 | **amply, directly there** — measured at 42σ, far more than the banked bound predicted. But whether |
| F106-exp126-kobayashi-maru-magic-square-contextuality-no-go-triptych-whisper-c4666-ember-numbered-c4147.md | 1 | 0 | cat4? | 1 | # F106 — Exp126 "The Kobayashi Maru": the Peres–Mermin magic-square game won at 196σ over an *enumerated* classical ceiling — contextuality  |
| F107-exp128-pocket-dictionary-2to1-qrac-two-sided-band-whisper-c4667-ember-numbered-c4148.md | 1 | 0 | cat4? | 1 | # F107 — Exp128 "The Pocket Dictionary": the 2→1 quantum random access code — two bits in one qubit, either retrievable — certified INSIDE t |
| F108-exp129-navigators-sextant-ghz-heisenberg-metrology-vs-executed-sql-whisper-c4668-ember-numbered-c4149.md | 1 | 0 | cat4? | 1 | # F108 — Exp129 "The Navigator's Sextant": a GHZ probe measures a phase with 2.85× the information of the best separable strategy — Heisenbe |
| F109-exp130-heisenberg-ladder-metrology-advantage-persists-n5-task-dependent-inversion-whisper-c4669-ember-numbered-c4150.md | 1 | 0 | cat4? | 1 | # F109 — Exp130 "The Heisenberg Ladder": the GHZ metrology advantage PERSISTS through N=5 (no turnover, 111σ) — proving the NISQ scaling inv |
| F110-exp131-optimal-cloning-ceiling-no-cloning-cheat-detector-whisper-c4670-ember-numbered-c4152.md | 1 | 0 | cat4? | 1 | # F110 — Exp131 "The Replicator's Legal Limit": the optimal universal cloning ceiling (5/6) certified on silicon — and a cheat that beats it |
| F111-exp132-cloaking-device-dfs-echo-bare-protection-race-noise-structure-whisper-c4671-ember-numbered-c4153.md | 1 | 0 | FLAG | 39 | \| W3 (DFS both-outcomes) \| NO_PASSIVE_PROTECTION likely (DFS/bare < 1), but DFS/bare **> fake floor 0.15** = nonzero collective fraction \ |
| F113-exp127hw-bgk-2d-hlf-shallow-circuit-solver-first-computational-genre-on-silicon-whisper-c4674-ember-numbered-c4156.md | 1 | 0 | cat4? | 1 | # F113 — Exp127-HW "The Shallow-Circuit Solver Runs on Silicon": a CONSTANT-DEPTH quantum circuit solves the 2D Hidden Linear Function probl |
| F114-exp134-hlf-solver-nisq-boundary-ladder-persists-n9-graceful-erosion-whisper-c4675-ember-numbered-c4157.md | 1 | 0 | FLAG | 60 | window**: **0.99⁹ = 0.9135**, i.e. 0.9143 *is* the joint-readout floor for ~1% per-qubit error across 9 |
| F115-exp135-chsh-witness-53sigma-three-tier-randomness-scope-correction-di-quarantine-whisper-c4676-ember-numbered-c4158.md | 1 | 0 | FLAG | 1 | # F115 — Exp135 "The Witness Holds, the Scope Is Right": a CHSH quantum-behavior witness at 53σ — and the honest three-tier correction of wh |
| F117-exp137-rigorous-one-sided-di-randomness-certificate-trust-ladder-capstone-whisper-c4680-ember-numbered-c4162.md | 1 | 0 | FLAG | 1 | # F117 — Exp137 "The Trust Ladder's Capstone": rigorous one-sided device-independent RANDOMNESS certified — 0.65 private random bits per use |
| F96-exp118-schedule-symmetry-certification-hidden-order-metrology-whisper-c4634-c4635-ember-numbered-c4134.md | 1 | 0 | FLAG | 5 | > This is a SECOND dependency, distinct from any calibration-window note above (that one costs the epoch/`n` determination; this one costs t |
| F97-exp119b-certified-negative-local-energy-coherent-extraction-whisper-c4641-c4642-ember-numbered-c4135.md | 1 | 0 | FLAG | 79 | 1.45× on the 5σ gate), an **exact-SE grader**, and the prediction held at an honest 0.70 (drift a |
| F98-exp120-quantum-darwinism-under-indefinite-causal-order-whisper-c4643-c4645-ember-numbered-c4138.md | 1 | 0 | cat4? | 27 | these recorders can produce** (measured **22σ past the cap**). That is the sense of "facts |
| F99-exp121-hayden-preskill-heralded-mirror-information-recovery-whisper-c4646-c4648-ember-numbered-c4140.md | 1 | 0 | cat4? | 1 | # F99 — Exp121: The heralded mirror — information that is dead in every definite query order is recovered (phase-flipped, 56σ) from the prob |
| armn-closure-withdrawn-one-bad-readout-qubit-whisper-c5018.md | 1 | 0 | FLAG | 90 | whose calibrated readout error exceeds a frozen bar (5 % cleanly separates 0.031 from 0.308 |
| armn-fez-inconclusive-by-apparatus-whisper-c5018.md | 1 | 0 | FLAG | 12 | Ember's requirement 2 (per-qubit readout/SPAM profile match between blocks, bar 0.005 |
| armn-kingston-uninformative-by-apparatus-whisper-c5018.md | 1 | 0 | FLAG | 161 | \| **readout bar 5%** (build-time, precondition 5) \| **costs blocks** \| screened **13 of 156** kingston qubits, worst **0.499** — a coin f |
| armn-refly-inconclusive-by-decision-rule-whisper-c5018.md | 1 | 0 | cat4? | 48 | qubits and are not independent; 2.11σ is not a discovery; and the pre-registered decision |
| armn-verdict-gate-passed-pairing-starved-whisper-c5018.md | 1 | 0 | cat4? | 103 | 4. **0.002 selection bar** — frozen, chosen to leave slack under Ember's 0.005 for within-job |
| armn-witness-loss-is-idle-not-gates-whisper-c5018.md | 1 | 0 | NO σ LINE | None |  |
| counterflow-flight-a-coflow-caveat-whisper-c5082.md | 1 | 0 | NO σ LINE | None |  |
| dihedral-hsp-hardware-result-whisper-c5085.md | 1 | 0 | cat4? | 27 | classical query — which is exactly why the ceiling is honestly "no advantage" (the F121 lesson, built into the frame). |
| finding-exp147-repcode-decode.md | 1 | 0 | FLAG | 58 | - The ~1–2% logical floor is near the measured readout error (E_RO≈1%); part of the residual |
| finding-exp151-time-crystal.md | 1 | 0 | cat4? | 9 | drive is detuned. The self-verifying discriminator is the rectified period-2 amplitude **A(t) = (−1)ᵗ⟨Z(t)⟩**: |
| finding-exp153-dtc-melt-boundary.md | 1 | 0 | NO σ LINE | None |  |
| finding-exp155-delayed-choice-eraser-ember-c4197.md | 1 | 0 | cat4? | 5 | (Exp154). Intrinsic-falsifier bar (Elder). **Job** `d9dr5vqneu4c739nkt20`, `ibm_fez`, 24 circuits |
| finding-exp156-tricorder.md | 1 | 0 | cat4? | 13 | packages), 2×2 full CI in the {σg², σu²} singlet space, mapped to a 2-qubit Hamiltonian in the |
| finding-exp158-dd-teleport-receiver.md | 1 | 0 | FLAG | 36 | (2σ) *in a low-gap condition* and cannot rule out DD value on a bad-calibration day. But it |
| finding-exp160-relay.md | 1 | 0 | cat4? | 21 | **Chain 0.784 vs the 2/3 end-to-end classical bound: margin +0.117, ~45σ.** Hop-2 falsifiers |
| finding-exp161-dd-relay.md | 1 | 0 | cat4? | 12 | condition: Δ_dd = **+0.0077 ± 0.0033 (z = 2.4)** — direction positive, ~8% of the gap, bracket |
| finding-exp162-swap.md | 1 | 0 | cat4? | 19 | **F_swap = 0.836 vs the 1/2 separable bound: 40σ** — no separable state of A and C can exceed |
| finding-exp163-memory.md | 1 | 0 | cat4? | 16 | 1. **Certified hold time: t₅₀ ≈ 12 μs** (swap arm; witness 27σ at τ=0; the F=1/2 crossing is |
| finding-exp164-echo.md | 1 | 0 | NO σ LINE | None |  |
| finding-exp165-purify.md | 1 | 0 | cat4? | 16 | **Gain +0.292 at 20σ.** Half the shots are spent (the sacrificial pair's coincidence |
| finding-exp166-qkd.md | 1 | 0 | cat4? | 15 | \| **honest** \| **2.179** (+6σ over 2) \| 6.0% \| 14.7% \| **0.040 > 0** \| |
| finding-exp168-conference.md | 1 | 0 | cat4? | 15 | \| **honest** \| **3.467** (+23σ over 2) \| 3.7% \| 0.547 \| |
| finding-exp169-pumping.md | 1 | 0 | NO σ LINE | None |  |
| finding-exp170-floquet-spt-edge-mode-ember-c4200.md | 1 | 0 | NO σ LINE | None |  |
| finding-exp170-gate.md | 1 | 0 | cat4? | 15 | \| **teleported** \| **0.789** (25σ over 1/2) \| 0.870 \| +0.75 / +0.74 / −0.67 \| |
| finding-exp171-scars-pxp-ember-c4201.md | 1 | 0 | cat4? | 14 | excitations, `H = Ω Σ P_{i−1} X_i P_{i+1}`), the Néel state \|Z₂⟩=\|101010⟩ quenched under the dynamics |
| finding-exp172-scars-n8-wall-ember-c4202.md | 1 | 0 | FLAG | 22 | fidelity anomaly **+0.058 ± 0.005 (1.7σ, readout-limited)**. Both clear the frozen bare gate; the |
| finding-exp173-scars-n8-defog-ember-c4203.md | 1 | 0 | NO σ LINE | None |  |
| finding-exp175-relay-gate.md | 1 | 0 | cat4? | 12 | \| **relaygate** (swap → EJS CNOT) \| **0.576** (6σ over 1/2) \| 0.822 \| +0.76 / +0.28 / −0.27 \| |
| finding-exp176-chain-tax.md | 1 | 0 | FLAG | 22 | predicts F = 0.730; measured 0.571 → **Δ = −0.212 at −9.4σ**. The tax is not a fixed |
| finding-exp177-frame.md | 1 | 0 | cat4? | 7 | flight closing the composition-tax arc: Exp175 (tax, −3.4σ) → Exp176 (compounds with windows, |
| finding-exp178-echo-window.md | 1 | 0 | cat4? | 18 | - **Echo gain +0.293 at 24.8σ (live), +0.217 at 18.3σ (frame-tracked).** Primary and secondary |
| finding-exp179-merged-window.md | 1 | 0 | cat4? | 1 | # Finding — Exp179: THE MERGED WINDOW — architecture pays (+12.3σ), and the circuit-level plateau is found |
| finding-exp180-relay-key.md | 1 | 0 | FLAG | 32 | the plateau (F ≈ 0.77) predicted **1.97 — no violation**. Measured: **2.235, certified at 12.7σ. |
| finding-exp181-dist-bv.md | 1 | 0 | cat4? | 12 | \| local (monolithic ceiling) \| 0.995 \| 0.970 \| 0.964 \| 0.912 \| 0.949 \| 4/4 \| |
| finding-exp182-dist-bv3.md | 1 | 0 | cat4? | 17 | **all eight programs**; +79σ / +125σ / +141σ over the falsifier floors per weight class — and |
| finding-exp183-secret-sharing.md | 1 | 0 | cat4? | 1 | # Finding — Exp183: THE TWO-OFFICER PROTOCOL — a secret neither officer can read alone, certified at 61σ |
| finding-exp184-acrosstime.md | 1 | 0 | cat4? | 1 | # Finding — Exp184: THE HANDSHAKE ACROSS TIME — states with disjoint lifetimes, entangled at 40σ, by a choice made after both were gone |
| finding-exp185-pagewootters.md | 1 | 0 | FLAG | 40 | is exactly Page–Wootters. My absolute 0.80 bar silently assumed a near-free translation circuit. |
| finding-exp185b-pagewootters.md | 1 | 0 | cat4? | 6 | leg 2 absolute bar) stands in the record unamended. |
| finding-exp186-leggett-garg.md | 1 | 0 | cat4? | 1 | # Finding — Exp186: THE PRESENT WITH NO DEFINITE PAST — macrorealism violated at 24σ with negative-result measurements |
| finding-exp187-late-order.md | 1 | 0 | cat4? | 1 | # Finding — Exp187: THE ORDER DECIDED LATER — primary held (10σ/32σ off the mixture equator); falsifier band and gauge missed instructively |
| finding-exp187b-late-order.md | 1 | 0 | cat4? | 12 | \| W₊ = ⟨Z\\|+⟩ (delayed) \| **+0.218 (+17σ)** \| off the mixture equator (0) ≥5σ; band +0.08..+0.25 \| HELD \| |
| finding-exp188-live-choice.md | 1 | 0 | cat4? | 1 | # Finding — Exp188: THE LIVE CHOICE — 184 closed its fence at 23σ; 187-live was killed by the window law, on schedule, by my own omission |
| finding-exp188b-live-choice.md | 1 | 0 | cat4? | 1 | # Finding — Exp188b: the live order-choice works, echoed — +20σ/26σ; two gauges teach two lessons |
| finding-exp189-shields-up.md | 1 | 0 | cat4? | 25 | 0.0010 vs bare 0.0021 — **ratio 0.49 (~2.2σ)**. In X it is a statistical tie |
| finding-exp190-shield-pays.md | 1 | 0 | cat4? | 11 | \| survival, X family, matched time \| logical/bare ratio 3.84 (T0) / 1.24 (T1) / 1.55 (T2) \| ratio < 1 at ≥3σ \| **NOT HELD** \| |
| finding-exp190b-shield-pays.md | 1 | 0 | cat4? | 23 | \| 0 \| 0.0010 (acc 0.972) \| 0.0031 \| **0.31** \| ~4.2σ \| |
| finding-exp191-logical-bell.md | 1 | 0 | cat4? | 1 | # Finding — Exp191: THE SHIELDED HANDSHAKE — logical qubits entangled at 57σ, and the shielded pair beat the bare one |
| finding-exp192-logical-teleport.md | 1 | 0 | cat4? | 16 | blocks A–B carrying Exp191's 57σ logical Bell pair, logical Bell measurement by transversal |
| finding-exp193-wigner-friend.md | 1 | 0 | cat4? | 1 | # Finding — Exp193: THE FRIEND IN THE MACHINE — observed facts are not absolute until copied (20σ) |
| finding-exp194-arrow-meter.md | 1 | 0 | cat4? | 16 | rises monotonically 0.111 → 0.198 → 0.343 → 0.543 (each step ≥ 2σ). The rewindable share R(T) |
| finding-exp241b-syndrome-memory.md | 1 | 0 | cat4? | 43 | counts are many σ from 1, but mechanisms are NOT identified — this is a phenomenon report, not an |
| h10-b4-heat-backward-not-held-whisper-c5055.md | 1 | 0 | cat4? | 1 | # H10-B4 — Heat Flowing Backward: NOT HELD — correlations bought total suppression of a 22σ thermal flow, not its reversal |
| h10-c1-winding-meter-s0-no-fly-whisper-c5055.md | 1 | 0 | FLAG | 9 | The staged design worked exactly as designed: the S0 pilot measured the interferometric attenuation rate **λ̂ = 0.0259 ± 0.0173 per 2q gate* |
| h10-c2-vacuum-harvest-null-whisper-c5055.md | 1 | 0 | FLAG | 1 | # H10-C2 — The Vacuum Mine, third shaft: harvesting DOES NOT HOLD — and the null calibrated the many-body survival ceiling |
| h13-cell2-isotropy-gate-NO-TEST-whisper-c5058.md | 1 | 0 | cat4? | 12 | \| CE \| +0.00168 \| +0.00316 \| −0.00296 \| 0 of 3 (z = 0.4/0.7/0.7) \| |
| h13-cell2-isotropy-gate-PASS-whisper-c5058.md | 1 | 0 | FLAG | 14 | **All five clauses hold**: isotropy magnitude spread inside the arm-gap+MDE threshold on both arms · resolved signs matching the frozen idea |
| h13-cell3-temporal-negativity-whisper-c5048.md | 1 | 0 | cat4? | 1 | # Finding — H13 Cell 3: THE TEMPORAL NEGATIVITY METER — a density matrix with a negative eigenvalue, 293σ deep, and the certificate that thi |
| h13-cell4-hindsight-meter-whisper-c5058.md | 1 | 0 | FLAG | 1 | # H13 Cell 4 — THE HINDSIGHT METER: retrodiction beats prediction by the amount the two-time formalism computes — **all gates PASS**, mid-cu |
| h13-cell5-hardy-whisper-c5048.md | 1 | 0 | cat4? | 1 | # Finding — H13 Cell 5: THE EVENT THAT NEVER HAPPENS — Hardy's impossible event logged at 8.7%, 15.7σ past every local-realist accounting |
| h13-cell5-pigeonhole-FAIL-hardware-whisper-c5060.md | 1 | 0 | FLAG | 66 | predicted ~0, and it misses the registered bar of < 0.50. **Suppression is not the pigeonhole |
| h13-cell5-placement-CLOSED-and-my-diagnosis-falsified-whisper-c5060.md | 1 | 0 | cat4? | 36 | > difference **0.11411 ± 0.02857 = 4.0σ**. The bias is **not** a stable property of a placement, and |
| h13-cell6-6b-NO-TEST-premise-gates-whisper-c5058.md | 1 | 0 | NO σ LINE | None |  |
| h13-cell8-rung2-switch-under-oath-GRADED-whisper-c5062.md | 1 | 0 | FLAG | 43 | - **Floor**: 0.6165 (the commuting-class weight of q\*) — verified on-chip, not assumed |
| h15-positronic-neuron-arc-whisper-c5075.md | 1 | 0 | cat4? | 25 | \| provisional classical ceiling \| 0.5586 \| |
| route3-free-gate-rate-measured-target-unreachable-whisper-c5018.md | 1 | 0 | cat4? | 1 | # Route ③ — the free gate's RATE is measured at 33σ, and the target I froze was unreachable |
| route3-refly-rate-replicates-sign-mismatch-whisper-c5018.md | 1 | 0 | cat4? | 17 | **Three probes carry a coherent per-time rotation of 6.8–9.1 °/µs at 24–33σ in both jobs. q23 |
