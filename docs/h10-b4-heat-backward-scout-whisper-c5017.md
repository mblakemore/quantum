# H10-B4 SCOUT — Heat Flowing Backward: the arrow as custody of correlations

*Whisper C5017, 2026-08-01, substrate claude-fable-5. $0 scout per H10 §4 (next unstarted item);
run under the Creator's keep-going directive in the same live session as the C1/B1 completions.
**VERDICT: GO — bars frozen from exact theory; one named engineering choice to prereg.***

## 1. Literature pin

K. Micadei, J. P. S. Peterson, A. M. Souza, R. S. Sarthour, I. S. Oliveira, G. T. Landi,
T. B. Batalhão, R. M. Serra, E. Lutz, *Reversing the direction of heat flow using quantum
correlations*, **Nature Communications 10, 2456 (2019)**, arXiv:1711.03323. NMR, two spins-1/2 in
local thermal states at different effective temperatures with an initial thermally-coherent
correlation term; spontaneous cold→hot energy flow observed; the enabling trade quantified as
correlations-consumed-for-reversal (information-theoretic ledger). Our flight is the gate-model
chip version under the F94/F95 thermo-court grammar.

## 2. Exact two-qubit theory — operating point and bars (frozen tonight;
`results/h10_b4_heatback_bars_c5017.json`)

Setup: H_i = (ω/2)Z, ω=1; A hot (β_h=0.5), B cold (β_c=2.0); state ρ = ρ_A⊗ρ_B + χ with
χ = α|01⟩⟨10| + h.c.; positivity bounds **|α| ≤ 0.157** at these temperatures. Interaction
U(θ) = exp(−iθ(XX+YY)/2) — the excitation-exchange (iSWAP-family) gate, natively cheap.

**Operating point: α = 0.157·i, θ = 2.35.**

| Quantity | Exact value | Reads as |
|---|---|---|
| ΔE_cold, correlated arm | **−0.0262** | the cold qubit LOSES energy — flow is cold→hot |
| ΔE_cold, uncorrelated control (χ=0, same pair) | **+0.1308** | normal hot→cold |
| Separation | 0.157 | corr-vs-control, the headline |
| Mutual information, before → after | 0.278 → 0.214 | **the reversal CONSUMES correlations** — the ledger receipt, measurable by 2-qubit tomography |
| Shots to 5σ on the reversal SIGN | ~9,100 | cheap |
| Shots to 5σ on the corr-vs-control separation | **~254** | nearly free |

## 3. Design (arms, all one chip, one session)

1. **Correlated arm**: prepare ρ(α_max), apply U(θ=2.35), measure ⟨Z_B⟩ (and ⟨Z_A⟩ for the
   energy-conservation cross-check: what cold loses + hot gains + interaction term must book).
2. **Uncorrelated control**: identical prep WITHOUT χ, same U(θ), same session — the pre-registered
   single-difference control (F94/F95 grammar).
3. **θ-sweep**: 5 points through 2.35 — the reversal magnitude follows the exact curve, the
   meter's calibration leg.
4. **Ledger leg**: 2-qubit state tomography before/after at the OP — ΔI(A:B) = −0.064 predicted;
   the correlations-pay-for-it receipt, closing the books the way F94/F95 closed the engine's.

**Why it completes the thermo triangle** (H10 §3, B4): F97 = correlations buy energy below local
empty; F94/F95 = causal order buys work; B4 = correlations buy the ARROW'S DIRECTION. Together:
time's one-way-ness is a resource ledger, and we can post entries to it.

## 4. Fences

Effective temperatures are PREPARED STATES on a chip, not baths — said exactly so (the F94/F95
flat-bath court showed how). The correlation term is PREPARED, not harvested — this flight makes
no vacuum claim (C2 is the harvesting flight). Single pair, single chip. No cosmology: this is
the two-spin arrow, a chip analogue of the Micadei experiment, and the claim is the pre-registered
sign flip plus its ledger — nothing about time's arrow at large.

## 5. Remaining before prereg (one item, named)

**State-prep route for ρ(α):** the χ term is a coherent |01⟩⟨10| element, so ρ is a genuinely
mixed correlated state (rank 4 generically) — prepare via **2-ancilla purification isometry**
(4 qubits total, trivial compile at this size) or via a **classically-mixed ensemble of entangled
pure-state circuits** (per-shot sampling; needs the mixture to reproduce χ exactly — the
decomposition exists and should be chosen for hardware cheapness). The choice and its measured
prep fidelity belong to the prereg. Everything else is frozen above.

## 6. PREP ROUTE FROZEN (C5017, same session) — B4 is PREREG-READY

Eigendecomposition of ρ(α_max) (`results/h10_b4_prep_route_c5017.json`; reconstruction error
5.6e-17 = the KA gate): four pure states, probabilities {0.548, 0.407, 0.045, 0.0001} — two
PRODUCT states (0 CX) and two entangled (1 CX each), 95.5% of the mass in two states.
**Route: classical mixture — per-shot sample one of four ≤1-CX circuits with the listed
probabilities.** The 2-ancilla purification is rejected as strictly costlier. No open items
remain: every gate, arm, bar, and now the preparation are frozen from exact theory.

*Scout verdict: GO — PREREG-READY. The cheapest certifiable new physics on the H10 board:
254 shots to the headline, four ≤1-CX prep circuits, one iSWAP-family gate.*
