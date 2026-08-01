# H10-C1 SCOUT — The Bridge: size-winding witness design (and the re-scope the literature forces)

*Whisper C5015, 2026-07-31, substrate claude-fable-5. $0 scout per H10 §4 item 2. Sources fetched
and read this cycle: the full 65-page protocol paper PDF and the dispute Comment's abstract chain.
**VERDICT: GO — but the scout's central finding is that the H10 re-scope clause FIRES NOW, before
prereg, not as a fallback.** The flight this scout hands to prereg is "The Winding Meter," not
"a wormhole."*

## 1. Literature pin

- **Protocol + mechanism taxonomy**: T. Schuster, B. Kobrin, P. Gao, I. Cong, E. T.
  Khabiboulline, N. M. Linke, M. D. Lukin, C. Monroe, B. Yoshida, N. Y. Yao, *Many-Body Quantum
  Teleportation via Operator Spreading in the Traversable Wormhole Protocol*, Phys. Rev. X
  **12**, 031013 (2022), arXiv:2102.00010. Two mechanisms, **same circuit**: *peaked-size*
  teleportation (generic thermalizing dynamics, works at infinite temperature) vs
  *gravitational/size-winding* teleportation (finite temperature, holographic regime).
- **Size winding, exactly** (their Eq. 81 and surrounding): write the evolved probe operator in
  the Pauli-string basis with coefficients c_χ. Winding = the phases wind **linearly with
  operator size S**: c_χ = e^(−iαS[χ]/q)|c_χ|. The two-sided coupling e^{igV} applies a phase
  proportional to size, and at **g/N = −2α it unwinds the distribution**, lifting the
  teleportation correlator from its two-point value G_β to ~1. The witness object is the
  **winding size distribution f(S)** — normalized to G_β ≤ 1 (the plain size distribution
  normalizes to 1), with two distinct misalignment classes (within-size, across-size).
- **Measurement recipes** (their §IX): (a) prepare Q_l(t)|EPR⟩ and **measure the two-sided
  coupling operator V_s directly — the outcome distribution IS the size distribution**, with
  measurement count independent of system size; (b) moments ⟨V_sⁿ⟩ from local OTOCs at O(Nⁿ)
  cost (rejected — scaling); (c) the *phase-sensitive* winding measurement (f(S) phases, not just
  magnitudes) — the one item to pin from their appendices at prereg (§6.1).
- **Foundations**: Gao–Jafferis–Wall, JHEP 12 (2017) 151 (double-trace deformation opens the
  throat via a negative-energy shockwave); Maldacena–Qi arXiv:1804.00491 (eternal traversable);
  *Quantum Gravity in the Lab* I & II (arXiv:1911.06314; PRX Quantum **4**, 010321 (2023)).
- **The dispute, pinned**: D. Jafferis et al., Nature **612**, 51–55 (2022) — 9-qubit,
  7-Majorana, 5-term **fully-commuting** learned Hamiltonian. B. Kobrin, T. Schuster, N. Y. Yao,
  *Comment on "Traversable wormhole dynamics on a quantum processor"*, arXiv:2302.07897:
  (i) the learned Hamiltonian **does not thermalize**; (ii) SYK-like teleportation appears
  **only on the ML-training operators**; (iii) — the finding that redesigns our witness —
  **"perfect size winding is a generic feature of small-size, fully-commuting models"** and does
  not persist at larger size or with non-commuting terms. Reply: arXiv:2308.00697.

## 2. The scout's central finding — the artifact threat is at OUR scale

H10 wrote the re-scope clause as a fallback ("if the witness cannot be built at our scale…").
The Comment's point (iii) shows the actual failure mode is the opposite: at N ≈ 6–10 qubits the
witness can be built and can **pass for the wrong reason** — perfect winding as a small-size
artifact, exactly the trap the Nature claim fell into. Therefore:

> **Re-scope now, by design.** The flight is **THE WINDING METER**: the first gate-model
> measurement of the winding size distribution f(S) — magnitudes AND phases — with the
> unwinding relation g/N = −2α tested quantitatively, and the teleport classified
> peaked-size vs winding by a pre-registered diagnostic. The word *wormhole* appears only in an
> interpretation row citing GJW/MQ. **The claim is mechanism metrology, not gravity.**

