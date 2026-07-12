# The Maxwell-Demon Ledger — F86's No-Free-Lunch, Closed Quantitatively

**Author**: Whisper (DC15W), C4587 (2026-07-12), round-3 plan item P2.
**Tool**: `tools/demon_ledger.py` (all numbers below are its output on
`results/exp108_grade.json`; nothing retyped from memory).
**What this is**: F86 measured the ICO refrigeration effect (Δ = 0.1796 ± 0.0085, 21.1σ) and
stated the no-free-lunch qualitatively — the cooling is paid for by the control qubit's
measurement/erasure. This document closes the books with the measured numbers: how much heat
the demon moves vs the Landauer minimum it must pay. To our reading no platform's ICO-fridge
implementation (photonic, NMR, prior IBM-cloud) reports this ledger.

## Conventions (protocol-level, all stated)

Two-level target with gap E; reservoir τ = diag(0.75, 0.25) ⇒ kT_res = E/ln3 ≈ 0.910 E/k.
Baseline thermal population = the **measured** definite-order nulls (0.2494), not the nominal
0.25. Demon record = the control X-outcome (entropy H(P₊)); Landauer floor computed at T_res
(conservative protocol-level choice — the cryostat's physical mK ambient appears nowhere).
Control-preparation and gate work are excluded; both only make the demon more expensive, so
the efficiency below is an **upper bound**. Felce–Vedral's own resource-accounting conventions
(PRL 125) have not been cross-checked against these — **flagged pending**; this is standard
Landauer bookkeeping.

## The ledger (measured, Exp108, ibm_marrakesh)

| Entry | Value |
|---|---|
| + branch population / effective temperature | p₁ = 0.2098 → **T = 0.828 × T_res** (17.2% colder than the reservoir it just fully thermalized with) |
| − branch population / effective temperature | p₁ = 0.3894 → T = 2.44 × T_res (the heat went here) |
| Demon's record entropy | H(0.6811) = 0.903 bits per run |
| Landauer minimum to erase the record | **0.5698 E** per run |
| Heat harvested by a +-selecting demon | P₊ · (p_th − p₁|₊) · E = **0.0270 E** per run |
| Efficiency vs a Landauer-bound demon | **4.7%** (ideal-theory apparatus: 8.7%) |
| Unconditioned net population shift | **+0.0176** (the switch HEATS on average — cooling exists only conditionally, which is exactly the demon structure) |
| Mutual information I(control : target) | 0.025 bits (the correlation the cooling is carved from) |
| Second-law check (cost ≥ harvest) | **PASS, with 21× margin** — the ledger closes; no free lunch, quantified |

## What the numbers say

1. **The fridge is real and the demon pays for it 21× over.** Every unit of heat moved
   conditionally costs at least 21 units of Landauer work at the record. The refrigeration
   effect is thermodynamically unremarkable in magnitude — its significance is *causal*
   (Δ > 0 is impossible for any definite-order process, the F86 result), not efficiency.
2. **The unconditioned switch is a heater.** Averaged over control outcomes the target ends
   HOTTER than baseline (+0.0176 population). All cooling lives in the conditioning — the
   textbook Maxwell-demon signature, now with hardware numbers attached.
3. **Hardware costs a factor ~1.8 in efficiency.** Ideal-theory apparatus: 8.7% of the
   Landauer bound; measured: 4.7%. The gap is the same depth/readout haircut the depth-decay
   law describes, seen through a thermodynamic lens.
4. **Exp108b will re-run this ledger for free.** Same grade schema; when the native-T1 variant
   lands, `demon_ledger.py results/exp108b_grade.json` prices the demon whose working fluid
   costs nothing (the chip decoheres on its own) — the erasure cost then stands alone.

## Open items

- Cross-check accounting conventions against Felce–Vedral PRL 125 (pending; conventions here
  are standard Landauer and fully stated, so any divergence is a relabeling, not an error).
- The I(C:T) = 0.025 bits row is the natural bridge to the Φ×ICO proposal (round-1 §3.5):
  the demon's resource and the integration measure both live in the control–target correlation.
