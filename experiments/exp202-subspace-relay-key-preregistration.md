# Exp202 — THE SUBSPACE RELAY KEY: pre-registration (frozen before submission)

**Whisper C4896, 2026-07-19. Horizons-4 Invention 1, flight 1, flown on Creator go
("Fly the next one! | 2 | Invention 1, flight 1: Logical E91"). Committed BEFORE submission.**

## Claim under test

The network stack's key layer runs at the **logical level**: an entanglement-based E91/BBM92
key between two [[4,2,2]] shields — direct, and through an **untrusted relay shield** — with
the shield's key advantage **growing with depth** (the Subspace Relay thesis, from the
191→196→197 measured trend +0.07/+0.06/+0.24).

## Design (parents verbatim, credited)

5 arms × 4 transversal basis pairs (ZZ/ZX/XZ/XX) = 20 circuits, `ibm_fez`, 8000 shots:
`logical` (196's shielded pair) · `relay` (197's Federation: A and C never interact, key
rides the relay's 2 classical bits) · `bare` (196's) · `barerelay` (197's physical swap) ·
`nocx` (196's — executed no-entanglement null).

**The linearity duality**: at the logical level the key bases are transversal, so the same
four measurements are simultaneously the key (QBER_Z = (1−ZZ)/2, QBER_X = (1−XX)/2) and the
certificate (S = √2(ZZ+XX), mixed pairs = nulls). Nothing is measured twice.

**Key accounting**: r = max(0, 1 − h2(Q_Z) − h2(Q_X)) (asymptotic BBM92, one-way EC bound);
throughput column r × acceptance reported for both links (the shield's postselection toll).

## Frozen gates

- **G1 CERTIFICATES**: S(logical) ∈ [2.40, 2.85] and >2 at ≥5σ (196's certified band);
  S(relay) ∈ [2.30, 2.75] and >2 at ≥5σ (197 measured 2.6046); S(nocx) ∈ [−0.25, 0.30].
- **G2 KEYS EXIST**: QBER_Z, QBER_X < 0.11 (abort threshold) in logical/relay/bare/barerelay;
  nocx QBER ∈ [0.45, 0.55] both bases (no weld → the "key" is a coin).
- **G3 SHIELD QUALITY** (the deliverable): r(logical) > r(bare) at ≥3σ AND r(relay) >
  r(barerelay) at ≥3σ (delta-method SE on r); QBER_Z(relay) < QBER_Z(barerelay) at ≥5σ.
- **G4 DEPTH PAYS** (the invention thesis, gated): [r(relay) − r(barerelay)] >
  [r(logical) − r(bare)] at ≥3σ. A miss is a finding *against* Invention 1 and is kept.
- **G5 GAUGES**: acceptance ≥ 0.70 every basis (logical/nocx — 196's gate); ≥ 0.50 every
  basis (relay — 12q, 3 blocks); throughput reported, not gated.

**Registered verdict = G1∧G2∧G3∧G4∧G5.**

## Budget check (C4887 rule) + filed predictions

Key thresholds need λ ≈ 0.79 (QBER < 0.11 ⇔ corr > 0.78); parents measured 0.98 (196
direct) / 0.92 (197 relay). Ample.
**Filed**: QBER_Z(logical) ∈ [0.5%, 2.5%]; QBER_Z(relay) ∈ [2.5%, 6%];
**r(relay)/r(barerelay) ∈ [1.8, 5.0]** (the binary-entropy nonlinearity amplifying 197's
+0.24 CHSH edge into a key-rate multiple); crossover pattern (conf 0.6): bare wins
throughput on the direct link, logical wins throughput on the relay link.

## Scope (F115 trust-ladder discipline)

Trusted-device BBM92. The CHSH value is the in-protocol quantum-health certificate (tier-2),
**not device-independent** — no-signaling is unenforceable on one chip; the DI reading would
evaporate (F115 quarantine). Raw sifted bits + asymptotic secret fraction; deterministic
per-circuit settings (no per-shot QRNG basis choice; sifting fraction excluded); no
EC/PA/authentication (180's scope); expectation-value correlators with logical-level fair
sampling via stabilizer postselection (196/197 scope).

## What the outcomes mean

- **All held**: the first error-corrected QKD stack layer — and the depth-trend thesis of the
  Subspace Relay measured on the scoreboard that matters (secret bits).
- **G3 holds, G4 misses**: shields pay at every depth but the advantage doesn't grow —
  Invention 1's sequencing changes (the composed-stack flights lose priority to per-layer
  audits).
- **G1/G2 anchor misses**: instrument accounting (window drift vs parents); no band-shopping
  refly without an identifiable, pre-priceable cause (200 precedent).
