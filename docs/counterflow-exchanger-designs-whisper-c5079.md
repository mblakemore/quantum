# The Counterflow Exchanger — four designs from flown parts

**Author**: Whisper (DC15W), C5079 (2026-08-24), substrate claude-fable-5.
**Charter**: Creator ask, verbatim scope — *"look over our latest quantum docs and the museum on
indefinite causal order, energy transfer, and the quantum engine parts we've built, and anything
related to thermodynamics and flows — see if you can come up with ideas for using our existing
building blocks, experiments, and data to build something like a counterflow exchanger; something
to gain efficiency or drive something somewhere further past equilibrium."*
**Status**: PROPOSAL — options + recommendation. Nothing here is frozen, flown, or GO-requested.
**Rediscovery check**: `already-built.js` run on counterflow / ICO-cooling / heat-exchange before
writing (C5011 discipline). The three governing priors it surfaced are §1's fences.

---

## 0. The counterflow principle, and why it fits our bench

A counterflow exchanger runs two streams in **opposite directions** so the local gradient stays
roughly constant along the whole length. That geometry is why it beats co-flow: parallel streams
converge to the mean (effectiveness ≤ 50% at equal capacities — both exit lukewarm), while
counterflow lets the cold stream exit **hotter than the hot stream's own exit** ("temperature
crossing", effectiveness → 100% with length). The efficiency comes from *where you put the
contacts*, not from any exotic element.

That is exactly the kind of lever this campaign is good at: we own certified **elements**
(a branch-splitting thermal switch, a spendable cold branch, a cyclic information-driven
extraction wheel, an in-circuit feedforward transmission) and the open question is whether a
**geometry** composes them into more than their solo numbers.

## 1. What the corpus already settles (the fences this proposal must respect)

1. **C4720 (`ico-cooling-floor-and-concentration-boundary`)**: the ICO resource **saturates** —
   cascading the switch against *fixed* baths converges to p₁ ≈ 0.177 (bath 0.25) in ~3 stages,
   and on hardware the cascade *inverts* (22-CZ haircut +0.025 > stage-2 theory gain +0.007, the
   F85 scaling-inversion). Concentration is **classical** entropy compression (Exp139b flew it as
   a labeled engineering artifact, 37.6σ, **no F-number** — the fuel-mislocation guard, F94/C4717).
   Route C was the one strong lever — "the + branch is ~0.74× *whatever bath it is fed*" — and was
   dismissed as *"start with a colder bath… if you had a 0.05 bath you'd use it directly."*
   **This proposal's entire premise**: a counterflow geometry is the machine that *manufactures*
   progressively colder effective baths along its length. Route C stops being "start colder" and
   becomes "the geometry produces colder." The closed verdicts (cascade, concentration) stay closed.
2. **H10-B4 (`heat-backward-not-held`, C5055)**: on our silicon, pre-shared correlations bought
   **total suppression of a 22σ thermal flow, not its reversal**. Passive correlations are an
   *insulator*, not a pump. Any design here that moves energy against the gradient must do it the
   way F95/F97/exp195c did — **actively**: measure, communicate, feedforward, and pay the demon's
   invoice.
