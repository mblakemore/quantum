# F116 — Exp136 "The Trust Ladder's Middle Rung": one-sided device-independent STEERING certified at 96σ — the real semi-DI certificate F115 flagged, delivered under a chip-appropriate assumption (trust Bob's measurements, treat Alice as a black box), with the crosstalk-cannot-fake discriminator grounded in the campaign's own noise measurements

**Epoch**: n=2 basis=distinct-device · dispersion=0.01633±0.1285 (n=2) · window_retrievable=yes · checked=2026-08-18

> **Dispersion computed C5075 from this finding's own two windows** — marrakesh S3 = 1.6813 and the
> kingston re-fly S3 = 1.6582, both 2026-07-13, both windows banked in
> `results/window_rescue_c5075.json`. Mean 1.6698, SD across windows **0.01633**, within-window SE
> 0.00710, variance-components **σ_b = 0.01471** — so ~2.3× the within-window shot noise, real
> structure, but 0.016 on a quantity certified at 93–96σ over the LHS bound.
> **The interval is enormous and that is the honest part**: at n=2 the χ² CI on the SD spans
> [0.0073, 0.52], two orders of magnitude. A bare 0.01633 would read as settled; it is not, and the
> schema's requirement that dispersion carry its n AND an interval is what forces that to show.
> **basis=distinct-device** because the two flights span marrakesh and kingston — the stronger claim,
> and the reason this finding was never single-window fragile.

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

## Cross-device confirmation — the certificate itself travels (CONFIRMED_ON_RETEST, ibm_kingston)

The frozen Exp136 apparatus and advisor-locked scope were re-flown on **ibm_kingston** (Exp136k, job
`d9aneirv6alc73cs2cn0`, pair (88,89)) — a chip the design never saw. The certificate holds: **S3 =
1.6582 ± 0.0071 = 93.1σ** over the LHS bound (null faking-floor 0.004, sentinels 0.999/0.982),
side-by-side with marrakesh 1.6813 (96σ) — **both ~96% of the quantum max √3**. So the *certification
itself is device-independent* (not just the diagnostic bench of F112 — the semi-DI **certificate**
travels too). This is a **pure cross-device replication** (identical frozen functional and scope, zero
new scope risk), so per the campaign's replication discipline — the F82 causal-game-on-`ibm_fez`
precedent — it is folded here as **CONFIRMED_ON_RETEST**, not minted as a separate finding; a
single-observable second-device flight after F112 established portability is a confirmation, not a new
milestone.

## The 1SDI-randomness honest wall — flagged, then CLOSED by the SDP tool (scoping note)

Completing the trust ladder to an *actual one-sided-DI random bit-count* from the banked steering data
**hit an honest wall**: the correct 1SDI min-entropy bound is **SDP-based**, and the candidate
*analytic* bounds (P_guess ≤ ½ + f(S3)) **failed the boundary check** — they certify positive randomness
even at the unsteerable bound S3 = 1, where it must be *zero*. So **no bit-count was shipped from a wrong
analytic form** (the same discipline that quarantined the F115 DI number pre-freeze).

**The wall is now methodologically closed** (`tools/sdp_randomness.py`, Whisper C4679, Creator-directed —
docs/tool tier, no F-number). It is the **exact** 1SDI SDP for a trusted qubit Bob: by GHJW a qubit
assemblage is quantum-realizable **iff** PSD + no-signaling — precisely the SDP constraints — so no NPA
hierarchy is needed (Passaro–Acin 2015). It **passes the boundary the analytic bounds failed**: on Werner
states, H_min = **0.000 at S3 = 1** (unsteerable) and **≈ 1 at S3 = √3** (pure Bell), monotonic between;
and it reproduces the known Passaro feature that the **randomness threshold exceeds the steering
threshold** — states with S3 ∈ [1, ~1.3] are *steerable yet certify zero randomness*, exactly the nuance
no naive S→H_min bound can capture (the concrete reason the SDP was necessary). Applied to our data as a
**Werner-model estimate (labeled)**: marrakesh S3=1.68 → **0.656 bits/use**, kingston S3=1.66 → **0.587
bits/use**.

**The remaining honest gap (the earning-line):** the *rigorous* per-device number needs **assemblage
tomography** — Bob's X/Y/Z conditional states per Alice outcome/setting — which Exp136 did not measure
(matched-correlations only). The tool is *ready to consume it*: one cheap follow-up flight turns the
~0.6-bit Werner *estimate* into a rigorous 1SDI certificate, and **that flight — not this tool-build —
earns the 1SDI-randomness F-number** (the hardware-anchored-vs-tool discipline, c4155_001). Arc:
Exp135 (DI evaporated) → Exp136 (steering 96σ) → Exp136k (analytic bound failed) → the SDP tool
(correct, validated) → *assemblage-tomography flight (earns the F)*.

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
