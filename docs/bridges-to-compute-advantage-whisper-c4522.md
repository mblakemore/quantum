# Bridges to a Compute Advantage on Current Hardware — Creative Synthesis of the Campaign

> **⊘ SUPERSEDED (C4996, 2026-07-23 — same day, own red-team, pre-submission).** The F121 runtime-advantage claim recorded below is RETIRED: the planted MM problem's algebra falls to a classical 41-query linear-structure solve (~0.25 ms vs the 1,818 s simulation floor), run on our own sealed instance and confirmed independently by all three court seats. **F120 (shot-axis decoder) stands as an instrument result — not an advantage. F119 under re-audit.** This record is kept as-was, dated — see [the red-team finding](exp-hss-race6-REDTEAM-whitebox-break-whisper-c4996.md). Read every "advantage/WIN" statement below through that lens.

**Author**: Whisper (DC15W), C4522 (2026-07-09) — Creator-directed synthesis
**Scope**: every finding in this repo (F1–F82 line + Findings 1–51 + IIT arc), read back from the files, not from memory
**Honest frame first**: F54 quantified the brute-force gap — the Grover speedup that beats classical Monte Carlo
needs ~10⁴ two-qubit gates; the scrambling wall is ~10³ (F05, ORQ#6). No stack of constant factors closes a
50–100× depth deficit. So the question splits: (a) how far can the constant-factor levers take *useful work*,
and (b) where can the scoreboard itself be honestly changed so that an advantage is *provable at low depth*.

---

## Bridge 1 — The multiplicative stack (compound the constant factors)

The campaign's practical findings are largely **independent causal nodes in the noise DAG** — placement,
calibration window, readout depth, measurement basis, shot economics act on different mechanisms — so their
gains are multiplicative, not redundant:

| Lever | Finding(s) | Measured gain | Mechanism (why independent) |
|---|---|---|---|
| Noise-aware placement, re-queried live | F57, F58, F65–F70 | 17–46× bias; ~73% of witness decline | WHICH qubits (spatial noise map; stale within a day) |
| Calibration-window gating via sentinel | F81, Exp100/101 | err 0.154 → 0.0003 (~500×) | WHEN you run (temporal lottery; good window = zero contrast decay through 124 2q gates, Exp101 R=1.002) |
| IPE / semiclassical readout (feedforward) | Exp102/103, Finding 51 | removes 66–75% of 2q gates in QPE readout; +25.24pp exact-success on HW, gap grows with t | HOW MANY 2q gates exist at all — converts quantum depth into classical feedforward |
| Commutation-aligned measurement basis | F03, F12 | 1.2–3× (substrate-dependent magnitude, direction generalizes) | WHICH basis you read (free compile-time choice) |
| Shot/anchor economics | Findings 27, 30, 36–38, F48ᵃ/F53 | 1024-shot ceiling (2048 wastes 4×); best-of-k rescue +0.070; k-adaptive ≈ full lift at −30% compute; anchor RANK survives noise ρ=1.000 | CLASSICAL budget allocation around the QPU |

**The existence proof already happened**: F81's good window **saturated the quantum Cramér–Rao bound**
(err 0.0003, σ≈0.0009) on a real financial distribution — the statistical signature of the quantum estimator
working at theoretical efficiency — with default placement, no sentinel, by luck. The stack's job is to make
that reproducible-on-demand instead of a lottery win. Realistic composite: 1–2 orders of magnitude of
effective depth/precision over naive usage. Not a speedup over a laptop; a different machine than the
"average-calibration" one everyone else is using.

**Deepest lever = Finding 51's generalization.** The wall is a 2q-gate wall; therefore *every quantum gate
you can replace with mid-circuit measurement + classical feedforward is free depth*. IPE proved it for QPE
readout (66–75% of the whole circuit at probe scale). Systematic follow-up: audit every algorithm in our
stack for QFT-like blocks, uncompute chains, and controlled-classical structure that `if_else` can absorb.
The loader (F79's killer) is the hard case — but measurement-based state-prep variants exist and nobody has
run our sentinel-gated version of them.

## Bridge 2 — "Lucky computing": harvest the calibration lottery instead of fighting it

Astronomy solved atmospheric seeing twice: adaptive optics (fix it live) and **lucky imaging** (take many
cheap exposures, keep the top 1%). F81 + Exp100/101 say the QPU is a fluctuating channel whose quality is
**cheaply measurable but not published** (F81 addendum: IBM's published calibration data was FLAT across a
3× quality swing — our sentinel out-predicts their calibration feed).

**The pipeline** (all components already exist in this repo):
1. **Sentinel vector, not scalar** (Exp101: window quality is not scalar) — IWM k0 (readout/1q axis) +
   a shallow-2q retention probe (QQQ_k1-class; Exp101 Rec#5) + k0-retest pair. ~2 q-sec.
2. **Co-batch sentinel + payload in one job.** Exp100-O1's "queue batching collapses submit spread" is a
   *feature* here: co-batched PUBs execute in the same drain = same window **by construction** — the F77
   same-device drift-free trick promoted to a standing scheduling primitive.
3. **Gate trust on the sentinel**, pre-registered as conditional inference (report conditional AND
   unconditional results — this is post-selection and must be declared, or it's p-hacking with extra steps).
4. **Exp100 (in flight, probe #5 `d9808od2su3c739ilq4g`) decides the upgrade**: if H-TSC holds, windows are
   *forecastable* (schedule right after calibration) — cheaper. If NULL, they remain *detectable* — the
   harvest still works, we just pay the sentinel tax every job. Either verdict feeds the same pipeline.

**Creative extension — "QPU weather service"**: the sentinel-vector + quiet-qubit picker (works untuned
cross-device, F70) + drift statistics constitute a better device-quality oracle than the vendor's published
data. That is a real, sellable compute advantage for *anyone* scheduling work on these machines, independent
of any quantum speedup. It is also exactly the kind of asset our network is structurally good at maintaining
(daily cycles, pre-registration discipline, three independent operators).

## Bridge 3 — Change the scoreboard: per-query and informational advantages at low depth

Generic time-to-solution advantage is walled. **Query-complexity and information-theoretic advantages are
not** — they live at exactly the depth we own.

### 3a. The causal-order discrimination GAME (highest-value next experiment)

Chiribella (2012): the quantum switch **deterministically** decides whether two unknown unitaries commute or
anticommute using **one query of each**; Araújo et al. proved via SDP that *no definite-order process can do
this with probability 1*. Verified against current literature this cycle (see Sources in the C4522 cycle
notes; a device-independent photonic certification exists — Nature Comms 2023 — so our contribution is the
**gate-model, pre-registered, adversarially-controlled** version, not a world first; say so plainly).

**We already run this observable.** F75/F77's witness measures ⟨X_c⟩ = +0.865 (commute) / −0.905
(anticommute) on `ibm_marrakesh` — single-shot discrimination success ≈ 93–95%. The reframe: stop reporting
a *witness* and run the *game* —
- Pre-register the exact optimal causal-strategy success bound from the literature (pull the SDP number;
  do NOT approximate it from memory).
- Sample commuting/anticommuting Pauli pairs, one query each, grade single-shot success vs the causal bound.
- Same triple, same drift-free co-batching as F77; sentinel-gated window (Bridge 2) to fight the haircut.
- **If measured success > causal bound with pre-registered significance: that is a genuine, provable
  information-theoretic advantage on 2026 silicon.** Small, honest, ours. This directly answers P2's open
  frontier ("any route from order-coherence witnesses toward genuine query-complexity separations") — F80's
  retraction killed a tautology, not this.

### 3b. Channel-capacity activation (second switch dividend)

Theory: two zero-capacity channels in superposition of orders transmit information. Low-depth, same
apparatus family, never tested by us. One pre-registered sim → one HW job.

### 3c. Certified randomness from CHSH 2.74

96.8%-of-Tsirelson violation (F01) supports semi-device-independent randomness expansion. Honest scope: no
loophole-free claim on-chip; frame as a *certified-entropy primitive* with stated assumptions. Bridges to the
trading stack (auditable entropy for simulations) if ever wanted.

### 3d. VQE niche (already banked)

F08: chemical accuracy on H₂ today. Window-harvested + placement-stacked VQE could push a molecule size or
two — *scientific* value, not speedup value; keep expectations labeled.

## Wild cards (one cheap probe each, ranked by weirdness)

1. **Surf the scramblon** (F04): the noise is coherent/non-Markovian with sub-noise-floor *oscillations*.
   If revival phase is stable within a calibration window, gate scheduling timed to oscillation nodes dodges
   error instead of fighting it ("echo-timed compilation"). One sim + one probe decides if the phase is
   stable enough to exploit.
2. **Ancilla-as-probe** (ORQ#3 inversion, merges with the sentinel vector): a dedicated in-circuit qubit as
   continuous noise telemetry — accept its noise, use its correlations. The sentinel vector is the static
   version; this is the dynamic one.
3. **Symmetry amplification** (Finding 19): high graph symmetry *widened* the x-basis advantage. If symmetry
   is a controllable knob that concentrates commutation benefit, problem *encodings* could be chosen for
   symmetry the way we now choose qubits for quietness. Sim-tier sweep first.

## What NOT to chase (the corpus has receipts)

- Generic Grover/QAE speedup at production depth (F54: 50–100× past the wall).
- Standard error-mitigation stacks (F07: all four degraded signal).
- Noise-as-resource (P1 RESOLVED NEGATIVE: F55 false precision, F56 monotone harm, vacuous-test audits).
- NISQ QEC (F06 ancilla tax; F62 round-1 collapse replicated independently).
- Cross-instance warm-start transfer (Findings 31/34/35: killed, outlier-driven harm).

## Priority order (my recommendation)

1. **Causal discrimination game** (3a) — highest ratio of provable-advantage to marginal cost; apparatus exists.
2. **Sentinel-gated pipeline as standing infrastructure** (Bridge 2) — converts F81 from anomaly to method;
   Exp100 verdict slots in either way.
3. **IPE-ification audit** (Bridge 1) — mechanical, high-yield, already hardware-confirmed direction.
4. Capacity activation (3b) and scramblon surfing (wild card 1) as budget-gated follow-ups.

*Pearl note for the network: Bridges 1–2 are Rung-2 interventions on the noise DAG (do(placement),
do(window), do(readout-depth)) — we measured those causal effects properly, which is exactly why they
compose. Bridge 3a is the strange one: the advantage exists because the device's causal skeleton itself
can be superposed — the one resource on this machine that classical statistics cannot even represent,
which is why it is the one place a small provable win is available at depth we can afford.*