3. **The turbine NO-TEST (C5072)**: there is no ambient on-chip stream to siphon (q34 was
   gate-clock interference; q45 is a TLS drain, not a store). An exchanger's streams must be
   **manufactured** — which the chip supports natively: **MCM reset is a cold contact, idle/drive
   heating is a hot one** (board #143's exact pair), and prepared thermal populations are streams
   on demand.

## 2. The parts bench (all flown, all cited)

| Part | What it certifiably does | Source |
|---|---|---|
| **Switch contact** (g=0.75, bath 0.25) | Splits ONE bath into a **cold branch p₁=0.185** and a **hot branch p₁=0.417** per herald (Δ=0.232, causal value exactly 0) — a heat-pump element whose two outputs are the two streams | exp108 frozen theory; F86/F88 measured; **F118 spent the cold branch** (sub-bath 5σ on an external qubit); **F95 spent the hot branch** (full engine cycle, net work 0.034/run, demon billed +0.0051/action) |
| **QET extraction** | Local energy driven **12σ below local ground** via coherent conditional extraction; Alice's deposit +0.740 billed; LOCC leg failed on latency and stays failed | F97 (exp119b) |
| **The wheel** | Six back-to-back information-driven extraction rounds per shot, falsifiers paying every round, **wear slope +0.0002 ± 0.0056 = zero degradation** — cyclic operation certified | exp195c (C5073), board #146 done |
| **The transmission** | Mid-circuit herald → feedforward in ONE circuit; herald rate 0.35; sensor stable across a recalibration | C5073 automatic-transmission block |
| **Thermal insulation** | Correlations suppress a 22σ flow to zero — a certified *thermal valve* (the graded negative, used as a part) | H10-B4 |
| **Native reservoirs** | Reset ≈ cold bath contact; idle-heating ≈ hot bath; head unmeasured (open board row) | #143 (backlog, unassigned) |
| **Free phase** | In-window precession = free Z-rotations (design row, unspent) | #145 |
| **Error map** | Two-axis error field mapped; non-diagonal 33σ axis known (where chained conditionals die) | C5073 GEAR 1 / GEAR 3 |
| **Museum wing** | `ico-refrigerator`, `energy-teleport`, `negative-energy` exhibits — the thermo wing this would extend (via Dawn) | demo/ |

**The one translation that makes "flow" real on a static chip**: a *stream* is a repeated-
interaction sequence — one carrier qubit re-prepared per parcel (MCM reset = advection), so
"exchanger length" = number of contact stages, and **counterflow vs parallel-flow is purely the
pairing ORDER of which hot parcel meets which cold parcel**. Same gates, same depth, same shots —
only the order differs. The comparison is confound-free by construction.

## 3. The four designs

### A. The Counterflow Ladder — the geometry witness (build first)
Two carrier qubits (H-stream, C-stream) + partial-SWAP contacts (transmissivity τ = sin²θ, 2-3 CZ
each) + MCM-reset advection. Run the SAME ladder in co-flow and counterflow pairing order at
matched budget (N=3–4 stages, τ≈0.5).
**Claim (falsifiable, CI-graded): temperature crossing.** Counterflow's cold-stream exit
p₁ exceeds the hot-stream exit p₁; co-flow cannot cross ½-effectiveness at equal capacities.
Discrete theory: ε_cf = Nτ/(1+Nτ) = 0.60 at N=3, τ=0.5 vs ε_pf ≤ 0.5 — with prepared
p_hot=0.40 / p_cold=0.05 the crossing margin is ~0.035 in population, ~7× the SE at 10k shots.
**Honest label**: populations under partial-SWAP are classical Markov dynamics — this ships as a
**labeled engineering artifact** (the Exp139b precedent, no F-number), *and it is the certified
substrate B and C stand on*. It also executes **board #143 en route** (stage-1 nuisance
measurement of reset-bath temperature and idle-heating rate, the F95 two-stage pattern).
**Failure modes named**: sim-optimism (derive sentinel floors from measured gate/readout error,
not Fake* — the Exp139 NO-TEST lesson); readout-error asymmetry faking a crossing (use F118-style
null arms: both streams prepared equal must show NO crossing).
**Cost**: $0 sim decides; hardware ≈ 2 configs × ~30 CZ × 10k shots. Small.

### B. The Manufactured Bath — counterflow feeds the fridge (the record attempt)
Use A's ladder to pre-cool the *effective bath* a single ICO stage then eats: heralded output ≈
0.74 × p_eff. Target: **certified cold output below 0.177** — below the fixed-bath ICO floor —
with the attribution ledger split printed (geometry's share vs switch's share vs herald cost),
billed in one currency (F104 Landauer invoice; billing-currency attack class).
**Why this is not the C4720 cascade re-run**: the cascade paid ~22 CZ *per stage* for +0.007
theory gain per stage — inverted on hardware. Here the exchanger stages are cheap (2-3 CZ each)
and the expensive ICO block is paid **once**; each 0.01 of manufactured bath drop buys ~0.0074 of
output drop. The economics invert back. If a 3-stage ladder moves the effective bath 0.25 → 0.20,
the composite target is ≈ 0.148 vs the 0.177 floor — a ~4σ-resolvable gap at F118's error bars.
**Attribution discipline (the F94 guard, stated now)**: the composite is an engineering system —
"ICO drove below its own floor" would be fuel-mislocation. The claim is: *the system beats what
either the geometry (p_eff) or the switch-on-raw-bath (0.185 theory / 0.21 hw) achieves alone*,
with each part's contribution printed.
**Cost**: $0 sim; hardware ≈ one F118-class flight (~30 PUB, ~30 CZ). Medium.

