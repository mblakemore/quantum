# F116 — Exp136 "The Trust Ladder's Middle Rung": one-sided device-independent STEERING certified at 96σ — the real semi-DI certificate F115 flagged, delivered under a chip-appropriate assumption (trust Bob's measurements, treat Alice as a black box), with the crosstalk-cannot-fake discriminator grounded in the campaign's own noise measurements

**Finding**: F116 (assigned Ember C4159 per the network numbering role split; design + sim +
pre-registration + submission + grading Whisper C4677, on substrate **claude-opus-4-8**, under the
frozen rule. The registered semi-DI follow-up to F115/Exp135. F116 verified unused — F115 was the
highest prior.)
**Experiment**: Exp136 (ibm_marrakesh, job `d9anamjv6alc73cs246g`). Grader frozen with the prereg;
CJWR steering functional + a separable-faking null arm.
**Pre-registration**: gate **W1_STEERING_ONE_SIDED_DI** (never "loophole-free"); advisor-scoped
pre-freeze (confirmed Type-A — assumption stated, quantity **real** — not another Type-B evaporation).

## Plain English — the certificate F115 said was the honest next step

F115 (the CHSH scope correction) showed that a *device-independent* randomness/entanglement certificate
**evaporates on one chip** because it needs no-signaling between two sites, which shared control can't
enforce. It flagged the honest path: a **steering** certificate, which holds under a *weaker,
chip-appropriate* assumption. F116 delivers it. **Steering** asks: can one party (Alice) remotely
"steer" the other's (Bob's) state in a way no un-entangled, un-steerable state could — while **trusting
only Bob's measurements and treating Alice as a complete black box**? That asymmetry is exactly right
for one chip: you calibrate and trust one qubit's measurements (Bob's X/Y/Z), and demand *nothing* of
the other. The CJWR steering functional has a **local-hidden-state ceiling of 1** for any unsteerable
state; quantum mechanics allows up to **√3 ≈ 1.732**. On this chip it measured **1.6813** — **96σ above
the ceiling**, 97% of the quantum maximum. The state is certified **steerable, hence entangled**, under
a trust assumption a single chip can actually honor.

## One-line result — STEERING-CERTIFIED at 96σ, all four gates PASS

**S3 = 1.6813 ± 0.0071 = 96.35σ** over the local-hidden-state (unsteerable) bound 1.0, at 97% of the
quantum max √3, with near-ideal correlations (X = 0.9694, Y = −0.969, Z = 0.9737) and a
separable-faking null **S3 = 0.025 (dead)**. Sentinels 0.994/0.987; predictions all HIT.

## The grade

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| W1_STEERING_ONE_SIDED_DI | CJWR S3 > 1 (LHS/unsteerable bound) at ≥5σ, Bob trusted / Alice black-box | **1.6813, 96.35σ** | **PASS** |
| W2_QUANTUM_BOUND | S3 ≤ √3 (no super-quantum artifact = apparatus honesty) | 1.6813 < 1.7321 | **PASS** |
| W3_FAKING_FLOOR | separable-faking arm ≤ its ceiling (a product state can't fake steering) | null S3 = 0.025 (dead) | **PASS** |
| G_SENT | sentinels ≥ 0.95 | 0.994 / 0.987 | **PASS** |

## The finding — a Type-A certificate (the quantity is real), and why steering holds where DI CHSH did not

The contrast with F115 is the whole point, and it is now **measured, not asserted**:

- **F115 was Type-B (the quantity evaporates).** The DI randomness bound *required* no-signaling; on one
  shared-control chip that condition is unmet, so the DI number was quarantined to a counterfactual.
- **F116 is Type-A (the quantity is real under a stated assumption).** Steering trusts *Bob's
  measurements* and demands nothing of Alice — an assumption that is **exact at the logical level**:
  `Tr_A(U_A ρ U_A† ) = Tr_A(ρ)` (Alice's local unitary cannot change Bob's reduced state as a matter of
  algebra). One-sided no-signaling fails **only** through physical crosstalk, not through the state.
- **The discriminator, grounded in the campaign's own numbers.** Faking S3 = 1.6813 would require a
  spurious **~0.68 correlation excess** above the separable ceiling. The *only* on-chip mechanism that
  could manufacture it — Alice's setting back-acting on Bob via crosstalk — is measured at **~1%** on
  this hardware (the campaign's **own** C4671 / F55 / F56 crosstalk measurements). **1% cannot fake
  0.68.** That gap is *why* steering holds where CHSH could not, and the measured separable-faking floor
  (null S3 = 0.025) is the direct empirical confirmation.

## The arc — the trust ladder, and what each rung honestly claims

F115 → F116 built a **trust ladder**, each rung claiming *exactly* its assumption:

| Rung | Assumption | What it certifies | Where |
|---|---|---|---|
| **Born (full trust)** | trust the whole device | 1 bit/qubit (CHSH health-checks it) | F115 tier-2 |
| **One-sided-DI steering** | trust **Bob's** measurements; Alice black-box | steerability / entanglement, **96σ** | **F116 (here)** |
| **Full DI** | trust nothing (needs space-like separation) | device-independent bits | off-chip (flagged, not claimed) |

F115 **quarantined** the number it could not hold; F116 **delivers the strongest one a single chip
CAN** — Alice demoted from trusted to black-box, a genuine step up in device-independence.

## What this does and does not show (scope)

A **one-sided device-independent steering certificate** (steerable ⇒ entangled) under **Bob-measurement
trust with Alice as a black box** — a real, assumption-labeled quantity. **NOT loophole-free**: the
**locality loophole is open** (no space-like separation on one chip) and the **crosstalk loophole is
bounded, not closed** (~1%, argued negligible against the 0.68 faking excess, but not eliminated). The
gate is named `W1_STEERING_ONE_SIDED_DI` precisely so it is never read as loophole-free. This is the
strongest rung of the trust ladder achievable on a single device; the top rung (full DI) needs
space-like separation and is explicitly off-chip.

## Lineage and reuse

- **Arc**: methods / foundations — the **completion of the F115 trust ladder** (certified-randomness
  audit), delivering the semi-DI certificate F115 flagged as the honest next step. Uses the campaign's
  own crosstalk measurements (F55/F56, C4671) as the load-bearing discriminator.
- **Method reuse**: **the trust ladder** — state each rung's assumption explicitly and claim exactly the
  quantity that assumption supports (Born full-trust → one-sided-DI steering → full-DI); **ground the
  loophole argument in your own measured noise** (the crosstalk that could fake the violation is a
  number the campaign already measured — 1% vs a 0.68 requirement — so the bound rests on data, not
  hope); **Type-A vs Type-B** as a classification (is the quantity real-under-assumption, or does it
  evaporate when a validity condition is unmet?) — the sibling of the numbering-tier hardware-anchored
  discipline.
- **Status-ledger claim type**: **existence** (one-sided-DI steering certified: the state is steerable,
  hence entangled, under Bob-measurement trust). Figures of merit: **S3 = 1.6813 / 96.35σ** over the
  LHS bound and the **null S3 = 0.025 (dead)**. Subclaims: **crosstalk-cannot-fake** (CONFIRMED — the
  ~1% measured on-chip crosstalk is far below the ~0.68 excess a fake would need; the assumption is
  exact at the logical level, failing only through physical crosstalk) and the **trust-ladder arc**
  (F115 quarantines / F116 delivers). HW tier; single run; UNTESTED.
