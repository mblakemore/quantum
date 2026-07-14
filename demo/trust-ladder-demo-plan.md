# The Trust Ladder Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4689 · **For**: `demo/trust-ladder/` (Wing IV)
**Findings**: F115 (Exp135 CHSH witness) · F116 (Exp136 one-sided-DI steering) · F117 (Exp137 rigorous 1SDI randomness).

## 1. Goal & the "aha"
Climb a ladder of *trust*. The higher you climb, the less you assume about your devices — and the
stronger the security you demand of the hardware. At the bottom you trust everything and get a full
random bit. In the middle you trust only your own measurement and still get a rigorous, certified
0.65 bits. At the top you trust *nothing* — and the certificate **evaporates**, because a single chip
cannot provide the no-signaling that full device-independence requires. The exhibit makes tactile the
lesson that a claimed quantity can dissolve when a premise fails — and shows the honest sweet spot.

## 2. Data — verified first (results/exp135|136|137_hw_results.json)
- **Rung 1 · Full trust** — CHSH witness **S = 2.7522 (53σ)** health-checks that the device is quantum
  (rules out a classical mimic); under device trust, Born-rule randomness = **1.00 bit / qubit**. (F115)
- **Rung 2 · One-sided-DI** — steering **S₃ = 1.6813 (96σ)** with Bob trusted, Alice a black box;
  rigorous **H_min = 0.6823 ± 0.0063 bit/use** (H_min − 5σ = **0.6509 > 0**), from measured assemblage
  tomography via the SDP tool. (F116/F117, job `d9ansru6hjac73fenigg`) — **the certificate that stands.**
- **Rung 3 · Full DI** — the device-independent bound *would* give **0.5928 bit/use** — but it requires
  **no-signaling between the two sites**, which two qubits sharing control on one chip do not enforce
  (a shared-control classical device fakes S = 2√2 at zero entropy). On-chip the number **evaporates**;
  full-DI needs space-like separation, off-chip. **We did not perform full-DI** — this rung is the honest null. (F115 scope)

## 3. The exhibit — two panels
**A — Climb the ladder (interactive).** Three rungs, selectable (bottom = trust everything → top = trust
nothing). A central **certificate card** updates per rung: the *assumption*, the *security* it buys, the
*certified bits* (big number), and a **visual state** — SOLID for rungs 1–2, **DISSOLVING** for rung 3
(the number fades under a "no-signaling unmet" overlay; reduced-motion shows a static "unavailable on one
chip" state). The transition to the top is the memorable beat: more security demanded → the chip can't
provide it → the certificate evaporates.

**B — The three rungs, side by side.** A summary the visitor can read at a glance: 1.00 (Born, needs
device trust) · **0.65 (rigorous, one-sided-DI)** · — (full-DI, off-chip only). The measured-data badge
(F115/F116/F117, jobs). One line on *how* 0.65 is earned: the SDP tool computes H_min from the measured
steering assemblage — the exhibit points to that tool.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | Ladder direction ambiguous. | Bottom = most trust / least security; top = least trust / most security. *Climbing = demanding more, and the top is where the chip fails.* Labels state this. |
| G2 | Implying we achieved full-DI. | Rung 3 explicitly: **"we did not do this"** — full-DI needs off-chip space-like separation; the 0.59 is a quarantined counterfactual (Exp135). |
| G3 | *Why* it evaporates must be exact. | State the mechanism: a shared-control classical device fakes S = 2√2 at zero entropy ⇒ the DI quantity is unsupportable on one chip. |
| G4 | CHSH's role at rung 1 mis-stated as certifying the bit. | CHSH **health-checks** the device is quantum; the 1 bit is Born-rule **under device trust**, not certified by Bell. |
| G5 | a11y / motion. | Rungs are buttons (keyboard, aria-pressed); states carry text (SOLID / RIGOROUS / EVAPORATED), not colour alone; reduced-motion → static evaporated state. |
| G6 | Mobile. | Ladder + certificate stack < 680px; summary rows wrap. |
| G7 | Measured-only. | 1.00 (Born, exact) · 0.65 (measured F117) · 0.59 (measured DI counterfactual, labelled quarantined) · S values measured. |

## 5. Pre-dev structure
1. **Rung-data kernel**: an array of the 3 rungs {assume, security, bits, state, notes, measured refs}, pulled from the grade JSONs; assert bits are 1.00 / 0.6823 / 0.5928 and rung-3 state = "evaporate".
2. Ladder UI + certificate card on the kernel. 3. Summary panel. 4. Chrome (shared museum.css, cyan solid / amber evaporate). 5. Passes (a11y, mobile, motion, self-contained, look).

## 6. Acceptance
Three selectable rungs; rung 3's certificate visibly evaporates (static under reduced-motion) with the
honest "we did not do full-DI / no-signaling unmet" text; every number measured or a labelled quarantined
counterfactual; the middle rung is clearly the certified sweet spot (0.65, 5σ); keyboard-operable,
colour-not-alone, mobile-stack, no external requests, theme-aware.
