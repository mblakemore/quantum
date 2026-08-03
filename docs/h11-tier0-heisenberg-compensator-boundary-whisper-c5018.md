# H11 Tier-0 №2 — The Heisenberg-compensator boundary: classical-concentration floors, derived

*Whisper C5018, on Creator "$0 is auto go" (general#4223). Charge (H11 cell 6 / Tier-0 №2):
derive the classical-concentration bound tight enough to gate the ICO-refrigeration flight
against — the boundary any classical concentrator can reach, so "cooling past every classical
concentrator" becomes a number, not a slogan. Primary sources pinned this cycle: Raeisi–Mosca,
PRL 114, 100404 (2015) / arXiv:1407.3232 (asymptotic HBAC limit — Eqs. 2–6 extracted verbatim
from the PDF); Clivaz–Silva–Haack–Brask–Brunner–Huber, PRL 123, 170605 (2019) /
arXiv:1903.04970 (universal attainable cooling bound — Eqs. 1–2 extracted verbatim). The
single-round floor below is derived here, not quoted.*

## 0. The three-bar structure

A flight that claims "colder than classical" needs three bars, from inside out:

1. **BAR C (the gate): the resource-matched classical-concentrator floor** — what the best
   *diagonal* protocol reaches with the same qubit count and the same bath-contact budget as
   the ICO branch. This is the bar the flight must beat at 5σ. Derived in §2 (single-round,
   closed form) and §3 (multi-round asymptote, Raeisi–Mosca).
2. **BAR U (the envelope): the universal cooling bound** — what *any* definite-causal-order
   protocol (coherent or incoherent, any paradigm, infinite cycles) can reach with a machine
   of maximum gap E_max and bath at β_R. Quoted in §4. The ICO claim's honest habitat is the
   region between BAR C and BAR U; anything that appears to beat BAR U must show where the
   extra resource enters (§5).
3. **The measured inputs**: native excited population p and machine gaps are measured
   **in-job** (floor doctrine: derive → in-context → same-job). Every number below is a
   formula slot; the flight fills it from its own calibration pubs, never from a datasheet.

## 1. The classical-concentrator class, defined before any bar is stated

A **classical concentrator** on N qubits is any protocol whose every step is diagonal in the
computational basis: reversible permutations of the 2^N joint populations (X/CNOT/Toffoli
networks = the classical reversible circuits), stochastic mixtures thereof, and RESET of
designated qubits by fresh bath contact. No coherences are created or consumed. This class
contains sort-based cooling, all of heat-bath algorithmic cooling (HBAC/PPA), and every
"just relabel the cold branch" cheat. Post-selection is excluded from the class definition and
priced separately (§5) — the same F118 herald accounting the ICO branch is held to.

*Why permutations suffice for the optimum:* any doubly-stochastic map on populations is a
convex mixture of permutations (Birkhoff), and the target — ground population of one output
qubit — is linear in the population vector, so the optimum is attained at a permutation.

## 2. BAR C, single contact: the exact sort floor (derived)

Setup: N i.i.d. qubits, each with ground probability q = 1−p (p = excited population,
p < 1/2), one designated output qubit, **no bath refresh** (single-contact budget — the
resource envelope of a one-pass ICO branch). A permutation routes 2^{N−1} of the 2^N joint
states to the output-ground half; the output ground population is the sum of the routed
probabilities; the optimum routes the 2^{N−1} **largest** — achievable by the explicit sorting
permutation, hence tight, not just an upper bound.

For i.i.d. qubits the joint probabilities sort by excitation number k (weight q^{N−k}p^k,
multiplicity C(N,k)). Filling the half-register greedily:

| N | top-half composition | ground-pop floor q_out | excited floor p_out (exact) | leading order |
|---|---|---|---|---|
| 2 | k=0 (1) + 1 of k=1 (2) | q² + qp = q | **p_out = p — no cooling at all** | p |
| 3 | k=0 (1) + all k=1 (3) = 4 = 2^{N−1} exactly | q³ + 3q²p = q²(1+2p) | **p_out = 3p² − 2p³** | **3p²** |
| 4 | k=0 (1) + k=1 (4) + 3 of k=2 (6) | q⁴ + 4q³p + 3q²p² | **p_out = 3p² − 2p³ — exactly equal to N=3** | **3p²** |
| 5 | k=0 (1) + k=1 (5) + all k=2 (10) = 16 exactly | q⁵ + 5q⁴p + 10q³p² | **p_out = 10p³ − 15p⁴ + 6p⁵** | **10p³** |

Two structural facts fall out exactly, not approximately: **N=2 gives NO single-contact
cooling** (q_out = q; the first nontrivial concentrator is N=3 — so any 2-qubit "classical
control" arm must read *exactly* the native temperature, a free control-design check), and
**N=4 buys nothing over N=3** (3q²p²+4qp³+p⁴ expands to exactly 3p²−2p³ — the fourth qubit's
k=2 tier splits across the cut with zero net gain; the next real step is N=5's 10p³).

The clean rows (N=3 and N=5, where the binomial tiers fill the half-register exactly):

- **N=3: p_out = 3p² − 2p³** — at p = 0.02 (representative; measured in-job at flight time):
  p_out = 1.184×10⁻³, a 16.9× reduction. **This is the flight's primary bar.**
- **N=5: p_out = 10p³ − 15p⁴ + 6p⁵** — at p = 0.02: 7.77×10⁻⁵ (257×).

The general pattern: with the half-register filled through tier k*, the floor's leading term is
C(N−1, k*)·p^{k*+…} — cold fast. The classical floor at superconducting native polarization is
**already deep**, which is precisely why this cell demanded the derivation before any flight:
the gap to be located is narrow and quantitative, not rhetorical.

## 3. BAR C, unlimited contacts: the HBAC asymptote (Raeisi–Mosca, pinned)

With bath refresh allowed (k → ∞ contacts), the optimal diagonal protocol is the
partner-pairing algorithm, and its limit is proven (PRL 114, 100404, extracted verbatim from
arXiv:1407.3232):

- Asymptotic state condition (their Eq. 2): p∞_i·e^{−ε} = p∞_{i+1}·e^{ε} ∀i, over the 2^n
  computation-register basis states ordered by energy, ε = reset/bath polarization.
- Normalization (their Eq. 3): **p∞_0 = (e^{−2ε} − 1)/((e^{−2ε})^{2^n} − 1)** — the full
  asymptotic state is the geometric ladder p∞_i = e^{−2iε}p∞_0 ⊗ ρ_R (their Eq. 4).
- Small-ε cooling limit (their Eq. 5): first-qubit polarization **P = 2^{n−1}·ε** for n
  computation qubits + one reset qubit; effective temperature T_eff = (δ/Δ)·T_B/2^{n−1}
  (their Eq. 6).

Regime note the NMR-era folklore gets wrong on our hardware: superconducting native
polarization is ε ≈ 0.96, nowhere near the small-ε regime — the **exact** Eq. 3 form applies,
and it saturates almost completely (p∞_0 → 1 doubly-exponentially in n at large ε). Therefore:
**an unlimited-contact classical concentrator is essentially unbeatable on this hardware**, and
the only honest ICO claim is the **resource-matched** one — same N, same contact budget
(BAR C §2), stated as such in the prereg. A flight advertised against the unlimited-contact
floor would be advertising against a bar it cannot beat; a flight that hides the contact budget
is moving the bar. Both are now named defects.

## 4. BAR U: the universal envelope (Clivaz et al., pinned)

Extracted verbatim from arXiv:1903.04970 (PRL 123, 170605): for a target qubit cooled by a
machine with maximum energy gap E_max attached to a reservoir at inverse temperature β_R —
valid **for any control paradigm and machine size, after infinite cycles**:

- **p*_0 = 1/(1 + e^{−β_R·E_max})** (their Eq. 1) — the attainable upper bound on ground
  population;
- for a d_S-dimensional target, the final eigenvalue vector is majorized by the Gibbs-like
  ladder at rate e^{−β_R E_max} (their Eq. 2).

The slot to fill in-job: E_max of *our* machine register (device gaps, summed as the protocol
actually couples them) and β_R of the *measured* fluid, not the fridge sticker.

## 5. Where ICO must sit, and the accounting fence

The certifiable claim has exactly one honest shape: **delivered temperature below BAR C
(resource-matched, §2) at 5σ, with the F118 herald machinery pricing every post-selection, and
the result situated relative to BAR U (§4).** Three outcomes, all pre-named:

- **Below BAR C, at-or-below BAR U**: the Trek claim, correctly fenced — ICO beats every
  classical concentrator with the same resources, within the universal envelope. This is the
  target region and it is *narrow* (at p = 0.02, N=3: the branch must deliver p < 1.18×10⁻³).
- **Below BAR U (apparent)**: not a triumph — a resource-accounting alarm. The known critique
  of ICO-thermodynamics claims is that the switch's control measurement smuggles in work or
  purity; if the flight reads colder than the envelope, the certification must show where the
  resource enters (herald costs, control-qubit purity burn), or the verdict is
  QUARANTINED-NOT-QUALIFIED.
- **Above BAR C**: the cell dies at $0 + one cheap flight — and the derivation already warns
  this is live: the classical floor at native polarization is deep. If design-time simulation
  of the ICO branch cannot clear 3p²−2p³ on paper, the flight is not flown and the cell is
  closed honestly (price-the-remedy: the audit that kills a flight pays the same as one that
  clears it).

## 6. What Tier-0 №2 delivers, in one line each

- The gate bar exists: **p_out^classical(N=3, single contact) = 3p² − 2p³**, exact, derived,
  resource-matched — the number the ICO branch must beat.
- The unlimited-contact bar is proven unbeatable here (Raeisi–Mosca exact form at ε ≈ 0.96) —
  so the prereg language is constrained *before* it is written: resource-matched claims only.
- The universal envelope (Clivaz Eq. 1) is pinned with its in-job measurement slots, and the
  beyond-envelope outcome is pre-classified as an accounting alarm, not a discovery.
- N=2 classical arms read native temperature exactly — a free control-design fact.
- Next: cell 6's flight design gates on a $0 design-time simulation of the ICO branch against
  3p²−2p³ at the device's measured p. If it clears on paper, a prereg follows; if not, the
  cell closes.

*$0 as charged. — Whisper C5018, stamped claude-fable-5.*
