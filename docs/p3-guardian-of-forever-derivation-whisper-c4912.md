# P3 — The Guardian of Forever: energy on the bath-record dial (derivation)

**Whisper C4912, 2026-07-20. Substrate `claude-opus-4-8`.** Derivation on the Creator directive
"@whisper Derive P3." This is the dedicated derivation cycle P3 was held for (C4912: "the grand
unification deserves a cycle that does the QET–κ derivation properly first, not a forced
pre-registration"). Analytical result + statevector-exact numerical verification + a flight
pre-registration. **No hardware flown this cycle — this is the derivation.**

---

## 1. The claim to establish

The bath-record ledger (Exp200b/201/204/215) showed that **coherence, objectivity, irreversibility,
and wave-particle duality** all descend one dial: κ = cos(θ/2), the fraction of an event the
environment has recorded. **P3 asks whether ENERGY — a genuinely different physical category —
descends the same dial.** If yes, the arrow of time unifies information *and* energy on one curve.

---

## 2. The apparatus (one dial, one θ)

A single system qubit S and a single bath qubit B, on the certified 200b/215 apparatus:

- S prepared in the pointer superposition |+⟩; B in |0⟩.
- Couple by `cry(θ, S→B)` — the partial-record coupling. κ ≡ cos(θ/2).

State: |ψ(θ)⟩ = (|0⟩_S|0⟩_B + |1⟩_S|b(θ)⟩_B)/√2, where |b(θ)⟩ = Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩.

Everything below is derived on **this one state** and verified statevector-exact.

---

## 3. The information / coherence faces (recovered)

- **Coherence (wave):** ⟨X_S⟩ = ⟨0|b⟩ = cos(θ/2) = **κ** (the reduced system off-diagonal; 200b's C,
  215's V).
- **Record / objectivity:** ⟨Z_B⟩ = ½(⟨0|Z|0⟩ + ⟨b|Z|b⟩) = ½(1 + cosθ) = cos²(θ/2) = **κ²** (the
  bath's which-path polarization; 201's S ∝ κ²).
- **Distinguishability (particle):** D = √(1−κ²) = sin(θ/2) (215). **V² + D² = 1** (verified).
- The reduced bath ρ_B has eigenvalues **(1±κ)/2** — the bath's information about the system.

---

## 4. The energy faces (the new content) — derived + verified

Give the bath a local Hamiltonian **H_B = −σ_z^B** (ground |0⟩ at energy −1, the natural "the bath
relaxes toward its recorded pointer" field). All three energy quantities are clean functions of κ:

### 4.1 Energy stored in the record
⟨H_B⟩(θ) = −⟨Z_B⟩ = **−κ²**. Writing the record *costs* energy: as θ grows (record forms, κ→0),
the bath is driven up from −1 to 0. The **energy cost of recording** = ⟨H_B⟩(θ)−⟨H_B⟩(0) = **1−κ² =
D²** — the energy price of the record equals the which-path distinguishability squared.

### 4.2 Energy extractable by Quantum Energy Teleportation (Hotta protocol)
Alice measures σ_x on S (outcome μ=±1, probability p_μ=(1+μκ)/2, injecting energy globally) and
sends the one classical bit μ to Bob. Bob applies a μ-conditioned local rotation to B and extracts
energy locally. After Alice's X-measurement B is *pure* (|B_μ⟩ ∝ |0⟩+μ|b⟩), so Bob's optimal
μ-conditioned rotation takes each branch to |0⟩ (energy −1):

**W_QET (extracted with the bit) = ⟨H_B⟩_init − (−1) = 1 − κ² = D².**

### 4.3 The teleportation advantage — what the classical bit buys
Without Alice's bit, Bob's best is to rotate the *mixed* ρ_B to its passive form; the passive energy
of ρ_B (eigenvalues (1±κ)/2) under H_B is −κ, so local extraction = ⟨H_B⟩_init−(−κ) = **κ−κ²**.

**QET advantage = W_QET − W_local = (1−κ²) − (κ−κ²) = 1 − κ.**

**The profound reading:** at full record (θ=π, κ=0) the bath is *maximally mixed* — locally
useless, no local operation extracts anything — yet Alice's single classical bit lets Bob extract
the **maximum** energy (1−κ = 1). Energy is *teleported* into a locally-passive bath by information
alone. (Verified numerically: advantage 0.000 / 0.076 / 0.293 / 0.617 / 1.000 at θ/π = 0…1, exactly
1−κ.)

---

## 5. The grand unification (one κ = cos(θ/2) dial)

| face | category | law |
|---|---|---|
| coherence V = ⟨X_S⟩ | information (wave) | **κ** |
| objectivity ⟨Z_B⟩ | information (fact) | **κ²** |
| distinguishability D | information (particle) | **√(1−κ²)** |
| record energy cost | **energy** | **1−κ² = D²** |
| QET extractable energy W | **energy** | **1−κ² = D²** |
| QET teleportation advantage | **energy** | **1−κ** |

All verified statevector-exact. **Information (κ, κ²), duality (V²+D²=1), AND energy (κ², 1−κ², 1−κ)
descend the one bath-record dial.** The arrow of time — objectivity (201), irreversibility (204),
wave-particle duality (215), and now energy — is a single dialable quantity: how much the
environment has recorded. This is the ledger-of-time unification (201's "two phenomena, one measured
curve") extended across the information/energy boundary.

---

## 6. Flight pre-registration (ready to fly on "fly P3")

**Apparatus:** S=q0, B=q1; H(q0); cry(θ,0→1); H_B=−σ_z^B. Dial θ/π ∈ {0,¼,½,¾,1}. Shallow (1 cry).

**Terminal faces (no feed-forward — one Z-basis + one X-basis variant, both certified-easy):**
- G1 COHERENCE: ⟨X_S⟩ = κ to ≤ 0.08 (matches 200b/215).
- G2 RECORD ENERGY: ⟨Z_B⟩ = κ² to ≤ 0.08 — the stored energy on the dial.
- G3 CHANNEL: ⟨X_S Z_B⟩ = κ (the information channel enabling QET), terminally measurable.

**QET-extraction face (the striking one — needs feed-forward, a dynamic circuit):**
- G4 TELEPORTED ENERGY: measure ⟨H_B⟩ before, and after Alice's σ_x measurement + Bob's μ-conditioned
  rotation; extracted W = 1−κ² with the bit vs κ−κ² without; the **advantage 1−κ ≥ [band] at ≥5σ**.
  Honest caveat (218 finding): feed-forward carries a hardware latency cost, so G4 is the
  ambition-gated face; G1–G3 are the high-confidence terminal faces. Registered verdict on the
  terminal faces (G1∧G2∧G3), with G4 as the headline feed-forward demonstration reported alongside.
- Budget (C4887): terminal faces near-ideal (1 cry, ~215-class); G4's advantage hardware-priced
  from the 218 feed-forward haircut (expect the *shape* 1−κ to hold, the absolute possibly reduced)
  — price the band to the haircut, NOT to ideal (the P4/Exp223 lesson: MI/energy thresholds must be
  priced to hardware).

**Kill-criteria:** K1 depth (trivial here); K2 selftest must reproduce all laws to <0.03; K3 if the
feed-forward G4 shape (1−κ) degrades below recognizability on hardware, report G4 honestly as
"terminal faces unified, extraction shape hardware-limited," do not force it into the verdict.

---

## 7. Status

**P3 is DERIVED.** Energy rides the bath-record κ dial — stored energy κ², extractable energy 1−κ²,
teleportation advantage 1−κ — unifying with coherence (κ), objectivity (κ²), and duality on one
dial, on one apparatus. The flight is pre-registered and ready. The grand unification of the arrow
of time is now a derived, verified, flyable statement — no longer a forced pre-registration but an
earned one. Awaiting "fly P3."
