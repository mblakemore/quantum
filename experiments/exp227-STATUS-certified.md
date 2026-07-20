# Exp227 — THE GUARDIAN OF FOREVER: CERTIFIED — energy on the bath-record dial

**Whisper C4913, 2026-07-20. Job `d9ep30qneu4c739on4v0`, `ibm_fez`, 10 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (derivation C4912).** Horizons-5 P3 —
the grand unification of the arrow of time, on silicon.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** On one bath-record apparatus (system |+⟩, bath, cry(θ),
κ=cos(θ/2)), **energy descends the same κ dial as information** — coherence, objectivity, and the
extractable/teleportable energy are all functions of the single record-strength κ. Information and
energy, one dial. The derivation (C4912) confirmed on hardware.

## The measured dial

| θ/π | κ | ⟨X_S⟩ (=κ) | ⟨Z_B⟩ (=κ²) | ⟨X_S Z_B⟩ (=κ) | QET W (=1−κ²) |
|---|---|---|---|---|---|
| 0.00 | 1.000 | +0.997 | +0.998 | +0.995 | −0.006 |
| 0.25 | 0.924 | +0.916 | +0.850 | +0.894 | +0.104 |
| 0.50 | 0.707 | +0.707 | +0.530 | +0.673 | +0.367 |
| 0.75 | 0.383 | +0.398 | +0.159 | +0.344 | +0.686 |
| 1.00 | 0.000 | +0.040 | −0.009 | −0.027 | **+0.846** |

- **G1 COHERENCE** ⟨X_S⟩ = κ — the wave face (200b/215), tracked across the dial. **OK.**
- **G2 RECORD ENERGY** ⟨Z_B⟩ = κ² — the bath's stored energy equals its objectivity (201's κ² law).
  **OK.**
- **G3 CHANNEL** ⟨X_S Z_B⟩ = κ — the system–bath correlation that carries the information enabling
  QET. **OK.**
- **G4 QET EXTRACTION (reported headline, feed-forward):** Alice measures σ_x on S and sends one
  classical bit; Bob's conditioned rotation extracts energy W = ⟨Z_B⟩_after − ⟨Z_B⟩_before. The
  curve **W = [−0.006, 0.104, 0.367, 0.686, 0.846]** tracks the ideal 1−κ² = [0, 0.146, 0.5, 0.854,
  1.0] in shape — hardware-degraded by the feed-forward latency (the 218 caveat, priced into the
  pre-registration, reported not gated). **At the full-record end (κ=0) the bath is maximally mixed
  — locally useless — yet one classical bit teleports W = 0.846 of the maximum energy into it.**

## What it means

The bath-record ledger has now unified **five faces on one κ = cos(θ/2) dial**, measured:
- coherence (wave) V = κ — 200b/215
- objectivity (fact) ⟨Z_B⟩ = κ² — 201
- distinguishability (particle) D = √(1−κ²) — 215
- **stored energy** = κ² — this flight
- **teleportable energy** W = 1−κ² — this flight

The arrow of time — objectivity (201), irreversibility (204), wave-particle duality (215), and now
**energy** — is a single dialable quantity: how much the environment has recorded. This crosses the
information/energy boundary that 201's ledger unification did not: it is the same κ that decides
whether a fact is objective *and* how much energy a classical bit can teleport into the bath that
recorded it.

## How it was built

S=q0=|+⟩, B=q1; cry(θ) forms the record; bath field H_B = −σ_z^B. Terminal faces (G1–G3): one
circuit/θ measuring S in X and B in Z gives all three correlators at once. QET (G4): Alice's σ_x
measurement + Bob's μ-conditioned Ry (feed-forward, dynamic circuit) — Bob's rotation Ry(−θ/2) for
μ=+ and Ry(−π−θ/2) for μ=− takes each post-measurement branch to |0⟩. Derived + statevector-verified
first (C4912), then flown. Depth-check before submit (1–4 2q gates) — the 213 lesson, **14th
consecutive flight**.

## Scope (honest)

System + bath (2 qubits), the certified 200b/215 record apparatus + a bath field + the Hotta QET
protocol. Registered verdict on the terminal faces (G1–G3, high-confidence); G4 QET extraction is
the reported feed-forward headline, hardware-degraded (0.85 vs 1.0 at full record) but shape-clear —
priced from the 218 feed-forward haircut in the pre-registration, not forced into the verdict (the
P4/Exp223 lesson: price to hardware, keep the miss honest). Textbook QET (Hotta) + the campaign's
bath-record ledger; the contribution is the composition — energy on the same dial as information.

## Line

**The ledger of time balances one more column, and it is written in energy. On one apparatus we
turned a single knob — how much the environment remembers of an event — and watched the wave fade
as κ, the fact sharpen as κ², and the energy a classical bit can teleport into the recording bath
rise as 1−κ², until at full memory the bath was a blank locally-useless fog and one bit poured 0.85
of a quantum's worth of energy into it. Information and energy, objectivity and the arrow of time,
all one dial. The Guardian of Forever keeps its ledger in a single number.**
