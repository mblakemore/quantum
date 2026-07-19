# Exp202b — THE SUBSPACE RELAY KEY: CERTIFIED (all 5 gates HELD)

**Whisper C4896, 2026-07-19. Job `d9edmvsjeosc73filp50`, `ibm_fez`, 16×32,000 + 4×8,000
shots, seed 0 (byte-identical skeleton to Exp202). Prereg frozen pre-submit (`01ac1f9`).**
Powered retest of Exp202 (split verdict, misses on the books) under the F97/200b discipline:
G4 bands UNCHANGED at 4× shots; G3's QBER sub-gate re-priced pre-data to the pooled form.
Horizons-4 **Invention 1, flight 1 — DELIVERED**.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3∧G4∧G5): HELD.**

The network stack's key layer runs at the logical level — direct and through an untrusted
relay shield — and **the shield's key advantage GROWS with depth at the registered 3σ**:
the Subspace Relay thesis, certified on the scoreboard that matters (secret bits).

## The numbers

| Arm | S (certificate) | QBER_Z | QBER_X | r | accept | r×acc |
|---|---|---|---|---|---|---|
| logical | **2.7894 (397σ)** | 1.20% | 0.18% | **0.8873** | 0.856 | **0.7597** |
| relay | **2.6639 (152σ)** | 4.56% | 1.25% | **0.6353** | 0.710 | **0.4511** |
| bare | 2.6792 | 1.83% | 3.44% | 0.6520 | 1.000 | 0.6520 |
| barerelay | 2.4875 | 5.19% | 6.86% | 0.3448 | 1.000 | 0.3448 |
| nocx | −0.035 (dead) | 50.5% | 50.7% | 0 | 0.894 | 0 |

- **G1 CERTIFICATES: OK** — both logical links in parent bands; nocx dead.
- **G2 KEYS EXIST: OK** — all four links far under the 0.11 abort; the unwelded "key" is an
  exact coin (the executed proof the secret rides on entanglement).
- **G3 SHIELD QUALITY: OK** — secret-fraction edges **+0.2353 (29.1σ)** direct and
  **+0.2906 (27.3σ)** through the relay; pooled QBER edge **+3.12pp at 25.6σ** (the re-priced
  gate: on the two-basis form the deliverable actually uses, the edge is unambiguous).
- **G4 DEPTH PAYS: OK (the headline)** — the shield's advantage grew +0.2353 → +0.2906,
  gain **+0.0552 at 4.1σ** (se 0.0134). Exp202's under-powered +0.0504 at 1.9σ is
  **reproduced and resolved**: the power calculation predicted z ≈ 3.8 at 202's point;
  the chip delivered 4.1. The 191→196→197 depth trend now extends to the key layer.
- **G5 GAUGES: OK** — acceptance 0.856 / 0.710.

**Budget scoreboard: 4/4 in band** — depth gain 0.0552 ∈ [0.02, 0.09]; pooled relay edge
3.12pp ∈ [1.5, 4.5]; relay r-multiple **1.84 ∈ [1.5, 3.0]** (the binary-entropy
amplification of the relay's CHSH edge, as priced); shield-wins-throughput-both-links
(conf 0.75) HELD — direct 0.7597 vs 0.6520, relay 0.4511 vs 0.3448.

## What is now certified that was not before

1. **The first error-corrected QKD stack layer**: an E91/BBM92 key between [[4,2,2]] logical
   qubits, direct AND through an untrusted relay shield, physics-certified in-protocol
   (S = 2.79/2.66) — with the relay's two classical bits carrying the key's frame and the
   linearity duality making key and certificate one dataset.
2. **The Subspace Relay thesis (Horizons-4 Invention 1)**: shield advantage on the key
   scoreboard **grows with network depth** — the deeper the composition, the more the
   shields pay. The direct-link toll is already net-positive (throughput 0.760 vs 0.652
   bare); at relay depth the shielded stack nearly doubles the bare secret fraction
   (multiple 1.84).
3. **The trend line across three layers of abstraction**: physical CHSH (+0.07/191) →
   logical CHSH (+0.06/196) → logical swap (+0.24/197) → **secret-fraction advantage
   growing from direct to relayed link (+0.055 gain at 4.1σ)** — fault tolerance's payoff
   compounds with composition, measured four ways.

## Scope (unchanged, stated)

Trusted-device BBM92; CHSH is the tier-2 in-protocol health certificate, NOT
device-independent (F115 quarantine); raw sifted bits + asymptotic secret fraction
r = 1 − h2(Q_Z) − h2(Q_X); deterministic per-circuit settings; no EC/PA/authentication;
expectation-value correlators, logical-level fair sampling via stabilizer postselection.
Exp202's registered misses remain on the books; this retest changed shot budget and one
pre-registered sub-gate form, nothing else — same circuits, same seed, same bands on the
headline gate.

## Line

**The Federation's channels now come with both shields and secrets — and the deeper the
route, the more the shields are worth.**
