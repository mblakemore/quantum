# H10-C2 SCOUT — Entanglement Harvesting: mining the vacuum outside the cone

*Whisper C5018, 2026-08-02, substrate claude-fable-5. $0 scout per H10 §4 item 4 (B1 waits on
Elder's SDP co-check; C1 closed NO-FLY; B4 flown/graded; steth building on Ember's seat —
Creator: "Run the C2 scout"). Rediscovery check: no on-topic prior (top hit F61 toric-Bell
proxy at 2.4, unrelated genre; the C5015 sweep's "zero hits" confirmed). Literature pins
VERIFIED AT SOURCE this cycle — the C1 lesson (a paraphrased footnote inverted a protocol)
is now standing practice: no load-bearing citation enters a scout unchecked.*

## 1. Literature pin (verified verbatim)

- **B. Reznik, *Entanglement from the vacuum*, Found. Phys. 33, 167 (2003)**
  (quant-ph/0212044). Abstract, quoted: "We explore the entanglement of the vacuum of a
  relativistic field by letting a pair of causally disconnected probes interact with the
  field. We find that, even when the probes are initially non-entangled, they can wind up to
  a final entangled state." The founding result: vacuum entanglement is EXTRACTABLE by local
  detectors that never causally communicate.
- **A. Pozas-Kerstjens, E. Martín-Martínez, *Harvesting correlations from the quantum
  vacuum*, Phys. Rev. D 92, 064042 (2015)** (1506.03081). Two Unruh–DeWitt detectors,
  explicit spacelike configurations; design-relevant finding quoted from the abstract:
  **"smooth switching is much more efficient than sudden switching"** for spacelike
  harvesting — so BOTH switching families enter our sweep, with the literature predicting
  smooth wins (a checkable import, not an assumption).
- Adjacent corpus: Reznik–Retzker–Silman PRA 71, 042104 (2005) (Bell violation from vacuum);
  the Martín-Martínez harvesting program. Our declared in-house parents (H10 §7): F97
  (correlations buy energy below local empty), the QET exhibit (energy teleported via vacuum
  correlations + classical messages), F94/F95 grading grammar, messaging-limits.md (no-FTL
  receipts). **The triptych C2 completes: energy (F97), work (QET), and now ENTANGLEMENT
  mined from the vacuum — the vacuum as a resource ledger, third column.**

## 2. Chip-native design (the analogue, stated exactly)

- **Field**: a 1D XX chain of L qubits, H_f = J Σ_j (X_jX_{j+1} + Y_jY_{j+1})/2, J=1 —
  gapless, so the lattice vacuum (many-body ground state) carries long-range entanglement
  (the resource). **"Vacuum" means THIS chain's ground state; "lightcone" means THIS chain's
  causal cone** (Lieb–Robinson front), certified empirically on the same chip — no claim
  about spacetime, the EM vacuum, or cosmology (H10 §5 fence).
- **Detectors**: 2 ancilla qubits with gap Ω (H_d = Ω/2 Z), UDW-coupled at sites s1, s2
  (separation d): H_int = λ χ(t) [σ_x^{(1)} X_{s1} + σ_x^{(2)} X_{s2}].
- **Switching** χ(t): both detectors SIMULTANEOUS on window [0, T] — simultaneity makes the
  spacelike condition one-sided (no staggering bookkeeping): the protocol is
  exchange-disconnected iff the chain's signal front cannot cross d within T. Families:
  top-hat AND sine ramp (smooth), per the verified pin.
- **The lightcone-disjointness fence (the one design item H10 flagged)**: two layers —
  (i) design-time: the EXACT field response front δ⟨X_{s2}⟩(t) after a unit kick at s1,
  computed in exact sim — T is chosen so the front's arrival is bounded ≤ ε_front ≪ signal;
  (ii) flight-time: the SAME response front measured as an arm (perturb-and-probe) — the
  cone is CERTIFIED on the hardware that claims to harvest outside it. The residual
  (Lieb–Robinson tails are exponentially small, not zero) is REPORTED as a bound, never
  waved to zero.

## 3. Arms

| # | Arm | Reads as |
|---|---|---|
| A1 | Spacelike harvest (d, T inside the certified-disjoint window) | detector negativity N > 0 — entanglement mined outside the cone |
| A2 | Causal control (same coupling, d=1 or T past front arrival) | exchange-permitted correlation, larger, labeled |
| A3 | No-coupling floor | zeros |
| A4 | Product-state control (field prepared \|0…0⟩, NOT the ground state) | harvesting must die/change per exact prediction — the RESOURCE is the vacuum's entanglement, not the coupling |
| A5 | Cone certification (kick at s1, probe front at s2 vs t) | the empirical lightcone the fence stands on |
| A6 | Books: detector excitation P_e each side + field energy shift | the switching work that pays for the mining |

Readout: 2-detector tomography (9 settings) for A1/A2/A4; single-basis probes for A5/A6.

## 4. Budget gate (the C1 lesson, institutionalized before any numbers)

**Standing rule from the C1 flight record (quantum@8b333d0): a Heron interferometric/
amplitude-class pub must compile to ≤ ~475 2q gates at 0.22% median error for lambda ≥ 0.35;
apply a 1.6× routing factor to logical counts at design time.** C2's pubs are NOT
interferometric (direct tomography on 2 ancillas — attenuation degrades contrast but there
is no global-amplitude readout), so the budget applies as a contrast estimate rather than a
hard lambda gate — but the ≤475-gate target is adopted as the DESIGN ceiling anyway: the
scout's exact-sim campaign must find an operating point whose Trotterized protocol fits
~300 logical 2q gates (≈480 routed), or the verdict is NO-GO as designed.

## 5. Kill conditions (frozen before the campaign runs)

1. No operating point with harvested negativity measurable at ≥5σ under ≤ 50k shots/setting
   while the front-bound ε_front ≤ 10% of the harvested signal → NO-GO.
2. Depth over the §4 ceiling at every viable operating point → NO-GO as designed.
3. The A4 product-state control failing to separate from A1 in exact theory (i.e. the
   design cannot distinguish vacuum-resource from coupling artifact) → redesign or NO-GO.

## 6. Campaign plan ($0, exact)

L=8 primary (10-qubit total Hilbert space, exact), L=10 check; sweep d ∈ {3,4,5},
T ∈ {0.5…2.5}, λ ∈ {0.2,0.4,0.6}, Ω ∈ {0.5,1.0,1.5}, switching ∈ {tophat, sine}; per
config: exact evolution (piecewise-constant sparse steps), detector ρ, negativity,
concurrence, P_e; front table δ⟨X_{s2}⟩(t) per d; A4 twin per candidate OP. Outputs freeze
the prereg bars. Script: `scripts/h10_c2_harvest_sim_c5018.py`, artifact
`results/h10_c2_harvest_sim_c5018.json`.

*Scout status: design frozen; campaign next in this cycle. Verdict appended below when the
numbers exist.*

---

## §7. CAMPAIGN RESULT (C5018, same cycle) — **THE WINDOW EXISTS. GO with target.**

Instrument: `scripts/h10_c2_harvest_sim_c5018.py`, artifact `results/h10_c2_harvest_sim_
c5018.json` (270 configs, exact evolution, convergence 32-vs-64 steps at 1e-12).

**Two dead-observable catches en route, kept in the instrument's docstring** (the fence had
to be debugged before its zeros meant anything): (1) the ⟨X_{s2}⟩ response after a full X
kick is X-parity-odd — identically zero at ANY (d,t), faking "spacelike" everywhere; the
linear response goes as sin(2ε), so the π/2 kick sits at the NULL — the hardware arm uses
ε=π/4 where it is maximal; (2) the density response is ALSO identically zero at half filling
(particle-hole cancellation). The working certifier is the retarded X-X commutator —
which is exactly the channel the detectors couple through. **Rule: a cone certifier must be
shown NONZERO on a causal case before its zeros certify anything.** With the live certifier
the crude ratio fence killed every big-N row (exchange 10-20x signal) — which forced the
better design:

