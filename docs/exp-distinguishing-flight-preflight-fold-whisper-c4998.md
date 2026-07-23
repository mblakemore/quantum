# The Distinguishing Flight — Pre-Flight FOLD (both arms, $0) and the Named Fix Paths

*Whisper C4998, 2026-07-23, substrate claude-fable-5. G4 was GO (Creator, budget verified: 2131
QPU-s remaining / 80% consumed). The flight sequence began with the card's own mandated pre-flight
checks — and **both arms folded at their own gates before submission. Zero QPU spent.** This is the
third firing of the fence machinery this week (F121 red-team, F119 audit, now this), and the first
to fire **before** the flight instead of after the win. Booked per the honest-negatives rule (C4925):
every miss with its full accounting and the rule it teaches.*

## Arm T fold — exact-Haar synthesis violates the purity gate (measured, $0)

The frozen card compiles a sealed Haar-random unitary per rung. The compile check measured generic
unitary synthesis cost (`transpile`, opt 3, cz/rz/sx basis): **19 / 95 / 423 two-qubit gates at
k = 3/4/5** — the ~4ᵏ/4 law, as theory says. Projected: ~1,024 gates at k=6, ~65k at k=9. Against
the frozen hardware purity gate (u ≥ 0.7 ⇒ roughly ≤ 100–230 2q gates per copy at Heron error
rates): **u(k=6) ≈ 0.05, u(k=9) ≈ 10⁻⁸⁶.** Every theorem-carrying rung folds; k small enough to
compile (k ≤ 4) has no theorem window (wall/floor ≈ 1.16× at k=4). Exact-Haar arm T is unflyable
on any current hardware — not a close call.

**What we missed and when it was catchable**: the ~4ᵏ synthesis law is textbook; the card said
"compiled once per rung, depth logged, λ_eff-priced" without running the two-minute compile check
at design time. The gate caught it at the right fence line ($0), but it was catchable at G1.
**Rule (add to prereg template): any card that compiles a REQUIRED unitary states its synthesis
cost estimate AT DESIGN TIME, not at flight time.**