This is stronger than a wormhole costume, not weaker: the diagnostic that *settled* the field's
dispute becomes our certified instrument, flown with the control arms the disputed experiment
lacked.

## 3. Witness design (built to survive the Comment that killed the Nature claim)

**Hamiltonian**: a small **non-commuting** chaotic spin chain (mixed-field Ising class), chosen
by us, no machine learning — killing Comment objections (i)/(ii) by construction. At N_side ≤ 4
everything is exactly diagonalizable classically: **every measured curve has an exact-theory
overlay**. Said plainly in the claim: nothing here is beyond classical reach; exactness is the
certification, not a limitation.

**Arms** (all pre-registered, all on one chip):

| Arm | What it isolates |
|---|---|
| Finite-β TFD, coupling at g/N = −2α | the mechanism arm: winding present, unwinding lifts correlator toward exact-theory value |
| **g-sweep through −2α** | the *quantitative* relation — the unwinding optimum sits where the measured α says it must (this is the meter's calibration curve) |
| Wrong-sign g | GJW sign physics: the "throat" shuts; transmission must die |
| β = 0 (TFD = Bell pairs) | peaked-size regime: teleportation persists, **winding must be absent** — separates the mechanisms on hardware |
| Scrambled-phase coupling | mechanism broken at fixed magnitudes; transmission dies |
| No coupling | floor |
| **Commuting-H twin** | fly the *artifact itself*: a small fully-commuting model showing "perfect winding" — demonstrating on hardware exactly why small-N winding alone proves nothing (the Comment's point (iii), exhibited rather than footnoted) |
| Thermalization check | level statistics / late-time observable equilibration of our H vs the commuting twin — Comment point (i) as a measured contrast |

**The negative-energy leg** (kept, certified): ⟨H_R⟩ through the coupling — the injected-energy
dip measured under the F94/F95 + QET demon-ledger grammar. In GJW the coupling's negative-energy
pulse is what makes the throat traversable; here it is measured as **the priced cost of the
unwinding**, interpretation row only.

**Registered verdicts (freeze at prereg)**: (V1) winding phases fit the linear ansatz on the
mechanism arm with pre-set residual bar, and the g-sweep optimum lands at −2α(measured) within
pre-set tolerance; (V2) β=0 arm shows teleportation with winding absent (bar on winding
amplitude); (V3) wrong-sign and scrambled arms die (bars); (V4) commuting twin shows
winding-without-thermalization — the artifact, reproduced and labeled. **The exhibit is the
2×2 of (winding present/absent) × (mechanism real/artifact).**

## 4. Resources

- N_side = 3–4 ⇒ 6–8 system qubits + probe + readout ancilla(s) for the phase-sensitive
  measurement ⇒ **8–10 qubits**; trotterized e^{±iHt} both sides + coupling ⇒ depth of order
  40–80 two-qubit gates (Exp242 flew 54; Exp151 flew 12 drive periods).
- TFD prep: exact-compile isometry at this size (β=0 arm is free — Bell pairs).
- Shots: distribution + phase estimation across ~8 arms — the heaviest H10 flight; still
  single-digit QPU-minutes class. **Real flight, behind steth**, per H10 §4.

## 5. Kill conditions

- The phase-sensitive f(S) recipe (§6.1) requires resources beyond ~10 qubits or depth that
  drowns the phases in decoherence at exact-sim-predicted contrast → NO-GO as designed
  (fallback: magnitudes + g-sweep-optimum only, with the claim weakened accordingly and labeled).
- Exact simulation shows our chosen non-commuting H has no measurable winding window at any
  reachable (β, t) → choose different H or NO-GO; the window must exist **in exact theory
  first** — no hardware fishing.

## 6. What remains before prereg

1. **Pin the phase-sensitive winding measurement** — ✅ **RESOLVED C5016 (Creator go), from the
   paper's own §IX (Eqs. 106–107 + footnote 18), and it is BETTER than this scout assumed: no
   ancilla interferometry is needed.** The two-sided correlator IS the characteristic function
   of the size distribution, C_Q(t) = e^{ig}·Φ_S(g), so the full complex f(S) — magnitudes AND
   phases — comes from **sampling the correlator over a grid of g and Fourier-transforming in g**.
   Per g-point, two runs of the SAME teleportation circuit with modified insertion/readout:
   - **Re[φ_S(g)]**: replace state insertion with the projector (1+Q)/2; measure ⟨Q⟩ on the
     right side instead of teleportation fidelity.
   - **Im[φ_S(g)]** (the winding itself): replace insertion with the unitary (1+iQ)/√2 —
     which for Pauli Q is exactly **exp(iπQ/4)**, a single native-depth rotation.
   Footnote 18 covers our finite-β regime: the same procedure with the final measurement moved
   to the left side determines the winding size distribution of §VIIIB. The g-grid the mechanism
   arms already sweep IS the measurement grid — the meter and the experiment share circuits.
   One-sided adaptations exist when the coupling is classical (their Eq. 9 route), noted as a
   fallback with their own caveat (approximate, not exact) attached.
2. Exact-sim campaign ($0, classical): choose H, β, t; verify winding window + all eight arms'
   predicted contrasts at planned shots; freeze every bar from the sim.
3. Elder co-checks: the exact-diagonalization overlays and the V1 tolerance; Ember seals the
   arm schedule (blind to which arm is which where applicable).

*Scout verdict: GO, re-scoped by evidence. What the dispute did to the field's flagship claim,
we pre-build into the witness — and the meter we get is a better instrument than the costume
we declined.*


---
## §7. CAMPAIGN RESULT (C5016, Creator "run them") — HONEST NEGATIVE, kill-condition fired as designed

Instrument built and gate-checked (`scripts/h10_c1_winding_sim_c5016.py`): KA1 (Σf(S) = G_β
identity) and KA2 (zero winding phases at β=0) both PASS at machine precision (≤1e-15).
Campaign over mixed-field Ising (J=1, hx=1.05, hz=0.5), N=4/5/6, β∈[0.3,2.0], t∈[0.6,8.0]
(`results/h10_c1_winding_sim_c5016.json`, `..._refine_c5016.json`):

**NO measurable winding window exists for this Hamiltonian family at our scale.** Fitted |α| ≤ 0.04
everywhere (indistinguishable from zero), unwinding gain 1.000 (nothing to unwind), G_β = 0.67–0.95
(the two-point function barely decays — a local chain at N≤6 does not scramble Q enough to wind).

Per §5's pre-registered kill-condition: **choose a different H or NO-GO.** The requirement this
buys: the flight's Hamiltonian must be a FAST SCRAMBLER (all-to-all random 2-local / SYK-analog or
kicked-Floquet), which raises hardware compile depth — a real cost the prereg must price. The
local-chain family is dead for this flight and recorded so no future cycle re-tries it.


## §8. FAST-SCRAMBLER LEG (C5017, same session — Creator: "keep going") — **THE WINDOW EXISTS. GO.**

Same instrument, same known-answer gates (re-run on the new H: all pass ≤2.2e-16). Hamiltonian:
all-to-all random Heisenberg + random Z fields (seeded, N=6) — a fast scrambler, no ML
(`results/h10_c1_winding_fastscrambler_c5017.json`):

**The winding window exists in exact theory, and the meter's calibration relation holds:**
- β=3.0, t=4.0: **α = −0.337**, phase-fit rms 0.102 (linear winding, real), and the unwinding
  optimum **g\* = −0.68 vs 2α = −0.67** — the g = 2α relation confirmed to two decimals;
  unwind gain 1.63.
- β=1.0, t=0.5: α = −0.174, rms 0.114, g\* = −0.32 vs 2α = −0.35 — window present at moderate β
  where G_β = 0.366 (practical sweet spot candidate: |α|·G_β·fit-quality trade).

**Honest bars carried with the GO:** G_β = 0.036 at β=3 (tiny absolute correlator ⇒ shot-cost for
phase estimation is the binding constraint there; β≈1 likely the flyable point). The window is a
REGION (β≥1, specific t), not universal — several rows show rms 0.3–1.2 (no clean winding), which
is exactly what a prereg wants: an operating point with bars, not a universal claim. Contrast with
§7's local-chain negative is itself arm-grade evidence: same instrument, same gates, H is the
only difference.

**Remaining before prereg:** operating-point selection (maximize |α|·G_β·fit-quality); arm
predictions at that point; trotterized all-to-all compile-depth estimate (the priced cost §7
predicted). C1 status: **GO with a target.**

## §9. OPERATING POINT + ARM BARS (C5017) — the prereg's numbers, frozen from exact theory

**Operating point** (constraint rms<0.15, |α|>0.05, minimize shots-to-5σ;
`results/h10_c1_operating_point_c5017.json`):

> **β = 0.6, t = 0.3** · α = −0.176 (phase-fit rms 0.114, clean linear) · G_β = 0.634
> (large absolute correlator) · g\* = −0.42 · unwind gain 1.083 ·
> **shots-to-5σ ≈ 9.0k for the headline discrimination — flyable.**

**Arm bars at the OP (exact theory, freeze-ready):**

| Arm | Predicted value | Reads as |
|---|---|---|
| Mechanism, C(g\*) | **0.686** | the lift |
| No coupling, C(0) | 0.634 | floor (+0.052 = the 5σ target) |
| Wrong-sign, C(−g\*) | **0.497** | dies BELOW floor — the sign physics, visible |
| Scrambled-phase (mean/p95 over 200) | 0.350 / 0.600 | dies hard |
| β=0 winding phase / gain | 8e−15 / exactly 1.0 | winding ABSENT (KA2 doubles as the arm) |
| Commuting twin, same (β,t) | α=−0.044, **rms 0.474** | **no clean winding** |

**Honest reframe forced by the last row:** the KSY "perfect winding artifact" does NOT manifest
for our hz-Ising commuting twin at this OP — their artifact was a property of their specific
fully-commuting 5-term class. So the twin arm's registered prediction becomes **contrast**
(chaotic winds cleanly, commuting does not), and the §3 promise to "fly the artifact itself" is
withdrawn unless a twin that actually shows it is found. Better to demote the arm than inflate it.

**Sparsification check** (`results/h10_c1_sparse_scrambler_c5017.json`): a 3-regular (9-edge)
scrambler PRESERVES a window but degrades it ~36× in shot cost (best sparse point: α=−0.057,
shots-to-5σ ≈ 326k). **All-to-all is load-bearing for the flyable window — depth is the price of
signal, now a measured trade.**

**Depth accounting (order-of-magnitude, to sharpen at prereg):** t=0.3 is shallow — r=1–2 Trotter
steps plausible (error O(t²/r); quantify at prereg). All-to-all N=6: 15 pairs × 3 CX per
Heisenberg pair per step ≈ 45 CX/step + heavy-hex routing (~1.5–2×) ⇒ ~70–180 2q gates per side's
evolution. **The named remaining engineering item: the ρ^{1/2} insertion at finite β** (footnote-18
left-side route) — candidate implementations: low-order compiled expansion of e^{−βH/2} at β=0.6,
or variational thermal-purification; the choice and its measured fidelity belong to the prereg,
not to this scout.

**C1 status: GO — prereg inputs complete except (a) Trotter-error quantification at r∈{1,2},
(b) the ρ^{1/2}-insertion engineering choice.** Both are prereg-time items by design.

## §10. TROTTER ROUTE FROZEN (C5017, "keep them moving") — the window survives real circuits

Exact-vs-Trotterized winding at the OP (β=0.6, t=0.3; `results/h10_c1_trotter_error_c5017.json`):

| Evolution | unitary 2-norm err | α | Δα vs exact | rms |
|---|---|---|---|---|
| exact | — | −0.176 | — | 0.114 |
| r=1, 1st order | 0.62 | −0.103 | +0.073 (41%) | 0.113 |
| r=2, 1st order | 0.31 | −0.140 | +0.036 | 0.113 |
| **r=2, 2nd order** | **0.044** | **−0.165** | **+0.010 (6%)** | 0.122 |

**Frozen: 2nd-order symmetric Trotter, r=2.** The winding and the correlator bars survive with a
6% α bias (to be carried as a stated correction in the prereg's exact-theory overlays). Depth
with per-pair Heisenberg-term grouping (3 CX per pair-triplet): ~15 pairs × 3 CX × 2 sweeps ×
r=2 ≈ 180 CX + routing — deep, priced, and now a NUMBER rather than a fear. Remaining before
prereg: **one item — the ρ^{1/2}-insertion realization** (subtle; prereg-time by design).