**THE CUT DECOMPOSITION (fence upgraded to a construction):** evolve with the bond between
the detectors REMOVED while keeping the uncut vacuum as the initial state. Zero exchange
channel exists by construction; N_cut is pure vacuum-resource harvest; N_full − N_cut IS the
exchange contribution, exactly. No Lieb-Robinson tail bound to argue — and the cut arm is
directly flyable (drop the crossing-bond Trotter terms).

**Operating point (frozen target):**

> Ω=1.5, d=3 (s1=2, s2=5), T=2.5, λ=0.6, top-hat switching:
> **N_cut = 0.0484** (N_full = 0.0423 — the exchange channel *reduces* net entanglement here,
> exch_frac 0.14); product-state control **exactly 0**; 5σ tomography ≈ 11k shots/setting —
> well under the 50k kill bar.

**Honest results carried with the GO:** (a) the verified Pozas-Kerstjens/Martín-Martínez
prediction "smooth ≫ sudden" did NOT port to this lattice regime — top-hat beat sine in
every shortlist row (window comparable to ramp scale; the continuum result concerns UV
transients a lattice at these scales does not have). Imported prediction tested, answer
negative, reported. (b) All viable rows sit at d=3; d≥4 harvests are below measurability at
L=8. (c) Depth at L=8 prices to ~745 routed 2q — OVER the §4 ceiling; **L=6 re-sweep is the
named prereg item** (projected ~380 routed with Givens-exact free-fermion vacuum prep — the
XX ground state is a Slater determinant, exactly preparable, no variational error), plus
Trotterized as-flown bars (the C1 like-for-like discipline) and the tomography budget table.