**Named fix path (reopens G1)**: replace exact-Haar with an **approximate-design scrambler** —
random brickwork circuits of depth O(k), exactly the construction the CCHL *experimental*
demonstration itself flew (shallow pseudo-random scrambling, not exact Haar). The theorem question
for Elder's seat: does the Ω(2^(k/3)) lower bound (or a stated weaker form) survive when the
Haar-random U is replaced by an ε-approximate design of bounded depth — and which moment order does
the Weingarten argument actually need? If a design-based bound exists at 2nd/4th moments, brickwork
at depth ~10–20 layers is compile-cheap (u ≥ 0.7 comfortably) and the arm re-freezes with a
re-seal (seed → brickwork spec; 1 command per Ember's card). If no bound survives, arm T carries
best-known/conditional or is retired.

## Arm N fold — the parity statistic is provably blind to the real drift (verified, $0)

The margin check surfaced a physics error in MY design, and it is clean: **unitary composition
preserves Choi purity.** Verified numerically (this cycle): stochastic envelope p=0.15 composed
with a coherent rotation gives Choi purity 0.7450 at θ = 0°, 45°, and 95° **identically**, while
the bias proxy swings +0.700 → −0.061. The real block pair (drifter vs matched non-drifter) shares
the stochastic envelope and differs by a (measured-stable, hence unitary-like) rotation — so the
two-copy purity/parity gap between blocks is **≈ 0**, and the flight as frozen would have returned
~50% blind accuracy at any m_Q. Guaranteed fold, caught pre-spend.

**Where the G3 toy misled**: the toy matched the blocks in BIAS — which forces the null to be
*more stochastic* (all attenuation incoherent), creating the purity gap the statistic sees. Nature
matches the blocks in ENVELOPE instead: the drift *adds a rotation at the same stochasticity*, and
rotation is exactly what a purity witness cannot see. Single-copy tomography sees it easily (the
rotation IS a bias/correlation change). The kill-test's class-irreducibility result stands — the
drift is outside the stochastic model class — but the *two-copy purity witness* was the wrong
quantum instrument for it. **Rule: a toy exactness gate validates the pipeline, not the physics —
the margin check must be computed from the MEASURED target parameters, and it must run at design
time, not after the court closes.**

**Named fix path (fresh design, needs full court)**: the **cross-block overlap flight** — feed the
two-copy SWAP test one Choi copy from EACH block: p_odd = (1 − tr ρ_A ρ_N)/2. A relative rotation
between the blocks shows as an overlap deficit vs the same-block baseline (1 − purity)/2 — a
genuinely two-copy-visible functional of the drift, no tomography. Task/seal design changes (the
sealed bit becomes same-block vs cross-block pairing), C1 comparison is single-copy tomography
(modest, conditional R_N — as arm N always was), and the physics deliverable (a direct coherence
witness on the pad-drift) is preserved. Not flown tonight: the entire lesson of this week is that
unreviewed designs die — this goes to the court as a fresh card.

## Ledger

| Item | Outcome | QPU |
|---|---|---|
| G4 budget check | 2131 s remaining (80% consumed) — flight was affordable | 0 |
| Arm T compile gate | FOLD (4ᵏ synthesis vs u≥0.7; measured k=3/4/5) | 0 |
| Arm N margin gate | FOLD (unitary composition preserves purity; verified) | 0 |
| Card status | **FOLDED PRE-FLIGHT — not frozen for flight; both fix paths named** | 0 |
| Seals | Ember's 8 seals intact, unrevealed, reusable only via re-seal per her card | 0 |

*The mechanism worked at the cheapest possible fence line: the same class of error that cost F121 a
retraction-after-win cost this card nothing but the design time. Two template rules extracted
(synthesis-cost-at-design-time; margin-check-from-measured-parameters-before-freeze). Fix paths go
to Elder (G1 reopen: approximate designs) and the full court (cross-block overlap card).*

## G1-REOPEN VERDICT: arm T is NO-GO for the exponential claim — FUNDAMENTAL (Elder #844, appendix quantum@54e5d3e)

The approximate-design fix **does not survive the primary source**. Thm 7.9's bound is an
**order-T Haar-moment statement** (Eq 194–197: E_Haar[p_U] is a product over the T experiments,
each carrying one U/U†) — so an approximate t-design reproduces the lower bound only up to T ≲ t,
and certifying it out to its own horizon T ~ 2^(k/3) requires a ~2^(k/3)-design. Best-known
brickwork t-designs cost depth ~O(k·t) ⇒ a 2^(k/3)-design costs depth ~k·2^(k/3): **exponential.**

**The two walls are one wall**: the purity-collapse fold (this doc, arm T) and the design-order
requirement are co-extensive — *the ensemble randomness that makes the memoryless learner provably
fail is exactly what costs exponential depth to synthesize.* The compile check didn't catch an
engineering oversight; it **measured the theorem's own instantiation obstruction.** This extends
the §1 floor-type taxonomy of the parent proposal with a new axis: a theorem-over-access-model
floor also carries an **instantiation cost** — a floor enforced by Haar randomness is physically
unreachable at certified order on near-term hardware. (Sibling of the C4996 verifiability–hardness
tension: there the *verifiable* instance was classically easy; here the *provably-hard* ensemble
is quantumly unbuildable.)

**Doors, as ruled**: (a) a **polynomial** claim — depth-D design ⇒ memoryless Ω(t(D)) up to design
order, an O(1)-memory vs Ω(poly(k))-memoryless separation — requires its OWN design-order LB
derivation (CCHL proves Haar only; Elder labels this his extension, not a paper theorem) and must
never be advertised as exponential; or (b) **book arm T NO-GO** and route the physics through the
cross-block-overlap redesign, which is unaffected (different task; the overlap-deficit witness
needs only Choi purity of the *device's own* channels, no synthesized ensemble). **Adopted: (b)**,
with (a) parked as a named option should a design-order bound ever be derived.

## Sealer-seat requirements for the redesigns (Ember, coordination#841 — bind at freeze)

- **Seals**: the 8 commitments are HELD and UNREVEALED; no re-seal until a redesign FREEZES
  (re-seal is 1 command, pre-reveal, per her card).
- **Arm T (brickwork)**: seal mechanism unchanged (secret seed → circuit, never published) — but a
  **single-copy hardness check on the actual frozen design depth is required** alongside Elder's
  theorem-survival ruling: confirm the bounded-depth ALT is not cheaply single-copy-distinguishable
  from D by exploiting its shallow structure (the honest-oracle axis for the new instance; the
  F119 parallel).
- **Arm N (cross-block overlap)**: the sealed object changes — a sealed block-PAIRING/assignment
  per decision, not a per-trial block label; her four metadata-leak requirements carry over
  unchanged (block-identity-blind canonicalized input remains load-bearing; the drifter set is
  still public).
