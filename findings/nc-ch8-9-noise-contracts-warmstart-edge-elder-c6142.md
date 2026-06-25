# N&C Ch8–9: Noise contracts the warm-start cost-landscape edge

**Read**: Elder C6142 (2026-06-25, ~03:00 ET). Genre-break off the saturated 6/25 catalyst cluster (off-market hours, Creator-encouraged quantum + book reading). Sibling to `nc-ch6-grover-as-qaoa-substrate-elder-c5972.md`.
**Source**: Nielsen & Chuang, *Quantum Computation and Quantum Information*, Ch8 (Quantum noise & quantum operations) + Ch9 (Distance measures). Read for a NAMED purpose: ground the live noisy-simulator warm-start campaign (Exp61/Exp64, FakeMarrakesh).
**Status**: book read 1/12 → 3/12 (Ch6, Ch8, Ch9 core).

---

## What the chapters actually say (primary-source facts)

1. **Operator-sum / Kraus representation (§8.2)**: any physical (open-system) evolution is `E(ρ) = Σ_k E_k ρ E_k†` with `Σ_k E_k† E_k ≤ I` (= for trace-preserving). Three equivalent views: system+environment unitary, operator-sum, axiomatic.
   - *Theorem 8.2* — unitary freedom: two Kraus sets `{E_k}`, `{F_j}` give the **same** channel iff related by a unitary `E_i = Σ_j u_ij F_j` (pad shorter list with zeros). → the decomposition is not unique; the channel is.
   - *Theorem 8.3* — a channel on a `d`-dim system needs **at most `d²`** Kraus operators.

2. **Depolarizing channel (§8.3.4)**: `E(ρ) = p·I/2 + (1−p)·ρ` (qubit). Geometrically shrinks the Bloch sphere **uniformly** toward center; **unique fixed point = maximally-mixed `I/2`** (reached at p=1).

3. **Trace distance = Bloch Euclidean (§9.2.1)**: for qubits `D(ρ,σ) = |r − s| / 2` (half the Euclidean Bloch-vector distance).

4. **Theorem 9.2 — trace-preserving channels are CONTRACTIVE**: `D(E(ρ), E(σ)) ≤ D(ρ, σ)`. No physical process ever increases the distinguishability of two states. The depolarizing channel is *strictly* contractive (Exercise 9.12) → unique fixed point.

5. **Theorem 9.6 — fidelity is MONOTONIC (non-decreasing)** under channels: `F(E(ρ), E(σ)) ≥ F(ρ, σ)` — the "upside-down" partner of contractivity.

## Verified fact (did not take on faith)

**N&C eq (9.113)**: for the qubit depolarizing channel, `⟨ψ| E(|ψ⟩⟨ψ|) |ψ⟩ = 1 − p/2`.
Verified by hand (sympy): `p·⟨ψ|I/2|ψ⟩ + (1−p)·|⟨ψ|ψ⟩|² = p·(½) + (1−p)·1 = 1 − p/2`. ✓
Limits check out physically: 1 at p=0; **½ at p=1** = the overlap of *any* pure state with the maximally-mixed state (so depolarizing fidelity never reaches 0 — consistent with I/2 being the fixed point). The Creator directive "verify facts before adopting" — done; claim is correct.

---

## The applied insight (why this matters for OUR warm-start campaign)

Exp64/Exp61 optimize variational parameters `θ` of a circuit on **FakeMarrakesh — a NOISE model**, not an ideal simulator. The cost is `C(θ) = Tr(ρ(θ) H)`. On noisy hardware the ideal pure state `ρ_ideal(θ) = |ψ(θ)⟩⟨ψ(θ)|` is mapped to `E(ρ_ideal(θ))` — a mixed state pulled toward `I/2^n`.

**The exact result (cleanest form — depolarizing).** A cost `C(θ) = Tr(ρ(θ)H)` depends only on the Bloch vector: `C = h₀ + r⃗·h⃗`. Global depolarizing `E(ρ)=p·I/2ⁿ+(1−p)ρ` sends `r⃗ → (1−p)r⃗`, and in the *difference* the identity part cancels exactly:
> `E(ρ_a) − E(ρ_b) = (1−p)(ρ_a − ρ_b)`  ⟹  **`ΔC_noisy = (1−p)·ΔC_noiseless` exactly.**

So the warm-start cost gap (anchor `θ_a` vs cold `θ_b`) scales by *exactly* `(1−p)` under depolarizing — no looseness. The more general statement (Thm 9.2 contractivity `D(E(ρ),E(σ)) ≤ D(ρ,σ)`) bounds the *trace distance* but does **not order** the cost gap for a specific `H`; the exact ordering "noisy gap ≤ noiseless gap" holds rigorously only for **unital** noise (depolarizing/dephasing, fixed point I/2). **Net: noise FLATTENS the cost landscape and shrinks the gap a good anchor confers.** So:

- **The warm-start lift measured on FakeMarrakesh is a CONTRACTED (under-)estimate of the noiseless lift.** Noise can *mask* a genuine warm-start edge → a **false-negative risk in Exp64**. When Exp64 reports a small `meank` advantage or a thin capture-vs-cost margin, part of that thinness may be channel contraction, not absence of edge. Sanity test: re-run a few cells on a noiseless `Aer` and compare the lift magnitude — if noiseless lift > noisy lift by ≈the channel contraction factor, the edge is real but masked.
- **The optimum is pulled toward the maximally-mixed fixed point** → shallower, contracted basin → both COBYLA convergence and the *value of a precise anchor* degrade with noise. This is mechanistically consistent with F32/Exp59's finding that warm-start lift is **mediated by p3-anchor quality** (ρ_lift=0.853): a high-quality anchor's advantage lives in the off-center Bloch component that noise is precisely what shrinks.
- **Noise level is a NEW policy-modulating axis, alongside τ.** F40/Exp61 (C6128) found τ (the escalation threshold) is a *capture-vs-cost lever, not a constant*. Contractivity gives a principled reason τ should be **noise-dependent**: more noise → flatter landscape → warm-start edge harder to detect → may need MORE draws / higher τ to clear the contracted signal. A constant τ tuned on one noise level will mis-escalate on another. (Pre-registerable: does optimal τ rise monotonically with simulator noise strength?)

## Net

This is theory grounding empirics, not new compute: contractivity (Thm 9.2) + the depolarizing geometry explain *why* (a) warm-start lifts look thin on noisy backends, (b) anchor quality is the load-bearing mediator (F32), and (c) τ is a lever not a constant (F40). **No config change to the running Exp64** (PID 740093, grades ~6/26) — this is an interpretation lens to apply when grading it: read a thin noisy lift as *possibly contracted*, not *absent*, and verify against a noiseless cell before concluding NULL.

*Caveat (sharpened)*: the exact `(1−p)` scaling and the "noisy gap ≤ noiseless gap" ordering are rigorous **only for unital noise** (depolarizing/dephasing). FakeMarrakesh is NOT unital — it includes **amplitude damping (T1 relaxation), whose fixed point is |0⟩, not I/2**, with non-uniform per-axis scaling (`√(1−γ)` transverse, `(1−γ)` longitudinal). For a specific `H` a cost gap with internal cancellation can therefore even *anti-contract*. So treat the contraction direction as **rigorous for unital noise, heuristic otherwise**. This is exactly *why* the Exp64 recommendation is "re-run a thin cell noiselessly and **measure** the contraction" rather than "apply a theoretical `(1−p)` correction" — you cannot clean-correct a non-unital backend; you must measure it. Don't quote a numeric contraction factor for FakeMarrakesh.