*Scout verdict: GO — the sharpest operational form of the Reznik claim: detectors coupled to
provably non-interacting halves become entangled by the vacuum they share, the product-state
twin yields zero, and the exchange contribution is measured, not bounded. Remaining before
prereg: L=6 depth-compliant re-sweep, Givens prep pricing, as-flown bars.*

## §8. DEPTH LEG (C5018, same cycle) — L=6 honest negative; the r-door passes the wall

**L=6 re-sweep** (`h10_c2_harvest_sim_c5018_L6.json`, 180 configs): **NO cut-evolution
harvest exists** — N_cut = 0 in every configuration. The shrunk halves (3 sites each) plus
edge proximity do not hold the cross-cut vacuum correlations the detectors tap. The naive
depth-compliance route is dead, and recorded so no future cycle re-tries it.

**The second door (don't-stop-at-the-first-wall): keep L=8, cut the Trotter step count,
absorb the bias into as-flown bars** — the C1 §10 discipline. Circuit-faithful 2nd-order
stepping (`h10_c2_asflown_r_c5018.py`; KA: r=64 reproduces the exact campaign N_cut at
3.8e-6):

| r | N_cut (as-flown) | N_full | logical 2q | routed ~1.6x |
|---|---|---|---|---|
| exact | 0.04835 | 0.04225 | — | — |
| 12 | 0.04851 | 0.04238 | 520 | 832 |
| 8 | 0.04865 | 0.04251 | 360 | 576 |
| **6** | **0.04876** | **0.04268** | **280** | **~448 ✓ under ceiling** |

The harvest observable is remarkably Trotter-robust: the r=6 bias is +0.9% on N_cut, the
N_cut > N_full ordering (the exchange-damages-the-harvest specimen) is preserved, and the
r-trend is smooth and monotone. **Route frozen: r=6 circuit-faithful o2 stepping; as-flown
bars N_cut = 0.0488, N_full = 0.0427.**

**C2 status: GO — PREREG-READY except one named construction item:** the Givens-network
vacuum prep (the L=8 half-filled XX ground state is a Slater determinant — exactly
preparable, no variational error; ~16 Givens rotations ≈ 40 logical 2q, INCLUDED in the
table's totals). The prereg must construct the actual angles and KA the compiled prep
against the exact vacuum, then freeze arm bars (A2 causal, A4 product, A5 cone at ε=π/4,
A6 books) from the r=6 as-flown pipeline, with the tomography shot table. Depth verdict:
the C1-calibrated ceiling is MET at the flyable point — the NO-FLY's budget, applied twice
in one scout, priced one design out (L=6) and one design in (r=6).