### C. The Information Recuperator — heat forward, information backward (the physics prize)
The conceptually sharp one. In a classical counterflow exchanger both streams are matter. Here the
counterflowing stream is **information**: measurement records flow *against* the heat direction,
conditioning extraction upstream — the exp195c wheel construction **unrolled spatially** along a
qubit line (the wheel cycled one pair in time; this propagates the same certified borrow across
stages in space), using the transmission's in-circuit herald→feedforward (delivered herald rate
0.35 — billed, per the idealized-hard-delivered-easy attack class).
**The measured variable is counterflow itself.** Three arms at matched gates/shots:
  (i) information flows AGAINST the heat direction (counterflow),
  (ii) information flows WITH it (co-flow),
  (iii) feedforward severed — heralds replaced by fresh random bits (the H15 severed-synapse
       control style; also the H10-B4 lesson made mechanism: passive correlation alone must
       show suppression at best, never pumping).
**Claim shape**: net extracted work (the F95/exp195c observable, same currency) is greater in arm
(i) than (ii), and (iii) collapses to the no-communication baseline — i.e., *counter-directed
information is worth more than co-directed information at matched resources*. That is a statement
about the thermodynamic value of the information stream's DIRECTION, which nothing on our ledger
(F95 = one pair, F97 = one pair, exp195c = temporal cycles on one pair) has tested. If (i) beats
(ii), the exchanger geometry has genuine quantum-thermodynamic content on our hardware; if not,
an honest negative in the H10-B4 house style, with the accounting kept.
**Known hazard**: chained conditionals walk straight into the non-diagonal 33σ axis (GEAR 3) —
route the chain using the C5073 two-axis error map; the map exists for exactly this.
**Cost**: $0 sim first (the wheel's selftest machinery reproduces the −0.2001 gap exactly — extend
it spatially); hardware ≈ exp195c class (one batch, 40-60 CZ, 4-6 MCM). Medium.

### D. Coherence keeps the gradient — quantum vs dephased exchanger ($0 unless it survives sim)
Same ladder twice: coherent partial-SWAPs vs explicitly dephased between contacts. Matched
everything; the difference isolates what inter-contact coherence contributes to exchange
effectiveness. Likely an honest negative at our depth (coherences die in the contact chain);
worth exactly one $0 sim to decide, hardware only if the sim shows a margin that survives
measured-error floors. No claim otherwise.

## 4. Recommendation and sequence

**A → C → B, with D as a $0 side-check.**
- **A first**: cheapest, closes #143 en route, and B and C both stand on its certified substrate.
  It is also the direct answer to "gain efficiency from geometry" — the crossing witness IS the
  efficiency claim, graded with CIs.
- **C is the prize**: the only design whose claim is new physics for our ledger (directional value
  of an information stream), built almost verbatim from exp195c + F97 + the transmission — our
  three most recently certified parts.
- **B is the record**: a system number below the fixed-bath floor with clean attribution — a
  strong museum piece for the existing thermo wing (ico-refrigerator + energy-teleport +
  negative-energy exhibits, extended via Dawn).
- Every design sims at **$0 before any tank spend**; every hardware sketch above stays inside a
  single calibration window.

**Attack-preflight self-check (run at proposal time, C5027 lesson — infrastructure for a claim IS
the claim)**: baselines are *executed*, not assumed (arm (iii) and the no-communication bound for
C; solo-part numbers for B); one billing currency per comparison, frozen at prereg (work units of
F95/exp195c for C; population p₁ for A/B); delivered-artifact honesty (herald rate 0.35 billed,
not idealized); no simulation-cost-as-advantage claims anywhere (class 4 does not arise); the
planted-structure and index-space classes do not apply (no hidden secrets, no container
enumeration). Full `attack_preflight.py --claim` runs at each prereg freeze, per standing rule.

**What this proposal does NOT do**: it does not reopen the cascade or the concentration (closed,
C4720); it does not claim passive correlations pump heat (H10-B4 stands — arm (iii) *depends* on
it standing); it does not request a GO, a tank allocation, or an F-number.
