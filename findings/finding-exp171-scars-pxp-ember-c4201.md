# Quantum many-body scars on silicon — a state that refuses to forget, tested as an anomaly (Ember, C4201)

**Creator directive (2026-07-18):** *"fly the scars"* — the advisor-endorsed deeper exotic flight,
the session's deepest. **Job** `d9dtuf9htsac739dhi4g`, `ibm_fez`, 35 circuits (5 inits × step 0..6),
4000 shots, **260 CZ** deepest. **Pre-reg** (0.50, frozen in manifest): `F(scar) − max_generic F > 0.05
AND Neel(scar) − max_generic Neel > 0.05`. **Verdict: HELD.**

---

## The phase

Quantum many-body scars are a weak-ergodicity-breaking exception to thermalization: a few special
initial states evade the chaotic bath and *revive*. In the PXP model (Rydberg blockade, no two adjacent
excitations, `H = Ω Σ P_{i−1} X_i P_{i+1}`), the Néel state |Z₂⟩=|101010⟩ quenched under the dynamics
collapses its order and then brings it back — a coherent revival at t≈4.8. N=6, Trotter dt=0.8, 6 steps.

## The honest test — anomaly vs an ensemble, not a hand-picked control

Building this, the truth-gate exposed the trap: **at N=6 the constrained Hilbert space is only ~21-dim,
so revivals are *generic*** — my own scan found generic states reviving F = 0.04…0.49. Selecting the
one clean thermalizer (|100010⟩, F=0.04) as "the control" would have manufactured an 0.80-vs-0.04 gap —
the **selected-reference confound this campaign has now caught five times** (matched-control duration
C4196, estimator C4198, decay baseline C4199, borrowed per-qubit CZ C4199, and here the cherry-picked
control). The advisor flagged it before submit. So the real scar question was flown instead: **is |Z₂⟩
anomalous against the whole ensemble?** |Z₂⟩ vs four generic controls (|100010⟩, |101000⟩, |001010⟩,
|000000⟩ — spanning the range, including the toughest) in one job, same depth.

## Result

| init | role | F[6] | Néel \|m_s\|[6] |
|---|---|---|---|
| **101010** | **SCAR** | **0.229** | **0.307** |
| 101000 | generic | 0.115 | 0.177 |
| 000000 | generic | 0.105 | 0.030 |
| 001010 | generic | 0.065 | 0.147 |
| 100010 | generic | 0.019 | 0.031 |

- **|Z₂⟩ is the outlier** in both observables: its return probability (F: 0.97 → 0.00 through steps
  2–4 → **0.229** at step 6) and its revived Néel order (0.307) both exceed the *entire* generic range.
- **Anomaly = scar − max-generic: fidelity +0.114, Néel +0.130** — both clear the 0.05 gate. This is
  a demonstrated anomaly, not a selected contrast.

## Honest suppression — the C4200 correction, applied

The hardware anomaly is well below the noiseless (F +0.305, Néel +0.391), and that is *expected*, not a
failure: **a difference of expectations scales by the survival factor s, it does not cancel it.** Under
global depolarizing ⟨Z⟩_hw = s·⟨Z⟩_ideal ⇒ Δ_hw = s·Δ_ideal (only a *ratio* cancels s — why Exp151b's
P_hw/P_ideal genuinely was baseline-robust). At 260 CZ on the actual selected qubits (mean CZ 0.00200,
priced by reading `properties()` on the transpiled layout — the C4199 lesson applied to my own
power-calc), s ≈ 0.594, so the noiseless +0.39 Néel anomaly is expected near +0.23; the measured +0.13
is further suppressed by readout on the 6-qubit return probability and coherent Trotter error at depth.
**What survived is the ordering** — |Z₂⟩ still revives above every generic state. (This corrects the
Exp170/C4200 wording that called a contrast "baseline-robust"; a contrast is *suppressed-not-destroyed*,
and the ordering is what carries through depth.)

## Method

1. **Self-verifying:** I hold the initial states and the PXP dynamics; the truth-gate reproduces the
   revival, and the revival sits at t≈4.8 across dt = 0.4/0.6/0.8 — so it is the real PXP scar revival,
   not a Trotter resonance.
2. **Matched on the scar axis:** all five arms run the identical PXP circuit; only the initial state
   differs — the axis the scar lives on.
3. **Ensemble, not a control:** the claim is anomaly against the generic range, so no single reference
   can be cherry-picked to inflate it.
4. **Reachability priced on the actual qubits** (260 CZ, s≈0.59), not a borrowed rate.

## Fence

Finite chain (N=6 — small Hilbert space, hence the ensemble test rather than scar-vs-one-thermalizer),
coarse Trotter (dt=0.8; revival verified across dt), 260 CZ at the edge of the coherence wall so the
anomaly is real but modest (scar F 0.23 vs best generic 0.12). A hardware **signature** of the scar
anomaly, not a thermodynamic proof.

## What the universe answered

A single special initial state — the Néel |Z₂⟩ — revives its memory above every generic state in a
Rydberg-blockade chain, and the anomaly survives to ~260 CZ on real silicon. The exotic-phases wing now
holds four phases: the DTC (bulk time-order), anyon braiding (topological order, Whisper), the Floquet
SPT edge mode (boundary-only order), and **many-body scars (weak ergodicity breaking)** — each a
different way order defies the expectation of thermal chaos.

**Numbering:** new experiment (Exp171), exotic-phases wing; the session's deepest flight.
